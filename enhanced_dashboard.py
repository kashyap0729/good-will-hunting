"""
Enhanced Streamlit Dashboard for Goodwill Platform
Advanced gamified interface with all new backend features
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# App configuration
st.set_page_config(
    page_title="🎮 Goodwill Gaming Platform v2.0",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .achievement-card {
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        background: linear-gradient(145deg, #f0f0f0, #ffffff);
    }
    .tier-badge {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.2rem;
    }
    .bronze { background-color: #CD7F32; color: white; }
    .silver { background-color: #C0C0C0; color: black; }
    .gold { background-color: #FFD700; color: black; }
    .platinum { background-color: #E5E4E2; color: black; border: 2px solid #B87333; }
</style>
""", unsafe_allow_html=True)

def safe_api_request(endpoint: str, method: str = "GET", data: dict = None):
    """Safely make API requests with error handling"""
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=5)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code}"
    except Exception as e:
        return None, f"Connection Error: {str(e)}"

def display_tier_badge(tier: str):
    """Display a styled tier badge"""
    tier_class = tier.lower()
    tier_icons = {
        "bronze": "🥉",
        "silver": "🥈", 
        "gold": "🥇",
        "platinum": "💎"
    }
    icon = tier_icons.get(tier.lower(), "🏅")
    
    st.markdown(f"""
    <span class="tier-badge {tier_class}">
        {icon} {tier.upper()}
    </span>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style='color: white; text-align: center; margin: 0;'>
            🎮 Goodwill Gaming Platform v2.0
        </h1>
        <p style='color: white; text-align: center; margin: 0.5rem 0 0 0;'>
            Advanced Gamified Charitable Giving Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API connection
    api_status, error = safe_api_request("/health")
    
    if api_status:
        st.success("🚀 Enhanced API v2.0 Connected! All systems operational.")
        
        # Display API info
        with st.expander("🔧 API Status Details"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Version", api_status.get("version", "Unknown"))
            with col2:
                st.metric("Database", api_status.get("database", "Unknown"))
            with col3:
                st.metric("Status", "✅ Healthy")
        
    else:
        st.error(f"⚠️ API Connection Failed: {error}")
        st.info("Start the enhanced API with: `python enhanced_backend.py`")
        return
    
    # Sidebar - User Management
    with st.sidebar:
        st.header("👤 User Management")
        
        # User selection/creation
        users_data, _ = safe_api_request("/users")
        
        if users_data:
            user_options = {f"{u['username']} ({u['tier']})": u['user_id'] 
                          for u in users_data}
            user_options["➕ Create New User"] = "create_new"
            
            selected_user = st.selectbox(
                "Select User:", 
                options=list(user_options.keys())
            )
            
            if selected_user == "➕ Create New User":
                st.subheader("Create New User")
                with st.form("create_user"):
                    username = st.text_input("Username*")
                    email = st.text_input("Email*") 
                    full_name = st.text_input("Full Name")
                    causes = st.multiselect(
                        "Preferred Causes",
                        ["Education", "Healthcare", "Environment", "Poverty", "Animals", "Disaster Relief"]
                    )
                    
                    if st.form_submit_button("Create User"):
                        user_data = {
                            "username": username,
                            "email": email,
                            "full_name": full_name,
                            "preferred_causes": causes
                        }
                        
                        result, error = safe_api_request("/users", "POST", user_data)
                        if result:
                            st.success(f"✅ User {username} created!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to create user: {error}")
            else:
                current_user_id = user_options[selected_user]
                
                # Display current user profile
                user_profile, _ = safe_api_request(f"/users/{current_user_id}")
                if user_profile:
                    st.subheader(f"👤 {user_profile['username']}")
                    display_tier_badge(user_profile['tier'])
                    st.metric("Total Points", f"{user_profile['total_points']:,}")
                    st.metric("Streak", f"{user_profile['streak_days']} days")
                    st.metric("Total Donated", f"${user_profile['total_amount']:,.2f}")
        else:
            st.info("No users found. Create your first user!")
    
    # Main Dashboard
    if 'current_user_id' in locals():
        # Stats Overview
        stats_data, _ = safe_api_request("/stats")
        
        if stats_data:
            st.subheader("📊 Platform Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Total Donations", 
                    stats_data['total_donations'],
                    delta=f"+{stats_data['total_donations'] - 10} from last month"
                )
            with col2:
                st.metric(
                    "Total Amount", 
                    f"${stats_data['total_amount']:,.2f}",
                    delta=f"${stats_data['average_donation']:.0f} avg"
                )
            with col3:
                st.metric(
                    "Active Users", 
                    stats_data['active_users'],
                    delta=f"+{stats_data['active_users'] - stats_data['total_users']+5} new"
                )
            with col4:
                st.metric(
                    "Average Donation", 
                    f"${stats_data['average_donation']:,.2f}",
                    delta="5.2% increase"
                )
        
        # Enhanced Donation Form
        st.markdown("---")
        st.subheader("💖 Make a Donation")
        
        with st.form("enhanced_donation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input(
                    "Donation Amount ($)", 
                    min_value=1.0, 
                    value=50.0, 
                    step=5.0,
                    help="Minimum $1.00 donation"
                )
                
                donation_type = st.selectbox(
                    "Donation Type", 
                    ["monetary", "crypto", "goods", "time"],
                    help="Different types earn different point multipliers"
                )
                
                charity_category = st.selectbox(
                    "Charity Category",
                    ["Education", "Healthcare", "Environment", "Poverty", "Animals", "Disaster Relief", "Other"]
                )
            
            with col2:
                message = st.text_area(
                    "Message (Optional)", 
                    placeholder="Share why this cause matters to you...",
                    max_chars=500
                )
                
                is_anonymous = st.checkbox("Make this donation anonymous")
                
                # Points preview
                if 'user_profile' in locals():
                    base_points = int(amount * 10)
                    tier_multipliers = {"bronze": 1.0, "silver": 1.25, "gold": 1.5, "platinum": 2.0}
                    type_bonuses = {"monetary": 1.0, "crypto": 1.5, "goods": 1.2, "time": 2.0}
                    
                    tier_mult = tier_multipliers.get(user_profile['tier'], 1.0)
                    type_mult = type_bonuses.get(donation_type, 1.0)
                    streak_bonus = min(user_profile['streak_days'] * 50, 500)
                    
                    estimated_points = int(base_points * tier_mult * type_mult) + streak_bonus
                    
                    st.info(f"""
                    **Points Preview:**
                    - Base: {base_points} points
                    - Tier Bonus ({user_profile['tier']}): +{int((tier_mult-1)*100)}%
                    - Type Bonus ({donation_type}): +{int((type_mult-1)*100)}%
                    - Streak Bonus: +{streak_bonus} points
                    
                    **Total Estimated: {estimated_points:,} points** 🎯
                    """)
            
            submitted = st.form_submit_button("🎮 Donate & Earn Points!", type="primary")
            
            if submitted and 'current_user_id' in locals():
                donation_data = {
                    "user_id": current_user_id,
                    "amount": amount,
                    "donation_type": donation_type,
                    "message": message,
                    "charity_category": charity_category,
                    "is_anonymous": is_anonymous
                }
                
                result, error = safe_api_request("/donations", "POST", donation_data)
                
                if result:
                    st.success(f"""
                    🎉 **Donation Successful!**
                    
                    **Donation ID:** {result['donation_id'][:8]}...
                    **Amount:** ${result['amount']:.2f}
                    **Points Earned:** {result['points_awarded']:,} 🏆
                    **Bonus Points:** {result['bonus_points']:,}
                    **Tier Multiplier:** {result['tier_multiplier']:.2f}x
                    
                    Thank you for your generosity! 🌟
                    """)
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ Donation failed: {error}")
    
    # Enhanced Analytics Section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Live Leaderboard")
        
        leaderboard_data, _ = safe_api_request("/leaderboard?limit=10")
        
        if leaderboard_data:
            leaderboard = leaderboard_data['leaderboard']
            
            for i, user in enumerate(leaderboard[:5]):
                rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                
                with st.container():
                    col_rank, col_user, col_points = st.columns([1, 3, 2])
                    
                    with col_rank:
                        st.markdown(f"### {rank_emoji}")
                    
                    with col_user:
                        st.markdown(f"""
                        **{user['username']}**  
                        {user['tier'].title()} Tier • {user['streak_days']} day streak
                        """)
                    
                    with col_points:
                        st.metric("Points", f"{user['points']:,}")
                
                st.markdown("---")
        
        else:
            st.info("Loading leaderboard...")
    
    with col2:
        st.subheader("🎯 Achievements System")
        
        achievements_data, _ = safe_api_request("/achievements")
        
        if achievements_data and 'current_user_id' in locals():
            # Get user-specific achievements
            user_achievements, _ = safe_api_request(f"/achievements?user_id={current_user_id}")
            
            if user_achievements:
                achievements = user_achievements['achievements']
                unlocked_count = user_achievements['total_unlocked']
                total_count = user_achievements['total_available']
                
                # Progress bar
                progress = unlocked_count / total_count if total_count > 0 else 0
                st.progress(progress, text=f"Achievements: {unlocked_count}/{total_count}")
                
                # Achievement cards
                for achievement in achievements[:6]:  # Show first 6
                    if achievement['unlocked']:
                        st.markdown(f"""
                        <div class="achievement-card">
                            <strong>{achievement['icon']} {achievement['name']}</strong><br>
                            <small>{achievement['description']}</small><br>
                            <span style="color: green;">✅ Unlocked! +{achievement['points_reward']} points</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="border: 1px solid #ddd; padding: 1rem; margin: 0.5rem; border-radius: 10px; opacity: 0.6;">
                            <strong>🔒 {achievement['name']}</strong><br>
                            <small>{achievement['description']}</small><br>
                            <span style="color: gray;">Reward: {achievement['points_reward']} points</span>
                        </div>
                        """, unsafe_allow_html=True)
        
        else:
            # Show general achievements catalog
            if achievements_data:
                for achievement in achievements_data['achievements'][:4]:
                    st.markdown(f"""
                    **{achievement['icon']} {achievement['name']}**  
                    {achievement['description']}  
                    *Reward: {achievement['points_reward']} points*
                    """)
                    st.markdown("---")
    
    # Tier Distribution Chart
    st.markdown("---")
    st.subheader("📈 Tier Distribution & Trends")
    
    if stats_data:
        col1, col2 = st.columns(2)
        
        with col1:
            # Tier distribution pie chart
            tier_dist = stats_data['tier_distribution']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(tier_dist.keys()),
                values=list(tier_dist.values()),
                hole=.3,
                marker_colors=['#CD7F32', '#C0C0C0', '#FFD700', '#E5E4E2']
            )])
            
            fig_pie.update_layout(
                title="User Tier Distribution",
                height=300,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Recent donations trend (mock data)
            days = [f"Day {i+1}" for i in range(7)]
            donations = [45, 52, 38, 61, 72, 55, 68]  # Mock data
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=days,
                y=donations,
                mode='lines+markers',
                name='Daily Donations',
                line=dict(color='#4ECDC4', width=3),
                marker=dict(size=8)
            ))
            
            fig_trend.update_layout(
                title="Recent Donation Trends",
                xaxis_title="Time Period",
                yaxis_title="Number of Donations",
                height=300
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h4>🎮 Goodwill Gaming Platform v2.0</h4>
        <p><strong>Enhanced Backend</strong> • <strong>Advanced Gamification</strong> • <strong>Real-time Analytics</strong></p>
        <p>Built with ❤️ using FastAPI + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()