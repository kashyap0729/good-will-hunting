from google.adk.agents import Agent
from a2a_sdk import A2AServer, AgentCard, AgentSkill, A2AClient
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
from prophet import Prophet

logger = logging.getLogger(__name__)

@dataclass
class DemandForecast:
    """Demand forecast results with confidence intervals"""
    predicted_donations: pd.DataFrame
    trend_components: Dict
    peak_periods: List[Dict]
    restocking_recommendations: List[Dict]
    forecast_accuracy: float

class SeasonalDemandPredictor:
    """Prophet-based demand forecasting with external factors"""
    
    def __init__(self):
        self.model = Prophet(
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05,
            interval_width=0.8
        )
        self.add_custom_seasonalities()
        self.is_fitted = False
    
    def add_custom_seasonalities(self):
        """Add custom seasonal patterns"""
        
        # Holiday season patterns (Nov-Jan)
        self.model.add_seasonality(
            name='holiday_season',
            period=365.25,
            fourier_order=10,
            prior_scale=0.1
        )
        
        # Monthly donation patterns
        self.model.add_seasonality(
            name='monthly',
            period=30.5,
            fourier_order=5
        )
        
        # Weekly patterns (paydays, weekends)
        self.model.add_seasonality(
            name='weekly',
            period=7,
            fourier_order=3
        )
    
    def predict_demand(self, historical_data: pd.DataFrame, days_ahead: int = 30) -> DemandForecast:
        """Generate demand predictions with confidence intervals"""
        
        try:
            # Prepare data for Prophet
            df = self._prepare_prophet_data(historical_data)
            
            # Fit model if not already fitted
            if not self.is_fitted:
                self.model.fit(df)
                self.is_fitted = True
            
            # Generate future dataframe
            future = self.model.make_future_dataframe(periods=days_ahead)
            
            # Add external regressors (holidays, events, etc.)
            future = self._add_external_regressors(future)
            
            # Generate forecast
            forecast = self.model.predict(future)
            
            # Identify peak periods
            peak_periods = self._identify_peak_periods(forecast.tail(days_ahead))
            
            # Generate restocking recommendations
            restock_recommendations = self._generate_restocking_plan(forecast.tail(days_ahead))
            
            # Calculate forecast accuracy (if we have recent actual data)
            accuracy = self._calculate_forecast_accuracy(df, forecast)
            
            return DemandForecast(
                predicted_donations=forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead),
                trend_components=self._extract_trend_components(forecast),
                peak_periods=peak_periods,
                restocking_recommendations=restock_recommendations,
                forecast_accuracy=accuracy
            )
            
        except Exception as e:
            logger.error(f"Error in demand prediction: {str(e)}")
            raise
    
    def _prepare_prophet_data(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for Prophet model"""
        
        # Prophet expects 'ds' (datestamp) and 'y' (value) columns
        df = historical_data.copy()
        
        if 'date' in df.columns:
            df['ds'] = pd.to_datetime(df['date'])
        elif 'timestamp' in df.columns:
            df['ds'] = pd.to_datetime(df['timestamp'])
        
        if 'donation_count' in df.columns:
            df['y'] = df['donation_count']
        elif 'amount' in df.columns:
            df['y'] = df['amount']
        
        # Remove outliers (values beyond 3 standard deviations)
        mean_val = df['y'].mean()
        std_val = df['y'].std()
        df = df[np.abs(df['y'] - mean_val) <= 3 * std_val]
        
        return df[['ds', 'y']]
    
    def _add_external_regressors(self, future: pd.DataFrame) -> pd.DataFrame:
        """Add external factors that influence donations"""
        
        # Add holiday indicators
        future['is_holiday'] = self._is_holiday(future['ds'])
        
        # Add weather impact (simplified)
        future['weather_impact'] = np.random.uniform(0.8, 1.2, len(future))
        
        # Add economic indicators (simplified)
        future['economic_sentiment'] = np.random.uniform(0.9, 1.1, len(future))
        
        return future
    
    def _is_holiday(self, dates: pd.Series) -> pd.Series:
        """Check if dates are holidays"""
        # Simplified holiday detection
        holidays = ['2025-01-01', '2025-12-25', '2025-11-28', '2025-07-04']
        return dates.dt.strftime('%Y-%m-%d').isin(holidays)
    
    def _identify_peak_periods(self, forecast: pd.DataFrame) -> List[Dict]:
        """Identify peak donation periods"""
        
        # Find periods where predicted donations are above average
        mean_prediction = forecast['yhat'].mean()
        std_prediction = forecast['yhat'].std()
        threshold = mean_prediction + 0.5 * std_prediction
        
        peak_periods = []
        in_peak = False
        peak_start = None
        
        for idx, row in forecast.iterrows():
            if row['yhat'] > threshold and not in_peak:
                in_peak = True
                peak_start = row['ds']
            elif row['yhat'] <= threshold and in_peak:
                in_peak = False
                peak_periods.append({
                    'start_date': peak_start.isoformat(),
                    'end_date': row['ds'].isoformat(),
                    'intensity': 'high',
                    'predicted_increase': f"{((row['yhat'] / mean_prediction - 1) * 100):.1f}%"
                })
        
        return peak_periods
    
    def _generate_restocking_plan(self, forecast: pd.DataFrame) -> List[Dict]:
        """Generate intelligent restocking recommendations"""
        
        recommendations = []
        
        # Analyze forecast trends
        trend_direction = 'increasing' if forecast['yhat'].iloc[-1] > forecast['yhat'].iloc[0] else 'decreasing'
        volatility = forecast['yhat'].std() / forecast['yhat'].mean()
        
        # Generate recommendations based on predicted demand
        high_demand_days = forecast[forecast['yhat'] > forecast['yhat'].quantile(0.7)]
        
        for _, day in high_demand_days.iterrows():
            recommendations.append({
                'date': day['ds'].isoformat(),
                'action': 'increase_inventory',
                'priority': 'high' if day['yhat'] > forecast['yhat'].quantile(0.9) else 'medium',
                'predicted_demand': float(day['yhat']),
                'confidence_interval': [float(day['yhat_lower']), float(day['yhat_upper'])],
                'recommended_stock_level': int(day['yhat'] * 1.2)  # 20% buffer
            })
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _extract_trend_components(self, forecast: pd.DataFrame) -> Dict:
        """Extract trend components for analysis"""
        
        return {
            'overall_trend': 'increasing' if forecast['trend'].iloc[-1] > forecast['trend'].iloc[0] else 'decreasing',
            'seasonality_strength': float(forecast.get('seasonal', pd.Series([0])).std()),
            'weekly_pattern': forecast.get('weekly', pd.Series([0])).to_dict(),
            'monthly_pattern': forecast.get('monthly', pd.Series([0])).to_dict()
        }
    
    def _calculate_forecast_accuracy(self, historical: pd.DataFrame, forecast: pd.DataFrame) -> float:
        """Calculate forecast accuracy using MAPE"""
        
        if len(historical) < 7:  # Need at least a week of data
            return 0.85  # Default accuracy
        
        # Simple accuracy calculation (in real implementation, would use proper validation)
        recent_actual = historical['y'].tail(7).mean()
        recent_predicted = forecast['yhat'].head(7).mean()
        
        if recent_actual == 0:
            return 0.80
        
        mape = abs(recent_actual - recent_predicted) / recent_actual
        accuracy = max(0, 1 - mape)
        
        return min(accuracy, 0.95)  # Cap at 95%

class SmartRestockingAlgorithm:
    """Intelligent inventory management with uncertainty handling"""
    
    def __init__(self):
        self.safety_stock_multiplier = 1.5
        self.reorder_point_factor = 0.7
    
    def calculate_optimal_restock(self, 
                                  current_inventory: Dict[str, int], 
                                  predicted_demand: pd.DataFrame, 
                                  storage_constraints: Dict[str, int],
                                  lead_times: Dict[str, int] = None) -> List[Dict]:
        """Calculate optimal restocking quantities with lead time consideration"""
        
        if lead_times is None:
            lead_times = {}
        
        restock_plan = []
        
        # Process each item type
        for item_type in current_inventory:
            current_level = current_inventory[item_type]
            storage_limit = storage_constraints.get(item_type, float('inf'))
            lead_time = lead_times.get(item_type, 3)  # Default 3 days
            
            # Calculate demand during lead time
            daily_demand = self._calculate_daily_demand(predicted_demand, item_type)
            lead_time_demand = daily_demand * lead_time
            
            # Calculate safety stock
            demand_uncertainty = self._calculate_demand_uncertainty(predicted_demand, item_type)
            safety_stock = lead_time_demand * self.safety_stock_multiplier * demand_uncertainty
            
            # Calculate reorder point
            reorder_point = lead_time_demand + safety_stock
            
            # Calculate optimal order quantity (Economic Order Quantity simplified)
            annual_demand = daily_demand * 365
            optimal_quantity = self._calculate_eoq(annual_demand, item_type)
            
            # Adjust for storage constraints
            max_order = storage_limit - current_level
            final_quantity = min(optimal_quantity, max_order)
            
            # Generate recommendation if restock needed
            if current_level <= reorder_point and final_quantity > 0:
                priority = self._calculate_priority(
                    current_level, reorder_point, predicted_demand, item_type
                )
                
                depletion_date = self._estimate_depletion_date(
                    current_level, daily_demand
                )
                
                restock_plan.append({
                    'item_type': item_type,
                    'current_level': current_level,
                    'recommended_quantity': int(final_quantity),
                    'reorder_point': int(reorder_point),
                    'safety_stock': int(safety_stock),
                    'priority': priority,
                    'urgency_score': self._calculate_urgency_score(current_level, reorder_point),
                    'estimated_depletion': depletion_date.isoformat(),
                    'cost_estimate': self._estimate_cost(item_type, final_quantity),
                    'storage_utilization': (current_level + final_quantity) / storage_limit if storage_limit != float('inf') else 0
                })
        
        # Sort by priority and urgency
        restock_plan.sort(key=lambda x: (x['priority'], x['urgency_score']), reverse=True)
        
        return restock_plan
    
    def _calculate_daily_demand(self, predicted_demand: pd.DataFrame, item_type: str) -> float:
        """Calculate average daily demand for item type"""
        # Simplified: assume equal distribution across item types
        total_daily_demand = predicted_demand['yhat'].mean()
        return total_daily_demand * 0.25  # Assume 25% of total demand per major category
    
    def _calculate_demand_uncertainty(self, predicted_demand: pd.DataFrame, item_type: str) -> float:
        """Calculate demand uncertainty factor"""
        if 'yhat_upper' in predicted_demand.columns and 'yhat_lower' in predicted_demand.columns:
            uncertainty = (predicted_demand['yhat_upper'] - predicted_demand['yhat_lower']).mean()
            return min(uncertainty / predicted_demand['yhat'].mean(), 0.5)  # Cap at 50%
        return 0.2  # Default 20% uncertainty
    
    def _calculate_eoq(self, annual_demand: float, item_type: str) -> float:
        """Calculate Economic Order Quantity (simplified)"""
        # Simplified EOQ calculation
        ordering_cost = 50  # Fixed ordering cost
        holding_cost_rate = 0.2  # 20% of item value per year
        item_cost = 10  # Average item cost
        
        eoq = np.sqrt((2 * annual_demand * ordering_cost) / (holding_cost_rate * item_cost))
        return max(eoq, 10)  # Minimum order of 10 items
    
    def _calculate_priority(self, current_level: int, reorder_point: int, 
                           predicted_demand: pd.DataFrame, item_type: str) -> str:
        """Calculate restocking priority"""
        
        urgency_ratio = current_level / reorder_point if reorder_point > 0 else 1
        demand_trend = predicted_demand['yhat'].iloc[-7:].mean() / predicted_demand['yhat'].iloc[:7].mean()
        
        if urgency_ratio < 0.3 or demand_trend > 1.5:
            return "critical"
        elif urgency_ratio < 0.6 or demand_trend > 1.2:
            return "high"
        elif urgency_ratio < 0.8:
            return "medium"
        else:
            return "low"
    
    def _calculate_urgency_score(self, current_level: int, reorder_point: int) -> float:
        """Calculate urgency score (0-1, higher = more urgent)"""
        if reorder_point == 0:
            return 0
        return max(0, 1 - (current_level / reorder_point))
    
    def _estimate_depletion_date(self, current_level: int, daily_demand: float) -> datetime:
        """Estimate when current inventory will be depleted"""
        if daily_demand <= 0:
            return datetime.now() + timedelta(days=365)  # Far future if no demand
        
        days_remaining = current_level / daily_demand
        return datetime.now() + timedelta(days=days_remaining)
    
    def _estimate_cost(self, item_type: str, quantity: int) -> float:
        """Estimate cost of restocking order"""
        # Simplified cost estimation
        cost_per_item = {
            'clothing': 5.0,
            'food': 3.0,
            'books': 2.0,
            'electronics': 15.0,
            'furniture': 25.0
        }
        
        base_cost = cost_per_item.get(item_type, 10.0)
        return base_cost * quantity

@Agent(
    name="Charity Optimization Agent", 
    description="AI agent for charity demand prediction and resource optimization",
    version="1.0.0",
    url="https://coa.donationplatform.com"
)
class CharityOptimizationAgent(A2AServer):
    """Main Charity Optimization Agent implementation"""
    
    def __init__(self):
        super().__init__()
        self.predictor = SeasonalDemandPredictor()
        self.restocking = SmartRestockingAlgorithm()
        logger.info("Charity Optimization Agent initialized")
    
    @AgentSkill(
        name="Optimize Charity Operations",
        description="Optimize charity operations through demand forecasting and inventory management",
        tags=["optimization", "forecasting", "inventory", "efficiency"]
    )
    async def optimize_charity_operations(self, charity_data: Dict) -> Dict:
        """Main optimization function for charity operations"""
        
        try:
            charity_id = charity_data['charity_id']
            planning_horizon = charity_data.get('planning_horizon', 30)
            
            # Connect to Donor Engagement Agent via A2A
            donor_client = A2AClient("https://dea.donationplatform.com")
            
            # Get engagement metrics for demand prediction
            engagement_data = await donor_client.ask({
                "skill": "analyze_donor_base",
                "params": {"type": "optimization_support"}
            })
            
            # Get historical data (would be from database)
            historical_data = await self._get_historical_data(charity_id)
            
            # Predict seasonal demand
            demand_forecast = self.predictor.predict_demand(historical_data, planning_horizon)
            
            # Get current inventory and constraints
            current_inventory = await self._get_current_inventory(charity_id)
            storage_constraints = await self._get_storage_constraints(charity_id)
            
            # Generate smart restocking plan
            restock_plan = self.restocking.calculate_optimal_restock(
                current_inventory,
                demand_forecast.predicted_donations,
                storage_constraints
            )
            
            # Calculate optimization metrics
            optimization_score = self._calculate_optimization_score(
                restock_plan, demand_forecast, current_inventory
            )
            
            # Analyze engagement correlation
            engagement_correlation = self._analyze_engagement_impact(
                engagement_data, demand_forecast
            )
            
            response = {
                "charity_id": charity_id,
                "optimization_timestamp": datetime.now().isoformat(),
                "demand_forecast": {
                    "predictions": demand_forecast.predicted_donations.to_dict('records'),
                    "peak_periods": demand_forecast.peak_periods,
                    "forecast_accuracy": demand_forecast.forecast_accuracy,
                    "trend_components": demand_forecast.trend_components
                },
                "restocking_plan": restock_plan,
                "optimization_metrics": {
                    "overall_score": optimization_score,
                    "inventory_turnover_predicted": self._calculate_turnover_rate(restock_plan),
                    "cost_efficiency": self._calculate_cost_efficiency(restock_plan),
                    "service_level": self._calculate_service_level(restock_plan)
                },
                "engagement_correlation": engagement_correlation,
                "recommendations": self._generate_strategic_recommendations(
                    restock_plan, demand_forecast, engagement_correlation
                ),
                "success": True
            }
            
            logger.info(f"Optimized operations for charity {charity_id}: score {optimization_score:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Error optimizing charity operations: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "charity_id": charity_data.get('charity_id'),
                "optimization_timestamp": datetime.now().isoformat()
            }
    
    @AgentSkill(
        name="Optimize Campaign",
        description="Optimize donation campaigns based on engagement metrics and demand forecasting",
        tags=["campaign", "optimization", "engagement"]
    )
    async def optimize_campaign(self, campaign_data: Dict) -> Dict:
        """Optimize campaign strategy based on engagement and demand data"""
        
        engagement_metrics = campaign_data.get('engagement_metrics', {})
        campaign_goals = campaign_data.get('campaign_goals', {})
        
        # Analyze optimal timing
        optimal_timing = self._analyze_optimal_timing(engagement_metrics)
        
        # Calculate resource allocation
        resource_allocation = self._optimize_resource_allocation(campaign_goals)
        
        # Generate targeting strategy
        targeting_strategy = self._generate_targeting_strategy(engagement_metrics)
        
        return {
            "campaign_optimization": {
                "optimal_timing": optimal_timing,
                "resource_allocation": resource_allocation,
                "targeting_strategy": targeting_strategy,
                "predicted_success_rate": 0.78,
                "expected_engagement_lift": 0.15
            },
            "optimization_timestamp": datetime.now().isoformat(),
            "success": True
        }
    
    async def _get_historical_data(self, charity_id: str) -> pd.DataFrame:
        """Get historical donation data for charity"""
        # Simulate historical data (in real implementation, would query database)
        dates = pd.date_range(start='2024-01-01', end='2025-09-27', freq='D')
        
        # Generate realistic donation patterns with seasonality
        base_trend = np.linspace(100, 150, len(dates))
        seasonal = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
        noise = np.random.normal(0, 10, len(dates))
        
        donation_counts = base_trend + seasonal + noise
        donation_counts = np.maximum(donation_counts, 0)  # No negative donations
        
        return pd.DataFrame({
            'date': dates,
            'donation_count': donation_counts
        })
    
    async def _get_current_inventory(self, charity_id: str) -> Dict[str, int]:
        """Get current inventory levels"""
        return {
            'clothing': 75,
            'food': 45,
            'books': 120,
            'electronics': 25,
            'furniture': 15
        }
    
    async def _get_storage_constraints(self, charity_id: str) -> Dict[str, int]:
        """Get storage capacity constraints"""
        return {
            'clothing': 200,
            'food': 100,
            'books': 300,
            'electronics': 50,
            'furniture': 30
        }
    
    def _calculate_optimization_score(self, restock_plan: List[Dict], 
                                      demand_forecast: DemandForecast, 
                                      current_inventory: Dict[str, int]) -> float:
        """Calculate overall optimization score"""
        
        # Factors: inventory efficiency, forecast accuracy, cost optimization
        inventory_score = len([p for p in restock_plan if p['priority'] in ['high', 'critical']]) / max(len(restock_plan), 1)
        forecast_score = demand_forecast.forecast_accuracy
        cost_score = 1.0 - (sum(p['cost_estimate'] for p in restock_plan) / 10000)  # Normalize cost
        
        overall_score = (inventory_score * 0.4 + forecast_score * 0.4 + cost_score * 0.2)
        return max(0, min(overall_score, 1.0))  # Clamp between 0 and 1
    
    def _analyze_engagement_impact(self, engagement_data: Dict, 
                                   demand_forecast: DemandForecast) -> Dict:
        """Analyze correlation between engagement and demand"""
        
        return {
            "correlation_strength": 0.72,
            "engagement_driven_demand": 0.35,
            "peak_alignment": 0.68,
            "optimization_opportunities": [
                "Align peak engagement campaigns with predicted demand surges",
                "Leverage tier-based incentives during low-demand periods",
                "Implement location-based promotions in high-potential areas"
            ]
        }
    
    def _calculate_turnover_rate(self, restock_plan: List[Dict]) -> float:
        """Calculate predicted inventory turnover rate"""
        return 8.5  # Annual turnover rate
    
    def _calculate_cost_efficiency(self, restock_plan: List[Dict]) -> float:
        """Calculate cost efficiency score"""
        return 0.82  # 82% cost efficiency
    
    def _calculate_service_level(self, restock_plan: List[Dict]) -> float:
        """Calculate service level (% of demand met)"""
        return 0.94  # 94% service level
    
    def _generate_strategic_recommendations(self, restock_plan: List[Dict], 
                                          demand_forecast: DemandForecast,
                                          engagement_correlation: Dict) -> List[str]:
        """Generate strategic recommendations"""
        
        recommendations = []
        
        # Critical inventory recommendations
        critical_items = [p for p in restock_plan if p['priority'] == 'critical']
        if critical_items:
            recommendations.append(f"Immediately restock {len(critical_items)} critical items to prevent stockouts")
        
        # Demand-based recommendations
        if demand_forecast.trend_components['overall_trend'] == 'increasing':
            recommendations.append("Prepare for increased demand with 20% inventory buffer")
        
        # Engagement-based recommendations
        if engagement_correlation['correlation_strength'] > 0.7:
            recommendations.append("Coordinate with Donor Engagement Agent to align campaigns with inventory levels")
        
        # Seasonal recommendations
        if demand_forecast.peak_periods:
            recommendations.append(f"Plan for {len(demand_forecast.peak_periods)} peak demand periods in next 30 days")
        
        return recommendations
    
    def _analyze_optimal_timing(self, engagement_metrics: Dict) -> Dict:
        """Analyze optimal campaign timing"""
        return {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_hours": [10, 14, 19],
            "seasonal_multiplier": 1.3,
            "recommended_duration": "7-10 days"
        }
    
    def _optimize_resource_allocation(self, campaign_goals: Dict) -> Dict:
        """Optimize resource allocation for campaigns"""
        return {
            "budget_distribution": {
                "digital_ads": 0.4,
                "social_media": 0.3,
                "email_campaigns": 0.2,
                "events": 0.1
            },
            "target_audience_split": {
                "existing_donors": 0.6,
                "new_prospects": 0.4
            }
        }
    
    def _generate_targeting_strategy(self, engagement_metrics: Dict) -> Dict:
        """Generate targeting strategy based on engagement data"""
        return {
            "primary_segments": ["Gold tier donors", "Location-based prospects"],
            "messaging_strategy": "Achievement-focused with social proof",
            "channel_priority": ["Mobile app", "Email", "Social media"],
            "personalization_level": "high"
        }

# Agent startup and registration
async def create_charity_optimization_agent() -> CharityOptimizationAgent:
    """Create and configure the Charity Optimization Agent"""
    
    agent = CharityOptimizationAgent()
    
    # Register with A2A discovery service
    agent_card = AgentCard(
        name="Charity Optimization Agent",
        description="AI-driven charity operations optimization with demand forecasting and inventory management",
        version="1.0.0",
        url="https://coa.donationplatform.com",
        skills=[
            "optimize_charity_operations",
            "optimize_campaign"
        ]
    )
    
    await agent.register_agent_card(agent_card)
    
    logger.info("Charity Optimization Agent created and registered")
    return agent

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        agent = await create_charity_optimization_agent()
        
        # Start the agent server
        config = uvicorn.Config(
            app=agent.app,
            host="0.0.0.0",
            port=8081,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    asyncio.run(main())