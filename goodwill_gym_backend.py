"""
Enhanced Backend API v3.0 with SQLite Database and Google ADK Integration
Pokemon Go-style gym system with missing items gamification
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional, Union
from datetime import datetime, date
import sqlite3
import json
import logging
from enum import Enum

# Import our custom modules
from database import DatabaseManager, get_missing_items, update_gym_leader
from notification_agent import (
    notification_agent, 
    notify_achievement, 
    notify_donation, 
    notify_streak,
    notify_gym_leader,
    NotificationType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🎮 Goodwill Gym Platform API v3.0",
    description="Pokemon Go-style gamified donation platform with SQLite and Google ADK integration",
    version="3.0.0",
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

# Initialize database
db = DatabaseManager()

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class DonationCreate(BaseModel):
    user_id: int
    storage_id: int
    item_name: str
    quantity: int = 1

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    tier: str
    total_points: int
    total_donations: int
    streak_days: int
    achievements: List[str]

class Storage(BaseModel):
    id: int
    name: str
    address: Optional[str]
    latitude: float
    longitude: float
    gym_leader_id: Optional[int]
    gym_leader_username: Optional[str]
    gym_leader_points: int
    current_items: int

class DonationResponse(BaseModel):
    donation_id: int
    points_awarded: int
    bonus_points: int
    missing_item_bonus: bool
    notification: Dict
    tier_upgraded: bool = False

# Helper Functions
def calculate_points(item_name: str, quantity: int, is_missing_item: bool = False) -> Dict:
    """Calculate points for a donation"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get base points from catalog
        cursor.execute("""
            SELECT base_points, demand_multiplier 
            FROM item_catalog 
            WHERE item_name = ?
        """, (item_name,))
        
        result = cursor.fetchone()
        if result:
            base_points = result['base_points']
            demand_multiplier = result['demand_multiplier']
        else:
            base_points = 10  # Default
            demand_multiplier = 1.0
        
        # Calculate points
        item_points = int(base_points * quantity * demand_multiplier)
        bonus_points = 0
        
        # Missing item bonus
        if is_missing_item:
            cursor.execute("""
                SELECT bonus_points 
                FROM missing_items_requests 
                WHERE item_name = ? AND fulfilled = 0
                ORDER BY bonus_points DESC
                LIMIT 1
            """, (item_name,))
            
            bonus_result = cursor.fetchone()
            if bonus_result:
                bonus_points = bonus_result['bonus_points'] * quantity
        
        total_points = item_points + bonus_points
        
        return {
            'base_points': item_points,
            'bonus_points': bonus_points,
            'total_points': total_points,
            'is_missing_item': is_missing_item
        }
        
    except Exception as e:
        logger.error(f"Error calculating points: {e}")
        return {'base_points': 10, 'bonus_points': 0, 'total_points': 10, 'is_missing_item': False}
    finally:
        conn.close()

def update_user_tier(user_id: int) -> Optional[str]:
    """Update user tier based on total points"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT tier, total_points FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            return None
        
        current_tier = result['tier']
        total_points = result['total_points']
        
        # Tier thresholds
        new_tier = current_tier
        if total_points >= 10000:
            new_tier = 'platinum'
        elif total_points >= 5000:
            new_tier = 'gold'
        elif total_points >= 2000:
            new_tier = 'silver'
        else:
            new_tier = 'bronze'
        
        if new_tier != current_tier:
            cursor.execute("UPDATE users SET tier = ? WHERE id = ?", (new_tier, user_id))
            conn.commit()
            return new_tier
        
        return None
        
    except Exception as e:
        logger.error(f"Error updating user tier: {e}")
        return None
    finally:
        conn.close()

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "🎮 Goodwill Gym Platform API v3.0",
        "status": "✅ Enhanced with SQLite & Google ADK!",
        "features": [
            "Pokemon Go-style Gym System",
            "Missing Items Gamification", 
            "Google ADK Notifications",
            "SQLite Database",
            "Real-time Gym Leaders",
            "Interactive Maps"
        ]
    }

@app.get("/health")
async def health_check():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get database stats
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM storages")
    storage_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM donations")
    donation_count = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "database": {
            "users": user_count,
            "storages": storage_count,
            "donations": donation_count
        },
        "services": {
            "api": "✅ online",
            "database": "✅ connected",
            "notifications": "✅ active",
            "gym_system": "✅ ready"
        }
    }

@app.post("/users", response_model=Dict)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (username, email, full_name)
            VALUES (?, ?, ?)
        """, (user_data.username, user_data.email, user_data.full_name))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # Generate welcome notification
        notification = notify_achievement(
            "First Steps", 
            user_data.username,
            achievement_type="first_donation"
        )
        
        return {
            "user_id": user_id,
            "username": user_data.username,
            "message": "User created successfully!",
            "notification": notification
        }
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")
    finally:
        conn.close()

@app.get("/users", response_model=List[Dict])
async def get_users():
    """Get all users"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, email, full_name, tier, total_points, 
                   total_donations, streak_days, achievements
            FROM users
            WHERE is_active = 1
            ORDER BY total_points DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            achievements = json.loads(row['achievements']) if row['achievements'] else []
            users.append({
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'full_name': row['full_name'],
                'tier': row['tier'],
                'total_points': row['total_points'],
                'total_donations': row['total_donations'],
                'streak_days': row['streak_days'],
                'achievements': achievements
            })
        
        return users
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")
    finally:
        conn.close()

@app.get("/users/{user_id}", response_model=Dict)
async def get_user(user_id: int):
    """Get specific user by ID"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, email, full_name, tier, total_points, 
                   total_donations, streak_days, achievements, last_donation_date
            FROM users
            WHERE id = ? AND is_active = 1
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        achievements = json.loads(result['achievements']) if result['achievements'] else []
        
        return {
            'id': result['id'],
            'username': result['username'],
            'email': result['email'],
            'full_name': result['full_name'],
            'tier': result['tier'],
            'total_points': result['total_points'],
            'total_donations': result['total_donations'],
            'streak_days': result['streak_days'],
            'achievements': achievements,
            'last_donation_date': result['last_donation_date']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")
    finally:
        conn.close()

@app.get("/storages", response_model=List[Dict])
async def get_storages():
    """Get all storage locations with gym leader info"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT s.id, s.name, s.address, s.latitude, s.longitude,
                   s.gym_leader_id, s.gym_leader_points, s.current_items,
                   u.username as gym_leader_username
            FROM storages s
            LEFT JOIN users u ON s.gym_leader_id = u.id
            ORDER BY s.name
        """)
        
        storages = []
        for row in cursor.fetchall():
            storages.append({
                'id': row['id'],
                'name': row['name'],
                'address': row['address'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'gym_leader_id': row['gym_leader_id'],
                'gym_leader_username': row['gym_leader_username'],
                'gym_leader_points': row['gym_leader_points'] or 0,
                'current_items': row['current_items']
            })
        
        return storages
        
    except Exception as e:
        logger.error(f"Error fetching storages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch storages")
    finally:
        conn.close()

@app.post("/donate", response_model=DonationResponse)
async def make_donation(donation: DonationCreate, background_tasks: BackgroundTasks):
    """Process a donation with full gamification"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Validate user and storage
        cursor.execute("SELECT * FROM users WHERE id = ?", (donation.user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        cursor.execute("SELECT * FROM storages WHERE id = ?", (donation.storage_id,))
        storage = cursor.fetchone()
        if not storage:
            raise HTTPException(status_code=404, detail="Storage not found")
        
        # Check if this is a missing item
        missing_items = get_missing_items(donation.storage_id)
        is_missing_item = any(
            item['item_name'] == donation.item_name 
            for item in missing_items
        )
        
        # Calculate points
        points_data = calculate_points(
            donation.item_name, 
            donation.quantity, 
            is_missing_item
        )
        
        # Insert donation record
        cursor.execute("""
            INSERT INTO donations 
            (user_id, storage_id, item_name, quantity, points_awarded, bonus_points, missing_item_bonus)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            donation.user_id,
            donation.storage_id, 
            donation.item_name,
            donation.quantity,
            points_data['total_points'],
            points_data['bonus_points'],
            is_missing_item
        ))
        
        donation_id = cursor.lastrowid
        
        # Update user points and stats
        new_total_points = user['total_points'] + points_data['total_points']
        new_total_donations = user['total_donations'] + 1
        
        # Update streak logic
        today = date.today()
        last_donation = user['last_donation_date']
        
        if last_donation:
            last_date = datetime.strptime(last_donation, "%Y-%m-%d").date()
            if (today - last_date).days == 1:
                new_streak = user['streak_days'] + 1
            elif (today - last_date).days == 0:
                new_streak = user['streak_days']  # Same day
            else:
                new_streak = 1  # Reset streak
        else:
            new_streak = 1
        
        cursor.execute("""
            UPDATE users 
            SET total_points = ?, total_donations = ?, streak_days = ?, last_donation_date = ?
            WHERE id = ?
        """, (new_total_points, new_total_donations, new_streak, today, donation.user_id))
        
        # Update inventory
        cursor.execute("""
            UPDATE storage_inventory 
            SET current_quantity = current_quantity + ?, last_updated = CURRENT_TIMESTAMP
            WHERE storage_id = ? AND item_name = ?
        """, (donation.quantity, donation.storage_id, donation.item_name))
        
        # Mark missing item request as fulfilled if applicable
        if is_missing_item:
            cursor.execute("""
                UPDATE missing_items_requests 
                SET fulfilled = 1 
                WHERE storage_id = ? AND item_name = ? AND fulfilled = 0
            """, (donation.storage_id, donation.item_name))
        
        conn.commit()
        
        # Check for tier upgrade
        tier_upgraded = update_user_tier(donation.user_id)
        
        # Generate notification
        notification = notify_donation(
            donation.item_name,
            points_data['total_points'],
            is_high_demand=is_missing_item,
            bonus=points_data['bonus_points']
        )
        
        # Background tasks
        background_tasks.add_task(update_gym_leader, donation.storage_id)
        
        return DonationResponse(
            donation_id=donation_id,
            points_awarded=points_data['total_points'],
            bonus_points=points_data['bonus_points'],
            missing_item_bonus=is_missing_item,
            notification=notification,
            tier_upgraded=tier_upgraded is not None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing donation: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to process donation")
    finally:
        conn.close()

@app.get("/missing-items", response_model=List[Dict])
async def get_missing_items_endpoint(storage_id: Optional[int] = None):
    """Get items that are in high demand"""
    return get_missing_items(storage_id)

@app.get("/leaderboard", response_model=List[Dict])
async def get_leaderboard(limit: int = 10):
    """Get user leaderboard"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT u.id, u.username, u.total_points, u.tier, u.streak_days, u.total_donations
            FROM users u
            WHERE u.is_active = 1
            ORDER BY u.total_points DESC
            LIMIT ?
        """, (limit,))
        
        leaderboard = []
        for i, row in enumerate(cursor.fetchall(), 1):
            leaderboard.append({
                'rank': i,
                'user_id': row['id'],
                'username': row['username'],
                'total_points': row['total_points'],
                'tier': row['tier'],
                'streak_days': row['streak_days'],
                'total_donations': row['total_donations']
            })
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch leaderboard")
    finally:
        conn.close()

@app.get("/stats", response_model=Dict)
async def get_platform_stats():
    """Get comprehensive platform statistics"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Basic stats
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
        total_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM donations")
        total_donations = cursor.fetchone()['count']
        
        cursor.execute("SELECT SUM(points_awarded) as total FROM donations")
        total_points = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT COUNT(*) as count FROM storages")
        total_storages = cursor.fetchone()['count']
        
        # Missing items count
        missing_items = get_missing_items()
        critical_needs = len(missing_items)
        
        # Tier distribution
        cursor.execute("""
            SELECT tier, COUNT(*) as count
            FROM users
            WHERE is_active = 1
            GROUP BY tier
        """)
        
        tier_distribution = {}
        for row in cursor.fetchall():
            tier_distribution[row['tier']] = row['count']
        
        return {
            "total_users": total_users,
            "total_donations": total_donations,
            "total_points": total_points,
            "total_storages": total_storages,
            "critical_needs": critical_needs,
            "tier_distribution": tier_distribution,
            "platform_health": "excellent" if critical_needs < 10 else "good"
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")
    finally:
        conn.close()

@app.get("/notifications/missing-items", response_model=List[Dict])
async def get_missing_items_notifications():
    """Get notification messages for missing items"""
    missing_items = get_missing_items()
    return notification_agent.get_encouragement_for_missing_items(missing_items)

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Goodwill Gym Platform API v3.0...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")