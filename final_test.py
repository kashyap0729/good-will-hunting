#!/usr/bin/env python3
"""
Final comprehensive test - Start backend and test everything
"""

import subprocess
import sys
import time
import requests

def comprehensive_test():
    print("🚀 COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    
    # Step 1: Start backend
    print("1. Starting backend server...")
    try:
        process = subprocess.Popen([sys.executable, 'fast_backend.py'])
        print("   ⏳ Waiting 5 seconds for startup...")
        time.sleep(5)
        
        # Test connectivity
        response = requests.get('http://localhost:8000/stats', timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend started successfully!")
        else:
            print(f"   ⚠️ Backend status: {response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Backend start failed: {e}")
        return
    
    # Step 2: Test missing items endpoint
    print("\n2. Testing missing items (Priority Items)...")
    try:
        response = requests.get('http://localhost:8000/missing-items', timeout=10)
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ Got {len(items)} missing items:")
            for item in items[:3]:
                print(f"   - {item.get('item_name', 'Unknown')} at {item.get('storage_name', 'Unknown')}")
                print(f"     Bonus: +{item.get('bonus_points', 0)} points")
        else:
            print(f"   ❌ Missing items failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Missing items error: {e}")
    
    # Step 3: Test AI notifications endpoint
    print("\n3. Testing AI-powered notifications...")
    try:
        response = requests.get('http://localhost:8000/notifications/all', timeout=25)
        if response.status_code == 200:
            notifications = response.json()
            print(f"   ✅ Got {len(notifications)} AI notifications:")
            for i, notif in enumerate(notifications, 1):
                print(f"   {i}. {notif.get('type', 'unknown')}: {notif.get('message', 'No message')[:60]}...")
                print(f"      AI Icon: {notif.get('ai_icon', 'N/A')}")
        else:
            print(f"   ❌ Notifications failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Notifications error: {e}")
    
    # Step 4: Test donation with notification
    print("\n4. Testing donation with AI notification...")
    try:
        data = {
            "user_id": 1,
            "storage_id": 1,
            "item_name": "Winter Coats",  # High-demand item
            "quantity": 2
        }
        response = requests.post('http://localhost:8000/donate', json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Donation successful!")
            print(f"   Points awarded: {result.get('points_awarded', 0)}")
            print(f"   New total: {result.get('new_total_points', 0)}")
            print(f"   Bonus points: {result.get('bonus_points', 0)}")
            
            if result.get('notification'):
                print(f"   🤖 AI Notification: {result['notification'].get('message', 'No message')}")
                print(f"   AI Icon: {result['notification'].get('ai_icon', 'N/A')}")
            else:
                print("   ❌ No AI notification generated")
        else:
            print(f"   ❌ Donation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Donation error: {e}")
    
    print(f"\n🎉 TESTING COMPLETE!")
    print(f"✅ Backend is running at: http://localhost:8000")
    print(f"🎯 Start dashboard with: streamlit run fast_dashboard.py")
    print(f"💡 The dashboard should now show:")
    print(f"   - Priority Items with proper bonus points")
    print(f"   - AI-Powered Notifications section with content")
    print(f"   - Working donation system with immediate notifications")

if __name__ == "__main__":
    comprehensive_test()
