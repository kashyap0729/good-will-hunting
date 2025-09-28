"""
Dashboard - All UI Features with Performance Optimizations
- Session state caching
- Reduced API calls
- Faster map rendering
- Keeps: Maps showing leaders, Leaderboard, User profiles
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
    page_title=" Goodwill Gym",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Session state for caching
if 'users_cache' not in st.session_state:
    st.session_state.users_cache = None
if 'storages_cache' not in st.session_state:
    st.session_state.storages_cache = None
if 'stats_cache' not in st.session_state:
    st.session_state.stats_cache = None
if 'cache_time' not in st.session_state:
    st.session_state.cache_time = 0

# Cache timeout (30 seconds)
CACHE_TIMEOUT = 30

# Custom CSS (simplified for faster loading)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .gym-card {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        color: #212529;
    }
    
    .tier-badge {
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        margin: 0.1rem;
    }
    
    .bronze { background: #CD7F32; color: white; }
    .silver { background: #C0C0C0; color: black; }
    .gold { background: #FFD700; color: black; }
    .platinum { background: #E5E4E2; color: black; }
    
    .missing-item {
        border: 2px solid #FF6B6B;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        background: #fff5f5;
        color: #212529;
    }
    
    .notification-card {
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        border-left: 4px solid;
        color: #212529;
    }
    
    .notification-missing_item { border-left-color: #E74C3C; background: #fff5f5; color: #212529; }
</style>
""", unsafe_allow_html=True)

def fast_api_request(endpoint: str, method: str = "GET", data: dict = None, use_cache: bool = True):
    """API requests with caching and short timeouts"""
    
    # Check cache first for GET requests
    if method == "GET" and use_cache:
        cache_key = f"{endpoint}_cache"
        if cache_key in st.session_state:
            cache_data = st.session_state[cache_key]
            if time.time() - cache_data['timestamp'] < CACHE_TIMEOUT:
                return cache_data['data'], None
    
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=3)  # Short timeout for speed
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            
            # Cache successful GET requests
            if method == "GET" and use_cache:
                st.session_state[f"{endpoint}_cache"] = {
                    'data': result,
                    'timestamp': time.time()
                }
            
            return result, None
        else:
            return None, f"API Error {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return None, "Connection Error: Backend not running"
    except requests.exceptions.Timeout:
        return None, "Timeout: API too slow"
    except Exception as e:
        return None, f"Error: {str(e)}"

def display_tier_badge(tier: str):
    """tier badge display"""
    tier_icons = {"bronze": "🥉", "silver": "🥈", "gold": "🥇", "platinum": "💎"}
    icon = tier_icons.get(tier.lower(), "🏅")
    
    st.markdown(f"""
    <span class="tier-badge {tier.lower()}">
        {icon} {tier.upper()}
    </span>
    """, unsafe_allow_html=True)

def create_fast_map(storages_data):
    """Create optimized map with clear gym status visualization"""
    if not storages_data:
        return None
    
    # Calculate center quickly
    center_lat = sum(s['latitude'] for s in storages_data) / len(storages_data)
    center_lon = sum(s['longitude'] for s in storages_data) / len(storages_data)
    
    # Create map with better contrast
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add markers with clear status indicators
    for storage in storages_data:
        if storage['gym_leader_username']:
            icon_color = 'red'
            popup_text = f"🏛️ {storage['name']}\n👑 {storage['gym_leader_username']}\n🏆 {storage['gym_leader_points']:,} pts"
        else:
            icon_color = 'green'
            popup_text = f"🏛️ {storage['name']}\n✨ Available for Challenge!"
        
        folium.Marker(
            [storage['latitude'], storage['longitude']],
            popup=popup_text,
            tooltip=f"🏛️ {storage['name']}",
            icon=folium.Icon(color=icon_color, icon='star')
        ).add_to(m)
    return m
    # tooltip=f"🏛️ {storage['name']} - {'👑 Occupied' if storage['gym_leader_username'] else '✨ Available'}",
    #         icon=folium.Icon(
    #             color=icon_color, 
    #             icon=icon_symbol, 
    #             prefix='fa',
    #             icon_size=(20, 20)
    #         )
    #     ).add_to(m)
    
    # return m

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style='color: white; margin: 0;'>⚡Goodwill Hunting </h1>
        <p style='color: white; margin: 0; opacity: 0.9;'>
            🏖️ Miami Pokemon Go-style Charitable Gaming • 🏆 Compete • 📦 Donate • 🎯 Win
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick API health check
    api_status, error = fast_api_request("/health", use_cache=False)
    
    if not api_status:
        st.error(f"🚨 **Platform Offline:** {error}")
        st.info("Start the backend: `python fast_backend.py`")
        st.stop()
    
    # sidebar
    with st.sidebar:
        st.header("👤 Donor Profile")
        
        # Get cached users
        users_data, error = fast_api_request("/users")
        
        if users_data:
            user_options = {f"🎯 {u['username']} ({u['tier']})": u['id'] 
                          for u in users_data}
            user_options["➕ Register New Donor"] = "create_new"
            
            selected_option = st.selectbox(
                "Select Donor:", 
                options=list(user_options.keys()),
                key="user_selector"
            )
            
            if selected_option == "➕ Register New Donor":
                st.subheader("🎮 Quick Registration")
                with st.form("fast_create_user"):
                    username = st.text_input("Donor Name*")
                    email = st.text_input("Email*") 
                    
                    if st.form_submit_button("🚀 Join Now!", type="primary"):
                        if username and email:
                            user_data = {"username": username, "email": email, "full_name": ""}
                            result, error = fast_api_request("/users", "POST", user_data, use_cache=False)
                            
                            if result:
                                st.success(f"🎉 Welcome, {username}!")
                                # Clear users cache
                                if "/users_cache" in st.session_state:
                                    del st.session_state["/users_cache"]
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ Registration failed: {error}")
                        else:
                            st.error("Please fill in required fields")
            else:
                current_user_id = user_options[selected_option]
                
                # user profile display
                user_profile, _ = fast_api_request(f"/users/{current_user_id}")
                if user_profile:
                    st.markdown(f"### 🎮 {user_profile['username']}")
                    display_tier_badge(user_profile['tier'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Points", f"{user_profile['total_points']:,}")
                        st.metric("Donations", user_profile['total_donations'])
                    with col2:
                        st.metric("Streak", f"{user_profile['streak_days']} days")
                        st.metric("Achievements", len(user_profile['achievements']))
        else:
            st.error("Failed to load Donor")
            st.stop()
    
    # Main content (optimized for speed)
    if 'current_user_id' in locals() and current_user_id != "create_new":
        
        # platform stats
        stats_data, _ = fast_api_request("/stats")
        
        if stats_data:
            st.subheader("📊 Platform Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Donor", stats_data['total_users'])
            with col2:
                st.metric("Donations", stats_data['total_donations'])
            with col3:
                st.metric("Gyms", stats_data['total_storages'])
            with col4:
                st.metric("Critical Needs", stats_data['critical_needs'], 
                         delta="⚠️ Urgent" if stats_data['critical_needs'] > 5 else "✅ Good")
        
        # Interactive map section
        st.markdown("---")
        st.subheader("🗺️  Gym Locations - Interactive Map")
        st.info("💡 **Red markers** = Occupied by gym leaders | **Green markers** = Available for challenge")
        
        
        #storages_data, _ = fast_api_request("/storages")
        storages_data, _ = fast_api_request("/storages", use_cache=False) #new add
        
        if storages_data:
            # Create map
            fast_map = create_fast_map(storages_data)
            if fast_map:
                map_data = st_folium(fast_map, width=1050, height=525, returned_objects=["last_object_clicked"])
            
            # gym status cards (alternative to slow map interaction)
            st.markdown("#### 🏛️ Gym Status Overview")
            cols = st.columns(3)
            
            for i, storage in enumerate(storages_data):
                with cols[i % 3]:
                    if storage['gym_leader_username']:
                        st.markdown(f"""
                        <div class="gym-card">
                            <strong>🏛️ {storage['name']}</strong><br>
                            👑 Leader: <strong>{storage['gym_leader_username']}</strong><br>
                            🏆 Points: {storage['gym_leader_points']:,}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="gym-card">
                            <strong>🏛️ {storage['name']}</strong><br>
                            ✨ <strong>Available for Challenge!</strong><br>
                            📍 Be the first gym leader!
                        </div>
                        """, unsafe_allow_html=True)
        
        # missing items section
        st.markdown("---")
        st.subheader("🚨 Critical Needs (Load)")
        
        missing_items_data, _ = fast_api_request("/missing-items")
        notifications_data, _ = fast_api_request("/notifications/missing-items")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Priority Items")
            if missing_items_data:
                for item in missing_items_data:
                    st.markdown(f"""
                    <div class="missing-item">
                        <strong>🚨 {item['item_name']}</strong><br>
                        📍 {item['storage_name']}<br>
                        🎁 Bonus: +{item['bonus_points']} points!
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🤖 Notifications")
            if notifications_data:
                for notification in notifications_data:
                    st.markdown(f"""
                    <div class="notification-card notification-{notification['type']}">
                        <strong>{notification['icon']} {notification['message']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
        
        # donation form
        st.markdown("---")
        st.subheader("📦 Quick Donation")
        
        with st.form("fast_donation", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # storage selection
                if storages_data:
                    storage_options = {f"🏛️ {s['name']}": s['id'] for s in storages_data}
                    selected_storage = st.selectbox("Choose Gym:", list(storage_options.keys()))
                    storage_id = storage_options[selected_storage]
                
                # item selection
                priority_items = ["🚨 Winter Coats (+75)", "🚨 Baby Formula (+100)", "🚨 Blankets (+50)"]
                regular_items = ["📦 Canned Goods", "📦 Toys", "📦 Books", "📦 Hygiene Kits"]
                
                all_items = priority_items + regular_items
                selected_item_display = st.selectbox("Item:", all_items)
                
                # Extract item name
                item_name = selected_item_display.replace("🚨 ", "").replace("📦 ", "").split(" (+")[0]
                
                quantity = st.number_input("Quantity:", 1, 50, 1)
            
            with col2:
                st.markdown("#### 🎯 Quick Preview")
                
                # points calculation
                is_priority = "🚨" in selected_item_display
                base_points = 15 * quantity
                bonus_points = (75 if "Winter" in item_name else 100 if "Formula" in item_name else 50) * quantity if is_priority else 0
                total = base_points + bonus_points
                
                if is_priority:
                    st.warning("⚡ HIGH DEMAND ITEM!")
                
                st.info(f"""
                **Quick Calculation:**
                - Base: {base_points} pts
                - Bonus: {bonus_points} pts  
                - **Total: {total} pts**
                """)
            
            if st.form_submit_button("⚡ Donate!", type="primary"):
                donation_data = {
                    "user_id": current_user_id,
                    "storage_id": storage_id,
                    "item_name": item_name,
                    "quantity": quantity
                }
                
                result, error = fast_api_request("/donate", "POST", donation_data, use_cache=False)
                
                if result:
                    st.success(f"🎉 Success! +{result['points_awarded']} points!")
                    
                    # Clear relevant caches
                    for key in ["/users_cache", "/stats_cache"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    if result['bonus_points'] > 0:
                        st.balloons()
                    
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ Donation failed: {error}")
        
        # leaderboard and stats
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Leaderboard")
            
            leaderboard_data, _ = fast_api_request("/leaderboard?limit=5")
            
            if leaderboard_data and isinstance(leaderboard_data, list):
                for entry in leaderboard_data:
                    rank_emoji = ["👑", "🥈", "🥉", "4️⃣", "5️⃣"][entry['rank']-1] if entry['rank'] <= 5 else "🏅"
                    
                    is_current = entry['user_id'] == current_user_id
                    style = "background: linear-gradient(90deg, #FFD700, #FFA500); padding: 0.4rem; border-radius: 6px;" if is_current else ""
                    
                    st.markdown(f"""
                    <div style="{style}">
                        <strong>{rank_emoji} #{entry['rank']} {entry['username']}</strong><br>
                        🏆 {entry['total_points']:,} pts • 🔥 {entry['streak_days']} days<br>
                        <small>{entry['tier']} • {entry['total_donations']} donations</small>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("")
        
        with col2:
            st.subheader("📈 Quick Stats")
            
            if user_profile:
                # Simple progress chart (faster than complex plotly)
                if leaderboard_data and isinstance(leaderboard_data, list):
                    user_rank = next((i for i, u in enumerate(leaderboard_data, 1) if u.get('user_id') == current_user_id), 'N/A')
                    st.metric("Your Rank", f"#{user_rank}")
                else:
                    st.metric("Your Rank", "N/A")
                st.metric("Next Tier", "Coming Soon")
                
                # Achievement progress bar
                total_achievements = 5
                unlocked = len(user_profile['achievements'])
                progress = unlocked / total_achievements
                
                st.progress(progress, text=f"Achievements: {unlocked}/{total_achievements}")
                
                # Simple achievement list
                achievement_list = ["✅ First Steps", "✅ Generous Giver", "🔒 Streak Master", "🔒 Gym Leader", "🔒 Champion"]
                for i, achievement in enumerate(achievement_list):
                    if i < unlocked:
                        st.markdown(f"✅ {achievement.replace('✅ ', '')}")
                    else:
                        st.markdown(f"🔒 {achievement.replace('🔒 ', '')}")
    
    else:
        # welcome screen
        st.markdown("""
        ## ⚡ Welcome to Goodwill Gym!
        
        **High-Performance Pokemon Go-style Charitable Giving**
        
        ### Quick Start:
        1. 📝 **Register** in the sidebar (30 seconds)
        2. 🗺️ **View** gym locations on the map
        3. 📦 **Donate** items for instant points
        4. 🏆 **Compete** to become gym leaders
        5. 🚨 **Help** with high-priority items for bonus points
        
        ### Performance Features:
        - ⚡ **Sub-3-second** page loads
        - 🎯 **Cached data** for instant responses  
        - 🗺️ **maps** with simplified markers
        - 📊 **Quick stats** and leaderboards
        - 🚀 **Optimized** for speed and responsiveness
        
        **All the features, maximum speed! Register now! →**
        """)
    
    # footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;'>
        <h4 style='color: white; margin: 0;'>⚡ Goodwill Gym Platform</h4>
        <p style='color: white; margin: 0; opacity: 0.9;'>
            <strong>High Performance</strong> • <strong>All Features</strong> • <strong>Sub-3s Loads</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()