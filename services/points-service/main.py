"""
Points Service
Specialized microservice for handling gamification points, achievements, and leaderboards
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore
from typing import Dict, List, Optional
import asyncio
from contextlib import asynccontextmanager
import json
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
from enum import Enum

logger = logging.getLogger(__name__)

# Pydantic models
class AchievementType(str, Enum):
    DONATION_MILESTONE = "donation_milestone"
    LOCATION_DISCOVERY = "location_discovery"  
    STREAK_ACHIEVEMENT = "streak_achievement"
    TIER_PROGRESSION = "tier_progression"
    SOCIAL_ENGAGEMENT = "social_engagement"

class Achievement(BaseModel):
    id: str
    name: str
    description: str
    type: AchievementType
    points: int
    emoji: str
    unlocked_at: datetime
    requirements: Optional[Dict] = None

class LeaderboardEntry(BaseModel):
    user_id: str
    name: str
    points: int
    tier: str
    rank: int
    donations_count: int
    total_donated: float

class PointsTransaction(BaseModel):
    user_id: str
    points: int
    source: str  # donation, achievement, bonus, etc.
    description: str
    metadata: Optional[Dict] = None

class AchievementEngine:
    """Comprehensive achievement system with multiple unlock conditions"""
    
    def __init__(self):
        self.achievement_definitions = self._initialize_achievements()
    
    def _initialize_achievements(self) -> Dict[str, Dict]:
        """Initialize all possible achievements"""
        return {
            # Donation Milestones
            "first_donation": {
                "name": "First Steps",
                "description": "Made your first donation",
                "type": AchievementType.DONATION_MILESTONE,
                "points": 500,
                "emoji": "🎉",
                "requirements": {"donation_count": 1}
            },
            "generous_giver": {
                "name": "Generous Giver", 
                "description": "Donated $100 or more in a single donation",
                "type": AchievementType.DONATION_MILESTONE,
                "points": 1000,
                "emoji": "💝",
                "requirements": {"single_donation_amount": 100}
            },
            "hundred_club": {
                "name": "Hundred Club",
                "description": "Made 100 donations",
                "type": AchievementType.DONATION_MILESTONE,
                "points": 5000,
                "emoji": "💯",
                "requirements": {"donation_count": 100}
            },
            
            # Location Achievements
            "location_explorer": {
                "name": "Location Explorer",
                "description": "Donated to 5 different locations",
                "type": AchievementType.LOCATION_DISCOVERY,
                "points": 750,
                "emoji": "🗺️",
                "requirements": {"unique_locations": 5}
            },
            "city_champion": {
                "name": "City Champion",
                "description": "Donated to every district in the city",
                "type": AchievementType.LOCATION_DISCOVERY,
                "points": 2000,
                "emoji": "🏆",
                "requirements": {"city_coverage": 100}
            },
            "neighborhood_hero": {
                "name": "Neighborhood Hero",
                "description": "Top donor in your neighborhood",
                "type": AchievementType.LOCATION_DISCOVERY,
                "points": 1500,
                "emoji": "🦸",
                "requirements": {"neighborhood_rank": 1}
            },
            
            # Streak Achievements
            "week_warrior": {
                "name": "Week Warrior",
                "description": "Donated every day for a week",
                "type": AchievementType.STREAK_ACHIEVEMENT,
                "points": 800,
                "emoji": "🔥",
                "requirements": {"daily_streak": 7}
            },
            "consistency_king": {
                "name": "Consistency King",
                "description": "Donated every day for 30 days",
                "type": AchievementType.STREAK_ACHIEVEMENT,
                "points": 3000,
                "emoji": "👑",
                "requirements": {"daily_streak": 30}
            },
            
            # Tier Progressions
            "silver_status": {
                "name": "Silver Status",
                "description": "Reached Silver tier",
                "type": AchievementType.TIER_PROGRESSION,
                "points": 0,  # No additional points for tier progression
                "emoji": "🥈",
                "requirements": {"tier": "Silver"}
            },
            "golden_giver": {
                "name": "Golden Giver",
                "description": "Reached Gold tier",
                "type": AchievementType.TIER_PROGRESSION,
                "points": 0,
                "emoji": "🥇",
                "requirements": {"tier": "Gold"}
            },
            "platinum_plus": {
                "name": "Platinum Plus",
                "description": "Reached Platinum tier",
                "type": AchievementType.TIER_PROGRESSION,
                "points": 0,
                "emoji": "💎",
                "requirements": {"tier": "Platinum"}
            },
            "diamond_dynasty": {
                "name": "Diamond Dynasty",
                "description": "Reached Diamond tier",
                "type": AchievementType.TIER_PROGRESSION,
                "points": 0,
                "emoji": "💠",
                "requirements": {"tier": "Diamond"}
            },
            
            # Social Engagement
            "social_sharer": {
                "name": "Social Sharer",
                "description": "Shared 10 donations on social media",
                "type": AchievementType.SOCIAL_ENGAGEMENT,
                "points": 500,
                "emoji": "📱",
                "requirements": {"social_shares": 10}
            },
            "referral_champion": {
                "name": "Referral Champion", 
                "description": "Referred 5 new donors",
                "type": AchievementType.SOCIAL_ENGAGEMENT,
                "points": 2500,
                "emoji": "🤝",
                "requirements": {"referrals": 5}
            }
        }
    
    async def check_achievements(self, user_id: str, user_stats: Dict, recent_activity: Dict) -> List[Achievement]:
        """Check for newly unlocked achievements"""
        
        unlocked_achievements = []
        
        # Get user's existing achievements
        existing_achievements = set(user_stats.get('achievements', []))
        
        for achievement_id, achievement_def in self.achievement_definitions.items():
            
            # Skip if already unlocked
            if achievement_id in existing_achievements:
                continue
            
            # Check if requirements are met
            if self._check_requirements(achievement_def['requirements'], user_stats, recent_activity):
                
                achievement = Achievement(
                    id=achievement_id,
                    name=achievement_def['name'],
                    description=achievement_def['description'],
                    type=achievement_def['type'],
                    points=achievement_def['points'],
                    emoji=achievement_def['emoji'],
                    unlocked_at=datetime.now(),
                    requirements=achievement_def['requirements']
                )
                
                unlocked_achievements.append(achievement)
        
        return unlocked_achievements
    
    def _check_requirements(self, requirements: Dict, user_stats: Dict, recent_activity: Dict) -> bool:
        """Check if achievement requirements are met"""
        
        for req_key, req_value in requirements.items():
            
            if req_key == "donation_count":
                if user_stats.get('total_donations', 0) < req_value:
                    return False
            
            elif req_key == "single_donation_amount":
                if recent_activity.get('donation_amount', 0) < req_value:
                    return False
            
            elif req_key == "unique_locations":
                if len(user_stats.get('unique_locations', [])) < req_value:
                    return False
            
            elif req_key == "daily_streak":
                if user_stats.get('current_streak', 0) < req_value:
                    return False
            
            elif req_key == "tier":
                if user_stats.get('tier') != req_value:
                    return False
            
            elif req_key == "social_shares":
                if user_stats.get('social_shares', 0) < req_value:
                    return False
            
            elif req_key == "referrals":
                if user_stats.get('referrals', 0) < req_value:
                    return False
            
            # Add more requirement checks as needed
        
        return True

class LeaderboardManager:
    """Manage various leaderboards and rankings"""
    
    def __init__(self, db: firestore.AsyncClient):
        self.db = db
    
    async def get_global_leaderboard(self, limit: int = 100) -> List[LeaderboardEntry]:
        """Get global points leaderboard"""
        
        try:
            # Query top users by total points
            query = self.db.collection('users').order_by('total_points', direction=firestore.Query.DESCENDING).limit(limit)
            
            leaderboard = []
            rank = 1
            
            async for doc in query.stream():
                user_data = doc.to_dict()
                
                entry = LeaderboardEntry(
                    user_id=doc.id,
                    name=user_data.get('name', 'Anonymous'),
                    points=user_data.get('total_points', 0),
                    tier=user_data.get('tier', 'Bronze'),
                    rank=rank,
                    donations_count=user_data.get('total_donations', 0),
                    total_donated=user_data.get('total_amount_donated', 0.0)
                )
                
                leaderboard.append(entry)
                rank += 1
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting global leaderboard: {str(e)}")
            return []
    
    async def get_tier_leaderboard(self, tier: str, limit: int = 50) -> List[LeaderboardEntry]:
        """Get leaderboard for specific tier"""
        
        try:
            query = (self.db.collection('users')
                    .where('tier', '==', tier)
                    .order_by('total_points', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            
            leaderboard = []
            rank = 1
            
            async for doc in query.stream():
                user_data = doc.to_dict()
                
                entry = LeaderboardEntry(
                    user_id=doc.id,
                    name=user_data.get('name', 'Anonymous'),
                    points=user_data.get('total_points', 0),
                    tier=tier,
                    rank=rank,
                    donations_count=user_data.get('total_donations', 0),
                    total_donated=user_data.get('total_amount_donated', 0.0)
                )
                
                leaderboard.append(entry)
                rank += 1
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting tier leaderboard: {str(e)}")
            return []
    
    async def get_location_leaderboard(self, location: Dict, radius_km: float = 10, limit: int = 50) -> List[LeaderboardEntry]:
        """Get leaderboard for users in specific geographic area"""
        
        try:
            # In production, would use geospatial queries
            # For demo, returning global leaderboard
            return await self.get_global_leaderboard(limit)
            
        except Exception as e:
            logger.error(f"Error getting location leaderboard: {str(e)}")
            return []
    
    async def get_user_rank(self, user_id: str) -> Optional[int]:
        """Get user's current global rank"""
        
        try:
            # Get user's points
            user_doc = await self.db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return None
            
            user_points = user_doc.to_dict().get('total_points', 0)
            
            # Count users with higher points
            query = self.db.collection('users').where('total_points', '>', user_points)
            higher_ranked_users = len([doc async for doc in query.stream()])
            
            return higher_ranked_users + 1
            
        except Exception as e:
            logger.error(f"Error getting user rank: {str(e)}")
            return None

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db = firestore.AsyncClient()
    app.state.achievement_engine = AchievementEngine()
    app.state.leaderboard_manager = LeaderboardManager(app.state.db)
    
    logger.info("Points service startup complete")
    yield
    
    # Cleanup
    logger.info("Points service shutdown complete")

# FastAPI app initialization
app = FastAPI(
    title="Points & Achievements Service",
    description="Gamification service for points, achievements, and leaderboards",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency functions
async def get_db():
    return app.state.db

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "points-service"
    }

@app.post("/api/v1/points/award")
async def award_points(
    transaction: PointsTransaction,
    db: firestore.AsyncClient = Depends(get_db)
):
    """Award points to user and check for achievements"""
    
    try:
        user_id = transaction.user_id
        
        # Get current user stats
        user_doc_ref = db.collection('users').document(user_id)
        user_doc = await user_doc_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict()
        current_points = user_data.get('total_points', 0)
        new_total = current_points + transaction.points
        
        # Update user points
        await user_doc_ref.update({
            'total_points': new_total,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        # Record points transaction
        transaction_record = {
            'user_id': user_id,
            'points': transaction.points,
            'source': transaction.source,
            'description': transaction.description,
            'metadata': transaction.metadata or {},
            'timestamp': firestore.SERVER_TIMESTAMP,
            'running_total': new_total
        }
        
        await db.collection('points_transactions').add(transaction_record)
        
        # Check for newly unlocked achievements
        recent_activity = transaction.metadata or {}
        unlocked_achievements = await app.state.achievement_engine.check_achievements(
            user_id, user_data, recent_activity
        )
        
        # Save any new achievements
        for achievement in unlocked_achievements:
            await db.collection('user_achievements').add({
                'user_id': user_id,
                'achievement_id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'points': achievement.points,
                'emoji': achievement.emoji,
                'unlocked_at': achievement.unlocked_at,
                'type': achievement.type
            })
            
            # Update user's achievement list
            user_achievements = user_data.get('achievements', [])
            user_achievements.append(achievement.id)
            await user_doc_ref.update({
                'achievements': user_achievements
            })
        
        return {
            'success': True,
            'points_awarded': transaction.points,
            'total_points': new_total,
            'achievements_unlocked': [
                {
                    'id': ach.id,
                    'name': ach.name,
                    'description': ach.description,
                    'points': ach.points,
                    'emoji': ach.emoji
                }
                for ach in unlocked_achievements
            ],
            'transaction_id': str(uuid.uuid4())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error awarding points: {str(e)}")
        raise HTTPException(status_code=500, detail="Error awarding points")

@app.get("/api/v1/leaderboard/global")
async def get_global_leaderboard(
    limit: int = 100,
    offset: int = 0
):
    """Get global points leaderboard"""
    
    try:
        leaderboard = await app.state.leaderboard_manager.get_global_leaderboard(limit + offset)
        
        # Apply offset
        paginated_results = leaderboard[offset:offset + limit]
        
        return {
            'success': True,
            'leaderboard': [entry.dict() for entry in paginated_results],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total_shown': len(paginated_results)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting global leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving leaderboard")

@app.get("/api/v1/leaderboard/tier/{tier}")
async def get_tier_leaderboard(
    tier: str,
    limit: int = 50
):
    """Get leaderboard for specific tier"""
    
    valid_tiers = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]
    if tier not in valid_tiers:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    try:
        leaderboard = await app.state.leaderboard_manager.get_tier_leaderboard(tier, limit)
        
        return {
            'success': True,
            'tier': tier,
            'leaderboard': [entry.dict() for entry in leaderboard]
        }
        
    except Exception as e:
        logger.error(f"Error getting tier leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving tier leaderboard")

@app.get("/api/v1/users/{user_id}/achievements")
async def get_user_achievements(
    user_id: str,
    db: firestore.AsyncClient = Depends(get_db)
):
    """Get user's unlocked achievements"""
    
    try:
        query = db.collection('user_achievements').where('user_id', '==', user_id).order_by('unlocked_at', direction=firestore.Query.DESCENDING)
        
        achievements = []
        async for doc in query.stream():
            achievement_data = doc.to_dict()
            achievements.append(achievement_data)
        
        return {
            'success': True,
            'user_id': user_id,
            'achievements': achievements,
            'total_count': len(achievements)
        }
        
    except Exception as e:
        logger.error(f"Error getting user achievements: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving achievements")

@app.get("/api/v1/users/{user_id}/rank")
async def get_user_rank(
    user_id: str
):
    """Get user's current global rank"""
    
    try:
        rank = await app.state.leaderboard_manager.get_user_rank(user_id)
        
        if rank is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            'success': True,
            'user_id': user_id,
            'global_rank': rank
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user rank: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving user rank")

@app.get("/api/v1/users/{user_id}/points/history")
async def get_points_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    db: firestore.AsyncClient = Depends(get_db)
):
    """Get user's points transaction history"""
    
    try:
        query = (db.collection('points_transactions')
                .where('user_id', '==', user_id)
                .order_by('timestamp', direction=firestore.Query.DESCENDING)
                .offset(offset)
                .limit(limit))
        
        transactions = []
        async for doc in query.stream():
            transaction_data = doc.to_dict()
            transaction_data['id'] = doc.id
            transactions.append(transaction_data)
        
        return {
            'success': True,
            'user_id': user_id,
            'transactions': transactions,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'count': len(transactions)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting points history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving points history")

@app.get("/api/v1/achievements/available")
async def get_available_achievements():
    """Get all available achievements"""
    
    try:
        achievement_definitions = app.state.achievement_engine.achievement_definitions
        
        achievements = []
        for achievement_id, achievement_def in achievement_definitions.items():
            achievements.append({
                'id': achievement_id,
                'name': achievement_def['name'],
                'description': achievement_def['description'],
                'type': achievement_def['type'],
                'points': achievement_def['points'],
                'emoji': achievement_def['emoji'],
                'requirements': achievement_def['requirements']
            })
        
        return {
            'success': True,
            'achievements': achievements,
            'total_count': len(achievements)
        }
        
    except Exception as e:
        logger.error(f"Error getting available achievements: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving achievements")

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )