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

    # ✅ TOOL DEFINITIONS (UPGRADED)
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
                "description": "Fetch available campus facilities. Use facility_type when user specifies labs, classrooms, auditoriums, sports, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "facility_type": {
                            "type": "string",
                            "description": "Type of facility such as lab, classroom, auditorium, sports"
                        }
                    }
                }
            }
        }
    ]

    # ================= UNIVERSAL LLM =================

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
                "history": []
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
            query["type"] = {"$regex": facility_type, "$options": "i"}

        return await db.facilities.find(
            query,
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
            raw = self.call_llm(messages).content or ""
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
        history = session["history"]

        # ✅ Confirmation flow
        if session.get("pending_confirmation"):

            if message.lower() in ["yes", "confirm", "ok"]:
                result = await self.execute_booking(session["pending_confirmation"])
                session["pending_confirmation"] = None

                reply = "✅ Booking Confirmed!"

                history.append({"role": "assistant", "content": reply})

                return ChatResponse(
                    response=reply,
                    session_id=session_id,
                    intent="BOOKING_CONFIRMED",
                    data=result
                )

            elif message.lower() in ["no", "cancel"]:
                session["pending_confirmation"] = None

                reply = "Booking cancelled 👍"

                history.append({"role": "assistant", "content": reply})

                return ChatResponse(
                    response=reply,
                    session_id=session_id
                )

        # ✅ SYSTEM PROMPT WITH MEMORY
        messages = [
            {
                "role": "system",
                "content": """
You are a smart AI assistant for a college campus.

Remember conversation context.
Resolve references like:
- "book it"
- "that lab"
- "tomorrow"

Use tools when needed.
Do NOT hallucinate data.
"""
            }
        ]

        messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.call_llm(messages, tools=self.TOOLS)

        # ✅ TOOL CALL DETECTED
        if response.tool_calls:

            tool_call = response.tool_calls[0]
            tool_name = tool_call.function.name

            args = {}
            if tool_call.function.arguments:
                try:
                    args = json.loads(tool_call.function.arguments)
                except:
                    args = {}

            if tool_name == "get_events":
                data = await self.get_events()

            elif tool_name == "get_facilities":
                facility_type = args.get("facility_type")
                data = await self.get_facilities(facility_type)

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

            # save memory
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": reply})

            if len(history) > 12:
                history.pop(0)
                history.pop(0)

            return ChatResponse(
                response=reply,
                session_id=session_id,
                intent=tool_name,
                data=data
            )

        # ✅ Booking fallback
        if "book" in message.lower():

            validation = await self.validate_booking_request(message)

            if validation["valid"]:
                session["pending_confirmation"] = validation["booking_data"]

                reply = f"""
I can help you book this facility:

{json.dumps(validation["booking_data"], indent=2)}

Type YES to confirm.
"""

                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": reply})

                return ChatResponse(
                    response=reply,
                    session_id=session_id,
                    intent="BOOKING_REQUEST",
                    requires_confirmation=True
                )
            else:
                reply = validation["message"]

        else:
            reply = response.content or "How can I assist you?"

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})

        if len(history) > 12:
            history.pop(0)
            history.pop(0)

        return ChatResponse(
            response=reply,
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
