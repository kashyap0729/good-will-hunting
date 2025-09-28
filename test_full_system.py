#!/usr/bin/env python3
"""
Test donation processing and notification generation
"""

def test_donation_processing():
    print("🧪 Testing Donation Processing & Notifications")
    print("=" * 60)
    
    # Test 1: Process donation
    print("1. Testing donation processing...")
    try:
        from database import process_donation
        result = process_donation(1, 1, 'Test Blanket', 1)
        
        print("✅ Donation processed successfully:")
        print(f"   Points awarded: {result.get('points_awarded', 0)}")
        print(f"   New total points: {result.get('new_total_points', 0)}")
        print(f"   Bonus points: {result.get('bonus_points', 0)}")
        print(f"   New tier: {result.get('new_tier', 'Unknown')}")
        print(f"   Missing item bonus: {result.get('is_missing_item_bonus', False)}")
        
    except Exception as e:
        print(f"❌ Error processing donation: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "-" * 40 + "\n")
    
    # Test 2: Generate AI notification  
    print("2. Testing AI notification generation...")
    try:
        from notification_agent import notify_donation
        
        notification = notify_donation("Test Blanket", 15, False)
        print("✅ AI notification generated:")
        print(f"   Message: {notification.get('message', 'No message')}")
        print(f"   AI Generated: {notification.get('ai_generated', False)}")
        print(f"   AI Icon: {notification.get('ai_icon', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error generating notification: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "-" * 40 + "\n")
    
    # Test 3: Test missing items notifications
    print("3. Testing missing items notifications...")
    try:
        from database import get_missing_items
        from notification_agent import notification_agent, NotificationType
        
        missing_items = get_missing_items()
        print(f"Found {len(missing_items)} missing items:")
        for item in missing_items[:2]:
            print(f"   - {item['item_name']} at {item['storage_name']} (+{item['bonus_points']} points)")
        
        if missing_items:
            notifications = notification_agent.get_encouragement_for_missing_items(missing_items[:1])
            if notifications:
                print(f"✅ Generated missing item notification:")
                print(f"   Message: {notifications[0].get('message', 'No message')}")
            else:
                print("❌ No missing item notifications generated")
        else:
            print("ℹ️ No missing items found in database")
            
    except Exception as e:
        print(f"❌ Error with missing items: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_donation_processing()
