#!/usr/bin/env python3
"""
Test donation with notification display
"""

import requests
import json

# Test donation API call
def test_donation():
    url = "http://localhost:8000/donate"
    data = {
        "user_id": 1,  # Alice Demo user
        "storage_id": 1,
        "item_name": "Winter Coats",  # Real item from missing items
        "quantity": 2
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Donation Success!")
            print(f"Points Awarded: {result.get('points_awarded', 0)}")
            print(f"Total Points: {result.get('new_total_points', 0)}")
            
            # Check notification
            if result.get('notification'):
                notif = result['notification']
                print(f"\n🤖 AI Notification:")
                print(f"Message: {notif.get('message', 'No message')}")
                print(f"AI Generated: {notif.get('ai_generated', False)}")
                print(f"AI Icon: {notif.get('ai_icon', 'N/A')}")
            else:
                print("\n❌ No notification in response")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("Make sure the backend is running: python fast_backend.py")

if __name__ == "__main__":
    test_donation()
