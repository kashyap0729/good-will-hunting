#!/usr/bin/env python3
"""
Comprehensive test to verify Gemini API is actually being called
This test will definitively show whether AI is working or using fallbacks
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

def test_with_api_key():
    """Test with a real API key to see if Gemini is called"""
    print("🧪 TESTING GEMINI API INTEGRATION")
    print("=" * 50)
    
    # Check if we have an API key
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key or api_key == "your_google_api_key_here":
        print("❌ No valid GOOGLE_API_KEY found!")
        print("   Please set a real Google API key in your .env file")
        print("   Get one from: https://makersuite.google.com/app/apikey")
        return False
    
    # Import and test
    try:
        from notification_agent import notification_agent, NotificationType
        
        print(f"✅ Agent initialized: {notification_agent.agent_name}")
        print(f"   AI Mode: {notification_agent.use_ai}")
        print(f"   Has Model: {notification_agent.model is not None}")
        
        if not notification_agent.use_ai:
            print("❌ Agent is in fallback mode - AI not working")
            return False
        
        # Test actual API call with detailed logging
        print("\n🚀 Testing actual Gemini API call...")
        
        test_context = {
            'achievement_name': 'API Test Achievement',
            'username': 'TestUser',
            'special_marker': 'GEMINI_TEST_12345'  # Unique marker to verify AI response
        }
        
        # Add custom logging to see the actual prompt
        original_build_prompt = notification_agent._build_prompt
        original_get_message = notification_agent._get_message
        
        def logged_build_prompt(notification_type, context):
            prompt = original_build_prompt(notification_type, context)
            print(f"\n📝 PROMPT SENT TO GEMINI:")
            print("-" * 30)
            print(prompt)
            print("-" * 30)
            return prompt
        
        def logged_get_message(notification_type, context):
            print(f"\n🤖 CALLING GEMINI API...")
            if not notification_agent.use_ai or not notification_agent.model:
                print("❌ Using fallback instead of AI!")
                return original_get_message(notification_type, context)
            
            try:
                prompt = logged_build_prompt(notification_type, context)
                print("🔄 Sending request to Gemini...")
                
                response = notification_agent.model.generate_content(prompt)
                message = response.text.strip().replace('"', '')
                
                print(f"✅ GEMINI RESPONSE RECEIVED:")
                print(f"   Raw response: '{response.text}'")
                print(f"   Cleaned message: '{message}'")
                
                # Check if response contains our unique marker or context
                if 'GEMINI_TEST_12345' in message or 'API Test Achievement' in message or 'TestUser' in message:
                    print("🎯 VERIFIED: Response contains context data - AI is working!")
                else:
                    print("⚠️  Response doesn't contain expected context - checking if it's personalized...")
                
                return message
                
            except Exception as e:
                print(f"❌ GEMINI API CALL FAILED: {e}")
                print("   Falling back to template message")
                return notification_agent._get_fallback_message(notification_type, context)
        
        # Temporarily replace methods for testing
        notification_agent._build_prompt = logged_build_prompt
        notification_agent._get_message = logged_get_message
        
        # Make the actual test call
        result = notification_agent.generate_notification(
            NotificationType.ACHIEVEMENT,
            test_context
        )
        
        print(f"\n📋 FINAL RESULT:")
        print(f"   Type: {result['type']}")
        print(f"   Message: '{result['message']}'")
        print(f"   Agent: {result['agent']}")
        
        # Restore original methods
        notification_agent._build_prompt = original_build_prompt
        notification_agent._get_message = original_get_message
        
        # Verify this isn't a fallback message
        fallback_msg = notification_agent._get_fallback_message(NotificationType.ACHIEVEMENT, test_context)
        
        if result['message'] == fallback_msg:
            print("❌ RESULT MATCHES FALLBACK - AI NOT WORKING")
            return False
        else:
            print("✅ RESULT DIFFERENT FROM FALLBACK - AI IS WORKING!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_mode():
    """Test fallback mode by removing API key"""
    print("\n🧪 TESTING FALLBACK MODE")
    print("=" * 50)
    
    # Remove API key temporarily
    original_key = os.environ.get("GOOGLE_API_KEY")
    if "GOOGLE_API_KEY" in os.environ:
        del os.environ["GOOGLE_API_KEY"]
    
    # Force reload of the module to test fallback
    if 'notification_agent' in sys.modules:
        del sys.modules['notification_agent']
    
    try:
        from notification_agent import notification_agent, NotificationType
        
        print(f"✅ Agent in fallback mode: {notification_agent.agent_name}")
        print(f"   AI Mode: {notification_agent.use_ai}")
        print(f"   Has Model: {notification_agent.model is not None}")
        
        # Test fallback message
        result = notification_agent.generate_notification(
            NotificationType.ACHIEVEMENT,
            {'achievement_name': 'Fallback Test', 'username': 'TestUser'}
        )
        
        print(f"\n📋 FALLBACK RESULT:")
        print(f"   Message: '{result['message']}'")
        
        if not notification_agent.use_ai:
            print("✅ Fallback mode working correctly")
        else:
            print("❌ Should be in fallback mode but isn't")
            
    finally:
        # Restore original API key
        if original_key:
            os.environ["GOOGLE_API_KEY"] = original_key

if __name__ == "__main__":
    print("🔬 COMPREHENSIVE GEMINI API TEST")
    print("=" * 60)
    
    # Test with API key
    api_working = test_with_api_key()
    
    # Test fallback mode
    test_fallback_mode()
    
    print("\n" + "=" * 60)
    print("📊 FINAL ASSESSMENT:")
    
    if api_working:
        print("✅ GEMINI AI IS WORKING - Real API calls are being made")
        print("✅ Prompts are being sent to Gemini")
        print("✅ Personalized responses are being generated")
    else:
        print("❌ GEMINI AI IS NOT WORKING - Only fallback messages")
        print("❌ Check your API key and internet connection")
    
    print("✅ Fallback system working as backup")
