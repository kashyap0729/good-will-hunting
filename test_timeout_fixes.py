#!/usr/bin/env python3
"""
Quick test to verify API timeout fixes
"""

import asyncio
import time
from notification_agent import notify_donation, notification_agent, NotificationType

async def test_timeout_fixes():
    print("🧪 Testing API Timeout Fixes")
    print("=" * 50)
    
    # Test 1: Quick notification generation
    print("1. Testing fast notification generation...")
    start_time = time.time()
    
    try:
        notification = notify_donation("Winter Coats", 50, True, bonus=25)
        end_time = time.time()
        
        print(f"✅ Success in {end_time - start_time:.2f} seconds")
        print(f"   Message: {notification.get('message', 'No message')}")
        print(f"   AI Icon: {notification.get('ai_icon', 'N/A')}")
        
    except Exception as e:
        end_time = time.time()
        print(f"❌ Failed in {end_time - start_time:.2f} seconds: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Multiple notifications with timeout handling
    print("2. Testing multiple notifications...")
    
    test_cases = [
        {"item": "Baby Formula", "points": 30},
        {"item": "Blankets", "points": 15},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"   {i}. Testing {case['item']}...")
        start_time = time.time()
        
        try:
            context = {
                'item_name': case['item'],
                'points': case['points'],
                'is_high_demand': True
            }
            
            notification = notification_agent.generate_notification(
                NotificationType.DONATION, 
                context
            )
            
            end_time = time.time()
            print(f"      ✅ Generated in {end_time - start_time:.2f}s: {notification.get('message', 'No message')[:50]}...")
            
        except Exception as e:
            end_time = time.time()
            print(f"      ❌ Failed in {end_time - start_time:.2f}s: {e}")
    
    print("\n✅ Timeout test complete!")
    print("\n💡 If all tests passed quickly (< 10s each), the timeouts are fixed!")
    print("💡 If tests failed, check your Google API key and internet connection.")

if __name__ == "__main__":
    asyncio.run(test_timeout_fixes())
