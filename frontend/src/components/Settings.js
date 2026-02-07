import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { useTheme } from '../context/ThemeContext';
import { Moon, Sun, Bell, Globe, Shield, User, Palette } from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
};

function SettingItem({ icon: Icon, title, description, children }) {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl hover:bg-muted/50 transition-colors">
      <div className="flex items-center gap-4">
        <div className="p-2 rounded-lg bg-primary/10 text-primary">
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <Label className="text-sm font-medium">{title}</Label>
          <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
        </div>
      </div>
      {children}
    </div>
  );
}

export function Settings() {
  const { theme, toggleTheme } = useTheme();
  const [notifications, setNotifications] = React.useState(true);

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="p-4 md:p-6 lg:p-8 space-y-6 max-w-3xl"
      data-testid="settings-page"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your preferences and account settings</p>
      </motion.div>

      {/* Appearance */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="w-5 h-5 text-primary" />
              Appearance
            </CardTitle>
            <CardDescription>Customize how CampusAI looks on your device</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <SettingItem
              icon={theme === 'dark' ? Moon : Sun}
              title="Dark Mode"
              description="Toggle between light and dark theme"
            >
              <Switch 
                checked={theme === 'dark'} 
                onCheckedChange={toggleTheme}
                data-testid="dark-mode-switch"
              />
            </SettingItem>
          </CardContent>
        </Card>
      </motion.div>

      {/* Notifications */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary" />
              Notifications
            </CardTitle>
            <CardDescription>Configure notification preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <SettingItem
              icon={Bell}
              title="Push Notifications"
              description="Receive notifications about bookings and events"
            >
              <Switch 
                checked={notifications} 
                onCheckedChange={setNotifications}
                data-testid="notifications-switch"
              />
            </SettingItem>
          </CardContent>
        </Card>
      </motion.div>

      {/* Account */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5 text-primary" />
              Account
            </CardTitle>
            <CardDescription>Manage your account settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <SettingItem
              icon={Globe}
              title="Language"
              description="Set your preferred language"
            >
              <Button variant="outline" size="sm">English</Button>
            </SettingItem>
            <SettingItem
              icon={Shield}
              title="Privacy"
              description="Manage your privacy settings"
            >
              <Button variant="outline" size="sm">Manage</Button>
            </SettingItem>
          </CardContent>
        </Card>
      </motion.div>

      {/* About */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-sm text-muted-foreground">
              CampusAI v1.0.0 • Built with React & FastAPI
            </p>
            <p className="text-xs text-muted-foreground mt-2">
              Your intelligent campus assistant
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
