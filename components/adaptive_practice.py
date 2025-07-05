"""
Adaptive practice system for EduTech AI Learning Platform
Copy this code into components/adaptive_practice.py
"""

import streamlit as st
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from config.app_settings import PROBLEM_BANKS, DIFFICULTY_LEVELS, SUBJECTS

logger = logging.getLogger(__name__)

class AdaptivePractice:
    """Intelligent practice system that adapts to user performance"""
    
    def __init__(self):
        self.problem_banks = PROBLEM_BANKS
        self.difficulty_levels = DIFFICULTY_LEVELS
        self.subjects = SUBJECTS
    
    def render_practice_interface(self, user_id: str):
        """Render the complete adaptive practice interface"""
        try:
            # Import managers
            from utils.enhanced_stats import EnhancedStatsManager
            from utils.achievements import AchievementManager
            
            self.stats_manager = EnhancedStatsManager()
            self.achievement_manager = AchievementManager()
            
            # Get user data
            user_data = st.session_state.all_users.get(user_id, {})
            stats = self.stats_manager.get_user_stats(user_id)
            
            st.title("🧮 Adaptive Practice Center")
            st.write("AI-powered practice that adapts to your skill level!")
            
            # Practice overview
            self._render_practice_overview(stats)
            
            # Practice session selector
            col1, col2 = st.columns([2, 1])
            
            with col1:
                self._render_practice_session(user_id, user_data, stats)
            
            with col2:
                self._render_practice_analytics(user_id, stats)
            
            # Check for pending achievements
            self.achievement_manager.check_pending_achievements(user_id)
            
        except Exception as e:
            logger.error(f"Error rendering practice interface: {e}")
            st.error("Unable to load practice interface. Please refresh the page.")
    
    def _render_practice_overview(self, stats: Dict[str, Any]):
        """Render practice statistics overview"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            problems_today = stats.get('problems_solved', 0) % 20  # Reset daily
            st.metric("Problems Today", problems_today, delta=f"Goal: 10")
        
        with col2:
            accuracy = stats.get('accuracy_rate', 0)
            delta_color = "normal" if accuracy >= 70 else "inverse"
            st.metric("Accuracy Rate", f"{accuracy:.1f}%", delta=f"Target: 80%")
        
        with col3:
            current_level = self._get_adaptive_difficulty(stats)
            st.metric("Current Level", current_level, delta=None)
        
        with col4:
            streak = stats.get('study_streak', 0)
            st.metric("Practice Streak", f"{streak} days", delta="🔥" if streak > 0 else None)
    
    def _render_practice_session(self, user_id: str, user_data: Dict[str, Any], stats: Dict[str, Any]):
        """Render practice session interface"""
        st.subheader("🎯 Smart Practice Session")
        
        # Subject selection with recommendations
        user_subjects = user_data.get("subjects_interest", self.subjects[:4])
        
        # Get recommended subject based on weak areas
        recommended_subject = self._get_recommended_subject(user_id, user_subjects, stats)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if recommended_subject:
                st.info(f"💡 Recommended: **{recommended_subject}** (needs attention)")
                default_index = user_subjects.index(recommended_subject) if recommended_subject in user_subjects else 0
            else:
                default_index = 0
            
            selected_subject = st.selectbox(
                "Choose subject:", 
                user_subjects,
                index=default_index
            )
        
        with col2:
            # Practice modes
            practice_mode = st.selectbox("Practice Mode:", [
                "🤖 Adaptive (Recommended)",
                "🎯 Quick Practice", 
                "📝 Quiz Mode (5 Questions)",
                "⚡ Speed Challenge",
                "🧠 Memory Drill"
            ])
        
        # Adaptive difficulty display
        adaptive_difficulty = self._get_adaptive_difficulty(stats)
        subject_stats = stats.get('subject_stats', {}).get(selected_subject, {})
        
        if subject_stats:
            subject_accuracy = subject_stats.get('accuracy', 0)
            subject_level = self._calculate_subject_difficulty(subject_stats)
            
            st.markdown(f"""
            <div class="info-card">
                <h4>📊 {selected_subject} Performance</h4>
                <p><strong>Subject Level:</strong> {subject_level}</p>
                <p><strong>Subject Accuracy:</strong> {subject_accuracy:.1f}%</p>
                <p><strong>Problems Solved:</strong> {subject_stats.get('total_problems', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Start practice session
        if st.button("🚀 Start Practice Session", use_container_width=True, type="primary"):
            self._start_practice_session(user_id, selected_subject, practice_mode, stats)
    
    def _start_practice_session(self, user_id: str, subject: str, mode: str, stats: Dict[str, Any]):
        """Start an adaptive practice session"""
        try:
            if "🤖 Adaptive" in mode:
                self._adaptive_practice_session(user_id, subject, stats)
            elif "🎯 Quick Practice" in mode:
                self._quick_practice_session(user_id, subject, stats)
            elif "📝 Quiz Mode" in mode:
                self._quiz_mode_session(user_id, subject, stats)
            elif "⚡ Speed Challenge" in mode:
                self._speed_challenge_session(user_id, subject, stats)
            elif "🧠 Memory Drill" in mode:
                self._memory_drill_session(user_id, subject, stats)
            
        except Exception as e:
            logger.error(f"Error starting practice session: {e}")
            st.error("Unable to start practice session. Please try again.")
    
    def _adaptive_practice_session(self, user_id: str, subject: str, stats: Dict[str, Any]):
        """Run an adaptive practice session that adjusts difficulty"""
        st.subheader(f"🤖 Adaptive Practice: {subject}")
        
        # Determine starting difficulty
        difficulty = self._get_adaptive_difficulty_for_subject(subject, stats)
        
        # Initialize session state
        if 'adaptive_session' not in st.session_state:
            st.session_state.adaptive_session = {
                'problems_attempted': 0,
                'problems_correct': 0,
                'current_difficulty': difficulty,
                'difficulty_history': [],
                'session_start': datetime.now(),
                'subject': subject,
                'adaptive_adjustments': 0
            }
        
        session = st.session_state.adaptive_session
        
        # Generate problem based on current difficulty
        problem = self._get_adaptive_problem(subject, session['current_difficulty'])
        
        if not problem:
            st.warning(f"No problems available for {subject} at {session['current_difficulty']} level.")
            return
        
        # Display problem
        st.markdown(f"""
        <div class="practice-problem">
            <h4>Problem {session['problems_attempted'] + 1}</h4>
            <p><strong>Difficulty:</strong> {session['current_difficulty']}</p>
            <p><strong>Type:</strong> {problem['type'].title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"**Question:** {problem['question']}")
        
        # Answer input
        user_answer = st.text_input("Your answer:", key=f"adaptive_answer_{session['problems_attempted']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Submit Answer", disabled=not user_answer):
                self._process_adaptive_answer(user_id, problem, user_answer, session)
        
        with col2:
            if st.button("Get Hint"):
                hint = self._generate_hint(problem)
                st.info(f"💡 Hint: {hint}")
        
        with col3:
            if st.button("Skip Problem"):
                self._skip_adaptive_problem(user_id, session)
        
        # Session progress
        if session['problems_attempted'] > 0:
            accuracy = (session['problems_correct'] / session['problems_attempted']) * 100
            st.progress(min(session['problems_attempted'] / 10, 1.0))
            st.write(f"Progress: {session['problems_attempted']}/10 | Accuracy: {accuracy:.1f}%")
            
            # Show difficulty adaptation
            if session['adaptive_adjustments'] > 0:
                st.success(f"🎯 Difficulty adapted {session['adaptive_adjustments']} times to match your skill level!")
        
        # End session after 10 problems
        if session['problems_attempted'] >= 10:
            self._complete_adaptive_session(user_id, session)
    
    def _process_adaptive_answer(self, user_id: str, problem: Dict[str, Any], user_answer: str, session: Dict[str, Any]):
        """Process answer and adapt difficulty"""
        try:
            is_correct = self._check_answer(problem, user_answer)
            
            session['problems_attempted'] += 1
            
            if is_correct:
                session['problems_correct'] += 1
                points = problem.get('points', 2)
                
                # Update stats
                self.stats_manager.update_stats(
                    user_id, 'problem_solved',
                    correct=True,
                    subject=session['subject'],
                    difficulty=session['current_difficulty'],
                    points=points
                )
                
                st.success(f"✅ Correct! +{points} points")
                
                # Adapt difficulty up if consistently correct
                if self._should_increase_difficulty(session):
                    old_difficulty = session['current_difficulty']
                    session['current_difficulty'] = self._get_next_difficulty(old_difficulty)
                    session['adaptive_adjustments'] += 1
                    
                    if session['current_difficulty'] != old_difficulty:
                        st.info(f"🔼 Difficulty increased to {session['current_difficulty']}! You're doing great!")
            
            else:
                st.error(f"❌ Incorrect. The answer is: {problem['answer']}")
                
                # Provide explanation
                explanation = self._generate_explanation(problem)
                if explanation:
                    st.info(f"💡 Explanation: {explanation}")
                
                # Adapt difficulty down if struggling
                if self._should_decrease_difficulty(session):
                    old_difficulty = session['current_difficulty']
                    session['current_difficulty'] = self._get_previous_difficulty(old_difficulty)
                    session['adaptive_adjustments'] += 1
                    
                    if session['current_difficulty'] != old_difficulty:
                        st.info(f"🔽 Difficulty adjusted to {session['current_difficulty']} to help you learn better.")
            
            # Record difficulty change
            session['difficulty_history'].append({
                'problem_number': session['problems_attempted'],
                'difficulty': session['current_difficulty'],
                'correct': is_correct
            })
            
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error processing adaptive answer: {e}")
            st.error("Error processing answer. Please try again.")
    
    def _quick_practice_session(self, user_id: str, subject: str, stats: Dict[str, Any]):
        """Quick practice session with single problems"""
        st.subheader(f"🎯 Quick Practice: {subject}")
        
        difficulty = self._get_adaptive_difficulty_for_subject(subject, stats)
        problem = self._get_adaptive_problem(subject, difficulty)
        
        if not problem:
            st.warning(f"No problems available for {subject}.")
            return
        
        st.info(f"**{problem['type'].title()} Problem:** {problem['question']}")
        
        user_answer = st.text_input("Your answer:", key=f"quick_answer_{random.randint(1000,9999)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Submit", disabled=not user_answer):
                self._process_quick_answer(user_id, problem, user_answer, subject, difficulty)
        
        with col2:
            if st.button("New Problem"):
                st.rerun()
    
    def _quiz_mode_session(self, user_id: str, subject: str, stats: Dict[str, Any]):
        """Quiz mode with 5 questions"""
        st.subheader(f"📝 Quiz Mode: {subject}")
        
        # Initialize quiz session
        if 'quiz_session' not in st.session_state:
            difficulty = self._get_adaptive_difficulty_for_subject(subject, stats)
            problems = self._get_quiz_problems(subject, difficulty, count=5)
            
            st.session_state.quiz_session = {
                'problems': problems,
                'answers': [''] * len(problems),
                'submitted': False,
                'subject': subject,
                'difficulty': difficulty,
                'start_time': datetime.now()
            }
        
        quiz = st.session_state.quiz_session
        
        if not quiz['submitted']:
            with st.form("quiz_form"):
                st.write(f"**Difficulty Level:** {quiz['difficulty']}")
                st.write("Answer all questions and submit when ready:")
                st.markdown("---")
                
                for i, problem in enumerate(quiz['problems']):
                    st.write(f"**Question {i+1}:** {problem['question']}")
                    st.write(f"*Type: {problem['type'].title()}*")
                    quiz['answers'][i] = st.text_input(f"Answer {i+1}:", key=f"quiz_q_{i}")
                    st.markdown("---")
                
                submitted = st.form_submit_button("Submit Quiz", use_container_width=True)
                
                if submitted:
                    self._process_quiz_submission(user_id, quiz)
        else:
            self._display_quiz_results(quiz)
    
    def _speed_challenge_session(self, user_id: str, subject: str, stats: Dict[str, Any]):
        """Speed challenge mode"""
        st.subheader(f"⚡ Speed Challenge: {subject}")
        
        # Initialize speed session
        if 'speed_session' not in st.session_state:
            st.session_state.speed_session = {
                'time_limit': 60,  # 60 seconds
                'problems_solved': 0,
                'problems_correct': 0,
                'started': False,
                'start_time': None,
                'subject': subject
            }
        
        speed = st.session_state.speed_session
        
        if not speed['started']:
            st.write("🎯 **Challenge:** Solve as many problems as possible in 60 seconds!")
            st.write("📊 **Scoring:** +2 points per correct answer, -1 point per wrong answer")
            
            if st.button("🚀 Start Speed Challenge", use_container_width=True):
                speed['started'] = True
                speed['start_time'] = datetime.now()
                st.rerun()
        else:
            self._run_speed_challenge(user_id, speed)
    
    def _memory_drill_session(self, user_id: str, subject: str, stats: Dict[str, Any]):
        """Memory drill session"""
        st.subheader(f"🧠 Memory Drill: {subject}")
        
        st.info("💡 **Memory Drill:** Review problems you've gotten wrong before to reinforce learning!")
        
        # Get problems user has struggled with
        weak_problems = self._get_review_problems(user_id, subject)
        
        if not weak_problems:
            st.success("🎉 Great! You don't have any problems that need review in this subject.")
            st.write("Try practicing new problems to continue learning!")
            return
        
        problem = random.choice(weak_problems)
        
        st.warning(f"**Review Problem:** This is similar to one you found challenging before.")
        st.info(f"**Question:** {problem['question']}")
        
        user_answer = st.text_input("Your answer:", key=f"memory_answer_{random.randint(1000,9999)}")
        
        if st.button("Submit", disabled=not user_answer):
            self._process_memory_answer(user_id, problem, user_answer, subject)
    
    def _render_practice_analytics(self, user_id: str, stats: Dict[str, Any]):
        """Render practice analytics and recommendations"""
        st.subheader("📊 Practice Analytics")
        
        # Recent performance
        recent_accuracy = stats.get('accuracy_rate', 0)
        improvement_rate = stats.get('improvement_rate', 0)
        
        # Performance indicators
        if recent_accuracy >= 80:
            st.success(f"🎯 Excellent accuracy: {recent_accuracy:.1f}%")
        elif recent_accuracy >= 60:
            st.info(f"📈 Good progress: {recent_accuracy:.1f}%")
        else:
            st.warning(f"📚 Keep practicing: {recent_accuracy:.1f}%")
        
        # Improvement trend
        if improvement_rate > 0:
            st.success(f"📈 Improving! +{improvement_rate:.1f}% accuracy trend")
        elif improvement_rate == 0:
            st.info("📊 Steady performance")
        else:
            st.info("💪 Focus on fundamentals to improve")
        
        # Subject recommendations
        st.subheader("💡 Recommendations")
        
        subject_stats = stats.get('subject_stats', {})
        weak_subjects = stats.get('weak_areas', [])
        
        if weak_subjects:
            st.warning("🎯 **Focus Areas:**")
            for subject in weak_subjects[:3]:  # Top 3 weak areas
                subject_data = subject_stats.get(subject, {})
                accuracy = subject_data.get('accuracy', 0)
                st.write(f"• **{subject}**: {accuracy:.1f}% accuracy - Practice more!")
        
        # Study schedule recommendation
        st.subheader("📅 Study Schedule")
        
        problems_today = stats.get('problems_solved', 0) % 20
        goal_progress = (problems_today / 10) * 100
        
        st.progress(goal_progress / 100)
        st.write(f"Daily Goal: {problems_today}/10 problems ({goal_progress:.0f}%)")
        
        if goal_progress >= 100:
            st.success("🎉 Daily goal achieved! Consider setting a higher target.")
        else:
            remaining = 10 - problems_today
            st.info(f"💪 {remaining} more problems to reach your daily goal!")
    
    # Helper methods
    def _get_adaptive_difficulty(self, stats: Dict[str, Any]) -> str:
        """Determine adaptive difficulty based on user performance"""
        progress = stats.get('overall_progress', 0)
        accuracy = stats.get('accuracy_rate', 0)
        
        if progress < 20 or accuracy < 50:
            return 'Beginner'
        elif progress < 60 or accuracy < 75:
            return 'Intermediate'
        else:
            return 'Advanced'
    
    def _get_adaptive_difficulty_for_subject(self, subject: str, stats: Dict[str, Any]) -> str:
        """Get adaptive difficulty for specific subject"""
        subject_stats = stats.get('subject_stats', {}).get(subject, {})
        
        if not subject_stats:
            return self._get_adaptive_difficulty(stats)
        
        accuracy = subject_stats.get('accuracy', 0)
        problems_count = subject_stats.get('total_problems', 0)
        
        if problems_count < 5:
            return 'Beginner'
        elif accuracy < 60:
            return 'Beginner'
        elif accuracy < 80:
            return 'Intermediate'
        else:
            return 'Advanced'
    
    def _calculate_subject_difficulty(self, subject_stats: Dict[str, Any]) -> str:
        """Calculate difficulty level for a subject"""
        accuracy = subject_stats.get('accuracy', 0)
        problems = subject_stats.get('total_problems', 0)
        
        if problems < 5:
            return 'Getting Started'
        elif accuracy >= 85:
            return 'Advanced'
        elif accuracy >= 70:
            return 'Intermediate'
        else:
            return 'Beginner'
    
    def _get_recommended_subject(self, user_id: str, subjects: List[str], stats: Dict[str, Any]) -> Optional[str]:
        """Get recommended subject based on weak areas"""
        weak_areas = stats.get('weak_areas', [])
        
        # Return first weak area that's in user's subjects
        for subject in weak_areas:
            if subject in subjects:
                return subject
        
        return None
    
    def _get_adaptive_problem(self, subject: str, difficulty: str) -> Optional[Dict[str, Any]]:
        """Get a problem for adaptive practice"""
        if subject in self.problem_banks and difficulty in self.problem_banks[subject]:
            problems = self.problem_banks[subject][difficulty]
            return random.choice(problems) if problems else None
        return None
    
    def _get_quiz_problems(self, subject: str, difficulty: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get problems for quiz mode"""
        if subject in self.problem_banks and difficulty in self.problem_banks[subject]:
            problems = self.problem_banks[subject][difficulty]
            return random.sample(problems, min(count, len(problems)))
        return []
    
    def _get_review_problems(self, user_id: str, subject: str) -> List[Dict[str, Any]]:
        """Get problems for review based on past mistakes"""
        # This would typically come from a database of user's past incorrect answers
        # For now, return beginner problems as review material
        return self._get_quiz_problems(subject, 'Beginner', count=10)
    
    def _check_answer(self, problem: Dict[str, Any], user_answer: str) -> bool:
        """Check if user answer is correct"""
        correct_answer = problem['answer'].lower().strip()
        user_answer = user_answer.lower().strip()
        
        # Handle multiple possible answers (e.g., "x = 2, 3" vs "2, 3")
        if ',' in correct_answer:
            correct_parts = [part.strip() for part in correct_answer.split(',')]
            user_parts = [part.strip() for part in user_answer.split(',')]
            return set(correct_parts) == set(user_parts)
        
        return correct_answer == user_answer
    
    def _generate_hint(self, problem: Dict[str, Any]) -> str:
        """Generate a hint for the problem"""
        hints = {
            'arithmetic': "Break down the calculation step by step.",
            'algebra': "Isolate the variable by performing the same operation on both sides.",
            'geometry': "Remember the formulas for area, volume, and perimeter.",
            'percentage': "Convert the percentage to a decimal and multiply.",
            'calculus': "Apply the derivative or integral rules you've learned.",
            'physics': "Identify the known variables and the formula that relates them.",
            'chemistry': "Check if the equation is balanced and use molar masses.",
            'concepts': "Think about the fundamental principles and definitions."
        }
        
        problem_type = problem.get('type', 'concepts')
        return hints.get(problem_type, "Think step by step and check your work.")
    
    def _generate_explanation(self, problem: Dict[str, Any]) -> str:
        """Generate an explanation for the correct answer"""
        explanations = {
            'arithmetic': f"The correct calculation gives us {problem['answer']}.",
            'algebra': f"Solving step by step: {problem['answer']}",
            'geometry': f"Using the appropriate formula: {problem['answer']}",
            'percentage': f"Converting and calculating: {problem['answer']}",
            'calculus': f"Applying calculus rules: {problem['answer']}",
            'physics': f"Using physics principles: {problem['answer']}",
            'chemistry': f"Following chemical laws: {problem['answer']}",
            'concepts': f"The concept teaches us: {problem['answer']}"
        }
        
        problem_type = problem.get('type', 'concepts')
        return explanations.get(problem_type, f"The answer is {problem['answer']}.")
    
    def _should_increase_difficulty(self, session: Dict[str, Any]) -> bool:
        """Determine if difficulty should be increased"""
        if session['problems_attempted'] < 3:
            return False
        
        recent_correct = sum(1 for entry in session['difficulty_history'][-3:] if entry['correct'])
        return recent_correct >= 3  # 3 correct in a row
    
    def _should_decrease_difficulty(self, session: Dict[str, Any]) -> bool:
        """Determine if difficulty should be decreased"""
        if session['problems_attempted'] < 3:
            return False
        
        recent_incorrect = sum(1 for entry in session['difficulty_history'][-3:] if not entry['correct'])
        return recent_incorrect >= 2  # 2 incorrect in recent 3
    
    def _get_next_difficulty(self, current: str) -> str:
        """Get next higher difficulty level"""
        levels = ['Beginner', 'Intermediate', 'Advanced']
        try:
            current_index = levels.index(current)
            return levels[min(current_index + 1, len(levels) - 1)]
        except ValueError:
            return 'Intermediate'
    
    def _get_previous_difficulty(self, current: str) -> str:
        """Get previous lower difficulty level"""
        levels = ['Beginner', 'Intermediate', 'Advanced']
        try:
            current_index = levels.index(current)
            return levels[max(current_index - 1, 0)]
        except ValueError:
            return 'Beginner'
    
    def _process_quick_answer(self, user_id: str, problem: Dict[str, Any], user_answer: str, subject: str, difficulty: str):
        """Process quick practice answer"""
        try:
            is_correct = self._check_answer(problem, user_answer)
            
            if is_correct:
                points = problem.get('points', 2)
                self.stats_manager.update_stats(
                    user_id, 'problem_solved',
                    correct=True, subject=subject, difficulty=difficulty, points=points
                )
                st.success(f"✅ Correct! +{points} points")
                st.balloons()
            else:
                st.error(f"❌ Incorrect. The answer is: {problem['answer']}")
                explanation = self._generate_explanation(problem)
                st.info(f"💡 {explanation}")
            
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error processing quick answer: {e}")
            st.error("Error processing answer.")
    
    def _process_quiz_submission(self, user_id: str, quiz: Dict[str, Any]):
        """Process quiz submission"""
        try:
            correct_count = 0
            results = []
            
            for i, (problem, user_answer) in enumerate(zip(quiz['problems'], quiz['answers'])):
                is_correct = self._check_answer(problem, user_answer)
                if is_correct:
                    correct_count += 1
                
                results.append({
                    'question': problem['question'],
                    'user_answer': user_answer,
                    'correct_answer': problem['answer'],
                    'is_correct': is_correct,
                    'points': problem.get('points', 2) if is_correct else 0
                })
            
            quiz['results'] = results
            quiz['score'] = correct_count
            quiz['submitted'] = True
            quiz['completion_time'] = datetime.now()
            
            # Update stats
            total_points = sum(r['points'] for r in results)
            self.stats_manager.update_stats(
                user_id, 'session_completed',
                subject=quiz['subject'],
                problems_solved=len(quiz['problems']),
                problems_correct=correct_count,
                points_earned=total_points,
                duration=(quiz['completion_time'] - quiz['start_time']).total_seconds() / 60
            )
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error processing quiz: {e}")
            st.error("Error processing quiz.")
    
    def _display_quiz_results(self, quiz: Dict[str, Any]):
        """Display quiz results"""
        try:
            score = quiz['score']
            total = len(quiz['problems'])
            percentage = (score / total) * 100
            
            st.subheader("📊 Quiz Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score", f"{score}/{total}")
            
            with col2:
                st.metric("Percentage", f"{percentage:.1f}%")
            
            with col3:
                duration = (quiz['completion_time'] - quiz['start_time']).total_seconds() / 60
                st.metric("Time", f"{duration:.1f} min")
            
            # Performance feedback
            if percentage >= 80:
                st.success("🎉 Excellent work! You've mastered this level!")
                st.balloons()
            elif percentage >= 60:
                st.info("👍 Good job! Keep practicing to improve further.")
            else:
                st.warning("📚 Keep studying! Review the topics you missed.")
            
            # Detailed results
            with st.expander("📝 Detailed Results"):
                for i, result in enumerate(quiz['results']):
                    icon = "✅" if result['is_correct'] else "❌"
                    st.write(f"{icon} **Q{i+1}:** {result['question']}")
                    st.write(f"Your answer: {result['user_answer']}")
                    if not result['is_correct']:
                        st.write(f"Correct answer: {result['correct_answer']}")
                    st.markdown("---")
            
            # Reset quiz
            if st.button("🔄 Take Another Quiz"):
                del st.session_state.quiz_session
                st.rerun()
                
        except Exception as e:
            logger.error(f"Error displaying quiz results: {e}")
            st.error("Error displaying results.")
    
    def _run_speed_challenge(self, user_id: str, speed: Dict[str, Any]):
        """Run the speed challenge session"""
        try:
            # Calculate remaining time
            elapsed = (datetime.now() - speed['start_time']).total_seconds()
            remaining = max(0, speed['time_limit'] - elapsed)
            
            if remaining <= 0:
                self._complete_speed_challenge(user_id, speed)
                return
            
            # Display timer
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown(f"""
                <div style="text-align: center; font-size: 2em; color: red; font-weight: bold;">
                    ⏰ {remaining:.0f} seconds remaining
                </div>
                """, unsafe_allow_html=True)
            
            # Current stats
            if speed['problems_solved'] > 0:
                accuracy = (speed['problems_correct'] / speed['problems_solved']) * 100
                st.write(f"**Score:** {speed['problems_correct']} correct out of {speed['problems_solved']} | **Accuracy:** {accuracy:.1f}%")
            
            # Generate problem
            problem = self._get_adaptive_problem(speed['subject'], 'Beginner')  # Use beginner for speed
            
            if problem:
                st.info(f"**Quick:** {problem['question']}")
                
                user_answer = st.text_input("Answer:", key=f"speed_{speed['problems_solved']}")
                
                if st.button("Submit", disabled=not user_answer) or user_answer:
                    if user_answer:  # Auto-submit on enter
                        is_correct = self._check_answer(problem, user_answer)
                        speed['problems_solved'] += 1
                        
                        if is_correct:
                            speed['problems_correct'] += 1
                            st.success("✅ Correct! +2 points")
                        else:
                            st.error(f"❌ Wrong! Answer: {problem['answer']}")
                        
                        time.sleep(0.5)
                        st.rerun()
            
            # Auto-refresh every second
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error running speed challenge: {e}")
            st.error("Error in speed challenge.")
    
    def _complete_speed_challenge(self, user_id: str, speed: Dict[str, Any]):
        """Complete the speed challenge and show results"""
        try:
            st.subheader("⚡ Speed Challenge Complete!")
            
            final_score = speed['problems_correct'] * 2 - (speed['problems_solved'] - speed['problems_correct'])
            accuracy = (speed['problems_correct'] / speed['problems_solved']) * 100 if speed['problems_solved'] > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Problems Solved", speed['problems_solved'])
            
            with col2:
                st.metric("Correct Answers", speed['problems_correct'])
            
            with col3:
                st.metric("Accuracy", f"{accuracy:.1f}%")
            
            with col4:
                st.metric("Final Score", final_score)
            
            # Performance rating
            if final_score >= 15:
                st.success("🏆 Outstanding! Lightning fast problem solver!")
                rating = "Outstanding"
            elif final_score >= 10:
                st.success("🎯 Excellent! Great speed and accuracy!")
                rating = "Excellent"
            elif final_score >= 5:
                st.info("👍 Good! Keep practicing to improve speed.")
                rating = "Good"
            else:
                st.warning("📚 Practice more to improve speed and accuracy.")
                rating = "Needs Practice"
            
            # Update stats
            self.stats_manager.update_stats(
                user_id, 'session_completed',
                subject=speed['subject'],
                problems_solved=speed['problems_solved'],
                problems_correct=speed['problems_correct'],
                points_earned=max(final_score, 0),
                duration=1.0,  # 1 minute session
                session_type='speed_challenge',
                performance_rating=rating
            )
            
            # Reset challenge
            if st.button("🔄 Try Again"):
                del st.session_state.speed_session
                st.rerun()
                
        except Exception as e:
            logger.error(f"Error completing speed challenge: {e}")
            st.error("Error completing challenge.")
    
    def _process_memory_answer(self, user_id: str, problem: Dict[str, Any], user_answer: str, subject: str):
        """Process memory drill answer"""
        try:
            is_correct = self._check_answer(problem, user_answer)
            
            if is_correct:
                points = problem.get('points', 2) * 1.5  # Bonus for review
                self.stats_manager.update_stats(
                    user_id, 'problem_solved',
                    correct=True, subject=subject, difficulty='Review', points=points
                )
                st.success(f"🎉 Excellent! You've mastered this concept! +{points:.0f} points (review bonus)")
                st.balloons()
                
                # Award memory master achievement if applicable
                if 'memory_master' not in st.session_state.user_stats.get(user_id, {}).get('badges', []):
                    self.achievement_manager.award_achievement(user_id, 'memory_master')
                
            else:
                st.error(f"❌ Still challenging. The answer is: {problem['answer']}")
                explanation = self._generate_explanation(problem)
                st.info(f"💡 Study tip: {explanation}")
                st.info("💪 Don't worry! Reviewing mistakes is how we learn best.")
            
            if st.button("Continue Memory Drill"):
                st.rerun()
                
        except Exception as e:
            logger.error(f"Error processing memory answer: {e}")
            st.error("Error processing answer.")
    
    def _skip_adaptive_problem(self, user_id: str, session: Dict[str, Any]):
        """Skip current problem in adaptive session"""
        try:
            session['problems_attempted'] += 1
            
            # Record as incorrect for difficulty adaptation
            session['difficulty_history'].append({
                'problem_number': session['problems_attempted'],
                'difficulty': session['current_difficulty'],
                'correct': False
            })
            
            # Adapt difficulty down for skipped problems
            if self._should_decrease_difficulty(session):
                old_difficulty = session['current_difficulty']
                session['current_difficulty'] = self._get_previous_difficulty(old_difficulty)
                session['adaptive_adjustments'] += 1
                
                if session['current_difficulty'] != old_difficulty:
                    st.info(f"🔽 Difficulty adjusted to {session['current_difficulty']} - let's try easier problems.")
            
            st.info("⏭️ Problem skipped. Let's try the next one!")
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error skipping problem: {e}")
            st.error("Error skipping problem.")
    
    def _complete_adaptive_session(self, user_id: str, session: Dict[str, Any]):
        """Complete adaptive session and show results"""
        try:
            st.subheader("🎉 Adaptive Session Complete!")
            
            accuracy = (session['problems_correct'] / session['problems_attempted']) * 100
            duration = (datetime.now() - session['start_time']).total_seconds() / 60
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Problems Solved", session['problems_attempted'])
            
            with col2:
                st.metric("Accuracy", f"{accuracy:.1f}%")
            
            with col3:
                st.metric("Final Difficulty", session['current_difficulty'])
            
            with col4:
                st.metric("Adaptations", session['adaptive_adjustments'])
            
            # Session analysis
            st.subheader("📊 Session Analysis")
            
            if session['adaptive_adjustments'] > 0:
                st.info(f"🤖 **AI Adaptation:** The system made {session['adaptive_adjustments']} difficulty adjustments to match your skill level perfectly!")
            
            if accuracy >= 80:
                st.success("🎯 **Outstanding Performance!** You're ready for more challenging problems.")
                performance = "Outstanding"
            elif accuracy >= 60:
                st.success("👍 **Good Work!** You're making solid progress.")
                performance = "Good"
            else:
                st.info("📚 **Keep Learning!** Every mistake is a step toward mastery.")
                performance = "Learning"
            
            # Difficulty progression chart
            if len(session['difficulty_history']) > 1:
                st.subheader("📈 Difficulty Progression")
                
                difficulty_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
                progression_data = []
                
                for entry in session['difficulty_history']:
                    progression_data.append({
                        'Problem': entry['problem_number'],
                        'Difficulty Level': difficulty_map[entry['difficulty']],
                        'Result': 'Correct' if entry['correct'] else 'Incorrect'
                    })
                
                # Simple text representation
                st.write("**Difficulty Journey:**")
                for i, entry in enumerate(session['difficulty_history']):
                    result_icon = "✅" if entry['correct'] else "❌"
                    st.write(f"Problem {entry['problem_number']}: {entry['difficulty']} {result_icon}")
            
            # Update comprehensive stats
            total_points = session['problems_correct'] * 3  # Base points for adaptive session
            if session['adaptive_adjustments'] > 0:
                total_points += session['adaptive_adjustments'] * 2  # Bonus for adaptation
            
            self.stats_manager.update_stats(
                user_id, 'session_completed',
                subject=session['subject'],
                problems_solved=session['problems_attempted'],
                problems_correct=session['problems_correct'],
                points_earned=total_points,
                duration=duration,
                session_type='adaptive',
                final_difficulty=session['current_difficulty'],
                adaptations_made=session['adaptive_adjustments'],
                performance_rating=performance
            )
            
            # Recommendations for next session
            st.subheader("💡 Next Steps")
            
            if accuracy >= 85 and session['current_difficulty'] != 'Advanced':
                st.info("🎯 **Recommendation:** Try the next difficulty level in your next session!")
            elif accuracy < 60:
                st.info("📚 **Recommendation:** Review the fundamentals before your next practice session.")
            else:
                st.info("💪 **Recommendation:** Keep practicing at this level to build confidence!")
            
            # Reset session
            if st.button("🔄 Start New Adaptive Session"):
                del st.session_state.adaptive_session
                st.rerun()
                
        except Exception as e:
            logger.error(f"Error completing adaptive session: {e}")
            st.error("Error completing session.")
