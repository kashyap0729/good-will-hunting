#!/usr/bin/env python3
"""
Quick test of notification system with user names
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notification_agent import NotificationType, notification_agent

def test_user_name_notifications():
    print("🧪 Testing User Name Notifications\n")
    
    # Test cases with user names
    test_cases = [
        {
            "type": NotificationType.DONATION,
            "context": {
                "user_name": "Alice Demo",
                "item_name": "Winter Coats", 
                "points": 75
            },
            "description": "Donation notification"
        },
        {
            "type": NotificationType.DONATION,
            "context": {
                "user_name": "Bob Demo",
                "item_name": "Baby Formula", 
                "points": 100
            },
            "description": "High value donation"
        },
        {
            "type": NotificationType.ACHIEVEMENT,
            "context": {
                "user_name": "Charlie Smith",
                "achievement_name": "First Donation"
            },
            "description": "Achievement notification"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Test {i}: {test_case['description']} ---")
        print(f"Context: {test_case['context']}")
        
        try:
            result = notification_agent.generate_notification(
                test_case['type'], 
                test_case['context']
            )
            
            message = result.get('message', 'No message')
            print(f"✅ Generated: {message}")
            
            # Check if message contains "you" (should not)
            if 'you' in message.lower() or 'your' in message.lower():
                print("⚠️  WARNING: Message contains 'you' or 'your'")
            else:
                print("✅ Good: No 'you' references found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_user_name_notifications()
