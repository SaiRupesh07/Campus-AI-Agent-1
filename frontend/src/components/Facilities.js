import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Building2, MapPin, Users, CheckCircle2, Wifi, MonitorPlay, Wind, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
};

const facilityImages = {
  'lab': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&h=200&fit=crop',
  'classroom': 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=400&h=200&fit=crop',
  'auditorium': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=200&fit=crop',
  'sports': 'https://images.unsplash.com/photo-1546483875-ad9014c88eba?w=400&h=200&fit=crop',
  'library': 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=400&h=200&fit=crop',
  'default': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=200&fit=crop',
};

const featureIcons = {
  'wifi': Wifi,
  'projector': MonitorPlay,
  'ac': Wind,
  'computers': MonitorPlay,
};

function BookingModal({ facility, open, onClose }) {
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    purpose: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate booking - in real app, this would call the API
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setLoading(false);
    setSuccess(true);
    
    setTimeout(() => {
      setSuccess(false);
      onClose();
      setFormData({ date: '', time: '', purpose: '' });
    }, 2000);
  };

  if (!facility) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]" data-testid="booking-modal">
        {success ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="py-12 text-center"
          >
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <CheckCircle2 className="w-8 h-8 text-emerald-500" />
            </div>
            <h3 className="text-xl font-semibold">Booking Confirmed!</h3>
            <p className="text-muted-foreground mt-2">Your booking for {facility.name} has been submitted.</p>
          </motion.div>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="text-xl">Book {facility.name}</DialogTitle>
              <DialogDescription>
                Fill in the details below to book this facility.
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  required
                  data-testid="booking-date-input"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="time">Time</Label>
                <Input
                  id="time"
                  type="time"
                  value={formData.time}
                  onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                  required
                  data-testid="booking-time-input"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="purpose">Purpose</Label>
                <textarea
                  id="purpose"
                  value={formData.purpose}
                  onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
                  placeholder="Describe the purpose of your booking..."
                  required
                  rows={3}
                  className="w-full px-3 py-2 rounded-md border border-input bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                  data-testid="booking-purpose-input"
                />
              </div>
              
              <DialogFooter className="pt-4">
                <Button type="button" variant="outline" onClick={onClose} data-testid="booking-cancel-btn">
                  Cancel
                </Button>
                <Button type="submit" disabled={loading} data-testid="booking-confirm-btn">
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      Booking...
                    </>
                  ) : (
                    'Confirm Booking'
                  )}
                </Button>
              </DialogFooter>
            </form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

function FacilityCard({ facility, onBook, index }) {
  const imageUrl = facilityImages[facility.type?.toLowerCase()] || facilityImages.default;
  const statusColor = facility.status === 'available' ? 'bg-emerald-500' : 'bg-amber-500';
  
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
            alt={facility.name}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute top-3 right-3">
            <span className={`px-3 py-1 text-xs font-semibold rounded-full ${statusColor} text-white capitalize`}>
              {facility.status}
            </span>
          </div>
        </div>
        
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary" />
            {facility.name}
          </CardTitle>
          <CardDescription>{facility.type}</CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-3">
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin className="w-4 h-4 text-primary" />
            <span>{facility.building} - Floor {facility.floor}</span>
          </div>
          
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <Users className="w-4 h-4 text-primary" />
            <span>Capacity: {facility.capacity}</span>
          </div>

          {facility.features && facility.features.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2 border-t">
              {facility.features.map((feature, i) => {
                const Icon = featureIcons[feature.toLowerCase()] || CheckCircle2;
                return (
                  <span key={i} className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-muted text-muted-foreground">
                    <Icon className="w-3 h-3" />
                    {feature}
                  </span>
                );
              })}
            </div>
          )}

          <Button 
            className="w-full mt-2 rounded-full"
            onClick={() => onBook(facility)}
            disabled={facility.status !== 'available'}
            data-testid={`facility-book-${facility.id}`}
          >
            {facility.status === 'available' ? 'Book Now' : 'Not Available'}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function Facilities() {
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFacility, setSelectedFacility] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    loadFacilities();
  }, []);

  const loadFacilities = async () => {
    try {
      const response = await fetch(`${API_URL}/api/facilities`);
      const data = await response.json();
      setFacilities(data);
    } catch (error) {
      console.error('Error loading facilities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBook = (facility) => {
    setSelectedFacility(facility);
    setModalOpen(true);
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="p-4 md:p-6 lg:p-8 space-y-6"
      data-testid="facilities-page"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Facilities</h1>
        <p className="text-muted-foreground mt-1">{facilities.length} facilities available for booking</p>
      </motion.div>

      {/* Facilities Grid */}
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
      ) : facilities.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {facilities.map((facility, index) => (
            <FacilityCard key={facility.id} facility={facility} onBook={handleBook} index={index} />
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <Building2 className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold">No Facilities Found</h3>
          <p className="text-muted-foreground">No facilities are currently available.</p>
        </Card>
      )}

      {/* Booking Modal */}
      <BookingModal 
        facility={selectedFacility}
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedFacility(null);
        }}
      />
    </motion.div>
  );
}
