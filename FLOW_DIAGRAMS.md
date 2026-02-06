# College Campus AI Agent - Flow Diagrams

This document contains detailed flow diagrams for the AI agent system.

## 1. Complete System Flow

```
┌──────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                  (Web Browser / Mobile)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ User Message
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  FRONTEND (React)                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Chat Interface                                        │ │
│  │  - Message input                                       │ │
│  │  - Message display                                     │ │
│  │  - Quick actions                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ POST /api/chat
                         │ { message, session_id }
                         ▼
┌──────────────────────────────────────────────────────────────┐
│               BACKEND API (FastAPI)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  API Gateway                                           │ │
│  │  - Request validation                                  │ │
│  │  - CORS handling                                       │ │
│  │  - Error handling                                      │ │
│  └──────────────────────┬─────────────────────────────────┘ │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         CampusAIAgent (Main Logic)                     │ │
│  │                                                        │ │
│  │  Step 1: Get/Create Session                           │ │
│  │  ↓                                                     │ │
│  │  Step 2: Check for Pending Confirmation               │ │
│  │  ↓          ↓                                          │ │
│  │  YES       NO                                          │ │
│  │  │          │                                          │ │
│  │  │          Step 3: Classify Intent (GPT-4o)          │ │
│  │  │          ↓                                          │ │
│  │  │          Intent Type Decision                      │ │
│  │  │          ├── EVENTS_QUERY                          │ │
│  │  │          ├── FACILITY_QUERY                        │ │
│  │  │          ├── BOOKING_REQUEST                       │ │
│  │  │          └── GENERAL                               │ │
│  │  │          │                                          │ │
│  │  Execute   Step 4: Route to Handler                   │ │
│  │  Pending   │                                          │ │
│  │  Action    ▼                                          │ │
│  │  │         ┌─────────────────────────────────┐       │ │
│  │  │         │  Intent Handler                  │       │ │
│  │  │         │  - Query Database                │       │ │
│  │  │         │  - Validate Constraints          │       │ │
│  │  │         │  - Check Confirmation Needed     │       │ │
│  │  │         └──────────┬──────────────────────┘       │ │
│  │  │                    │                               │ │
│  │  │                    ▼                               │ │
│  │  │         Confirmation Required?                     │ │
│  │  │                    │                               │ │
│  │  │              YES   │   NO                          │ │
│  │  │              ├─────┴─────┐                         │ │
│  │  │              ▼           ▼                         │ │
│  │  │         Store Pending   Execute                    │ │
│  │  │         in Session      Action                     │ │
│  │  │              │           │                         │ │
│  │  └──────────────┴───────────┘                         │ │
│  │                 │                                     │ │
│  │                 ▼                                     │ │
│  │  Step 5: Generate Response (GPT-4o)                  │ │
│  │  ↓                                                    │ │
│  │  Step 6: Return Response                             │ │
│  └────────────────────┬───────────────────────────────┘ │
└────────────────────────┼─────────────────────────────────┘
                         │
                         │ Response
                         │ { response, session_id, intent, data }
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  - Display bot response                                      │
│  - Update UI based on intent                                 │
│  - Show confirmation dialog if needed                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
                     USER sees response
```

## 2. Intent Classification Flow

```
┌─────────────────────┐
│   User Message      │
│  "Book Lab 1 for    │
│   March 10 2PM"     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  GPT-4o Intent Classifier           │
│                                     │
│  System Prompt:                     │
│  "You are an intent classifier..."  │
│                                     │
│  Input: User message                │
│  Output: JSON                       │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Classification Result (JSON)       │
│  {                                  │
│    "intent": "BOOKING_REQUEST",     │
│    "entities": {                    │
│      "facility": "Lab 1",           │
│      "date": "2026-03-10",          │
│      "time": "14:00"                │
│    },                               │
│    "confidence": 0.95               │
│  }                                  │
└──────────┬──────────────────────────┘
           │
           ▼
      Intent Router
           │
     ┌─────┴──────┬──────────┬──────────┐
     │            │          │          │
     ▼            ▼          ▼          ▼
  EVENTS    FACILITY    BOOKING    GENERAL
  Handler   Handler     Handler    Handler
```

## 3. Booking Request Flow (Detailed)

```
┌──────────────────────────────────┐
│ User: "Book Lab 1 for March 10"  │
└────────────┬─────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 1: Intent Classification            │
│ Result: BOOKING_REQUEST                  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 2: Extract Booking Details          │
│ Using GPT-4o to parse:                   │
│ - Resource: "Lab 1"                      │
│ - Date: "2026-03-10"                     │
│ - Time: "14:00-16:00" (inferred)         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 3: Validate Resource Exists         │
│ Query: facilities.find({name: "Lab 1"}) │
│ Result: Found                            │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 4: Check Operational Hours          │
│ Lab 1 hours: Mon-Fri 09:00-18:00        │
│ Requested: March 10, 14:00              │
│ Result: ✓ Within hours                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 5: Check for Conflicts              │
│ Query: bookings.find({                   │
│   resource_id: "lab1",                   │
│   date: "2026-03-10",                    │
│   time_overlap: true                     │
│ })                                       │
│ Result: No conflicts                     │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 6: Store Pending Confirmation       │
│ session["pending_confirmation"] = {      │
│   resource: "Lab 1",                     │
│   date: "2026-03-10",                    │
│   time: "14:00-16:00"                    │
│ }                                        │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 7: Request User Confirmation        │
│ Response: "I can help you book that...   │
│ Please type 'confirm' to proceed"        │
└────────────┬────────────────────────────┘
             │
             ▼
       User Response
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
    "confirm"   "cancel"
       │           │
       │           ▼
       │     Cancel booking
       │     Clear session
       │           │
       │           ▼
       │     "Booking cancelled"
       │
       ▼
┌─────────────────────────────────────────┐
│ Step 8: Execute Booking                  │
│ - Create booking record                  │
│ - Set status: "confirmed"                │
│ - Save to database                       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 9: Generate Confirmation Response   │
│ "✓ Booking confirmed!                    │
│  Resource: Lab 1                         │
│  Date: March 10, 2026                    │
│  Time: 14:00-16:00                       │
│  Booking ID: xxx-yyy-zzz"                │
└─────────────────────────────────────────┘
```

## 4. Constraint Validation Flow

```
┌─────────────────────────────────┐
│  Booking Request Received        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Constraint 1: Resource Exists?           │
│ Query database for facility/event        │
└────────────┬────────────────────────────┘
             │
        ┌────┴────┐
        │         │
       YES       NO
        │         │
        │         ▼
        │    Return Error:
        │    "Resource not found"
        │
        ▼
┌─────────────────────────────────────────┐
│ Constraint 2: Within Operational Hours?  │
│ Check facility operational_hours         │
└────────────┬────────────────────────────┘
             │
        ┌────┴────┐
        │         │
       YES       NO
        │         │
        │         ▼
        │    Return Error:
        │    "Outside operational hours"
        │
        ▼
┌─────────────────────────────────────────┐
│ Constraint 3: No Time Conflicts?         │
│ Query existing bookings for overlap      │
└────────────┬────────────────────────────┘
             │
        ┌────┴────┐
        │         │
       YES       NO
        │         │
        │         ▼
        │    Return Error:
        │    "Time slot already booked"
        │
        ▼
┌─────────────────────────────────────────┐
│ Constraint 4: Valid Date/Time Format?    │
│ Validate date is future, format correct  │
└────────────┬────────────────────────────┘
             │
        ┌────┴────┐
        │         │
       YES       NO
        │         │
        │         ▼
        │    Return Error:
        │    "Invalid date/time"
        │
        ▼
┌─────────────────────────────────────────┐
│ All Constraints Passed                   │
│ Proceed with booking                     │
└─────────────────────────────────────────┘
```

## 5. Data Retrieval Flow

```
┌─────────────────────────────────┐
│  Intent: EVENTS_QUERY            │
│  Entities: {type: "seminar"}     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Build Database Query                     │
│ query = {                                │
│   "event_type": "seminar",               │
│   "status": "upcoming"                   │
│ }                                        │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Execute Query                            │
│ events = db.events.find(query)           │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Process Results                          │
│ - Sort by date                           │
│ - Limit to 10 results                    │
│ - Format for response                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Generate Natural Language Response       │
│ Using GPT-4o:                            │
│ "Here are the upcoming seminars..."      │
│ + formatted event list                   │
└─────────────────────────────────────────┘
```

## 6. Session Management Flow

```
┌─────────────────────────────────┐
│  Incoming Request                │
│  session_id: "abc-123" or null   │
└────────────┬────────────────────┘
             │
             ▼
        Session ID exists?
             │
        ┌────┴────┐
        │         │
       YES       NO
        │         │
        │         ▼
        │    Generate new UUID
        │    Create session entry
        │    {
        │      messages: [],
        │      pending: null,
        │      context: {}
        │    }
        │         │
        └────┬────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Load Session Data                        │
│ session = sessions[session_id]           │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Process Message with Context             │
│ - Access conversation history            │
│ - Check pending confirmations            │
│ - Update session state                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Return Response with session_id          │
│ Client stores session_id for next request│
└─────────────────────────────────────────┘
```

## 7. Multi-System Integration Flow

```
┌─────────────────────────────────┐
│     User Query Received          │
│  "Show seminar in Lab 1 on       │
│   March 10 at 2 PM"              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Intent Classification                    │
│ Result: Complex query needs multiple     │
│         systems                          │
└────────────┬────────────────────────────┘
             │
             ▼
      Agent Decision:
      Need to query multiple systems
             │
     ┌───────┴───────┬───────────────┐
     │               │               │
     ▼               ▼               ▼
┌─────────┐   ┌──────────┐   ┌───────────┐
│ Events  │   │Facilities│   │ Bookings  │
│ System  │   │ System   │   │ System    │
└────┬────┘   └────┬─────┘   └─────┬─────┘
     │             │               │
     │ seminars    │ Lab 1 info    │ Lab 1
     │ in March    │ & availability│ bookings
     │             │               │ March 10
     └─────────────┴───────────────┘
                   │
                   ▼
         Combine & Cross-reference
                   │
                   ▼
┌─────────────────────────────────────────┐
│ Generate Comprehensive Response          │
│ "There is a Python Workshop on March 10  │
│  from 2-5 PM in Computer Lab 1.          │
│  The lab has 40 capacity with computers. │
│  Currently 38 registered."               │
└─────────────────────────────────────────┘
```

## 8. Error Handling Flow

```
┌─────────────────────────────────┐
│  Request Processing              │
└────────────┬────────────────────┘
             │
             ▼
        Try: Process
             │
        ┌────┴────┐
        │         │
    SUCCESS    ERROR
        │         │
        │         ▼
        │    Catch Exception Type
        │         │
        │    ┌────┴────┬─────────┬──────────┐
        │    │         │         │          │
        │  Network  Database  LLM API   Other
        │  Error    Error     Error     Error
        │    │         │         │          │
        │    ▼         ▼         ▼          ▼
        │  Log &    Log &     Log &      Log &
        │  Return   Return    Return     Return
        │  Error    Error     Error      Error
        │    │         │         │          │
        └────┴─────────┴─────────┴──────────┘
                       │
                       ▼
┌─────────────────────────────────────────┐
│ Generate User-Friendly Error Message    │
│ Using GPT-4o:                           │
│ "Sorry, I encountered an issue.         │
│  Please try again or contact support."  │
└─────────────────────────────────────────┘
```

---

## Summary

This flow diagram document illustrates:

1. **Complete System Flow**: End-to-end request processing
2. **Intent Classification**: How user messages are understood
3. **Booking Request Flow**: Detailed booking process with confirmation
4. **Constraint Validation**: Multi-level validation checks
5. **Data Retrieval**: How data is fetched from databases
6. **Session Management**: Conversation context handling
7. **Multi-System Integration**: Coordinating multiple data sources
8. **Error Handling**: Graceful error management

Each flow demonstrates the agent's decision-making process and how it routes requests through the appropriate systems while maintaining user confirmation requirements and constraint validation.
