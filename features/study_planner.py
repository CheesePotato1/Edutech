"""
Study planner and goal management for EduTech AI Learning Platform
Copy this code into features/study_planner.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
from typing import Dict, Any, List, Optional, Tuple
import calendar
import random
import logging

logger = logging.getLogger(__name__)

class StudyPlanner:
    """Intelligent study planning and goal management system"""
    
    def __init__(self):
        self.subjects = ["Mathematics", "Physics", "Chemistry", "Literature", "History", "Biology"]
        self.difficulty_levels = ["Beginner", "Intermediate", "Advanced"]
        self.session_types = ["Study", "Practice", "Review", "Quiz", "Project"]
        
        # Study session templates
        self.session_templates = {
            "Quick Review": {"duration": 15, "type": "Review", "intensity": "Light"},
            "Focus Session": {"duration": 30, "type": "Study", "intensity": "Medium"},
            "Deep Dive": {"duration": 60, "type": "Study", "intensity": "High"},
            "Practice Drill": {"duration": 25, "type": "Practice", "intensity": "Medium"},
            "Quiz Challenge": {"duration": 20, "type": "Quiz", "intensity": "High"}
        }
    
    def render_study_planner_interface(self, user_id: str):
        """Render the complete study planner interface"""
        try:
            # Get user stats and data
            from utils.enhanced_stats import EnhancedStatsManager
            stats_manager = EnhancedStatsManager()
            user_stats = stats_manager.get_user_stats(user_id)
            user_data = st.session_state.all_users.get(user_id, {})
            
            st.title("📅 Smart Study Planner")
            st.write("Plan your learning journey with AI-powered recommendations!")
            
            # Main tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Today's Plan", 
                "📅 Weekly Schedule", 
                "🎯 Goals & Targets", 
                "📊 Analytics"
            ])
            
            with tab1:
                self._render_daily_planner(user_id, user_stats, user_data)
            
            with tab2:
                self._render_weekly_scheduler(user_id, user_stats, user_data)
            
            with tab3:
                self._render_goals_manager(user_id, user_stats, user_data)
            
            with tab4:
                self._render_study_analytics(user_id, user_stats)
            
        except Exception as e:
            logger.error(f"Error rendering study planner: {e}")
            st.error("Unable to load study planner. Please refresh the page.")
    
    def _render_daily_planner(self, user_id: str, user_stats: Dict[str, Any], user_data: Dict[str, Any]):
        """Render today's study plan"""
        try:
            st.subheader("📋 Today's Study Plan")
            today = datetime.now().date()
            
            # Get or create today's plan
            daily_plan = self._get_daily_plan(user_id, today, user_stats, user_data)
            
            # Display progress overview
            self._render_daily_progress_overview(user_stats, daily_plan)
            
            # Today's schedule
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🕐 Today's Schedule")
                
                if daily_plan['sessions']:
                    for i, session in enumerate(daily_plan['sessions']):
                        self._render_session_card(user_id, session, i)
                else:
                    st.info("No study sessions planned for today. Let's create your schedule!")
                    if st.button("🎯 Generate Smart Schedule", use_container_width=True):
                        new_plan = self._generate_smart_daily_plan(user_id, user_stats, user_data)
                        self._save_daily_plan(user_id, today, new_plan)
                        st.rerun()
            
            with col2:
                st.subheader("⚡ Quick Actions")
                
                # Quick session launcher
                st.markdown("### 🚀 Start Quick Session")
                
                quick_session_type = st.selectbox(
                    "Session Type:",
                    list(self.session_templates.keys()),
                    key="quick_session"
                )
                
                if st.button("Start Now", use_container_width=True):
                    self._start_quick_session(user_id, quick_session_type, user_stats)
                
                # Today's insights
                st.markdown("### 💡 Today's Insights")
                insights = self._generate_daily_insights(user_stats, daily_plan)
                for insight in insights:
                    st.info(insight)
                
                # Motivation boost
                st.markdown("### 💪 Motivation Boost")
                motivation = self._get_motivational_message(user_stats)
                st.success(motivation)
            
        except Exception as e:
            logger.error(f"Error rendering daily planner: {e}")
            st.error("Unable to load daily planner.")
    
    def _render_session_card(self, user_id: str, session: Dict[str, Any], index: int):
        """Render individual study session card"""
        try:
            # Session status
            status = session.get('status', 'planned')
            status_colors = {
                'planned': '#2196F3',
                'in_progress': '#FF9800', 
                'completed': '#4CAF50',
                'skipped': '#9E9E9E'
            }
            
            status_icons = {
                'planned': '⏳',
                'in_progress': '▶️',
                'completed': '✅',
                'skipped': '⏭️'
            }
            
            # Time formatting
            start_time = session.get('start_time', '09:00')
            duration = session.get('duration', 30)
            end_time = self._add_minutes_to_time(start_time, duration)
            
            # Card content
            st.markdown(f"""
            <div style="
                border: 2px solid {status_colors[status]};
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background: {status_colors[status]}10;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: {status_colors[status]};">
                        {status_icons[status]} {session['title']}
                    </h4>
                    <span style="color: {status_colors[status]}; font-weight: bold;">
                        {start_time} - {end_time}
                    </span>
                </div>
                <p style="margin: 5px 0;"><strong>Subject:</strong> {session['subject']}</p>
                <p style="margin: 5px 0;"><strong>Type:</strong> {session['type']} ({duration} min)</p>
                <p style="margin: 5px 0;"><strong>Goal:</strong> {session.get('goal', 'Complete session')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if status == 'planned':
                    if st.button("▶️ Start", key=f"start_{index}"):
                        self._start_session(user_id, session, index)
                elif status == 'in_progress':
                    if st.button("✅ Complete", key=f"complete_{index}"):
                        self._complete_session(user_id, session, index)
            
            with col2:
                if status == 'planned':
                    if st.button("✏️ Edit", key=f"edit_{index}"):
                        self._edit_session(user_id, session, index)
            
            with col3:
                if status in ['planned', 'in_progress']:
                    if st.button("⏭️ Skip", key=f"skip_{index}"):
                        self._skip_session(user_id, session, index)
            
        except Exception as e:
            logger.error(f"Error rendering session card: {e}")
            st.error("Unable to render session card.")
    
    def _render_weekly_scheduler(self, user_id: str, user_stats: Dict[str, Any], user_data: Dict[str, Any]):
        """Render weekly schedule view"""
        try:
            st.subheader("📅 Weekly Schedule")
            
            # Week navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("◀️ Previous Week"):
                    st.session_state.selected_week_offset = st.session_state.get('selected_week_offset', 0) - 1
                    st.rerun()
            
            with col2:
                week_offset = st.session_state.get('selected_week_offset', 0)
                current_week_start = datetime.now().date() + timedelta(days=week_offset * 7)
                current_week_start -= timedelta(days=current_week_start.weekday())  # Monday
                week_end = current_week_start + timedelta(days=6)
                
                st.markdown(f"### Week of {current_week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
            
            with col3:
                if st.button("Next Week ▶️"):
                    st.session_state.selected_week_offset = st.session_state.get('selected_week_offset', 0) + 1
                    st.rerun()
            
            # Weekly overview
            self._render_weekly_overview(user_id, current_week_start, user_stats)
            
            # Daily schedule grid
            self._render_weekly_grid(user_id, current_week_start, user_stats, user_data)
            
            # Weekly goals and targets
            st.subheader("🎯 This Week's Targets")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                weekly_study_goal = user_stats.get('weekly_goals', {}).get('study_time', 14)
                current_weekly_time = self._calculate_weekly_study_time(user_id, current_week_start)
                
                st.metric(
                    "Study Time Goal", 
                    f"{current_weekly_time:.1f}/{weekly_study_goal} hrs",
                    delta=f"{((current_weekly_time/weekly_study_goal)*100):.0f}% complete"
                )
            
            with col2:
                weekly_problem_goal = user_stats.get('weekly_goals', {}).get('problems_solved', 70)
                current_weekly_problems = random.randint(30, 60)  # Mock data
                
                st.metric(
                    "Problems Goal",
                    f"{current_weekly_problems}/{weekly_problem_goal}",
                    delta=f"{((current_weekly_problems/weekly_problem_goal)*100):.0f}% complete"
                )
            
            with col3:
                weekly_session_goal = user_stats.get('weekly_goals', {}).get('sessions_completed', 14)
                current_weekly_sessions = random.randint(8, 12)  # Mock data
                
                st.metric(
                    "Sessions Goal",
                    f"{current_weekly_sessions}/{weekly_session_goal}",
                    delta=f"{((current_weekly_sessions/weekly_session_goal)*100):.0f}% complete"
                )
            
        except Exception as e:
            logger.error(f"Error rendering weekly scheduler: {e}")
            st.error("Unable to load weekly scheduler.")
    
    def _render_goals_manager(self, user_id: str, user_stats: Dict[str, Any], user_data: Dict[str, Any]):
        """Render goals and targets management"""
        try:
            st.subheader("🎯 Goals & Targets Management")
            
            # Current goals overview
            st.markdown("### 📊 Current Goals Overview")
            
            # Get current goals
            daily_goals = user_stats.get('daily_goals', {
                'study_time': 2.0,
                'problems_solved': 10,
                'sessions_completed': 2
            })
            
            weekly_goals = user_stats.get('weekly_goals', {
                'study_time': 14.0,
                'problems_solved': 70,
                'sessions_completed': 14
            })
            
            # Display current progress
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📅 Daily Goals")
                
                daily_progress = self._calculate_daily_progress(user_stats)
                
                for goal, target in daily_goals.items():
                    current = daily_progress.get(goal, 0)
                    progress_pct = min(100, (current / target) * 100)
                    
                    st.metric(
                        goal.replace('_', ' ').title(),
                        f"{current:.1f}/{target}",
                        delta=f"{progress_pct:.0f}% complete"
                    )
                    st.progress(progress_pct / 100)
            
            with col2:
                st.markdown("#### 📆 Weekly Goals")
                
                for goal, target in weekly_goals.items():
                    # Mock weekly progress
                    current = random.randint(int(target * 0.4), int(target * 0.8))
                    progress_pct = min(100, (current / target) * 100)
                    
                    st.metric(
                        goal.replace('_', ' ').title(),
                        f"{current}/{target}",
                        delta=f"{progress_pct:.0f}% complete"
                    )
                    st.progress(progress_pct / 100)
            
            # Goal setting interface
            st.markdown("### ⚙️ Customize Your Goals")
            
            with st.expander("📝 Edit Goals", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Daily Goals")
                    
                    new_daily_study = st.slider(
                        "Daily Study Time (hours)",
                        min_value=0.5, max_value=8.0, 
                        value=daily_goals['study_time'],
                        step=0.5
                    )
                    
                    new_daily_problems = st.slider(
                        "Daily Problems Target",
                        min_value=1, max_value=50,
                        value=int(daily_goals['problems_solved'])
                    )
                    
                    new_daily_sessions = st.slider(
                        "Daily Sessions Target", 
                        min_value=1, max_value=10,
                        value=int(daily_goals['sessions_completed'])
                    )
                
                with col2:
                    st.markdown("#### Weekly Goals")
                    
                    new_weekly_study = st.slider(
                        "Weekly Study Time (hours)",
                        min_value=3.0, max_value=50.0,
                        value=weekly_goals['study_time'],
                        step=1.0
                    )
                    
                    new_weekly_problems = st.slider(
                        "Weekly Problems Target",
                        min_value=10, max_value=300,
                        value=int(weekly_goals['problems_solved'])
                    )
                    
                    new_weekly_sessions = st.slider(
                        "Weekly Sessions Target",
                        min_value=5, max_value=50,
                        value=int(weekly_goals['sessions_completed'])
                    )
                
                if st.button("💾 Save Goals", use_container_width=True):
                    self._update_user_goals(user_id, {
                        'daily_goals': {
                            'study_time': new_daily_study,
                            'problems_solved': new_daily_problems,
                            'sessions_completed': new_daily_sessions
                        },
                        'weekly_goals': {
                            'study_time': new_weekly_study,
                            'problems_solved': new_weekly_problems,
                            'sessions_completed': new_weekly_sessions
                        }
                    })
                    st.success("✅ Goals updated successfully!")
                    st.rerun()
            
            # Long-term goals
            st.markdown("### 🚀 Long-term Learning Goals")
            
            self._render_longterm_goals(user_id, user_stats, user_data)
            
        except Exception as e:
            logger.error(f"Error rendering goals manager: {e}")
            st.error("Unable to load goals manager.")
    
    def _render_study_analytics(self, user_id: str, user_stats: Dict[str, Any]):
        """Render study analytics and insights"""
        try:
            st.subheader("📊 Study Analytics & Insights")
            
            # Study pattern analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 Study Time Trends")
                
                # Generate mock study time data
                dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
                study_times = []
                
                for i, date in enumerate(dates):
                    base_time = 1.5  # Base study time
                    weekend_factor = 0.7 if date.weekday() >= 5 else 1.0
                    trend_factor = 1 + (i * 0.01)  # Slight upward trend
                    noise = random.uniform(0.5, 1.5)
                    
                    study_time = base_time * weekend_factor * trend_factor * noise
                    study_times.append(max(0, study_time))
                
                study_df = pd.DataFrame({
                    'Date': dates,
                    'Study Time': study_times
                })
                
                fig = px.line(
                    study_df, x='Date', y='Study Time',
                    title='Daily Study Time (Last 30 Days)',
                    labels={'Study Time': 'Hours'}
                )
                fig.update_traces(line_color='#667eea')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🎯 Goal Achievement Rate")
                
                # Mock goal achievement data
                goal_data = pd.DataFrame({
                    'Goal Type': ['Daily Study Time', 'Daily Problems', 'Daily Sessions', 'Weekly Study Time'],
                    'Achievement Rate': [85, 92, 78, 88]
                })
                
                fig = px.bar(
                    goal_data, x='Goal Type', y='Achievement Rate',
                    title='Goal Achievement Rates (%)',
                    color='Achievement Rate',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Study efficiency analysis
            st.markdown("#### ⚡ Study Efficiency Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                efficiency_score = random.randint(75, 95)
                st.metric(
                    "Overall Efficiency",
                    f"{efficiency_score}%",
                    delta="+5% from last week"
                )
                
                st.progress(efficiency_score / 100)
                
                if efficiency_score >= 90:
                    st.success("🌟 Excellent efficiency!")
                elif efficiency_score >= 80:
                    st.info("👍 Good efficiency!")
                else:
                    st.warning("📈 Room for improvement")
            
            with col2:
                focus_score = random.randint(70, 90)
                st.metric(
                    "Focus Quality",
                    f"{focus_score}%",
                    delta="+2% from last week"
                )
                
                st.progress(focus_score / 100)
                
                # Focus recommendations
                if focus_score < 80:
                    st.info("💡 Try shorter study sessions with more breaks")
            
            with col3:
                retention_score = random.randint(80, 95)
                st.metric(
                    "Knowledge Retention",
                    f"{retention_score}%",
                    delta="+8% from last month"
                )
                
                st.progress(retention_score / 100)
                
                # Retention tips
                if retention_score < 85:
                    st.info("🧠 Review material within 24 hours for better retention")
            
            # Study insights and recommendations
            st.markdown("#### 💡 Personalized Insights")
            
            insights = self._generate_study_insights(user_stats)
            
            for insight in insights:
                insight_type = insight.get('type', 'info')
                message = insight.get('message', '')
                
                if insight_type == 'success':
                    st.success(f"🎉 {message}")
                elif insight_type == 'warning':
                    st.warning(f"⚠️ {message}")
                else:
                    st.info(f"💡 {message}")
            
            # Study pattern recommendations
            st.markdown("#### 📋 Optimization Recommendations")
            
            recommendations = self._generate_study_recommendations(user_stats)
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. **{rec['title']}** - {rec['description']}")
            
        except Exception as e:
            logger.error(f"Error rendering study analytics: {e}")
            st.error("Unable to load study analytics.")
    
    # Helper methods
    def _get_daily_plan(self, user_id: str, date: datetime.date, user_stats: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get or create daily study plan"""
        try:
            # Check if plan exists in session state
            plan_key = f"daily_plan_{user_id}_{date.isoformat()}"
            
            if plan_key in st.session_state:
                return st.session_state[plan_key]
            
            # Generate new plan
            return self._generate_smart_daily_plan(user_id, user_stats, user_data)
            
        except Exception as e:
            logger.error(f"Error getting daily plan: {e}")
            return {'sessions': [], 'total_time': 0, 'subjects_covered': []}
    
    def _generate_smart_daily_plan(self, user_id: str, user_stats: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent daily study plan"""
        try:
            # Get user preferences and weak areas
            subjects_interest = user_data.get('subjects_interest', self.subjects[:3])
            weak_areas = user_stats.get('weak_areas', [])
            daily_goal_time = user_stats.get('daily_goals', {}).get('study_time', 2.0)
            
            # Prioritize subjects (weak areas first)
            priority_subjects = weak_areas + [s for s in subjects_interest if s not in weak_areas]
            
            sessions = []
            total_time = 0
            current_time = "09:00"
            
            # Determine number of sessions based on available time
            if daily_goal_time <= 1.0:
                session_count = 2
                session_duration = 30
            elif daily_goal_time <= 2.0:
                session_count = 3
                session_duration = 40
            else:
                session_count = 4
                session_duration = 45
            
            for i in range(min(session_count, len(priority_subjects))):
                subject = priority_subjects[i]
                
                # Determine session type based on subject priority
                if subject in weak_areas:
                    session_type = "Focus Session"
                    goal = f"Strengthen understanding in {subject}"
                else:
                    session_type = random.choice(["Practice Drill", "Quick Review"])
                    goal = f"Maintain proficiency in {subject}"
                
                session = {
                    'title': f"{subject} {session_type}",
                    'subject': subject,
                    'type': session_type,
                    'duration': session_duration,
                    'start_time': current_time,
                    'goal': goal,
                    'status': 'planned',
                    'difficulty': self._get_adaptive_difficulty(user_stats, subject)
                }
                
                sessions.append(session)
                total_time += session_duration
                
                # Add break and calculate next start time
                break_duration = 15 if i < session_count - 1 else 0
                current_time = self._add_minutes_to_time(current_time, session_duration + break_duration)
            
            plan = {
                'sessions': sessions,
                'total_time': total_time / 60,  # Convert to hours
                'subjects_covered': [s['subject'] for s in sessions],
                'generated_at': datetime.now()
            }
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating smart daily plan: {e}")
            return {'sessions': [], 'total_time': 0, 'subjects_covered': []}
    
    def _render_daily_progress_overview(self, user_stats: Dict[str, Any], daily_plan: Dict[str, Any]):
        """Render daily progress overview"""
        try:
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate daily progress
            completed_sessions = len([s for s in daily_plan.get('sessions', []) if s.get('status') == 'completed'])
            total_sessions = len(daily_plan.get('sessions', []))
            
            study_time_today = user_stats.get('study_time_today', 0)
            study_goal = user_stats.get('daily_goals', {}).get('study_time', 2.0)
            
            problems_today = user_stats.get('problems_solved', 0) % 20  # Daily reset simulation
            problems_goal = user_stats.get('daily_goals', {}).get('problems_solved', 10)
            
            with col1:
                session_progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
                st.metric(
                    "Sessions Progress",
                    f"{completed_sessions}/{total_sessions}",
                    delta=f"{session_progress:.0f}% complete"
                )
            
            with col2:
                time_progress = min(100, (study_time_today / study_goal) * 100)
                st.metric(
                    "Study Time",
                    f"{study_time_today:.1f}h / {study_goal}h",
                    delta=f"{time_progress:.0f}% of goal"
                )
            
            with col3:
                problem_progress = min(100, (problems_today / problems_goal) * 100)
                st.metric(
                    "Problems Solved",
                    f"{problems_today} / {problems_goal}",
                    delta=f"{problem_progress:.0f}% of goal"
                )
            
            with col4:
                overall_progress = (session_progress + time_progress + problem_progress) / 3
                st.metric(
                    "Overall Progress",
                    f"{overall_progress:.0f}%",
                    delta="Today's performance"
                )
            
        except Exception as e:
            logger.error(f"Error rendering daily progress overview: {e}")
    
    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        """Add minutes to a time string"""
        try:
            hour, minute = map(int, time_str.split(':'))
            total_minutes = hour * 60 + minute + minutes
            
            new_hour = (total_minutes // 60) % 24
            new_minute = total_minutes % 60
            
            return f"{new_hour:02d}:{new_minute:02d}"
            
        except Exception as e:
            logger.error(f"Error adding minutes to time: {e}")
            return time_str
    
    def _start_session(self, user_id: str, session: Dict[str, Any], index: int):
        """Start a study session"""
        try:
            session['status'] = 'in_progress'
            session['actual_start_time'] = datetime.now().strftime("%H:%M")
            
            st.success(f"🚀 Started: {session['title']}")
            st.info(f"⏰ Estimated duration: {session['duration']} minutes")
            
            # Could integrate with timer here
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            st.error("Unable to start session.")
    
    def _complete_session(self, user_id: str, session: Dict[str, Any], index: int):
        """Complete a study session"""
        try:
            from utils.enhanced_stats import EnhancedStatsManager
            stats_manager = EnhancedStatsManager()
            
            session['status'] = 'completed'
            session['completed_at'] = datetime.now().strftime("%H:%M")
            
            # Update user stats
            duration_hours = session['duration'] / 60
            stats_manager.update_stats(
                user_id, 'session_completed',
                subject=session['subject'],
                duration=duration_hours,
                session_type=session['type']
            )
            
            st.success(f"✅ Completed: {session['title']}")
            st.balloons()
            
            # Award points
            points_earned = session['duration'] // 5  # 1 point per 5 minutes
            st.info(f"🎯 Earned {points_earned} points!")
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error completing session: {e}")
            st.error("Unable to complete session.")
    
    def _skip_session(self, user_id: str, session: Dict[str, Any], index: int):
        """Skip a study session"""
        try:
            session['status'] = 'skipped'
            session['skipped_at'] = datetime.now().strftime("%H:%M")
            
            st.warning(f"⏭️ Skipped: {session['title']}")
            st.info("No worries! You can always reschedule or try a shorter session.")
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error skipping session: {e}")
            st.error("Unable to skip session.")
    
    def _start_quick_session(self, user_id: str, session_type: str, user_stats: Dict[str, Any]):
        """Start a quick study session"""
        try:
            template = self.session_templates[session_type]
            
            # Create quick session
            session = {
                'title': f"Quick {session_type}",
                'type': template['type'],
                'duration': template['duration'],
                'intensity': template['intensity'],
                'status': 'in_progress',
                'started_at': datetime.now().strftime("%H:%M")
            }
            
            # Store in session state for tracking
            if 'current_quick_session' not in st.session_state:
                st.session_state.current_quick_session = session
            
            st.success(f"🚀 Started {session_type}!")
            st.info(f"⏰ Duration: {template['duration']} minutes")
            st.info(f"💪 Intensity: {template['intensity']}")
            
            # Timer display (simplified)
            st.markdown(f"""
            <div style="background: #f0f0f0; padding: 20px; border-radius: 10px; text-align: center;">
                <h2>⏰ {template['duration']:02d}:00</h2>
                <p>Stay focused! You've got this! 💪</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ Complete Session"):
                self._complete_quick_session(user_id, session)
            
        except Exception as e:
            logger.error(f"Error starting quick session: {e}")
            st.error("Unable to start quick session.")
    
    def _complete_quick_session(self, user_id: str, session: Dict[str, Any]):
        """Complete a quick study session"""
        try:
            from utils.enhanced_stats import EnhancedStatsManager
            stats_manager = EnhancedStatsManager()
            
            # Update stats
            duration_hours = session['duration'] / 60
            stats_manager.update_stats(
                user_id, 'session_completed',
                duration=duration_hours,
                session_type='quick_session'
            )
            
            # Clear current session
            if 'current_quick_session' in st.session_state:
                del st.session_state.current_quick_session
            
            st.success("🎉 Quick session completed!")
            st.balloons()
            
            points = session['duration'] // 5
            st.info(f"🎯 Earned {points} points!")
            
        except Exception as e:
            logger.error(f"Error completing quick session: {e}")
            st.error("Unable to complete session.")
    
    def _generate_daily_insights(self, user_stats: Dict[str, Any], daily_plan: Dict[str, Any]) -> List[str]:
        """Generate daily insights and tips"""
        insights = []
        
        try:
            accuracy = user_stats.get('accuracy_rate', 0)
            streak = user_stats.get('study_streak', 0)
            
            # Accuracy-based insights
            if accuracy >= 85:
                insights.append("🎯 Your accuracy is excellent! Consider challenging yourself with harder problems.")
            elif accuracy >= 70:
                insights.append("📈 Good accuracy! Focus on consistency to reach 85%.")
            else:
                insights.append("📚 Take time to understand concepts deeply before moving to new topics.")
            
            # Streak-based insights
            if streak >= 14:
                insights.append("🔥 Amazing 2-week streak! You're building incredible study habits.")
            elif streak >= 7:
                insights.append("💪 Great weekly streak! Keep the momentum going.")
            elif streak >= 3:
                insights.append("👍 Good consistency! Try to reach a 7-day streak.")
            else:
                insights.append("📅 Focus on studying a little bit every day for better results.")
            
            # Plan-based insights
            subjects_today = daily_plan.get('subjects_covered', [])
            if len(subjects_today) >= 3:
                insights.append("🌟 Great variety in today's plan! This helps with knowledge retention.")
            
            return insights[:3]  # Return top 3 insights
            
        except Exception as e:
            logger.error(f"Error generating daily insights: {e}")
            return ["Keep up the great work! Every study session counts."]
    
    def _get_motivational_message(self, user_stats: Dict[str, Any]) -> str:
        """Get personalized motivational message"""
        try:
            progress = user_stats.get('overall_progress', 0)
            
            if progress >= 80:
                messages = [
                    "🚀 You're a learning superstar! Keep reaching for excellence!",
                    "🌟 Outstanding progress! You're inspiring others with your dedication!",
                    "🏆 You're in the top tier of learners! Stay amazing!"
                ]
            elif progress >= 60:
                messages = [
                    "💪 You're making excellent progress! Every step counts!",
                    "🎯 You're on the right track! Keep building on your success!",
                    "📈 Great momentum! You're closer to your goals than you think!"
                ]
            elif progress >= 30:
                messages = [
                    "🌱 You're growing every day! Small steps lead to big results!",
                    "💫 Every expert was once a beginner. You're doing great!",
                    "🎪 Learning is a journey, and you're making steady progress!"
                ]
            else:
                messages = [
                    "🌟 Every great journey starts with a single step. You've started!",
                    "💪 Believe in yourself! You have everything it takes to succeed!",
                    "🚀 Your potential is unlimited! Take it one lesson at a time!"
                ]
            
            return random.choice(messages)
            
        except Exception as e:
            logger.error(f"Error getting motivational message: {e}")
            return "🌟 You're doing great! Keep learning and growing!"
    
    def _render_weekly_overview(self, user_id: str, week_start: datetime.date, user_stats: Dict[str, Any]):
        """Render weekly overview metrics"""
        try:
            col1, col2, col3, col4 = st.columns(4)
            
            # Mock weekly data
            planned_sessions = random.randint(12, 16)
            completed_sessions = random.randint(8, completed_sessions if 'completed_sessions' in locals() else 12)
            total_study_time = random.uniform(8, 15)
            avg_accuracy = random.uniform(70, 90)
            
            with col1:
                completion_rate = (completed_sessions / planned_sessions) * 100
                st.metric(
                    "Session Completion",
                    f"{completed_sessions}/{planned_sessions}",
                    delta=f"{completion_rate:.0f}%"
                )
            
            with col2:
                st.metric(
                    "Total Study Time",
                    f"{total_study_time:.1f} hours",
                    delta="+2.3 hrs vs last week"
                )
            
            with col3:
                st.metric(
                    "Average Accuracy",
                    f"{avg_accuracy:.1f}%",
                    delta="+5.2% vs last week"
                )
            
            with col4:
                productivity_score = (completion_rate + avg_accuracy) / 2
                st.metric(
                    "Productivity Score",
                    f"{productivity_score:.0f}%",
                    delta="+7% vs last week"
                )
            
        except Exception as e:
            logger.error(f"Error rendering weekly overview: {e}")
    
    def _render_weekly_grid(self, user_id: str, week_start: datetime.date, user_stats: Dict[str, Any], user_data: Dict[str, Any]):
        """Render weekly schedule grid"""
        try:
            st.markdown("#### 📅 Weekly Schedule Grid")
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for i, day in enumerate(days):
                current_date = week_start + timedelta(days=i)
                is_today = current_date == datetime.now().date()
                
                # Day header
                header_style = "background: #667eea; color: white;" if is_today else "background: #f0f0f0;"
                
                st.markdown(f"""
                <div style="{header_style} padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <h4 style="margin: 0;">{day} - {current_date.strftime('%b %d')}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Mock sessions for each day
                if current_date <= datetime.now().date():
                    sessions_count = random.randint(1, 3)
                    for j in range(sessions_count):
                        subject = random.choice(user_data.get('subjects_interest', ['Mathematics', 'Physics']))
                        session_time = f"{9 + j*2}:00"
                        duration = random.choice([25, 30, 45])
                        
                        status = random.choice(['completed', 'completed', 'skipped']) if current_date < datetime.now().date() else 'planned'
                        status_color = {'completed': '#4CAF50', 'skipped': '#9E9E9E', 'planned': '#2196F3'}[status]
                        status_icon = {'completed': '✅', 'skipped': '⏭️', 'planned': '⏳'}[status]
                        
                        st.markdown(f"""
                        <div style="background: {status_color}20; border-left: 4px solid {status_color}; 
                                    padding: 8px; margin: 3px 0; border-radius: 3px;">
                            {status_icon} {session_time} - {subject} ({duration}min)
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
            
        except Exception as e:
            logger.error(f"Error rendering weekly grid: {e}")
    
    def _render_longterm_goals(self, user_id: str, user_stats: Dict[str, Any], user_data: Dict[str, Any]):
        """Render long-term goals interface"""
        try:
            # Get existing long-term goals
            longterm_goals = user_stats.get('longterm_goals', [])
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if longterm_goals:
                    st.markdown("#### 🎯 Your Long-term Goals")
                    
                    for i, goal in enumerate(longterm_goals):
                        progress = goal.get('progress', 0)
                        target_date = goal.get('target_date', 'No deadline')
                        
                        st.markdown(f"""
                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0;">
                            <h5>{goal['title']}</h5>
                            <p>{goal['description']}</p>
                            <p><strong>Target:</strong> {target_date}</p>
                            <div style="background: #f0f0f0; border-radius: 10px; height: 8px;">
                                <div style="background: #4CAF50; width: {progress}%; height: 100%; border-radius: 10px;"></div>
                            </div>
                            <small>{progress}% complete</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No long-term goals set yet. Create your first learning goal!")
            
            with col2:
                st.markdown("#### ➕ Add New Goal")
                
                with st.form("add_longterm_goal"):
                    goal_title = st.text_input("Goal Title", placeholder="e.g., Master Calculus")
                    goal_description = st.text_area("Description", placeholder="What do you want to achieve?")
                    goal_category = st.selectbox("Category", ["Academic", "Skill Building", "Test Prep", "Personal Interest"])
                    target_date = st.date_input("Target Date", value=datetime.now().date() + timedelta(days=90))
                    
                    if st.form_submit_button("🎯 Add Goal"):
                        if goal_title and goal_description:
                            new_goal = {
                                'title': goal_title,
                                'description': goal_description,
                                'category': goal_category,
                                'target_date': target_date.strftime('%Y-%m-%d'),
                                'progress': 0,
                                'created_at': datetime.now().isoformat()
                            }
                            
                            if 'longterm_goals' not in user_stats:
                                user_stats['longterm_goals'] = []
                            
                            user_stats['longterm_goals'].append(new_goal)
                            st.success("🎉 Goal added successfully!")
                            st.rerun()
            
        except Exception as e:
            logger.error(f"Error rendering longterm goals: {e}")
    
    def _calculate_daily_progress(self, user_stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate daily progress towards goals"""
        try:
            return {
                'study_time': user_stats.get('study_time_today', 0),
                'problems_solved': user_stats.get('problems_solved', 0) % 20,  # Daily reset
                'sessions_completed': user_stats.get('sessions_completed', 0) % 10  # Daily reset
            }
        except Exception as e:
            logger.error(f"Error calculating daily progress: {e}")
            return {'study_time': 0, 'problems_solved': 0, 'sessions_completed': 0}
    
    def _calculate_weekly_study_time(self, user_id: str, week_start: datetime.date) -> float:
        """Calculate study time for the week"""
        try:
            # Mock calculation - in real app, would sum from database
            return random.uniform(5, 12)
        except Exception as e:
            logger.error(f"Error calculating weekly study time: {e}")
            return 0
    
    def _update_user_goals(self, user_id: str, new_goals: Dict[str, Any]):
        """Update user's goals"""
        try:
            if user_id in st.session_state.user_stats:
                st.session_state.user_stats[user_id].update(new_goals)
        except Exception as e:
            logger.error(f"Error updating user goals: {e}")
    
    def _get_adaptive_difficulty(self, user_stats: Dict[str, Any], subject: str) -> str:
        """Get adaptive difficulty for subject"""
        try:
            subject_stats = user_stats.get('subject_stats', {}).get(subject, {})
            accuracy = subject_stats.get('accuracy', user_stats.get('accuracy_rate', 0))
            
            if accuracy >= 85:
                return "Advanced"
            elif accuracy >= 70:
                return "Intermediate"
            else:
                return "Beginner"
        except Exception as e:
            logger.error(f"Error getting adaptive difficulty: {e}")
            return "Beginner"
    
    def _save_daily_plan(self, user_id: str, date: datetime.date, plan: Dict[str, Any]):
        """Save daily plan to session state"""
        try:
            plan_key = f"daily_plan_{user_id}_{date.isoformat()}"
            st.session_state[plan_key] = plan
        except Exception as e:
            logger.error(f"Error saving daily plan: {e}")
    
    def _generate_study_insights(self, user_stats: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate study insights and recommendations"""
        insights = []
        
        try:
            accuracy = user_stats.get('accuracy_rate', 0)
            streak = user_stats.get('study_streak', 0)
            total_time = user_stats.get('total_study_time', 0)
            
            # Accuracy insights
            if accuracy >= 90:
                insights.append({
                    'type': 'success',
                    'message': 'Outstanding accuracy! You have mastered the fundamentals.'
                })
            elif accuracy < 60:
                insights.append({
                    'type': 'warning',
                    'message': 'Focus on understanding concepts deeply rather than rushing through problems.'
                })
            
            # Streak insights
            if streak >= 21:
                insights.append({
                    'type': 'success',
                    'message': 'Incredible 3-week streak! Your consistency is paying off tremendously.'
                })
            elif streak == 0:
                insights.append({
                    'type': 'info',
                    'message': 'Start a study streak today! Even 15 minutes daily makes a huge difference.'
                })
            
            # Study time insights
            if total_time >= 50:
                insights.append({
                    'type': 'success',
                    'message': 'You\'ve put in serious study hours! Your dedication is impressive.'
                })
            elif total_time < 10:
                insights.append({
                    'type': 'info',
                    'message': 'Consider increasing your study time gradually for better results.'
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating study insights: {e}")
            return [{'type': 'info', 'message': 'Keep up the great work!'}]
    
    def _generate_study_recommendations(self, user_stats: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate study recommendations"""
        recommendations = []
        
        try:
            accuracy = user_stats.get('accuracy_rate', 0)
            streak = user_stats.get('study_streak', 0)
            
            if accuracy < 70:
                recommendations.append({
                    'title': 'Focus on Quality',
                    'description': 'Spend more time understanding each concept thoroughly before moving on.'
                })
            
            if streak < 5:
                recommendations.append({
                    'title': 'Build Consistency',
                    'description': 'Aim for at least 20 minutes of study every day to build momentum.'
                })
            
            recommendations.extend([
                {
                    'title': 'Use Active Recall',
                    'description': 'Test yourself regularly instead of just re-reading material.'
                },
                {
                    'title': 'Take Strategic Breaks',
                    'description': 'Use the Pomodoro Technique: 25 minutes study, 5 minutes break.'
                },
                {
                    'title': 'Track Your Progress',
                    'description': 'Regular progress monitoring helps maintain motivation and direction.'
                }
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [{'title': 'Stay Consistent', 'description': 'Regular practice is key to success!'}]
