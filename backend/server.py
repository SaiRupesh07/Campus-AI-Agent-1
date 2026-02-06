from fastapi import FastAPI, APIRouter, HTTPException
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
import os
import uuid
import json
import logging
import re
from datetime import datetime, timezone

from groq import Groq


# ================= ENV =================

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

groq_client = Groq(api_key=GROQ_API_KEY)

mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]


# ================= APP =================

app = FastAPI(title="Campus AI Agent")
api_router = APIRouter(prefix="/api")

sessions: Dict[str, Dict[str, Any]] = {}


# ================= MODELS =================

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: Optional[str] = None
    data: Optional[Any] = None
    requires_confirmation: bool = False


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
    status: str = "confirmed"
    confirmed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ================= AI AGENT =================

class CampusAIAgent:

    def get_session(self, session_id):

        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {}

        return session_id


    # ---------- INTENT ----------
    async def classify_intent(self, message: str):

        system_prompt = """
Classify the user intent.

Return ONLY JSON:

{
"intent":"EVENTS_QUERY | FACILITY_QUERY | BOOKING_REQUEST | GENERAL"
}
"""

        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )

        text = completion.choices[0].message.content.strip()

        # Extract JSON safely
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            return json.loads(json_match.group())["intent"]
        except:
            return "GENERAL"


    # ---------- AI RESPONSE ----------
    async def ai_response(self, message, data=None):

        context = f"""
User Message: {message}

Database Data:
{json.dumps(data, indent=2) if data else "None"}
"""

        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "You are a smart college campus assistant."},
                {"role": "user", "content": context}
            ]
        )

        return completion.choices[0].message.content


    # ---------- EVENTS ----------
    async def events(self):

        return await db.events.find(
            {"status": "upcoming"},
            {"_id": 0}
        ).to_list(10)


    # ---------- FACILITIES ----------
    async def facilities(self):

        return await db.facilities.find(
            {"status": "available"},
            {"_id": 0}
        ).to_list(10)


    # ---------- BOOKING ----------
    async def create_booking(self, message):

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

        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message}
            ]
        )

        text = completion.choices[0].message.content

        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            data = json.loads(json_match.group())
        except:
            return "Could not understand booking details."

        facility = await db.facilities.find_one(
            {"name": {"$regex": data["resource_name"], "$options": "i"}},
            {"_id": 0}
        )

        if not facility:
            return "Facility not found."

        booking = Booking(
            user_name="Guest",
            user_email="guest@campus.edu",
            resource_id=facility["id"],
            resource_type="facility",
            resource_name=facility["name"],
            date=data["date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            purpose=data["purpose"],
        )

        await db.bookings.insert_one(booking.model_dump())

        return booking.model_dump()


    # ---------- ROUTER ----------
    async def handle(self, message, session_id):

        session_id = self.get_session(session_id)

        intent = await self.classify_intent(message)

        if intent == "EVENTS_QUERY":

            data = await self.events()
            reply = await self.ai_response(message, data)

        elif intent == "FACILITY_QUERY":

            data = await self.facilities()
            reply = await self.ai_response(message, data)

        elif intent == "BOOKING_REQUEST":

            booking = await self.create_booking(message)
            reply = f"✅ Booking Confirmed!\n\n{json.dumps(booking, indent=2)}"

        else:
            reply = await self.ai_response(message)

        return ChatResponse(
            response=reply,
            session_id=session_id,
            intent=intent
        )


agent = CampusAIAgent()


# ================= ROUTES =================

@api_router.post("/chat", response_model=ChatResponse)
async def chat(msg: ChatMessage):

    try:
        return await agent.handle(msg.message, msg.session_id)

    except Exception as e:
        logging.exception("CHAT ERROR")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/")
async def health():
    return {"status": "Campus AI Running 🚀"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
