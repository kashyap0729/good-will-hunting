"""
FastAPI Donation Service
Core microservice for handling donations with A2A agent integration
"""

from fastapi import FastAPI, WebSocket, Depends, HTTPException, Header, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore
from typing import Dict, List, Optional, Any
import asyncio
from contextlib import asynccontextmanager
import json
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
from enum import Enum

# Import our A2A client
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'agents'))
from a2a_protocol import A2AClient

logger = logging.getLogger(__name__)

# Pydantic models
class DonationType(str, Enum):
    MONETARY = "monetary"
    ITEMS = "items"
    VOLUNTEER_TIME = "volunteer_time"

class DonationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

class DonationItem(BaseModel):
    type: str = Field(..., description="Type of item (clothing, food, books, etc.)")
    quantity: int = Field(..., gt=0, description="Quantity of items")
    condition: str = Field(default="good", description="Condition of items")
    estimated_value: float = Field(default=0.0, ge=0, description="Estimated monetary value")
    description: Optional[str] = None

class DonationRequest(BaseModel):
    amount: Optional[float] = Field(None, ge=0, description="Monetary donation amount")
    donation_type: DonationType
    items: Optional[List[DonationItem]] = None
    location: Optional[Location] = None
    charity_id: str = Field(..., description="Target charity ID")
    message: Optional[str] = Field(None, max_length=500, description="Optional message")
    recurring: bool = Field(default=False, description="Is this a recurring donation")
    recurring_frequency: Optional[str] = Field(None, description="Frequency for recurring donations")

class User(BaseModel):
    uid: str
    email: str
    name: str
    tier: str = "Bronze"
    total_points: int = 0
    total_donations: int = 0
    location: Optional[Location] = None

class PointsCalculationEngine:
    """Advanced points calculation with multiple factors"""
    
    TIER_MULTIPLIERS = {
        'Bronze': 1.0, 'Silver': 1.1, 'Gold': 1.2,
        'Platinum': 1.3, 'Diamond': 1.5
    }
    
    DONATION_TYPE_MULTIPLIERS = {
        DonationType.MONETARY: 1.0,
        DonationType.ITEMS: 1.2,
        DonationType.VOLUNTEER_TIME: 1.5
    }
    
    def __init__(self):
        self.seasonal_events = self._initialize_seasonal_events()
    
    def _initialize_seasonal_events(self) -> Dict[str, Dict]:
        """Initialize seasonal bonus events"""
        return {
            "holiday_season": {
                "start": "12-01",
                "end": "01-15", 
                "multiplier": 2.0
            },
            "back_to_school": {
                "start": "08-15",
                "end": "09-15",
                "multiplier": 1.5
            },
            "thanksgiving": {
                "start": "11-15", 
                "end": "11-30",
                "multiplier": 1.8
            }
        }
    
    def calculate_points(self, donation: DonationRequest, user_profile: Dict, context: Dict) -> Dict:
        """Calculate points for a donation with comprehensive factors"""
        
        # Base points calculation
        if donation.donation_type == DonationType.MONETARY:
            base_points = int((donation.amount or 0) * 1.5)
        elif donation.donation_type == DonationType.ITEMS:
            item_values = sum(item.estimated_value for item in (donation.items or []))
            base_points = int(item_values * 1.5) + len(donation.items or []) * 10
        else:  # VOLUNTEER_TIME
            base_points = 100  # Base points for volunteer time
        
        # Apply tier multiplier
        tier = user_profile.get('tier', 'Bronze')
        tier_multiplier = self.TIER_MULTIPLIERS.get(tier, 1.0)
        
        # Apply donation type multiplier
        type_multiplier = self.DONATION_TYPE_MULTIPLIERS.get(donation.donation_type, 1.0)
        
        # Apply bonuses
        first_time_bonus = 3.0 if context.get('first_donation') else 1.0
        recurring_bonus = 2.0 if donation.recurring else 1.0
        location_bonus = 1.2 if donation.location else 1.0
        seasonal_bonus = self._get_seasonal_bonus()
        
        # Calculate final points
        total_multiplier = (tier_multiplier * type_multiplier * first_time_bonus * 
                          recurring_bonus * location_bonus * seasonal_bonus)
        final_points = int(base_points * total_multiplier)
        
        # Check for tier progression
        current_points = user_profile.get('total_points', 0)
        new_total = current_points + final_points
        new_tier = self._calculate_tier_progression(new_total)
        
        return {
            'points_awarded': final_points,
            'breakdown': {
                'base': base_points,
                'tier_multiplier': tier_multiplier,
                'type_multiplier': type_multiplier,
                'first_time_bonus': first_time_bonus > 1,
                'recurring_bonus': recurring_bonus > 1,
                'location_bonus': location_bonus > 1,
                'seasonal_bonus': seasonal_bonus
            },
            'new_tier': new_tier if new_tier != tier else None,
            'total_points': new_total,
            'tier_progression': new_tier != tier
        }
    
    def _get_seasonal_bonus(self) -> float:
        """Calculate current seasonal bonus multiplier"""
        current_date = datetime.now()
        current_month_day = f"{current_date.month:02d}-{current_date.day:02d}"
        
        for event_name, event_data in self.seasonal_events.items():
            start = event_data["start"]
            end = event_data["end"]
            
            # Handle year-end rollover (e.g., holiday season)
            if start > end:  # crosses year boundary
                if current_month_day >= start or current_month_day <= end:
                    return event_data["multiplier"]
            else:
                if start <= current_month_day <= end:
                    return event_data["multiplier"]
        
        return 1.0  # No seasonal bonus
    
    def _calculate_tier_progression(self, total_points: int) -> str:
        """Calculate tier based on total points"""
        tier_thresholds = {
            "Bronze": 0,
            "Silver": 1000,
            "Gold": 5000,
            "Platinum": 15000,
            "Diamond": 50000
        }
        
        for tier, threshold in sorted(tier_thresholds.items(), key=lambda x: x[1], reverse=True):
            if total_points >= threshold:
                return tier
        return "Bronze"

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
        
    async def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
    async def broadcast_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id][:]:  # Copy list to avoid modification during iteration
                try:
                    await connection.send_json(message)
                except:
                    await self.disconnect(connection, user_id)
    
    async def broadcast_to_all(self, message: dict):
        for user_id in list(self.active_connections.keys()):
            await self.broadcast_to_user(user_id, message)

# Event processor for Pub/Sub integration
class EventDrivenDonationProcessor:
    def __init__(self, project_id: str):
        self.project_id = project_id
        # In production, would initialize Pub/Sub clients
        
    async def process_donation_event(self, donation_data: Dict):
        """Process donation through event-driven pipeline"""
        
        # Step 1: Publish to donation-created topic (simulated)
        await self._publish_event('donation-created', donation_data)
        
        # Step 2: Trigger parallel processing
        await asyncio.gather(
            self.trigger_points_calculation(donation_data),
            self.trigger_agent_processing(donation_data),
            self.trigger_analytics_update(donation_data),
            self.trigger_notification(donation_data)
        )
    
    async def _publish_event(self, topic: str, data: Dict):
        """Publish event to Pub/Sub topic (simulated)"""
        logger.info(f"Publishing to {topic}: {data.get('donation_id', 'unknown')}")
    
    async def trigger_points_calculation(self, donation_data: Dict):
        """Trigger points calculation"""
        logger.info(f"Triggering points calculation for donation {donation_data.get('id')}")
    
    async def trigger_agent_processing(self, donation_data: Dict):
        """Send donation to A2A agents for processing"""
        logger.info(f"Triggering A2A agent processing for donation {donation_data.get('id')}")
    
    async def trigger_analytics_update(self, donation_data: Dict):
        """Update analytics"""
        logger.info(f"Updating analytics for donation {donation_data.get('id')}")
    
    async def trigger_notification(self, donation_data: Dict):
        """Send notifications"""
        logger.info(f"Sending notifications for donation {donation_data.get('id')}")

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db = firestore.AsyncClient()
    app.state.connection_manager = ConnectionManager()
    app.state.points_engine = PointsCalculationEngine()
    app.state.a2a_donor_client = A2AClient("https://dea.donationplatform.com")
    app.state.a2a_charity_client = A2AClient("https://coa.donationplatform.com")
    app.state.event_processor = EventDrivenDonationProcessor("donation-platform")
    
    logger.info("Donation service startup complete")
    yield
    
    # Cleanup
    await app.state.connection_manager.disconnect
    logger.info("Donation service shutdown complete")

# FastAPI app initialization
app = FastAPI(
    title="Gamified Donation Platform API",
    description="Core donation processing service with A2A agent integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency functions
async def get_db():
    return app.state.db

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user"""
    # Simplified authentication - in production, verify JWT token
    return User(
        uid="user_12345",
        email="user@example.com", 
        name="John Doe",
        tier="Gold",
        total_points=2450,
        total_donations=25
    )

async def get_user_profile(user_id: str, db: firestore.AsyncClient) -> Dict:
    """Get user profile from Firestore"""
    try:
        doc_ref = db.collection('users').document(user_id)
        doc = await doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            # Create default profile
            default_profile = {
                'user_id': user_id,
                'total_points': 0,
                'total_donations': 0,
                'tier': 'Bronze',
                'created_at': firestore.SERVER_TIMESTAMP
            }
            await doc_ref.set(default_profile)
            return default_profile
            
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return {
            'user_id': user_id,
            'total_points': 0,
            'total_donations': 0,
            'tier': 'Bronze'
        }

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "donation-service"
    }

@app.post("/api/v1/donations")
async def create_donation(
    donation_request: DonationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: firestore.AsyncClient = Depends(get_db)
):
    """Create donation with A2A agent processing"""
    
    try:
        # Generate donation ID
        donation_id = str(uuid.uuid4())
        
        # Create donation record
        donation_data = {
            'id': donation_id,
            'user_id': current_user.uid,
            'amount': donation_request.amount,
            'donation_type': donation_request.donation_type,
            'items': [item.dict() for item in (donation_request.items or [])],
            'location': donation_request.location.dict() if donation_request.location else None,
            'charity_id': donation_request.charity_id,
            'message': donation_request.message,
            'recurring': donation_request.recurring,
            'status': DonationStatus.PROCESSING,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        # Save to Firestore
        doc_ref = db.collection('donations').document(donation_id)
        await doc_ref.set(donation_data)
        
        # Get user profile for points calculation
        user_profile = await get_user_profile(current_user.uid, db)
        
        # Calculate points
        context = {
            'first_donation': user_profile.get('total_donations', 0) == 0,
            'recurring_donor': user_profile.get('total_donations', 0) > 5
        }
        
        points_result = app.state.points_engine.calculate_points(
            donation_request,
            user_profile,
            context
        )
        
        # Update user profile
        await db.collection('users').document(current_user.uid).update({
            'total_points': points_result['total_points'],
            'total_donations': user_profile.get('total_donations', 0) + 1,
            'tier': points_result.get('new_tier', user_profile.get('tier', 'Bronze')),
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        # Update donation with points info
        await doc_ref.update({
            'points_awarded': points_result['points_awarded'],
            'points_breakdown': points_result['breakdown'],
            'tier_progression': points_result.get('tier_progression', False),
            'status': DonationStatus.COMPLETED,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        # Send real-time notification
        await app.state.connection_manager.broadcast_to_user(
            current_user.uid,
            {
                'type': 'donation_created',
                'donation_id': donation_id,
                'points_awarded': points_result['points_awarded'],
                'new_tier': points_result.get('new_tier'),
                'tier_progression': points_result.get('tier_progression', False)
            }
        )
        
        # Process through A2A agents asynchronously
        background_tasks.add_task(
            process_donation_with_agents,
            donation_data,
            app.state.a2a_donor_client,
            app.state.a2a_charity_client
        )
        
        # Process through event-driven pipeline
        background_tasks.add_task(
            app.state.event_processor.process_donation_event,
            donation_data
        )
        
        return {
            'success': True,
            'donation_id': donation_id,
            'status': DonationStatus.COMPLETED,
            'points': points_result,
            'created_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating donation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating donation: {str(e)}")

@app.get("/api/v1/donations/{donation_id}")
async def get_donation(
    donation_id: str,
    current_user: User = Depends(get_current_user),
    db: firestore.AsyncClient = Depends(get_db)
):
    """Get donation details"""
    
    try:
        doc_ref = db.collection('donations').document(donation_id)
        doc = await doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Donation not found")
        
        donation_data = doc.to_dict()
        
        # Check if user owns this donation
        if donation_data.get('user_id') != current_user.uid:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            'success': True,
            'donation': donation_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting donation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving donation")

@app.get("/api/v1/users/{user_id}/donations")
async def get_user_donations(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: firestore.AsyncClient = Depends(get_db)
):
    """Get user's donation history"""
    
    # Check authorization
    if user_id != current_user.uid:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        query = db.collection('donations').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING)
        
        # Apply pagination
        docs = query.offset(offset).limit(limit).stream()
        
        donations = []
        async for doc in docs:
            donation_data = doc.to_dict()
            donation_data['id'] = doc.id
            donations.append(donation_data)
        
        return {
            'success': True,
            'donations': donations,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'count': len(donations)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting user donations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving donations")

@app.get("/api/v1/analytics/donations/today")
async def get_donations_today(db: firestore.AsyncClient = Depends(get_db)):
    """Get today's donation analytics"""
    
    try:
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        
        # Query donations from today
        query = db.collection('donations').where('created_at', '>=', start_of_day)
        docs = query.stream()
        
        total_amount = 0
        count = 0
        
        async for doc in docs:
            donation = doc.to_dict()
            total_amount += donation.get('amount', 0) or 0
            count += 1
        
        # Calculate change from yesterday (simplified)
        change_percentage = 12.5  # Simulated
        
        return {
            'amount': total_amount,
            'count': count,
            'change': change_percentage,
            'date': today.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting today's donations: {str(e)}")
        return {
            'amount': 0,
            'count': 0,
            'change': 0,
            'date': datetime.now().date().isoformat()
        }

@app.get("/api/v1/analytics/donors/active")
async def get_active_donors(db: firestore.AsyncClient = Depends(get_db)):
    """Get active donor count"""
    
    try:
        # Query active donors in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # This would be a more complex aggregation query in production
        active_count = 1250  # Simulated
        new_today = 15  # Simulated
        
        return {
            'count': active_count,
            'new_today': new_today,
            'period': '30_days'
        }
        
    except Exception as e:
        logger.error(f"Error getting active donors: {str(e)}")
        return {
            'count': 0,
            'new_today': 0,
            'period': '30_days'
        }

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str
):
    """Real-time WebSocket connection for notifications"""
    
    manager = app.state.connection_manager
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
            elif data.startswith("subscribe:"):
                # Handle subscription to specific events
                event_type = data.split(":", 1)[1]
                logger.info(f"User {user_id} subscribed to {event_type}")
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "event_type": event_type
                })
                
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
    finally:
        await manager.disconnect(websocket, user_id)

# Background task for A2A agent processing
async def process_donation_with_agents(donation_data: Dict, donor_client: A2AClient, charity_client: A2AClient):
    """Process donation through A2A agents"""
    
    try:
        # Send to Donor Engagement Agent
        donor_result = await donor_client.ask({
            "skill": "process_donation",
            "params": donation_data
        })
        
        if donor_result.get("success"):
            logger.info(f"DEA processed donation {donation_data['id']} successfully")
        else:
            logger.error(f"DEA failed to process donation {donation_data['id']}: {donor_result.get('error')}")
        
        # Send to Charity Optimization Agent
        charity_result = await charity_client.ask({
            "skill": "optimize_charity_operations", 
            "params": {
                "charity_id": donation_data['charity_id'],
                "donation_data": donation_data
            }
        })
        
        if charity_result.get("success"):
            logger.info(f"COA processed donation {donation_data['id']} successfully")
        else:
            logger.error(f"COA failed to process donation {donation_data['id']}: {charity_result.get('error')}")
            
    except Exception as e:
        logger.error(f"Error processing donation with agents: {str(e)}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )