import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Any, Optional
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="EduTech AI Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Literature", "History", "Biology", "Geography", "Economics"]
LEARNING_STYLES = ["Visual", "Auditory", "Kinesthetic", "Reading/Writing"]

# Initialize session state
def initialize_session_state():
    """Initialize all required session state variables"""
    required_states = {
        'user_data': {},
        'current_user': None,
        'chat_history': [],
        'learning_progress': {},
        'assessment_results': {},
        'all_users': {},
        'user_stats': {},
        'notifications': [],
        'theme': 'light',
        'last_activity': datetime.now(),
        'show_demo_options': False
    }
    
    for key, default_value in required_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Demo users data
DEMO_USERS = {
    "demo_student": {
        "name": "Demo Student",
        "role": "Student",
        "email": "student@demo.com",
        "age": 16,
        "grade": "10th Grade",
        "learning_style": ["Visual"],
        "subjects_interest": ["Mathematics", "Physics", "Chemistry"],
        "progress": {
            "Mathematics": 85,
            "Physics": 78,
            "Chemistry": 65,
            "Literature": 45,
            "History": 40
        }
    },
    "demo_tutor": {
        "name": "Demo Tutor",
        "role": "Tutor",
        "email": "tutor@demo.com",
        "specialization": ["Mathematics", "Physics", "Chemistry"],
        "experience": "5+ years",
        "students": ["Demo Student"]
    },
    "demo_parent": {
        "name": "Demo Parent",
        "role": "Parent",
        "email": "parent@demo.com",
        "num_children": 1,
        "children": ["Demo Student"]
    },
    "demo_teacher": {
        "name": "Demo Teacher",
        "role": "Teacher",
        "email": "teacher@demo.com",
        "subjects": ["Mathematics", "Physics"],
        "grade_levels": ["High School"],
        "class_size": 28
    }
}

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .chat-message {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .user-message {
        background: #e3f2fd;
        margin-left: 2rem;
    }
    .ai-message {
        background: #f3e5f5;
        margin-right: 2rem;
    }
    .achievement-badge {
        background: linear-gradient(45deg, #ffd700, #ffed4e);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.25rem;
        font-weight: bold;
    }
    
    @media (max-width: 768px) {
        .metric-card {
            margin: 0.5rem 0;
            padding: 0.8rem;
        }
        
        .main-header {
            padding: 0.5rem;
            font-size: 0.9em;
        }
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
def safe_get_list_item(items: List, index: int = 0, default: Any = None):
    """Safely get item from list with fallback"""
    try:
        if items and len(items) > index:
            return items[index]
        return default
    except (IndexError, TypeError):
        return default

def safe_random_choice(items: List, default_items: Optional[List] = None) -> Any:
    """Safely choose random item with fallback"""
    try:
        if items and len(items) > 0:
            return random.choice(items)
        elif default_items and len(default_items) > 0:
            return random.choice(default_items)
        else:
            return "Mathematics"  # Ultimate fallback
    except (IndexError, TypeError):
        return "Mathematics"

def safe_get_subjects(user_data: Dict, default_subjects: Optional[List] = None) -> List[str]:
    """Safely get user subjects with fallback"""
    if default_subjects is None:
        default_subjects = ["Mathematics", "Physics", "Chemistry", "Literature"]
    
    try:
        subjects = user_data.get("subjects_interest", [])
        if not subjects or len(subjects) == 0:
            subjects = default_subjects
        return subjects
    except (AttributeError, TypeError):
        return default_subjects

# Enhanced user stats management
def get_user_stats(user_id: str) -> Dict[str, Any]:
    """Get or initialize user statistics"""
    if user_id not in st.session_state.user_stats:
        st.session_state.user_stats[user_id] = {
            'overall_progress': 0,
            'study_streak': 0,
            'study_time_today': 0,
            'achievements': 0,
            'last_activity_date': None,
            'total_study_time': 0,
            'sessions_completed': 0,
            'problems_solved': 0,
            'accuracy_rate': 60,
            'level': 1,
            'experience_points': 0,
            'favorite_subjects': [],
            'weak_areas': [],
            'badges': [],
            'daily_goals': {
                'study_time': 2.0,
                'problems_solved': 10,
                'sessions_completed': 2
            }
        }
    return st.session_state.user_stats[user_id]

def update_user_stats(user_id: str, activity_type: str, progress_amount: float = 0, 
                     time_spent: float = 0, subject: Optional[str] = None) -> Dict[str, Any]:
    """Update user statistics based on activity"""
    try:
        stats = get_user_stats(user_id)
        today = datetime.now().date()
        
        # Update activity timestamp
        st.session_state.last_activity = datetime.now()
        
        # Update study time
        stats['study_time_today'] += time_spent
        stats['total_study_time'] += time_spent
        
        # Update progress
        stats['overall_progress'] = min(100, stats['overall_progress'] + progress_amount)
        
        # Update experience points
        stats['experience_points'] += int(progress_amount * 10)
        
        # Update level (every 100 XP = 1 level)
        new_level = (stats['experience_points'] // 100) + 1
        if new_level > stats['level']:
            stats['level'] = new_level
            award_achievement(user_id, 'level_up')
        
        # Update streak
        if stats['last_activity_date'] != today:
            if stats['last_activity_date'] == today - timedelta(days=1):
                stats['study_streak'] += 1
            else:
                stats['study_streak'] = 1
            stats['last_activity_date'] = today
        
        # Activity-specific updates
        if activity_type == 'lesson_completed':
            stats['sessions_completed'] += 1
            if stats['sessions_completed'] % 5 == 0:
                award_achievement(user_id, 'session_milestone')
                
        elif activity_type == 'problem_solved':
            stats['problems_solved'] += 1
            stats['accuracy_rate'] = min(100, stats['accuracy_rate'] + 0.5)
            if stats['problems_solved'] % 10 == 0:
                award_achievement(user_id, 'problem_solver')
        
        # Check for streak achievements
        if stats['study_streak'] >= 7 and stats['study_streak'] % 7 == 0:
            award_achievement(user_id, 'streak_master')
        
        # Update subject-specific tracking
        if subject and subject not in stats['favorite_subjects'] and len(stats['favorite_subjects']) < 3:
            stats['favorite_subjects'].append(subject)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")
        return get_user_stats(user_id)

def award_achievement(user_id: str, achievement_type: str):
    """Award an achievement to a user"""
    try:
        stats = get_user_stats(user_id)
        
        achievement_definitions = {
            'level_up': {
                'name': 'Level Up! 🆙',
                'description': 'Reached a new level',
                'points': 50,
                'icon': '🆙'
            },
            'session_milestone': {
                'name': 'Session Master 📚',
                'description': 'Completed 5 study sessions',
                'points': 25,
                'icon': '📚'
            },
            'problem_solver': {
                'name': 'Problem Solver 🧮',
                'description': 'Solved 10 practice problems',
                'points': 30,
                'icon': '🧮'
            },
            'streak_master': {
                'name': 'Streak Master 🔥',
                'description': 'Maintained a 7-day study streak',
                'points': 100,
                'icon': '🔥'
            }
        }
        
        if achievement_type in achievement_definitions and achievement_type not in stats['badges']:
            achievement = achievement_definitions[achievement_type]
            stats['badges'].append(achievement_type)
            stats['achievements'] += 1
            stats['experience_points'] += achievement['points']
            
            st.success(f"🏆 Achievement Unlocked: {achievement['name']}")
            
    except Exception as e:
        logger.error(f"Error awarding achievement: {e}")

def login_page():
    """Login and Registration page"""
    st.markdown("""
    <div class="main-header">
        <h1>🎓 EduTech AI Learning Platform</h1>
        <p>Personalized Learning Experiences Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            render_signin_tab()
        
        with tab2:
            render_registration_tab()

def render_signin_tab():
    """Render the sign-in tab"""
    st.subheader("Welcome Back!")
    
    with st.form("signin_form"):
        email = st.text_input("Email Address", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            signin_submitted = st.form_submit_button("Sign In", use_container_width=True)
        with col_b:
            demo_mode = st.form_submit_button("Try Demo", use_container_width=True)
        
        if signin_submitted:
            handle_signin(email, password)
        
        if demo_mode:
            st.session_state.show_demo_options = True
    
    # Demo mode section
    if st.session_state.get('show_demo_options', False):
        render_demo_options()

def handle_signin(email: str, password: str):
    """Handle user sign-in"""
    if not email or not password:
        st.error("Please enter both email and password.")
        return
    
    # Check if user exists
    user_found = None
    for user_id, user_data in st.session_state.all_users.items():
        if user_data.get("email") == email:
            user_found = user_id
            break
    
    if user_found:
        st.session_state.current_user = user_found
        st.success(f"Welcome back, {st.session_state.all_users[user_found]['name']}! 🎉")
        time.sleep(1)
        st.rerun()
    else:
        st.error("Account not found. Please check your email or create a new account.")

def render_demo_options():
    """Render demo account options"""
    st.markdown("---")
    st.subheader("Try Demo Account")
    demo_options = {
        "Demo Student": "demo_student",
        "Demo Tutor": "demo_tutor", 
        "Demo Parent": "demo_parent",
        "Demo Teacher": "demo_teacher"
    }
    
    selected_demo = st.selectbox("Choose demo role:", list(demo_options.keys()))
    
    if st.button("Enter Demo", use_container_width=True):
        st.session_state.current_user = demo_options[selected_demo]
        st.session_state.show_demo_options = False
        st.success(f"Entering demo as {selected_demo}...")
        time.sleep(1)
        st.rerun()

def render_registration_tab():
    """Render the registration tab"""
    st.subheader("Join EduTech Today!")
    
    with st.form("registration_form"):
        name = st.text_input("Full Name *", placeholder="Enter your full name")
        email = st.text_input("Email Address *", placeholder="Enter your email")
        password = st.text_input("Password *", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password")
        
        st.markdown("---")
        st.subheader("What's your role?")
        
        role = st.selectbox("I am a...", [
            "",
            "Student - I want to learn and improve my skills",
            "Tutor - I want to help students learn effectively", 
            "Parent - I want to monitor my child's progress",
            "Teacher - I want to manage my classroom",
            "Expert - I want to create educational content"
        ])
        
        # Role-specific fields
        role_data = render_role_specific_fields(role)
        
        # Terms and conditions
        st.markdown("---")
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            handle_registration(name, email, password, confirm_password, role, role_data, agree_terms)

def render_role_specific_fields(role: str) -> Dict[str, Any]:
    """Render role-specific registration fields"""
    role_data = {}
    
    if "Student" in str(role):
        st.markdown("### Tell us about yourself")
        role_data['age'] = st.number_input("Age", min_value=5, max_value=25, value=16)
        role_data['grade'] = st.selectbox("Grade Level", 
                               ["", "K", "1st", "2nd", "3rd", "4th", "5th", "6th", 
                                "7th", "8th", "9th", "10th", "11th", "12th", "University"])
        role_data['learning_style'] = st.multiselect("How do you prefer to learn?", LEARNING_STYLES)
        role_data['subjects_interest'] = st.multiselect("What subjects interest you?", SUBJECTS)
        
    elif "Tutor" in str(role):
        st.markdown("### Tutor Information")
        role_data['specialization'] = st.multiselect("Your specialization subjects", SUBJECTS)
        role_data['experience'] = st.selectbox("Years of tutoring experience", 
                                    ["Less than 1 year", "1-3 years", "3-5 years", "5+ years"])
        
    elif "Parent" in str(role):
        st.markdown("### Parent Information")
        role_data['num_children'] = st.number_input("Number of children", min_value=1, max_value=10, value=1)
        role_data['children_ages'] = st.text_input("Children's ages (separated by commas)", 
                                       placeholder="e.g., 8, 12, 16")
        
    elif "Teacher" in str(role):
        st.markdown("### Teacher Information")
        role_data['subjects_taught'] = st.multiselect("Subjects you teach", SUBJECTS)
        role_data['grade_levels'] = st.multiselect("Grade levels you teach", 
                                      ["Elementary", "Middle School", "High School", "University"])
        
    elif "Expert" in str(role):
        st.markdown("### Expert Information")
        role_data['expertise_areas'] = st.multiselect("Your areas of expertise", SUBJECTS)
        role_data['credentials'] = st.text_area("Brief description of your credentials", 
                                   placeholder="PhD in Mathematics, 10 years industry experience...")
    
    return role_data

def handle_registration(name: str, email: str, password: str, confirm_password: str, 
                       role: str, role_data: Dict, agree_terms: bool):
    """Handle user registration"""
    # Validation
    if not all([name, email, password, confirm_password, role, agree_terms]):
        st.error("Please fill in all required fields and agree to the terms.")
        return
    
    if not role.strip():
        st.error("Please select your role.")
        return
    
    if password != confirm_password:
        st.error("Passwords do not match.")
        return
    
    if len(password) < 6:
        st.error("Password must be at least 6 characters long.")
        return
    
    # Check if email already exists
    email_exists = any(user_data.get("email") == email for user_data in st.session_state.all_users.values())
    
    if email_exists:
        st.error("An account with this email already exists. Please sign in instead.")
        return
    
    # Create new user
    create_new_user(name, email, password, role, role_data)

def create_new_user(name: str, email: str, password: str, role: str, role_data: Dict):
    """Create a new user account"""
    try:
        # Extract role from selection
        user_role = role.split(" - ")[0]
        
        # Create new user data
        new_user_id = f"user_{len(st.session_state.all_users) + 1}"
        user_data = {
            "name": name,
            "role": user_role,
            "email": email,
            "password": password  # In production, this would be hashed
        }
        
        # Add role-specific data
        if user_role == "Student":
            user_data.update({
                "age": role_data.get('age'),
                "grade": role_data.get('grade'),
                "learning_style": role_data.get('learning_style', []),
                "subjects_interest": role_data.get('subjects_interest', []),
                "progress": {subject: random.randint(40, 90) 
                           for subject in role_data.get('subjects_interest', [])[:5]}
            })
        elif user_role == "Tutor":
            user_data.update({
                "specialization": role_data.get('specialization', []),
                "experience": role_data.get('experience'),
                "students": []
            })
        elif user_role == "Parent":
            user_data.update({
                "num_children": role_data.get('num_children', 1),
                "children_ages": role_data.get('children_ages', ''),
                "children": [f"Child {i+1}" for i in range(role_data.get('num_children', 1))]
            })
        elif user_role == "Teacher":
            user_data.update({
                "subjects": role_data.get('subjects_taught', []),
                "grade_levels": role_data.get('grade_levels', []),
                "class_size": random.randint(20, 35)
            })
        elif user_role == "Expert":
            user_data.update({
                "expertise_areas": role_data.get('expertise_areas', []),
                "credentials": role_data.get('credentials', '')
            })
        
        # Store user data
        st.session_state.all_users[new_user_id] = user_data
        st.session_state.current_user = new_user_id
        
        st.success(f"Welcome to EduTech AI Learning Platform, {name}! 🎉")
        time.sleep(2)
        st.rerun()
        
    except Exception as e:
        logger.error(f"Error creating new user: {e}")
        st.error("Failed to create account. Please try again.")

def student_dashboard():
    """Student dashboard with personalized learning"""
    try:
        user_data = st.session_state.all_users[st.session_state.current_user]
        user_id = st.session_state.current_user
        stats = get_user_stats(user_id)
        
        st.title(f"Welcome back, {user_data['name']}! 🎓")
        
        # Progress Overview with real stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Overall Progress</h3>
                <h2>{stats['overall_progress']:.0f}%</h2>
                <p>Level {stats['level']}</p>
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
                <p>Goal: {stats['daily_goals']['study_time']} hrs</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🏆 Achievements</h3>
                <h2>{stats['achievements']}</h2>
                <p>{len(stats['badges'])} badges earned</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display recent achievements
        if stats['badges']:
            st.subheader("🏅 Recent Achievements")
            achievement_cols = st.columns(min(4, len(stats['badges'])))
            for i, badge in enumerate(stats['badges'][-4:]):  # Show last 4 badges
                with achievement_cols[i]:
                    st.markdown(f'<div class="achievement-badge">{badge.replace("_", " ").title()}</div>', 
                              unsafe_allow_html=True)
        
        # Subject Progress with safe handling
        st.subheader("📈 Subject Progress")
        
        # Use user's actual progress or create sample data
        if user_data.get("progress"):
            current_progress = user_data["progress"].copy()
            
            # Add some adaptive learning based on user stats
            if stats['sessions_completed'] > 0:
                for subject in current_progress:
                    boost = min(stats['sessions_completed'] * 2, 20)
                    current_progress[subject] = min(100, current_progress[subject] + boost)
            
            progress_data = pd.DataFrame([
                {"Subject": subject, "Progress": progress}
                for subject, progress in current_progress.items()
            ])
        else:
            # Safe default progress for users without specific progress data
            default_subjects = safe_get_subjects(user_data, ["Mathematics", "Physics", "Chemistry", "Literature"])
            progress_data = pd.DataFrame([
                {"Subject": subject, "Progress": max(0, min(100, random.randint(20, 40) + stats['overall_progress']))}
                for subject in default_subjects[:4]
            ])
        
        if not progress_data.empty:
            fig = px.bar(progress_data, x="Subject", y="Progress", 
                         color="Progress", color_continuous_scale="viridis",
                         title="Your Learning Progress by Subject")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Interactive Learning Path
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Today's Learning Plan")
            
            # Generate learning tasks based on user's interests with safe handling
            subjects = safe_get_subjects(user_data, ["Mathematics", "Physics", "Literature", "History"])
            learning_tasks = []
            
            # Adaptive difficulty based on progress
            difficulty_level = "Beginner" if stats['overall_progress'] < 30 else "Intermediate" if stats['overall_progress'] < 70 else "Advanced"
            
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
                            # Update stats when starting a lesson
                            progress_gained = random.randint(3, 8)
                            time_spent = task['estimated_hours']
                            
                            update_user_stats(user_id, 'lesson_completed', 
                                            progress_amount=progress_gained, 
                                            time_spent=time_spent,
                                            subject=task['type'])
                            
                            # Update subject progress
                            if user_data.get("progress") and task['type'] in user_data["progress"]:
                                user_data["progress"][task['type']] = min(100, 
                                    user_data["progress"][task['type']] + progress_gained)
                            
                            st.success(f"🎉 Great job! You gained {progress_gained} progress points and studied for {time_spent:.1f} hours!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                            
                    with col_b:
                        if st.button(f"Get Help", key=f"help_{task['task']}"):
                            st.info("🤖 AI tutor is ready to help! Ask any questions about this topic.")
        
        with col2:
            st.subheader("🤖 AI Learning Assistant")
            
            # Interactive practice problems
            st.subheader("🧮 Quick Practice")
            
            if st.button("Generate Practice Problem", use_container_width=True):
                problems = {
                    "Mathematics": [
                        {"question": "Solve: 2x + 5 = 13", "answer": "4", "type": "algebra"},
                        {"question": "Find the area of a circle with radius 7cm (use π ≈ 3.14)", "answer": "153.86", "type": "geometry"},
                        {"question": "Simplify: (3x²)(4x³)", "answer": "12x⁵", "type": "algebra"},
                        {"question": "What is 15% of 240?", "answer": "36", "type": "percentage"}
                    ],
                    "Physics": [
                        {"question": "A car accelerates at 2 m/s². What's its velocity after 5 seconds from rest?", "answer": "10 m/s", "type": "motion"},
                        {"question": "Calculate the force needed to accelerate a 10kg object at 3 m/s²", "answer": "30 N", "type": "forces"},
                        {"question": "What's the kinetic energy of a 5kg object moving at 10 m/s?", "answer": "250 J", "type": "energy"}
                    ],
                    "Chemistry": [
                        {"question": "Balance this equation: H₂ + O₂ → H₂O", "answer": "2H₂ + O₂ → 2H₂O", "type": "equations"},
                        {"question": "How many moles are in 36g of H₂O? (H₂O = 18 g/mol)", "answer": "2 moles", "type": "moles"},
                        {"question": "What's the pH of a 0.1M HCl solution?", "answer": "1", "type": "acids"}
                    ],
                    "Literature": [
                        {"question": "What literary device uses comparison with 'like' or 'as'?", "answer": "simile", "type": "devices"},
                        {"question": "Who wrote 'Romeo and Juliet'?", "answer": "shakespeare", "type": "authors"}
                    ],
                    "History": [
                        {"question": "In what year did World War II end?", "answer": "1945", "type": "dates"},
                        {"question": "Who was the first President of the United States?", "answer": "george washington", "type": "people"}
                    ]
                }
                
                # FIXED: Safe subject selection
                user_subjects = safe_get_subjects(user_data, ["Mathematics", "Physics", "Chemistry"])
                selected_subject = safe_random_choice(user_subjects, ["Mathematics", "Physics", "Chemistry"])
                
                if selected_subject in problems:
                    problem = safe_random_choice(problems[selected_subject], problems["Mathematics"])
                    st.info(f"**{selected_subject} Problem:** {problem['question']}")
                    
                    user_answer = st.text_input("Your answer:", key=f"answer_{random.randint(1000,9999)}")
                    
                    if st.button("Submit Answer") and user_answer:
                        # Check answer
                        is_correct = user_answer.lower().strip() == problem['answer'].lower().strip()
                        
                        if is_correct:
                            progress_gained = random.randint(1, 3)
                            update_user_stats(user_id, 'problem_solved', progress_amount=progress_gained, subject=selected_subject)
                            st.success(f"✅ Correct! You earned {progress_gained} progress points!")
                            
                            # Update subject progress
                            if user_data.get("progress") and selected_subject in user_data["progress"]:
                                user_data["progress"][selected_subject] = min(100, 
                                    user_data["progress"][selected_subject] + progress_gained)
                            
                            st.balloons()
                        else:
                            st.error(f"❌ Not quite right. The correct answer is: {problem['answer']}")
                            st.info("💡 Don't worry! Learning from mistakes is part of the process.")
                        
                        time.sleep(1)
                        st.rerun()
            
            # Chat Interface
            st.subheader("💬 Chat with AI Tutor")
            st.write("Ask me anything about your studies!")
            
            # Initialize chat history if not exists
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            # Display recent chat messages
            for message in st.session_state.chat_history[-3:]:  # Show last 3 messages
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message">👤 {message["content"]}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message ai-message">🤖 {message["content"]}</div>', 
                              unsafe_allow_html=True)
            
            user_input = st.text_input("Type your question here...", key="chat_input")
            
            if st.button("Send") and user_input:
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
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
                
                ai_response = safe_random_choice(ai_responses, ["That's a great question! Let me help you with that..."])
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                
                # Small progress for engaging with AI
                update_user_stats(user_id, 'chat_interaction', progress_amount=0.5, time_spent=0.05)
                
                st.rerun()
        
        # Dynamic Recommendations based on progress
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
        
        # Progress Reset Option (for testing)
        with st.expander("🔄 Reset Progress (Demo Purpose)"):
            if st.button("Reset All Stats", type="secondary"):
                if user_id in st.session_state.user_stats:
                    del st.session_state.user_stats[user_id]
                st.success("Stats reset! Refresh to see changes.")
                st.rerun()
    
    except Exception as e:
        logger.error(f"Error in student dashboard: {e}")
        st.error("An error occurred while loading the dashboard. Please try refreshing the page.")

def practice_page():
    """Enhanced practice page"""
    try:
        user_data = st.session_state.all_users[st.session_state.current_user]
        user_id = st.session_state.current_user
        stats = get_user_stats(user_id)
        
        st.title("🧮 Practice Center")
        st.write("Strengthen your skills with interactive practice problems!")
        
        # Practice stats overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Problems Solved", stats['problems_solved'])
        
        with col2:
            st.metric("Practice Sessions", stats['sessions_completed'])
        
        with col3:
            accuracy = stats['accuracy_rate']
            st.metric("Accuracy Rate", f"{accuracy:.1f}%", delta=f"+{min(5, stats['problems_solved'])}%")
        
        with col4:
            difficulty_level = "Beginner" if stats['overall_progress'] < 30 else "Intermediate" if stats['overall_progress'] < 70 else "Advanced"
            st.metric("Current Level", difficulty_level)
        
        # Subject selection with safe handling
        st.subheader("📚 Choose Your Subject")
        
        subjects = safe_get_subjects(user_data, ["Mathematics", "Physics", "Chemistry", "Literature", "History"])
        selected_subject = st.selectbox("Select a subject to practice:", subjects)
        
        # Difficulty selection based on progress
        col1, col2 = st.columns(2)
        
        with col1:
            if stats['overall_progress'] < 30:
                available_difficulties = ["Beginner"]
            elif stats['overall_progress'] < 70:
                available_difficulties = ["Beginner", "Intermediate"]
            else:
                available_difficulties = ["Beginner", "Intermediate", "Advanced"]
            
            selected_difficulty = st.selectbox("Choose difficulty:", available_difficulties)
        
        with col2:
            practice_type = st.selectbox("Practice type:", [
                "Single Problem",
                "Quick Quiz (5 questions)",
                "Timed Challenge",
                "Review Mode"
            ])
        
        # Enhanced problem bank
        problem_banks = {
            "Mathematics": {
                "Beginner": [
                    {"question": "What is 15 + 27?", "answer": "42", "type": "arithmetic", "points": 2},
                    {"question": "Solve for x: x + 5 = 12", "answer": "7", "type": "algebra", "points": 3},
                    {"question": "What is 8 × 9?", "answer": "72", "type": "arithmetic", "points": 2},
                    {"question": "What is 144 ÷ 12?", "answer": "12", "type": "arithmetic", "points": 2}
                ],
                "Intermediate": [
                    {"question": "Solve: 2x + 7 = 19", "answer": "6", "type": "algebra", "points": 4},
                    {"question": "Find the area of a circle with radius 5cm (use π ≈ 3.14)", "answer": "78.5", "type": "geometry", "points": 5},
                    {"question": "Simplify: (3x²)(4x³)", "answer": "12x⁵", "type": "algebra", "points": 4}
                ],
                "Advanced": [
                    {"question": "Find the derivative of f(x) = 3x² + 2x + 1", "answer": "6x + 2", "type": "calculus", "points": 6},
                    {"question": "Solve the quadratic equation: x² - 5x + 6 = 0", "answer": "x = 2, 3", "type": "algebra", "points": 6}
                ]
            },
            "Physics": {
                "Beginner": [
                    {"question": "What is the unit of force?", "answer": "Newton", "type": "concepts", "points": 2},
                    {"question": "If a car travels 60 km in 2 hours, what is its speed?", "answer": "30 km/h", "type": "motion", "points": 3}
                ],
                "Intermediate": [
                    {"question": "A car accelerates at 2 m/s². What's its velocity after 5 seconds from rest?", "answer": "10 m/s", "type": "motion", "points": 4},
                    {"question": "Calculate force: F = ma, where m = 10kg and a = 3 m/s²", "answer": "30 N", "type": "forces", "points": 4}
                ],
                "Advanced": [
                    {"question": "Calculate the electric field 2m from a 5μC charge (k = 9×10⁹)", "answer": "11,250 N/C", "type": "electricity", "points": 6}
                ]
            },
            "Chemistry": {
                "Beginner": [
                    {"question": "What is the chemical symbol for water?", "answer": "H2O", "type": "formulas", "points": 2},
                    {"question": "How many protons does carbon have?", "answer": "6", "type": "atoms", "points": 2}
                ],
                "Intermediate": [
                    {"question": "Balance: H₂ + O₂ → H₂O", "answer": "2H₂ + O₂ → 2H₂O", "type": "equations", "points": 4},
                    {"question": "How many moles are in 36g of H₂O? (H₂O = 18 g/mol)", "answer": "2 moles", "type": "moles", "points": 4}
                ],
                "Advanced": [
                    {"question": "What is the pH of 0.01 M HCl solution?", "answer": "2", "type": "acids", "points": 5}
                ]
            }
        }
        
        # Generate practice session
        if st.button("🎯 Start Practice Session", use_container_width=True, type="primary"):
            if selected_subject in problem_banks and selected_difficulty in problem_banks[selected_subject]:
                problems = problem_banks[selected_subject][selected_difficulty]
                
                if practice_type == "Quick Quiz (5 questions)":
                    # Generate a quiz
                    st.subheader(f"📝 {selected_subject} Quiz - {selected_difficulty} Level")
                    
                    if problems:
                        # Safely sample problems
                        quiz_problems = []
                        num_problems = min(5, len(problems))
                        if num_problems > 0:
                            quiz_problems = random.sample(problems, num_problems)
                        
                        if quiz_problems:
                            correct_answers = 0
                            
                            with st.form("quiz_form"):
                                user_answers = []
                                for i, problem in enumerate(quiz_problems):
                                    st.write(f"**Question {i+1}:** {problem['question']}")
                                    answer = st.text_input(f"Your answer:", key=f"q_{i}")
                                    user_answers.append(answer)
                                
                                submitted = st.form_submit_button("Submit Quiz")
                                
                                if submitted:
                                    for i, (problem, user_answer) in enumerate(zip(quiz_problems, user_answers)):
                                        if user_answer.lower().strip() == problem['answer'].lower().strip():
                                            correct_answers += 1
                                            st.success(f"✅ Question {i+1}: Correct!")
                                        else:
                                            st.error(f"❌ Question {i+1}: Incorrect. Answer: {problem['answer']}")
                                    
                                    # Calculate score and update stats
                                    score = (correct_answers / len(quiz_problems)) * 100
                                    progress_gained = correct_answers * 2
                                    
                                    st.subheader(f"🎉 Quiz Complete!")
                                    st.write(f"**Score:** {correct_answers}/{len(quiz_problems)} ({score:.0f}%)")
                                    st.write(f"**Progress gained:** {progress_gained} points")
                                    
                                    # Update user stats
                                    update_user_stats(user_id, 'problem_solved', 
                                                    progress_amount=progress_gained, 
                                                    time_spent=0.25,
                                                    subject=selected_subject)
                                    
                                    # Update subject progress
                                    if user_data.get("progress") and selected_subject in user_data["progress"]:
                                        user_data["progress"][selected_subject] = min(100, 
                                            user_data["progress"][selected_subject] + progress_gained)
                                    
                                    if score >= 80:
                                        st.balloons()
                                        st.success("🌟 Excellent work! You're mastering this topic!")
                                    elif score >= 60:
                                        st.success("👍 Good job! Keep practicing to improve!")
                                    else:
                                        st.info("📚 Keep studying! Practice makes perfect!")
                                    
                                    time.sleep(2)
                                    st.rerun()
                        else:
                            st.warning("No problems available for quiz.")
                    else:
                        st.warning("No problems available for this difficulty level.")
                
                else:
                    # Single problem practice
                    if problems:
                        problem = safe_random_choice(problems, [{"question": "What is 2 + 2?", "answer": "4", "type": "arithmetic", "points": 1}])
                        
                        st.subheader(f"🔍 {selected_subject} Practice - {selected_difficulty}")
                        st.write(f"**Problem Type:** {problem['type'].title()}")
                        
                        st.info(f"**Question:** {problem['question']}")
                        
                        user_answer = st.text_input("Your answer:", key=f"practice_{random.randint(1000,9999)}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("Check Answer") and user_answer:
                                if user_answer.lower().strip() == problem['answer'].lower().strip():
                                    progress_gained = problem.get('points', 2)
                                    update_user_stats(user_id, 'problem_solved', 
                                                    progress_amount=progress_gained, 
                                                    time_spent=0.1,
                                                    subject=selected_subject)
                                    
                                    # Update subject progress
                                    if user_data.get("progress") and selected_subject in user_data["progress"]:
                                        user_data["progress"][selected_subject] = min(100, 
                                            user_data["progress"][selected_subject] + progress_gained)
                                    
                                    st.success(f"✅ Correct! You earned {progress_gained} progress points!")
                                    st.balloons()
                                else:
                                    st.error(f"❌ Not quite right. The correct answer is: {problem['answer']}")
                                    st.info("💡 Don't worry! Learning from mistakes is part of the process.")
                                
                                time.sleep(1)
                                st.rerun()
                        
                        with col2:
                            if st.button("Skip & Get New Problem"):
                                st.rerun()
                    else:
                        st.warning("No problems available for this subject and difficulty level.")
            else:
                st.error("Problems not available for this subject and difficulty combination.")
    
    except Exception as e:
        logger.error(f"Error in practice page: {e}")
        st.error("An error occurred while loading the practice page. Please try refreshing.")

def tutor_dashboard():
    """Tutor dashboard for managing students and sessions"""
    try:
        user_data = st.session_state.all_users[st.session_state.current_user]
        
        st.title(f"Tutor Dashboard - {user_data['name']} 👨‍🏫")
        
        # Quick Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>👥 Active Students</h3>
                <h2>15</h2>
                <p>This week</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>⏰ Sessions Today</h3>
                <h2>8</h2>
                <p>Scheduled</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Avg. Improvement</h3>
                <h2>23%</h2>
                <p>Student progress</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>⭐ Rating</h3>
                <h2>4.9/5</h2>
                <p>Student feedback</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Student Management
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Student Progress Overview")
            
            # Sample student data
            student_data = pd.DataFrame([
                {"Student": "Alex Johnson", "Subject": "Mathematics", "Progress": 85, "Last Session": "2 days ago", "Next Session": "Today 3 PM"},
                {"Student": "Emma Davis", "Subject": "Physics", "Progress": 72, "Last Session": "1 day ago", "Next Session": "Tomorrow 10 AM"},
                {"Student": "Michael Chen", "Subject": "Chemistry", "Progress": 68, "Last Session": "3 days ago", "Next Session": "Today 5 PM"},
            ])
            
            st.dataframe(student_data, use_container_width=True)
            
            # Quick Session Prep
            st.subheader("🎯 Quick Session Preparation")
            
            selected_student = st.selectbox("Select Student for Session Prep", student_data["Student"].tolist())
            
            if st.button("Generate Session Brief"):
                st.success(f"Session brief generated for {selected_student}!")
                
                st.markdown("""
                **Session Focus Areas:**
                - Quadratic equations (struggling with factoring)
                - Word problems (needs more practice)
                - Graph interpretation (strength to leverage)
                
                **Recommended 10-minute Focus:**
                1. Quick review of factoring methods (3 min)
                2. Solve one challenging word problem together (5 min)
                3. Preview next topics and assign practice (2 min)
                
                **AI Tutor Pre-work:** Student completed 80% of assigned problems, struggled with problems #7, #12, #15
                """)
        
        with col2:
            st.subheader("🔔 Today's Schedule")
            
            schedule = [
                {"time": "10:00 AM", "student": "Sarah Kim", "subject": "Physics", "duration": "10 min"},
                {"time": "11:30 AM", "student": "John Doe", "subject": "Mathematics", "duration": "10 min"},
                {"time": "2:00 PM", "student": "Alex Johnson", "subject": "Mathematics", "duration": "10 min"},
                {"time": "3:30 PM", "student": "Emma Davis", "subject": "Physics", "duration": "10 min"},
                {"time": "5:00 PM", "student": "Michael Chen", "subject": "Chemistry", "duration": "10 min"},
            ]
            
            for session in schedule:
                with st.expander(f"{session['time']} - {session['student']}", expanded=False):
                    st.write(f"**Subject:** {session['subject']}")
                    st.write(f"**Duration:** {session['duration']}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Start Session", key=f"start_{session['student']}"):
                            st.success("Session started!")
                    with col_b:
                        if st.button("View Prep", key=f"prep_{session['student']}"):
                            st.info("Loading session materials...")
        
        # Performance Analytics
        st.subheader("📈 Teaching Performance Analytics")
        
        # Student improvement over time
        dates = pd.date_range(start='2024-01-01', end='2024-06-22', freq='W')
        improvement_data = pd.DataFrame({
            'Date': dates,
            'Average Student Progress': np.random.normal(70, 10, len(dates)).cumsum() / len(dates) + 50
        })
        
        fig = px.line(improvement_data, x='Date', y='Average Student Progress',
                      title='Student Progress Improvement Over Time')
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        logger.error(f"Error in tutor dashboard: {e}")
        st.error("An error occurred while loading the tutor dashboard.")

def intake_assessment():
    """Adaptive intake assessment"""
    try:
        st.header("📋 Personalized Learning Assessment")
        
        user_data = st.session_state.all_users[st.session_state.current_user]
        
        if user_data["role"] == "Student":
            st.subheader("Let's understand your learning preferences!")
            
            with st.form("intake_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Learning Style Assessment")
                    learning_pref = st.radio(
                        "How do you prefer to learn new concepts?",
                        ["Visual (charts, diagrams, mind maps)",
                         "Auditory (listening, discussions)",
                         "Kinesthetic (hands-on activities)",
                         "Reading/Writing (text-based)"]
                    )
                    
                    study_time = st.slider("Available study hours per day", 1, 8, 3)
                    
                    goals = st.multiselect(
                        "Select your academic goals:",
                        ["Improve grades", "Test preparation", "College readiness", 
                         "Skill development", "Career preparation"]
                    )
                
                with col2:
                    st.subheader("Subject Assessment")
                    subjects_interest = st.multiselect("Subjects you enjoy:", SUBJECTS)
                    subjects_struggle = st.multiselect("Subjects you find challenging:", SUBJECTS)
                    
                    motivation = st.select_slider(
                        "How motivated are you to learn?",
                        options=["Low", "Moderate", "High", "Very High"]
                    )
                    
                    tech_comfort = st.select_slider(
                        "How comfortable are you with technology?",
                        options=["Beginner", "Intermediate", "Advanced", "Expert"]
                    )
                
                submitted = st.form_submit_button("Complete Assessment", use_container_width=True)
                
                if submitted:
                    st.session_state.assessment_results = {
                        "learning_preference": learning_pref,
                        "study_time": study_time,
                        "goals": goals,
                        "interests": subjects_interest,
                        "struggles": subjects_struggle,
                        "motivation": motivation,
                        "tech_comfort": tech_comfort
                    }
                    
                    # Update user data with assessment results
                    user_data.update({
                        "subjects_interest": subjects_interest,
                        "subjects_struggle": subjects_struggle,
                        "daily_study_time": study_time
                    })
                    
                    # Award assessment completion achievement
                    update_user_stats(st.session_state.current_user, 'assessment_completed', progress_amount=5)
                    
                    st.success("Assessment completed! Your personalized learning plan is being generated...")
                    time.sleep(2)
                    st.rerun()
    
    except Exception as e:
        logger.error(f"Error in intake assessment: {e}")
        st.error("An error occurred during the assessment. Please try again.")

def main():
    """Main application function"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Initialize demo users if not present
        if not st.session_state.all_users:
            st.session_state.all_users = DEMO_USERS.copy()
        
        # Check if user is logged in
        if st.session_state.current_user is None:
            login_page()
            return
        
        # Get current user data
        user_data = st.session_state.all_users[st.session_state.current_user]
        
        # Sidebar navigation
        with st.sidebar:
            st.title(f"Welcome, {user_data['name']}")
            st.write(f"**Role:** {user_data['role']}")
            
            # Navigation menu
            if user_data['role'] == 'Student':
                if 'assessment_results' not in st.session_state or not st.session_state.assessment_results:
                    page = st.selectbox("Navigate", ["Assessment", "Dashboard", "Practice"])
                else:
                    page = st.selectbox("Navigate", ["Dashboard", "Practice", "Assessment"])
            else:
                page = st.selectbox("Navigate", ["Dashboard"])
            
            # Quick stats
            st.markdown("---")
            st.subheader("Quick Stats")
            
            # Get user stats for sidebar display
            user_stats = get_user_stats(st.session_state.current_user)
            
            if user_data['role'] == 'Student':
                st.metric("Overall Progress", f"{user_stats['overall_progress']:.0f}%", 
                         delta=f"Level {user_stats['level']}")
                st.metric("Study Streak", f"{user_stats['study_streak']} days", 
                         delta="🔥" if user_stats['study_streak'] > 0 else None)
                st.metric("Problems Solved", user_stats['problems_solved'])
            elif user_data['role'] == 'Tutor':
                st.metric("Active Students", "15", "👥")
                st.metric("Sessions Today", "8", "📅")
            elif user_data['role'] == 'Parent':
                st.metric("Child's Progress", "68%", "📈 +8%")
            elif user_data['role'] == 'Teacher':
                st.metric("Class Average", "76%", "📊")
                st.metric("Students at Risk", "3", "⚠️")
            
            # Logout button
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                st.session_state.current_user = None
                st.session_state.chat_history = []
                st.session_state.assessment_results = {}
                st.rerun()
        
        # Main content area
        if user_data['role'] == 'Student':
            if page == "Assessment":
                intake_assessment()
            elif page == "Dashboard":
                student_dashboard()
            elif page == "Practice":
                practice_page()
        elif user_data['role'] == 'Tutor':
            if page == "Dashboard":
                tutor_dashboard()
        elif user_data['role'] == 'Parent':
            if page == "Dashboard":
                parent_dashboard()
        elif user_data['role'] == 'Teacher':
            if page == "Dashboard":
                teacher_dashboard()
        elif user_data['role'] == 'Expert':
            if page == "Dashboard":
                expert_dashboard()
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        st.error("An error occurred while loading the application. Please refresh the page.")
        st.write("If the problem persists, please contact support.")

def parent_dashboard():
    """Parent dashboard for monitoring child's progress"""
    try:
        user_data = st.session_state.all_users[st.session_state.current_user]
        
        st.title(f"Parent Dashboard - {user_data['name']} 👨‍👩‍👧‍👦")
        
        # Child selection
        children = user_data.get("children", ["Child 1"])
        child_name = st.selectbox("Select Child", children)
        
        # Use demo student data for child progress
        child_data = {
            "progress": {
                "Mathematics": 85,
                "Physics": 78,
                "Chemistry": 65,
                "Literature": 45,
                "History": 40
            }
        }
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📚 Study Time</h3>
                <h2>18.5 hrs</h2>
                <p>This week</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Improvement</h3>
                <h2>+15%</h2>
                <p>Overall progress</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>🎯 Goals Met</h3>
                <h2>7/10</h2>
                <p>This month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>🏆 Achievements</h3>
                <h2>3 new</h2>
                <p>Badges earned</p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Academic Progress")
            
            # Progress chart
            progress_df = pd.DataFrame([
                {"Subject": subject, "Progress": progress, "Target": 80}
                for subject, progress in child_data["progress"].items()
            ])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Current Progress', x=progress_df['Subject'], y=progress_df['Progress']))
            fig.add_trace(go.Scatter(name='Target', x=progress_df['Subject'], y=progress_df['Target'], 
                                    mode='markers', marker=dict(color='red', size=10, symbol='diamond')))
            
            fig.update_layout(title='Subject-wise Progress vs Targets')
            st.plotly_chart(fig, use_container_width=True)
            
            # Knowledge gaps
            st.subheader("🎯 Areas Needing Attention")
            
            weak_subjects = [subject for subject, progress in child_data["progress"].items() if progress < 60]
            
            for subject in weak_subjects:
                progress = child_data["progress"][subject]
                st.markdown(f"""
                <div class="role-card">
                    <h4>{subject}</h4>
                    <p><strong>Current Level:</strong> {progress}%</p>
                    <p><strong>Recommended Action:</strong> Additional practice sessions</p>
                    <p><strong>Resources:</strong> Extra worksheets, online tutorials</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📅 Weekly Activity Summary")
            
            # Activity timeline
            activities = [
                {"Date": "June 22", "Activity": "Mathematics Quiz", "Score": "85%", "Status": "Completed"},
                {"Date": "June 21", "Activity": "Physics Lab Simulation", "Score": "78%", "Status": "Completed"},
                {"Date": "June 20", "Activity": "Literature Essay", "Score": "Pending", "Status": "In Progress"},
                {"Date": "June 19", "Activity": "History Timeline Project", "Score": "92%", "Status": "Completed"},
            ]
            
            for activity in activities:
                status_color = "🟢" if activity["Status"] == "Completed" else "🟡"
                st.markdown(f"""
                {status_color} **{activity['Date']}** - {activity['Activity']}  
                Score: {activity['Score']} | Status: {activity['Status']}
                """)
            
            st.subheader("💡 How You Can Help")
            
            recommendations = [
                "Review literature reading comprehension techniques together",
                "Practice history timeline memorization with flashcards",
                "Encourage consistent study schedule (2 hours daily)",
                "Celebrate achievements in Mathematics and Physics"
            ]
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
            
            # Communication with tutors
            st.subheader("💬 Tutor Communication")
            
            if st.button("Schedule Parent-Tutor Meeting"):
                st.success("Meeting request sent! You'll receive a confirmation email.")
            
            if st.button("Send Message to Tutor"):
                st.text_area("Message", placeholder="Type your message to the tutor...")
                if st.button("Send"):
                    st.success("Message sent successfully!")
    
    except Exception as e:
        logger.error(f"Error in parent dashboard: {e}")
        st.error("An error occurred while loading the parent dashboard.")

def teacher_dashboard():
    """Teacher dashboard for classroom management"""
    try:
        user_data = st.session_state.all_users[st.session_state.current_user]
        
        st.title(f"Teacher Dashboard - {user_data['name']} 👨‍🏫")
        
        # Class Overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>👥 Total Students</h3>
                <h2>28</h2>
                <p>Active learners</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Class Average</h3>
                <h2>76%</h2>
                <p>Overall progress</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📚 Assignments</h3>
                <h2>5</h2>
                <p>Pending review</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>⚠️ At Risk</h3>
                <h2>3</h2>
                <p>Students need help</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Class Performance
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Class Performance Distribution")
            
            # Generate sample grade distribution
            grades = np.random.normal(75, 15, 28)
            grades = np.clip(grades, 0, 100)
            
            fig = px.histogram(x=grades, nbins=10, title="Grade Distribution",
                              labels={'x': 'Grades', 'y': 'Number of Students'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Students needing attention
            st.subheader("🚨 Students Requiring Attention")
            
            at_risk_students = [
                {"Name": "John Smith", "Average": "45%", "Issues": "Math fundamentals, attendance"},
                {"Name": "Lisa Wang", "Average": "52%", "Issues": "Reading comprehension"},
                {"Name": "Carlos Rodriguez", "Average": "48%", "Issues": "Language barrier, homework completion"}
            ]
            
            for student in at_risk_students:
                with st.expander(f"⚠️ {student['Name']} - {student['Average']}"):
                    st.write(f"**Issues:** {student['Issues']}")
                    st.write("**Recommended Actions:**")
                    st.write("- One-on-one tutoring sessions")
                    st.write("- Parent conference")
                    st.write("- Modified assignments")
                    
                    if st.button(f"Create Intervention Plan", key=f"intervention_{student['Name']}"):
                        st.success("Intervention plan created and sent to student's support team!")
        
        with col2:
            st.subheader("📅 Curriculum Progress")
            
            curriculum_topics = [
                {"Topic": "Algebra Fundamentals", "Progress": 100, "Status": "Completed"},
                {"Topic": "Quadratic Equations", "Progress": 85, "Status": "In Progress"},
                {"Topic": "Functions and Graphs", "Progress": 60, "Status": "In Progress"},
                {"Topic": "Trigonometry Basics", "Progress": 0, "Status": "Not Started"},
                {"Topic": "Statistics Introduction", "Progress": 0, "Status": "Not Started"},
            ]
            
            for topic in curriculum_topics:
                progress = topic["Progress"]
                if progress == 100:
                    status_icon = "✅"
                elif progress > 0:
                    status_icon = "🔄"
                else:
                    status_icon = "⏳"
                
                st.markdown(f"""
                {status_icon} **{topic['Topic']}**  
                Progress: {progress}% | Status: {topic['Status']}
                """)
                
                if progress < 100:
                    st.progress(progress / 100)
            
            st.subheader("🎯 Assignment Creation")
            
            with st.form("create_assignment"):
                assignment_title = st.text_input("Assignment Title")
                assignment_subject = st.selectbox("Subject", user_data.get("subjects", SUBJECTS))
                assignment_type = st.selectbox("Type", ["Quiz", "Homework", "Project", "Test"])
                due_date = st.date_input("Due Date")
                
                submitted = st.form_submit_button("Create Assignment")
                
                if submitted and assignment_title:
                    st.success(f"Assignment '{assignment_title}' created successfully!")
    
    except Exception as e:
        logger.error(f"Error in teacher dashboard: {e}")
        st.error("An error occurred while loading the teacher dashboard.")

def expert_dashboard():
    """Expert dashboard for content creation and analysis"""
    try:
        st.title("Expert Dashboard - Content & Curriculum Development 🧠")
        
        # Expert Overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📚 Content Created</h3>
                <h2>127</h2>
                <p>This month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>👥 Students Reached</h3>
                <h2>1,247</h2>
                <p>Using your content</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>⭐ Avg. Rating</h3>
                <h2>4.8/5</h2>
                <p>Content quality</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>🔄 In Review</h3>
                <h2>23</h2>
                <p>Pending approval</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Content Creation Tools
        st.subheader("🛠️ Content Creation Tools")
        
        tab1, tab2, tab3 = st.tabs(["Create Content", "Analytics", "Collaboration"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 New Learning Material")
                
                with st.form("content_creation"):
                    content_title = st.text_input("Content Title")
                    content_subject = st.selectbox("Subject", SUBJECTS)
                    content_type = st.selectbox("Content Type", 
                        ["Video Lesson", "Interactive Exercise", "Mindmap", "Audio Explanation", "Reading Material"])
                    grade_level = st.selectbox("Grade Level", 
                        ["Elementary", "Middle School", "High School", "University"])
                    difficulty = st.slider("Difficulty Level", 1, 10, 5)
                    
                    content_description = st.text_area("Content Description")
                    
                    uploaded_file = st.file_uploader("Upload Content File", 
                        type=['pdf', 'mp4', 'mp3', 'png', 'jpg', 'docx'])
                    
                    if st.form_submit_button("Create Content"):
                        if content_title and content_description:
                            st.success("Content created and submitted for review!")
                        else:
                            st.error("Please fill in all required fields")
            
            with col2:
                st.subheader("🤖 AI Content Assistant")
                
                st.write("Generate content suggestions using AI:")
                
                ai_prompt = st.text_area("Describe the content you want to create:")
                
                if st.button("Generate AI Suggestions"):
                    suggestions = [
                        "Interactive quadratic equation solver with step-by-step explanations",
                        "Visual mindmap connecting algebra concepts to real-world applications",
                        "Audio explanation series for different learning styles",
                        "Gamified practice problems with immediate feedback"
                    ]
                    
                    st.write("**AI Suggestions:**")
                    for i, suggestion in enumerate(suggestions, 1):
                        st.write(f"{i}. {suggestion}")
        
        with tab2:
            st.subheader("📊 Content Performance Analytics")
            
            # Sample analytics data
            analytics_data = pd.DataFrame({
                'Content': ['Algebra Basics', 'Physics Motion', 'Chemistry Bonds', 'Literature Analysis'],
                'Views': [1247, 892, 654, 445],
                'Completion Rate': [85, 78, 92, 67],
                'Rating': [4.8, 4.6, 4.9, 4.3]
            })
            
            st.dataframe(analytics_data, use_container_width=True)
            
            # Performance chart
            fig = px.bar(analytics_data, x='Content', y='Views', color='Rating',
                         title='Content Performance Overview')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("🤝 Expert Collaboration")
            
            st.write("**Active Collaborations:**")
            
            collaborations = [
                {"Project": "Advanced Calculus Series", "Collaborators": ["Dr. Smith", "Prof. Johnson"], "Status": "In Progress"},
                {"Project": "Interactive Chemistry Lab", "Collaborators": ["Dr. Lee", "Ms. Brown"], "Status": "Review"},
                {"Project": "Literature Analysis Framework", "Collaborators": ["Prof. Wilson"], "Status": "Completed"}
            ]
            
            for collab in collaborations:
                with st.expander(f"📋 {collab['Project']} - {collab['Status']}"):
                    st.write(f"**Collaborators:** {', '.join(collab['Collaborators'])}")
                    st.write(f"**Status:** {collab['Status']}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("View Project", key=f"view_{collab['Project']}"):
                            st.info("Opening project details...")
                    with col_b:
                        if st.button("Join Meeting", key=f"meet_{collab['Project']}"):
                            st.success("Joining collaboration meeting...")
    
    except Exception as e:
        logger.error(f"Error in expert dashboard: {e}")
        st.error("An error occurred while loading the expert dashboard.")

if __name__ == "__main__":
    main()
