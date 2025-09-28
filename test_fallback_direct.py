#!/usr/bin/env python3
"""
Direct test of fallback messages to verify user names
"""

def test_fallback_messages():
    print("🧪 Testing Fallback Messages (No API calls)\n")
    
    # Import the notification system
    import sys
    import os
    sys.path.append('c:\\ganti.b\\Hackathon\\GWH2\\good-will-hunting')
    
    try:
        from notification_agent import NotificationType, NotificationAgent
        
        # Create agent instance
        agent = NotificationAgent()
        
        # Test fallback messages directly
        test_contexts = [
            {
                "type": NotificationType.DONATION,
                "context": {
                    "user_name": "Alice Demo",
                    "item_name": "Winter Coats",
                    "points": 75
                },
                "description": "Alice donation"
            },
            {
                "type": NotificationType.DONATION,
                "context": {
                    "user_name": "Bob Demo", 
                    "item_name": "Baby Formula",
                    "points": 100
                },
                "description": "Bob donation"
            }
        ]
        
        for test in test_contexts:
            print(f"--- {test['description']} ---")
            print(f"Context: {test['context']}")
            
            # Get fallback message directly
            fallback_msg = agent._get_rate_limit_fallback(test['type'], test['context'])
            print(f"Fallback: {fallback_msg}")
            
            # Check for "you" references
            if 'you' in fallback_msg.lower() or 'your' in fallback_msg.lower():
                print("⚠️  WARNING: Contains 'you' or 'your'")
            else:
                print("✅ Good: Uses proper names")
            print()
            
    except Exception as e:
        print(f"❌ Error importing: {e}")

if __name__ == "__main__":
    test_fallback_messages()
