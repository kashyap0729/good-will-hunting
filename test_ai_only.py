#!/usr/bin/env python3
"""
Test AI-only notification system
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

try:
    from notification_agent import notification_agent, NotificationType
    
    print("🤖 Testing AI-Only Notification System")
    print("=" * 50)
    print(f"Agent: {notification_agent.agent_name}")
    print(f"Version: {notification_agent.version}")
    
    # Test different notification types
    test_cases = [
        {
            "type": NotificationType.ACHIEVEMENT,
            "context": {"achievement_name": "First Donation", "username": "Alice"},
            "description": "Achievement notification"
        },
        {
            "type": NotificationType.DONATION,
            "context": {"item_name": "Winter Coats", "points": 150, "is_high_demand": True},
            "description": "High-demand donation"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test['description']}:")
        try:
            result = notification_agent.generate_notification(test["type"], test["context"])
            
            print(f"   ✅ Success!")
            print(f"   Message: '{result['message']}'")
            print(f"   AI Generated: {result.get('ai_generated', False)}")
            print(f"   AI Model: {result.get('ai_model', 'N/A')}")
            print(f"   AI Icon: {result.get('ai_icon', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print("\n✅ AI-only notification system test complete!")
    
except Exception as e:
    print(f"❌ Error importing or testing: {e}")
    import traceback
    traceback.print_exc()
