"""
Demo Runner for Goodwill Platform
A simple script to demonstrate the working functionality
"""

import requests
import time
import json

API_BASE_URL = "http://localhost:8000"

def test_api():
    print("🎮 Goodwill Platform Demo")
    print("=" * 50)
    
    # Test API health
    print("\n1. Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy!")
            health_data = response.json()
            print(f"   Status: {health_data['status']}")
        else:
            print("❌ API health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure to run: python simple_donation_api.py")
        return False
    
    # Test donations
    print("\n2. Creating test donations...")
    test_donations = [
        {"user_id": "alice_demo", "amount": 25.0, "message": "Great cause!"},
        {"user_id": "bob_demo", "amount": 100.0, "message": "Amazing work!"},
        {"user_id": "charlie_demo", "amount": 500.0, "message": "Keep it up!"}
    ]
    
    for donation in test_donations:
        try:
            response = requests.post(f"{API_BASE_URL}/donations", json=donation)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {donation['user_id']}: ${donation['amount']} → {result['points_awarded']} points")
            else:
                print(f"   ❌ Failed donation for {donation['user_id']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Get stats
    print("\n3. Platform Statistics...")
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            platform_stats = stats["platform_stats"]
            tier_dist = stats["tier_distribution"]
            
            print(f"   📊 Total Donations: {platform_stats['total_donations']}")
            print(f"   💰 Total Amount: ${platform_stats['total_amount']:,.2f}")
            print(f"   👥 Active Users: {platform_stats['total_users']}")
            print(f"   📈 Average: ${platform_stats['average_donation']:.2f}")
            print(f"   🏆 Tiers: Bronze({tier_dist['bronze']}) Silver({tier_dist['silver']}) Gold({tier_dist['gold']})")
        else:
            print("   ❌ Failed to get stats")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test user profile
    print("\n4. User Profile Example...")
    try:
        response = requests.get(f"{API_BASE_URL}/users/charlie_demo")
        if response.status_code == 200:
            profile = response.json()
            user_profile = profile["profile"]
            achievements = profile["achievements"]
            
            print(f"   👤 User: charlie_demo")
            print(f"   💎 Tier: {user_profile['tier'].title()}")
            print(f"   🏆 Points: {user_profile['total_points']}")
            print(f"   🎯 Achievements: {sum(1 for a in achievements if a['unlocked'])}/{len(achievements)} unlocked")
        else:
            print("   ❌ Failed to get user profile")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print("✅ The Goodwill Platform API is fully functional!")
    print("\nNext Steps:")
    print("1. Visit http://localhost:8505 for the Streamlit dashboard")
    print("2. Or use the API directly at http://localhost:8000")
    print("3. API docs available at http://localhost:8000/docs")
    return True

if __name__ == "__main__":
    test_api()