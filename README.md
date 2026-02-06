# College Campus AI Agent 🎓🤖

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.1-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0.0-blue.svg)](https://reactjs.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-black.svg)](https://openai.com/)

An intelligent AI agent for college campus management that provides information on events, facilities, and handles booking requests with natural language understanding.

## 🎯 Project Overview

This project implements a complete AI-powered assistant for college campuses that:

- **Understands Natural Language**: Uses OpenAI GPT-4o for intent detection and response generation
- **Manages Events**: Provides information about upcoming campus events, seminars, and workshops
- **Handles Facilities**: Shows available rooms, labs, and campus facilities
- **Processes Bookings**: Validates and confirms facility bookings with explicit user confirmation
- **Validates Constraints**: Checks availability, operational hours, and prevents double bookings

## 📋 Assignment Requirements Fulfilled

### ✅ Functional Requirements

1. **Intent Identification**: AI agent identifies whether requests relate to:
   - Events information
   - Facilities queries
   - Booking requests
   - General campus information

2. **Multi-System Data Retrieval**: 
   - Retrieves event data from events database
   - Fetches facility information from facilities database
   - Manages bookings in separate booking system

3. **Availability & Constraint Checking**:
   - Validates operational hours for facilities
   - Checks for conflicting bookings
   - Verifies capacity constraints
   - Ensures date/time validity

4. **User Confirmation**:
   - Requires explicit confirmation before creating bookings
   - Displays booking details for user review
   - Allows cancellation before confirmation

### ✅ Expected Agent Behavior

1. **System Routing**: Agent decides which internal system to consult based on intent
2. **Constraint Validation**: Determines when availability checks are required
3. **Confirmation Management**: Decides when explicit user confirmation is mandatory

## 🏗️ Architecture

See `ARCHITECTURE.md` for detailed architecture documentation.

## 🛠️ Technology Stack & Justification

### Backend

| Technology | Version | Justification |
|------------|---------|---------------|
| **FastAPI** | 0.110.1 | High-performance async Python framework |
| **OpenAI GPT-4o** | Latest | Best-in-class natural language understanding |
| **MongoDB** | 4.5.0 | Flexible schema for dynamic data models |
| **Motor** | 3.3.1 | Async MongoDB driver |
| **Emergentintegrations** | 0.1.0 | Unified LLM API interface |

### Frontend

| Technology | Version | Justification |
|------------|---------|---------------|
| **React** | 19.0.0 | Modern UI framework |
| **Tailwind CSS** | 3.4.17 | Utility-first CSS |
| **Radix UI** | Latest | Accessible components |

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB
- Emergent LLM Key (provided in .env)

### Quick Start

```bash
# Start all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

## 📊 Database Schema

### Events Collection

```json
{
  "id": "uuid",
  "name": "Tech Symposium 2026",
  "event_type": "seminar",
  "date": "2026-03-15",
  "start_time": "10:00",
  "end_time": "16:00",
  "location": "Main Auditorium",
  "capacity": 200,
  "status": "upcoming"
}
```

### Facilities Collection

```json
{
  "id": "uuid",
  "name": "Computer Lab 1",
  "type": "lab",
  "building": "Engineering Block",
  "capacity": 50,
  "features": ["computers", "projector", "AC"],
  "status": "available"
}
```

### Bookings Collection

```json
{
  "id": "uuid",
  "user_name": "John Doe",
  "resource_id": "facility-uuid",
  "date": "2026-03-10",
  "start_time": "14:00",
  "end_time": "16:00",
  "status": "confirmed"
}
```

## 🔌 API Endpoints

### Chat Endpoint

```http
POST /api/chat
Content-Type: application/json

{
  "message": "What events are happening next week?",
  "session_id": "optional-session-id"
}
```

### Other Endpoints

- `GET /api/events` - List all events
- `POST /api/events` - Create new event
- `GET /api/facilities` - List all facilities
- `POST /api/facilities` - Create new facility
- `GET /api/bookings` - List all bookings
- `POST /api/bookings` - Create booking
- `GET /api/availability` - Check availability

## 🎯 Usage Examples

### Example 1: Event Query

```
User: "What events are happening this month?"
Agent: Lists all upcoming events with details
```

### Example 2: Facility Query

```
User: "Show me available computer labs"
Agent: Shows all computer labs with capacity and features
```

### Example 3: Booking with Confirmation

```
User: "I want to book Computer Lab 1 for March 10 from 2 PM to 4 PM"
Agent: Shows booking details and requests confirmation
User: "confirm"
Agent: Creates booking and provides confirmation
```

## 🧪 Testing

### API Testing

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What events are happening?"}'
```

### UI Testing

All interactive elements include `data-testid` attributes for automated testing.

## 📚 Documentation

- **ARCHITECTURE.md**: Detailed architecture and system design
- **API Docs**: Auto-generated at `/docs` endpoint when backend is running

## 🎓 Assignment Submission Checklist

- ✅ Complete AI agent architecture designed
- ✅ Flow diagram showing all decision points
- ✅ Intent detection implemented (GPT-4o)
- ✅ Data retrieval from multiple systems
- ✅ Constraint validation engine
- ✅ User confirmation flow
- ✅ Response generation
- ✅ Working implementation with UI
- ✅ Framework justification documented
- ✅ Sample data and demonstrations
- ✅ Comprehensive documentation

## 📝 License

Created for educational purposes as part of an AI/ML assignment.

## 👨‍💻 Author

Developed as a comprehensive solution for the College Campus AI Agent assignment.
