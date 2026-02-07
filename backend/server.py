from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
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

    # ⭐ TOOL DEFINITIONS
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "get_events",
                "description": "Fetch upcoming campus events",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_facilities",
                "description": "Fetch available campus facilities",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

    # ⭐ UNIVERSAL LLM CALL
    def call_llm(self, messages, tools=None):

        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
            max_tokens=800
        )

        return completion.choices[0].message

    # SESSION
    def get_or_create_session(self, session_id):

        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                "pending_confirmation": None
            }

        return session_id, sessions[session_id]

    # ================= DATABASE HANDLERS =================

    async def get_events(self):
        return await db.events.find(
            {"status": "upcoming"},
            {"_id": 0}
        ).limit(10).to_list(10)

    async def get_facilities(self):
        return await db.facilities.find(
            {"status": "available"},
            {"_id": 0}
        ).limit(10).to_list(10)

    # ================= BOOKING =================

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

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": message}
        ]

        try:
            raw = self.call_llm(messages).content
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

    async def execute_booking(self, booking_data):

        booking = Booking(**booking_data)
        booking.status = "confirmed"
        booking.confirmed_at = datetime.now(timezone.utc).isoformat()

        doc = booking.model_dump()
        await db.bookings.insert_one(doc)

        return {k: v for k, v in doc.items() if k != "_id"}

    # ================= AGENT LOOP =================

    async def handle_message(self, message, session_id):

        session_id, session = self.get_or_create_session(session_id)

        # 🔥 Confirmation Flow
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

        # ⭐ AGENT SYSTEM PROMPT
        messages = [
            {
                "role": "system",
                "content": """
You are an AI assistant for a college campus.

Use tools when needed:

- get_events → when user asks about events
- get_facilities → when user asks about labs, rooms, facilities

For booking requests:
Ask the user for date, time, and facility name.
Do NOT hallucinate data.
"""
            },
            {
                "role": "user",
                "content": message
            }
        ]

        response = self.call_llm(messages, tools=self.TOOLS)

        # 🔥 TOOL CALL DETECTED
        if response.tool_calls:

            tool_name = response.tool_calls[0].function.name

            if tool_name == "get_events":
                data = await self.get_events()

            elif tool_name == "get_facilities":
                data = await self.get_facilities()

            else:
                data = {}

            # Send tool result back
            messages.append(response)

            messages.append({
                "role": "tool",
                "tool_call_id": response.tool_calls[0].id,
                "content": json.dumps(data)
            })

            final = self.call_llm(messages)

            reply = final.content

            return ChatResponse(
                response=reply,
                session_id=session_id,
                intent=tool_name,
                data=data
            )

        # 🔥 Booking fallback
        if "book" in message.lower():
            validation = await self.validate_booking_request(message)

            if validation["valid"]:
                session["pending_confirmation"] = validation["booking_data"]

                return ChatResponse(
                    response=f"""
I can help you book this facility:

{json.dumps(validation["booking_data"], indent=2)}

Type YES to confirm.
""",
                    session_id=session_id,
                    intent="BOOKING_REQUEST",
                    requires_confirmation=True
                )
            else:
                return ChatResponse(
                    response=validation["message"],
                    session_id=session_id
                )

        # Normal reply
        return ChatResponse(
            response=response.content,
            session_id=session_id,
            intent="GENERAL"
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
