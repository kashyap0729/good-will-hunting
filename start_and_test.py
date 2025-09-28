#!/usr/bin/env python3
"""
Start backend and test APIs
"""

import subprocess
import sys
import time
import requests
import json

def test_api_endpoints():
    print("🚀 Starting Backend and Testing APIs")
    print("=" * 50)
    
    # Start backend
    print("1. Starting backend server...")
    try:
        process = subprocess.Popen([sys.executable, 'fast_backend.py'])
        print("   ⏳ Waiting 5 seconds for startup...")
        time.sleep(5)
        
        # Test basic connectivity
        print("2. Testing connectivity...")
        response = requests.get('http://localhost:8000/stats', timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running!")
        else:
            print(f"   ⚠️ Backend status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Backend start failed: {e}")
        return
    
    print("\n3. Testing notifications endpoint...")
    try:
        response = requests.get('http://localhost:8000/notifications/all', timeout=20)
        if response.status_code == 200:
            notifications = response.json()
            print(f"   ✅ Got {len(notifications)} notifications:")
            for i, notif in enumerate(notifications, 1):
                print(f"   {i}. {notif.get('type', 'unknown')}: {notif.get('message', 'No message')[:50]}...")
        else:
            print(f"   ❌ Notifications failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Notifications error: {e}")
    
    print("\n4. Testing donation...")
    try:
        data = {
            "user_id": 1,
            "storage_id": 1, 
            "item_name": "Test Donation",
            "quantity": 1
        }
        response = requests.post('http://localhost:8000/donate', json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Donation successful!")
            print(f"   Points: {result.get('points_awarded', 0)}")
            print(f"   Total: {result.get('new_total_points', 0)}")
            
            if result.get('notification'):
                print(f"   🤖 Notification: {result['notification'].get('message', 'No message')}")
            else:
                print("   ❌ No notification generated")
        else:
            print(f"   ❌ Donation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Donation error: {e}")
    
    print(f"\n✅ Testing complete! Backend should be running at http://localhost:8000")
    print(f"💡 You can now test the dashboard with: streamlit run fast_dashboard.py")

if __name__ == "__main__":
    test_api_endpoints()
