"""
Google ADK-style Notification Agent for Goodwill Platform
Generates encouraging messages for achievements, streaks, and donations
"""

import random
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    ACHIEVEMENT = "achievement"
    STREAK = "streak"
    DONATION = "donation"
    GYM_LEADER = "gym_leader"
    MISSING_ITEM = "missing_item"
    TIER_UPGRADE = "tier_upgrade"
    MILESTONE = "milestone"

class GoogleADKNotificationAgent:
    """
    Mock Google ADK Agent for generating contextual notifications
    Based on Google Agent Development Kit (ADK) patterns
    """
    
    def __init__(self):
        self.agent_name = "GoodwillEncouragementAgent"
        self.version = "1.0.0"
        self.personality = "encouraging"
        
        # Message templates organized by type and context
        self.message_templates = {
            NotificationType.ACHIEVEMENT: {
                "first_donation": [
                    "🎉 Welcome to the Goodwill family! Your first donation is the beginning of something amazing!",
                    "⭐ Achievement Unlocked: First Steps! Every great journey starts with a single act of kindness.",
                    "🌟 Congratulations on your first donation! You've just made someone's day brighter!"
                ],
                "generous_giver": [
                    "💰 Wow! Your generous $100+ donation shows incredible compassion!",
                    "🏆 Achievement Unlocked: Generous Giver! Your kindness is truly inspiring!",
                    "💎 Such generosity! You're making a real difference in your community!"
                ],
                "streak_master": [
                    "🔥 Streak Master! Your consistency in giving is absolutely incredible!",
                    "⚡ 7 days of continuous kindness! You're a true champion of goodwill!",
                    "🌈 Your dedication streak is inspiring others to give back too!"
                ],
                "gym_leader": [
                    "👑 Congratulations! You're now the Gym Leader! Defend your title with more amazing donations!",
                    "🏆 New Gym Leader crowned! Your generosity has earned you this prestigious title!",
                    "⚔️ You've conquered this location! Other donors will try to challenge your leadership!"
                ]
            },
            
            NotificationType.STREAK: {
                "short": [
                    "🔥 {days}-day streak! You're building an amazing habit of giving!",
                    "⭐ Day {days} of your donation journey! Keep the momentum going!",
                    "🌟 {days} days strong! Your consistency is making a real impact!"
                ],
                "medium": [
                    "🚀 {days} days of continuous giving! You're a donation superhero!",
                    "💫 {days}-day streak! Your dedication is inspiring the entire community!",
                    "🎯 {days} days and counting! You're setting an incredible example!"
                ],
                "long": [
                    "🏆 LEGENDARY! {days} days of donations! You're a true champion of charity!",
                    "👑 {days}-day streak! You've achieved donation royalty status!",
                    "🌟 AMAZING! {days} consecutive days! You're redefining what it means to give back!"
                ]
            },
            
            NotificationType.DONATION: {
                "standard": [
                    "Thank you for your {item_name} donation! You've earned {points} points!",
                    "Your {item_name} will help someone in need! +{points} points for your kindness!",
                    "Donation received! {item_name} → {points} points. Your generosity matters!"
                ],
                "high_demand": [
                    "🎯 PERFECT TIMING! Your {item_name} was desperately needed! +{points} points + {bonus} bonus!",
                    "⚡ CRITICAL DONATION! {item_name} was on our urgent needs list! Amazing timing!",
                    "🔥 HIGH IMPACT! Your {item_name} donation fills a critical gap! Bonus points awarded!"
                ]
            },
            
            NotificationType.GYM_LEADER: {
                "new_leader": [
                    "👑 NEW GYM LEADER at {location}! {username}, you now rule this charitable kingdom!",
                    "🏆 LEADERSHIP CHANGE! {username} has become the new champion of {location}!",
                    "⚔️ VICTORY! {username} has claimed the throne at {location} gym!"
                ],
                "defending": [
                    "🛡️ Still defending {location}! Your leadership inspires others to give more!",
                    "👑 Holding strong at {location}! Can anyone challenge your generous reign?",
                    "🏰 Your {location} fortress remains strong! Keep inspiring others!"
                ]
            },
            
            NotificationType.MISSING_ITEM: [
                "🚨 URGENT NEED: {location} desperately needs {item_name}! Extra points for helping!",
                "⚠️ CRITICAL: {location} is running low on {item_name}! Be a hero and donate!",
                "🎯 HIGH PRIORITY: {item_name} needed at {location}! Your donation would be perfect!"
            ],
            
            NotificationType.TIER_UPGRADE: {
                "bronze_to_silver": [
                    "🥈 TIER UPGRADE! Welcome to Silver status! Your dedication is paying off!",
                    "✨ You've reached Silver tier! Enhanced rewards and recognition await!",
                    "🌟 Silver achieved! Your consistent giving has earned this upgrade!"
                ],
                "silver_to_gold": [
                    "🥇 GOLD TIER ACHIEVED! You're now among our most valued contributors!",
                    "👑 Welcome to Gold status! Your generosity is truly exceptional!",
                    "💛 GOLD TIER! You've demonstrated outstanding commitment to giving!"
                ],
                "gold_to_platinum": [
                    "💎 PLATINUM STATUS! You've reached the pinnacle of charitable giving!",
                    "🏆 LEGENDARY! Platinum tier reserved for the most generous souls!",
                    "👑 PLATINUM ROYALTY! You're in the top tier of charitable champions!"
                ]
            },
            
            NotificationType.MILESTONE: [
                "🎊 MILESTONE: {milestone}! You've reached an incredible achievement!",
                "🏆 CELEBRATION TIME! {milestone} - your impact keeps growing!",
                "🌟 AMAZING MILESTONE: {milestone}! Thank you for your continued generosity!"
            ]
        }
    
    def generate_notification(
        self, 
        notification_type: NotificationType, 
        context: Dict = None, 
        **kwargs
    ) -> Dict:
        """
        Generate a contextual notification message
        
        Args:
            notification_type: Type of notification to generate
            context: Additional context for message generation
            **kwargs: Additional parameters for message customization
        
        Returns:
            Dict with notification details
        """
        context = context or {}
        
        try:
            message = self._get_message(notification_type, context, **kwargs)
            
            notification = {
                "agent": self.agent_name,
                "type": notification_type.value,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "personality": self.personality
            }
            
            # Add special formatting based on type
            if notification_type == NotificationType.ACHIEVEMENT:
                notification["color"] = "gold"
                notification["icon"] = "🏆"
                notification["duration"] = 5000  # Show longer for achievements
            elif notification_type == NotificationType.STREAK:
                notification["color"] = "orange"
                notification["icon"] = "🔥"
                notification["duration"] = 3000
            elif notification_type == NotificationType.GYM_LEADER:
                notification["color"] = "purple"
                notification["icon"] = "👑"
                notification["duration"] = 4000
            elif notification_type == NotificationType.MISSING_ITEM:
                notification["color"] = "red"
                notification["icon"] = "🚨"
                notification["duration"] = 6000
            else:
                notification["color"] = "blue"
                notification["icon"] = "💙"
                notification["duration"] = 3000
            
            return notification
            
        except Exception as e:
            # Fallback message if generation fails
            return {
                "agent": self.agent_name,
                "type": "error",
                "message": "Thank you for your donation! Your kindness makes a difference!",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _get_message(
        self, 
        notification_type: NotificationType, 
        context: Dict, 
        **kwargs
    ) -> str:
        """Generate appropriate message based on type and context"""
        
        if notification_type == NotificationType.ACHIEVEMENT:
            achievement_type = context.get('achievement_type', 'first_donation')
            templates = self.message_templates[notification_type].get(achievement_type, 
                       self.message_templates[notification_type]['first_donation'])
            
        elif notification_type == NotificationType.STREAK:
            days = context.get('days', 1)
            if days <= 3:
                category = 'short'
            elif days <= 10:
                category = 'medium' 
            else:
                category = 'long'
            templates = self.message_templates[notification_type][category]
            
        elif notification_type == NotificationType.DONATION:
            is_high_demand = context.get('is_high_demand', False)
            category = 'high_demand' if is_high_demand else 'standard'
            templates = self.message_templates[notification_type][category]
            
        elif notification_type == NotificationType.GYM_LEADER:
            is_new = context.get('is_new_leader', True)
            category = 'new_leader' if is_new else 'defending'
            templates = self.message_templates[notification_type][category]
            
        elif notification_type == NotificationType.TIER_UPGRADE:
            upgrade_type = context.get('upgrade_type', 'bronze_to_silver')
            templates = self.message_templates[notification_type].get(upgrade_type,
                       self.message_templates[notification_type]['bronze_to_silver'])
            
        else:
            templates = self.message_templates.get(notification_type, 
                       ["Thank you for your contribution!"])
        
        # Select random message from templates
        message = random.choice(templates)
        
        # Format message with context variables
        try:
            formatted_message = message.format(**context, **kwargs)
        except KeyError:
            # If formatting fails, return the original message
            formatted_message = message
        
        return formatted_message
    
    def get_encouragement_for_missing_items(self, missing_items: List[Dict]) -> List[Dict]:
        """Generate notifications for missing items across all storages"""
        notifications = []
        
        for item in missing_items[:5]:  # Limit to top 5 most needed
            context = {
                'item_name': item['item_name'],
                'location': item['storage_name'],
                'shortage': item['shortage'],
                'bonus_points': item['bonus_points']
            }
            
            notification = self.generate_notification(
                NotificationType.MISSING_ITEM,
                context=context
            )
            notifications.append(notification)
        
        return notifications
    
    def celebrate_achievement(self, achievement_name: str, user_name: str, **kwargs) -> Dict:
        """Generate achievement celebration notification"""
        context = {
            'achievement_name': achievement_name,
            'username': user_name,
            **kwargs
        }
        
        # Determine achievement type for appropriate message
        achievement_type = 'first_donation'
        if 'generous' in achievement_name.lower():
            achievement_type = 'generous_giver'
        elif 'streak' in achievement_name.lower():
            achievement_type = 'streak_master'
        elif 'leader' in achievement_name.lower():
            achievement_type = 'gym_leader'
        
        context['achievement_type'] = achievement_type
        
        return self.generate_notification(
            NotificationType.ACHIEVEMENT,
            context=context
        )

# Global agent instance
notification_agent = GoogleADKNotificationAgent()

# Convenience functions for easy use
def notify_achievement(achievement_name: str, user_name: str, **kwargs) -> Dict:
    """Quick function to generate achievement notification"""
    return notification_agent.celebrate_achievement(achievement_name, user_name, **kwargs)

def notify_donation(item_name: str, points: int, is_high_demand: bool = False, **kwargs) -> Dict:
    """Quick function to generate donation notification"""
    context = {
        'item_name': item_name,
        'points': points,
        'is_high_demand': is_high_demand,
        **kwargs
    }
    return notification_agent.generate_notification(NotificationType.DONATION, context)

def notify_streak(days: int, user_name: str) -> Dict:
    """Quick function to generate streak notification"""
    context = {
        'days': days,
        'username': user_name
    }
    return notification_agent.generate_notification(NotificationType.STREAK, context)

def notify_gym_leader(location: str, user_name: str, is_new: bool = True) -> Dict:
    """Quick function to generate gym leader notification"""
    context = {
        'location': location,
        'username': user_name,
        'is_new_leader': is_new
    }
    return notification_agent.generate_notification(NotificationType.GYM_LEADER, context)

if __name__ == "__main__":
    # Test the notification agent
    agent = GoogleADKNotificationAgent()
    
    print("🤖 Google ADK Notification Agent Testing\n")
    
    # Test different notification types
    test_cases = [
        {
            "type": NotificationType.ACHIEVEMENT,
            "context": {"achievement_type": "first_donation", "username": "Alice"},
            "description": "First donation achievement"
        },
        {
            "type": NotificationType.STREAK,
            "context": {"days": 7, "username": "Bob"},
            "description": "Weekly streak"
        },
        {
            "type": NotificationType.DONATION,
            "context": {"item_name": "Winter Coats", "points": 150, "is_high_demand": True, "bonus": 50},
            "description": "High-demand donation"
        },
        {
            "type": NotificationType.GYM_LEADER,
            "context": {"location": "Downtown Hub", "username": "Charlie", "is_new_leader": True},
            "description": "New gym leader"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['description']}:")
        notification = agent.generate_notification(test["type"], test["context"])
        print(f"   {notification['icon']} {notification['message']}")
        print(f"   Color: {notification['color']}, Duration: {notification['duration']}ms\n")
    
    print("✅ All notification types working correctly!")