#!/usr/bin/env python3
"""
Test missing items and priority display
"""

def test_missing_items():
    print("🔍 Testing Missing Items System")
    print("=" * 50)
    
    # Test missing items
    try:
        from database import get_missing_items
        missing_items = get_missing_items()
        
        print(f"Found {len(missing_items)} missing items:")
        for item in missing_items:
            print(f"  - {item['item_name']} at {item['storage_name']}")
            print(f"    Shortage: {item['shortage']} (need {item['min_threshold']}, have {item['current_quantity']})")
            print(f"    Bonus: +{item['bonus_points']} points")
            print()
            
        # Test if we can generate notifications for them
        if missing_items:
            print("Testing AI notifications for missing items...")
            from notification_agent import notification_agent, NotificationType
            
            # Test first missing item
            first_item = missing_items[0]
            context = {
                'item_name': first_item['item_name'],
                'location': first_item['storage_name'],
                'bonus_points': first_item['bonus_points']
            }
            
            notification = notification_agent.generate_notification(
                NotificationType.MISSING_ITEM, 
                context
            )
            
            print("✅ Generated notification:")
            print(f"   Message: {notification.get('message', 'No message')}")
            print(f"   AI Icon: {notification.get('ai_icon', 'N/A')}")
            
        else:
            print("❌ No missing items found - this is why notifications aren't showing!")
            print("💡 The database may need to be populated with inventory data")
            
    except Exception as e:
        print(f"❌ Error testing missing items: {e}")
        import traceback
        traceback.print_exc()

def check_database_tables():
    print("\n🗃️ Checking Database Tables")
    print("=" * 50)
    
    try:
        import sqlite3
        conn = sqlite3.connect('goodwill_gym.db')
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Database tables: {tables}")
        
        # Check storage_inventory table
        if 'storage_inventory' in tables:
            cursor.execute("SELECT COUNT(*) FROM storage_inventory")
            count = cursor.fetchone()[0]
            print(f"Storage inventory records: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM storage_inventory LIMIT 3")
                rows = cursor.fetchall()
                print("Sample inventory records:")
                for row in rows:
                    print(f"  {row}")
        else:
            print("❌ storage_inventory table missing!")
            
        # Check missing_items_requests table  
        if 'missing_items_requests' in tables:
            cursor.execute("SELECT COUNT(*) FROM missing_items_requests")
            count = cursor.fetchone()[0]
            print(f"Missing items requests: {count}")
        else:
            print("❌ missing_items_requests table missing!")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check error: {e}")

if __name__ == "__main__":
    test_missing_items()
    check_database_tables()
