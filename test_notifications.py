#!/usr/bin/env python3
"""
Test script for notification agent
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

# Remove API key to test fallback mode
if 'GOOGLE_API_KEY' in os.environ:
    del os.environ['GOOGLE_API_KEY']

try:
    from notification_agent import notification_agent, NotificationType
    
    print("✅ Notification agent imported successfully")
    print(f"   Agent: {notification_agent.agent_name}")
    print(f"   Version: {notification_agent.version}")
    print(f"   AI Mode: {notification_agent.use_ai}")
    
    # Test a simple notification
    result = notification_agent.generate_notification(
        NotificationType.ACHIEVEMENT,
        {'achievement_name': 'First Donation', 'username': 'TestUser'}
    )
    
    print(f"\nTest notification:")
    print(f"   Type: {result['type']}")
    print(f"   Message: {result['message']}")
    print(f"   Icon: {result['icon']}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
