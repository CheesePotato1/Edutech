import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Any
import time

# Page configuration
st.set_page_config(
    page_title="EduTech AI Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'learning_progress' not in st.session_state:
    st.session_state.learning_progress = {}
if 'assessment_results' not in st.session_state:
    st.session_state.assessment_results = {}
if 'all_users' not in st.session_state:
    st.session_state.all_users = {}

# Sample data for demonstration (demo users)
DEMO_USERS = {
    "demo_student": {
        "name": "Demo Student",
        "role": "Student",
        "email": "student@demo.com",
        "age": 16,
        "grade": "10th Grade",
        "learning_style": ["Visual"],
        "subjects_interest": ["Mathematics", "Physics"],
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

# Initialize demo users in session state
if not st.session_state.all_users:
    st.session_state.all_users = DEMO_USERS.copy()

SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Literature", "History", "Biology", "Geography", "Economics"]
LEARNING_STYLES = ["Visual", "Auditory", "Kinesthetic", "Reading/Writing"]
LLM_MODELS = {
    "GPT-4": "Primary tutoring, creative writing, complex problem-solving",
    "Claude": "Content summarization, reading comprehension, academic discussions",
    "Perplexity": "Research assistance, fact-checking, current events",
    "Gemini": "Multimodal analysis, mathematical problem solving",
    "Grok": "Conversational practice, engagement-focused interactions"
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
    .progress-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
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
</style>
""", unsafe_allow_html=True)

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
        # Toggle between Sign In and Register
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
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
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
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
                
                if demo_mode:
                    # Show demo user options
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
                        st.success(f"Entering demo as {selected_demo}...")
                        time.sleep(1)
                        st.rerun()
        
        with tab2:
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
                
                # Additional fields based on role selection
                age, grade, learning_style, subjects_interest = None, None, [], []
                specialization, experience = [], ""
                num_children, children_ages = 1, ""
                subjects_taught, grade_levels = [], []
                expertise_areas, credentials = [], ""
                
                if "Student" in str(role):
                    st.markdown("### Tell us about yourself")
                    age = st.number_input("Age", min_value=5, max_value=25, value=16)
                    grade = st.selectbox("Grade Level", 
                                       ["", "K", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th", "University"])
                    learning_style = st.multiselect("How do you prefer to learn? (Select all that apply)", LEARNING_STYLES)
                    subjects_interest = st.multiselect("What subjects interest you?", SUBJECTS)
                    
                elif "Tutor" in str(role):
                    st.markdown("### Tutor Information")
                    specialization = st.multiselect("Your specialization subjects", SUBJECTS)
                    experience = st.selectbox("Years of tutoring experience", ["Less than 1 year", "1-3 years", "3-5 years", "5+ years"])
                    
                elif "Parent" in str(role):
                    st.markdown("### Parent Information")
                    num_children = st.number_input("Number of children", min_value=1, max_value=10, value=1)
                    children_ages = st.text_input("Children's ages (separated by commas)", placeholder="e.g., 8, 12, 16")
                    
                elif "Teacher" in str(role):
                    st.markdown("### Teacher Information")
                    subjects_taught = st.multiselect("Subjects you teach", SUBJECTS)
                    grade_levels = st.multiselect("Grade levels you teach", 
                                                ["Elementary", "Middle School", "High School", "University"])
                    
                elif "Expert" in str(role):
                    st.markdown("### Expert Information")
                    expertise_areas = st.multiselect("Your areas of expertise", SUBJECTS)
                    credentials = st.text_area("Brief description of your credentials", 
                                             placeholder="PhD in Mathematics, 10 years industry experience...")
                
                # Terms and conditions
                st.markdown("---")
                agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
                
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if submitted:
                    # Validation
                    if not name or not email or not password or not confirm_password or not role or not agree_terms:
                        st.error("Please fill in all required fields and agree to the terms.")
                    elif not role.strip():
                        st.error("Please select your role.")
                    elif password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        # Check if email already exists
                        email_exists = any(user_data.get("email") == email for user_data in st.session_state.all_users.values())
                        
                        if email_exists:
                            st.error("An account with this email already exists. Please sign in instead.")
                        else:
                            # Extract role from selection
                            user_role = role.split(" - ")[0]
                            
                            # Create new user data
                            new_user_id = f"user_{len(st.session_state.all_users) + 1}"
                            user_data = {
                                "name": name,
                                "role": user_role,
                                "email": email,
                                "password": password  # In a real app, this would be hashed
                            }
                            
                            # Add role-specific data
                            if user_role == "Student":
                                user_data.update({
                                    "age": age,
                                    "grade": grade,
                                    "learning_style": learning_style,
                                    "subjects_interest": subjects_interest,
                                    "progress": {subject: random.randint(40, 90) for subject in subjects_interest[:5]} if subjects_interest else {}
                                })
                            elif user_role == "Tutor":
                                user_data.update({
                                    "specialization": specialization,
                                    "experience": experience,
                                    "students": []
                                })
                            elif user_role == "Parent":
                                user_data.update({
                                    "num_children": num_children,
                                    "children_ages": children_ages,
                                    "children": [f"Child {i+1}" for i in range(num_children)]
                                })
                            elif user_role == "Teacher":
                                user_data.update({
                                    "subjects": subjects_taught,
                                    "grade_levels": grade_levels,
                                    "class_size": random.randint(20, 35)
                                })
                            elif user_role == "Expert":
                                user_data.update({
                                    "expertise_areas": expertise_areas,
                                    "credentials": credentials
                                })
                            
                            # Store user data
                            st.session_state.all_users[new_user_id] = user_data
                            st.session_state.current_user = new_user_id
                            
                            st.success(f"Welcome to EduTech AI Learning Platform, {name}! 🎉")
                            time.sleep(2)
                            st.rerun()

def intake_assessment():
    """Adaptive intake assessment"""
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
                st.success("Assessment completed! Your personalized learning plan is being generated...")
                time.sleep(2)
                st.rerun()

def student_dashboard():
    """Student dashboard with personalized learning"""
    user_data = st.session_state.all_users[st.session_state.current_user]
    
    st.title(f"Welcome back, {user_data['name']}! 🎓")
    
    # Progress Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Overall Progress</h3>
            <h2>72%</h2>
            <p>Keep going!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🔥 Study Streak</h3>
            <h2>15 days</h2>
            <p>Amazing!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⏱️ Study Time Today</h3>
            <h2>2.5 hrs</h2>
            <p>On track</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🏆 Achievements</h3>
            <h2>12</h2>
            <p>Badges earned</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Subject Progress
    st.subheader("📈 Subject Progress")
    
    # Use user's actual progress or create sample data
    if user_data.get("progress"):
        progress_data = pd.DataFrame([
            {"Subject": subject, "Progress": progress}
            for subject, progress in user_data["progress"].items()
        ])
    else:
        # Default progress for users without specific progress data
        default_subjects = user_data.get("subjects_interest", ["Mathematics", "Physics", "Chemistry", "Literature"])
        progress_data = pd.DataFrame([
            {"Subject": subject, "Progress": random.randint(40, 90)}
            for subject in default_subjects[:4]
        ])
    
    if not progress_data.empty:
        fig = px.bar(progress_data, x="Subject", y="Progress", 
                     color="Progress", color_continuous_scale="viridis",
                     title="Your Learning Progress by Subject")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Learning Path
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Today's Learning Plan")
        
        # Generate learning tasks based on user's interests
        subjects = user_data.get("subjects_interest", ["Mathematics", "Physics", "Literature", "History"])
        learning_tasks = []
        
        for i, subject in enumerate(subjects[:4]):
            tasks = {
                "Mathematics": "Complete Algebra Chapter 5",
                "Physics": "Newton's Laws Practice", 
                "Chemistry": "Chemical Bonding Exercises",
                "Literature": "Essay Writing Practice",
                "History": "World War II Timeline",
                "Biology": "Cell Structure Study",
                "Geography": "Climate Zones Review",
                "Economics": "Supply and Demand Analysis"
            }
            
            task_name = tasks.get(subject, f"{subject} Practice Session")
            learning_tasks.append({
                "task": task_name,
                "time": f"{random.randint(25, 50)} min",
                "type": subject
            })
        
        for task in learning_tasks:
            with st.expander(f"📚 {task['task']} ({task['time']})"):
                st.write(f"**Subject:** {task['type']}")
                st.write("**Learning Mode:** Interactive with AI tutor")
                st.write("**Resources:** Video, Practice Problems, Mindmap")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"Start Learning", key=f"start_{task['task']}"):
                        st.success("Starting your personalized lesson...")
                with col_b:
                    if st.button(f"Get Help", key=f"help_{task['task']}"):
                        st.info("Connecting you with AI tutor...")
    
    with col2:
        st.subheader("🤖 AI Learning Assistant")
        
        # Chat Interface
        st.write("Ask me anything about your studies!")
        
        for message in st.session_state.chat_history[-5:]:  # Show last 5 messages
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
            
            # Generate AI response (simulated)
            ai_responses = [
                "Great question! Let me help you understand this concept step by step...",
                "I can see you're working on this topic. Here's a different approach that might help...",
                "That's a common challenge! Let's break it down using your preferred visual learning style...",
                "Excellent! You're making good progress. Here's what to focus on next..."
            ]
            
            ai_response = random.choice(ai_responses)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            st.rerun()
    
    # Recommendations
    st.subheader("💡 Personalized Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="role-card">
            <h4>📖 Recommended Resources</h4>
            <ul>
                <li>Khan Academy: Quadratic Equations</li>
                <li>Crash Course Physics: Motion</li>
                <li>Interactive Chemistry Lab Sim</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="role-card">
            <h4>🎯 Focus Areas</h4>
            <ul>
                <li>Literature: Reading comprehension</li>
                <li>History: Timeline memorization</li>
                <li>Chemistry: Balancing equations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="role-card">
            <h4>🏆 Next Milestones</h4>
            <ul>
                <li>Complete 5 math problems</li>
                <li>Read 2 history chapters</li>
                <li>Practice essay writing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def tutor_dashboard():
    """Tutor dashboard for managing students and sessions"""
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

def parent_dashboard():
    """Parent dashboard for monitoring child's progress"""
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

def teacher_dashboard():
    """Teacher dashboard for classroom management"""
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

def expert_dashboard():
    """Expert dashboard for content creation and analysis"""
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

def llm_integration_demo():
    """Demonstration of LLM integration for different learning scenarios"""
    st.title("🤖 AI Learning Models Integration")
    
    st.write("Experience how different AI models enhance your learning:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available AI Models")
        
        for model, description in LLM_MODELS.items():
            st.markdown(f"""
            <div class="role-card">
                <h4>{model}</h4>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Try AI-Powered Learning")
        
        learning_scenario = st.selectbox("Choose Learning Scenario:", [
            "Math Problem Solving",
            "Essay Writing Help",
            "Science Concept Explanation",
            "Historical Research",
            "Language Practice"
        ])
        
        user_question = st.text_area("Ask your question:")
        
        if st.button("Get AI Help"):
            # Simulate different AI responses based on scenario
            responses = {
                "Math Problem Solving": "Let me break down this problem step by step using visual diagrams...",
                "Essay Writing Help": "I'll help you structure your essay with a clear thesis and supporting arguments...",
                "Science Concept Explanation": "Let me explain this concept using real-world examples and interactive visualizations...",
                "Historical Research": "I'll help you find reliable sources and verify historical facts...",
                "Language Practice": "Let's practice this conversation in a fun, engaging way..."
            }
            
            recommended_model = {
                "Math Problem Solving": "Gemini",
                "Essay Writing Help": "GPT-4",
                "Science Concept Explanation": "Claude",
                "Historical Research": "Perplexity",
                "Language Practice": "Grok"
            }
            
            st.success(f"**Recommended AI Model:** {recommended_model[learning_scenario]}")
            st.write(f"**AI Response:** {responses[learning_scenario]}")

# Main application logic
def main():
    """Main application function"""
    
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
                page = st.selectbox("Navigate", ["Assessment", "Dashboard", "AI Models Demo"])
            else:
                page = st.selectbox("Navigate", ["Dashboard", "Assessment", "AI Models Demo"])
        else:
            page = st.selectbox("Navigate", ["Dashboard", "AI Models Demo"])
        
        # Quick stats
        st.markdown("---")
        st.subheader("Quick Stats")
        
        if user_data['role'] == 'Student':
            st.metric("Overall Progress", "72%", "↗️ +5%")
            st.metric("Study Streak", "15 days", "🔥")
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
        elif page == "AI Models Demo":
            llm_integration_demo()
    elif user_data['role'] == 'Tutor':
        if page == "Dashboard":
            tutor_dashboard()
        elif page == "AI Models Demo":
            llm_integration_demo()
    elif user_data['role'] == 'Parent':
        if page == "Dashboard":
            parent_dashboard()
        elif page == "AI Models Demo":
            llm_integration_demo()
    elif user_data['role'] == 'Teacher':
        if page == "Dashboard":
            teacher_dashboard()
        elif page == "AI Models Demo":
            llm_integration_demo()
    elif user_data['role'] == 'Expert':
        if page == "Dashboard":
            expert_dashboard()
        elif page == "AI Models Demo":
            llm_integration_demo()

if __name__ == "__main__":
    main()
