"""
Enhanced chart and visualization components for EduTech AI Learning Platform
Copy this code into components/better_charts.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class BetterCharts:
    """Enhanced visualization components for learning analytics"""
    
    def __init__(self):
        self.color_scheme = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'info': '#2196F3',
            'background': '#f8f9fa'
        }
    
    def render_progress_dashboard(self, user_id: str, stats: Dict[str, Any]):
        """Render comprehensive progress dashboard"""
        try:
            st.subheader("📊 Learning Analytics Dashboard")
            
            # Progress overview cards
            self._render_progress_cards(stats)
            
            # Main charts
            col1, col2 = st.columns(2)
            
            with col1:
                self._render_subject_progress_chart(user_id, stats)
                self._render_accuracy_trend_chart(stats)
            
            with col2:
                self._render_activity_calendar(stats)
                self._render_performance_radar(stats)
            
            # Detailed analytics
            self._render_detailed_analytics(user_id, stats)
            
        except Exception as e:
            logger.error(f"Error rendering progress dashboard: {e}")
            st.error("Unable to load analytics dashboard.")
    
    def _render_progress_cards(self, stats: Dict[str, Any]):
        """Render animated progress cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        progress = stats.get('overall_progress', 0)
        streak = stats.get('study_streak', 0)
        accuracy = stats.get('accuracy_rate', 0)
        level = stats.get('level', 1)
        
        with col1:
            self._create_animated_metric_card(
                "📊 Overall Progress", 
                f"{progress:.1f}%", 
                progress, 
                "success" if progress >= 75 else "warning" if progress >= 50 else "info"
            )
        
        with col2:
            self._create_animated_metric_card(
                "🔥 Study Streak", 
                f"{streak} days", 
                min(streak * 3.33, 100),  # Max at 30 days
                "success" if streak >= 7 else "warning" if streak >= 3 else "info"
            )
        
        with col3:
            self._create_animated_metric_card(
                "🎯 Accuracy Rate", 
                f"{accuracy:.1f}%", 
                accuracy,
                "success" if accuracy >= 80 else "warning" if accuracy >= 60 else "error"
            )
        
        with col4:
            xp = stats.get('experience_points', 0)
            next_level_xp = (level ** 2) * 100
            level_progress = (xp % next_level_xp) / next_level_xp * 100
            
            self._create_animated_metric_card(
                "⭐ Level", 
                f"Level {level}", 
                level_progress,
                "primary"
            )
    
    def _create_animated_metric_card(self, title: str, value: str, progress: float, color_type: str):
        """Create an animated metric card with progress bar"""
        color = self.color_scheme.get(color_type, self.color_scheme['info'])
        
        st.markdown(f"""
        <div class="metric-card-enhanced" style="
            background: linear-gradient(135deg, {color}15, {color}05);
            border: 2px solid {color}30;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            height: 150px;
            position: relative;
            overflow: hidden;
        ">
            <div style="position: relative; z-index: 2;">
                <h4 style="color: {color}; margin: 0; font-size: 0.9em;">{title}</h4>
                <h2 style="color: {color}; margin: 10px 0; font-weight: bold;">{value}</h2>
                <div style="
                    background: #e0e0e0; 
                    border-radius: 10px; 
                    height: 8px; 
                    margin: 10px 0;
                    overflow: hidden;
                ">
                    <div style="
                        background: {color}; 
                        width: {progress}%; 
                        height: 100%; 
                        border-radius: 10px;
                        transition: width 2s ease-in-out;
                    "></div>
                </div>
                <small style="color: {color}80;">{progress:.0f}% Complete</small>
            </div>
            <div style="
                position: absolute;
                top: -50%;
                right: -50%;
                width: 100%;
                height: 100%;
                background: {color}10;
                border-radius: 50%;
                z-index: 1;
            "></div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_subject_progress_chart(self, user_id: str, stats: Dict[str, Any]):
        """Render interactive subject progress chart"""
        st.subheader("📚 Subject Progress")
        
        try:
            # Get subject data
            user_data = st.session_state.all_users.get(user_id, {})
            subject_progress = user_data.get('progress', {})
            subject_stats = stats.get('subject_stats', {})
            
            if not subject_progress:
                st.info("Start practicing to see your subject progress!")
                return
            
            # Prepare data
            chart_data = []
            for subject, progress in subject_progress.items():
                subject_data = subject_stats.get(subject, {})
                accuracy = subject_data.get('accuracy', 0)
                problems_solved = subject_data.get('total_problems', 0)
                
                chart_data.append({
                    'Subject': subject,
                    'Progress': progress,
                    'Accuracy': accuracy,
                    'Problems Solved': problems_solved,
                    'Target': 80  # Target progress
                })
            
            df = pd.DataFrame(chart_data)
            
            # Create interactive bar chart
            fig = go.Figure()
            
            # Progress bars
            fig.add_trace(go.Bar(
                name='Current Progress',
                x=df['Subject'],
                y=df['Progress'],
                marker_color=self.color_scheme['primary'],
                text=df['Progress'].apply(lambda x: f'{x:.0f}%'),
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Progress: %{y:.1f}%<br>Problems: %{customdata}<extra></extra>',
                customdata=df['Problems Solved']
            ))
            
            # Target line
            fig.add_trace(go.Scatter(
                name='Target (80%)',
                x=df['Subject'],
                y=df['Target'],
                mode='markers+lines',
                marker=dict(color=self.color_scheme['success'], size=8, symbol='diamond'),
                line=dict(color=self.color_scheme['success'], width=2, dash='dash')
            ))
            
            fig.update_layout(
                title='Subject Progress vs Target',
                yaxis_title='Progress (%)',
                template='plotly_white',
                height=400,
                showlegend=True,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Progress insights
            weak_subjects = [subj for subj, prog in subject_progress.items() if prog < 60]
            strong_subjects = [subj for subj, prog in subject_progress.items() if prog >= 80]
            
            if weak_subjects:
                st.warning(f"🎯 **Focus on:** {', '.join(weak_subjects[:3])}")
            if strong_subjects:
                st.success(f"🌟 **Excelling in:** {', '.join(strong_subjects[:3])}")
            
        except Exception as e:
            logger.error(f"Error rendering subject progress chart: {e}")
            st.error("Unable to load subject progress chart.")
    
    def _render_accuracy_trend_chart(self, stats: Dict[str, Any]):
        """Render accuracy trend over time"""
        st.subheader("📈 Accuracy Trend")
        
        try:
            # Generate sample trend data (in real app, this would come from database)
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            base_accuracy = stats.get('accuracy_rate', 60)
            
            # Simulate improving trend with some noise
            trend_data = []
            for i, date in enumerate(dates):
                # Base improvement over time with random variation
                accuracy = base_accuracy + (i * 0.5) + np.random.normal(0, 5)
                accuracy = max(30, min(100, accuracy))  # Clamp between 30-100
                
                trend_data.append({
                    'Date': date,
                    'Accuracy': accuracy,
                    'Moving Average': None
                })
            
            df = pd.DataFrame(trend_data)
            
            # Calculate moving average
            df['Moving Average'] = df['Accuracy'].rolling(window=7, center=True).mean()
            
            # Create trend chart
            fig = go.Figure()
            
            # Daily accuracy (light line)
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Accuracy'],
                mode='lines',
                name='Daily Accuracy',
                line=dict(color=self.color_scheme['info'], width=1, dash='dot'),
                opacity=0.6
            ))
            
            # Moving average (bold line)
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Moving Average'],
                mode='lines',
                name='7-Day Average',
                line=dict(color=self.color_scheme['primary'], width=3),
                fill='tonexty',
                fillcolor=f"{self.color_scheme['primary']}20"
            ))
            
            # Target line
            fig.add_hline(
                y=80, 
                line_dash="dash", 
                line_color=self.color_scheme['success'],
                annotation_text="Target: 80%"
            )
            
            fig.update_layout(
                title='Accuracy Trend (Last 30 Days)',
                xaxis_title='Date',
                yaxis_title='Accuracy (%)',
                template='plotly_white',
                height=400,
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trend analysis
            recent_avg = df['Moving Average'].dropna().iloc[-7:].mean()
            older_avg = df['Moving Average'].dropna().iloc[:7].mean()
            
            if not np.isnan(recent_avg) and not np.isnan(older_avg):
                improvement = recent_avg - older_avg
                if improvement > 5:
                    st.success(f"📈 Great improvement! +{improvement:.1f}% accuracy over the month!")
                elif improvement > 0:
                    st.info(f"📊 Steady progress: +{improvement:.1f}% accuracy improvement")
                else:
                    st.warning("📚 Focus on accuracy - review problem-solving strategies")
            
        except Exception as e:
            logger.error(f"Error rendering accuracy trend: {e}")
            st.error("Unable to load accuracy trend.")
    
    def _render_activity_calendar(self, stats: Dict[str, Any]):
        """Render activity calendar heatmap"""
        st.subheader("📅 Activity Calendar")
        
        try:
            # Generate activity data for last 12 weeks
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=84)  # 12 weeks
            
            activity_data = []
            current_streak = stats.get('study_streak', 0)
            
            # Generate sample activity data
            for i in range(84):
                date = start_date + timedelta(days=i)
                
                # Simulate activity based on current streak and random variation
                if i >= (84 - current_streak):
                    activity_level = np.random.randint(1, 4)  # Active recent days
                else:
                    activity_level = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])  # Less active older days
                
                activity_data.append({
                    'Date': date,
                    'Activity': activity_level,
                    'Week': date.isocalendar()[1],
                    'Weekday': date.weekday()
                })
            
            df = pd.DataFrame(activity_data)
            
            # Create calendar heatmap
            weeks = df['Week'].unique()
            weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            # Create matrix for heatmap
            calendar_matrix = np.zeros((len(weekdays), len(weeks)))
            date_matrix = np.empty((len(weekdays), len(weeks)), dtype=object)
            
            for _, row in df.iterrows():
                week_idx = list(weeks).index(row['Week'])
                day_idx = row['Weekday']
                calendar_matrix[day_idx, week_idx] = row['Activity']
                date_matrix[day_idx, week_idx] = row['Date'].strftime('%Y-%m-%d')
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=calendar_matrix,
                x=[f"Week {w}" for w in weeks],
                y=weekdays,
                colorscale=[
                    [0, '#ebedf0'],      # No activity
                    [0.33, '#c6e48b'],   # Light activity
                    [0.66, '#7bc96f'],   # Medium activity  
                    [1.0, '#239a3b']     # High activity
                ],
                showscale=True,
                colorbar=dict(
                    title="Activity Level",
                    tickvals=[0, 1, 2, 3],
                    ticktext=['None', 'Light', 'Medium', 'High']
                ),
                hovertemplate='<b>%{text}</b><br>Activity: %{z}<extra></extra>',
                text=date_matrix
            ))
            
            fig.update_layout(
                title='Study Activity Calendar (Last 12 Weeks)',
                height=300,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Activity insights
            total_active_days = len(df[df['Activity'] > 0])
            activity_percentage = (total_active_days / 84) * 100
            
            if activity_percentage >= 70:
                st.success(f"🔥 Excellent consistency! Active {activity_percentage:.0f}% of days")
            elif activity_percentage >= 50:
                st.info(f"📊 Good consistency: {activity_percentage:.0f}% active days")
            else:
                st.warning(f"📈 Room for improvement: {activity_percentage:.0f}% active days")
            
        except Exception as e:
            logger.error(f"Error rendering activity calendar: {e}")
            st.error("Unable to load activity calendar.")
    
    def _render_performance_radar(self, stats: Dict[str, Any]):
        """Render performance radar chart"""
        st.subheader("🎯 Performance Radar")
        
        try:
            # Define performance dimensions
            dimensions = [
                'Accuracy',
                'Consistency', 
                'Speed',
                'Difficulty Level',
                'Problem Variety',
                'Study Time'
            ]
            
            # Calculate scores for each dimension (0-100)
            accuracy_score = stats.get('accuracy_rate', 0)
            consistency_score = min(stats.get('study_streak', 0) * 10, 100)
            speed_score = min(stats.get('problems_solved', 0) * 2, 100)
            difficulty_score = {'Beginner': 25, 'Intermediate': 60, 'Advanced': 100}.get(
                stats.get('difficulty_preference', 'Beginner'), 25
            )
            variety_score = min(len(stats.get('subject_stats', {})) * 20, 100)
            time_score = min(stats.get('total_study_time', 0) * 5, 100)
            
            scores = [
                accuracy_score,
                consistency_score,
                speed_score,
                difficulty_score,
                variety_score,
                time_score
            ]
            
            # Create radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=dimensions,
                fill='toself',
                name='Your Performance',
                line_color=self.color_scheme['primary'],
                fillcolor=f"{self.color_scheme['primary']}30"
            ))
            
            # Add target performance
            target_scores = [80] * len(dimensions)  # Target 80% in all areas
            fig.add_trace(go.Scatterpolar(
                r=target_scores,
                theta=dimensions,
                fill='toself',
                name='Target Level',
                line_color=self.color_scheme['success'],
                line_dash='dash',
                fillcolor=f"{self.color_scheme['success']}10"
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title='Performance Across Key Areas',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance insights
            strong_areas = [dim for dim, score in zip(dimensions, scores) if score >= 70]
            weak_areas = [dim for dim, score in zip(dimensions, scores) if score < 50]
            
            if strong_areas:
                st.success(f"💪 **Strengths:** {', '.join(strong_areas[:3])}")
            if weak_areas:
                st.info(f"🎯 **Areas for Growth:** {', '.join(weak_areas[:3])}")
            
        except Exception as e:
            logger.error(f"Error rendering performance radar: {e}")
            st.error("Unable to load performance radar.")
    
    def _render_detailed_analytics(self, user_id: str, stats: Dict[str, Any]):
        """Render detailed analytics section"""
        st.subheader("📈 Detailed Analytics")
        
        tab1, tab2, tab3 = st.tabs(["🏆 Achievements", "📊 Study Patterns", "🎯 Goal Progress"])
        
        with tab1:
            self._render_achievement_analytics(user_id, stats)
        
        with tab2:
            self._render_study_pattern_analytics(stats)
        
        with tab3:
            self._render_goal_progress_analytics(stats)
    
    def _render_achievement_analytics(self, user_id: str, stats: Dict[str, Any]):
        """Render achievement analytics"""
        try:
            from utils.achievements import AchievementManager
            achievement_manager = AchievementManager()
            
            achievement_stats = achievement_manager.get_achievement_stats(user_id)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Achievement completion chart
                category_progress = achievement_stats.get('category_progress', {})
                
                if category_progress:
                    categories = list(category_progress.keys())
                    percentages = [progress['percentage'] for progress in category_progress.values()]
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=categories,
                            y=percentages,
                            marker_color=self.color_scheme['primary'],
                            text=[f"{p:.0f}%" for p in percentages],
                            textposition='auto'
                        )
                    ])
                    
                    fig.update_layout(
                        title='Achievement Progress by Category',
                        yaxis_title='Completion (%)',
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Achievement timeline
                recent_achievements = achievement_stats.get('recent_achievements', [])
                
                if recent_achievements:
                    timeline_data = []
                    for ach in recent_achievements[-5:]:  # Last 5 achievements
                        timeline_data.append({
                            'Achievement': ach['name'][:20] + '...' if len(ach['name']) > 20 else ach['name'],
                            'Points': ach['points'],
                            'Date': ach.get('timestamp', datetime.now())
                        })
                    
                    df = pd.DataFrame(timeline_data)
                    
                    fig = go.Figure(data=[
                        go.Scatter(
                            x=df['Date'],
                            y=df['Points'],
                            mode='markers+lines',
                            marker=dict(
                                size=df['Points'] / 2,
                                color=self.color_scheme['success'],
                                sizemode='diameter'
                            ),
                            text=df['Achievement'],
                            hovertemplate='<b>%{text}</b><br>Points: %{y}<br>Date: %{x}<extra></extra>'
                        )
                    ])
                    
                    fig.update_layout(
                        title='Recent Achievement Timeline',
                        xaxis_title='Date',
                        yaxis_title='Points',
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("🏆 Start practicing to earn your first achievements!")
            
        except Exception as e:
            logger.error(f"Error rendering achievement analytics: {e}")
            st.error("Unable to load achievement analytics.")
    
    def _render_study_pattern_analytics(self, stats: Dict[str, Any]):
        """Render study pattern analytics"""
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                # Study time distribution (mock data)
                hours = list(range(24))
                study_intensity = []
                
                for hour in hours:
                    if 6 <= hour <= 8:  # Morning peak
                        intensity = np.random.randint(20, 40)
                    elif 14 <= hour <= 16:  # Afternoon peak
                        intensity = np.random.randint(30, 50)
                    elif 19 <= hour <= 21:  # Evening peak
                        intensity = np.random.randint(25, 45)
                    else:
                        intensity = np.random.randint(0, 15)
                    
                    study_intensity.append(intensity)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=hours,
                        y=study_intensity,
                        marker_color=self.color_scheme['info'],
                        text=[f"{i}%" for i in study_intensity],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title='Study Time Distribution by Hour',
                    xaxis_title='Hour of Day',
                    yaxis_title='Study Intensity (%)',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Find peak hours
                peak_hour = hours[np.argmax(study_intensity)]
                st.info(f"🕐 **Peak Performance:** {peak_hour}:00 - {peak_hour+1}:00")
            
            with col2:
                # Weekly pattern
                weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                weekly_activity = [
                    np.random.randint(40, 80),  # Mon
                    np.random.randint(50, 90),  # Tue
                    np.random.randint(45, 85),  # Wed
                    np.random.randint(40, 80),  # Thu
                    np.random.randint(30, 70),  # Fri
                    np.random.randint(20, 60),  # Sat
                    np.random.randint(25, 65),  # Sun
                ]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=weekdays,
                        y=weekly_activity,
                        marker_color=self.color_scheme['secondary'],
                        text=[f"{a}%" for a in weekly_activity],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title='Weekly Study Pattern',
                    xaxis_title='Day of Week',
                    yaxis_title='Activity Level (%)',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Best day
                best_day = weekdays[np.argmax(weekly_activity)]
                st.info(f"📅 **Most Productive Day:** {best_day}")
            
        except Exception as e:
            logger.error(f"Error rendering study pattern analytics: {e}")
            st.error("Unable to load study pattern analytics.")
    
    def _render_goal_progress_analytics(self, stats: Dict[str, Any]):
        """Render goal progress analytics"""
        try:
            # Get daily goals
            daily_goals = stats.get('daily_goals', {
                'study_time': 2.0,
                'problems_solved': 10,
                'sessions_completed': 2
            })
            
            # Calculate current progress
            current_progress = {
                'study_time': stats.get('study_time_today', 0),
                'problems_solved': stats.get('problems_solved', 0) % 20,  # Daily reset simulation
                'sessions_completed': stats.get('sessions_completed', 0) % 10  # Daily reset simulation
            }
            
            # Create goal progress chart
            goals = list(daily_goals.keys())
            targets = list(daily_goals.values())
            current = list(current_progress.values())
            progress_pct = [(c/t)*100 if t > 0 else 0 for c, t in zip(current, targets)]
            
            fig = go.Figure()
            
            # Current progress
            fig.add_trace(go.Bar(
                name='Current Progress',
                x=goals,
                y=current,
                marker_color=self.color_scheme['primary'],
                text=[f"{p:.0f}%" for p in progress_pct],
                textposition='auto'
            ))
            
            # Targets
            fig.add_trace(go.Bar(
                name='Daily Target',
                x=goals,
                y=targets,
                marker_color=self.color_scheme['success'],
                opacity=0.6
            ))
            
            fig.update_layout(
                title='Daily Goal Progress',
                yaxis_title='Count / Hours',
                barmode='overlay',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Goal insights
            completed_goals = sum(1 for p in progress_pct if p >= 100)
            total_goals = len(goals)
            
            if completed_goals == total_goals:
                st.success("🎉 All daily goals completed! Consider setting higher targets.")
            elif completed_goals > 0:
                st.info(f"💪 {completed_goals}/{total_goals} daily goals completed!")
            else:
                st.warning("🎯 Focus on reaching your daily goals for better progress.")
            
            # Weekly goal progress
            st.subheader("📊 Weekly Goal Tracking")
            
            # Simulate weekly progress
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            weekly_completion = [
                np.random.randint(60, 100) if i < 4 else np.random.randint(30, 80) 
                for i in range(7)
            ]
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=days,
                    y=weekly_completion,
                    mode='lines+markers',
                    marker=dict(size=8, color=self.color_scheme['info']),
                    line=dict(width=3, color=self.color_scheme['info']),
                    fill='tonexty',
                    fillcolor=f"{self.color_scheme['info']}20"
                )
            ])
            
            fig.add_hline(
                y=100, 
                line_dash="dash", 
                line_color=self.color_scheme['success'],
                annotation_text="100% Goal"
            )
            
            fig.update_layout(
                title='Weekly Goal Completion Trend',
                xaxis_title='Day',
                yaxis_title='Goal Completion (%)',
                height=300,
                yaxis=dict(range=[0, 120])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Error rendering goal progress analytics: {e}")
            st.error("Unable to load goal progress analytics.")
    
    def render_comparison_chart(self, user_stats: Dict[str, Any], comparison_data: Dict[str, Any]):
        """Render comparison chart with peers or previous performance"""
        try:
            st.subheader("📊 Performance Comparison")
            
            metrics = ['Accuracy', 'Problems Solved', 'Study Time', 'Streak']
            user_values = [
                user_stats.get('accuracy_rate', 0),
                user_stats.get('problems_solved', 0),
                user_stats.get('total_study_time', 0),
                user_stats.get('study_streak', 0)
            ]
            
            comparison_values = [
                comparison_data.get('avg_accuracy', 70),
                comparison_data.get('avg_problems', 50),
                comparison_data.get('avg_study_time', 20),
                comparison_data.get('avg_streak', 5)
            ]
            
            # Normalize values for comparison (scale to 0-100)
            user_normalized = [
                user_values[0],  # Accuracy already 0-100
                min(user_values[1] * 2, 100),  # Problems * 2, max 100
                min(user_values[2] * 5, 100),  # Study time * 5, max 100
                min(user_values[3] * 10, 100)  # Streak * 10, max 100
            ]
            
            comparison_normalized = [
                comparison_values[0],  # Accuracy already 0-100
                min(comparison_values[1] * 2, 100),  # Problems * 2, max 100
                min(comparison_values[2] * 5, 100),  # Study time * 5, max 100
                min(comparison_values[3] * 10, 100)  # Streak * 10, max 100
            ]
            
            # Create comparison chart
            x = np.arange(len(metrics))
            width = 0.35
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Your Performance',
                x=metrics,
                y=user_normalized,
                marker_color=self.color_scheme['primary'],
                text=[f"{v:.0f}" for v in user_values],
                textposition='auto'
            ))
            
            fig.add_trace(go.Bar(
                name='Class Average',
                x=metrics,
                y=comparison_normalized,
                marker_color=self.color_scheme['secondary'],
                text=[f"{v:.0f}" for v in comparison_values],
                textposition='auto'
            ))
            
            fig.update_layout(
                title='Performance vs Class Average',
                yaxis_title='Normalized Score (0-100)',
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance insights
            outperforming = sum(1 for u, c in zip(user_normalized, comparison_normalized) if u > c)
            total_metrics = len(metrics)
            
            if outperforming >= 3:
                st.success(f"🌟 Excellent! You're above average in {outperforming}/{total_metrics} areas!")
            elif outperforming >= 2:
                st.info(f"👍 Good work! You're above average in {outperforming}/{total_metrics} areas.")
            else:
                st.info("📈 Keep working! Focus on the areas where you can improve.")
            
        except Exception as e:
            logger.error(f"Error rendering comparison chart: {e}")
            st.error("Unable to load comparison chart.")
    
    def render_learning_velocity_chart(self, stats: Dict[str, Any]):
        """Render learning velocity and efficiency metrics"""
        try:
            st.subheader("⚡ Learning Velocity")
            
            # Generate velocity data over time
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            
            velocity_data = []
            base_velocity = stats.get('learning_velocity', 10)
            
            for i, date in enumerate(dates):
                # Simulate improving velocity with fluctuations
                velocity = base_velocity + (i * 0.3) + np.random.normal(0, 2)
                velocity = max(5, velocity)  # Minimum velocity
                
                efficiency = min(100, 50 + (i * 1.2) + np.random.normal(0, 5))
                efficiency = max(30, efficiency)  # Minimum efficiency
                
                velocity_data.append({
                    'Date': date,
                    'Learning Velocity': velocity,
                    'Efficiency': efficiency
                })
            
            df = pd.DataFrame(velocity_data)
            
            # Create dual-axis chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Learning velocity
            fig.add_trace(
                go.Scatter(
                    x=df['Date'],
                    y=df['Learning Velocity'],
                    mode='lines',
                    name='Learning Velocity',
                    line=dict(color=self.color_scheme['primary'], width=3)
                ),
                secondary_y=False,
            )
            
            # Efficiency
            fig.add_trace(
                go.Scatter(
                    x=df['Date'],
                    y=df['Efficiency'],
                    mode='lines',
                    name='Efficiency',
                    line=dict(color=self.color_scheme['success'], width=2, dash='dot')
                ),
                secondary_y=True,
            )
            
            # Set axis titles
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Points per Hour", secondary_y=False)
            fig.update_yaxes(title_text="Efficiency (%)", secondary_y=True)
            
            fig.update_layout(
                title='Learning Velocity & Efficiency Trends',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Velocity insights
            current_velocity = df['Learning Velocity'].iloc[-1]
            avg_velocity = df['Learning Velocity'].mean()
            
            if current_velocity > avg_velocity * 1.2:
                st.success(f"🚀 Learning acceleration detected! Current velocity: {current_velocity:.1f} points/hour")
            elif current_velocity > avg_velocity:
                st.info(f"📈 Good learning pace: {current_velocity:.1f} points/hour")
            else:
                st.warning(f"🎯 Focus on efficiency: {current_velocity:.1f} points/hour")
            
        except Exception as e:
            logger.error(f"Error rendering learning velocity chart: {e}")
            st.error("Unable to load learning velocity chart.")
    
    def render_subject_mastery_chart(self, user_id: str, stats: Dict[str, Any]):
        """Render subject mastery progression chart"""
        try:
            st.subheader("🎓 Subject Mastery Progression")
            
            subject_stats = stats.get('subject_stats', {})
            
            if not subject_stats:
                st.info("Start practicing different subjects to see mastery progression!")
                return
            
            # Prepare mastery data
            mastery_data = []
            for subject, data in subject_stats.items():
                problems = data.get('total_problems', 0)
                accuracy = data.get('accuracy', 0)
                
                # Calculate mastery level (0-100)
                mastery = min(100, (problems * 2) + (accuracy * 0.5))
                
                # Determine mastery level
                if mastery >= 80:
                    level = "Expert"
                    color = self.color_scheme['success']
                elif mastery >= 60:
                    level = "Advanced"
                    color = self.color_scheme['primary']
                elif mastery >= 40:
                    level = "Intermediate"
                    color = self.color_scheme['info']
                else:
                    level = "Beginner"
                    color = self.color_scheme['warning']
                
                mastery_data.append({
                    'Subject': subject,
                    'Mastery': mastery,
                    'Level': level,
                    'Color': color,
                    'Problems': problems,
                    'Accuracy': accuracy
                })
            
            df = pd.DataFrame(mastery_data)
            df = df.sort_values('Mastery', ascending=True)  # Sort for better visualization
            
            # Create horizontal bar chart
            fig = go.Figure()
            
            for _, row in df.iterrows():
                fig.add_trace(go.Bar(
                    name=row['Subject'],
                    x=[row['Mastery']],
                    y=[row['Subject']],
                    orientation='h',
                    marker_color=row['Color'],
                    text=f"{row['Level']} ({row['Mastery']:.0f}%)",
                    textposition='auto',
                    hovertemplate=f"<b>{row['Subject']}</b><br>" +
                                f"Mastery: {row['Mastery']:.0f}%<br>" +
                                f"Level: {row['Level']}<br>" +
                                f"Problems: {row['Problems']}<br>" +
                                f"Accuracy: {row['Accuracy']:.1f}%<extra></extra>"
                ))
            
            fig.update_layout(
                title='Subject Mastery Levels',
                xaxis_title='Mastery Level (%)',
                yaxis_title='Subjects',
                height=max(300, len(df) * 60),
                showlegend=False,
                xaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mastery insights
            expert_subjects = df[df['Level'] == 'Expert']['Subject'].tolist()
            beginner_subjects = df[df['Level'] == 'Beginner']['Subject'].tolist()
            
            if expert_subjects:
                st.success(f"🏆 **Expert Level:** {', '.join(expert_subjects)}")
            if beginner_subjects:
                st.info(f"📚 **Focus Areas:** {', '.join(beginner_subjects)} need more practice")
            
            # Next milestone
            closest_to_next_level = None
            min_gap = float('inf')
            
            for _, row in df.iterrows():
                current = row['Mastery']
                if current < 40:  # To Intermediate
                    gap = 40 - current
                    next_level = "Intermediate"
                elif current < 60:  # To Advanced
                    gap = 60 - current
                    next_level = "Advanced"
                elif current < 80:  # To Expert
                    gap = 80 - current
                    next_level = "Expert"
                else:
                    continue
                
                if gap < min_gap:
                    min_gap = gap
                    closest_to_next_level = (row['Subject'], next_level, gap)
            
            if closest_to_next_level:
                subject, next_level, gap = closest_to_next_level
                st.info(f"🎯 **Next Milestone:** {subject} is {gap:.0f}% away from {next_level} level!")
            
        except Exception as e:
            logger.error(f"Error rendering subject mastery chart: {e}")
            st.error("Unable to load subject mastery chart.")
    
    def render_study_session_timeline(self, stats: Dict[str, Any]):
        """Render study session timeline"""
        try:
            st.subheader("📚 Study Session Timeline")
            
            # Generate mock session data
            sessions = []
            base_date = datetime.now() - timedelta(days=7)
            
            for i in range(15):  # Last 15 sessions
                session_date = base_date + timedelta(
                    days=np.random.randint(0, 7),
                    hours=np.random.randint(8, 22),
                    minutes=np.random.randint(0, 59)
                )
                
                duration = np.random.randint(15, 90)  # 15-90 minutes
                problems_solved = np.random.randint(3, 15)
                accuracy = np.random.normal(75, 15)
                accuracy = max(40, min(100, accuracy))
                
                subject = np.random.choice(['Mathematics', 'Physics', 'Chemistry', 'Literature'])
                
                sessions.append({
                    'Date': session_date,
                    'Duration': duration,
                    'Problems': problems_solved,
                    'Accuracy': accuracy,
                    'Subject': subject,
                    'Points': int(problems_solved * (accuracy / 100) * 3)
                })
            
            df = pd.DataFrame(sessions)
            df = df.sort_values('Date')
            
            # Create timeline chart
            fig = go.Figure()
            
            # Color map for subjects
            subject_colors = {
                'Mathematics': self.color_scheme['primary'],
                'Physics': self.color_scheme['info'],
                'Chemistry': self.color_scheme['success'],
                'Literature': self.color_scheme['warning']
            }
            
            for subject in df['Subject'].unique():
                subject_data = df[df['Subject'] == subject]
                
                fig.add_trace(go.Scatter(
                    x=subject_data['Date'],
                    y=subject_data['Duration'],
                    mode='markers',
                    name=subject,
                    marker=dict(
                        size=subject_data['Problems'] * 2,  # Size based on problems solved
                        color=subject_colors.get(subject, self.color_scheme['primary']),
                        opacity=0.7,
                        sizemode='diameter'
                    ),
                    text=subject_data.apply(lambda row: 
                        f"Subject: {row['Subject']}<br>" +
                        f"Duration: {row['Duration']} min<br>" +
                        f"Problems: {row['Problems']}<br>" +
                        f"Accuracy: {row['Accuracy']:.1f}%<br>" +
                        f"Points: {row['Points']}", axis=1
                    ),
                    hovertemplate='%{text}<extra></extra>'
                ))
            
            fig.update_layout(
                title='Study Session Timeline (Last 7 Days)',
                xaxis_title='Date & Time',
                yaxis_title='Session Duration (minutes)',
                height=400,
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Session insights
            total_sessions = len(df)
            avg_duration = df['Duration'].mean()
            avg_accuracy = df['Accuracy'].mean()
            most_studied = df['Subject'].value_counts().index[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", total_sessions)
            
            with col2:
                st.metric("Avg Duration", f"{avg_duration:.0f} min")
            
            with col3:
                st.metric("Avg Accuracy", f"{avg_accuracy:.1f}%")
            
            with col4:
                st.metric("Most Studied", most_studied)
            
        except Exception as e:
            logger.error(f"Error rendering study session timeline: {e}")
            st.error("Unable to load session timeline.")
    
    def render_achievement_progress_chart(self, user_id: str):
        """Render achievement progress visualization"""
        try:
            from utils.achievements import AchievementManager
            achievement_manager = AchievementManager()
            
            st.subheader("🏆 Achievement Progress")
            
            available_achievements = achievement_manager.get_available_achievements(user_id)
            earned_achievements = achievement_manager.get_user_achievements(user_id)
            
            # Prepare progress data
            progress_data = []
            for ach in available_achievements:
                if ach['progress'] > 0:  # Only show achievements with some progress
                    progress_data.append({
                        'Achievement': ach['name'][:25] + '...' if len(ach['name']) > 25 else ach['name'],
                        'Progress': ach['progress'],
                        'Points': ach['points'],
                        'Description': ach['description']
                    })
            
            if not progress_data:
                st.info("Start practicing to make progress toward achievements!")
                return
            
            df = pd.DataFrame(progress_data)
            df = df.sort_values('Progress', ascending=True)
            
            # Create horizontal progress bars
            fig = go.Figure()
            
            colors = []
            for progress in df['Progress']:
                if progress >= 75:
                    colors.append(self.color_scheme['success'])
                elif progress >= 50:
                    colors.append(self.color_scheme['warning'])
                else:
                    colors.append(self.color_scheme['info'])
            
            fig.add_trace(go.Bar(
                x=df['Progress'],
                y=df['Achievement'],
                orientation='h',
                marker_color=colors,
                text=df['Progress'].apply(lambda x: f"{x:.0f}%"),
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>' +
                            'Progress: %{x:.0f}%<br>' +
                            'Points: %{customdata}<extra></extra>',
                customdata=df['Points']
            ))
            
            fig.update_layout(
                title='Achievement Progress (Closest to Completion)',
                xaxis_title='Progress (%)',
                height=max(300, len(df) * 50),
                xaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show closest achievements
            closest = df[df['Progress'] >= 75]
            if not closest.empty:
                st.success("🎯 **Almost There!** You're close to earning these achievements:")
                for _, row in closest.iterrows():
                    st.write(f"• **{row['Achievement']}** - {row['Progress']:.0f}% complete ({row['Points']} points)")
            
        except Exception as e:
            logger.error(f"Error rendering achievement progress chart: {e}")
            st.error("Unable to load achievement progress chart.")
