"""
Google ADK-style Notification Agent for Goodwill Platform
Generates encouraging         try:
            print("   ⚡ Sending fast request to Gemini AI...")
            
            # Configure generation for speed
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 100,  # Limit output for faster response
            }
            
            # Generate with faster configuration
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            message = response.text.strip().replace('"', '')
            print(f"   ✨ AI generated: '{message[:60]}{'...' if len(message) > 60 else ''}'")
            
            if not message:
                raise ValueError("Received empty response from Gemini AI")
            
            return messageor achievements, streaks, and donations using the Gemini API.
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

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
    raise ValueError("❌ GOOGLE_API_KEY is required for AI-powered notifications. Please set a valid API key in your .env file.")

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
        self.version = "4.0.0-ai-only"
        self.personality = "encouraging, uplifting, and slightly gamified"
        
        # Initialize the Generative Model - API key is required
        try:
            self.model = genai.GenerativeModel(model_name)
            print(f"🤖 AI-Powered Notification Agent '{self.agent_name}' v{self.version} initialized with '{model_name}'")
            print(f"   🧠 Pure AI mode - All notifications powered by Gemini")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini model: {e}. Check your API key and internet connection.")

    def _build_prompt(self, notification_type: NotificationType, context: Dict) -> str:
        """Constructs a concise prompt for faster Gemini API response."""
        
        prompt = f"""Generate a short, encouraging notification for a Goodwill donation platform user.

Type: {notification_type.value}
Context: {context}

Requirements:
- One sentence only
- Include relevant emoji
- Be positive and motivational
- No quotes or preamble

Generate the message:"""
        return prompt

    def _get_message(self, notification_type: NotificationType, context: Dict) -> str:
        """
        Generates a message using the Gemini AI API based on type and context.
        Pure AI implementation - no fallbacks.
        """
        print(f"� Generating AI notification for {notification_type.value}")
        prompt = self._build_prompt(notification_type, context)
        
        try:
            print("   � Sending request to Gemini AI...")
            response = self.model.generate_content(prompt)
            message = response.text.strip().replace('"', '')
            print(f"   ✨ AI generated: '{message[:60]}{'...' if len(message) > 60 else ''}'")
            
            if not message:
                raise ValueError("Received empty response from Gemini AI")
            
            return message
            
        except Exception as e:
            print(f"   ❌ Gemini AI call failed: {e}")
            raise RuntimeError(f"AI notification generation failed: {e}")

    def generate_notification(self, notification_type: NotificationType, context: Dict = None) -> Dict:
        """
        Generate a contextual notification message using AI.
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
                "personality": self.personality,
                "ai_generated": True,  # 🤖 Mark as AI-generated
                "ai_model": "gemini-2.0-flash",
                "ai_version": self.version
            }
            
            # Add special formatting based on type with AI indicators
            if notification_type == NotificationType.ACHIEVEMENT:
                notification["color"] = "gold"
                notification["icon"] = "🏆"
                notification["ai_icon"] = "🤖✨"  # AI indicator
                notification["duration"] = 5000
            elif notification_type == NotificationType.STREAK:
                notification["color"] = "orange"
                notification["icon"] = "🔥"
                notification["ai_icon"] = "🤖🔥"  # AI indicator
                notification["duration"] = 3000
            elif notification_type == NotificationType.GYM_LEADER:
                notification["color"] = "purple"
                notification["icon"] = "👑"
                notification["ai_icon"] = "🤖👑"  # AI indicator
                notification["duration"] = 4000
            elif notification_type == NotificationType.MISSING_ITEM:
                notification["color"] = "red"
                notification["icon"] = "🚨"
                notification["ai_icon"] = "🤖🚨"  # AI indicator
                notification["duration"] = 6000
            elif notification_type == NotificationType.TIER_UPGRADE:
                notification["color"] = "purple"
                notification["icon"] = "🌟"
                notification["ai_icon"] = "🤖🌟"  # AI indicator
                notification["duration"] = 5000
            elif notification_type == NotificationType.DONATION:
                notification["color"] = "green"
                notification["icon"] = "🎁"
                notification["ai_icon"] = "🤖🎁"  # AI indicator
                notification["duration"] = 4000
            else:
                notification["color"] = "blue"
                notification["icon"] = "💙"
                notification["ai_icon"] = "🤖💙"  # AI indicator
                notification["duration"] = 3000
            
            return notification
            
        except Exception as e:
            # If AI fails, raise error instead of falling back
            raise RuntimeError(f"Failed to generate AI notification: {e}")
    
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