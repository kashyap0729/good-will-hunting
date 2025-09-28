# 🔌 API Reference - Google A2A Gamified Goodwill Platform

## Base URL & Authentication

### Production Environment
```
Base URL: https://api.goodwillplatform.com
Version: v1
Authentication: Bearer JWT tokens
```

### Headers
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
X-API-Version: v1
```

---

## 🎯 Donations API

### Create Donation
Create a new charitable donation with automatic gamification processing.

```http
POST /api/v1/donations
```

#### Request Body
```json
{
  "amount": 75.50,
  "donation_type": "monetary",
  "charity_id": "550e8400-e29b-41d4-a716-446655440001",
  "location": {
    "lat": 37.7749,
    "lng": -122.4194,
    "address": "Downtown Community Center"
  },
  "message": "Keep up the great work!",
  "anonymous": false,
  "recurring": {
    "enabled": true,
    "frequency": "monthly",
    "end_date": "2024-12-31"
  }
}
```

#### Response
```json
{
  "donation_id": "don_1234567890",
  "amount": 75.50,
  "status": "completed",
  "points_awarded": 755,
  "tier_bonus": 113,
  "location_bonus": 38,
  "streak_multiplier": 1.5,
  "achievements_unlocked": [
    {
      "id": "first_donation",
      "name": "Welcome Contributor",
      "description": "Made your first donation!",
      "points": 100,
      "badge_url": "https://cdn.platform.com/badges/welcome.png"
    }
  ],
  "new_tier": null,
  "leaderboard_position": 1247,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Donation History
Retrieve user's donation history with filtering options.

```http
GET /api/v1/donations/history
```

#### Query Parameters
- `limit` (int): Number of donations to return (default: 20, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `start_date` (string): ISO date filter start (optional)
- `end_date` (string): ISO date filter end (optional)
- `charity_id` (string): Filter by specific charity (optional)
- `donation_type` (string): Filter by type (monetary|goods|time) (optional)

#### Response
```json
{
  "donations": [
    {
      "donation_id": "don_1234567890",
      "amount": 75.50,
      "donation_type": "monetary",
      "charity_name": "Local Food Bank",
      "points_awarded": 755,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 42,
  "has_more": true,
  "next_offset": 20
}
```

---

## 🏆 Points & Achievements API

### Get User Profile
Retrieve complete user gamification profile.

```http
GET /api/v1/users/{user_id}/profile
```

#### Response
```json
{
  "user_id": "usr_987654321",
  "total_points": 15420,
  "current_tier": "gold",
  "tier_progress": {
    "current_points": 15420,
    "next_tier_threshold": 20000,
    "progress_percentage": 77.1
  },
  "statistics": {
    "total_donations": 87,
    "total_amount_donated": 4387.50,
    "current_streak": 12,
    "longest_streak": 28,
    "favorite_charity_category": "education",
    "average_donation": 50.43
  },
  "achievements": [
    {
      "id": "streak_master",
      "name": "Streak Master",
      "description": "Maintained 30-day donation streak",
      "unlocked_at": "2024-01-10T15:22:00Z",
      "rarity": "legendary"
    }
  ],
  "badges": [
    "consistent_giver",
    "community_champion", 
    "education_supporter"
  ]
}
```

### Get Available Achievements
List all achievements with unlock requirements.

```http
GET /api/v1/achievements
```

#### Response
```json
{
  "categories": {
    "giving": [
      {
        "id": "first_donation",
        "name": "Welcome Contributor",
        "description": "Make your first donation",
        "points": 100,
        "rarity": "common",
        "requirement": "donations >= 1",
        "badge_url": "https://cdn.platform.com/badges/welcome.png"
      },
      {
        "id": "generous_giver",
        "name": "Generous Giver", 
        "description": "Donate $500 or more in a single contribution",
        "points": 1000,
        "rarity": "rare",
        "requirement": "single_donation >= 500",
        "badge_url": "https://cdn.platform.com/badges/generous.png"
      }
    ],
    "consistency": [
      {
        "id": "weekly_warrior",
        "name": "Weekly Warrior",
        "description": "Donate every week for a month",
        "points": 500,
        "rarity": "uncommon", 
        "requirement": "weekly_donations >= 4",
        "badge_url": "https://cdn.platform.com/badges/weekly.png"
      }
    ]
  }
}
```

### Update Achievement Progress
Manually trigger achievement check (admin only).

```http
POST /api/v1/users/{user_id}/achievements/check
```

---

## 📊 Leaderboards API

### Global Leaderboard
Get top users across all categories.

```http
GET /api/v1/leaderboard/global
```

#### Query Parameters
- `limit` (int): Number of users to return (default: 50, max: 100)
- `timeframe` (string): all_time|monthly|weekly|daily (default: all_time)

#### Response
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": "usr_123456789",
      "username": "CharityChampion2024",
      "total_points": 89420,
      "tier": "diamond",
      "total_donations": 312,
      "profile_image": "https://cdn.platform.com/avatars/user123.jpg"
    }
  ],
  "current_user_rank": 47,
  "total_participants": 15847,
  "timeframe": "all_time",
  "last_updated": "2024-01-15T12:00:00Z"
}
```

### Tier-Specific Leaderboard
Get leaderboard for specific tier only.

```http
GET /api/v1/leaderboard/tier/{tier_name}
```

#### Response
```json
{
  "tier": "gold",
  "leaderboard": [
    {
      "rank": 1,
      "user_id": "usr_555666777",
      "username": "GoldGiver42",
      "total_points": 17892,
      "donations_this_period": 8,
      "tier_entry_date": "2024-01-01T00:00:00Z"
    }
  ],
  "tier_requirements": {
    "min_points": 10000,
    "max_points": 19999,
    "benefits": [
      "20% point multiplier",
      "Exclusive gold badge",
      "Priority customer support"
    ]
  }
}
```

---

## 🗺️ Location & Mapping API

### Find Nearby Charity Locations
Discover charity locations near user with gamification hotspots.

```http
GET /api/v1/locations/nearby
```

#### Query Parameters
- `lat` (float): User latitude (required)
- `lng` (float): User longitude (required)  
- `radius` (int): Search radius in meters (default: 5000, max: 50000)
- `category` (string): Filter by charity category (optional)

#### Response
```json
{
  "locations": [
    {
      "charity_id": "chr_789012345",
      "name": "Downtown Food Pantry",
      "category": "hunger_relief",
      "location": {
        "lat": 37.7849,
        "lng": -122.4094,
        "address": "123 Main Street, San Francisco, CA 94102"
      },
      "distance_meters": 847,
      "hotspot_active": true,
      "bonus_multiplier": 1.25,
      "hotspot_expires_at": "2024-01-15T18:00:00Z",
      "recent_activity": {
        "donations_today": 23,
        "total_raised_today": 1247.50
      }
    }
  ],
  "total_found": 12,
  "user_location": {
    "lat": 37.7749,
    "lng": -122.4194
  }
}
```

### Get Location Heatmap Data
Retrieve donation density data for map visualization.

```http
GET /api/v1/locations/heatmap
```

#### Query Parameters
- `bounds` (string): Map bounds in format "lat1,lng1,lat2,lng2"
- `timeframe` (string): Filter by time period (24h|7d|30d|all)

#### Response
```json
{
  "heatmap_points": [
    {
      "lat": 37.7749,
      "lng": -122.4194,
      "intensity": 0.85,
      "donation_count": 142,
      "total_amount": 7420.50
    }
  ],
  "bounds": {
    "north": 37.8349,
    "south": 37.7149, 
    "east": -122.3594,
    "west": -122.4794
  },
  "timeframe": "7d",
  "generated_at": "2024-01-15T12:30:00Z"
}
```

---

## 🤖 A2A Agent Integration API

### Invoke Donor Engagement Agent
Trigger AI agent for personalized donor engagement.

```http
POST /api/v1/agents/donor-engagement/invoke
```

#### Request Headers
```http
A2A-Protocol-Version: 0.3.0
A2A-Agent-ID: donor-engagement-agent
Content-Type: application/json
```

#### Request Body
```json
{
  "skill": "analyze_donor_profile",
  "params": {
    "user_id": "usr_123456789",
    "analysis_type": "engagement_recommendations"
  },
  "context": {
    "session_id": "sess_abc123def456",
    "user_tier": "gold",
    "recent_activity": "high"
  }
}
```

#### Response
```json
{
  "success": true,
  "execution_id": "exec_789012345",
  "result": {
    "recommendations": [
      {
        "type": "charity_match",
        "charity_id": "chr_education_501c3",
        "match_score": 0.92,
        "reason": "Based on your education-focused donation history",
        "suggested_amount": 85.00
      }
    ],
    "engagement_score": 0.78,
    "predicted_retention": 0.85,
    "next_donation_probability": 0.71
  },
  "metadata": {
    "processing_time_ms": 245,
    "model_version": "v2.1.0",
    "confidence": 0.89
  }
}
```

### Get Agent Status
Check current status of AI agents.

```http
GET /api/v1/agents/status
```

#### Response
```json
{
  "agents": [
    {
      "agent_id": "donor-engagement-agent",
      "status": "healthy",
      "version": "2.1.0",
      "last_health_check": "2024-01-15T12:45:00Z",
      "active_sessions": 23,
      "avg_response_time_ms": 187
    },
    {
      "agent_id": "charity-optimization-agent", 
      "status": "healthy",
      "version": "1.8.2",
      "last_health_check": "2024-01-15T12:45:00Z",
      "active_sessions": 8,
      "avg_response_time_ms": 312
    }
  ],
  "a2a_protocol_version": "0.3.0",
  "system_health": "operational"
}
```

---

## 📊 Analytics & Reporting API

### Get Donation Analytics
Retrieve comprehensive donation analytics.

```http
GET /api/v1/analytics/donations
```

#### Query Parameters
- `start_date` (string): Analysis start date (ISO format)
- `end_date` (string): Analysis end date (ISO format)
- `granularity` (string): hour|day|week|month (default: day)
- `charity_id` (string): Filter by charity (optional)

#### Response
```json
{
  "summary": {
    "total_donations": 1247,
    "total_amount": 62350.75,
    "average_donation": 50.04,
    "unique_donors": 823,
    "growth_rate": 0.15
  },
  "trends": [
    {
      "date": "2024-01-15",
      "donation_count": 89,
      "total_amount": 4235.50,
      "unique_donors": 67,
      "avg_donation": 47.58
    }
  ],
  "top_charities": [
    {
      "charity_id": "chr_education_501c3",
      "name": "Education Foundation",
      "donation_count": 156,
      "total_amount": 8940.25,
      "percentage_of_total": 14.34
    }
  ],
  "user_segments": {
    "new_donors": 234,
    "returning_donors": 589,
    "retention_rate": 0.72
  }
}
```

### Export Data
Generate and download comprehensive data export.

```http
POST /api/v1/analytics/export
```

#### Request Body
```json
{
  "format": "csv",
  "data_types": ["donations", "users", "achievements"],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "filters": {
    "charity_categories": ["education", "health"],
    "min_donation_amount": 25.00
  }
}
```

#### Response
```json
{
  "export_id": "exp_456789012",
  "status": "processing",
  "estimated_completion": "2024-01-15T12:55:00Z",
  "download_url": null,
  "expires_at": "2024-01-22T12:50:00Z"
}
```

---

## 🔔 WebSocket Real-Time API

### Connection
Connect to real-time updates stream.

```javascript
const ws = new WebSocket('wss://api.goodwillplatform.com/ws/user/{user_id}');

ws.onopen = function(event) {
    console.log('Connected to real-time updates');
    
    // Authenticate connection
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'your-jwt-token-here'
    }));
};
```

### Message Types

#### Donation Created
```json
{
  "type": "donation_created",
  "data": {
    "donation_id": "don_1234567890",
    "amount": 75.50,
    "points_awarded": 755,
    "tier_bonus": 113,
    "streak_multiplier": 1.5,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Achievement Unlocked
```json
{
  "type": "achievement_unlocked",
  "data": {
    "achievement_id": "streak_master",
    "name": "Streak Master",
    "points_awarded": 500,
    "badge_url": "https://cdn.platform.com/badges/streak.png",
    "rarity": "rare",
    "unlocked_at": "2024-01-15T10:30:15Z"
  }
}
```

#### Tier Progression
```json
{
  "type": "tier_progression",
  "data": {
    "old_tier": "silver",
    "new_tier": "gold", 
    "points_required": 10000,
    "current_points": 10247,
    "benefits_unlocked": [
      "20% point multiplier",
      "Exclusive gold badge",
      "Priority support"
    ],
    "progressed_at": "2024-01-15T10:30:20Z"
  }
}
```

#### Leaderboard Update
```json
{
  "type": "leaderboard_update",
  "data": {
    "old_rank": 52,
    "new_rank": 47,
    "rank_change": 5,
    "leaderboard_type": "global",
    "updated_at": "2024-01-15T10:30:25Z"
  }
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions) 
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `429` - Rate Limited
- `500` - Internal Server Error
- `503` - Service Unavailable

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid donation amount",
    "details": {
      "field": "amount",
      "constraint": "must_be_positive",
      "provided_value": -25.50
    },
    "request_id": "req_abc123def456",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Request validation failed
- `INSUFFICIENT_FUNDS` - Donation amount exceeds available balance
- `CHARITY_NOT_FOUND` - Specified charity doesn't exist
- `DUPLICATE_DONATION` - Identical donation already processed
- `RATE_LIMIT_EXCEEDED` - Too many requests from client
- `AGENT_UNAVAILABLE` - AI agent temporarily unavailable
- `GEOLOCATION_INVALID` - Invalid latitude/longitude coordinates

---

## 🔒 Rate Limiting

### Default Limits
- **Authenticated requests**: 1000 requests/hour per user
- **Donation creation**: 10 donations/minute per user
- **Leaderboard queries**: 100 requests/hour per user
- **WebSocket connections**: 5 concurrent per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1642248600
X-RateLimit-Retry-After: 3600
```

---

## 📝 Changelog

### v1.2.0 (2024-01-15)
- Added recurring donation support
- Enhanced A2A agent capabilities
- Improved WebSocket real-time updates
- New tier progression system

### v1.1.0 (2024-01-01) 
- Location-based hotspots and bonuses
- Advanced analytics and reporting
- Export functionality
- Enhanced error handling

### v1.0.0 (2023-12-01)
- Initial API release
- Core donation processing
- Basic gamification system
- User authentication and profiles

---

## 🔗 Related Resources

- [🚀 Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [🛠️ Development Setup](./DEV_SETUP.md)  
- [🔐 Security Guidelines](./SECURITY.md)
- [📊 Performance Monitoring](./MONITORING.md)
- [🤝 Contributing Guidelines](./CONTRIBUTING.md)

---

**Need help?** Contact our developer support team at `api-support@goodwillplatform.com`