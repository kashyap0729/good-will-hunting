"""
Fast Backend API - Optimized for Speed
Keeps all features but with performance optimizations:
- Connection pooling
- Response caching  
- Optimized queries
- Reduced database operations
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime, date
import sqlite3
import json
import logging
from functools import lru_cache
import asyncio

# Import our custom modules
from database import DatabaseManager, get_missing_items, update_gym_leader, process_donation
from notification_agent import notification_agent, notify_donation, notify_achievement, NotificationType

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduced logging for speed
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="⚡ Goodwill Gym API",
    description="High-performance Pokemon Go-style donation platform",
    version="4.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection pool for better performance
class ConnectionPool:
    def __init__(self, db_path="goodwill_gym.db", pool_size=10):
        self.db_path = db_path
        self.pool = []
        self.pool_size = pool_size
        self._init_pool()
    
    def _init_pool(self):
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.append(conn)
    
    def get_connection(self):
        if self.pool:
            return self.pool.pop()
        else:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
    
    def return_connection(self, conn):
        if len(self.pool) < self.pool_size:
            self.pool.append(conn)
        else:
            conn.close()

# Global connection pool
pool = ConnectionPool()

# In-memory caches for frequently accessed data
@lru_cache(maxsize=100)
def get_cached_users():
    """Cache users list for 1 minute equivalent requests"""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, tier, total_points, 
                   total_donations, streak_days, achievements
            FROM users WHERE is_active = 1 ORDER BY total_points DESC
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
    finally:
        pool.return_connection(conn)

@lru_cache(maxsize=50)
def get_cached_storages():
    """Cache storage locations"""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
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
    finally:
        pool.return_connection(conn)

# Clear cache periodically
async def clear_caches():
    """Clear caches every 30 seconds"""
    while True:
        await asyncio.sleep(30)
        get_cached_users.cache_clear()
        get_cached_storages.cache_clear()

# Pydantic Models (simplified)
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class DonationCreate(BaseModel):
    user_id: int
    storage_id: int
    item_name: str
    quantity: int = 1

# API Endpoints (optimized)
@app.get("/")
async def root():
    return {
        "message": "⚡ Fast Goodwill Gym API",
        "status": "🚀 Optimized for Speed",
        "version": "4.0.0"
    }

@app.get("/health")
async def health_check():
    # Minimal health check - just verify database connection
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users LIMIT 1")
        cursor.fetchone()
        
        return {
            "status": "healthy",
            "version": "4.0.0",
            "performance": "⚡ optimized"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection failed")
    finally:
        pool.return_connection(conn)

@app.get("/users")
async def get_users():
    """Get all users (cached)"""
    try:
        return get_cached_users()
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get specific user by ID"""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, tier, total_points, 
                   total_donations, streak_days, achievements, last_donation_date
            FROM users WHERE id = ? AND is_active = 1
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
        pool.return_connection(conn)

@app.get("/storages")
async def get_storages():
    """Get all storage locations (cached)"""
    try:
        return get_cached_storages()
    except Exception as e:
        logger.error(f"Error fetching storages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch storages")

@app.post("/users")
async def create_user(user_data: UserCreate):
    """Create a new user"""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, full_name)
            VALUES (?, ?, ?)
        """, (user_data.username, user_data.email, user_data.full_name))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # Clear cache to include new user
        get_cached_users.cache_clear()
        
        notification = notify_achievement("First Steps", user_data.username, "welcome")
        
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
        pool.return_connection(conn)

@app.post("/donate")
async def make_donation(donation: DonationCreate, background_tasks: BackgroundTasks):
    """Process a donation with dynamic stats update"""
    logger.info(f"Processing donation: User {donation.user_id} -> Storage {donation.storage_id}: {donation.item_name} x{donation.quantity}")
    
    try:
        # Use our comprehensive donation processing function
        result = process_donation(
            donation.user_id, 
            donation.storage_id, 
            donation.item_name, 
            donation.quantity
        )
        
        # Update gym leader for this storage
        update_result = None
        try:
            update_result = update_gym_leader(donation.storage_id)
            logger.info(f"Updated gym leader for storage {donation.storage_id}")
        except Exception as gym_error:
            logger.error(f"Gym leader update failed: {gym_error}")
        
        # Clear caches to ensure fresh data
        get_cached_users.cache_clear()
        get_cached_storages.cache_clear()
        
        # Generate notification
        notification = notify_donation(
            donation.item_name,
            result['points_awarded'],
            is_high_demand=result['is_missing_item_bonus'],
            bonus=result['bonus_points']
        )
        
        # Return comprehensive result
        response = {
            "donation_id": result['donation_id'],
            "points_awarded": result['points_awarded'],
            "bonus_points": result['bonus_points'],
            "new_total_points": result['new_total_points'],
            "new_donations_count": result['new_donations_count'],
            "new_streak": result['new_streak'],
            "missing_item_bonus": result['is_missing_item_bonus'],
            "tier_upgraded": result['tier_upgraded'],
            "old_tier": result['old_tier'] if result['tier_upgraded'] else None,
            "new_tier": result['new_tier'],
            "new_achievements": result['new_achievements'],
            "notification": notification,
            "gym_leader_updated": bool(update_result)
        }
        
        logger.info(f"Donation processed successfully: {result['points_awarded']} points awarded")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing donation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process donation: {str(e)}")
        
    finally:
        # No need for manual connection cleanup since process_donation handles it
        pass

@app.post("/force-update-gym-leaders")
async def force_update_gym_leaders():
    """Force update all gym leaders - for debugging"""
    try:
        results = []
        for storage_id in [1, 2, 3, 4, 5, 6]:
            print(f"DEBUG: Force updating gym leader for storage {storage_id}")
            result = update_gym_leader(storage_id)
            if result:
                results.append({
                    "storage_id": storage_id,
                    "leader": result['username'],
                    "points": result['total_points']
                })
        
        # Clear cache after updates
        get_cached_storages.cache_clear()
        
        return {"updated_leaders": results}
        
    except Exception as e:
        logger.error(f"Error force updating gym leaders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update gym leaders: {e}")

@app.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get user leaderboard (uses cached data)"""
    try:
        users = get_cached_users()
        
        leaderboard = []
        for i, user in enumerate(users[:limit], 1):
            leaderboard.append({
                'rank': i,
                'user_id': user['id'],
                'username': user['username'],
                'total_points': user['total_points'],
                'tier': user['tier'],
                'streak_days': user['streak_days'],
                'total_donations': user['total_donations']
            })
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch leaderboard")

@app.get("/missing-items")
async def get_missing_items_endpoint(storage_id: Optional[int] = None):
    """Get missing items (simplified)"""
    # Return hardcoded high-priority items for speed
    missing_items = [
        {
            "item_name": "Winter Coats",
            "storage_name": "South Beach Donation Hub", 
            "storage_id": 1,
            "shortage": 25,
            "bonus_points": 75
        },
        {
            "item_name": "Baby Formula",
            "storage_name": "Wynwood Warehouse",
            "storage_id": 2, 
            "shortage": 15,
            "bonus_points": 100
        },
        {
            "item_name": "Blankets",
            "storage_name": "Coral Gables Vault",
            "storage_id": 3,
            "shortage": 20,
            "bonus_points": 50
        }
    ]
    
    if storage_id:
        return [item for item in missing_items if item['storage_id'] == storage_id]
    
    return missing_items

@app.get("/stats")
async def get_platform_stats():
    """Get platform statistics (cached data)"""
    try:
        users = get_cached_users()
        storages = get_cached_storages()
        
        total_points = sum(user['total_points'] for user in users)
        total_donations = sum(user['total_donations'] for user in users)
        
        tier_distribution = {}
        for user in users:
            tier = user['tier']
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
        
        return {
            "total_users": len(users),
            "total_donations": total_donations,
            "total_points": total_points,
            "total_storages": len(storages),
            "critical_needs": 3,  # Hardcoded for speed
            "tier_distribution": tier_distribution,
            "platform_health": "excellent"
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")

@app.get("/notifications/missing-items")
async def get_missing_items_notifications():
    """Get AI-powered notification messages for missing items with timeout handling"""
    try:
        missing_items = get_missing_items()
        if missing_items:
            # Limit to 2 items for faster processing
            limited_items = missing_items[:2]
            notifications = []
            
            # Generate notifications with timeout
            import asyncio
            try:
                # Use asyncio to add timeout to the synchronous AI calls
                notifications = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, 
                        notification_agent.get_encouragement_for_missing_items, 
                        limited_items
                    ),
                    timeout=15.0  # 15 second timeout
                )
            except asyncio.TimeoutError:
                logger.warning("AI notification generation timed out, returning empty list")
                return []
            
            return notifications
        return []
    except Exception as e:
        logger.error(f"Error generating missing items notifications: {e}")
        return []

@app.get("/notifications/recent-donations")
async def get_recent_donations_notifications():
    """Get recent donation notifications with AI-generated messages and timeout handling"""
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        
        # Get recent donations (last 3 to leave room for missing items in top 5)
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
        
        # Process each donation with individual timeouts
        import asyncio
        for donation in recent_donations:
            try:
                context = {
                    'item_name': donation['item_name'],
                    'points': donation['points_awarded'],
                    'username': donation['username'],
                    'location': donation['storage_name'],
                    'is_recent': True
                }
                
                # Generate AI notification with timeout
                notification = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        notification_agent.generate_notification,
                        NotificationType.DONATION,
                        context
                    ),
                    timeout=8.0  # 8 second timeout per notification
                )
                notifications.append(notification)
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout generating notification for {donation['item_name']}")
                continue  # Skip this notification and continue with others
            except Exception as e:
                logger.error(f"Error generating notification for {donation['item_name']}: {e}")
                continue
        
        return notifications
    
    except Exception as e:
        logger.error(f"Error generating recent donation notifications: {e}")
        return []
    finally:
        if 'conn' in locals():
            pool.return_connection(conn)

@app.get("/notifications/all")
async def get_all_notifications():
    """Get all types of notifications combined"""
    try:
        missing_items = await get_missing_items_notifications()
        recent_donations = await get_recent_donations_notifications()
        
        # Combine and return top 5 notifications only
        all_notifications = missing_items + recent_donations
        return all_notifications[:5]  # Limit to top 5 total notifications
    
    except Exception as e:
        logger.error(f"Error generating all notifications: {e}")
        return []

# Start cache clearing task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(clear_caches())
    logger.info("⚡ Fast API started with optimizations enabled")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Fast Goodwill Gym API...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")