"""
Enhanced Goodwill Platform Backend API
A comprehensive FastAPI backend with all gamification features
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json
import logging
import uuid
import hashlib
import time
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🎮 Goodwill Gaming Platform API",
    description="Complete gamified donation platform with advanced features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Data Models
class DonationType(str, Enum):
    MONETARY = "monetary"
    GOODS = "goods"
    TIME = "time"
    CRYPTO = "crypto"

class UserTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class AchievementType(str, Enum):
    FIRST_DONATION = "first_donation"
    GENEROUS_GIVER = "generous_giver"
    CHAMPION_DONOR = "champion_donor"
    CONSISTENT_SUPPORTER = "consistent_supporter"
    CRYPTO_PIONEER = "crypto_pioneer"
    TIME_VOLUNTEER = "time_volunteer"
    GOODS_DONOR = "goods_donor"
    STREAK_MASTER = "streak_master"

# Request/Response Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    preferred_causes: List[str] = []

class User(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    preferred_causes: List[str]
    tier: UserTier
    total_donations: int
    total_amount: float
    total_points: int
    achievements: List[str]
    streak_days: int
    last_donation: Optional[datetime]
    created_at: datetime
    is_active: bool

class DonationCreate(BaseModel):
    amount: float = Field(..., gt=0)
    donation_type: DonationType = DonationType.MONETARY
    message: Optional[str] = Field(None, max_length=500)
    user_id: str
    charity_category: Optional[str] = None
    is_anonymous: bool = False

class Donation(BaseModel):
    donation_id: str
    user_id: str
    amount: float
    donation_type: DonationType
    message: Optional[str]
    charity_category: Optional[str]
    points_awarded: int
    base_points: int
    bonus_points: int
    tier_multiplier: float
    streak_bonus: int
    status: str
    is_anonymous: bool
    created_at: datetime

class Achievement(BaseModel):
    achievement_id: str
    type: AchievementType
    name: str
    description: str
    icon: str
    points_reward: int
    requirement: str
    unlocked: bool
    unlocked_at: Optional[datetime]

class Leaderboard(BaseModel):
    period: str
    users: List[Dict]
    updated_at: datetime

class PlatformStats(BaseModel):
    total_donations: int
    total_amount: float
    total_users: int
    active_users: int
    average_donation: float
    top_charity_categories: List[Dict]
    tier_distribution: Dict[str, int]
    recent_milestones: List[Dict]

# Enhanced In-memory Storage
class DataStore:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.donations: List[Donation] = []
        self.achievements_catalog: Dict[str, Achievement] = {}
        self.user_achievements: Dict[str, List[str]] = {}
        self.leaderboards: Dict[str, Leaderboard] = {}
        self._initialize_achievements()
        self._create_demo_data()
    
    def _initialize_achievements(self):
        """Initialize achievement catalog"""
        achievements_data = [
            {
                "type": AchievementType.FIRST_DONATION,
                "name": "First Steps",
                "description": "Make your first donation",
                "icon": "🎯",
                "points_reward": 100,
                "requirement": "Complete 1 donation"
            },
            {
                "type": AchievementType.GENEROUS_GIVER,
                "name": "Generous Giver", 
                "description": "Donate $100 or more",
                "icon": "💰",
                "points_reward": 500,
                "requirement": "Single donation ≥ $100"
            },
            {
                "type": AchievementType.CHAMPION_DONOR,
                "name": "Champion Donor",
                "description": "Reach $500 in total donations",
                "icon": "🏆",
                "points_reward": 1000,
                "requirement": "Total donations ≥ $500"
            },
            {
                "type": AchievementType.CONSISTENT_SUPPORTER,
                "name": "Consistent Supporter",
                "description": "Make 10 donations",
                "icon": "⭐",
                "points_reward": 750,
                "requirement": "Complete 10 donations"
            },
            {
                "type": AchievementType.STREAK_MASTER,
                "name": "Streak Master",
                "description": "Donate for 7 consecutive days",
                "icon": "🔥",
                "points_reward": 1500,
                "requirement": "7-day donation streak"
            },
            {
                "type": AchievementType.CRYPTO_PIONEER,
                "name": "Crypto Pioneer",
                "description": "Make a cryptocurrency donation",
                "icon": "₿",
                "points_reward": 2000,
                "requirement": "1 crypto donation"
            }
        ]
        
        for ach_data in achievements_data:
            ach_id = str(uuid.uuid4())
            self.achievements_catalog[ach_id] = Achievement(
                achievement_id=ach_id,
                type=ach_data["type"],
                name=ach_data["name"],
                description=ach_data["description"],
                icon=ach_data["icon"],
                points_reward=ach_data["points_reward"],
                requirement=ach_data["requirement"],
                unlocked=False,
                unlocked_at=None
            )

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            preferred_causes=user_data.preferred_causes,
            tier=UserTier.BRONZE,
            total_donations=0,
            total_amount=0.0,
            total_points=0,
            achievements=[],
            streak_days=0,
            last_donation=None,
            created_at=datetime.now(),
            is_active=True
        )
        
        self.users[user_id] = user
        self.user_achievements[user_id] = []
        return user
        
    def _create_demo_data(self):
        """Create some demo users and donations"""
        demo_users = [
            {"username": "alice_demo", "email": "alice@demo.com", "full_name": "Alice Demo"},
            {"username": "bob_demo", "email": "bob@demo.com", "full_name": "Bob Demo"},
            {"username": "charlie_demo", "email": "charlie@demo.com", "full_name": "Charlie Demo"}
        ]
        
        for user_data in demo_users:
            self.create_user(UserCreate(**user_data))

# Global data store
db = DataStore()

# Helper Functions
class GameEngine:
    @staticmethod
    def calculate_points(amount: float, user: User, donation_type: DonationType) -> Dict:
        """Enhanced points calculation with multiple factors"""
        base_points = int(amount * 10)  # Base: 10 points per dollar
        
        # Tier multiplier
        tier_multipliers = {
            UserTier.BRONZE: 1.0,
            UserTier.SILVER: 1.25,
            UserTier.GOLD: 1.5,
            UserTier.PLATINUM: 2.0
        }
        tier_multiplier = tier_multipliers[user.tier]
        
        # Donation type bonus
        type_bonuses = {
            DonationType.MONETARY: 1.0,
            DonationType.CRYPTO: 1.5,
            DonationType.GOODS: 1.2,
            DonationType.TIME: 2.0  # Time is most valuable
        }
        type_bonus = type_bonuses[donation_type]
        
        # Streak bonus
        streak_bonus = min(user.streak_days * 50, 500)  # Max 500 bonus
        
        # Calculate totals
        tier_points = int(base_points * tier_multiplier)
        type_points = int(base_points * type_bonus)
        bonus_points = type_points - base_points + streak_bonus
        total_points = base_points + bonus_points
        
        return {
            "base_points": base_points,
            "bonus_points": bonus_points,
            "tier_multiplier": tier_multiplier,
            "streak_bonus": streak_bonus,
            "total_points": total_points
        }
    
    @staticmethod
    def update_user_tier(user: User) -> bool:
        """Update user tier based on total donations"""
        old_tier = user.tier
        
        if user.total_amount >= 2000:
            user.tier = UserTier.PLATINUM
        elif user.total_amount >= 500:
            user.tier = UserTier.GOLD
        elif user.total_amount >= 100:
            user.tier = UserTier.SILVER
        else:
            user.tier = UserTier.BRONZE
        
        return old_tier != user.tier
    
    @staticmethod
    def check_achievements(user: User, donation: Donation) -> List[str]:
        """Check and unlock achievements"""
        new_achievements = []
        user_achievements = db.user_achievements.get(user.user_id, [])
        
        for ach_id, achievement in db.achievements_catalog.items():
            if ach_id in user_achievements:
                continue
                
            unlocked = False
            
            if achievement.type == AchievementType.FIRST_DONATION:
                unlocked = user.total_donations >= 1
            elif achievement.type == AchievementType.GENEROUS_GIVER:
                unlocked = donation.amount >= 100
            elif achievement.type == AchievementType.CHAMPION_DONOR:
                unlocked = user.total_amount >= 500
            elif achievement.type == AchievementType.CONSISTENT_SUPPORTER:
                unlocked = user.total_donations >= 10
            elif achievement.type == AchievementType.STREAK_MASTER:
                unlocked = user.streak_days >= 7
            elif achievement.type == AchievementType.CRYPTO_PIONEER:
                unlocked = donation.donation_type == DonationType.CRYPTO
            
            if unlocked:
                new_achievements.append(ach_id)
                user.total_points += achievement.points_reward
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now()
        
        if new_achievements:
            if user.user_id not in db.user_achievements:
                db.user_achievements[user.user_id] = []
            db.user_achievements[user.user_id].extend(new_achievements)
        
        return new_achievements

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "🎮 Goodwill Gaming Platform API v2.0",
        "status": "✅ Enhanced & Ready!",
        "features": [
            "Advanced Gamification",
            "Multi-tier System", 
            "Achievement Engine",
            "Leaderboards",
            "Streak System",
            "Multiple Donation Types"
        ],
        "endpoints": {
            "docs": "/docs",
            "users": "/users",
            "donations": "/donations",
            "achievements": "/achievements",
            "leaderboard": "/leaderboard",
            "stats": "/stats"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "database": f"{len(db.users)} users, {len(db.donations)} donations",
        "services": {
            "api": "✅ online",
            "gamification": "✅ active",
            "achievements": "✅ ready",
            "leaderboards": "✅ updated"
        }
    }

@app.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user account"""
    # Check if username/email already exists
    for existing_user in db.users.values():
        if existing_user.username == user_data.username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if existing_user.email == user_data.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    user_id = str(uuid.uuid4())
    user = User(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        preferred_causes=user_data.preferred_causes,
        tier=UserTier.BRONZE,
        total_donations=0,
        total_amount=0.0,
        total_points=0,
        achievements=[],
        streak_days=0,
        last_donation=None,
        created_at=datetime.now(),
        is_active=True
    )
    
    db.users[user_id] = user
    db.user_achievements[user_id] = []
    
    logger.info(f"Created new user: {user.username}")
    return user

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user profile by ID"""
    if user_id not in db.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = db.users[user_id]
    user.achievements = db.user_achievements.get(user_id, [])
    return user

@app.get("/users", response_model=List[User])
async def list_users(skip: int = 0, limit: int = 50):
    """List all users with pagination"""
    users = list(db.users.values())[skip:skip + limit]
    for user in users:
        user.achievements = db.user_achievements.get(user.user_id, [])
    return users

@app.post("/donations", response_model=Donation)
async def create_donation(donation_data: DonationCreate, background_tasks: BackgroundTasks):
    """Process a new donation with full gamification"""
    
    # Validate user exists
    if donation_data.user_id not in db.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = db.users[donation_data.user_id]
    donation_id = str(uuid.uuid4())
    
    # Calculate points
    points_info = GameEngine.calculate_points(
        donation_data.amount, user, donation_data.donation_type
    )
    
    # Create donation record
    donation = Donation(
        donation_id=donation_id,
        user_id=donation_data.user_id,
        amount=donation_data.amount,
        donation_type=donation_data.donation_type,
        message=donation_data.message,
        charity_category=donation_data.charity_category,
        points_awarded=points_info["total_points"],
        base_points=points_info["base_points"],
        bonus_points=points_info["bonus_points"],
        tier_multiplier=points_info["tier_multiplier"],
        streak_bonus=points_info["streak_bonus"],
        status="completed",
        is_anonymous=donation_data.is_anonymous,
        created_at=datetime.now()
    )
    
    # Update user stats
    user.total_donations += 1
    user.total_amount += donation_data.amount
    user.total_points += points_info["total_points"]
    
    # Update streak
    now = datetime.now()
    if user.last_donation and (now - user.last_donation).days == 1:
        user.streak_days += 1
    elif user.last_donation is None or (now - user.last_donation).days > 1:
        user.streak_days = 1
    
    user.last_donation = now
    
    # Check tier upgrade
    tier_upgraded = GameEngine.update_user_tier(user)
    
    # Check achievements
    new_achievements = GameEngine.check_achievements(user, donation)
    
    # Store donation
    db.donations.append(donation)
    
    # Background task for notifications/analytics
    background_tasks.add_task(
        log_donation_analytics, 
        donation_id, 
        tier_upgraded, 
        new_achievements
    )
    
    logger.info(f"Donation processed: {donation_id} for ${donation.amount}")
    
    return donation

@app.get("/donations")
async def get_donations(
    user_id: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    """Get donations with optional filtering"""
    donations = db.donations
    
    if user_id:
        donations = [d for d in donations if d.user_id == user_id]
    
    # Sort by most recent first
    donations.sort(key=lambda x: x.created_at, reverse=True)
    
    return {
        "donations": donations[skip:skip + limit],
        "total_count": len(donations),
        "has_more": len(donations) > skip + limit
    }

@app.get("/achievements")
async def get_achievements(user_id: Optional[str] = None):
    """Get achievements catalog or user achievements"""
    if user_id:
        if user_id not in db.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_achievement_ids = db.user_achievements.get(user_id, [])
        user_achievements = []
        
        for ach_id, achievement in db.achievements_catalog.items():
            ach_copy = achievement.model_copy()
            ach_copy.unlocked = ach_id in user_achievement_ids
            if ach_copy.unlocked:
                # Find when it was unlocked (simplified)
                ach_copy.unlocked_at = datetime.now()
            user_achievements.append(ach_copy)
        
        return {
            "user_id": user_id,
            "achievements": user_achievements,
            "total_unlocked": len(user_achievement_ids),
            "total_available": len(db.achievements_catalog)
        }
    
    return {
        "achievements": list(db.achievements_catalog.values()),
        "total_count": len(db.achievements_catalog)
    }

@app.get("/leaderboard")
async def get_leaderboard(period: str = "all_time", limit: int = 10):
    """Get user leaderboard"""
    users = list(db.users.values())
    
    if period == "monthly":
        # Simplified - would filter by date in real implementation
        users = [u for u in users if u.last_donation and 
                (datetime.now() - u.last_donation).days <= 30]
    
    # Sort by total points
    users.sort(key=lambda x: x.total_points, reverse=True)
    
    leaderboard_data = []
    for i, user in enumerate(users[:limit]):
        leaderboard_data.append({
            "rank": i + 1,
            "user_id": user.user_id,
            "username": user.username,
            "points": user.total_points,
            "tier": user.tier,
            "total_donated": user.total_amount,
            "streak_days": user.streak_days
        })
    
    return {
        "period": period,
        "leaderboard": leaderboard_data,
        "updated_at": datetime.now()
    }

@app.get("/stats", response_model=PlatformStats)
async def get_platform_stats():
    """Get comprehensive platform statistics"""
    total_donations = len(db.donations)
    total_amount = sum(d.amount for d in db.donations)
    total_users = len(db.users)
    active_users = len([u for u in db.users.values() if u.is_active])
    
    # Tier distribution
    tier_dist = {tier.value: 0 for tier in UserTier}
    for user in db.users.values():
        tier_dist[user.tier.value] += 1
    
    # Top charity categories
    category_stats = {}
    for donation in db.donations:
        if donation.charity_category:
            category_stats[donation.charity_category] = \
                category_stats.get(donation.charity_category, 0) + donation.amount
    
    top_categories = [
        {"category": k, "total_amount": v}
        for k, v in sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Recent milestones
    recent_milestones = [
        {"type": "New Gold Member", "description": "Charlie reached Gold tier!", "timestamp": datetime.now()},
        {"type": "Achievement Unlocked", "description": "5 users unlocked Generous Giver!", "timestamp": datetime.now()}
    ]
    
    return PlatformStats(
        total_donations=total_donations,
        total_amount=total_amount,
        total_users=total_users,
        active_users=active_users,
        average_donation=total_amount / max(total_donations, 1),
        top_charity_categories=top_categories,
        tier_distribution=tier_dist,
        recent_milestones=recent_milestones
    )

# Background Tasks
async def log_donation_analytics(donation_id: str, tier_upgraded: bool, new_achievements: List[str]):
    """Log analytics data (would integrate with external services)"""
    logger.info(f"Analytics: Donation {donation_id}")
    if tier_upgraded:
        logger.info(f"Tier upgrade detected for donation {donation_id}")
    if new_achievements:
        logger.info(f"New achievements unlocked: {len(new_achievements)}")



if __name__ == "__main__":
    import uvicorn
    logger.info("🎮 Starting Enhanced Goodwill Platform API...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")