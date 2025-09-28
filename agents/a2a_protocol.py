"""
A2A Communication Protocol Implementation
Google Agent-to-Agent protocol v0.3 for seamless AI collaboration
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import httpx
import websockets
from cryptography.fernet import Fernet
import jwt

logger = logging.getLogger(__name__)

@dataclass
class AgentCard:
    """Agent discovery card for A2A protocol"""
    name: str
    description: str
    version: str
    url: str
    skills: List[str]
    protocol_version: str = "0.3.0"
    security_mode: str = "jwt_authenticated"
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class A2AMessage:
    """Standardized A2A message format"""
    id: str
    sender_agent: str
    recipient_agent: str
    skill: str
    params: Dict[str, Any]
    timestamp: str
    protocol_version: str = "0.3.0"
    
    def to_dict(self) -> Dict:
        return asdict(self)

class A2ASecurityManager:
    """Handle authentication and encryption for A2A communications"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.jwt_algorithm = "HS256"
        self.token_expiry = 3600  # 1 hour
    
    def generate_token(self, agent_id: str, permissions: List[str] = None) -> str:
        """Generate JWT token for agent authentication"""
        payload = {
            "agent_id": agent_id,
            "permissions": permissions or ["read", "write"],
            "exp": datetime.utcnow().timestamp() + self.token_expiry,
            "iat": datetime.utcnow().timestamp(),
            "protocol_version": "0.3.0"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def encrypt_message(self, message: Dict) -> bytes:
        """Encrypt message payload"""
        fernet = Fernet(Fernet.generate_key())  # In production, use stable key
        return fernet.encrypt(json.dumps(message).encode())
    
    def decrypt_message(self, encrypted_data: bytes, key: bytes) -> Dict:
        """Decrypt message payload"""
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data)
        return json.loads(decrypted.decode())

class A2AChannel:
    """Bidirectional communication channel between agents"""
    
    def __init__(self, agent1_card: AgentCard, agent2_card: AgentCard, security_manager: A2ASecurityManager):
        self.agent1_card = agent1_card
        self.agent2_card = agent2_card
        self.security_manager = security_manager
        self.protocol_version = "0.3.0"
        self.active_connections = {}
        
        logger.info(f"A2A Channel established between {agent1_card.name} and {agent2_card.name}")
    
    async def send_to_agent1(self, message_data: Dict) -> Dict:
        """Send message to agent 1"""
        return await self._send_message(self.agent1_card.url, message_data, self.agent2_card.name)
    
    async def send_to_agent2(self, message_data: Dict) -> Dict:
        """Send message to agent 2"""
        return await self._send_message(self.agent2_card.url, message_data, self.agent1_card.name)
    
    async def _send_message(self, target_url: str, message_data: Dict, sender_name: str) -> Dict:
        """Send message to target agent with security"""
        
        try:
            # Generate authentication token
            token = self.security_manager.generate_token(sender_name)
            
            # Create standardized A2A message
            message = A2AMessage(
                id=f"a2a_{datetime.now().timestamp()}",
                sender_agent=sender_name,
                recipient_agent=target_url,
                skill=message_data.get("skill", "default"),
                params=message_data.get("params", {}),
                timestamp=datetime.now().isoformat()
            )
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "A2A-Protocol-Version": self.protocol_version
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{target_url}/a2a/invoke",
                    json=message.to_dict(),
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"A2A message failed: {response.status_code} - {response.text}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error sending A2A message: {str(e)}")
            return {"success": False, "error": str(e)}

class A2AClient:
    """Client for communicating with remote agents"""
    
    def __init__(self, target_agent_url: str, security_key: str = None):
        self.target_url = target_agent_url
        self.security_manager = A2ASecurityManager(security_key or "default-key")
        self.agent_card = None
        
    async def discover_agent(self) -> Optional[AgentCard]:
        """Discover target agent capabilities"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.target_url}/.well-known/agent.json")
                
                if response.status_code == 200:
                    agent_data = response.json()
                    self.agent_card = AgentCard(**agent_data)
                    logger.info(f"Discovered agent: {self.agent_card.name}")
                    return self.agent_card
                else:
                    logger.error(f"Agent discovery failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error discovering agent: {str(e)}")
            return None
    
    async def ask(self, request: Dict) -> Dict:
        """Send request to target agent"""
        
        if not self.agent_card:
            await self.discover_agent()
        
        try:
            token = self.security_manager.generate_token("client")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "A2A-Protocol-Version": "0.3.0"
            }
            
            message = {
                "id": f"req_{datetime.now().timestamp()}",
                "skill": request.get("skill"),
                "params": request.get("params", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.target_url}/a2a/invoke",
                    json=message,
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Request failed: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error sending request: {str(e)}")
            return {"success": False, "error": str(e)}

class A2AServer:
    """Base server class for A2A-enabled agents"""
    
    def __init__(self, agent_name: str, agent_url: str):
        self.agent_name = agent_name
        self.agent_url = agent_url
        self.security_manager = A2ASecurityManager("agent-secret-key")
        self.skills = {}
        self.app = self._create_fastapi_app()
    
    def _create_fastapi_app(self):
        """Create FastAPI application with A2A endpoints"""
        from fastapi import FastAPI, HTTPException, Header, Depends
        from fastapi.responses import JSONResponse
        
        app = FastAPI(title=f"{self.agent_name} A2A Interface")
        
        @app.get("/.well-known/agent.json")
        async def agent_discovery():
            """Agent discovery endpoint"""
            return {
                "name": self.agent_name,
                "description": f"A2A-enabled {self.agent_name}",
                "version": "1.0.0",
                "url": self.agent_url,
                "skills": list(self.skills.keys()),
                "protocol_version": "0.3.0",
                "security_mode": "jwt_authenticated"
            }
        
        @app.post("/a2a/invoke")
        async def invoke_skill(
            message: Dict,
            authorization: str = Header(None),
            a2a_protocol_version: str = Header(None, alias="A2A-Protocol-Version")
        ):
            """Invoke agent skill via A2A protocol"""
            
            # Verify authentication
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid authorization")
            
            token = authorization.split(" ")[1]
            
            try:
                self.security_manager.verify_token(token)
            except ValueError as e:
                raise HTTPException(status_code=401, detail=str(e))
            
            # Extract skill and parameters
            skill_name = message.get("skill")
            params = message.get("params", {})
            
            if skill_name not in self.skills:
                raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
            
            # Execute skill
            try:
                skill_function = self.skills[skill_name]
                result = await skill_function(params)
                
                return {
                    "success": True,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                    "agent": self.agent_name
                }
                
            except Exception as e:
                logger.error(f"Error executing skill {skill_name}: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                        "agent": self.agent_name
                    }
                )
        
        return app
    
    def register_skill(self, name: str, function: callable, description: str = None):
        """Register a skill function"""
        self.skills[name] = function
        logger.info(f"Registered skill: {name}")
    
    async def register_agent_card(self, agent_card: AgentCard):
        """Register agent with discovery service"""
        # In production, would register with Google's A2A discovery service
        logger.info(f"Registered agent card for {agent_card.name}")

# Coordination workflow functions
async def fetch_agent_card(url: str) -> Optional[AgentCard]:
    """Fetch agent card from well-known endpoint"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return AgentCard(**data)
            else:
                logger.error(f"Failed to fetch agent card from {url}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error fetching agent card: {str(e)}")
        return None

async def setup_a2a_communication(donor_agent_url: str, charity_agent_url: str) -> A2AChannel:
    """Initialize bidirectional agent communication"""
    
    # Agent discovery via well-known endpoints
    donor_agent_card = await fetch_agent_card(f"{donor_agent_url}/.well-known/agent.json")
    charity_agent_card = await fetch_agent_card(f"{charity_agent_url}/.well-known/agent.json")
    
    if not donor_agent_card or not charity_agent_card:
        raise ValueError("Failed to discover one or both agents")
    
    # Create security manager
    security_manager = A2ASecurityManager("shared-secret-key")
    
    # Establish secure communication channel
    communication_channel = A2AChannel(
        agent1_card=donor_agent_card,
        agent2_card=charity_agent_card,
        security_manager=security_manager
    )
    
    logger.info("A2A communication channel established successfully")
    return communication_channel

async def coordinate_donation_campaign(channel: A2AChannel, campaign_data: Dict) -> Dict:
    """Example coordination workflow between agents"""
    
    try:
        # Step 1: DEA analyzes donor engagement potential
        engagement_analysis = await channel.send_to_agent1({
            "skill": "analyze_donor_base",
            "params": {"campaign_type": campaign_data['type']}
        })
        
        if not engagement_analysis.get("success"):
            raise ValueError("Failed to get engagement analysis")
        
        # Step 2: COA optimizes based on engagement data
        optimization_plan = await channel.send_to_agent2({
            "skill": "optimize_campaign", 
            "params": {
                "engagement_metrics": engagement_analysis["result"],
                "campaign_goals": campaign_data['goals']
            }
        })
        
        if not optimization_plan.get("success"):
            raise ValueError("Failed to get optimization plan")
        
        # Step 3: Calculate success probability
        success_probability = calculate_success_probability(
            engagement_analysis["result"], 
            optimization_plan["result"]
        )
        
        return {
            "success": True,
            "engagement_potential": engagement_analysis["result"],
            "optimization_strategy": optimization_plan["result"],
            "success_probability": success_probability,
            "coordination_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in campaign coordination: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "coordination_timestamp": datetime.now().isoformat()
        }

def calculate_success_probability(engagement_analysis: Dict, optimization_plan: Dict) -> float:
    """Calculate campaign success probability based on agent analyses"""
    
    # Extract key metrics
    engagement_rate = engagement_analysis.get("engagement_metrics", {}).get("engagement_rate", 0.5)
    predicted_lift = optimization_plan.get("campaign_optimization", {}).get("expected_engagement_lift", 0.1)
    
    # Simple success probability calculation
    base_probability = 0.6
    engagement_factor = engagement_rate * 0.3
    optimization_factor = predicted_lift * 0.1
    
    success_probability = min(base_probability + engagement_factor + optimization_factor, 0.95)
    
    return round(success_probability, 3)

# Example usage and testing
async def test_a2a_communication():
    """Test A2A communication setup"""
    
    try:
        # Setup communication channel
        channel = await setup_a2a_communication(
            "https://dea.donationplatform.com",
            "https://coa.donationplatform.com"
        )
        
        # Test campaign coordination
        campaign_data = {
            "type": "holiday_drive",
            "goals": {
                "target_amount": 50000,
                "duration_days": 14,
                "target_donors": 500
            }
        }
        
        result = await coordinate_donation_campaign(channel, campaign_data)
        
        if result["success"]:
            logger.info("A2A communication test successful")
            logger.info(f"Success probability: {result['success_probability']}")
        else:
            logger.error(f"A2A communication test failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"A2A communication test error: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test A2A communication
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(test_a2a_communication())
    print(json.dumps(result, indent=2))