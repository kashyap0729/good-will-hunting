"""
Goodwill Gym Dashboard v3.0
Pokemon Go-style gamified donation platform with interactive maps
"""

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# App configuration
st.set_page_config(
    page_title="🎮 Goodwill Gym Platform",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for Pokemon Go-style interface
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .gym-card {
        border: 3px solid #4CAF50;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        background: linear-gradient(145deg, #f0f8f0, #ffffff);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .leader-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: black;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .tier-badge {
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
    
    .bronze { background: linear-gradient(45deg, #CD7F32, #D2691E); color: white; }
    .silver { background: linear-gradient(45deg, #C0C0C0, #A8A8A8); color: black; }
    .gold { background: linear-gradient(45deg, #FFD700, #FFA500); color: black; }
    .platinum { background: linear-gradient(45deg, #E5E4E2, #B87333); color: black; }
    
    .missing-item {
        border: 2px solid #FF6B6B;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(145deg, #fff5f5, #ffffff);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
    }
    
    .achievement-unlock {
        border: 3px solid #FFD700;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: linear-gradient(145deg, #fff8dc, #ffffff);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        animation: achievement-glow 1s ease-in-out;
    }
    
    @keyframes achievement-glow {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .notification-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid;
    }
    
    .notification-achievement { border-left-color: #FFD700; background: #fff8dc; }
    .notification-streak { border-left-color: #FF6B35; background: #fff5f0; }
    .notification-gym_leader { border-left-color: #9B59B6; background: #f8f5ff; }
    .notification-missing_item { border-left-color: #E74C3C; background: #fff5f5; }
</style>
""", unsafe_allow_html=True)

def safe_api_request(endpoint: str, method: str = "GET", data: dict = None):
    """Safely make API requests with comprehensive error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error {response.status_code}: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return None, "Connection Error: Cannot connect to API. Is the backend running?"
    except requests.exceptions.Timeout:
        return None, "Timeout Error: API request took too long"
    except Exception as e:
        return None, f"Unexpected Error: {str(e)}"

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

def display_notification(notification: dict):
    """Display a notification with appropriate styling"""
    notification_type = notification.get('type', 'donation')
    icon = notification.get('icon', '💙')
    message = notification.get('message', 'Thank you!')
    
    st.markdown(f"""
    <div class="notification-card notification-{notification_type}">
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style='color: white; margin: 0;'>🎮 Goodwill Gym Platform v3.0</h1>
        <p style='color: white; margin: 0.5rem 0 0 0; opacity: 0.9;'>
            Pokemon Go-style Charitable Giving • Compete • Collect • Contribute!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API connection
    api_status, error = safe_api_request("/health")
    
    if not api_status:
        st.error(f"🚨 **Platform Offline:** {error}")
        st.info("**To start the platform:**")
        st.code("python launch_platform.py")
        st.stop()
    
    # Display API status
    with st.expander("🔧 System Status", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("API Version", api_status.get("version", "Unknown"))
        with col2:
            db_stats = api_status.get("database", {})
            st.metric("Users", db_stats.get("users", 0))
        with col3:
            st.metric("Storage Gyms", db_stats.get("storages", 0))
    
    # Sidebar - Trainer Profile
    with st.sidebar:
        st.header("👤 Trainer Profile")
        
        # Get users for selection
        users_data, error = safe_api_request("/users")
        
        if users_data:
            user_options = {f"🎯 {u['username']} ({u['tier']})": u['id'] 
                          for u in users_data}
            user_options["➕ Register New Trainer"] = "create_new"
            
            selected_option = st.selectbox(
                "Select Trainer:", 
                options=list(user_options.keys())
            )
            
            if selected_option == "➕ Register New Trainer":
                st.subheader("🎮 Trainer Registration")
                with st.form("create_user"):
                    username = st.text_input("Trainer Name*", placeholder="Enter your trainer name")
                    email = st.text_input("Email*", placeholder="your.email@example.com") 
                    full_name = st.text_input("Real Name", placeholder="Your real name (optional)")
                    
                    if st.form_submit_button("🎯 Join the Gym Network!"):
                        if username and email:
                            user_data = {
                                "username": username,
                                "email": email,
                                "full_name": full_name
                            }
                            
                            result, error = safe_api_request("/users", "POST", user_data)
                            if result:
                                st.success(f"🎉 Welcome, Trainer {username}!")
                                if 'notification' in result:
                                    display_notification(result['notification'])
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ Registration failed: {error}")
                        else:
                            st.error("Please fill in required fields (Trainer Name and Email)")
            else:
                current_user_id = user_options[selected_option]
                
                # Display current trainer profile
                user_profile, _ = safe_api_request(f"/users/{current_user_id}")
                if user_profile:
                    st.markdown("### 🎮 Active Trainer")
                    st.markdown(f"**{user_profile['username']}**")
                    display_tier_badge(user_profile['tier'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Points", f"{user_profile['total_points']:,}")
                        st.metric("Donations", user_profile['total_donations'])
                    with col2:
                        st.metric("Streak", f"{user_profile['streak_days']} days")
                        st.metric("Achievements", len(user_profile['achievements']))
        else:
            st.error("Failed to load trainers")
            st.stop()
    
    # Main content
    if 'current_user_id' in locals() and current_user_id != "create_new":
        
        # Platform Statistics
        stats_data, _ = safe_api_request("/stats")
        
        if stats_data:
            st.subheader("🌐 Platform Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Active Trainers", stats_data['total_users'])
            with col2:
                st.metric("Total Donations", stats_data['total_donations'])
            with col3:
                st.metric("Storage Gyms", stats_data['total_storages'])
            with col4:
                critical_needs = stats_data.get('critical_needs', 0)
                st.metric("Critical Needs", critical_needs, 
                         delta="⚠️ Urgent" if critical_needs > 5 else "✅ Good")
        
        # Interactive Gym Map
        st.markdown("---")
        st.subheader("🗺️ Goodwill Gym Locations")
        
        storages_data, _ = safe_api_request("/storages")
        
        if storages_data:
            # Create interactive map
            center_lat = sum(s['latitude'] for s in storages_data) / len(storages_data)
            center_lon = sum(s['longitude'] for s in storages_data) / len(storages_data)
            
            m = folium.Map(
                location=[center_lat, center_lon], 
                zoom_start=11,
                tiles='OpenStreetMap'
            )
            
            # Add gym locations
            for storage in storages_data:
                # Determine gym status
                if storage['gym_leader_username']:
                    icon_color = 'red'  # Occupied gym
                    icon_symbol = 'crown'
                    popup_html = f"""
                    <div style="width: 200px;">
                        <h4>🏛️ {storage['name']}</h4>
                        <p><strong>👑 Gym Leader:</strong> {storage['gym_leader_username']}</p>
                        <p><strong>🏆 Leader Points:</strong> {storage['gym_leader_points']:,}</p>
                        <p><strong>📍 Address:</strong> {storage['address']}</p>
                        <p><em>Challenge this leader by donating more!</em></p>
                    </div>
                    """
                else:
                    icon_color = 'green'  # Available gym
                    icon_symbol = 'star'
                    popup_html = f"""
                    <div style="width: 200px;">
                        <h4>🏛️ {storage['name']}</h4>
                        <p><strong>Status:</strong> No Leader - Open for Challenge!</p>
                        <p><strong>📍 Address:</strong> {storage['address']}</p>
                        <p><em>Be the first to claim this gym!</em></p>
                    </div>
                    """
                
                folium.Marker(
                    [storage['latitude'], storage['longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"🏛️ {storage['name']}",
                    icon=folium.Icon(color=icon_color, icon=icon_symbol, prefix='fa')
                ).add_to(m)
            
            # Display map
            map_data = st_folium(m, width=700, height=400)
            
            # Show clicked gym details
            if map_data['last_object_clicked_popup']:
                st.info("💡 **Pro Tip:** Click on gym markers to see details and challenge leaders!")
        
        else:
            st.error("Failed to load gym locations")
        
        # Missing Items Alert System
        st.markdown("---")
        st.subheader("🚨 Critical Needs Alert System")
        
        missing_items_data, _ = safe_api_request("/missing-items")
        notifications_data, _ = safe_api_request("/notifications/missing-items")
        
        if missing_items_data and len(missing_items_data) > 0:
            st.warning(f"⚠️ **{len(missing_items_data)} items urgently needed!** Extra points for these donations!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 High Priority Items")
                for item in missing_items_data[:5]:
                    shortage = item.get('shortage', 0)
                    bonus = item.get('bonus_points', 0)
                    
                    st.markdown(f"""
                    <div class="missing-item">
                        <strong>🚨 {item['item_name']}</strong><br>
                        📍 {item['storage_name']}<br>
                        📊 Need: {shortage} more items<br>
                        🎁 Bonus: +{bonus} points each!
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🤖 ADK Agent Alerts")
                if notifications_data:
                    for notification in notifications_data[:3]:
                        display_notification(notification)
        else:
            st.success("✅ All storage gyms are well-stocked! Great job, trainers!")
        
        # Donation Interface
        st.markdown("---")
        st.subheader("📦 Make a Donation")
        
        with st.form("donation_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Storage selection
                if storages_data:
                    storage_options = {f"🏛️ {s['name']}": s['id'] for s in storages_data}
                    selected_storage = st.selectbox(
                        "Choose Storage Gym:",
                        options=list(storage_options.keys())
                    )
                    storage_id = storage_options[selected_storage]
                
                # Item selection with missing items highlighted
                item_categories = [
                    "Winter Coats", "Canned Goods", "Children's Books", "Blankets",
                    "Toys", "Baby Formula", "Hygiene Kits", "School Supplies",
                    "Warm Socks", "First Aid Supplies"
                ]
                
                # Highlight missing items
                missing_item_names = [item['item_name'] for item in missing_items_data] if missing_items_data else []
                item_options = []
                for item in item_categories:
                    if item in missing_item_names:
                        item_options.append(f"🚨 {item} (HIGH DEMAND)")
                    else:
                        item_options.append(f"📦 {item}")
                
                selected_item_display = st.selectbox(
                    "Select Item to Donate:",
                    options=item_options
                )
                
                # Extract actual item name
                item_name = selected_item_display.replace("🚨 ", "").replace("📦 ", "").replace(" (HIGH DEMAND)", "")
                
                quantity = st.number_input("Quantity:", min_value=1, max_value=100, value=1)
            
            with col2:
                st.markdown("#### 🎯 Donation Preview")
                
                # Calculate estimated points
                is_high_demand = "HIGH DEMAND" in selected_item_display
                base_points = 15 if is_high_demand else 10
                estimated_points = base_points * quantity
                bonus_points = 50 * quantity if is_high_demand else 0
                total_estimated = estimated_points + bonus_points
                
                if is_high_demand:
                    st.markdown("""
                    <div class="missing-item">
                        <strong>🎯 HIGH DEMAND ITEM!</strong><br>
                        This item is urgently needed!<br>
                        You'll get extra bonus points!
                    </div>
                    """, unsafe_allow_html=True)
                
                st.info(f"""
                **Points Breakdown:**
                - Base Points: {estimated_points}
                - Bonus Points: {bonus_points}
                - **Total: {total_estimated} points** 🎯
                """)
                
                if user_profile:
                    st.success(f"Current Points: {user_profile['total_points']:,}")
            
            submitted = st.form_submit_button("🎮 Donate Now!", type="primary", use_container_width=True)
            
            if submitted:
                donation_data = {
                    "user_id": current_user_id,
                    "storage_id": storage_id,
                    "item_name": item_name,
                    "quantity": quantity
                }
                
                result, error = safe_api_request("/donate", "POST", donation_data)
                
                if result:
                    # Success with notification
                    st.markdown("""
                    <div class="achievement-unlock">
                        <h3>🎉 Donation Successful!</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Points Awarded", result['points_awarded'])
                    with col2:
                        st.metric("Bonus Points", result['bonus_points'])
                    with col3:
                        st.metric("Missing Item Bonus", "Yes!" if result['missing_item_bonus'] else "No")
                    
                    # Display notification
                    if 'notification' in result:
                        display_notification(result['notification'])
                    
                    if result.get('tier_upgraded'):
                        st.balloons()
                        st.success("🏆 TIER UPGRADE! You've reached a new level!")
                    
                    # Auto-refresh after successful donation
                    time.sleep(3)
                    st.rerun()
                    
                else:
                    st.error(f"❌ Donation failed: {error}")
        
        # Leaderboard and Statistics
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Gym Leaders Leaderboard")
            
            leaderboard_data, _ = safe_api_request("/leaderboard?limit=10")
            
            if leaderboard_data:
                for i, entry in enumerate(leaderboard_data[:5]):
                    rank_emoji = ["👑", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                    
                    is_current_user = entry['user_id'] == current_user_id
                    style = "background: linear-gradient(90deg, #FFD700, #FFA500); padding: 0.5rem; border-radius: 8px;" if is_current_user else ""
                    
                    st.markdown(f"""
                    <div style="{style}">
                        <strong>{rank_emoji} #{entry['rank']} {entry['username']}</strong><br>
                        🏆 {entry['total_points']:,} points • 🔥 {entry['streak_days']} day streak<br>
                        <small>{entry['tier'].title()} Tier • {entry['total_donations']} donations</small>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
        
        with col2:
            st.subheader("📊 Your Stats")
            
            if user_profile:
                # Points chart (mock data for demonstration)
                days = list(range(1, 8))
                points = [100, 150, 200, 180, 250, 300, user_profile['total_points'] % 400 + 200]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=days,
                    y=points,
                    mode='lines+markers',
                    name='Daily Points',
                    line=dict(color='#4CAF50', width=3),
                    marker=dict(size=8, color='#4CAF50')
                ))
                
                fig.update_layout(
                    title="📈 Points Progress (Last 7 Days)",
                    xaxis_title="Days",
                    yaxis_title="Points",
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Achievement progress
                st.markdown("#### 🎖️ Achievements")
                achievement_names = [
                    "First Steps", "Generous Giver", "Streak Master", 
                    "Gym Leader", "Champion Donor"
                ]
                
                unlocked = len(user_profile['achievements'])
                total = len(achievement_names)
                progress = unlocked / total if total > 0 else 0
                
                st.progress(progress, text=f"Achievements: {unlocked}/{total}")
                
                for i, achievement in enumerate(achievement_names):
                    if i < unlocked:
                        st.markdown(f"✅ {achievement}")
                    else:
                        st.markdown(f"🔒 {achievement}")
    
    else:
        # Welcome screen for new users
        st.markdown("""
        ## 🎮 Welcome to Goodwill Gym!
        
        **Join the Pokemon Go-style charitable giving adventure!**
        
        ### How to Play:
        1. 📝 **Register** as a trainer in the sidebar
        2. 🗺️ **Explore** gym locations on the interactive map  
        3. 📦 **Donate** items to earn points and challenge gym leaders
        4. 🏆 **Compete** to become the top trainer at each location
        5. 🎯 **Help** by donating high-demand items for bonus points!
        
        ### Features:
        - 🎪 **Pokemon Go-style gym system**
        - 🤖 **Google ADK notification agent** 
        - 💾 **Persistent progress** with SQLite database
        - 🗺️ **Real Los Angeles locations** on interactive maps
        - 🚨 **Missing items alerts** with bonus point rewards
        - 👑 **Gym leader competition** system
        
        **Ready to make a difference? Register now! →**
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-top: 2rem;'>
        <h4 style='color: white; margin: 0;'>🎮 Goodwill Gym Platform v3.0</h4>
        <p style='color: white; margin: 0.5rem 0 0 0; opacity: 0.9;'>
            <strong>Pokemon Go-style Charity</strong> • <strong>SQLite Database</strong> • <strong>Google ADK Notifications</strong>
        </p>
        <p style='color: white; margin: 0.5rem 0 0 0; opacity: 0.8; font-size: 0.9rem;'>
            Built with ❤️ using FastAPI + Streamlit + Folium Maps
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()