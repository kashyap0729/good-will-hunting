#!/usr/bin/env python3
"""
Fresh test for Gemini API with module reload
"""
import os
import sys
import importlib

# Force reload all modules to pick up new .env
if 'notification_agent' in sys.modules:
    del sys.modules['notification_agent']

print("🔬 FRESH GEMINI API TEST")
print("=" * 50)

# Check .env file directly
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"✅ Found .env file")
    print(f"   API Key present: {'Yes' if api_key else 'No'}")
    print(f"   API Key length: {len(api_key) if api_key else 0} characters")
    print(f"   API Key starts with: {api_key[:10] + '...' if api_key and len(api_key) > 10 else 'N/A'}")
else:
    print("❌ No .env file found")
    exit(1)

if not api_key:
    print("❌ No API key in .env file")
    exit(1)

# Now import with fresh module
print("\n🚀 Importing notification agent with fresh environment...")
try:
    from notification_agent import notification_agent, NotificationType
    
    print(f"✅ Agent loaded: {notification_agent.agent_name}")
    print(f"   AI Mode: {notification_agent.use_ai}")
    print(f"   Has Model: {notification_agent.model is not None}")
    
    if notification_agent.use_ai and notification_agent.model:
        print("🎯 AI MODE DETECTED - Testing real API call...")
        
        # Test with unique context to verify AI response
        test_result = notification_agent.generate_notification(
            NotificationType.ACHIEVEMENT,
            {
                'achievement_name': 'API_TEST_UNIQUE_12345',
                'username': 'GeminiTestUser',
                'test_marker': 'VERIFY_AI_WORKING'
            }
        )
        
        print(f"\n📋 API TEST RESULT:")
        print(f"   Message: '{test_result['message']}'")
        
        # Check if it's using fallback by comparing with fallback message
        fallback = notification_agent._get_fallback_message(
            NotificationType.ACHIEVEMENT,
            {'achievement_name': 'API_TEST_UNIQUE_12345', 'username': 'GeminiTestUser'}
        )
        
        print(f"\n🔍 VERIFICATION:")
        if test_result['message'] != fallback:
            print("✅ CONFIRMED: Response is different from fallback - AI IS WORKING!")
            print("✅ Gemini API is being called and generating unique responses")
        else:
            print("❌ Response matches fallback - AI may not be working")
            
    else:
        print("❌ AI MODE NOT ENABLED - Check API key validity")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
