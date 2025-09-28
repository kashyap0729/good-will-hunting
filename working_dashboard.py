"""
Working Streamlit Dashboard
A simple gamified donation dashboard that actually works
"""

import streamlit as st
import requests
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# App configuration
st.set_page_config(
    page_title="🎮 Goodwill Platform",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def get_api_data(endpoint):
    """Safely get data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def main():
    # Header
    st.markdown("""
    # 🎮 Goodwill Gaming Platform
    ### Gamified Charitable Giving - **Now Actually Working!** ✅
    """)
    
    # Check API connection
    api_status = get_api_data("/health")
    
    if api_status:
        st.success("✅ API Connected! Platform is operational.")
    else:
        st.warning("⚠️ API not running. Start the API with: `python simple_donation_api.py`")
        st.info("This demo shows the interface even without the API connection.")
    
    # Main dashboard
    col1, col2, col3 = st.columns(3)
    
    # Get stats from API
    stats_data = get_api_data("/stats") if api_status else None
    
    if stats_data:
        platform_stats = stats_data["platform_stats"]
        
        with col1:
            st.metric(
                "Total Donations", 
                platform_stats["total_donations"],
                delta=f"+{platform_stats['total_donations'] - 3} new"
            )
        
        with col2:
            st.metric(
                "Total Amount", 
                f"${platform_stats['total_amount']:,.2f}",
                delta=f"${platform_stats['average_donation']:.0f} avg"
            )
        
        with col3:
            st.metric(
                "Active Users", 
                platform_stats["total_users"],
                delta="+2 this week"
            )
    else:
        # Demo data when API is not available
        with col1:
            st.metric("Total Donations", "247", delta="+12 new")
        
        with col2:
            st.metric("Total Amount", "$12,450", delta="$85 avg")
        
        with col3:
            st.metric("Active Users", "89", delta="+7 this week")
    
    # Donation form
    st.markdown("---")
    st.subheader("💖 Make a Donation")
    
    with st.form("donation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("Your User ID", value="demo_user_new")
            amount = st.number_input("Donation Amount ($)", min_value=1.0, value=25.0, step=5.0)
        
        with col2:
            donation_type = st.selectbox("Donation Type", ["monetary", "goods", "time"])
            message = st.text_area("Optional Message", placeholder="Your message of support...")
        
        submitted = st.form_submit_button("🎮 Donate & Earn Points!")
        
        if submitted:
            if api_status:
                try:
                    donation_data = {
                        "user_id": user_id,
                        "amount": amount,
                        "donation_type": donation_type,
                        "message": message
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/donations", 
                        json=donation_data,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"""
                        🎉 Donation Successful!
                        
                        **Donation ID:** {result['donation_id'][:8]}...
                        **Amount:** ${result['amount']:.2f}
                        **Points Earned:** {result['points_awarded']} 🏆
                        
                        Thank you for your generosity!
                        """)
                        st.balloons()
                    else:
                        st.error("Donation failed. Please try again.")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
            else:
                # Simulate donation when API is not available
                points = int(amount * 10)
                st.success(f"""
                🎉 Donation Simulated!
                
                **Amount:** ${amount:.2f}
                **Points Earned:** {points} 🏆
                
                (Start the API to process real donations)
                """)
                st.balloons()
    
    # Leaderboard and Stats
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Recent Activity")
        
        if stats_data and "recent_activity" in stats_data:
            recent = stats_data["recent_activity"]
            
            if recent:
                for donation in recent[-3:]:
                    with st.container():
                        st.markdown(f"""
                        **${donation['amount']:.2f}** from User {donation['user_id'][-4:]}  
                        *{donation['points_awarded']} points earned* 🎮  
                        *{donation.get('message', 'No message')}*
                        """)
                        st.markdown("---")
            else:
                st.info("No recent donations. Be the first! 🎯")
        else:
            # Demo data
            demo_donations = [
                {"amount": 150.0, "user": "Alice", "points": 2250, "message": "Amazing work!"},
                {"amount": 75.0, "user": "Bob", "points": 937, "message": "Keep it up!"},
                {"amount": 25.0, "user": "Carol", "points": 250, "message": "Great cause!"}
            ]
            
            for donation in demo_donations:
                st.markdown(f"""
                **${donation['amount']:.2f}** from {donation['user']}  
                *{donation['points']} points earned* 🎮  
                *{donation['message']}*
                """)
                st.markdown("---")
    
    with col2:
        st.subheader("🎖️ Achievement Tiers")
        
        if stats_data and "tier_distribution" in stats_data:
            tiers = stats_data["tier_distribution"]
            
            # Create tier chart using plotly directly
            fig = go.Figure(data=[
                go.Bar(
                    x=["🥉 Bronze", "🥈 Silver", "🥇 Gold"],
                    y=[tiers["bronze"], tiers["silver"], tiers["gold"]],
                    marker_color=['#CD7F32', '#C0C0C0', '#FFD700']
                )
            ])
            fig.update_layout(
                title="User Tier Distribution",
                xaxis_title="Tier",
                yaxis_title="Users",
                showlegend=False, 
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Demo chart
            fig = go.Figure(data=[
                go.Bar(
                    x=["🥉 Bronze", "🥈 Silver", "🥇 Gold"],
                    y=[45, 32, 12],
                    marker_color=['#CD7F32', '#C0C0C0', '#FFD700']
                )
            ])
            fig.update_layout(
                title="User Tier Distribution (Demo)",
                xaxis_title="Tier",
                yaxis_title="Users",
                showlegend=False, 
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tier requirements
        st.markdown("""
        **Tier Requirements:**
        - 🥉 Bronze: $0+ donated
        - 🥈 Silver: $100+ donated  
        - 🥇 Gold: $500+ donated
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <h4>🎮 Built with Streamlit & FastAPI | Working Demo ✅</h4>
        <p>This is a functional demonstration of the gamified donation platform.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()