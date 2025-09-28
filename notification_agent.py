"""
Google ADK-style Notification Agent for Goodwill Platform
Generates encouraging messages for achievements, streaks, and donations using the Gemini API.
"""

import os
from pathlib import Path
import random
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import google.generativeai as genai
from dotenv import load_dotenv

# --- Environment Setup ---
project_dir = Path.cwd()
env_path = project_dir / '.env'
load_dotenv(dotenv_path=env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please create a .env file and add your key.")

genai.configure(api_key=GOOGLE_API_KEY)


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
    Google ADK Agent that uses the Gemini API for generating contextual notifications.
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.agent_name = "GoodwillEncouragementAgent" 
        self.version = "3.0.0-google-adk"
        self.personality = "encouraging, uplifting, and slightly gamified"
        
        # Initialize the Generative Model with Google ADK
        self.model = genai.GenerativeModel(model_name)
        print(f"✅ Google ADK Agent '{self.agent_name}' v{self.version} initialized with '{model_name}'")

    def _build_prompt(self, notification_type: NotificationType, context: Dict) -> str:
        """Constructs a detailed prompt for the Gemini API."""
        
        prompt = f"""
        You are the '{self.agent_name}', an AI agent with an {self.personality} personality.
        Your task is to generate a single, short, and engaging notification message for a user on the Goodwill donation platform.
        
        Guidelines:
        - The message must be a single, concise sentence.
        - Use relevant emojis to make it fun and visually appealing.
        - The tone must be positive and motivational.
        - Do NOT include any preamble like "Here is your message:" or wrap the message in quotation marks.
        - Directly address the user's action or status.

        ---
        Notification Request:
        - Type: {notification_type.value}
        - Details: {context}
        ---
        
        Based on the request above, generate the perfect notification message.
        """
        return prompt

    def _get_message(self, notification_type: NotificationType, context: Dict) -> str:
        """
        Generates a message using the Gemini API based on type and context.
        """
        prompt = self._build_prompt(notification_type, context)
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up the response to ensure it's a single line of text
            message = response.text.strip().replace('"', '')
            if not message:
                 raise ValueError("Received an empty response from the API.")
            return message
        except Exception as e:
            print(f"❗️ Gemini API call failed: {e}")
            # Fallback message in case of API failure
            return "Thank you for your wonderful contribution! Every bit helps."

    def generate_notification(self, notification_type: NotificationType, context: Dict = None) -> Dict:
        """
        Generate a contextual notification message.
        """
        context = context or {}
        
        try:
            message = self._get_message(notification_type, context)
            
            notification = {
                "agent": self.agent_name,
                "type": notification_type.value,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "personality": self.personality
            }
            
            # Add special formatting based on type (this logic remains the same)
            if notification_type == NotificationType.ACHIEVEMENT:
                notification["color"] = "gold"
                notification["icon"] = "🏆"
                notification["duration"] = 5000
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
            return {
                "agent": self.agent_name,
                "type": "error",
                "message": "Thank you for your donation! Your kindness makes a difference!",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    # --- High-level convenience methods (no changes needed here) ---
    def get_encouragement_for_missing_items(self, missing_items: List[Dict]) -> List[Dict]:
        notifications = []
        for item in missing_items[:3]: # Limit to top 3 to avoid too many API calls
            context = {
                'item_name': item['item_name'],
                'location': item['storage_name'],
            }
            notification = self.generate_notification(NotificationType.MISSING_ITEM, context=context)
            notifications.append(notification)
        return notifications

    def celebrate_achievement(self, achievement_name: str, user_name: str, **kwargs) -> Dict:
        context = {
            'achievement_name': achievement_name,
            'username': user_name,
            **kwargs
        }
        return self.generate_notification(NotificationType.ACHIEVEMENT, context=context)


# Global agent instance
notification_agent = GoogleADKNotificationAgent()

# Convenience functions (no changes needed)
def notify_achievement(achievement_name: str, user_name: str, **kwargs) -> Dict:
    return notification_agent.celebrate_achievement(achievement_name, user_name, **kwargs)

def notify_donation(item_name: str, points: int, is_high_demand: bool = False, **kwargs) -> Dict:
    context = {
        'item_name': item_name,
        'points': points,
        'is_high_demand': is_high_demand,
        **kwargs
    }
    return notification_agent.generate_notification(NotificationType.DONATION, context)

def notify_streak(days: int, user_name: str) -> Dict:
    context = {'days': days, 'username': user_name}
    return notification_agent.generate_notification(NotificationType.STREAK, context)

def notify_gym_leader(location: str, user_name: str, is_new: bool = True) -> Dict:
    context = {'location': location, 'username': user_name, 'is_new': is_new}
    return notification_agent.generate_notification(NotificationType.GYM_LEADER, context)

if __name__ == "__main__":
    print("🤖 Google ADK Notification Agent (v2.0 - Gemini Powered) Testing\n")
    
    test_cases = [
        {
            "type": NotificationType.ACHIEVEMENT,
            "context": {"achievement_name": "First Donation", "username": "Alice"},
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
            "context": {"location": "Downtown Hub", "username": "Charlie", "is_new": True},
            "description": "New gym leader"
        },
        {
            "type": NotificationType.TIER_UPGRADE,
            "context": {"old_tier": "Silver", "new_tier": "Gold", "username": "Denise"},
            "description": "Tier Upgrade to Gold"
        },
        {
            "type": NotificationType.MISSING_ITEM,
            "context": {"item_name": "Children's Books", "location": "Westchester Branch"},
            "description": "Missing Item Alert"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['description']}:")
        notification = notification_agent.generate_notification(test["type"], test["context"])
        if "error" in notification:
            print(f"   ❌ Error generating notification: {notification['error']}")
        else:
            print(f"   {notification['icon']} {notification['message']}")
            print(f"   Color: {notification['color']}, Duration: {notification['duration']}ms\n")
    
    print("✅ Testing complete!")