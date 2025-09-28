from google.adk.agents import Agent
from a2a_sdk import A2AServer, AgentCard, AgentSkill
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PointsCalculation:
    """Result of points calculation with breakdown"""
    base_points: int
    tier_multiplier: float
    seasonal_bonus: float
    proximity_bonus: float
    total_points: int
    breakdown: Dict[str, float]

class PointsEngine:
    """Advanced multi-factor point calculation system"""
    
    def __init__(self):
        self.points_db = {}
        self.activity_multipliers = {
            "donation": 10,
            "volunteer": 5,
            "referral": 3,
            "newsletter_signup": 1,
            "social_share": 2,
            "recurring_setup": 15
        }
        self.tier_multipliers = {
            "Bronze": 1.0,
            "Silver": 1.1, 
            "Gold": 1.2,
            "Platinum": 1.3,
            "Diamond": 1.5
        }
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
    
    def calculate_points(self, user_id: str, activity: str, amount: int, user_tier: str, location: Optional[Dict] = None) -> PointsCalculation:
        """Advanced multi-factor point calculation"""
        
        # Base points calculation
        base_points = amount * self.activity_multipliers.get(activity, 1)
        
        # Tier multiplier bonus
        tier_bonus = self.tier_multipliers.get(user_tier, 1.0)
        
        # Seasonal bonus calculation
        seasonal_bonus = self._get_seasonal_bonus()
        
        # Proximity bonus for local donations
        proximity_bonus = 1.2 if self._check_local_donation(user_id, location) else 1.0
        
        # Streak bonus for consistent donors
        streak_bonus = self._calculate_streak_bonus(user_id)
        
        # Calculate final points
        total_multiplier = tier_bonus * seasonal_bonus * proximity_bonus * streak_bonus
        total_points = int(base_points * total_multiplier)
        
        return PointsCalculation(
            base_points=base_points,
            tier_multiplier=tier_bonus,
            seasonal_bonus=seasonal_bonus,
            proximity_bonus=proximity_bonus,
            total_points=total_points,
            breakdown={
                "base": base_points,
                "tier_bonus": tier_bonus,
                "seasonal_bonus": seasonal_bonus,
                "proximity_bonus": proximity_bonus,
                "streak_bonus": streak_bonus,
                "final_multiplier": total_multiplier
            }
        )
    
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
    
    def _check_local_donation(self, user_id: str, location: Optional[Dict]) -> bool:
        """Check if donation is within local area for proximity bonus"""
        if not location:
            return False
        
        # Implementation would check user's home location vs donation location
        # For demo, return True if within 10km (simplified)
        return True  # Simplified for demo
    
    def _calculate_streak_bonus(self, user_id: str) -> float:
        """Calculate bonus based on donation streak"""
        # Implementation would check user's donation history
        # For demo purposes, return progressive streak bonus
        streak_days = 7  # Would be fetched from database
        
        if streak_days >= 30:
            return 1.5
        elif streak_days >= 14:
            return 1.3
        elif streak_days >= 7:
            return 1.2
        return 1.0

class RankingSystem:
    """Manage user rankings and leaderboards"""
    
    def __init__(self):
        self.rankings = {}
        self.tier_thresholds = {
            "Bronze": 0,
            "Silver": 1000,
            "Gold": 5000,
            "Platinum": 15000,
            "Diamond": 50000
        }
    
    async def update_rank(self, user_id: str, points: int) -> Dict[str, any]:
        """Update user rank and check for tier progression"""
        
        # Get current user data (would be from database)
        current_points = self.rankings.get(user_id, {}).get("total_points", 0)
        new_total = current_points + points
        
        # Check for tier progression
        current_tier = self._get_tier(current_points)
        new_tier = self._get_tier(new_total)
        
        # Update rankings
        self.rankings[user_id] = {
            "total_points": new_total,
            "tier": new_tier,
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "previous_tier": current_tier,
            "new_tier": new_tier,
            "tier_upgraded": new_tier != current_tier,
            "total_points": new_total,
            "points_to_next_tier": self._points_to_next_tier(new_total)
        }
    
    def _get_tier(self, points: int) -> str:
        """Determine tier based on points"""
        for tier, threshold in sorted(self.tier_thresholds.items(), key=lambda x: x[1], reverse=True):
            if points >= threshold:
                return tier
        return "Bronze"
    
    def _points_to_next_tier(self, current_points: int) -> int:
        """Calculate points needed for next tier"""
        current_tier = self._get_tier(current_points)
        tier_order = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]
        
        current_index = tier_order.index(current_tier)
        if current_index == len(tier_order) - 1:  # Already at max tier
            return 0
        
        next_tier = tier_order[current_index + 1]
        return self.tier_thresholds[next_tier] - current_points

class LocationIntelligence:
    """Handle location-based achievements and hotspot detection"""
    
    def __init__(self):
        self.hotspots = {}
        self.user_locations = {}
    
    async def check_achievements(self, user_id: str, location: Dict[str, float]) -> List[Dict]:
        """Check and award location-based achievements"""
        achievements = []
        
        # Track user's donation locations
        if user_id not in self.user_locations:
            self.user_locations[user_id] = []
        
        self.user_locations[user_id].append(location)
        
        # Check for exploration achievements
        unique_locations = len(set(
            (loc["lat"], loc["lng"]) for loc in self.user_locations[user_id]
        ))
        
        if unique_locations >= 5 and "location_explorer" not in self._get_user_achievements(user_id):
            achievements.append({
                "name": "Location Explorer",
                "description": "Donated to 5 different locations",
                "points": 500,
                "type": "exploration",
                "emoji": "🗺️"
            })
        
        # Check for hotspot discoveries
        if self._is_new_hotspot(location):
            achievements.append({
                "name": "Hotspot Hunter", 
                "description": "Discovered a new donation hotspot",
                "points": 1000,
                "type": "discovery",
                "emoji": "🔥"
            })
        
        return achievements
    
    def _get_user_achievements(self, user_id: str) -> List[str]:
        """Get user's current achievements (would be from database)"""
        return []  # Simplified for demo
    
    def _is_new_hotspot(self, location: Dict[str, float]) -> bool:
        """Check if location is a new donation hotspot"""
        # Simplified hotspot detection logic
        return False  # Would implement actual hotspot algorithm

@Agent(
    name="Donor Engagement Agent",
    description="AI agent managing gamified donor engagement with points, tiers, and achievements",
    version="1.0.0",
    url="https://dea.donationplatform.com"
)
class DonorEngagementAgent(A2AServer):
    """Main Donor Engagement Agent implementation"""
    
    def __init__(self):
        super().__init__()
        self.points_engine = PointsEngine()
        self.ranking_system = RankingSystem()
        self.location_intelligence = LocationIntelligence()
        logger.info("Donor Engagement Agent initialized")
    
    @AgentSkill(
        name="Process Donation",
        description="Process donation and award gamification points with tier progression",
        tags=["donation", "gamification", "points", "achievements"]
    )
    async def process_donation(self, donation_data: Dict) -> Dict:
        """Core donation processing with comprehensive gamification"""
        
        try:
            user_id = donation_data['user_id']
            amount = donation_data['amount']
            location = donation_data.get('location')
            
            # Get user profile for tier calculation
            user_tier = await self._get_user_tier(user_id)
            
            # Calculate multi-factor points
            points_result = self.points_engine.calculate_points(
                user_id=user_id,
                activity="donation",
                amount=amount,
                user_tier=user_tier,
                location=location
            )
            
            # Update rankings and check tier progression
            rank_update = await self.ranking_system.update_rank(
                user_id, points_result.total_points
            )
            
            # Check location-based achievements
            location_achievements = await self.location_intelligence.check_achievements(
                user_id, location or {}
            )
            
            # Get updated leaderboard position
            leaderboard_position = await self._get_leaderboard_position(user_id)
            
            # Prepare response
            response = {
                "donation_id": donation_data['id'],
                "user_id": user_id,
                "points_awarded": points_result.total_points,
                "points_breakdown": points_result.breakdown,
                "tier_progression": rank_update,
                "achievements_unlocked": location_achievements,
                "leaderboard_position": leaderboard_position,
                "processing_timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Processed donation {donation_data['id']} for user {user_id}: {points_result.total_points} points")
            return response
            
        except Exception as e:
            logger.error(f"Error processing donation {donation_data.get('id', 'unknown')}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "donation_id": donation_data.get('id'),
                "processing_timestamp": datetime.now().isoformat()
            }
    
    @AgentSkill(
        name="Analyze Donor Base",
        description="Analyze donor engagement patterns and predict campaign success",
        tags=["analytics", "prediction", "engagement"]
    )
    async def analyze_donor_base(self, campaign_data: Dict) -> Dict:
        """Analyze donor engagement potential for campaigns"""
        
        campaign_type = campaign_data.get('type', 'general')
        
        # Simulate engagement analysis (would use real data and ML)
        engagement_metrics = {
            "active_donors_30d": 1250,
            "average_donation": 75.50,
            "engagement_rate": 0.68,
            "repeat_donor_rate": 0.45,
            "geographic_spread": 0.82,
            "tier_distribution": {
                "Bronze": 0.45,
                "Silver": 0.25, 
                "Gold": 0.20,
                "Platinum": 0.08,
                "Diamond": 0.02
            }
        }
        
        # Campaign-specific predictions
        success_factors = {
            "seasonal_alignment": self._check_seasonal_alignment(campaign_type),
            "donor_fatigue_risk": 0.15,  # Low risk
            "geographic_relevance": 0.88,
            "tier_appeal": self._calculate_tier_appeal(campaign_type)
        }
        
        return {
            "campaign_type": campaign_type,
            "engagement_metrics": engagement_metrics,
            "success_factors": success_factors,
            "recommended_strategy": self._generate_strategy_recommendations(success_factors),
            "predicted_engagement_lift": 0.12,  # 12% increase predicted
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def _get_user_tier(self, user_id: str) -> str:
        """Get user's current tier (would query database)"""
        return "Gold"  # Simplified for demo
    
    async def _get_leaderboard_position(self, user_id: str) -> int:
        """Get user's current leaderboard position"""
        return 42  # Simplified for demo
    
    def _check_seasonal_alignment(self, campaign_type: str) -> float:
        """Check if campaign aligns with current season"""
        return 0.85  # Good seasonal alignment
    
    def _calculate_tier_appeal(self, campaign_type: str) -> Dict[str, float]:
        """Calculate appeal by tier"""
        return {
            "Bronze": 0.7,
            "Silver": 0.8,
            "Gold": 0.9,
            "Platinum": 0.85,
            "Diamond": 0.95
        }
    
    def _generate_strategy_recommendations(self, success_factors: Dict) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        recommendations = [
            "Focus on Gold and Platinum tier donors for maximum impact",
            "Leverage seasonal timing with 2x point multipliers",
            "Implement location-based hotspot rewards",
            "Create tier-specific achievement challenges"
        ]
        return recommendations

# Agent startup and registration
async def create_donor_engagement_agent() -> DonorEngagementAgent:
    """Create and configure the Donor Engagement Agent"""
    
    agent = DonorEngagementAgent()
    
    # Register with A2A discovery service
    agent_card = AgentCard(
        name="Donor Engagement Agent",
        description="Gamified donor engagement with points, achievements, and tier progression",
        version="1.0.0",
        url="https://dea.donationplatform.com",
        skills=[
            "process_donation",
            "analyze_donor_base"
        ]
    )
    
    await agent.register_agent_card(agent_card)
    
    logger.info("Donor Engagement Agent created and registered")
    return agent

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        agent = await create_donor_engagement_agent()
        
        # Start the agent server
        config = uvicorn.Config(
            app=agent.app,
            host="0.0.0.0",
            port=8080,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    asyncio.run(main())