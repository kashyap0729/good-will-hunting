"""
Streamlit Dashboard - Main Application
Multi-page dashboard with real-time metrics, achievements, and interactive maps
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import time
import numpy as np
from typing import Dict, List, Optional
import requests

# Page configuration
st.set_page_config(
    page_title="Donation Platform Dashboard",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for gamification UI
st.markdown("""
<style>
.achievement-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 12px;
    color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin: 10px 0;
    text-align: center;
}

.tier-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: bold;
    margin: 5px;
    color: white;
}

.bronze { background: #CD7F32; }
.silver { background: #C0C0C0; color: black; }
.gold { background: #FFD700; color: black; }
.platinum { background: #E5E4E2; color: black; }
.diamond { background: #B9F2FF; color: black; }

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
}

.leaderboard-entry {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    margin: 5px 0;
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.pulse {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.notification-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #28a745;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}
</style>
""", unsafe_allow_html=True)

class APIClient:
    """Client for communicating with backend services"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": "Bearer demo-token",
            "Content-Type": "application/json"
        })
    
    def get_donations_today(self) -> Dict:
        """Get today's donation metrics"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/analytics/donations/today")
            if response.status_code == 200:
                return response.json()
            return {"amount": 12450.75, "count": 156, "change": 15.3}
        except:
            # Fallback data
            return {"amount": 12450.75, "count": 156, "change": 15.3}
    
    def get_active_donors(self) -> Dict:
        """Get active donor metrics"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/analytics/donors/active")
            if response.status_code == 200:
                return response.json()
            return {"count": 1250, "new_today": 28}
        except:
            return {"count": 1250, "new_today": 28}
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get leaderboard data"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/leaderboard/global?limit={limit}")
            if response.status_code == 200:
                return response.json().get("leaderboard", [])
        except:
            pass
        
        # Fallback data
        return [
            {"name": "Sarah Johnson", "points": 15420, "tier": "Diamond", "total_donated": 2850.00, "rank": 1},
            {"name": "Michael Chen", "points": 12380, "tier": "Platinum", "total_donated": 2100.00, "rank": 2},
            {"name": "Emma Wilson", "points": 9750, "tier": "Gold", "total_donated": 1650.00, "rank": 3},
            {"name": "David Martinez", "points": 8200, "tier": "Gold", "total_donated": 1400.00, "rank": 4},
            {"name": "Lisa Thompson", "points": 6850, "tier": "Silver", "total_donated": 1150.00, "rank": 5},
            {"name": "James Brown", "points": 5420, "tier": "Silver", "total_donated": 950.00, "rank": 6},
            {"name": "Anna Garcia", "points": 4200, "tier": "Bronze", "total_donated": 780.00, "rank": 7},
            {"name": "Robert Davis", "points": 3850, "tier": "Bronze", "total_donated": 650.00, "rank": 8},
            {"name": "Maria Rodriguez", "points": 3200, "tier": "Bronze", "total_donated": 520.00, "rank": 9},
            {"name": "John Smith", "points": 2750, "tier": "Bronze", "total_donated": 450.00, "rank": 10}
        ]
    
    def get_nearby_hotspots(self) -> List[Dict]:
        """Get nearby donation hotspots"""
        # Simulated hotspot data
        return [
            {
                "lat": 37.7849, "lng": -122.4094, 
                "name": "Downtown Community Center",
                "activity_level": 8, "points_multiplier": 2.0,
                "organization": "SF Community Aid"
            },
            {
                "lat": 37.7649, "lng": -122.4294,
                "name": "Mission District Hub", 
                "activity_level": 6, "points_multiplier": 1.5,
                "organization": "Mission Helpers"
            },
            {
                "lat": 37.7949, "lng": -122.3994,
                "name": "Chinatown Cultural Center",
                "activity_level": 7, "points_multiplier": 1.8,
                "organization": "Chinatown Outreach"
            },
            {
                "lat": 37.7549, "lng": -122.4494,
                "name": "Castro Support Center",
                "activity_level": 5, "points_multiplier": 1.3,
                "organization": "Castro Community"
            }
        ]
    
    def get_user_achievements(self, user_id: str = "demo_user") -> List[Dict]:
        """Get user achievements"""
        return [
            {
                "emoji": "🎉",
                "name": "First Steps",
                "description": "Made your first donation",
                "points": 500,
                "unlocked_at": "2025-09-20T10:30:00Z"
            },
            {
                "emoji": "🏆", 
                "name": "Generous Giver",
                "description": "Donated $100+ in single donation",
                "points": 1000,
                "unlocked_at": "2025-09-22T14:15:00Z"
            },
            {
                "emoji": "🗺️",
                "name": "Location Explorer", 
                "description": "Donated to 5 different locations",
                "points": 750,
                "unlocked_at": "2025-09-25T16:45:00Z"
            },
            {
                "emoji": "🔥",
                "name": "Week Warrior",
                "description": "Donated every day for a week", 
                "points": 800,
                "unlocked_at": "2025-09-27T09:20:00Z"
            }
        ]

class DonationDashboard:
    """Main dashboard class"""
    
    def __init__(self):
        self.api_client = APIClient()
        self.init_session_state()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {
                'name': 'John Doe',
                'tier': 'Gold',
                'total_points': 8200,
                'leaderboard_position': 4,
                'donation_streak': 15,
                'total_donated': 1400.00
            }
        if 'refresh_counter' not in st.session_state:
            st.session_state.refresh_counter = 0
            
    def render_main_dashboard(self):
        """Main dashboard with real-time metrics"""
        
        # Auto-refresh setup
        placeholder = st.empty()
        
        with placeholder.container():
            # Header with user tier
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.title("🎮 Gamified Donation Dashboard")
                
            with col2:
                user_tier = st.session_state.user_data.get('tier', 'Bronze')
                st.markdown(f'<span class="tier-badge {user_tier.lower()}">{user_tier} Tier</span>', 
                           unsafe_allow_html=True)
                
            with col3:
                points = st.session_state.user_data.get('total_points', 0)
                st.metric("Your Points", f"{points:,}")
            
            with col4:
                if st.button("🔄 Refresh", key="refresh_btn"):
                    st.session_state.refresh_counter += 1
                    st.rerun()
            
            # Real-time metrics row
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                donations_today = self.api_client.get_donations_today()
                st.metric(
                    "Donations Today",
                    f"${donations_today['amount']:,.2f}",
                    delta=f"+{donations_today['change']:.1f}%"
                )
                
            with metrics_col2:
                active_donors = self.api_client.get_active_donors()
                st.metric(
                    "Active Donors",
                    f"{active_donors['count']:,}",
                    delta=f"+{active_donors['new_today']}"
                )
                
            with metrics_col3:
                leaderboard_position = st.session_state.user_data.get('leaderboard_position', 0)
                st.metric(
                    "Your Rank",
                    f"#{leaderboard_position}",
                    delta="↑2" if leaderboard_position < 50 else "↓1"
                )
                
            with metrics_col4:
                streak = st.session_state.user_data.get('donation_streak', 0)
                st.metric(
                    "Donation Streak",
                    f"{streak} days",
                    delta="🔥" if streak > 7 else ""
                )
    
    def render_gamification_section(self):
        """Gamification elements with achievements"""
        
        st.subheader("🏆 Achievements & Progress")
        
        # Progress to next tier
        current_points = st.session_state.user_data.get('total_points', 0)
        next_tier_points = self.get_next_tier_requirement(current_points)
        progress = (current_points % 5000) / 5000  # Assuming 5000 points per tier
        
        st.progress(progress, text=f"{current_points:,} / {next_tier_points:,} points to next tier")
        
        # Recent achievements
        achievements = self.api_client.get_user_achievements()
        
        # Display achievements in columns
        if achievements:
            cols = st.columns(min(len(achievements), 4))
            for col, achievement in zip(cols, achievements[:4]):
                with col:
                    st.markdown(f"""
                    <div class="achievement-card">
                        <h3>{achievement['emoji']}</h3>
                        <p><strong>{achievement['name']}</strong></p>
                        <small>+{achievement['points']} points</small>
                        <br><small>{achievement['description']}</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    def render_interactive_map(self):
        """Render donation hotspot map with Plotly"""
        
        st.subheader("📍 Donation Hotspots Near You")
        
        # Get hotspot data
        hotspots_data = self.api_client.get_nearby_hotspots()
        
        if hotspots_data:
            # Create DataFrame
            df = pd.DataFrame(hotspots_data)
            
            # Create Plotly map
            fig = go.Figure()
            
            # Add hotspot markers
            fig.add_trace(go.Scattermapbox(
                mode='markers+text',
                lon=df['lng'],
                lat=df['lat'],
                marker=dict(
                    size=[h['activity_level'] * 5 for h in hotspots_data],
                    color=[h['points_multiplier'] for h in hotspots_data],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Points Multiplier")
                ),
                text=[f"{h['name']}<br>Multiplier: {h['points_multiplier']}x" 
                      for h in hotspots_data],
                textposition='top center',
                hovertemplate="<b>%{text}</b><br>" +
                             "Organization: %{customdata[0]}<br>" +
                             "Activity Level: %{customdata[1]}/10<extra></extra>",
                customdata=[[h['organization'], h['activity_level']] for h in hotspots_data],
                name="Hotspots"
            ))
            
            # Update layout
            fig.update_layout(
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=37.7749, lon=-122.4194),
                    zoom=12
                ),
                height=500,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Hotspot details
            with st.expander("🔍 Hotspot Details"):
                for hotspot in hotspots_data:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{hotspot['name']}**")
                    with col2:
                        st.write(f"Multiplier: {hotspot['points_multiplier']}x")
                    with col3:
                        st.write(f"Activity: {hotspot['activity_level']}/10")
    
    def render_leaderboard(self):
        """Live leaderboard with animations"""
        
        st.subheader("🏅 Live Leaderboard")
        
        leaderboard_data = self.api_client.get_leaderboard(20)
        
        # Display top 3 with special formatting
        if len(leaderboard_data) >= 3:
            st.markdown("### 🏆 Top 3 Champions")
            medal_cols = st.columns(3)
            
            medals = ["🥇", "🥈", "🥉"]
            colors = ["gold", "silver", "#CD7F32"]
            
            for i, (col, user) in enumerate(zip(medal_cols, leaderboard_data[:3])):
                with col:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, {colors[i]}22, {colors[i]}44); border-radius: 10px; margin: 10px 0;">
                        <h2>{medals[i]}</h2>
                        <h3>{user['name']}</h3>
                        <p><span class="tier-badge {user['tier'].lower()}">{user['tier']}</span></p>
                        <p><strong>{user['points']:,} points</strong></p>
                        <p>${user['total_donated']:,.0f} donated</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Rest of leaderboard
        if len(leaderboard_data) > 3:
            st.markdown("### 📊 Full Leaderboard")
            
            # Create DataFrame for display
            df_leaderboard = pd.DataFrame(leaderboard_data[3:])
            
            # Display as interactive table
            for idx, user in enumerate(leaderboard_data[3:], 4):
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**#{idx}**")
                with col2:
                    st.markdown(f"**{user['name']}**")
                with col3:
                    st.markdown(f'<span class="tier-badge {user["tier"].lower()}">{user["tier"]}</span>', 
                               unsafe_allow_html=True)
                with col4:
                    st.markdown(f"**{user['points']:,}** pts")
                with col5:
                    st.markdown(f"${user['total_donated']:,.0f}")
                
                st.divider()
    
    def render_analytics_charts(self):
        """Advanced analytics and charts"""
        
        st.subheader("📊 Analytics Dashboard")
        
        # Generate sample data for charts
        dates = pd.date_range(start='2025-09-01', end='2025-09-27', freq='D')
        
        # Donation trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Daily Donations")
            
            # Generate realistic donation data with trend
            base_donations = 100 + np.random.normal(0, 20, len(dates))
            trend = np.linspace(0, 50, len(dates))  # Upward trend
            seasonal = 30 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)  # Weekly pattern
            donations = base_donations + trend + seasonal
            donations = np.maximum(donations, 0)
            
            df_donations = pd.DataFrame({
                'Date': dates,
                'Donations': donations
            })
            
            fig_donations = px.line(df_donations, x='Date', y='Donations',
                                   title="Daily Donation Trend")
            fig_donations.update_traces(line_color='#667eea')
            st.plotly_chart(fig_donations, use_container_width=True)
        
        with col2:
            st.markdown("#### 👥 User Engagement")
            
            # Generate engagement data
            active_users = 50 + np.random.normal(0, 10, len(dates))
            active_users = np.maximum(active_users, 0)
            
            df_users = pd.DataFrame({
                'Date': dates,
                'Active_Users': active_users
            })
            
            fig_users = px.area(df_users, x='Date', y='Active_Users',
                               title="Daily Active Users")
            fig_users.update_traces(fill='tonexty', fillcolor='rgba(46, 204, 113, 0.3)')
            st.plotly_chart(fig_users, use_container_width=True)
        
        # Tier distribution
        st.markdown("#### 🏆 Tier Distribution")
        
        tier_data = {
            'Tier': ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond'],
            'Count': [450, 250, 200, 80, 20],
            'Percentage': [45, 25, 20, 8, 2]
        }
        
        df_tiers = pd.DataFrame(tier_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(df_tiers, values='Count', names='Tier',
                           title="User Distribution by Tier",
                           color_discrete_map={
                               'Bronze': '#CD7F32',
                               'Silver': '#C0C0C0', 
                               'Gold': '#FFD700',
                               'Platinum': '#E5E4E2',
                               'Diamond': '#B9F2FF'
                           })
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(df_tiers, x='Tier', y='Count',
                           title="Users per Tier",
                           color='Tier',
                           color_discrete_map={
                               'Bronze': '#CD7F32',
                               'Silver': '#C0C0C0', 
                               'Gold': '#FFD700',
                               'Platinum': '#E5E4E2',
                               'Diamond': '#B9F2FF'
                           })
            st.plotly_chart(fig_bar, use_container_width=True)
    
    def render_recent_activity(self):
        """Recent donation activity feed"""
        
        st.subheader("🔄 Recent Activity")
        
        # Generate sample recent activities
        activities = [
            {"user": "Sarah J.", "action": "donated $75", "location": "Downtown Center", "time": "2 minutes ago", "points": 150},
            {"user": "Mike C.", "action": "unlocked achievement", "location": "Mission Hub", "time": "5 minutes ago", "points": 500},
            {"user": "Emma W.", "action": "donated items", "location": "Castro Center", "time": "8 minutes ago", "points": 120},
            {"user": "David M.", "action": "reached Gold tier", "location": "Chinatown", "time": "15 minutes ago", "points": 0},
            {"user": "Lisa T.", "action": "donated $50", "location": "Downtown Center", "time": "23 minutes ago", "points": 100},
        ]
        
        for activity in activities:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.write(f"**{activity['user']}** {activity['action']}")
            with col2:
                st.write(f"📍 {activity['location']}")
            with col3:
                st.write(f"⏰ {activity['time']}")
            with col4:
                if activity['points'] > 0:
                    st.write(f"⭐ +{activity['points']}")
            
            st.divider()
    
    def get_next_tier_requirement(self, current_points: int) -> int:
        """Calculate points needed for next tier"""
        tier_thresholds = [0, 1000, 5000, 15000, 50000]
        
        for threshold in tier_thresholds:
            if current_points < threshold:
                return threshold
        
        return tier_thresholds[-1]  # Max tier reached

# WebSocket simulation for real-time updates
def simulate_realtime_updates():
    """Simulate real-time updates"""
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
    
    # Update every 30 seconds
    if time.time() - st.session_state.last_update > 30:
        # Simulate new donation
        st.session_state.user_data['total_points'] += np.random.randint(50, 200)
        st.session_state.last_update = time.time()
        
        # Show notification
        st.success("🎉 New donation received! +150 points")

def main():
    """Main application"""
    
    # Initialize dashboard
    dashboard = DonationDashboard()
    
    # Sidebar navigation
    st.sidebar.title("🎮 Navigation")
    
    page = st.sidebar.selectbox("Choose a page:", [
        "🏠 Dashboard Home",
        "🏆 Achievements", 
        "📍 Map & Hotspots",
        "🏅 Leaderboard",
        "📊 Analytics",
        "🔄 Recent Activity"
    ])
    
    # User profile in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Your Profile")
        user_data = st.session_state.user_data
        
        st.markdown(f"**Name:** {user_data['name']}")
        st.markdown(f"**Tier:** {user_data['tier']}")
        st.markdown(f"**Points:** {user_data['total_points']:,}")
        st.markdown(f"**Rank:** #{user_data['leaderboard_position']}")
        st.markdown(f"**Streak:** {user_data['donation_streak']} days")
        st.markdown(f"**Total Donated:** ${user_data['total_donated']:,.2f}")
        
        # Progress bar for next tier
        progress = (user_data['total_points'] % 5000) / 5000
        st.progress(progress, text="Progress to next tier")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🎁 Make Donation"):
            st.success("Redirecting to donation page...")
        if st.button("📱 Share Achievement"):
            st.success("Shared to social media!")
        if st.button("🗺️ Find Nearby"):
            st.success("Finding nearby hotspots...")
    
    # Main content based on selected page
    if page == "🏠 Dashboard Home":
        dashboard.render_main_dashboard()
        dashboard.render_gamification_section()
        
    elif page == "🏆 Achievements":
        st.title("🏆 Achievements")
        dashboard.render_gamification_section()
        
        # All achievements
        st.subheader("📋 All Available Achievements")
        all_achievements = dashboard.api_client.get_user_achievements()
        
        for achievement in all_achievements:
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.markdown(f"## {achievement['emoji']}")
            with col2:
                st.markdown(f"**{achievement['name']}**")
                st.markdown(achievement['description'])
                st.markdown(f"*Unlocked: {achievement['unlocked_at'][:10]}*")
            with col3:
                st.markdown(f"**+{achievement['points']}**")
            st.divider()
        
    elif page == "📍 Map & Hotspots":
        st.title("📍 Interactive Donation Map")
        dashboard.render_interactive_map()
        
    elif page == "🏅 Leaderboard":
        st.title("🏅 Live Leaderboard")
        dashboard.render_leaderboard()
        
    elif page == "📊 Analytics":
        st.title("📊 Platform Analytics")
        dashboard.render_analytics_charts()
        
    elif page == "🔄 Recent Activity":
        st.title("🔄 Recent Activity Feed")
        dashboard.render_recent_activity()
    
    # Real-time updates simulation
    simulate_realtime_updates()
    
    # Auto-refresh every minute
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True
    
    if st.session_state.auto_refresh:
        # Placeholder for auto-refresh (in production, use WebSocket)
        time.sleep(0.1)

if __name__ == "__main__":
    main()