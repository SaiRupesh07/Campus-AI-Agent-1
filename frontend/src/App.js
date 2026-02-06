import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { Bot, Send, User, Calendar, Building2, BookOpen, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_BASE;


function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [events, setEvents] = useState([]);
  const [facilities, setFacilities] = useState([]);
  const [bookings, setBookings] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    setMessages([{
      type: 'bot',
      content: "👋 Hi! I'm your College Campus AI Assistant. I can help you with:\n\n• 📅 Upcoming events and seminars\n• 🏢 Room and lab availability\n• 📝 Facility bookings\n• ℹ️ Campus information\n\nHow can I help you today?",
      timestamp: new Date()
    }]);

    // Load initial data
    loadEvents();
    loadFacilities();
    loadBookings();
  }, []);

  const loadEvents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/events`);
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Error loading events:', error);
    }
  };

  const loadFacilities = async () => {
    try {
      const response = await fetch(`${API_URL}/api/facilities`);
      const data = await response.json();
      setFacilities(data);
    } catch (error) {
      console.error('Error loading facilities:', error);
    }
  };

  const loadBookings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/bookings`);
      const data = await response.json();
      setBookings(data);
    } catch (error) {
      console.error('Error loading bookings:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId
        })
      });

      const data = await response.json();
      
      if (!sessionId) {
        setSessionId(data.session_id);
      }

      const botMessage = {
        type: 'bot',
        content: data.response,
        timestamp: new Date(),
        intent: data.intent,
        data: data.data,
        requires_confirmation: data.requires_confirmation
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Reload data if booking was made
      if (data.intent === 'BOOKING_CONFIRMED') {
        loadBookings();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'bot',
        content: '❌ Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const QuickAction = ({ icon: Icon, text, onClick }) => (
    <button
      onClick={onClick}
      className="quick-action"
      data-testid={`quick-action-${text.toLowerCase().replace(/ /g, '-')}`}
    >
      <Icon size={16} />
      <span>{text}</span>
    </button>
  );

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="header-title">
            <Bot size={32} className="header-icon" />
            <div>
              <h1>Campus AI Agent</h1>
              <p>Your intelligent campus assistant</p>
            </div>
          </div>
          <div className="header-tabs">
            <button
              className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
              data-testid="tab-chat"
            >
              💬 Chat
            </button>
            <button
              className={`tab ${activeTab === 'events' ? 'active' : ''}`}
              onClick={() => setActiveTab('events')}
              data-testid="tab-events"
            >
              📅 Events
            </button>
            <button
              className={`tab ${activeTab === 'facilities' ? 'active' : ''}`}
              onClick={() => setActiveTab('facilities')}
              data-testid="tab-facilities"
            >
              🏢 Facilities
            </button>
            <button
              className={`tab ${activeTab === 'bookings' ? 'active' : ''}`}
              onClick={() => setActiveTab('bookings')}
              data-testid="tab-bookings"
            >
              📝 Bookings
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {activeTab === 'chat' && (
          <div className="chat-container">
            <div className="messages" data-testid="messages-container">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`message ${msg.type}`}
                  data-testid={`message-${msg.type}-${index}`}
                >
                  <div className="message-icon">
                    {msg.type === 'bot' ? <Bot size={20} /> : <User size={20} />}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{msg.content}</div>
                    <div className="message-time">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message bot" data-testid="loading-message">
                  <div className="message-icon">
                    <Bot size={20} />
                  </div>
                  <div className="message-content">
                    <div className="message-text">
                      <Loader2 className="spinner" size={16} />
                      Thinking...
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="quick-actions">
              <QuickAction
                icon={Calendar}
                text="Show events"
                onClick={() => setInput('What events are happening?')}
              />
              <QuickAction
                icon={Building2}
                text="Find facilities"
                onClick={() => setInput('Show me available facilities')}
              />
              <QuickAction
                icon={BookOpen}
                text="Book a room"
                onClick={() => setInput('I want to book a room')}
              />
            </div>

            <form onSubmit={sendMessage} className="input-form">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message here..."
                className="message-input"
                disabled={loading}
                data-testid="message-input"
              />
              <button
                type="submit"
                className="send-button"
                disabled={loading || !input.trim()}
                data-testid="send-button"
              >
                <Send size={20} />
              </button>
            </form>
          </div>
        )}

        {activeTab === 'events' && (
          <div className="data-grid" data-testid="events-grid">
            <div className="data-header">
              <h2>📅 Upcoming Events</h2>
              <p>{events.length} events scheduled</p>
            </div>
            <div className="cards-grid">
              {events.map((event) => (
                <div key={event.id} className="card" data-testid={`event-card-${event.id}`}>
                  <div className="card-header">
                    <h3>{event.name}</h3>
                    <span className="badge">{event.event_type}</span>
                  </div>
                  <p className="card-description">{event.description}</p>
                  <div className="card-details">
                    <div className="detail">
                      <Calendar size={16} />
                      <span>{event.date}</span>
                    </div>
                    <div className="detail">
                      <span>⏰ {event.start_time} - {event.end_time}</span>
                    </div>
                    <div className="detail">
                      <span>📍 {event.location}</span>
                    </div>
                    <div className="detail">
                      <span>👥 {event.registered_count}/{event.capacity} registered</span>
                    </div>
                  </div>
                  {event.tags && event.tags.length > 0 && (
                    <div className="tags">
                      {event.tags.map((tag, i) => (
                        <span key={i} className="tag">#{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'facilities' && (
          <div className="data-grid" data-testid="facilities-grid">
            <div className="data-header">
              <h2>🏢 Campus Facilities</h2>
              <p>{facilities.length} facilities available</p>
            </div>
            <div className="cards-grid">
              {facilities.map((facility) => (
                <div key={facility.id} className="card" data-testid={`facility-card-${facility.id}`}>
                  <div className="card-header">
                    <h3>{facility.name}</h3>
                    <span className={`badge ${facility.status}`}>{facility.status}</span>
                  </div>
                  <div className="card-details">
                    <div className="detail">
                      <Building2 size={16} />
                      <span>{facility.building} - Floor {facility.floor}</span>
                    </div>
                    <div className="detail">
                      <span>💺 Capacity: {facility.capacity}</span>
                    </div>
                    <div className="detail">
                      <span>🏷️ Type: {facility.type}</span>
                    </div>
                  </div>
                  {facility.features && facility.features.length > 0 && (
                    <div className="tags">
                      {facility.features.map((feature, i) => (
                        <span key={i} className="tag">✓ {feature}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'bookings' && (
          <div className="data-grid" data-testid="bookings-grid">
            <div className="data-header">
              <h2>📝 Recent Bookings</h2>
              <p>{bookings.length} bookings</p>
            </div>
            <div className="cards-grid">
              {bookings.map((booking) => (
                <div key={booking.id} className="card" data-testid={`booking-card-${booking.id}`}>
                  <div className="card-header">
                    <h3>{booking.resource_name || booking.resource_id}</h3>
                    <span className={`badge ${booking.status}`}>{booking.status}</span>
                  </div>
                  <div className="card-details">
                    <div className="detail">
                      <User size={16} />
                      <span>{booking.user_name}</span>
                    </div>
                    <div className="detail">
                      <Calendar size={16} />
                      <span>{booking.date}</span>
                    </div>
                    <div className="detail">
                      <span>⏰ {booking.start_time} - {booking.end_time}</span>
                    </div>
                    <div className="detail">
                      <span>📝 {booking.purpose}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>College Campus AI Agent • Powered by GPT-4o • Built with FastAPI & React</p>
      </footer>
    </div>
  );
}

export default App;
