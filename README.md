#  Campus AI Agent 🎓🤖

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Modern-blue.svg)](https://reactjs.org/)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange.svg)](https://groq.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-green.svg)](https://mongodb.com/)

> 🚀 **Live AI-powered campus assistant that understands natural language, retrieves data across systems, and executes real-world booking workflows.**

---

## 🌐 Live Deployment

### 🔥 Try the App Now

- **Frontend:** [https://YOUR-VERCEL-LINK.vercel.app](https://campus-ai-agent-1.vercel.app/)
- **Backend API:** [https://YOUR-RENDER-LINK.onrender.com](https://campus-ai-agent.onrender.com/)
- **Swagger Docs:** [https://YOUR-RENDER-LINK.onrender.com/docs](https://campus-ai-agent.onrender.com/docs)

*(Replace with your actual deployment links)*

---

## 🎯 Project Overview

The **College Campus AI Agent** is a production-style intelligent assistant designed to automate campus operations using Large Language Models. It enables students and faculty to interact with campus systems using simple conversational language.

### ✅ Core Capabilities

- 🧠 **Natural Language Understanding** — Powered by Groq Llama-3 for ultra-fast inference
- 📅 **Event Discovery** — Fetch upcoming seminars, workshops, and fests
- 🏢 **Facility Intelligence** — Search labs, classrooms, and auditoriums
- 📌 **Smart Booking Engine** — Validate availability before confirming reservations
- 🔒 **Constraint Enforcement** — Prevent double bookings & invalid time slots
- 💬 **Session-Based Conversations** — Maintains booking context during chat

---

## 🧠 Why This Project Stands Out

Unlike basic chatbots, this system behaves like a **true AI agent**:

✅ Routes queries to the correct internal system  
✅ Makes decisions based on constraints  
✅ Requests confirmation before executing actions  
✅ Retrieves real-time database results  
✅ Generates structured human-like responses  

👉 This mirrors how **modern enterprise AI assistants** are built.

---

## 🏗️ Architecture

See **ARCHITECTURE.md** for detailed system design and decision flow.

### High-Level Flow

```
User → AI Agent → Intent Detection → Tool Execution → Constraint Validation → Response
```

---

## 🛠️ Technology Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async APIs |
| **Groq (Llama-3)** | Lightning-fast LLM inference |
| **MongoDB** | Flexible NoSQL database |
| **Motor** | Async DB driver |
| **Pydantic** | Data validation |

### Frontend

| Technology | Purpose |
|------------|---------|
| **React** | Interactive UI |
| **Tailwind CSS** | Modern styling |
| **Radix UI** | Accessible components |

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account
- Groq API Key

### 🔧 Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn server:app --reload
```

Backend runs on: `http://localhost:8000`  
API Documentation: `http://localhost:8000/docs`

### 💻 Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

Frontend runs on: `http://localhost:3000`

---

## 🔑 Environment Variables

Create a `.env` file inside the `backend` directory:

```env
MONGO_URL=your_mongodb_connection_string
DB_NAME=campus_ai
GROQ_API_KEY=your_groq_api_key
```

---

## 📊 Database Schema

### Events Collection

```json
{
  "id": "uuid",
  "name": "Tech Symposium",
  "event_type": "seminar",
  "date": "2026-03-15",
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
  "capacity": 50,
  "features": ["computers", "projector"],
  "status": "available"
}
```

### Bookings Collection

```json
{
  "id": "uuid",
  "resource_name": "Computer Lab 1",
  "date": "2026-03-10",
  "start_time": "14:00",
  "end_time": "16:00",
  "status": "confirmed"
}
```

---

## 🔌 API Endpoints

### Chat Endpoint

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Show me available labs"
}
```

### Other Routes

- `GET /api/events` - Retrieve all events
- `POST /api/events` - Create a new event
- `GET /api/facilities` - Retrieve all facilities
- `POST /api/facilities` - Add a new facility
- `GET /api/bookings` - Retrieve all bookings
- `POST /api/bookings` - Create a new booking
- `GET /api/availability` - Check resource availability

---

## 🎯 Usage Examples

### Event Query

```
User: What events are happening this week?
```

👉 Agent returns structured event list with details

### Facility Search

```
User: Show available computer labs
```

👉 Agent fetches real-time database results

### Smart Booking

```
User: Book Computer Lab 1 tomorrow from 2–4 PM
```

Agent workflow:
1. ✅ Extracts booking details
2. ✅ Validates availability
3. ✅ Requests confirmation
4. ✅ Creates booking

---

## 🧪 Testing

### API Test with cURL

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What events are happening?"}'
```

---

## 📚 Documentation

- **Architecture Diagram** → See `ARCHITECTURE.md`
- **API Documentation** → Available at `/docs` endpoint (Swagger UI)

---

## 🎓 Engineering Highlights

✅ Agent-style architecture  
✅ Multi-system data retrieval  
✅ Constraint-aware decision making  
✅ Production deployment ready  
✅ Async backend for performance  
✅ Tool-based execution model  

👉 This project reflects **real-world AI system design principles**

---

## 🔮 Future Improvements

- [ ] Vector search for semantic retrieval
- [ ] Authentication & role-based booking permissions
- [ ] Redis memory store for conversation history
- [ ] Multi-agent orchestration
- [ ] Voice assistant support
- [ ] Email/SMS notifications for bookings
- [ ] Calendar integration (Google Calendar, Outlook)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Devarinti Sai Rupesh**

Building production-grade AI systems focused on real-world automation.

- GitHub: [@your-github-username](https://github.com/SaiRupesh07)
- LinkedIn: [Your LinkedIn](https://www.linkedin.com/in/sai-rupesh-devarinti/)
- Email: devarintisairupesh840@gmail.com

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for ultra-fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [MongoDB](https://mongodb.com/) for flexible data storage
- The open-source community

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ by Devarinti Sai Rupesh**
