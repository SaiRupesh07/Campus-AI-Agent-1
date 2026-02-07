import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Loader2, Sparkles, Calendar, Building2, BookOpen } from 'lucide-react';
import { Button } from './ui/button';
import { cn } from '../lib/utils';

// ✅ SAFE API URL (works in local + production)
const API_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.3 } }
};

const messageVariants = {
  hidden: { opacity: 0, y: 10, scale: 0.95 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.3, ease: 'easeOut' } }
};

function TypingIndicator() {
  return (
    <div className="flex gap-1.5 p-4 bg-muted/30 rounded-2xl w-fit">
      <span className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce" />
      <span className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce delay-150" />
      <span className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce delay-300" />
    </div>
  );
}

function ChatMessage({ message, isUser }) {
  const time = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <motion.div
      variants={messageVariants}
      initial="hidden"
      animate="show"
      className={cn("flex gap-3 max-w-[85%]", isUser ? "ml-auto flex-row-reverse" : "mr-auto")}
    >
      <div className={cn(
        "flex items-center justify-center w-9 h-9 rounded-full flex-shrink-0",
        isUser ? "bg-emerald-500 text-white" : "bg-primary text-primary-foreground"
      )}>
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      <div className={cn("flex flex-col gap-1", isUser && "items-end")}>
        <div className={cn(
          "px-4 py-3 rounded-2xl whitespace-pre-wrap leading-relaxed",
          isUser
            ? "bg-primary text-primary-foreground rounded-tr-sm"
            : "bg-muted/50 border border-border/50 rounded-tl-sm"
        )}>
          {message.content}
        </div>
        <span className="text-xs text-muted-foreground px-1">{time}</span>
      </div>
    </motion.div>
  );
}

function QuickAction({ icon: Icon, text, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-muted/50 hover:bg-muted border border-border/50 hover:border-primary/30 transition-all text-sm font-medium"
    >
      <Icon className="w-4 h-4 text-primary" />
      <span>{text}</span>
    </motion.button>
  );
}

export function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    setMessages([{
      type: 'bot',
      content:
        "Hello! I'm your Campus AI Assistant.\n\n• Find facilities\n• Discover events\n• Book rooms\n\nHow can I help you today?",
      timestamp: new Date()
    }]);
  }, []);

  const sendMessage = async (text) => {
    const messageText = text || input;

    if (!messageText.trim() || loading) return;

    const userMessage = {
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      console.log("Connecting to:", API_URL);

      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.status}`);
      }

      const data = await response.json();

      console.log("Backend response:", data);

      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }

      const botMessage = {
        type: 'bot',
        content: data.response || "No response from assistant.",
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error("Backend connection failed:", error);

      setMessages(prev => [...prev, {
        type: 'bot',
        content:
          "⚠️ Cannot connect to the AI server.\n\nCheck:\n• Backend is running\n• CORS enabled\n• Correct Render URL",
        timestamp: new Date()
      }]);

    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="flex flex-col h-screen"
    >
      {/* Header */}
      <div className="p-4 border-b bg-background/80 backdrop-blur-lg">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-primary-foreground">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Campus AI Assistant</h1>
            <p className="text-sm text-muted-foreground">
              Ask anything about your campus
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <AnimatePresence>
          {messages.map((msg, index) => (
            <ChatMessage key={index} message={msg} isUser={msg.type === 'user'} />
          ))}
        </AnimatePresence>

        {loading && (
          <div className="flex gap-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-full bg-primary text-primary-foreground">
              <Bot className="w-5 h-5" />
            </div>
            <TypingIndicator />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-3 border-t bg-muted/20 flex gap-2 overflow-x-auto">
        <QuickAction icon={Calendar} text="Show events"
          onClick={() => sendMessage('What events are happening?')} />
        <QuickAction icon={Building2} text="Find facilities"
          onClick={() => sendMessage('Show available facilities')} />
        <QuickAction icon={BookOpen} text="Book a room"
          onClick={() => sendMessage('I want to book a room')} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t bg-background">
        <div className="flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-full bg-muted border border-border focus:border-primary outline-none"
          />

          <Button
            type="submit"
            size="icon"
            disabled={loading || !input.trim()}
            className="w-12 h-12 rounded-full"
          >
            {loading
              ? <Loader2 className="w-5 h-5 animate-spin" />
              : <Send className="w-5 h-5" />}
          </Button>
        </div>
      </form>
    </motion.div>
  );
}
