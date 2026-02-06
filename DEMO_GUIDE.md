# College Campus AI Agent - Demo & Testing Guide

## 🚀 Quick Start Demo

### 1. Access the Application

**Frontend URL**: Your deployed frontend URL or `http://localhost:3000`
**Backend API**: Your backend URL or `http://localhost:8001`
**API Documentation**: `http://localhost:8001/docs`

### 2. System Status Check

```bash
# Check all services are running
sudo supervisorctl status

# Expected output:
# backend    RUNNING
# frontend   RUNNING
# mongodb    RUNNING
```

## 🎯 Demo Scenarios

### Scenario 1: Query Campus Events

**User Action**: "What events are happening this month?"

**Expected Behavior**:
1. Agent classifies intent as `EVENTS_QUERY`
2. Retrieves events from database
3. Returns formatted list with:
   - Event name
   - Date and time
   - Location
   - Capacity and registration count
   - Tags

**Sample Response**:
```
Here are the upcoming events in March 2026:

1. 📅 Tech Symposium 2026
   Date: March 15, 2026
   Time: 10:00 - 16:00
   Location: Main Auditorium
   Capacity: 200 (45 registered)
   Tags: #technology #AI #seminar

2. 🎭 Cultural Fest
   Date: March 20, 2026
   ...
```

### Scenario 2: Find Available Facilities

**User Action**: "Show me available computer labs"

**Expected Behavior**:
1. Agent classifies intent as `FACILITY_QUERY`
2. Filters facilities by type = "lab"
3. Returns available labs with details

**Sample Response**:
```
Here are the available computer labs:

1. 💻 Computer Lab 1
   Building: Engineering Block, Floor 2
   Capacity: 50 people
   Features: computers, projector, AC, whiteboard
   Hours: Mon-Fri 09:00-18:00

2. 💻 Computer Lab 2
   ...
```

### Scenario 3: Book a Facility (Complete Flow)

**Step 1 - User Request**:
"I want to book Seminar Hall A for March 25 from 2 PM to 4 PM for a meeting"

**Expected Behavior**:
1. Agent classifies as `BOOKING_REQUEST`
2. Extracts booking details using GPT-4o
3. Validates facility exists
4. Checks operational hours
5. Checks for conflicts
6. **Requests confirmation** (key requirement!)

**Agent Response**:
```
I can help you book that. Here are the details:

📅 Date: 2026-03-25
⏰ Time: 14:00 - 16:00
🏢 Resource: Seminar Hall A
📝 Purpose: meeting

Please type 'confirm' or 'yes' to proceed with this booking, or 'cancel' to cancel.
```

**Step 2 - User Confirms**:
"confirm"

**Expected Behavior**:
1. Agent recognizes `CONFIRMATION` intent
2. Retrieves pending booking from session
3. Creates booking in database
4. Sets status to "confirmed"
5. Returns confirmation

**Agent Response**:
```
✅ Booking confirmed!

Your booking details:
- Resource: Seminar Hall A
- Date: March 25, 2026
- Time: 14:00 - 16:00
- Status: Confirmed
- Booking ID: xxx-yyy-zzz
```

### Scenario 4: Constraint Validation

**Test Case 1: Outside Operational Hours**

User: "Book Computer Lab 1 for March 10 at 10 PM"

Expected: Error message - "Outside operational hours"

**Test Case 2: Conflicting Booking**

User: "Book Seminar Hall A for March 25 at 2 PM"
(When already booked)

Expected: Error message - "Time slot already booked"

**Test Case 3: Non-existent Facility**

User: "Book the Rocket Lab for tomorrow"

Expected: Error message - "Could not find facility"

### Scenario 5: General Campus Information

**User Action**: "How can you help me?"

**Expected Behavior**:
1. Agent classifies as `GENERAL`
2. Provides helpful overview

**Agent Response**:
```
I'm your College Campus AI Assistant! I can help you with:

• 📅 Finding upcoming events and seminars
• 🏢 Checking room and lab availability
• 📝 Booking facilities for your activities
• ℹ️ General campus information

What would you like to know?
```

## 🧪 Complete Test Suite

### API Testing with cURL

```bash
# Test 1: Health Check
curl http://localhost:8001/api/

# Test 2: Get All Events
curl http://localhost:8001/api/events

# Test 3: Get All Facilities
curl http://localhost:8001/api/facilities

# Test 4: Chat - Events Query
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What events are happening?"}'

# Test 5: Chat - Facility Query
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me available facilities"}'

# Test 6: Chat - Booking Request (save session_id from response)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book Computer Lab 1 for April 1 at 3 PM"}'

# Test 7: Chat - Confirm Booking (use session_id from Test 6)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "confirm", "session_id": "YOUR_SESSION_ID"}'

# Test 8: Verify Booking Created
curl http://localhost:8001/api/bookings
```

### Frontend UI Testing

**Manual Test Checklist**:

1. **Chat Interface**
   - [ ] Welcome message displays
   - [ ] Can type and send messages
   - [ ] Bot responses appear
   - [ ] Messages scroll automatically
   - [ ] Loading indicator shows during processing

2. **Quick Actions**
   - [ ] "Show events" button works
   - [ ] "Find facilities" button works
   - [ ] "Book a room" button works
   - [ ] Buttons populate input field correctly

3. **Events Tab**
   - [ ] All events display in cards
   - [ ] Event details are complete
   - [ ] Tags display correctly
   - [ ] Capacity shows correctly

4. **Facilities Tab**
   - [ ] All facilities display
   - [ ] Features list shows
   - [ ] Status badges appear
   - [ ] Building/floor info visible

5. **Bookings Tab**
   - [ ] All bookings display
   - [ ] Status badges show correctly
   - [ ] User info displays
   - [ ] Date/time shows properly

6. **Navigation**
   - [ ] Tab switching works smoothly
   - [ ] Active tab highlighted
   - [ ] Content updates correctly

7. **Responsive Design**
   - [ ] Mobile view works
   - [ ] Tablet view works
   - [ ] Desktop view works

## 📊 Expected Data

### Sample Events (Seeded)

```
1. Tech Symposium 2026 - March 15
2. Cultural Fest - March 20
3. Python Workshop - March 10
```

### Sample Facilities (Seeded)

```
1. Computer Lab 1 - Engineering Block
2. Seminar Hall A - Academic Block
3. Main Auditorium - Central Block
4. Basketball Court - Sports Complex
```

## 🔍 Verification Points

### Agent Decision Making

**Intent Classification**:
- [x] Correctly identifies EVENTS_QUERY
- [x] Correctly identifies FACILITY_QUERY
- [x] Correctly identifies BOOKING_REQUEST
- [x] Correctly identifies CONFIRMATION
- [x] Handles ambiguous queries

**System Routing**:
- [x] Routes to Events System for event queries
- [x] Routes to Facilities System for facility queries
- [x] Routes to Booking System for booking requests
- [x] Handles multi-system queries

**Constraint Validation**:
- [x] Checks facility existence
- [x] Validates operational hours
- [x] Detects booking conflicts
- [x] Validates date/time format

**Confirmation Management**:
- [x] Requires confirmation for bookings
- [x] Stores pending action in session
- [x] Waits for user response
- [x] Executes only after confirmation
- [x] Allows cancellation

## 🎬 Live Demo Script

### Introduction (30 seconds)
```
"This is the College Campus AI Agent, an intelligent assistant powered by 
OpenAI GPT-4o. It helps students and staff with events, facilities, and 
bookings using natural language."
```

### Demo 1: Events (45 seconds)
```
1. Show chat interface
2. Type: "What events are happening?"
3. Show agent understanding and retrieving data
4. Highlight formatted response with event details
```

### Demo 2: Facilities (45 seconds)
```
1. Type: "Show me computer labs"
2. Show facility query with features
3. Switch to Facilities tab
4. Show visual cards with all facilities
```

### Demo 3: Booking Flow (90 seconds)
```
1. Type: "Book Seminar Hall A for March 28 at 3 PM for presentation"
2. **Highlight**: Agent requests confirmation (requirement!)
3. Show booking details displayed
4. Type: "confirm"
5. Show success message
6. Switch to Bookings tab
7. Show booking created with confirmed status
```

### Demo 4: Validation (30 seconds)
```
1. Try booking same slot again
2. Show error: "Already booked"
3. **Highlight**: Constraint validation working
```

### Conclusion (30 seconds)
```
"The agent demonstrates:
- Natural language understanding
- Intent classification
- Multi-system integration
- Constraint validation
- Required confirmation flow
- All assignment requirements met!"
```

## 📸 Screenshot Checklist

For documentation, capture:

1. **Chat Interface**
   - Welcome message
   - Event query response
   - Facility query response
   - Booking confirmation prompt
   - Booking success message

2. **Events Tab**
   - Grid view of events
   - Event cards with details

3. **Facilities Tab**
   - Facility cards
   - Features and status

4. **Bookings Tab**
   - Booking list
   - Status badges

5. **Architecture Diagram**
   - System components (from ARCHITECTURE.md)

6. **Flow Diagram**
   - Booking flow (from FLOW_DIAGRAMS.md)

## 🐛 Troubleshooting

### Issue: Backend not responding
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Restart
sudo supervisorctl restart backend
```

### Issue: Frontend not loading
```bash
# Check logs
tail -f /var/log/supervisor/frontend.err.log

# Restart
sudo supervisorctl restart frontend
```

### Issue: MongoDB connection error
```bash
# Check MongoDB status
sudo supervisorctl status mongodb

# Restart
sudo supervisorctl restart mongodb
```

### Issue: LLM API errors
```bash
# Verify API key in .env
cat /app/backend/.env | grep EMERGENT_LLM_KEY

# Check for rate limiting in logs
```

## ✅ Assignment Submission Checklist

Before submitting:

- [ ] All services running
- [ ] Chat working with all intents
- [ ] Booking flow with confirmation working
- [ ] Constraint validation working
- [ ] UI displays correctly
- [ ] All documentation complete
- [ ] README is comprehensive
- [ ] Architecture diagrams included
- [ ] Flow diagrams included
- [ ] .env.example files created
- [ ] .gitignore configured
- [ ] No sensitive keys in repository
- [ ] GitHub repository is public
- [ ] All code is well-commented

## 🎓 Assignment Requirements Mapping

| Requirement | Implementation | Status |
|------------|----------------|---------|
| Intent identification | GPT-4o classifier | ✅ |
| Multi-system data retrieval | Events/Facilities/Bookings DBs | ✅ |
| Availability checking | Constraint validator | ✅ |
| User confirmation | Confirmation handler | ✅ |
| System routing decision | Intent router | ✅ |
| Constraint validation | Validation engine | ✅ |
| Complete architecture | ARCHITECTURE.md | ✅ |
| Flow diagrams | FLOW_DIAGRAMS.md | ✅ |
| Framework justification | README.md + ARCHITECTURE.md | ✅ |
| Working implementation | Full-stack app | ✅ |

---

**Ready for submission!** All assignment requirements are met and demonstrated.
