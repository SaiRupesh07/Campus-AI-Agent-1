from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import json
from groq import Groq

# ================= ENV =================

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

app = FastAPI(title="College Campus AI Agent API")
api_router = APIRouter(prefix="/api")

sessions: Dict[str, Dict[str, Any]] = {}

# ================= MODELS =================

class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_name: str
    user_email: str
    resource_id: str
    resource_type: str
    resource_name: str
    date: str
    start_time: str
    end_time: str
    purpose: str
    status: str = "pending"
    requires_confirmation: bool = True
    confirmed_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: Optional[str] = None
    data: Optional[Any] = None
    requires_confirmation: bool = False


# ================= AI AGENT =================

class CampusAIAgent:

    # 🔥 UNIVERSAL LLM CALL
    def call_llm(self, system_prompt, user_prompt):

        completion = groq_client.chat.completions.create(
            model=MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return completion.choices[0].message.content.strip()

    # SESSION
    def get_or_create_session(self, session_id):

        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                "pending_confirmation": None
            }

        return session_id, sessions[session_id]

    # 🔥 INTENT ROUTER (Bulletproof)
    async def llm_router(self, message: str):

        system = """
Decide the user intent.

Return ONLY one word:

EVENTS_QUERY
FACILITY_QUERY
BOOKING_REQUEST
GENERAL
"""

        intent = self.call_llm(system, message)

        intent = intent.strip().upper().replace(".", "")

        allowed = [
            "EVENTS_QUERY",
            "FACILITY_QUERY",
            "BOOKING_REQUEST",
            "GENERAL"
        ]

        return intent if intent in allowed else "GENERAL"

    # RESPONSE
    async def generate_response(self, intent, data, message):

        system = """You are a helpful college campus assistant.
Keep responses friendly, structured, and professional."""

        context = f"""
User asked: {message}
Intent: {intent}
Data: {json.dumps(data, indent=2) if data else "None"}
"""

        return self.call_llm(system, context)

    # EVENTS
    async def handle_events_query(self):
        return await db.events.find(
            {"status": "upcoming"},
            {"_id": 0}
        ).limit(10).to_list(10)

    # FACILITIES
    async def handle_facility_query(self):
        return await db.facilities.find(
            {"status": "available"},
            {"_id": 0}
        ).limit(10).to_list(10)

    # BOOKING VALIDATION
    async def validate_booking_request(self, message):

        system = """
Extract booking details.

Return ONLY JSON:

{
"resource_name":"",
"date":"",
"start_time":"",
"end_time":"",
"purpose":""
}
"""

        try:
            raw = self.call_llm(system, message)

            raw = raw.replace("```json", "").replace("```", "").strip()

            booking_data = json.loads(raw)

        except:
            return {"valid": False, "message": "Could not understand booking details."}

        facility = await db.facilities.find_one(
            {"name": {"$regex": booking_data.get("resource_name", ""), "$options": "i"}},
            {"_id": 0}
        )

        if not facility:
            return {"valid": False, "message": "Facility not found."}

        booking_data["resource_id"] = facility["id"]
        booking_data["resource_type"] = "facility"
        booking_data["user_name"] = "Guest User"
        booking_data["user_email"] = "guest@campus.edu"

        return {"valid": True, "booking_data": booking_data}

    # EXECUTE BOOKING
    async def execute_booking(self, booking_data):

        booking = Booking(**booking_data)
        booking.status = "confirmed"
        booking.confirmed_at = datetime.now(timezone.utc).isoformat()

        doc = booking.model_dump()
        await db.bookings.insert_one(doc)

        return {k: v for k, v in doc.items() if k != "_id"}

    # 🔥 MAIN AGENT LOOP
    async def handle_message(self, message, session_id):

        session_id, session = self.get_or_create_session(session_id)

        # Confirmation flow
        if session.get("pending_confirmation"):

            if message.lower() in ["yes", "confirm", "ok"]:
                result = await self.execute_booking(session["pending_confirmation"])
                session["pending_confirmation"] = None

                return ChatResponse(
                    response="✅ Booking Confirmed!",
                    session_id=session_id,
                    intent="BOOKING_CONFIRMED",
                    data=result
                )

            elif message.lower() in ["no", "cancel"]:
                session["pending_confirmation"] = None

                return ChatResponse(
                    response="Booking cancelled 👍",
                    session_id=session_id
                )

        # ROUTE
        intent = await self.llm_router(message)

        if intent == "EVENTS_QUERY":

            data = await self.handle_events_query()
            reply = await self.generate_response(intent, data, message)

        elif intent == "FACILITY_QUERY":

            data = await self.handle_facility_query()
            reply = await self.generate_response(intent, data, message)

        elif intent == "BOOKING_REQUEST":

            validation = await self.validate_booking_request(message)

            if validation["valid"]:
                session["pending_confirmation"] = validation["booking_data"]

                reply = f"""
I can help you book this facility:

{json.dumps(validation["booking_data"], indent=2)}

Type YES to confirm.
"""
            else:
                reply = validation["message"]

        else:

            reply = await self.generate_response(intent, None, message)

        return ChatResponse(
            response=reply,
            session_id=session_id,
            intent=intent
        )


agent = CampusAIAgent()

# ================= ROUTES =================

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    try:
        return await agent.handle_message(request.message, request.session_id)
    except Exception as e:
        logging.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/")
async def root():
    return {"status": "College Campus AI Agent Running 🚀"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
