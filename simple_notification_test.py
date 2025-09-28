#!/usr/bin/env python3
"""
Simple test to verify notification mode
"""
from notification_agent import notify_donation, notify_achievement

print("Testing current notification system...")
print("=" * 40)

print("1. Testing donation notification:")
result1 = notify_donation('Winter Coats', 150, is_high_demand=True, bonus=50)
print(f"   Message: {result1['message']}")

print("\n2. Testing achievement notification:")
result2 = notify_achievement('Generous Giver', 'TestUser')
print(f"   Message: {result2['message']}")

print("\n3. Testing streak notification:")
from notification_agent import notify_streak
result3 = notify_streak(7, 'TestUser')
print(f"   Message: {result3['message']}")
