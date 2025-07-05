"""
Student dashboard for EduTech AI Learning Platform
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class StudentDashboard:
    """Student dashboard with personalized learning features"""
    
    def __init__(self):
        self.user_id = st.session_state.current_user
        self.user_data = st.session_state.all_users.get(self.user_id, {})
    
    def render(self):
        """Render the complete student dashboard"""
        try:
            # Import here to avoid circular imports
            from utils.data_manager import DataManager
            self.data_manager = DataManager()
            
            stats = self.data_manager.get_user_stats(self.user_id)
            
            st.title(f"Welcome back, {self.user_data['name']}! 🎓")
            
            # Progress Overview
            self._render_progress_overview(stats)
            
            # Subject Progress
            self._render_subject_progress()
            
            # Interactive Learning Path
            col1, col2 = st.columns(2)
            
            with col1:
                self._render_learning_plan(stats)
            
            with col2:
                self._render_ai_assistant(stats)
            
            # Recommendations
            self._render_recommendations(stats)
            
            # Demo reset option
            self._render_demo_controls()
            
        except Exception as e:
            logger.error(f"Error rendering student dashboard: {e}")
            st.error("Unable to load dashboard. Please refresh the page.")
    
    def _render_progress_overview(self, stats: Dict[str, Any]):
        """Render progress overview metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Overall Progress</h3>
                <h2>{stats['overall_progress']:.0f}%</h2>
                <p>Keep going!</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔥 Study Streak</h3>
                <h2>{stats['study_streak']} days</h2>
                <p>{"Amazing!" if stats['study_streak'] > 7 else "Great start!"}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>⏱️ Study Time Today</h3>
                <h2>{stats['study_time_today']:.1f} hrs</h2>
                <p>{"On track" if stats['study_time_today'] >= 2 else "Keep going"}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🏆 Achievements</h3>
                <h2>{stats['achievements']}</h2>
                <p>Badges earned</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_subject_progress(self):
        """Render subject progress chart"""
        st.subheader("📈 Subject Progress")
        
        # Get current progress data
        if self.user_data.get("progress"):
            current_progress = self.user_data["progress"].copy()
            
            # Add some adaptive learning based on user stats
            stats = self.data_manager.get_user_stats(self.user_id)
            if stats['sessions_completed'] > 0:
                for subject in current_progress:
                    boost = min(stats['sessions_completed'] * 2, 20)
                    current_progress[subject] = min(100, current_progress[subject] + boost)
            
            progress_data = pd.DataFrame([
                {"Subject": subject, "Progress": progress}
                for subject, progress in current_progress.items()
            ])
        else:
            # Default progress for users without specific progress data
            default_subjects = self.user_data.get("subjects_interest", ["Mathematics", "Physics", "Chemistry", "Literature"])
            stats = self.data_manager.get_user_stats(self.user_id)
            progress_data = pd.DataFrame([
                {"Subject": subject, "Progress": max(0, min(100, random.randint(20, 40) + stats['overall_progress']))}
                for subject in default_subjects[:4]
            ])
        
        if not progress_data.empty:
            fig = px.bar(progress_data, x="Subject", y="Progress", 
                         color="Progress", color_continuous_scale="viridis",
                         title="Your Learning Progress by Subject")
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_learning_plan(self, stats: Dict[str, Any]):
        """Render today's learning plan"""
        st.subheader("🎯 Today's Learning Plan")
        
        # Generate learning tasks based on user's interests and adaptive difficulty
        subjects = self.user_data.get("subjects_interest", ["Mathematics", "Physics", "Literature", "History"])
        
        # Adaptive difficulty based on progress
        difficulty_level = "Beginner" if stats['overall_progress'] < 30 else "Intermediate" if stats['overall_progress'] < 70 else "Advanced"
        
        learning_tasks = []
        for i, subject in enumerate(subjects[:4]):
            tasks = {
                "Mathematics": f"{difficulty_level} Algebra Chapter 5",
                "Physics": f"{difficulty_level} Newton's Laws Practice", 
                "Chemistry": f"{difficulty_level} Chemical Bonding Exercises",
                "Literature": f"{difficulty_level} Essay Writing Practice",
                "History": f"{difficulty_level} World War II Timeline",
                "Biology": f"{difficulty_level} Cell Structure Study",
                "Geography": f"{difficulty_level} Climate Zones Review",
                "Economics": f"{difficulty_level} Supply and Demand Analysis"
            }
            
            task_name = tasks.get(subject, f"{difficulty_level} {subject} Practice Session")
            estimated_time = random.randint(25, 50) * (1.5 if difficulty_level == "Advanced" else 1)
            
            learning_tasks.append({
                "task": task_name,
                "time": f"{estimated_time:.0f} min",
                "type": subject,
                "estimated_hours": estimated_time / 60
            })
        
        for task in learning_tasks:
            with st.expander(f"📚 {task['task']} ({task['time']})"):
                st.write(f"**Subject:** {task['type']}")
                st.write(f"**Difficulty:** {difficulty_level}")
                st.write("**Learning Mode:** Interactive with AI tutor")
                st.write("**Resources:** Video, Practice Problems, Mindmap")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"Start Learning", key=f"start_{task['task']}"):
                        self._handle_start_learning(task)
                        
                with col_b:
                    if st.button(f"Get Help", key=f"help_{task['task']}"):
                        st.info("🤖 AI tutor is ready to help! Ask any questions about this topic.")
    
    def _handle_start_learning(self, task: Dict[str, Any]):
        """Handle starting a learning session"""
        try:
            # Update stats when starting a lesson
            progress_gained = random.randint(3, 8)
            time_spent = task['estimated_hours']
            
            self.data_manager.update_user_stats(
                self.user_id, 
                'lesson_completed', 
                progress_amount=progress_gained, 
                time_spent=time_spent,
                subject=task['type']
            )
            
            st.success(f"🎉 Great job! You gained {progress_gained} progress points and studied for {time_spent:.1f} hours!")
            st.balloons()
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error handling start learning: {e}")
            st.error("Unable to start learning session. Please try again.")
    
    def _render_ai_assistant(self, stats: Dict[str, Any]):
        """Render AI learning assistant section"""
        st.subheader("🤖 AI Learning Assistant")
        
        # Quick Practice Section
        st.subheader("🧮 Quick Practice")
        
        if st.button("Generate Practice Problem", use_container_width=True):
            self._generate_practice_problem(stats)
        
        # Chat Interface
        st.subheader("💬 Chat with AI Tutor")
        st.write("Ask me anything about your studies!")
        
        # Display recent chat messages
        from utils.state_manager import StateManager
        state_manager = StateManager()
        
        recent_messages = state_manager.get_chat_history(limit=3)
        for message in recent_messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 {message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message ai-message">🤖 {message["content"]}</div>', 
                          unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Type your question here...", key="chat_input")
        
        if st.button("Send") and user_input:
            self._handle_chat_message(user_input, stats, state_manager)
    
    def _generate_practice_problem(self, stats: Dict[str, Any]):
        """Generate and handle a practice problem"""
        try:
            # Get practice problems
            user_subjects = self.user_data.get("subjects_interest", ["Mathematics"])
            selected_subject = random.choice(user_subjects)
            
            difficulty_level = "Beginner" if stats['overall_progress'] < 30 else "Intermediate" if stats['overall_progress'] < 70 else "Advanced"
            
            problems = self.data_manager.get_practice_problems(selected_subject, difficulty_level, count=1)
            
            if problems:
                problem = problems[0]
                st.info(f"**{selected_subject} Problem:** {problem['question']}")
                
                user_answer = st.text_input("Your answer:", key=f"answer_{random.randint(1000,9999)}")
                
                if st.button("Submit Answer") and user_answer:
                    self._check_practice_answer(problem, user_answer, selected_subject)
            else:
                st.warning("No practice problems available for this subject.")
                
        except Exception as e:
            logger.error(f"Error generating practice problem: {e}")
            st.error("Unable to generate practice problem. Please try again.")
    
    def _check_practice_answer(self, problem: Dict[str, Any], user_answer: str, subject: str):
        """Check practice problem answer"""
        try:
            is_correct = user_answer.lower().strip() == problem['answer'].lower().strip()
            
            if is_correct:
                progress_gained = problem.get('points', random.randint(2, 4))
                self.data_manager.update_user_stats(
                    self.user_id, 
                    'problem_solved', 
                    progress_amount=progress_gained,
                    subject=subject
                )
                
                st.success(f"✅ Correct! You earned {progress_gained} progress points!")
                st.balloons()
            else:
                st.error(f"❌ Not quite right. The correct answer is: {problem['answer']}")
                st.info("💡 Don't worry! Learning from mistakes is part of the process.")
            
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error checking practice answer: {e}")
            st.error("Unable to check answer. Please try again.")
    
    def _handle_chat_message(self, user_input: str, stats: Dict[str, Any], state_manager):
        """Handle chat message with AI tutor"""
        try:
            # Add user message
            state_manager.add_chat_message("user", user_input)
            
            # Generate adaptive AI response based on user's progress
            if stats['overall_progress'] < 30:
                ai_responses = [
                    "Great question! Let me start with the basics and build up to this concept...",
                    "I can see you're just getting started. Let's break this down into simple steps...",
                    "Perfect timing to learn this! Here's a beginner-friendly explanation..."
                ]
            elif stats['overall_progress'] < 70:
                ai_responses = [
                    "Good question! You're making solid progress. Let me explain this intermediate concept...",
                    "I can see you're developing your skills well. Here's how to tackle this...",
                    "You're ready for this challenge! Let me guide you through it..."
                ]
            else:
                ai_responses = [
                    "Excellent question! At your advanced level, let's explore the deeper concepts...",
                    "Great to see you tackling advanced topics! Here's a comprehensive explanation...",
                    "You're doing amazing work! Let's dive into the advanced aspects..."
                ]
            
            ai_response = random.choice(ai_responses)
            state_manager.add_chat_message("assistant", ai_response)
            
            # Small progress for engaging with AI
            self.data_manager.update_user_stats(self.user_id, 'chat_interaction', progress_amount=0.5, time_spent=0.05)
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            st.error("Unable to process chat message. Please try again.")
    
    def _render_recommendations(self, stats: Dict[str, Any]):
        """Render personalized recommendations"""
        st.subheader("💡 Personalized Recommendations")
        
        col1, col2, col3 = st.columns(3)
        
        # Adaptive recommendations based on user's current level
        if stats['overall_progress'] < 30:
            recommendations = {
                "resources": ["Khan Academy: Basic Concepts", "Interactive Tutorials", "Visual Learning Aids"],
                "focus": ["Foundation building", "Basic problem solving", "Study habits"],
                "milestones": ["Complete first 5 lessons", "Solve 10 practice problems", "Study 30 minutes daily"]
            }
        elif stats['overall_progress'] < 70:
            recommendations = {
                "resources": ["Advanced Coursework", "Practice Tests", "Peer Study Groups"],
                "focus": ["Complex problem solving", "Application skills", "Time management"],
                "milestones": ["Master current topics", "Take practice quiz", "Maintain study streak"]
            }
        else:
            recommendations = {
                "resources": ["Research Papers", "Advanced Simulations", "Expert Lectures"],
                "focus": ["Critical thinking", "Research skills", "Teaching others"],
                "milestones": ["Lead a study group", "Complete advanced project", "Mentor new students"]
            }
        
        with col1:
            st.markdown(f"""
            <div class="role-card">
                <h4>📖 Recommended Resources</h4>
                <ul>
                    {''.join([f'<li>{resource}</li>' for resource in recommendations["resources"]])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="role-card">
                <h4>🎯 Focus Areas</h4>
                <ul>
                    {''.join([f'<li>{focus}</li>' for focus in recommendations["focus"]])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="role-card">
                <h4>🏆 Next Milestones</h4>
                <ul>
                    {''.join([f'<li>{milestone}</li>' for milestone in recommendations["milestones"]])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_demo_controls(self):
        """Render demo control options"""
        with st.expander("🔄 Reset Progress (Demo Purpose)"):
            if st.button("Reset All Stats", type="secondary"):
                from utils.state_manager import StateManager
                state_manager = StateManager()
                state_manager.reset_user_progress(self.user_id)
                st.success("Stats reset! Refresh to see changes.")
                st.rerun()
