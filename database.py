"""
SQLite Database Module for Goodwill Gaming Platform
Handles Users, Storages, Donations, and Item Inventory Management
"""

import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "goodwill_gym.db"

class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    full_name TEXT,
                    tier TEXT DEFAULT 'bronze',
                    total_points INTEGER DEFAULT 0,
                    total_donations INTEGER DEFAULT 0,
                    total_amount REAL DEFAULT 0.0,
                    streak_days INTEGER DEFAULT 0,
                    last_donation_date DATE,
                    achievements TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Storage locations (Gyms) table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS storages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    gym_leader_id INTEGER,
                    gym_leader_points INTEGER DEFAULT 0,
                    capacity INTEGER DEFAULT 1000,
                    current_items INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (gym_leader_id) REFERENCES users (id)
                )
            """)
            
            # Available items catalog
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS item_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    base_points INTEGER DEFAULT 10,
                    demand_multiplier REAL DEFAULT 1.0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Storage inventory (what's available at each storage)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS storage_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    storage_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    current_quantity INTEGER DEFAULT 0,
                    min_threshold INTEGER DEFAULT 5,
                    max_capacity INTEGER DEFAULT 100,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (storage_id) REFERENCES storages (id),
                    UNIQUE(storage_id, item_name)
                )
            """)
            
            # Donations log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS donations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    storage_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    points_awarded INTEGER NOT NULL,
                    bonus_points INTEGER DEFAULT 0,
                    missing_item_bonus BOOLEAN DEFAULT 0,
                    donation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (storage_id) REFERENCES storages (id)
                )
            """)
            
            # Missing items requests (what charities need most)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS missing_items_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    storage_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    urgency_level INTEGER DEFAULT 1,
                    requested_quantity INTEGER NOT NULL,
                    bonus_points INTEGER DEFAULT 50,
                    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fulfilled BOOLEAN DEFAULT 0,
                    FOREIGN KEY (storage_id) REFERENCES storages (id)
                )
            """)
            
            conn.commit()
            self._seed_initial_data()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _seed_initial_data(self):
        """Seed database with initial data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM storages")
            if cursor.fetchone()[0] > 0:
                return  # Data already seeded
            
            # Seed storage locations (Pokemon Go style gyms) - Miami locations
            storages = [
                ("South Beach Donation Hub", "123 Ocean Dr, South Beach", 25.7617, -80.1918),
                ("Wynwood Warehouse", "456 NW 2nd Ave, Wynwood", 25.8010, -80.1998),
                ("Coral Gables Vault", "789 Miracle Mile, Coral Gables", 25.7463, -80.2551),
                ("Brickell Bay Boutique", "321 Brickell Ave, Brickell", 25.7617, -80.1918),
                ("Little Havana Helper Hub", "654 SW 8th St, Little Havana", 25.7663, -80.2201),
                ("Coconut Grove Pantry", "987 Main Hwy, Coconut Grove", 25.7282, -80.2436)
            ]
            
            cursor.executemany("""
                INSERT INTO storages (name, address, latitude, longitude) 
                VALUES (?, ?, ?, ?)
            """, storages)
            
            # Seed item catalog
            items = [
                ("Winter Coats", "Clothing", 25, 2.0, "Warm winter coats for cold weather"),
                ("Canned Goods", "Food", 10, 1.5, "Non-perishable canned food items"),
                ("Children's Books", "Education", 15, 1.8, "Educational books for children"),
                ("Blankets", "Household", 20, 2.2, "Warm blankets for shelter"),
                ("Toys", "Recreation", 12, 1.3, "Toys for children in need"),
                ("Baby Formula", "Baby Care", 30, 3.0, "Essential baby nutrition"),
                ("Hygiene Kits", "Personal Care", 18, 1.9, "Soap, toothbrush, shampoo kits"),
                ("School Supplies", "Education", 14, 1.6, "Notebooks, pencils, backpacks"),
                ("Warm Socks", "Clothing", 8, 1.4, "Warm socks for winter"),
                ("First Aid Supplies", "Medical", 25, 2.5, "Basic medical supplies")
            ]
            
            cursor.executemany("""
                INSERT INTO item_catalog (item_name, category, base_points, demand_multiplier, description) 
                VALUES (?, ?, ?, ?, ?)
            """, items)
            
            # Seed storage inventory for each location
            storage_ids = [1, 2, 3, 4, 5, 6]  # Assuming 6 storages
            item_names = [item[0] for item in items]
            
            for storage_id in storage_ids:
                for item_name in item_names:
                    # Random initial quantities and thresholds
                    import random
                    current_qty = random.randint(0, 50)
                    min_threshold = random.randint(3, 8)
                    max_capacity = random.randint(80, 120)
                    
                    cursor.execute("""
                        INSERT INTO storage_inventory (storage_id, item_name, current_quantity, min_threshold, max_capacity)
                        VALUES (?, ?, ?, ?, ?)
                    """, (storage_id, item_name, current_qty, min_threshold, max_capacity))
            
            # Create some missing item requests for high-demand items
            missing_requests = [
                (1, "Winter Coats", 3, 20, 100),  # Urgent need for winter coats
                (2, "Baby Formula", 3, 15, 150),
                (3, "Blankets", 2, 25, 75),
                (4, "First Aid Supplies", 3, 10, 200),
                (5, "Hygiene Kits", 2, 30, 80),
                (6, "Children's Books", 1, 40, 60)
            ]
            
            cursor.executemany("""
                INSERT INTO missing_items_requests (storage_id, item_name, urgency_level, requested_quantity, bonus_points)
                VALUES (?, ?, ?, ?, ?)
            """, missing_requests)
            
            # Create demo users
            demo_users = [
                ("alice_demo", "alice@demo.com", "Alice Demo"),
                ("bob_demo", "bob@demo.com", "Bob Demo"),
                ("charlie_demo", "charlie@demo.com", "Charlie Demo"),
                ("diana_demo", "diana@demo.com", "Diana Demo")
            ]
            
            cursor.executemany("""
                INSERT INTO users (username, email, full_name)
                VALUES (?, ?, ?)
            """, demo_users)
            
            conn.commit()
            logger.info("Initial data seeded successfully")
            
        except Exception as e:
            logger.error(f"Data seeding error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_missing_items(self, storage_id: int = None) -> List[Dict]:
        """Get items that are in high demand or low supply"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if storage_id:
            # Get missing items for specific storage
            cursor.execute("""
                SELECT 
                    si.storage_id,
                    si.item_name,
                    si.current_quantity,
                    si.min_threshold,
                    ic.base_points,
                    ic.demand_multiplier,
                    mir.bonus_points,
                    mir.urgency_level,
                    s.name as storage_name
                FROM storage_inventory si
                JOIN item_catalog ic ON si.item_name = ic.item_name
                JOIN storages s ON si.storage_id = s.id
                LEFT JOIN missing_items_requests mir ON si.storage_id = mir.storage_id 
                    AND si.item_name = mir.item_name AND mir.fulfilled = 0
                WHERE si.storage_id = ? AND si.current_quantity <= si.min_threshold
                ORDER BY mir.urgency_level DESC, si.current_quantity ASC
            """, (storage_id,))
        else:
            # Get all missing items across all storages
            cursor.execute("""
                SELECT 
                    si.storage_id,
                    si.item_name,
                    si.current_quantity,
                    si.min_threshold,
                    ic.base_points,
                    ic.demand_multiplier,
                    mir.bonus_points,
                    mir.urgency_level,
                    s.name as storage_name
                FROM storage_inventory si
                JOIN item_catalog ic ON si.item_name = ic.item_name
                JOIN storages s ON si.storage_id = s.id
                LEFT JOIN missing_items_requests mir ON si.storage_id = mir.storage_id 
                    AND si.item_name = mir.item_name AND mir.fulfilled = 0
                WHERE si.current_quantity <= si.min_threshold
                ORDER BY mir.urgency_level DESC, si.current_quantity ASC
            """)
        
        results = cursor.fetchall()
        conn.close()
        
        missing_items = []
        for row in results:
            missing_items.append({
                'storage_id': row['storage_id'],
                'storage_name': row['storage_name'],
                'item_name': row['item_name'],
                'current_quantity': row['current_quantity'],
                'min_threshold': row['min_threshold'],
                'shortage': row['min_threshold'] - row['current_quantity'],
                'base_points': row['base_points'],
                'demand_multiplier': row['demand_multiplier'] or 1.0,
                'bonus_points': row['bonus_points'] or 0,
                'urgency_level': row['urgency_level'] or 1
            })
        
        return missing_items
    
    def update_gym_leader(self, storage_id: int):
        """Update gym leader based on highest points at this storage"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Debug: Check if we have donations for this storage
            cursor.execute("SELECT COUNT(*) as count FROM donations WHERE storage_id = ?", (storage_id,))
            donation_count = cursor.fetchone()['count']
            print(f"DEBUG: Found {donation_count} donations for storage {storage_id}")
            
            # Find user with most points from donations at this storage
            cursor.execute("""
                SELECT 
                    d.user_id,
                    u.username,
                    SUM(d.points_awarded) as total_points
                FROM donations d
                JOIN users u ON d.user_id = u.id
                WHERE d.storage_id = ?
                GROUP BY d.user_id, u.username
                ORDER BY total_points DESC
                LIMIT 1
            """, (storage_id,))
            
            result = cursor.fetchone()
            if result:
                print(f"DEBUG: New leader should be {result['username']} with {result['total_points']} points")
                
                cursor.execute("""
                    UPDATE storages 
                    SET gym_leader_id = ?, gym_leader_points = ?
                    WHERE id = ?
                """, (result['user_id'], result['total_points'], storage_id))
                
                conn.commit()
                print(f"DEBUG: Updated gym leader for storage {storage_id}: {result['username']} with {result['total_points']} points")
                logger.info(f"Updated gym leader for storage {storage_id}: {result['username']} with {result['total_points']} points")
                return result
            else:
                print(f"DEBUG: No donations found for storage {storage_id}")
        
        except Exception as e:
            print(f"DEBUG: Error updating gym leader: {e}")
            logger.error(f"Error updating gym leader: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        return None

# Initialize database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_missing_items(storage_id: int = None):
    return db_manager.get_missing_items(storage_id)

def update_gym_leader(storage_id: int):
    return db_manager.update_gym_leader(storage_id)

if __name__ == "__main__":
    # Initialize database when run directly
    db_manager = DatabaseManager()
    print("✅ Database initialized successfully!")
    
    # Show some stats
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM storages")
    storage_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM item_catalog")
    item_count = cursor.fetchone()[0]
    
    print(f"📊 Database Stats:")
    print(f"   Users: {user_count}")
    print(f"   Storage Locations: {storage_count}")
    print(f"   Item Types: {item_count}")
    
    # Show missing items
    missing = get_missing_items()
    print(f"   Missing Items: {len(missing)}")
    
    conn.close()