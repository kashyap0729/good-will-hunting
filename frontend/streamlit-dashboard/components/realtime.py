"""
Real-time Dashboard Components
WebSocket integration and live data streaming for the Streamlit dashboard
"""

import streamlit as st
import asyncio
import websockets
import json
import threading
import queue
from typing import Dict, List, Optional
import time
from datetime import datetime

class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self, websocket_url: str = "ws://localhost:8001/ws/demo_user"):
        self.websocket_url = websocket_url
        self.connection = None
        self.message_queue = queue.Queue()
        self.is_connected = False
        self.listener_thread = None
        
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.connection = await websockets.connect(self.websocket_url)
            self.is_connected = True
            print(f"Connected to {self.websocket_url}")
            
            # Start listening for messages
            await self.listen_for_messages()
            
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            self.is_connected = False
    
    async def listen_for_messages(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.connection:
                data = json.loads(message)
                self.message_queue.put(data)
                
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            print(f"Error listening for messages: {e}")
            self.is_connected = False
    
    def start_connection(self):
        """Start WebSocket connection in a separate thread"""
        if not self.is_connected:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.listener_thread = threading.Thread(
                target=lambda: loop.run_until_complete(self.connect())
            )
            self.listener_thread.daemon = True
            self.listener_thread.start()
    
    def get_messages(self) -> List[Dict]:
        """Get all pending messages from the queue"""
        messages = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages
    
    def send_message(self, message: Dict):
        """Send message through WebSocket"""
        if self.is_connected and self.connection:
            try:
                asyncio.create_task(
                    self.connection.send(json.dumps(message))
                )
            except Exception as e:
                print(f"Error sending message: {e}")

class RealtimeMetrics:
    """Manage real-time metrics and updates"""
    
    def __init__(self):
        self.metrics_history = {
            'donations_per_minute': [],
            'active_users': [],
            'points_awarded': [],
            'achievements_unlocked': []
        }
        self.current_metrics = {
            'total_donations_today': 0,
            'active_users_now': 0,
            'points_awarded_today': 0,
            'new_achievements': 0
        }
    
    def update_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Update a specific metric"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if metric_name in self.metrics_history:
            self.metrics_history[metric_name].append({
                'timestamp': timestamp,
                'value': value
            })
            
            # Keep only last 100 data points for performance
            if len(self.metrics_history[metric_name]) > 100:
                self.metrics_history[metric_name] = self.metrics_history[metric_name][-100:]
    
    def get_trend(self, metric_name: str, minutes: int = 10) -> float:
        """Calculate trend for a metric over the last N minutes"""
        if metric_name not in self.metrics_history:
            return 0.0
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_data = [
            point for point in self.metrics_history[metric_name]
            if point['timestamp'] > cutoff_time
        ]
        
        if len(recent_data) < 2:
            return 0.0
        
        # Simple trend calculation (slope)
        x_values = [(point['timestamp'] - recent_data[0]['timestamp']).total_seconds() 
                   for point in recent_data]
        y_values = [point['value'] for point in recent_data]
        
        if len(x_values) < 2:
            return 0.0
        
        # Linear regression slope
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope

class LiveNotificationSystem:
    """Manage live notifications for the dashboard"""
    
    def __init__(self):
        self.notifications = []
        self.max_notifications = 10
    
    def add_notification(self, notification_type: str, title: str, message: str, 
                        icon: str = "🔔", duration: int = 5000):
        """Add a new notification"""
        notification = {
            'id': f"notif_{int(time.time() * 1000)}",
            'type': notification_type,
            'title': title,
            'message': message,
            'icon': icon,
            'timestamp': datetime.now(),
            'duration': duration,
            'is_read': False
        }
        
        self.notifications.insert(0, notification)
        
        # Keep only the most recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]
        
        return notification
    
    def mark_as_read(self, notification_id: str):
        """Mark notification as read"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['is_read'] = True
                break
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return sum(1 for n in self.notifications if not n['is_read'])
    
    def get_recent_notifications(self, count: int = 5) -> List[Dict]:
        """Get recent notifications"""
        return self.notifications[:count]

def render_live_notifications():
    """Render live notifications component"""
    
    if 'notification_system' not in st.session_state:
        st.session_state.notification_system = LiveNotificationSystem()
    
    notification_system = st.session_state.notification_system
    
    # Notification indicator
    unread_count = notification_system.get_unread_count()
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🔔 Live Notifications")
        
        with col2:
            if unread_count > 0:
                st.markdown(f"**{unread_count} new**", help="Unread notifications")
        
        # Display recent notifications
        recent_notifications = notification_system.get_recent_notifications()
        
        if recent_notifications:
            for notification in recent_notifications:
                with st.container():
                    # Notification styling based on type
                    bg_color = {
                        'success': '#d4edda',
                        'info': '#d1ecf1', 
                        'warning': '#fff3cd',
                        'error': '#f8d7da',
                        'achievement': '#e7f3ff'
                    }.get(notification['type'], '#f8f9fa')
                    
                    border_color = {
                        'success': '#28a745',
                        'info': '#17a2b8',
                        'warning': '#ffc107', 
                        'error': '#dc3545',
                        'achievement': '#007bff'
                    }.get(notification['type'], '#6c757d')
                    
                    # Time ago calculation
                    time_diff = datetime.now() - notification['timestamp']
                    if time_diff.seconds < 60:
                        time_ago = f"{time_diff.seconds}s ago"
                    elif time_diff.seconds < 3600:
                        time_ago = f"{time_diff.seconds // 60}m ago"
                    else:
                        time_ago = f"{time_diff.seconds // 3600}h ago"
                    
                    st.markdown(f"""
                    <div style="
                        background-color: {bg_color};
                        border-left: 4px solid {border_color};
                        padding: 12px;
                        margin: 8px 0;
                        border-radius: 4px;
                        opacity: {'0.6' if notification['is_read'] else '1.0'};
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{notification['icon']} {notification['title']}</strong><br>
                                <small>{notification['message']}</small>
                            </div>
                            <small style="color: #6c757d;">{time_ago}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def render_realtime_metrics():
    """Render real-time metrics display"""
    
    if 'realtime_metrics' not in st.session_state:
        st.session_state.realtime_metrics = RealtimeMetrics()
    
    metrics = st.session_state.realtime_metrics
    
    # Simulate real-time data updates
    import random
    
    # Update metrics with simulated data
    metrics.update_metric('donations_per_minute', random.randint(5, 20))
    metrics.update_metric('active_users', random.randint(50, 150))
    metrics.update_metric('points_awarded', random.randint(100, 500))
    
    # Display real-time metrics
    st.markdown("### ⚡ Live Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_donations = metrics.current_metrics['total_donations_today']
        trend = metrics.get_trend('donations_per_minute', 5)
        delta_color = "normal" if trend >= 0 else "inverse"
        
        st.metric(
            "Donations/Min", 
            f"{current_donations}",
            delta=f"{trend:+.1f}",
            delta_color=delta_color
        )
    
    with col2:
        active_users = metrics.current_metrics['active_users_now']
        user_trend = metrics.get_trend('active_users', 5)
        
        st.metric(
            "Active Users",
            f"{active_users}",
            delta=f"{user_trend:+.0f}",
            delta_color="normal" if user_trend >= 0 else "inverse"
        )
    
    with col3:
        points_today = metrics.current_metrics['points_awarded_today']
        points_trend = metrics.get_trend('points_awarded', 5)
        
        st.metric(
            "Points/Min",
            f"{points_today}",
            delta=f"{points_trend:+.0f}",
            delta_color="normal" if points_trend >= 0 else "inverse"
        )
    
    with col4:
        achievements = metrics.current_metrics['new_achievements']
        
        st.metric(
            "New Achievements",
            f"{achievements}",
            delta="🏆" if achievements > 0 else None
        )

def setup_websocket_integration():
    """Setup WebSocket integration for real-time updates"""
    
    if 'websocket_manager' not in st.session_state:
        st.session_state.websocket_manager = WebSocketManager()
        st.session_state.websocket_manager.start_connection()
    
    # Process incoming messages
    ws_manager = st.session_state.websocket_manager
    messages = ws_manager.get_messages()
    
    if messages:
        notification_system = st.session_state.get('notification_system', LiveNotificationSystem())
        
        for message in messages:
            msg_type = message.get('type', 'info')
            
            if msg_type == 'donation_created':
                notification_system.add_notification(
                    'success',
                    'New Donation! 🎁',
                    f"${message.get('amount', 0):.2f} donated. +{message.get('points', 0)} points!",
                    '💰'
                )
            
            elif msg_type == 'achievement_unlocked':
                notification_system.add_notification(
                    'achievement',
                    'Achievement Unlocked! 🏆',
                    f"{message.get('achievement_name', 'Unknown')}",
                    '🎉'
                )
            
            elif msg_type == 'tier_progression':
                notification_system.add_notification(
                    'success',
                    'Tier Up! 📈',
                    f"Reached {message.get('new_tier', 'Unknown')} tier!",
                    '🌟'
                )
        
        # Update session state
        st.session_state.notification_system = notification_system

def render_live_activity_feed():
    """Render live activity feed component"""
    
    st.markdown("### 🔄 Live Activity Feed")
    
    # Simulate live activities
    activities = [
        {"user": "Sarah J.", "action": "donated $75", "time": "Just now", "icon": "💰"},
        {"user": "Mike C.", "action": "unlocked 'Generous Giver'", "time": "2m ago", "icon": "🏆"},
        {"user": "Emma W.", "action": "reached Gold tier", "time": "5m ago", "icon": "🌟"},
        {"user": "David M.", "action": "donated items", "time": "8m ago", "icon": "📦"},
        {"user": "Lisa T.", "action": "shared achievement", "time": "12m ago", "icon": "📱"},
    ]
    
    # Container for scrollable feed
    with st.container():
        for activity in activities:
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 12px;
                margin: 4px 0;
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                border-left: 3px solid #667eea;
            ">
                <div>
                    {activity['icon']} <strong>{activity['user']}</strong> {activity['action']}
                </div>
                <small style="color: #888;">{activity['time']}</small>
            </div>
            """, unsafe_allow_html=True)

# Auto-refresh functionality
def auto_refresh_data(interval_seconds: int = 30):
    """Auto-refresh data at specified intervals"""
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    current_time = time.time()
    
    if current_time - st.session_state.last_refresh > interval_seconds:
        # Trigger refresh
        st.session_state.last_refresh = current_time
        
        # Add refresh notification
        if 'notification_system' in st.session_state:
            st.session_state.notification_system.add_notification(
                'info',
                'Data Refreshed',
                'Dashboard updated with latest data',
                '🔄',
                duration=2000
            )
        
        # Force rerun to update data
        st.rerun()

# Export functions for use in main app
__all__ = [
    'WebSocketManager',
    'RealtimeMetrics', 
    'LiveNotificationSystem',
    'render_live_notifications',
    'render_realtime_metrics',
    'setup_websocket_integration',
    'render_live_activity_feed',
    'auto_refresh_data'
]