"""
Achievement system for EduTech AI Learning Platform
Copy this code into utils/achievements.py
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from config.app_settings import ACHIEVEMENTS, NOTIFICATION_TYPES

logger = logging.getLogger(__name__)

class AchievementManager:
    """Manages user achievements, badges, and rewards"""
    
    def __init__(self):
        self.achievements = ACHIEVEMENTS
        self.notification_types = NOTIFICATION_TYPES
    
    def award_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Award an achievement to a user"""
        try:
            if achievement_id not in self.achievements:
                logger.warning(f"Unknown achievement: {achievement_id}")
                return False
            
            # Get user stats
            if user_id not in st.session_state.user_stats:
                logger.warning(f"User stats not found for {user_id}")
                return False
            
            stats = st.session_state.user_stats[user_id]
            
            # Check if user already has this achievement
            if 'badges' not in stats:
                stats['badges'] = []
            
            if achievement_id in stats['badges']:
                return False  # Already has this achievement
            
            # Award the achievement
            achievement = self.achievements[achievement_id]
            stats['badges'].append(achievement_id)
            stats['achievements'] = len(stats['badges'])
            
            # Add points
            if 'total_points' not in stats:
                stats['total_points'] = 0
            stats['total_points'] += achievement['points']
            
            if 'experience_points' not in stats:
                stats['experience_points'] = 0
            stats['experience_points'] += achievement['points']
            
            # Record achievement with timestamp
            achievement_record = {
                'id': achievement_id,
                'name': achievement['name'],
                'description': achievement['description'],
                'points': achievement['points'],
                'icon': achievement['icon'],
                'timestamp': datetime.now(),
                'user_id': user_id
            }
            
            # Add to recent achievements
            if 'recent_achievements' not in stats:
                stats['recent_achievements'] = []
            stats['recent_achievements'].append(achievement_record)
            
            # Keep only last 10 achievements
            if len(stats['recent_achievements']) > 10:
                stats['recent_achievements'] = stats['recent_achievements'][-10:]
            
            # Add notification
            self._add_achievement_notification(user_id, achievement_record)
            
            # Check for milestone achievements
            self._check_milestone_achievements(user_id, stats)
            
            logger.info(f"Awarded achievement '{achievement_id}' to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error awarding achievement: {e}")
            return False
    
    def _add_achievement_notification(self, user_id: str, achievement: Dict[str, Any]):
        """Add an achievement notification"""
        try:
            if 'notifications' not in st.session_state:
                st.session_state.notifications = []
            
            notification = {
                'id': len(st.session_state.notifications),
                'user_id': user_id,
                'type': 'achievement',
                'title': 'Achievement Unlocked!',
                'message': f"{achievement['icon']} {achievement['name']}: {achievement['description']}",
                'points': achievement['points'],
                'timestamp': datetime.now(),
                'read': False,
                'achievement_id': achievement['id']
            }
            
            st.session_state.notifications.append(notification)
            
            # Also add to session state for immediate display
            if 'pending_achievements' not in st.session_state:
                st.session_state.pending_achievements = []
            st.session_state.pending_achievements.append(achievement)
            
        except Exception as e:
            logger.error(f"Error adding achievement notification: {e}")
    
    def _check_milestone_achievements(self, user_id: str, stats: Dict[str, Any]):
        """Check for milestone achievements based on total achievements"""
        achievement_count = len(stats.get('badges', []))
        
        milestone_achievements = {
            5: 'achievement_collector',
            10: 'badge_hunter',
            20: 'achievement_master',
            50: 'legendary_achiever'
        }
        
        for threshold, milestone_id in milestone_achievements.items():
            if achievement_count >= threshold and milestone_id not in stats.get('badges', []):
                # Create dynamic milestone achievement
                milestone_achievement = {
                    'name': f'Achievement Collector {achievement['icon']}',
                    'description': f'Earn {threshold} achievements',
                    'points': threshold * 10,
                    'icon': '🏆'
                }
                
                # Add to achievements if not exists
                if milestone_id not in self.achievements:
                    self.achievements[milestone_id] = milestone_achievement
                
                # Award the milestone
                self.award_achievement(user_id, milestone_id)
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all achievements for a user"""
        try:
            if user_id not in st.session_state.user_stats:
                return []
            
            stats = st.session_state.user_stats[user_id]
            badges = stats.get('badges', [])
            
            user_achievements = []
            for badge_id in badges:
                if badge_id in self.achievements:
                    achievement = self.achievements[badge_id].copy()
                    achievement['id'] = badge_id
                    achievement['earned'] = True
                    
                    # Try to get timestamp from recent achievements
                    recent_achievements = stats.get('recent_achievements', [])
                    for recent in recent_achievements:
                        if recent['id'] == badge_id:
                            achievement['timestamp'] = recent['timestamp']
                            break
                    
                    user_achievements.append(achievement)
            
            # Sort by timestamp (most recent first)
            user_achievements.sort(
                key=lambda x: x.get('timestamp', datetime.min), 
                reverse=True
            )
            
            return user_achievements
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return []
    
    def get_available_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get achievements user can still earn"""
        try:
            if user_id not in st.session_state.user_stats:
                return list(self.achievements.values())
            
            stats = st.session_state.user_stats[user_id]
            earned_badges = set(stats.get('badges', []))
            
            available = []
            for achievement_id, achievement in self.achievements.items():
                if achievement_id not in earned_badges:
                    achievement_copy = achievement.copy()
                    achievement_copy['id'] = achievement_id
                    achievement_copy['earned'] = False
                    achievement_copy['progress'] = self._calculate_achievement_progress(
                        user_id, achievement_id, stats
                    )
                    available.append(achievement_copy)
            
            # Sort by progress (closest to completion first)
            available.sort(key=lambda x: x['progress'], reverse=True)
            
            return available
            
        except Exception as e:
            logger.error(f"Error getting available achievements: {e}")
            return []
    
    def _calculate_achievement_progress(self, user_id: str, achievement_id: str, stats: Dict[str, Any]) -> float:
        """Calculate progress towards an achievement (0-100%)"""
        try:
            # Define progress calculation for each achievement
            progress_calculators = {
                'problem_solver_10': lambda: min(100, (stats.get('problems_solved', 0) / 10) * 100),
                'problem_solver_50': lambda: min(100, (stats.get('problems_solved', 0) / 50) * 100),
                'streak_7': lambda: min(100, (stats.get('study_streak', 0) / 7) * 100),
                'streak_30': lambda: min(100, (stats.get('study_streak', 0) / 30) * 100),
                'progress_25': lambda: min(100, (stats.get('overall_progress', 0) / 25) * 100),
                'progress_50': lambda: min(100, (stats.get('overall_progress', 0) / 50) * 100),
                'progress_75': lambda: min(100, (stats.get('overall_progress', 0) / 75) * 100),
                'progress_100': lambda: min(100, (stats.get('overall_progress', 0) / 100) * 100),
                'session_milestone_5': lambda: min(100, (stats.get('sessions_completed', 0) / 5) * 100),
                'session_milestone_25': lambda: min(100, (stats.get('sessions_completed', 0) / 25) * 100),
            }
            
            if achievement_id in progress_calculators:
                return progress_calculators[achievement_id]()
            
            return 0  # No progress calculation available
            
        except Exception as e:
            logger.error(f"Error calculating achievement progress: {e}")
            return 0
    
    def get_achievement_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive achievement statistics"""
        try:
            earned_achievements = self.get_user_achievements(user_id)
            available_achievements = self.get_available_achievements(user_id)
            
            total_possible = len(self.achievements)
            total_earned = len(earned_achievements)
            total_points = sum(ach['points'] for ach in earned_achievements)
            
            # Calculate completion percentage
            completion_percentage = (total_earned / total_possible) * 100 if total_possible > 0 else 0
            
            # Get recent achievements (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_achievements = [
                ach for ach in earned_achievements 
                if ach.get('timestamp', datetime.min) > week_ago
            ]
            
            # Find closest achievements (>75% progress)
            close_achievements = [
                ach for ach in available_achievements 
                if ach['progress'] >= 75
            ]
            
            # Achievement categories
            categories = {
                'Progress': ['progress_25', 'progress_50', 'progress_75', 'progress_100'],
                'Practice': ['problem_solver_10', 'problem_solver_50', 'first_practice'],
                'Consistency': ['streak_7', 'streak_30', 'early_bird', 'night_owl'],
                'Learning': ['session_milestone_5', 'session_milestone_25', 'assessment_complete'],
                'Social': ['tutor_favorite'],
                'Milestones': ['first_login']
            }
            
            category_progress = {}
            for category, achievement_ids in categories.items():
                earned_in_category = sum(1 for ach in earned_achievements if ach['id'] in achievement_ids)
                total_in_category = len(achievement_ids)
                category_progress[category] = {
                    'earned': earned_in_category,
                    'total': total_in_category,
                    'percentage': (earned_in_category / total_in_category) * 100 if total_in_category > 0 else 0
                }
            
            return {
                'total_earned': total_earned,
                'total_possible': total_possible,
                'completion_percentage': completion_percentage,
                'total_points': total_points,
                'recent_achievements': recent_achievements,
                'close_achievements': close_achievements,
                'category_progress': category_progress,
                'achievement_rate': len(recent_achievements),  # Achievements per week
                'next_milestone': self._get_next_major_milestone(earned_achievements)
            }
            
        except Exception as e:
            logger.error(f"Error getting achievement stats: {e}")
            return {}
    
    def _get_next_major_milestone(self, earned_achievements: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get the next major achievement milestone"""
        total_earned = len(earned_achievements)
        
        milestones = [
            (5, "Achievement Starter", "Earn your first 5 achievements"),
            (10, "Badge Collector", "Collect 10 different badges"),
            (15, "Achievement Hunter", "Unlock 15 achievements"),
            (20, "Badge Master", "Master 20 achievements"),
            (25, "Achievement Legend", "Become a legend with 25 achievements")
        ]
        
        for threshold, name, description in milestones:
            if total_earned < threshold:
                return {
                    'threshold': threshold,
                    'name': name,
                    'description': description,
                    'progress': total_earned,
                    'remaining': threshold - total_earned
                }
        
        return None
    
    def display_achievement_notification(self, achievement: Dict[str, Any]):
        """Display achievement notification in Streamlit"""
        try:
            # Create achievement display
            st.markdown(f"""
            <div class="achievement-notification" style="
                background: linear-gradient(135deg, #FFD700, #FFA500);
                border: 2px solid #FF8C00;
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                animation: pulse 2s infinite;
            ">
                <div style="font-size: 3em; margin-bottom: 10px;">
                    {achievement['icon']}
                </div>
                <h2 style="color: #8B4513; margin: 10px 0; font-weight: bold;">
                    🏆 Achievement Unlocked! 🏆
                </h2>
                <h3 style="color: #8B4513; margin: 10px 0;">
                    {achievement['name']}
                </h3>
                <p style="color: #8B4513; font-size: 1.1em; margin: 10px 0;">
                    {achievement['description']}
                </p>
                <div style="background: rgba(139, 69, 19, 0.1); border-radius: 10px; padding: 10px; margin-top: 15px;">
                    <strong style="color: #8B4513; font-size: 1.2em;">
                        +{achievement['points']} Points Earned! 🎯
                    </strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add CSS animation
            st.markdown("""
            <style>
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            </style>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error displaying achievement notification: {e}")
    
    def show_achievement_gallery(self, user_id: str):
        """Display achievement gallery for a user"""
        try:
            st.subheader("🏆 Achievement Gallery")
            
            earned = self.get_user_achievements(user_id)
            available = self.get_available_achievements(user_id)
            stats = self.get_achievement_stats(user_id)
            
            # Achievement summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Earned", f"{stats['total_earned']}/{stats['total_possible']}")
            
            with col2:
                st.metric("Completion", f"{stats['completion_percentage']:.1f}%")
            
            with col3:
                st.metric("Total Points", stats['total_points'])
            
            with col4:
                st.metric("This Week", len(stats['recent_achievements']))
            
            # Progress bar
            progress = stats['completion_percentage'] / 100
            st.progress(progress)
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["🏅 Earned", "🎯 Available", "📊 Categories"])
            
            with tab1:
                if earned:
                    cols = st.columns(3)
                    for i, achievement in enumerate(earned):
                        with cols[i % 3]:
                            self._display_achievement_card(achievement, earned=True)
                else:
                    st.info("No achievements earned yet. Start learning to unlock your first badge!")
            
            with tab2:
                if available:
                    # Show closest achievements first
                    close_achievements = [ach for ach in available if ach['progress'] >= 25]
                    
                    if close_achievements:
                        st.subheader("🎯 Almost There!")
                        cols = st.columns(3)
                        for i, achievement in enumerate(close_achievements[:6]):
                            with cols[i % 3]:
                                self._display_achievement_card(achievement, earned=False)
                    
                    st.subheader("🔓 All Available")
                    cols = st.columns(3)
                    for i, achievement in enumerate(available):
                        with cols[i % 3]:
                            self._display_achievement_card(achievement, earned=False)
                else:
                    st.success("🎉 Congratulations! You've earned all available achievements!")
            
            with tab3:
                self._display_category_progress(stats['category_progress'])
            
        except Exception as e:
            logger.error(f"Error showing achievement gallery: {e}")
            st.error("Unable to load achievement gallery.")
    
    def _display_achievement_card(self, achievement: Dict[str, Any], earned: bool = True):
        """Display individual achievement card"""
        try:
            # Card styling based on earned status
            if earned:
                card_style = """
                background: linear-gradient(135deg, #FFD700, #FFA500);
                border: 2px solid #FF8C00;
                opacity: 1;
                """
            else:
                card_style = """
                background: linear-gradient(135deg, #E0E0E0, #BDBDBD);
                border: 2px solid #9E9E9E;
                opacity: 0.7;
                """
            
            # Progress bar for unearned achievements
            progress_bar = ""
            if not earned and achievement.get('progress', 0) > 0:
                progress = achievement['progress']
                progress_bar = f"""
                <div style="background: #f0f0f0; border-radius: 10px; margin: 5px 0;">
                    <div style="background: #4CAF50; width: {progress}%; height: 8px; border-radius: 10px;"></div>
                </div>
                <small style="color: #666;">Progress: {progress:.0f}%</small>
                """
            
            # Timestamp for earned achievements
            timestamp_info = ""
            if earned and 'timestamp' in achievement:
                timestamp = achievement['timestamp']
                if isinstance(timestamp, datetime):
                    days_ago = (datetime.now() - timestamp).days
                    if days_ago == 0:
                        timestamp_info = "<small style='color: #666;'>Earned today!</small>"
                    elif days_ago == 1:
                        timestamp_info = "<small style='color: #666;'>Earned yesterday</small>"
                    else:
                        timestamp_info = f"<small style='color: #666;'>Earned {days_ago} days ago</small>"
            
            st.markdown(f"""
            <div style="
                {card_style}
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                text-align: center;
                min-height: 200px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="font-size: 2.5em; margin-bottom: 10px;">
                        {achievement['icon']}
                    </div>
                    <h4 style="color: #8B4513; margin: 10px 0; font-weight: bold;">
                        {achievement['name']}
                    </h4>
                    <p style="color: #8B4513; font-size: 0.9em; margin: 5px 0;">
                        {achievement['description']}
                    </p>
                </div>
                <div>
                    {progress_bar}
                    <div style="margin-top: 10px;">
                        <strong style="color: #8B4513;">
                            {achievement['points']} points
                        </strong>
                    </div>
                    {timestamp_info}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error displaying achievement card: {e}")
    
    def _display_category_progress(self, category_progress: Dict[str, Dict[str, Any]]):
        """Display progress by achievement category"""
        try:
            st.subheader("📊 Progress by Category")
            
            for category, progress in category_progress.items():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{category}**")
                    percentage = progress['percentage']
                    st.progress(percentage / 100)
                    st.write(f"{progress['earned']}/{progress['total']} achievements ({percentage:.0f}%)")
                
                with col2:
                    # Category icon
                    category_icons = {
                        'Progress': '📈',
                        'Practice': '🧮',
                        'Consistency': '🔥',
                        'Learning': '📚',
                        'Social': '👥',
                        'Milestones': '🎯'
                    }
                    icon = category_icons.get(category, '🏆')
                    st.markdown(f"<div style='text-align: center; font-size: 3em; margin-top: 20px;'>{icon}</div>", 
                              unsafe_allow_html=True)
                
                st.markdown("---")
                
        except Exception as e:
            logger.error(f"Error displaying category progress: {e}")
    
    def check_pending_achievements(self, user_id: str):
        """Check and display any pending achievement notifications"""
        try:
            if 'pending_achievements' in st.session_state and st.session_state.pending_achievements:
                for achievement in st.session_state.pending_achievements:
                    self.display_achievement_notification(achievement)
                    st.balloons()  # Celebration effect
                
                # Clear pending achievements after display
                st.session_state.pending_achievements = []
                
        except Exception as e:
            logger.error(f"Error checking pending achievements: {e}")
