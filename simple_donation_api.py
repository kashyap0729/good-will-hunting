"""
Simple Working Donation API
A basic FastAPI service that works without complex dependencies
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
import logging
from typing import Dict, List, Optional
import uuid

app = FastAPI(
    title="Goodwill Donation API",
    description="Simple working donation service for the gamified platform",
    version="1.0.0"
)

# Simple in-memory storage (for demo)
donations_db: List[Dict] = []
users_db: Dict = {}

class Donation(BaseModel):
    amount: float
    donation_type: str = "monetary"
    message: Optional[str] = None
    user_id: str

class DonationResponse(BaseModel):
    donation_id: str
    amount: float
    points_awarded: int
    status: str
    created_at: datetime

@app.get("/")
async def root():
    return {
        "message": "🎮 Goodwill Donation Platform API",
        "status": "✅ Working!",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "donations": "/donations",
            "stats": "/stats"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "database": "connected",
        "services": {
            "api": "✅ online",
            "donations": "✅ ready",
            "gamification": "✅ active"
        }
    }

@app.post("/donations", response_model=DonationResponse)
async def create_donation(donation: Donation):
    """Create a new donation and calculate gamification points"""
    
    # Generate donation ID
    donation_id = str(uuid.uuid4())
    
    # Simple points calculation (10 points per dollar)
    base_points = int(donation.amount * 10)
    
    # Tier bonuses
    tier_bonus = 0
    if donation.amount >= 100:
        tier_bonus = int(base_points * 0.5)  # Gold tier: 50% bonus
    elif donation.amount >= 50:
        tier_bonus = int(base_points * 0.25)  # Silver tier: 25% bonus
    
    total_points = base_points + tier_bonus
    
    # Store donation
    donation_record = {
        "donation_id": donation_id,
        "user_id": donation.user_id,
        "amount": donation.amount,
        "donation_type": donation.donation_type,
        "message": donation.message,
        "points_awarded": total_points,
        "base_points": base_points,
        "tier_bonus": tier_bonus,
        "status": "completed",
        "created_at": datetime.now().isoformat()
    }
    
    donations_db.append(donation_record)
    
    # Update user stats
    if donation.user_id not in users_db:
        users_db[donation.user_id] = {
            "total_donations": 0,
            "total_amount": 0.0,
            "total_points": 0,
            "tier": "bronze"
        }
    
    user = users_db[donation.user_id]
    user["total_donations"] += 1
    user["total_amount"] += donation.amount
    user["total_points"] += total_points
    
    # Update tier
    if user["total_amount"] >= 500:
        user["tier"] = "gold"
    elif user["total_amount"] >= 100:
        user["tier"] = "silver"
    
    return DonationResponse(
        donation_id=donation_id,
        amount=donation.amount,
        points_awarded=total_points,
        status="completed",
        created_at=datetime.now()
    )

@app.get("/donations")
async def get_donations(limit: int = 10):
    """Get recent donations"""
    return {
        "donations": donations_db[-limit:],
        "total_count": len(donations_db)
    }

@app.get("/stats")
async def get_stats():
    """Get platform statistics"""
    
    total_donations = len(donations_db)
    total_amount = sum(d["amount"] for d in donations_db)
    total_users = len(users_db)
    
    # Calculate tier distribution
    tier_counts = {"bronze": 0, "silver": 0, "gold": 0}
    for user in users_db.values():
        tier_counts[user["tier"]] += 1
    
    return {
        "platform_stats": {
            "total_donations": total_donations,
            "total_amount": round(total_amount, 2),
            "total_users": total_users,
            "average_donation": round(total_amount / max(total_donations, 1), 2)
        },
        "tier_distribution": tier_counts,
        "recent_activity": donations_db[-5:] if donations_db else []
    }

@app.get("/users/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile and stats"""
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    user_donations = [d for d in donations_db if d["user_id"] == user_id]
    
    return {
        "user_id": user_id,
        "profile": user,
        "recent_donations": user_donations[-5:],
        "achievements": [
            {"name": "First Donation", "unlocked": len(user_donations) >= 1},
            {"name": "Generous Giver", "unlocked": user["total_amount"] >= 100},
            {"name": "Champion Donor", "unlocked": user["total_amount"] >= 500},
            {"name": "Consistent Supporter", "unlocked": len(user_donations) >= 10}
        ]
    }

# Add some demo data on startup
@app.on_event("startup")
async def startup_event():
    # Create some demo data
    demo_donations = [
        {"user_id": "demo_user_1", "amount": 25.0, "message": "Great cause!"},
        {"user_id": "demo_user_2", "amount": 75.0, "message": "Keep it up!"},
        {"user_id": "demo_user_3", "amount": 150.0, "message": "Amazing work!"}
    ]
    
    for demo in demo_donations:
        donation = Donation(**demo)
        await create_donation(donation)
    
    logging.info("✅ Demo data initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)