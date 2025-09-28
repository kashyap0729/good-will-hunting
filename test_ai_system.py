#!/usr/bin/env python3
"""
Test AI notifications system
"""

from notification_agent import notify_donation

print('🧪 Testing AI Notification System')
print('='*50)

try:
    print('1. Testing donation notification generation...')
    notification = notify_donation('Winter Coats', 195, True, bonus=50)
    
    print('✅ SUCCESS! Notification generated:')
    print(f'   Type: {notification.get("type")}')
    print(f'   Message: {notification.get("message", "No message")}')
    print(f'   AI Generated: {notification.get("ai_generated")}')
    print(f'   AI Icon: {notification.get("ai_icon")}')
    print(f'   AI Model: {notification.get("ai_model")}')
    
except Exception as e:
    print(f'❌ ERROR: {e}')

print('\n' + '='*50)
print('2. Testing backend endpoint simulation...')

try:
    import sqlite3
    from fast_backend import pool, notification_agent, NotificationType
    
    conn = pool.get_connection()
    cursor = conn.cursor()
    
    # Get recent donations
    cursor.execute("""
        SELECT d.id, d.item_name, d.points_awarded, d.donation_date,
               u.username, s.name as storage_name
        FROM donations d
        JOIN users u ON d.user_id = u.id
        JOIN storages s ON d.storage_id = s.id
        ORDER BY d.donation_date DESC
        LIMIT 3
    """)
    
    recent_donations = cursor.fetchall()
    notifications = []
    
    print(f'Found {len(recent_donations)} recent donations')
    
    for donation in recent_donations:
        context = {
            'item_name': donation['item_name'],
            'points': donation['points_awarded'],
            'username': donation['username'],
            'location': donation['storage_name'],
            'is_recent': True
        }
        
        # Generate AI notification
        notification = notification_agent.generate_notification(
            NotificationType.DONATION, 
            context
        )
        notifications.append(notification)
        print(f'   ✅ Generated notification for {donation["item_name"]}')
    
    pool.return_connection(conn)
    print(f'✅ Successfully generated {len(notifications)} notifications')
    
    # Show first notification as example
    if notifications:
        first = notifications[0]
        print(f'\nExample notification:')
        print(f'   Message: {first.get("message", "No message")}')
        print(f'   AI Icon: {first.get("ai_icon", "N/A")}')
    
except Exception as e:
    print(f'❌ Backend test failed: {e}')
    import traceback
    traceback.print_exc()

print('\n✅ Testing complete!')
