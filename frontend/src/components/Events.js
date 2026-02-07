import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Calendar, Clock, MapPin, Users, Tag } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
};

const eventImages = [
  'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=400&h=200&fit=crop',
  'https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=400&h=200&fit=crop',
  'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=400&h=200&fit=crop',
  'https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=400&h=200&fit=crop',
  'https://images.unsplash.com/photo-1591115765373-5207764f72e4?w=400&h=200&fit=crop',
];

function EventCard({ event, index }) {
  const imageUrl = eventImages[index % eventImages.length];
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      <Card className="group overflow-hidden hover:border-primary/50 transition-all duration-300 hover:shadow-xl h-full">
        {/* Image */}
        <div className="aspect-video w-full overflow-hidden bg-muted relative">
          <img 
            src={imageUrl} 
            alt={event.name}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute top-3 right-3">
            <span className="px-3 py-1 text-xs font-semibold rounded-full bg-primary text-primary-foreground">
              {event.event_type}
            </span>
          </div>
        </div>
        
        <CardHeader className="pb-2">
          <CardTitle className="text-lg line-clamp-1">{event.name}</CardTitle>
          <CardDescription className="line-clamp-2">{event.description}</CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-primary" />
              <span>{event.date}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-primary" />
              <span>{event.start_time} - {event.end_time}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin className="w-4 h-4 text-primary" />
            <span>{event.location}</span>
          </div>
          
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <Users className="w-4 h-4 text-primary" />
            <span>{event.registered_count}/{event.capacity} registered</span>
          </div>

          {event.tags && event.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2 border-t">
              {event.tags.map((tag, i) => (
                <span key={i} className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-muted text-muted-foreground">
                  <Tag className="w-3 h-3" />
                  {tag}
                </span>
              ))}
            </div>
          )}

          <Button 
            className="w-full mt-2 rounded-full" 
            data-testid={`event-register-${event.id}`}
          >
            Register Now
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function Events() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/events`);
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Error loading events:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="p-4 md:p-6 lg:p-8 space-y-6"
      data-testid="events-page"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Events</h1>
        <p className="text-muted-foreground mt-1">{events.length} upcoming events on campus</p>
      </motion.div>

      {/* Events Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <div className="aspect-video bg-muted" />
              <CardContent className="p-6 space-y-4">
                <div className="h-4 bg-muted rounded w-3/4" />
                <div className="h-3 bg-muted rounded w-full" />
                <div className="h-3 bg-muted rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : events.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {events.map((event, index) => (
            <EventCard key={event.id} event={event} index={index} />
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <Calendar className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold">No Events Found</h3>
          <p className="text-muted-foreground">Check back later for upcoming events.</p>
        </Card>
      )}
    </motion.div>
  );
}
