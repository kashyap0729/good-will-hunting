#!/usr/bin/env python3
"""
Update missing items requests with proper bonus points
"""

import sqlite3

def update_missing_items():
    print("🔧 Updating Missing Items with Proper Bonus Points")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('goodwill_gym.db')
        cursor = conn.cursor()
        
        # First, check current missing items requests
        cursor.execute("SELECT * FROM missing_items_requests WHERE fulfilled = 0")
        current = cursor.fetchall()
        print(f"Current missing item requests: {len(current)}")
        for item in current:
            print(f"  - {item}")
        
        # Clear old requests
        cursor.execute("DELETE FROM missing_items_requests")
        
        # Add high-priority missing items with proper bonus points
        missing_items = [
            {
                'storage_id': 1,  # South Beach Donation Hub
                'item_name': 'Winter Coats',
                'requested_quantity': 10,
                'urgency_level': 3,
                'bonus_points': 75,
                'reason': 'Urgent winter weather need'
            },
            {
                'storage_id': 2,  # Wynwood Warehouse  
                'item_name': 'Baby Formula',
                'requested_quantity': 20,
                'urgency_level': 3,
                'bonus_points': 100,
                'reason': 'Critical infant nutrition shortage'
            },
            {
                'storage_id': 3,  # Coral Gables Vault
                'item_name': 'Blankets', 
                'requested_quantity': 15,
                'urgency_level': 2,
                'bonus_points': 50,
                'reason': 'Homeless shelter emergency'
            }
        ]
        
        for item in missing_items:
            cursor.execute("""
                INSERT INTO missing_items_requests 
                (storage_id, item_name, requested_quantity, urgency_level, 
                 bonus_points, request_date, fulfilled)
                VALUES (?, ?, ?, ?, ?, datetime('now'), 0)
            """, (
                item['storage_id'], item['item_name'], item['requested_quantity'],
                item['urgency_level'], item['bonus_points']
            ))
        
        # Also update storage inventory to show these as low stock
        inventory_updates = [
            ('Winter Coats', 1, 0, 10),    # storage_id=1, current=0, min=10
            ('Baby Formula', 2, 2, 15),   # storage_id=2, current=2, min=15  
            ('Blankets', 3, 3, 12)        # storage_id=3, current=3, min=12
        ]
        
        for item_name, storage_id, current_qty, min_threshold in inventory_updates:
            # Insert or update storage inventory
            cursor.execute("""
                INSERT OR REPLACE INTO storage_inventory 
                (storage_id, item_name, current_quantity, min_threshold, max_capacity)
                VALUES (?, ?, ?, ?, ?)
            """, (storage_id, item_name, current_qty, min_threshold, min_threshold * 3))
        
        conn.commit()
        
        # Verify the updates
        print("\n✅ Updated missing items requests:")
        cursor.execute("""
            SELECT mir.item_name, s.name as storage_name, mir.bonus_points, mir.urgency_level
            FROM missing_items_requests mir
            JOIN storages s ON mir.storage_id = s.id
            WHERE mir.fulfilled = 0
        """)
        
        updated = cursor.fetchall()
        for item in updated:
            print(f"  - {item[0]} at {item[1]}: +{item[2]} points (urgency: {item[3]})")
        
        print(f"\n✅ Now test the missing items:")
        print(f"   python test_missing_items.py")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating missing items: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_missing_items()
