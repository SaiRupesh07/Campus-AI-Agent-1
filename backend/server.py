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

    # ⭐ FIXED INTENT MAP (Recruiter-level detail)
    INTENT_MAP = {
        "get_events": "EVENTS_QUERY",
        "get_facilities": "FACILITY_QUERY"
    }

    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "get_events",
                "description": "Fetch upcoming campus events",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_facilities",
                "description": "Fetch campus facilities. ALWAYS pass facility_type if user mentions labs, classrooms, auditoriums, sports etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "facility_type": {
                            "type": "string",
                            "description": "Facility type like lab, classroom, auditorium, sports"
                        }
                    }
                }
            }
        }
    ]

    # ================= LLM =================

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

    # ================= SESSION =================

    def get_or_create_session(self, session_id):

        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())

            sessions[session_id] = {
                "pending_confirmation": None,
                "history": [],
                "booking_state": None   # ⭐ NEW
            }

        return session_id, sessions[session_id]

    # ================= DATABASE =================

    async def get_events(self):
        return await db.events.find(
            {"status": "upcoming"},
            {"_id": 0}
        ).limit(10).to_list(10)

    async def get_facilities(self, facility_type=None):

        query = {"status": "available"}

        if facility_type:
            query["type"] = {
                "$regex": facility_type,
                "$options": "i"
            }

        data = await db.facilities.find(
            query,
            {"_id": 0}
        ).limit(10).to_list(10)

        # ⭐ Safety fallback
        if not data and facility_type:
            data = await db.facilities.find(
                {"status": "available"},
                {"_id": 0}
            ).limit(10).to_list(10)

        return data

    # ================= BOOKING FLOW =================

    def start_booking_flow(self, session):
        session["booking_state"] = {
            "step": "facility",
            "data": {}
        }

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
        history = session["history"]

        # ✅ MULTI STEP BOOKING FLOW
        if session.get("booking_state"):

            state = session["booking_state"]
            step = state["step"]

            if step == "facility":
                state["data"]["resource_name"] = message
                state["step"] = "date"

                return ChatResponse(
                    response="Great 👍 Which date do you want to book it for?",
                    session_id=session_id,
                    intent="BOOKING_FLOW"
                )

            elif step == "date":
                state["data"]["date"] = message
                state["step"] = "time"

                return ChatResponse(
                    response="What time slot do you need?",
                    session_id=session_id,
                    intent="BOOKING_FLOW"
                )

            elif step == "time":
                state["data"]["start_time"] = message
                state["step"] = "purpose"

                return ChatResponse(
                    response="What is the purpose of the booking?",
                    session_id=session_id,
                    intent="BOOKING_FLOW"
                )

            elif step == "purpose":

                booking_data = state["data"]
                session["booking_state"] = None

                facility = await db.facilities.find_one(
                    {"name": {"$regex": booking_data.get("resource_name", ""), "$options": "i"}},
                    {"_id": 0}
                )

                if not facility:
                    return ChatResponse(
                        response="Facility not found.",
                        session_id=session_id
                    )

                booking_data.update({
                    "resource_id": facility["id"],
                    "resource_type": "facility",
                    "user_name": "Guest User",
                    "user_email": "guest@campus.edu",
                    "end_time": booking_data["start_time"]
                })

                session["pending_confirmation"] = booking_data

                return ChatResponse(
                    response=f"""
I can book this for you:

{json.dumps(booking_data, indent=2)}

Type YES to confirm.
""",
                    session_id=session_id,
                    intent="BOOKING_REQUEST",
                    requires_confirmation=True
                )

        # ✅ Confirmation
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

        # ⭐ Start booking trigger
        if "book" in message.lower():
            self.start_booking_flow(session)

            return ChatResponse(
                response="Sure! Which facility would you like to book?",
                session_id=session_id,
                intent="BOOKING_FLOW"
            )

        # ================= TOOL AGENT =================

        messages = [
            {
                "role": "system",
                "content": """
You are a smart AI assistant for a college campus.

Use tools whenever possible.
Do NOT hallucinate.
"""
            }
        ]

        messages.extend(history[-6:])
        messages.append({"role": "user", "content": message})

        response = self.call_llm(messages, tools=self.TOOLS)

        if response.tool_calls:

            tool_call = response.tool_calls[0]
            tool_name = tool_call.function.name

            args = {}
            if tool_call.function.arguments:
                try:
                    args = json.loads(tool_call.function.arguments)
                except:
                    pass

            if tool_name == "get_events":
                data = await self.get_events()

            elif tool_name == "get_facilities":
                data = await self.get_facilities(args.get("facility_type"))

            else:
                data = {}

            messages.append(response)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(data)
            })

            final = self.call_llm(messages)
            reply = final.content or "Here is what I found."

            history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": reply}
            ])

            return ChatResponse(
                response=reply,
                session_id=session_id,
                intent=self.INTENT_MAP.get(tool_name, "GENERAL"),
                data=data
            )

        return ChatResponse(
            response=response.content or "How can I assist you?",
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
