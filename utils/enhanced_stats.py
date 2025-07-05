"""
Enhanced statistics tracking for EduTech AI Learning Platform
Copy this code into utils/enhanced_stats.py
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from config.app_settings import DIFFICULTY_LEVELS, DEFAULT_GOALS, PROGRESS_SETTINGS

logger = logging.getLogger(__name__)

class EnhancedStatsManager:
    """Advanced statistics tracking and analytics"""
    
    def __init__(self):
        self.progress_settings = PROGRESS_SETTINGS
        self.default_goals = DEFAULT_GOALS
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get or initialize comprehensive user statistics"""
        if user_id not in st.session_state.user_stats:
            st.session_state.user_stats[user_id] = self._initialize_user_stats()
        return st.session_state.user_stats[user_id]
    
    def _initialize_user_stats(self) -> Dict[str, Any]:
        """Initialize comprehensive user statistics"""
        return {
            # Core progress metrics
            'overall_progress': 0,
            'total_points': 0,
            'level': 1,
            'experience_points': 0,
            
            # Time tracking
            'study_streak': 0,
            'study_time_today': 0,
            'total_study_time': 0,
            'average_session_time': 0,
            'last_activity_date': None,
            
            # Learning metrics
            'sessions_completed': 0,
            'problems_solved': 0,
            'problems_correct': 0,
            'accuracy_rate': 0,
            'improvement_rate': 0,
            
            # Achievement tracking
            'achievements': 0,
            'badges': [],
            'milestones_reached': [],
            
            # Subject-specific tracking
            'subject_stats': {},
            'favorite_subjects': [],
            'weak_areas': [],
            'mastered_topics': [],
            
            # Engagement metrics
            'login_streak': 0,
            'daily_goal_completions': 0,
            'weekly_goal_completions': 0,
            'consistency_score': 0,
            
            # Performance analytics
            'learning_velocity': 0,  # Progress per hour
            'difficulty_preference': 'Beginner',
            'peak_performance_time': '14:00',  # Best time of day
            'study_pattern': 'Regular',  # Learning pattern
            
            # Goals and targets
            'daily_goals': self.default_goals['daily'].copy(),
            'weekly_goals': self.default_goals['weekly'].copy(),
            'monthly_goals': self.default_goals['monthly'].copy(),
            'custom_goals': [],
            
            # Recent activity
            'recent_sessions': [],
            'recent_achievements': [],
            'activity_history': [],
            
            # Predictive metrics
            'predicted_completion_date': None,
            'estimated_study_time_remaining': 0,
            'next_milestone': None
        }
    
    def update_stats(self, user_id: str, activity_type: str, **kwargs) -> Dict[str, Any]:
        """Update user statistics based on activity"""
        try:
            stats = self.get_user_stats(user_id)
            current_time = datetime.now()
            today = current_time.date()
            
            # Update last activity
            stats['last_activity_date'] = today
            
            # Record activity in history
            activity_record = {
                'type': activity_type,
                'timestamp': current_time,
                'data': kwargs
            }
            stats['activity_history'].append(activity_record)
            
            # Keep only last 100 activities
            if len(stats['activity_history']) > 100:
                stats['activity_history'] = stats['activity_history'][-100:]
            
            # Process specific activity types
            if activity_type == 'problem_solved':
                self._update_problem_stats(stats, kwargs)
            elif activity_type == 'session_completed':
                self._update_session_stats(stats, kwargs)
            elif activity_type == 'study_time':
                self._update_time_stats(stats, kwargs)
            elif activity_type == 'login':
                self._update_login_stats(stats)
            
            # Update derived metrics
            self._calculate_derived_metrics(stats)
            
            # Check for achievements
            new_achievements = self._check_achievements(user_id, stats)
            
            # Update streaks
            self._update_streaks(stats, today)
            
            # Calculate level and experience
            self._update_level_and_experience(stats)
            
            logger.info(f"Updated enhanced stats for user {user_id}: {activity_type}")
            return stats
            
        except Exception as e:
            logger.error(f"Error updating enhanced stats: {e}")
            return self.get_user_stats(user_id)
    
    def _update_problem_stats(self, stats: Dict[str, Any], data: Dict[str, Any]):
        """Update statistics for problem solving"""
        stats['problems_solved'] += 1
        
        if data.get('correct', False):
            stats['problems_correct'] += 1
        
        # Update accuracy rate
        if stats['problems_solved'] > 0:
            stats['accuracy_rate'] = (stats['problems_correct'] / stats['problems_solved']) * 100
        
        # Award points based on difficulty
        difficulty = data.get('difficulty', 'Beginner')
        points = self.progress_settings['points_per_problem'].get(difficulty, 2)
        
        # Apply accuracy bonus
        if stats['accuracy_rate'] >= self.progress_settings['accuracy_bonus_threshold'] * 100:
            points *= 1.2  # 20% bonus for high accuracy
        
        # Apply streak bonus
        if stats['study_streak'] >= 7:
            points *= self.progress_settings['streak_bonus_multiplier']
        
        stats['total_points'] += points
        stats['experience_points'] += points
        
        # Update subject-specific stats
        subject = data.get('subject')
        if subject:
            self._update_subject_stats(stats, subject, points, data.get('correct', False))
    
    def _update_session_stats(self, stats: Dict[str, Any], data: Dict[str, Any]):
        """Update statistics for session completion"""
        stats['sessions_completed'] += 1
        
        session_data = {
            'timestamp': datetime.now(),
            'duration': data.get('duration', 0),
            'subject': data.get('subject'),
            'problems_solved': data.get('problems_solved', 0),
            'points_earned': data.get('points_earned', 0)
        }
        
        stats['recent_sessions'].append(session_data)
        
        # Keep only last 20 sessions
        if len(stats['recent_sessions']) > 20:
            stats['recent_sessions'] = stats['recent_sessions'][-20:]
        
        # Update average session time
        total_duration = sum(s['duration'] for s in stats['recent_sessions'])
        stats['average_session_time'] = total_duration / len(stats['recent_sessions'])
    
    def _update_time_stats(self, stats: Dict[str, Any], data: Dict[str, Any]):
        """Update time-based statistics"""
        time_spent = data.get('time_spent', 0)
        stats['study_time_today'] += time_spent
        stats['total_study_time'] += time_spent
        
        # Award points for time spent
        time_points = time_spent * self.progress_settings['time_spent_points_ratio']
        stats['total_points'] += min(time_points, self.progress_settings['max_daily_points'])
    
    def _update_login_stats(self, stats: Dict[str, Any]):
        """Update login and engagement statistics"""
        today = datetime.now().date()
        
        # Update login streak
        if stats['last_activity_date'] == today - timedelta(days=1):
            stats['login_streak'] += 1
        elif stats['last_activity_date'] != today:
            stats['login_streak'] = 1
    
    def _update_subject_stats(self, stats: Dict[str, Any], subject: str, points: float, correct: bool):
        """Update subject-specific statistics"""
        if 'subject_stats' not in stats:
            stats['subject_stats'] = {}
        
        if subject not in stats['subject_stats']:
            stats['subject_stats'][subject] = {
                'total_problems': 0,
                'correct_problems': 0,
                'total_points': 0,
                'accuracy': 0,
                'time_spent': 0,
                'level': 1,
                'mastery_progress': 0
            }
        
        subject_stats = stats['subject_stats'][subject]
        subject_stats['total_problems'] += 1
        subject_stats['total_points'] += points
        
        if correct:
            subject_stats['correct_problems'] += 1
        
        # Update subject accuracy
        subject_stats['accuracy'] = (subject_stats['correct_problems'] / subject_stats['total_problems']) * 100
        
        # Update mastery progress
        subject_stats['mastery_progress'] = min(100, subject_stats['total_points'] / 10)  # 1000 points = mastery
        
        # Update favorite subjects (top 3 by points)
        sorted_subjects = sorted(
            stats['subject_stats'].items(),
            key=lambda x: x[1]['total_points'],
            reverse=True
        )
        stats['favorite_subjects'] = [subject for subject, _ in sorted_subjects[:3]]
        
        # Identify weak areas (accuracy < 60%)
        stats['weak_areas'] = [
            subject for subject, data in stats['subject_stats'].items()
            if data['accuracy'] < 60 and data['total_problems'] >= 5
        ]
    
    def _calculate_derived_metrics(self, stats: Dict[str, Any]):
        """Calculate derived metrics and analytics"""
        # Learning velocity (progress per hour)
        if stats['total_study_time'] > 0:
            stats['learning_velocity'] = stats['total_points'] / stats['total_study_time']
        
        # Consistency score (based on streaks and regular activity)
        consistency_factors = [
            min(stats['study_streak'] / 30, 1),  # Max 30 days
            min(stats['login_streak'] / 30, 1),  # Max 30 days
            min(stats['sessions_completed'] / 100, 1)  # Max 100 sessions
        ]
        stats['consistency_score'] = sum(consistency_factors) / len(consistency_factors) * 100
        
        # Overall progress calculation
        progress_factors = [
            min(stats['total_points'] / 1000, 1),  # Max 1000 points
            min(stats['problems_solved'] / 100, 1),  # Max 100 problems
            stats['accuracy_rate'] / 100,  # Convert to 0-1 scale
            min(stats['sessions_completed'] / 50, 1)  # Max 50 sessions
        ]
        stats['overall_progress'] = sum(progress_factors) / len(progress_factors) * 100
        
        # Improvement rate (change in accuracy over recent sessions)
        if len(stats['recent_sessions']) >= 10:
            recent_accuracy = self._calculate_recent_accuracy(stats)
            older_accuracy = self._calculate_older_accuracy(stats)
            stats['improvement_rate'] = recent_accuracy - older_accuracy
    
    def _calculate_recent_accuracy(self, stats: Dict[str, Any]) -> float:
        """Calculate accuracy for recent sessions"""
        recent_sessions = stats['recent_sessions'][-5:]  # Last 5 sessions
        if not recent_sessions:
            return 0
        
        total_problems = sum(s.get('problems_solved', 0) for s in recent_sessions)
        # This is simplified - in real implementation, track correct answers per session
        return stats['accuracy_rate']  # Placeholder
    
    def _calculate_older_accuracy(self, stats: Dict[str, Any]) -> float:
        """Calculate accuracy for older sessions"""
        if len(stats['recent_sessions']) < 10:
            return stats['accuracy_rate']
        
        older_sessions = stats['recent_sessions'][-10:-5]  # Sessions 6-10 from end
        # Simplified calculation
        return stats['accuracy_rate'] * 0.9  # Placeholder showing improvement
    
    def _update_streaks(self, stats: Dict[str, Any], today):
        """Update various streak counters"""
        last_date = stats['last_activity_date']
        
        if last_date is None:
            stats['study_streak'] = 1
        elif last_date == today:
            pass  # Already studied today
        elif last_date == today - timedelta(days=1):
            stats['study_streak'] += 1
        else:
            stats['study_streak'] = 1
    
    def _update_level_and_experience(self, stats: Dict[str, Any]):
        """Update user level based on experience points"""
        xp = stats['experience_points']
        
        # Level calculation: Level = sqrt(XP / 100)
        new_level = int((xp / 100) ** 0.5) + 1
        
        if new_level > stats['level']:
            stats['level'] = new_level
            # Add level up achievement
            if 'level_up' not in stats['badges']:
                stats['badges'].append('level_up')
                stats['achievements'] += 1
    
    def _check_achievements(self, user_id: str, stats: Dict[str, Any]) -> List[str]:
        """Check for new achievements"""
        new_achievements = []
        
        # Import here to avoid circular imports
        from utils.achievements import AchievementManager
        achievement_manager = AchievementManager()
        
        # Check various achievement criteria
        achievement_checks = [
            ('problem_solver_10', lambda: stats['problems_solved'] >= 10),
            ('problem_solver_50', lambda: stats['problems_solved'] >= 50),
            ('streak_7', lambda: stats['study_streak'] >= 7),
            ('streak_30', lambda: stats['study_streak'] >= 30),
            ('progress_25', lambda: stats['overall_progress'] >= 25),
            ('progress_50', lambda: stats['overall_progress'] >= 50),
            ('progress_75', lambda: stats['overall_progress'] >= 75),
            ('progress_100', lambda: stats['overall_progress'] >= 100),
            ('session_milestone_5', lambda: stats['sessions_completed'] >= 5),
            ('session_milestone_25', lambda: stats['sessions_completed'] >= 25),
        ]
        
        for achievement_id, condition in achievement_checks:
            if achievement_id not in stats['badges'] and condition():
                achievement_manager.award_achievement(user_id, achievement_id)
                new_achievements.append(achievement_id)
        
        return new_achievements
    
    def get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive progress summary"""
        stats = self.get_user_stats(user_id)
        
        return {
            'overall_progress': stats['overall_progress'],
            'level': stats['level'],
            'total_points': stats['total_points'],
            'study_streak': stats['study_streak'],
            'accuracy_rate': stats['accuracy_rate'],
            'consistency_score': stats['consistency_score'],
            'learning_velocity': stats['learning_velocity'],
            'favorite_subjects': stats['favorite_subjects'],
            'weak_areas': stats['weak_areas'],
            'recent_achievements': stats['badges'][-5:],  # Last 5 achievements
            'daily_progress': self._calculate_daily_progress(stats),
            'weekly_progress': self._calculate_weekly_progress(stats),
            'next_milestone': self._get_next_milestone(stats)
        }
    
    def _calculate_daily_progress(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate progress towards daily goals"""
        goals = stats['daily_goals']
        
        return {
            'study_time': min(100, (stats['study_time_today'] / goals['study_time']) * 100),
            'problems_solved': min(100, ((stats['problems_solved'] % 20) / goals['problems_solved']) * 100),
            'sessions_completed': min(100, ((stats['sessions_completed'] % 10) / goals['sessions_completed']) * 100)
        }
    
    def _calculate_weekly_progress(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate progress towards weekly goals"""
        goals = stats['weekly_goals']
        
        # This is simplified - in real implementation, track weekly totals
        return {
            'study_time': min(100, (stats['study_time_today'] * 7 / goals['study_time']) * 100),
            'problems_solved': min(100, (stats['problems_solved'] / goals['problems_solved']) * 100),
            'sessions_completed': min(100, (stats['sessions_completed'] / goals['sessions_completed']) * 100)
        }
    
    def _get_next_milestone(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Get the next milestone for the user"""
        progress = stats['overall_progress']
        
        milestones = [
            (25, 'Complete basic foundation', 'Foundation Builder badge'),
            (50, 'Reach halfway point', 'Halfway Hero badge'),
            (75, 'Master core concepts', 'Progress Champion badge'),
            (90, 'Approach mastery level', 'Near Expert badge'),
            (100, 'Achieve complete mastery', 'Master Learner badge')
        ]
        
        for target, description, reward in milestones:
            if progress < target:
                return {
                    'target': target,
                    'description': description,
                    'reward': reward,
                    'progress_needed': target - progress
                }
        
        return {'target': 100, 'description': 'Maintain mastery level', 'reward': 'Continued excellence'}
    
    def reset_daily_stats(self, user_id: str):
        """Reset daily statistics (called at midnight)"""
        stats = self.get_user_stats(user_id)
        stats['study_time_today'] = 0
        # Note: Don't reset daily problem counts as they're cumulative
    
    def export_stats(self, user_id: str) -> Dict[str, Any]:
        """Export user statistics for backup or analysis"""
        stats = self.get_user_stats(user_id)
        
        return {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'stats': stats,
            'summary': self.get_progress_summary(user_id)
        }
