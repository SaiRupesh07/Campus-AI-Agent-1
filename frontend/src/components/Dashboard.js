import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Calendar, Building2, MessageSquare, Users, TrendingUp, Clock } from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
};

const stats = [
  { label: 'Upcoming Events', value: '12', icon: Calendar, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { label: 'Available Facilities', value: '8', icon: Building2, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  { label: 'Chat Sessions', value: '156', icon: MessageSquare, color: 'text-violet-500', bg: 'bg-violet-500/10' },
  { label: 'Active Users', value: '2.4k', icon: Users, color: 'text-amber-500', bg: 'bg-amber-500/10' },
];

const recentActivity = [
  { action: 'Booked Computer Lab 1', time: '2 min ago', icon: Building2 },
  { action: 'Registered for Tech Symposium', time: '15 min ago', icon: Calendar },
  { action: 'AI Assistant conversation', time: '1 hour ago', icon: MessageSquare },
  { action: 'Updated facility preferences', time: '3 hours ago', icon: TrendingUp },
];

export function Dashboard() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="p-4 md:p-6 lg:p-8 space-y-6"
      data-testid="dashboard-page"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Welcome back! Here's what's happening on campus.</p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div 
        variants={containerVariants}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div key={stat.label} variants={itemVariants}>
              <Card className="group hover:border-primary/50 transition-all duration-300 hover:shadow-lg">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                      <p className="text-3xl font-bold mt-2">{stat.value}</p>
                    </div>
                    <div className={`p-3 rounded-xl ${stat.bg} ${stat.color} group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-6 h-6" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-3">
              {[
                { label: 'Book a Room', icon: Building2, color: 'bg-emerald-500' },
                { label: 'View Events', icon: Calendar, color: 'bg-blue-500' },
                { label: 'Chat with AI', icon: MessageSquare, color: 'bg-violet-500' },
                { label: 'My Bookings', icon: Clock, color: 'bg-amber-500' },
              ].map((action) => {
                const Icon = action.icon;
                return (
                  <motion.button
                    key={action.label}
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex items-center gap-3 p-4 rounded-xl bg-muted/50 hover:bg-muted transition-colors border border-transparent hover:border-primary/20"
                    data-testid={`quick-action-${action.label.toLowerCase().replace(/ /g, '-')}`}
                  >
                    <div className={`p-2 rounded-lg ${action.color} text-white`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="font-medium text-sm">{action.label}</span>
                  </motion.button>
                );
              })}
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Activity */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentActivity.map((activity, index) => {
                const Icon = activity.icon;
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="p-2 rounded-lg bg-primary/10 text-primary">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{activity.action}</p>
                      <p className="text-sm text-muted-foreground">{activity.time}</p>
                    </div>
                  </motion.div>
                );
              })}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
