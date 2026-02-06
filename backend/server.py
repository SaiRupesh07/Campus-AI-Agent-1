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
from datetime import datetime, timezone, time
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
from dateutil import parser as date_parser


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="College Campus AI Agent API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# In-memory session storage (in production, use Redis)
sessions: Dict[str, Dict[str, Any]] = {}

# ==================== DATA MODELS ====================

class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    event_type: str  # seminar, workshop, fest, exam, sports
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    location: str
    capacity: int
    registered_count: int = 0
    status: str = "upcoming"  # upcoming, ongoing, completed, cancelled
    organizer: str
    tags: List[str] = []

class EventCreate(BaseModel):
    name: str
    description: str
    event_type: str
    date: str
    start_time: str
    end_time: str
    location: str
    capacity: int
    organizer: str
    tags: List[str] = []

class Facility(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # classroom, lab, auditorium, sports, library
    building: str
    floor: int
    capacity: int
    features: List[str] = []  # projector, AC, whiteboard, computers
    operational_hours: Dict[str, str] = {}  # {"monday": "09:00-18:00"}
    status: str = "available"  # available, occupied, maintenance

class FacilityCreate(BaseModel):
    name: str
    type: str
    building: str
    floor: int
    capacity: int
    features: List[str] = []
    operational_hours: Dict[str, str] = {}

class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_name: str
    user_email: str
    resource_id: str
    resource_type: str  # facility, event
    resource_name: str
    date: str
    start_time: str
    end_time: str
    purpose: str
    status: str = "pending"  # pending, confirmed, rejected, cancelled
    requires_confirmation: bool = True
    confirmed_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class BookingRequest(BaseModel):
    user_name: str
    user_email: str
    resource_id: str
    resource_type: str
    date: str
    start_time: str
    end_time: str
    purpose: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: Optional[str] = None
    data: Optional[Any] = None
    requires_confirmation: bool = False

# ==================== AI AGENT LOGIC ====================

class CampusAIAgent:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    def get_or_create_session(self, session_id: Optional[str]) -> tuple:
        """Get existing session or create new one"""
        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                "messages": [],
                "pending_confirmation": None,
                "context": {}
            }
        return session_id, sessions[session_id]
    
    async def classify_intent(self, message: str, session_id: str) -> Dict[str, Any]:
        """Use GPT-4o to classify user intent"""
        system_message = """You are an intent classifier for a college campus AI agent.
Analyze the user's message and classify it into one of these intents:
- EVENTS_QUERY: User asking about events, seminars, workshops
- FACILITY_QUERY: User asking about rooms, labs, facilities availability
- BOOKING_REQUEST: User wants to book a facility or register for event
- CONFIRMATION: User confirming or denying a previous action
- GENERAL: General questions about campus

Return ONLY a JSON object with this structure:
{
    "intent": "<intent_name>",
    "entities": {
        "date": "<extracted date if any>",
        "time": "<extracted time if any>",
        "facility_type": "<room/lab type if mentioned>",
        "event_type": "<event type if mentioned>",
        "keywords": ["<relevant keywords>"]
    },
    "confidence": <0.0 to 1.0>
}"""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"intent_{session_id}",
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=f"Classify this message: {message}")
        response = await chat.send_message(user_message)
        
        try:
            # Parse JSON response
            intent_data = json.loads(response)
            return intent_data
        except json.JSONDecodeError:
            # Fallback
            return {
                "intent": "GENERAL",
                "entities": {},
                "confidence": 0.5
            }
    
    async def generate_response(self, intent: str, data: Any, message: str, session_id: str) -> str:
        """Generate natural language response using GPT-4o"""
        system_message = """You are a helpful college campus assistant.
Generate a natural, friendly response based on the data provided.
Keep responses concise but informative.
If showing events or facilities, format them nicely.
If there's a booking confirmation needed, clearly ask for confirmation."""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"response_{session_id}",
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        context = f"""
User asked: {message}
Intent: {intent}
Data retrieved: {json.dumps(data, indent=2) if data else 'None'}

Generate an appropriate response."""
        
        user_message = UserMessage(text=context)
        response = await chat.send_message(user_message)
        
        return response
    
    async def handle_message(self, message: str, session_id: Optional[str]) -> ChatResponse:
        """Main message handling logic"""
        session_id, session = self.get_or_create_session(session_id)
        
        # Check if waiting for confirmation
        if session.get("pending_confirmation"):
            if message.lower() in ["yes", "confirm", "proceed", "ok", "sure"]:
                # Execute pending action
                result = await self.execute_booking(session["pending_confirmation"])
                session["pending_confirmation"] = None
                response_text = await self.generate_response(
                    "BOOKING_CONFIRMED",
                    result,
                    message,
                    session_id
                )
                return ChatResponse(
                    response=response_text,
                    session_id=session_id,
                    intent="BOOKING_CONFIRMED",
                    data=result,
                    requires_confirmation=False
                )
            elif message.lower() in ["no", "cancel", "nevermind"]:
                session["pending_confirmation"] = None
                return ChatResponse(
                    response="Booking cancelled. How else can I help you?",
                    session_id=session_id,
                    intent="BOOKING_CANCELLED",
                    requires_confirmation=False
                )
        
        # Classify intent
        intent_data = await self.classify_intent(message, session_id)
        intent = intent_data.get("intent", "GENERAL")
        entities = intent_data.get("entities", {})
        
        # Route to appropriate handler
        if intent == "EVENTS_QUERY":
            data = await self.handle_events_query(entities)
            response_text = await self.generate_response(intent, data, message, session_id)
            return ChatResponse(
                response=response_text,
                session_id=session_id,
                intent=intent,
                data=data
            )
        
        elif intent == "FACILITY_QUERY":
            data = await self.handle_facility_query(entities)
            response_text = await self.generate_response(intent, data, message, session_id)
            return ChatResponse(
                response=response_text,
                session_id=session_id,
                intent=intent,
                data=data
            )
        
        elif intent == "BOOKING_REQUEST":
            # This requires confirmation
            validation = await self.validate_booking_request(entities, message)
            if validation["valid"]:
                session["pending_confirmation"] = validation["booking_data"]
                response_text = f"""I can help you book that. Here are the details:

📅 Date: {validation['booking_data'].get('date', 'Not specified')}
⏰ Time: {validation['booking_data'].get('start_time', '')} - {validation['booking_data'].get('end_time', '')}
🏢 Resource: {validation['booking_data'].get('resource_name', 'Not specified')}
📝 Purpose: {validation['booking_data'].get('purpose', 'General use')}

Please type 'confirm' or 'yes' to proceed with this booking, or 'cancel' to cancel."""
                return ChatResponse(
                    response=response_text,
                    session_id=session_id,
                    intent=intent,
                    data=validation["booking_data"],
                    requires_confirmation=True
                )
            else:
                return ChatResponse(
                    response=validation["message"],
                    session_id=session_id,
                    intent="BOOKING_ERROR",
                    data=None,
                    requires_confirmation=False
                )
        
        else:  # GENERAL
            response_text = await self.generate_response(intent, None, message, session_id)
            return ChatResponse(
                response=response_text,
                session_id=session_id,
                intent=intent
            )
    
    async def handle_events_query(self, entities: Dict) -> List[Dict]:
        """Retrieve events from database"""
        query = {}
        
        if entities.get("event_type"):
            query["event_type"] = {"$regex": entities["event_type"], "$options": "i"}
        
        if entities.get("date"):
            query["date"] = entities["date"]
        
        # Get upcoming events
        query["status"] = "upcoming"
        
        events = await db.events.find(query, {"_id": 0}).limit(10).to_list(10)
        return events
    
    async def handle_facility_query(self, entities: Dict) -> List[Dict]:
        """Retrieve facilities from database"""
        query = {}
        
        if entities.get("facility_type"):
            query["type"] = {"$regex": entities["facility_type"], "$options": "i"}
        
        query["status"] = "available"
        
        facilities = await db.facilities.find(query, {"_id": 0}).limit(10).to_list(10)
        return facilities
    
    async def validate_booking_request(self, entities: Dict, message: str) -> Dict:
        """Validate booking request and prepare booking data"""
        # Extract booking details using GPT-4o
        system_message = """Extract booking details from the user message.
Return JSON with: resource_name, date (YYYY-MM-DD), start_time (HH:MM), end_time (HH:MM), purpose"""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="booking_extract",
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        try:
            booking_data = json.loads(response)
            
            # Validate constraints
            if not booking_data.get("date") or not booking_data.get("start_time"):
                return {
                    "valid": False,
                    "message": "Please provide a date and time for your booking."
                }
            
            # Check facility availability
            facility_query = {"name": {"$regex": booking_data.get("resource_name", ""), "$options": "i"}}
            facility = await db.facilities.find_one(facility_query, {"_id": 0})
            
            if not facility:
                return {
                    "valid": False,
                    "message": f"Could not find facility '{booking_data.get('resource_name')}'. Please check the name."
                }
            
            # Check for conflicting bookings
            conflict = await db.bookings.find_one({
                "resource_id": facility["id"],
                "date": booking_data["date"],
                "status": {"$in": ["confirmed", "pending"]},
                "$or": [
                    {"start_time": {"$lte": booking_data["start_time"]}, "end_time": {"$gt": booking_data["start_time"]}},
                    {"start_time": {"$lt": booking_data["end_time"]}, "end_time": {"$gte": booking_data["end_time"]}}
                ]
            })
            
            if conflict:
                return {
                    "valid": False,
                    "message": "This facility is already booked for that time slot. Please choose a different time."
                }
            
            booking_data["resource_id"] = facility["id"]
            booking_data["resource_type"] = "facility"
            booking_data["user_name"] = "Guest User"  # In real app, get from auth
            booking_data["user_email"] = "guest@campus.edu"
            
            return {
                "valid": True,
                "booking_data": booking_data
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": f"Could not process booking request. Please provide more details. Error: {str(e)}"
            }
    
    async def execute_booking(self, booking_data: Dict) -> Dict:
        """Execute the confirmed booking"""
        booking = Booking(**booking_data)
        booking.status = "confirmed"
        booking.confirmed_at = datetime.now(timezone.utc).isoformat()
        
        doc = booking.model_dump()
        await db.bookings.insert_one(doc)
        
        return doc

# Initialize agent
agent = CampusAIAgent()

# ==================== API ENDPOINTS ====================

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """Main chat endpoint for the AI agent"""
    try:
        response = await agent.handle_message(request.message, request.session_id)
        return response
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/events", response_model=List[Event])
async def get_events(event_type: Optional[str] = None, date: Optional[str] = None):
    """Get all events"""
    query = {"status": "upcoming"}
    if event_type:
        query["event_type"] = event_type
    if date:
        query["date"] = date
    
    events = await db.events.find(query, {"_id": 0}).to_list(100)
    return events

@api_router.post("/events", response_model=Event)
async def create_event(event: EventCreate):
    """Create a new event"""
    event_obj = Event(**event.model_dump())
    doc = event_obj.model_dump()
    await db.events.insert_one(doc)
    return event_obj

@api_router.get("/facilities", response_model=List[Facility])
async def get_facilities(facility_type: Optional[str] = None):
    """Get all facilities"""
    query = {}
    if facility_type:
        query["type"] = facility_type
    
    facilities = await db.facilities.find(query, {"_id": 0}).to_list(100)
    return facilities

@api_router.post("/facilities", response_model=Facility)
async def create_facility(facility: FacilityCreate):
    """Create a new facility"""
    facility_obj = Facility(**facility.model_dump())
    doc = facility_obj.model_dump()
    await db.facilities.insert_one(doc)
    return facility_obj

@api_router.get("/bookings", response_model=List[Booking])
async def get_bookings(status: Optional[str] = None):
    """Get all bookings"""
    query = {}
    if status:
        query["status"] = status
    
    bookings = await db.bookings.find(query, {"_id": 0}).to_list(100)
    return bookings

@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking_req: BookingRequest):
    """Create a booking (direct, without confirmation)"""
    booking = Booking(**booking_req.model_dump(), resource_name="")
    
    # Get resource name
    if booking_req.resource_type == "facility":
        facility = await db.facilities.find_one({"id": booking_req.resource_id}, {"_id": 0})
        if facility:
            booking.resource_name = facility["name"]
    
    booking.status = "confirmed"
    booking.confirmed_at = datetime.now(timezone.utc).isoformat()
    
    doc = booking.model_dump()
    await db.bookings.insert_one(doc)
    return booking

@api_router.get("/availability")
async def check_availability(resource_id: str, date: str):
    """Check availability for a resource on a given date"""
    bookings = await db.bookings.find({
        "resource_id": resource_id,
        "date": date,
        "status": {"$in": ["confirmed", "pending"]}
    }, {"_id": 0}).to_list(100)
    
    return {
        "resource_id": resource_id,
        "date": date,
        "bookings": bookings,
        "available": len(bookings) == 0
    }

# Health check
@api_router.get("/")
async def root():
    return {
        "message": "College Campus AI Agent API",
        "status": "operational",
        "version": "1.0.0"
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# ==================== SEED DATA FUNCTION ====================

async def seed_initial_data():
    """Seed database with sample data"""
    # Check if data already exists
    event_count = await db.events.count_documents({})
    if event_count > 0:
        return
    
    # Sample events
    sample_events = [
        {
            "id": str(uuid.uuid4()),
            "name": "Tech Symposium 2026",
            "description": "Annual technology symposium featuring AI and ML talks",
            "event_type": "seminar",
            "date": "2026-03-15",
            "start_time": "10:00",
            "end_time": "16:00",
            "location": "Main Auditorium",
            "capacity": 200,
            "registered_count": 45,
            "status": "upcoming",
            "organizer": "CS Department",
            "tags": ["technology", "AI", "seminar"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cultural Fest",
            "description": "Annual cultural festival with music, dance, and drama",
            "event_type": "fest",
            "date": "2026-03-20",
            "start_time": "09:00",
            "end_time": "18:00",
            "location": "Open Ground",
            "capacity": 500,
            "registered_count": 230,
            "status": "upcoming",
            "organizer": "Cultural Committee",
            "tags": ["cultural", "fest", "entertainment"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Python Workshop",
            "description": "Hands-on Python programming workshop for beginners",
            "event_type": "workshop",
            "date": "2026-03-10",
            "start_time": "14:00",
            "end_time": "17:00",
            "location": "Computer Lab 2",
            "capacity": 40,
            "registered_count": 38,
            "status": "upcoming",
            "organizer": "Coding Club",
            "tags": ["programming", "python", "workshop"]
        }
    ]
    
    # Sample facilities
    sample_facilities = [
        {
            "id": str(uuid.uuid4()),
            "name": "Computer Lab 1",
            "type": "lab",
            "building": "Engineering Block",
            "floor": 2,
            "capacity": 50,
            "features": ["computers", "projector", "AC", "whiteboard"],
            "operational_hours": {
                "monday": "09:00-18:00",
                "tuesday": "09:00-18:00",
                "wednesday": "09:00-18:00",
                "thursday": "09:00-18:00",
                "friday": "09:00-18:00"
            },
            "status": "available"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Seminar Hall A",
            "type": "classroom",
            "building": "Academic Block",
            "floor": 1,
            "capacity": 100,
            "features": ["projector", "AC", "sound_system", "podium"],
            "operational_hours": {
                "monday": "08:00-20:00",
                "tuesday": "08:00-20:00",
                "wednesday": "08:00-20:00",
                "thursday": "08:00-20:00",
                "friday": "08:00-20:00",
                "saturday": "09:00-17:00"
            },
            "status": "available"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Main Auditorium",
            "type": "auditorium",
            "building": "Central Block",
            "floor": 1,
            "capacity": 300,
            "features": ["projector", "AC", "sound_system", "stage", "lighting"],
            "operational_hours": {
                "monday": "08:00-22:00",
                "tuesday": "08:00-22:00",
                "wednesday": "08:00-22:00",
                "thursday": "08:00-22:00",
                "friday": "08:00-22:00",
                "saturday": "09:00-22:00",
                "sunday": "10:00-20:00"
            },
            "status": "available"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Basketball Court",
            "type": "sports",
            "building": "Sports Complex",
            "floor": 0,
            "capacity": 20,
            "features": ["outdoor", "floodlights", "seating"],
            "operational_hours": {
                "monday": "06:00-22:00",
                "tuesday": "06:00-22:00",
                "wednesday": "06:00-22:00",
                "thursday": "06:00-22:00",
                "friday": "06:00-22:00",
                "saturday": "06:00-22:00",
                "sunday": "06:00-22:00"
            },
            "status": "available"
        }
    ]
    
    # Insert data
    await db.events.insert_many(sample_events)
    await db.facilities.insert_many(sample_facilities)
    
    logger.info("Sample data seeded successfully")

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    await seed_initial_data()
    logger.info("Application started successfully")
