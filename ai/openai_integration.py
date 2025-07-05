"""
OpenAI integration for EduTech AI Learning Platform
Copy this code into ai/openai_integration.py
"""

import streamlit as st
import openai
import json
import random
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OpenAITutor:
    """AI tutoring system using OpenAI GPT models"""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.client = None
        self.mock_mode = True  # Set to False when you have API key
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            try:
                openai.api_key = self.api_key
                self.client = openai
                self.mock_mode = False
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.mock_mode = True
        
        # Conversation templates for different scenarios
        self.conversation_templates = {
            'math_tutor': {
                'system_prompt': """You are an expert mathematics tutor. Your role is to:
                1. Help students understand mathematical concepts step-by-step
                2. Provide hints without giving away the complete answer
                3. Encourage students and build their confidence
                4. Adapt explanations to the student's level
                5. Use examples and analogies to make concepts clear
                
                Always be patient, encouraging, and focus on helping the student learn.""",
                'examples': [
                    "Let's break this problem down step by step...",
                    "Great question! This concept is easier than it seems...",
                    "I can see you're working hard on this. Let me give you a hint..."
                ]
            },
            'science_tutor': {
                'system_prompt': """You are a science tutor specializing in Physics, Chemistry, and Biology. Your approach:
                1. Connect scientific concepts to real-world examples
                2. Use analogies and visual descriptions
                3. Encourage scientific thinking and curiosity
                4. Break down complex processes into simple steps
                5. Help students see the beauty and logic in science
                
                Make science exciting and accessible.""",
                'examples': [
                    "Think of this like...",
                    "In the real world, you can see this when...",
                    "Scientists discovered this by..."
                ]
            },
            'writing_coach': {
                'system_prompt': """You are a writing coach and literature tutor. You help students:
                1. Improve their writing skills and style
                2. Understand literary concepts and analysis
                3. Develop critical thinking about texts
                4. Express their ideas clearly and persuasively
                5. Build confidence in their writing abilities
                
                Be supportive and constructive in your feedback.""",
                'examples': [
                    "Your ideas are strong. Let's work on how to express them clearly...",
                    "This author uses an interesting technique here...",
                    "What do you think the author is trying to convey?"
                ]
            },
            'study_coach': {
                'system_prompt': """You are a study skills coach who helps students:
                1. Develop effective study strategies
                2. Manage their time and set goals
                3. Stay motivated and overcome challenges
                4. Build good learning habits
                5. Reduce stress and anxiety about learning
                
                Be encouraging and practical in your advice.""",
                'examples': [
                    "It sounds like you're feeling overwhelmed. Let's break this down...",
                    "You're making great progress! Here's how to keep building on it...",
                    "That's a common challenge. Here's a strategy that works well..."
                ]
            }
        }
    
    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from Streamlit secrets or environment"""
        try:
            # Try to get from Streamlit secrets first
            if hasattr(st, 'secrets') and 'openai' in st.secrets:
                return st.secrets.openai.api_key
            
            # Could also try environment variables
            import os
            return os.getenv('OPENAI_API_KEY')
            
        except Exception as e:
            logger.warning(f"Could not retrieve OpenAI API key: {e}")
            return None
    
    def chat_with_tutor(self, user_id: str, message: str, subject: str = "general", 
                       conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Main chat interface with AI tutor"""
        try:
            # Get user stats for personalization
            if user_id in st.session_state.user_stats:
                user_stats = st.session_state.user_stats[user_id]
            else:
                user_stats = {}
            
            # Get appropriate tutor type
            tutor_type = self._get_tutor_type(subject)
            
            if self.mock_mode:
                response = self._generate_mock_response(message, subject, user_stats)
            else:
                response = self._generate_ai_response(message, subject, tutor_type, user_stats, conversation_history)
            
            # Log the interaction
            self._log_conversation(user_id, message, response, subject)
            
            return {
                'response': response,
                'tutor_type': tutor_type,
                'timestamp': datetime.now(),
                'subject': subject
            }
            
        except Exception as e:
            logger.error(f"Error in chat_with_tutor: {e}")
            return {
                'response': "I'm having trouble right now. Please try again in a moment!",
                'error': True,
                'timestamp': datetime.now()
            }
    
    def _get_tutor_type(self, subject: str) -> str:
        """Determine appropriate tutor type based on subject"""
        subject_mapping = {
            'mathematics': 'math_tutor',
            'math': 'math_tutor',
            'physics': 'science_tutor',
            'chemistry': 'science_tutor',
            'biology': 'science_tutor',
            'science': 'science_tutor',
            'literature': 'writing_coach',
            'english': 'writing_coach',
            'writing': 'writing_coach',
            'history': 'writing_coach',
            'study': 'study_coach',
            'motivation': 'study_coach'
        }
        
        return subject_mapping.get(subject.lower(), 'study_coach')
    
    def _generate_ai_response(self, message: str, subject: str, tutor_type: str, 
                            user_stats: Dict[str, Any], conversation_history: List[Dict] = None) -> str:
        """Generate response using OpenAI API"""
        try:
            # Build conversation context
            messages = self._build_conversation_context(message, tutor_type, user_stats, conversation_history)
            
            # Make API call
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_mock_response(message, subject, user_stats)
    
    def _build_conversation_context(self, message: str, tutor_type: str, 
                                  user_stats: Dict[str, Any], conversation_history: List[Dict] = None) -> List[Dict]:
        """Build conversation context for OpenAI"""
        messages = []
        
        # System prompt
        template = self.conversation_templates[tutor_type]
        system_prompt = template['system_prompt']
        
        # Add user context
        user_context = self._build_user_context(user_stats)
        system_prompt += f"\n\nStudent Context: {user_context}"
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (last 5 exchanges)
        if conversation_history:
            for exchange in conversation_history[-5:]:
                messages.append({"role": "user", "content": exchange.get('user_message', '')})
                messages.append({"role": "assistant", "content": exchange.get('ai_response', '')})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def _build_user_context(self, user_stats: Dict[str, Any]) -> str:
        """Build context about the user for personalization"""
        context_parts = []
        
        # Learning level
        progress = user_stats.get('overall_progress', 0)
        if progress < 30:
            context_parts.append("beginner level student")
        elif progress < 70:
            context_parts.append("intermediate level student")
        else:
            context_parts.append("advanced level student")
        
        # Performance info
        accuracy = user_stats.get('accuracy_rate', 0)
        if accuracy >= 80:
            context_parts.append("high accuracy in problem solving")
        elif accuracy >= 60:
            context_parts.append("good problem-solving skills")
        else:
            context_parts.append("working to improve accuracy")
        
        # Study habits
        streak = user_stats.get('study_streak', 0)
        if streak >= 7:
            context_parts.append("consistent daily study habits")
        elif streak >= 3:
            context_parts.append("developing study routine")
        else:
            context_parts.append("building study consistency")
        
        # Weak areas
        weak_areas = user_stats.get('weak_areas', [])
        if weak_areas:
            context_parts.append(f"needs support in {', '.join(weak_areas[:2])}")
        
        return "This is a " + ", ".join(context_parts) + "."
    
    def _generate_mock_response(self, message: str, subject: str, user_stats: Dict[str, Any]) -> str:
        """Generate intelligent mock responses when API is not available"""
        
        # Analyze user's message for keywords
        message_lower = message.lower()
        
        # Math-related responses
        if any(word in message_lower for word in ['math', 'equation', 'solve', 'calculate', 'algebra']):
            responses = [
                "Great math question! Let's break this down step by step. First, identify what we know and what we need to find...",
                "I love seeing you tackle math problems! The key here is to work systematically. What's the first step you think we should take?",
                "Math can be tricky, but you're on the right track! Let me guide you through this concept with a helpful approach...",
                "That's an excellent question about mathematics! Here's how I like to think about this type of problem..."
            ]
        
        # Science-related responses
        elif any(word in message_lower for word in ['physics', 'chemistry', 'biology', 'science', 'experiment']):
            responses = [
                "Science is fascinating! This concept is actually all around us in daily life. Let me explain it in a way that makes sense...",
                "Great scientific thinking! The key to understanding this is to think about what's happening at the fundamental level...",
                "I love your curiosity about science! This is exactly the kind of question that leads to real understanding...",
                "Science can seem complex, but it's really about observing patterns. Let's explore this concept together..."
            ]
        
        # Writing/Literature responses
        elif any(word in message_lower for word in ['write', 'essay', 'literature', 'story', 'analyze']):
            responses = [
                "Writing is a powerful way to express your ideas! Let's work on organizing your thoughts clearly and persuasively...",
                "That's a thoughtful question about literature! The author's choice here reveals something important about the themes...",
                "I can help you develop this idea further. What's the main point you want your reader to understand?",
                "Great analytical thinking! When we examine literature, we're looking for patterns and deeper meanings..."
            ]
        
        # Study skills and motivation
        elif any(word in message_lower for word in ['study', 'motivation', 'difficult', 'help', 'confused']):
            responses = [
                "I understand that learning can be challenging sometimes. The fact that you're asking for help shows you're committed to improving!",
                "Every great learner has moments of confusion - that's completely normal! Let's break this down into manageable pieces...",
                "You're doing better than you think! Sometimes we need to adjust our approach to find what works best for you...",
                "I'm here to support your learning journey. What specific part would you like to focus on first?"
            ]
        
        # General encouraging responses
        else:
            responses = [
                "That's a really thoughtful question! I can tell you're thinking deeply about this topic...",
                "I'm impressed by your curiosity and willingness to learn. Let me help you explore this further...",
                "Great question! This is exactly the kind of thinking that leads to real understanding and growth...",
                "I love your enthusiasm for learning! Let's dive into this topic and discover something amazing together..."
            ]
        
        # Personalize based on user stats
        response = random.choice(responses)
        
        # Add personalized encouragement based on performance
        accuracy = user_stats.get('accuracy_rate', 0)
        streak = user_stats.get('study_streak', 0)
        
        if accuracy >= 80:
            response += " Your strong problem-solving skills will definitely help you here!"
        elif streak >= 7:
            response += " I can see from your consistent study habits that you're really dedicated to learning!"
        
        return response
    
    def generate_problem_explanation(self, problem: Dict[str, Any], user_answer: str, 
                                   correct_answer: str, user_stats: Dict[str, Any]) -> str:
        """Generate detailed explanation for a problem"""
        try:
            if self.mock_mode:
                return self._generate_mock_explanation(problem, user_answer, correct_answer, user_stats)
            else:
                return self._generate_ai_explanation(problem, user_answer, correct_answer, user_stats)
                
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"The correct answer is {correct_answer}. Let me know if you'd like me to explain the concept further!"
    
    def _generate_ai_explanation(self, problem: Dict[str, Any], user_answer: str, 
                               correct_answer: str, user_stats: Dict[str, Any]) -> str:
        """Generate AI-powered explanation"""
        try:
            prompt = f"""
            A student answered a {problem.get('type', 'math')} problem incorrectly. Please provide a helpful explanation.
            
            Problem: {problem.get('question', '')}
            Student's Answer: {user_answer}
            Correct Answer: {correct_answer}
            
            Please:
            1. Explain why the correct answer is right
            2. Help the student understand their mistake (if applicable)
            3. Provide a step-by-step solution
            4. Be encouraging and supportive
            
            Keep the explanation clear and educational.
            """
            
            messages = [
                {"role": "system", "content": "You are a helpful tutor explaining problems to students."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=400,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in AI explanation: {e}")
            return self._generate_mock_explanation(problem, user_answer, correct_answer, user_stats)
    
    def _generate_mock_explanation(self, problem: Dict[str, Any], user_answer: str, 
                                 correct_answer: str, user_stats: Dict[str, Any]) -> str:
        """Generate mock explanation when AI is not available"""
        
        problem_type = problem.get('type', 'general')
        
        explanations = {
            'arithmetic': f"Let's work through this step by step. The correct answer is {correct_answer}. When solving arithmetic problems, it's important to follow the order of operations (PEMDAS). Would you like me to break down each step?",
            
            'algebra': f"Great attempt! The correct answer is {correct_answer}. In algebra problems like this, we need to isolate the variable by performing the same operation on both sides of the equation. The key is to work systematically and check our work.",
            
            'geometry': f"Good thinking! The answer is {correct_answer}. For geometry problems, it helps to visualize the shape and identify which formula to use. Remember to check that your units are consistent throughout your calculation.",
            
            'percentage': f"Nice try! The correct answer is {correct_answer}. For percentage problems, remember that 'of' usually means multiply, and we convert percentages to decimals by dividing by 100. Practice with these conversions will make it automatic!",
            
            'physics': f"Good effort! The correct answer is {correct_answer}. Physics problems often require identifying the right equation and being careful with units. Always start by listing what you know and what you need to find.",
            
            'chemistry': f"Well done for trying! The answer is {correct_answer}. Chemistry problems often involve balanced equations and unit conversions. Double-check that your equation is balanced and your units cancel out properly.",
            
            'concepts': f"The correct answer is {correct_answer}. Understanding concepts is often about connecting new information to what you already know. Think about how this concept applies in real-world situations!"
        }
        
        base_explanation = explanations.get(problem_type, f"The correct answer is {correct_answer}. Let's work through this concept together!")
        
        # Add encouraging personalization
        if user_stats.get('accuracy_rate', 0) >= 70:
            base_explanation += " You're doing well overall - keep up the great work!"
        else:
            base_explanation += " Remember, every mistake is a learning opportunity. You're building important skills!"
        
        return base_explanation
    
    def generate_hint(self, problem: Dict[str, Any], user_stats: Dict[str, Any]) -> str:
        """Generate contextual hints for problems"""
        try:
            if self.mock_mode:
                return self._generate_mock_hint(problem, user_stats)
            else:
                return self._generate_ai_hint(problem, user_stats)
                
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return "Think about what you know and what you need to find. Break the problem into smaller steps!"
    
    def _generate_ai_hint(self, problem: Dict[str, Any], user_stats: Dict[str, Any]) -> str:
        """Generate AI-powered hint"""
        try:
            prompt = f"""
            Provide a helpful hint for this problem without giving away the answer:
            
            Problem: {problem.get('question', '')}
            Type: {problem.get('type', '')}
            
            Give a hint that guides the student toward the solution without solving it completely.
            Be encouraging and educational.
            """
            
            messages = [
                {"role": "system", "content": "You are a tutor providing helpful hints to guide students."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in AI hint: {e}")
            return self._generate_mock_hint(problem, user_stats)
    
    def _generate_mock_hint(self, problem: Dict[str, Any], user_stats: Dict[str, Any]) -> str:
        """Generate contextual hints when AI is not available"""
        
        problem_type = problem.get('type', 'general')
        
        hints = {
            'arithmetic': "Start by identifying the operation you need to perform. Remember the order of operations: Parentheses, Exponents, Multiplication/Division, Addition/Subtraction.",
            
            'algebra': "Think about what operation will help you isolate the variable. What can you do to both sides of the equation to get closer to your answer?",
            
            'geometry': "What formula applies to this shape? Make sure you're using the right measurements and that your units are consistent.",
            
            'percentage': "Remember that 'of' usually means multiply, and percentages need to be converted to decimals first. What's 25% as a decimal?",
            
            'physics': "Start by writing down what you know and what you need to find. Which physics formula connects these quantities?",
            
            'chemistry': "Check if your chemical equation is balanced first. Then think about the relationships between moles, mass, and molecular weight.",
            
            'concepts': "Think about the key principles involved. How does this concept apply to situations you already understand?"
        }
        
        base_hint = hints.get(problem_type, "Break the problem down into smaller steps. What do you know, and what do you need to find?")
        
        # Adapt hint based on user level
        if user_stats.get('overall_progress', 0) < 30:
            base_hint = "Let's start simple: " + base_hint
        elif user_stats.get('accuracy_rate', 0) >= 80:
            base_hint += " You've got strong skills - trust your instincts!"
        
        return base_hint
    
    def generate_study_plan(self, user_id: str, subject: str, goal: str) -> Dict[str, Any]:
        """Generate personalized study plan"""
        try:
            user_stats = st.session_state.user_stats.get(user_id, {})
            
            if self.mock_mode:
                return self._generate_mock_study_plan(user_stats, subject, goal)
            else:
                return self._generate_ai_study_plan(user_stats, subject, goal)
                
        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            return {
                'error': True,
                'message': "Unable to generate study plan right now. Please try again later."
            }
    
    def _generate_mock_study_plan(self, user_stats: Dict[str, Any], subject: str, goal: str) -> Dict[str, Any]:
        """Generate intelligent mock study plan"""
        
        # Analyze user's current level
        progress = user_stats.get('overall_progress', 0)
        accuracy = user_stats.get('accuracy_rate', 0)
        
        if progress < 30:
            level = "Beginner"
            focus = "Building strong foundations"
        elif progress < 70:
            level = "Intermediate"
            focus = "Developing problem-solving skills"
        else:
            level = "Advanced"
            focus = "Mastering complex concepts"
        
        # Generate plan based on subject and level
        study_plan = {
            'level': level,
            'focus': focus,
            'duration': '2-4 weeks',
            'daily_time': '30-45 minutes',
            'weekly_schedule': self._generate_weekly_schedule(subject, level),
            'milestones': self._generate_milestones(subject, level),
            'resources': self._generate_resources(subject, level),
            'tips': self._generate_study_tips(user_stats)
        }
        
        return study_plan
    
    def _generate_weekly_schedule(self, subject: str, level: str) -> List[Dict[str, str]]:
        """Generate weekly study schedule"""
        base_schedule = [
            {'day': 'Monday', 'topic': 'Review fundamentals', 'activity': 'Practice problems'},
            {'day': 'Tuesday', 'topic': 'New concept introduction', 'activity': 'Interactive learning'},
            {'day': 'Wednesday', 'topic': 'Application practice', 'activity': 'Problem solving'},
            {'day': 'Thursday', 'topic': 'Skill reinforcement', 'activity': 'Adaptive practice'},
            {'day': 'Friday', 'topic': 'Weekly review', 'activity': 'Quiz and assessment'},
            {'day': 'Saturday', 'topic': 'Challenge problems', 'activity': 'Advanced practice'},
            {'day': 'Sunday', 'topic': 'Rest and reflection', 'activity': 'Light review'}
        ]
        
        # Customize based on subject and level
        if subject.lower() == 'mathematics':
            for day in base_schedule:
                if day['day'] == 'Tuesday':
                    day['topic'] = 'New mathematical concept'
                elif day['day'] == 'Wednesday':
                    day['topic'] = 'Problem-solving strategies'
        
        return base_schedule
    
    def _generate_milestones(self, subject: str, level: str) -> List[str]:
        """Generate learning milestones"""
        if level == "Beginner":
            return [
                "Complete foundational concepts review",
                "Achieve 70% accuracy on basic problems",
                "Solve 50 practice problems",
                "Pass first assessment with 75%"
            ]
        elif level == "Intermediate":
            return [
                "Master intermediate concepts",
                "Achieve 80% accuracy consistently",
                "Complete 100 varied problems",
                "Apply concepts to real-world scenarios"
            ]
        else:
            return [
                "Tackle advanced problem sets",
                "Achieve 90% accuracy on complex problems",
                "Demonstrate teaching ability to others",
                "Complete capstone project"
            ]
    
    def _generate_resources(self, subject: str, level: str) -> List[str]:
        """Generate recommended resources"""
        general_resources = [
            "Interactive practice problems",
            "Step-by-step video explanations",
            "AI tutor chat sessions",
            "Progress tracking dashboard"
        ]
        
        subject_specific = {
            'mathematics': [
                "Khan Academy Math courses",
                "Graphing calculator practice",
                "Mathematical reasoning exercises"
            ],
            'physics': [
                "Virtual lab simulations",
                "Physics concept animations",
                "Real-world application examples"
            ],
            'chemistry': [
                "Molecular modeling tools",
                "Chemical reaction simulators",
                "Periodic table interactive"
            ]
        }
        
        resources = general_resources + subject_specific.get(subject.lower(), [])
        return resources
    
    def _generate_study_tips(self, user_stats: Dict[str, Any]) -> List[str]:
        """Generate personalized study tips"""
        tips = []
        
        accuracy = user_stats.get('accuracy_rate', 0)
        streak = user_stats.get('study_streak', 0)
        
        if accuracy < 60:
            tips.append("Focus on understanding concepts before attempting difficult problems")
            tips.append("Review your mistakes carefully to identify patterns")
        
        if streak < 3:
            tips.append("Try to study a little bit every day for consistency")
            tips.append("Set small, achievable daily goals")
        
        tips.extend([
            "Take breaks every 25-30 minutes to maintain focus",
            "Explain concepts out loud to test your understanding",
            "Connect new concepts to things you already know",
            "Celebrate small victories to stay motivated"
        ])
        
        return tips
    
    def _log_conversation(self, user_id: str, user_message: str, ai_response: str, subject: str):
        """Log conversation for analytics and improvement"""
        try:
            conversation_log = {
                'user_id': user_id,
                'timestamp': datetime.now(),
                'user_message': user_message,
                'ai_response': ai_response,
                'subject': subject,
                'session_id': st.session_state.get('session_id', 'unknown')
            }
            
            # Add to session state for immediate use
            if 'ai_conversation_log' not in st.session_state:
                st.session_state.ai_conversation_log = []
            
            st.session_state.ai_conversation_log.append(conversation_log)
            
            # Keep only last 50 conversations
            if len(st.session_state.ai_conversation_log) > 50:
                st.session_state.ai_conversation_log = st.session_state.ai_conversation_log[-50:]
            
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history for a user"""
        try:
            all_conversations = st.session_state.get('ai_conversation_log', [])
            user_conversations = [
                conv for conv in all_conversations 
                if conv.get('user_id') == user_id
            ]
            
            return user_conversations[-limit:] if limit else user_conversations
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def render_ai_chat_interface(self, user_id: str):
        """Render the AI chat interface"""
        try:
            st.subheader("🤖 AI Learning Assistant")
            
            # Subject selection for context
            col1, col2 = st.columns([2, 1])
            
            with col1:
                subject = st.selectbox(
                    "What subject can I help you with?",
                    ["General", "Mathematics", "Physics", "Chemistry", "Literature", "Study Skills"],
                    key="ai_subject_select"
                )
            
            with col2:
                if st.button("🔄 Clear Chat"):
                    if 'ai_chat_messages' in st.session_state:
                        st.session_state.ai_chat_messages = []
                    st.rerun()
            
            # Initialize chat messages
            if 'ai_chat_messages' not in st.session_state:
                st.session_state.ai_chat_messages = []
            
            # Display chat history
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.ai_chat_messages[-10:]:  # Show last 10 messages
                    if message['role'] == 'user':
                        st.markdown(f"""
                        <div style="background: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0; margin-left: 20%;">
                            <strong>You:</strong> {message['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0; margin-right: 20%;">
                            <strong>🤖 AI Tutor:</strong> {message['content']}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Chat input
            user_input = st.text_input(
                "Ask me anything about your studies...",
                placeholder="e.g., Can you help me understand quadratic equations?",
                key="ai_chat_input"
            )
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                send_button = st.button("Send Message", use_container_width=True)
            
            with col2:
                if st.button("Get Study Tips", use_container_width=True):
                    tips_response = self.generate_study_tips_response(user_id, subject)
                    st.session_state.ai_chat_messages.append({
                        'role': 'assistant',
                        'content': tips_response
                    })
                    st.rerun()
            
            with col3:
                if st.button("Ask for Help", use_container_width=True):
                    help_response = "I'm here to help you learn! You can ask me about:\n\n• Explaining difficult concepts\n• Solving practice problems\n• Study strategies and tips\n• Subject-specific questions\n• Motivation and learning techniques\n\nWhat would you like to explore together?"
                    st.session_state.ai_chat_messages.append({
                        'role': 'assistant',
                        'content': help_response
                    })
                    st.rerun()
            
            # Handle message sending
            if send_button and user_input:
                # Add user message
                st.session_state.ai_chat_messages.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Generate AI response
                with st.spinner("🤖 Thinking..."):
                    response_data = self.chat_with_tutor(
                        user_id, 
                        user_input, 
                        subject.lower(),
                        st.session_state.ai_chat_messages
                    )
                
                # Add AI response
                st.session_state.ai_chat_messages.append({
                    'role': 'assistant',
                    'content': response_data['response']
                })
                
                # Update user stats for AI interaction
                if user_id in st.session_state.user_stats:
                    from utils.enhanced_stats import EnhancedStatsManager
                    stats_manager = EnhancedStatsManager()
                    stats_manager.update_stats(user_id, 'chat_interaction', time_spent=0.1)
                
                st.rerun()
            
            # Quick action buttons
            if not st.session_state.ai_chat_messages:
                st.markdown("### 💡 Quick Start Options:")
                
                quick_options = [
                    ("📚 Explain a concept", "Can you explain a concept I'm struggling with?"),
                    ("🧮 Help with homework", "I need help with my homework problem"),
                    ("📈 Study strategies", "What are some effective study strategies?"),
                    ("🎯 Set learning goals", "Help me set realistic learning goals"),
                    ("💪 Stay motivated", "I'm feeling overwhelmed with my studies")
                ]
                
                cols = st.columns(len(quick_options))
                for i, (button_text, message) in enumerate(quick_options):
                    with cols[i]:
                        if st.button(button_text, key=f"quick_{i}"):
                            st.session_state.ai_chat_messages.append({
                                'role': 'user',
                                'content': message
                            })
                            
                            with st.spinner("🤖 Thinking..."):
                                response_data = self.chat_with_tutor(user_id, message, subject.lower())
                            
                            st.session_state.ai_chat_messages.append({
                                'role': 'assistant',
                                'content': response_data['response']
                            })
                            
                            st.rerun()
            
        except Exception as e:
            logger.error(f"Error rendering AI chat interface: {e}")
            st.error("Unable to load AI chat interface. Please refresh the page.")
    
    def generate_study_tips_response(self, user_id: str, subject: str) -> str:
        """Generate personalized study tips response"""
        try:
            user_stats = st.session_state.user_stats.get(user_id, {})
            accuracy = user_stats.get('accuracy_rate', 0)
            streak = user_stats.get('study_streak', 0)
            progress = user_stats.get('overall_progress', 0)
            
            tips = []
            
            # Personalized tips based on performance
            if accuracy >= 80:
                tips.append("🎯 Your accuracy is excellent! Try challenging yourself with more advanced problems to keep growing.")
            elif accuracy >= 60:
                tips.append("📈 You're making good progress! Focus on understanding why you get problems wrong to boost your accuracy.")
            else:
                tips.append("📚 Take time to review fundamental concepts before attempting new problems. Quality over quantity!")
            
            if streak >= 7:
                tips.append("🔥 Amazing study streak! Your consistency is paying off. Keep up the excellent habit!")
            elif streak >= 3:
                tips.append("💪 Great job maintaining your study routine! Try to study a little bit every day to build momentum.")
            else:
                tips.append("📅 Consistency is key to learning. Even 15 minutes of daily practice can make a huge difference!")
            
            # Subject-specific tips
            subject_tips = {
                'mathematics': "🧮 For math: Practice problems daily, show all your work, and don't skip steps. Math builds on itself!",
                'physics': "⚗️ For physics: Connect concepts to real-world examples. Understanding the 'why' makes formulas easier to remember.",
                'chemistry': "🔬 For chemistry: Use visual aids like molecular models. Chemistry is very visual and spatial!",
                'literature': "📖 For literature: Read actively by asking questions about characters, themes, and the author's purpose.",
                'general': "🎓 General tip: Teach concepts to someone else - it's one of the best ways to test your understanding!"
            }
            
            tips.append(subject_tips.get(subject.lower(), subject_tips['general']))
            
            # Additional universal tips
            tips.extend([
                "🧠 Use the Pomodoro Technique: 25 minutes of focused study, then a 5-minute break.",
                "✅ Set small, specific goals for each study session to stay motivated.",
                "🤝 Don't hesitate to ask for help when you're stuck - that's how learning happens!"
            ])
            
            response = "Here are some personalized study tips for you:\n\n" + "\n\n".join(tips)
            response += "\n\nRemember, everyone learns differently. Experiment with these strategies and stick with what works best for you! What specific area would you like more help with?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating study tips: {e}")
            return "Here are some great study tips: Stay consistent, practice regularly, and don't be afraid to ask for help!"
    
    def generate_problem_walkthrough(self, problem: Dict[str, Any], user_stats: Dict[str, Any]) -> str:
        """Generate step-by-step problem walkthrough"""
        try:
            if self.mock_mode:
                return self._generate_mock_walkthrough(problem, user_stats)
            else:
                return self._generate_ai_walkthrough(problem, user_stats)
                
        except Exception as e:
            logger.error(f"Error generating walkthrough: {e}")
            return "Let me walk you through this problem step by step..."
    
    def _generate_mock_walkthrough(self, problem: Dict[str, Any], user_stats: Dict[str, Any]) -> str:
        """Generate mock step-by-step walkthrough"""
        
        problem_type = problem.get('type', 'general')
        question = problem.get('question', '')
        answer = problem.get('answer', '')
        
        walkthroughs = {
            'arithmetic': f"""
Let's solve this step by step:

**Problem:** {question}

**Step 1:** Identify the operation needed
**Step 2:** Apply the order of operations (PEMDAS)
**Step 3:** Calculate carefully
**Step 4:** Check your answer

**Final Answer:** {answer}

The key is to work systematically and double-check each step!
            """,
            
            'algebra': f"""
Let's work through this algebra problem:

**Problem:** {question}

**Step 1:** Identify what we're solving for
**Step 2:** Isolate the variable by doing the same operation to both sides
**Step 3:** Simplify step by step
**Step 4:** Check by substituting back

**Final Answer:** {answer}

Remember: Whatever you do to one side, do to the other!
            """,
            
            'geometry': f"""
Let's approach this geometry problem:

**Problem:** {question}

**Step 1:** Identify the shape and what we need to find
**Step 2:** Recall the appropriate formula
**Step 3:** Substitute the known values
**Step 4:** Calculate and check units

**Final Answer:** {answer}

Geometry is all about visualizing and using the right formulas!
            """
        }
        
        return walkthroughs.get(problem_type, f"""
Let me help you understand this problem:

**Problem:** {question}

**Approach:**
1. Break down what the problem is asking
2. Identify what information we have
3. Determine the method or formula to use
4. Work through the solution step by step

**Answer:** {answer}

The key is to approach problems systematically!
        """)
    
    def _generate_ai_walkthrough(self, problem: Dict[str, Any], user_stats: Dict[str, Any]) -> str:
        """Generate AI-powered walkthrough"""
        try:
            prompt = f"""
            Create a detailed, step-by-step walkthrough for this problem:
            
            Problem: {problem.get('question', '')}
            Type: {problem.get('type', '')}
            Correct Answer: {problem.get('answer', '')}
            
            Please provide:
            1. A clear breakdown of the problem
            2. Step-by-step solution process
            3. Explanation of key concepts
            4. Tips for similar problems
            
            Make it educational and encouraging for a student.
            """
            
            messages = [
                {"role": "system", "content": "You are a patient tutor creating step-by-step problem walkthroughs."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in AI walkthrough: {e}")
            return self._generate_mock_walkthrough(problem, user_stats)
    
    def assess_learning_needs(self, user_id: str) -> Dict[str, Any]:
        """Assess user's learning needs and provide recommendations"""
        try:
            user_stats = st.session_state.user_stats.get(user_id, {})
            
            assessment = {
                'overall_level': self._assess_overall_level(user_stats),
                'strengths': self._identify_strengths(user_stats),
                'areas_for_improvement': self._identify_weak_areas(user_stats),
                'recommended_focus': self._recommend_focus_areas(user_stats),
                'study_pattern_analysis': self._analyze_study_patterns(user_stats),
                'motivation_factors': self._assess_motivation_factors(user_stats),
                'next_steps': self._suggest_next_steps(user_stats)
            }
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing learning needs: {e}")
            return {'error': 'Unable to assess learning needs at this time'}
    
    def _assess_overall_level(self, user_stats: Dict[str, Any]) -> str:
        """Assess user's overall learning level"""
        progress = user_stats.get('overall_progress', 0)
        accuracy = user_stats.get('accuracy_rate', 0)
        
        if progress >= 70 and accuracy >= 80:
            return "Advanced - You're excelling and ready for challenging material"
        elif progress >= 40 and accuracy >= 65:
            return "Intermediate - You have solid fundamentals and are progressing well"
        else:
            return "Developing - You're building important foundational skills"
    
    def _identify_strengths(self, user_stats: Dict[str, Any]) -> List[str]:
        """Identify user's learning strengths"""
        strengths = []
        
        if user_stats.get('study_streak', 0) >= 7:
            strengths.append("Excellent study consistency and habit formation")
        
        if user_stats.get('accuracy_rate', 0) >= 80:
            strengths.append("High accuracy in problem solving")
        
        if user_stats.get('sessions_completed', 0) >= 20:
            strengths.append("Strong engagement and persistence")
        
        if user_stats.get('problems_solved', 0) >= 50:
            strengths.append("Good practice volume and dedication")
        
        favorite_subjects = user_stats.get('favorite_subjects', [])
        if favorite_subjects:
            strengths.append(f"Particular strength in {', '.join(favorite_subjects[:2])}")
        
        if not strengths:
            strengths = ["Shows commitment to learning", "Willing to seek help and improve"]
        
        return strengths
    
    def _identify_weak_areas(self, user_stats: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement"""
        weak_areas = []
        
        if user_stats.get('accuracy_rate', 0) < 60:
            weak_areas.append("Accuracy needs improvement - focus on understanding concepts")
        
        if user_stats.get('study_streak', 0) < 3:
            weak_areas.append("Study consistency - establish a regular routine")
        
        if user_stats.get('overall_progress', 0) < 30:
            weak_areas.append("Overall progress - may need to adjust study strategies")
        
        subject_weak_areas = user_stats.get('weak_areas', [])
        if subject_weak_areas:
            weak_areas.append(f"Subject challenges in {', '.join(subject_weak_areas[:2])}")
        
        return weak_areas
    
    def _recommend_focus_areas(self, user_stats: Dict[str, Any]) -> List[str]:
        """Recommend areas to focus on"""
        recommendations = []
        
        accuracy = user_stats.get('accuracy_rate', 0)
        streak = user_stats.get('study_streak', 0)
        progress = user_stats.get('overall_progress', 0)
        
        if accuracy < 70:
            recommendations.append("Focus on quality over quantity - understand each concept thoroughly")
        
        if streak < 5:
            recommendations.append("Build a consistent daily study habit, even if just 15-20 minutes")
        
        if progress < 50:
            recommendations.append("Strengthen fundamental concepts before moving to advanced topics")
        
        weak_subjects = user_stats.get('weak_areas', [])
        if weak_subjects:
            recommendations.append(f"Dedicate extra time to {weak_subjects[0]} to close knowledge gaps")
        
        if user_stats.get('sessions_completed', 0) < 10:
            recommendations.append("Increase practice session frequency for better skill development")
        
        return recommendations
    
    def _analyze_study_patterns(self, user_stats: Dict[str, Any]) -> Dict[str, str]:
        """Analyze user's study patterns"""
        patterns = {}
        
        sessions = user_stats.get('sessions_completed', 0)
        study_time = user_stats.get('total_study_time', 0)
        
        if sessions > 0 and study_time > 0:
            avg_session_time = study_time / sessions * 60  # Convert to minutes
            
            if avg_session_time > 60:
                patterns['session_length'] = "Long sessions - consider shorter, more frequent sessions"
            elif avg_session_time < 20:
                patterns['session_length'] = "Short sessions - try to extend to 25-30 minutes for deeper focus"
            else:
                patterns['session_length'] = "Good session length - maintain this pattern"
        
        streak = user_stats.get('study_streak', 0)
        if streak >= 14:
            patterns['consistency'] = "Excellent consistency - you've built a strong habit"
        elif streak >= 7:
            patterns['consistency'] = "Good consistency - keep building this habit"
        else:
            patterns['consistency'] = "Work on consistency - daily practice is key"
        
        return patterns
    
    def _assess_motivation_factors(self, user_stats: Dict[str, Any]) -> List[str]:
        """Assess factors affecting motivation"""
        factors = []
        
        achievements = user_stats.get('achievements', 0)
        if achievements >= 5:
            factors.append("Achievement motivation - you respond well to goals and milestones")
        
        accuracy = user_stats.get('accuracy_rate', 0)
        if accuracy >= 75:
            factors.append("Success-driven - your high accuracy likely boosts confidence")
        elif accuracy < 50:
            factors.append("May need confidence building - focus on smaller, achievable goals")
        
        streak = user_stats.get('study_streak', 0)
        if streak >= 7:
            factors.append("Habit-driven - you find motivation in consistency")
        
        return factors
    
    def _suggest_next_steps(self, user_stats: Dict[str, Any]) -> List[str]:
        """Suggest concrete next steps"""
        steps = []
        
        progress = user_stats.get('overall_progress', 0)
        accuracy = user_stats.get('accuracy_rate', 0)
        
        if progress < 25:
            steps.append("Complete foundational skill building in your weakest subject")
        elif progress < 50:
            steps.append("Work toward 80% accuracy in all practiced subjects")
        elif progress < 75:
            steps.append("Challenge yourself with advanced practice problems")
        else:
            steps.append("Consider helping others or exploring specialized topics")
        
        if accuracy < 70:
            steps.append("Spend extra time reviewing incorrect answers to understand mistakes")
        
        if user_stats.get('study_streak', 0) < 7:
            steps.append("Focus on building a 7-day study streak")
        
        steps.append("Set a specific learning goal for the next two weeks")
        
        return steps
    
    def render_ai_features_demo(self):
        """Render demo of AI features for users"""
        try:
            st.subheader("🤖 AI-Powered Learning Features")
            
            # Feature tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "💬 Smart Tutoring", 
                "📝 Problem Explanations", 
                "📊 Learning Assessment", 
                "📚 Study Planning"
            ])
            
            with tab1:
                st.markdown("""
                ### 🎓 Personalized AI Tutor
                
                Our AI tutor adapts to your learning style and provides:
                
                - **Contextual Help**: Understands your current level and adjusts explanations
                - **Multiple Subjects**: Expert knowledge in Math, Science, Literature, and more
                - **Learning Strategies**: Study tips and techniques tailored to your needs
                - **Motivation Support**: Encouragement and goal-setting assistance
                """)
                
                if st.button("Try Sample Conversation"):
                    st.markdown("""
                    **You:** "I'm struggling with quadratic equations"
                    
                    **AI Tutor:** "I understand quadratic equations can seem challenging at first! Since I can see you're doing well with linear equations, let's build on that foundation. 
                    
                    Think of a quadratic equation like y = x² + 2x + 1 as a curved line instead of a straight line. The key insight is that these equations can have two solutions because a curve can cross the x-axis at two points.
                    
                    Would you like me to walk through a specific example step by step?"
                    """)
            
            with tab2:
                st.markdown("""
                ### 🧮 Intelligent Problem Explanations
                
                When you get a problem wrong, our AI provides:
                
                - **Step-by-step breakdowns** of the solution process
                - **Common mistake identification** to help you learn
                - **Alternative solution methods** for different learning styles
                - **Related concept connections** to deepen understanding
                """)
                
                if st.button("See Sample Explanation"):
                    st.markdown("""
                    **Problem:** "What is 15% of 240?"
                    **Your Answer:** "30"
                    **Correct Answer:** "36"
                    
                    **AI Explanation:**
                    
                    I can see where the confusion might come from! Here's the step-by-step approach:
                    
                    **Step 1:** Convert percentage to decimal: 15% = 0.15
                    **Step 2:** Multiply: 0.15 × 240 = 36
                    
                    **Common Mistake:** You might have calculated 240 ÷ 8 = 30, which would be about 12.5%. 
                    
                    **Memory Tip:** "OF" means multiply, and always convert the percentage first!
                    """)
            
            with tab3:
                st.markdown("""
                ### 📊 Comprehensive Learning Assessment
                
                Our AI analyzes your learning patterns to provide:
                
                - **Strengths identification** to build confidence
                - **Weakness detection** with targeted improvement plans
                - **Learning style analysis** to optimize your study approach
                - **Progress predictions** to set realistic goals
                """)
                
                if st.button("View Sample Assessment"):
                    st.markdown("""
                    **Your Learning Profile:**
                    
                    **🎯 Strengths:**
                    - Excellent consistency (14-day study streak!)
                    - High accuracy in algebra (85%)
                    - Strong problem-solving persistence
                    
                    **📈 Growth Areas:**
                    - Geometry concepts need reinforcement
                    - Speed could improve with more practice
                    
                    **💡 Recommendations:**
                    - Focus 60% of study time on geometry this week
                    - Use visual aids and drawing for spatial concepts
                    - Practice timed exercises to build speed
                    """)
            
            with tab4:
                st.markdown("""
                ### 📚 Personalized Study Planning
                
                Get custom study plans that include:
                
                - **Adaptive scheduling** based on your availability
                - **Goal-oriented milestones** with progress tracking
                - **Resource recommendations** tailored to your learning style
                - **Difficulty progression** that challenges without overwhelming
                """)
                
                if st.button("See Sample Study Plan"):
                    st.markdown("""
                    **2-Week Mathematics Focus Plan**
                    
                    **Week 1: Foundation Strengthening**
                    - Mon/Wed/Fri: 30min Algebra review
                    - Tue/Thu: 25min Geometry basics
                    - Weekend: Practice quiz
                    
                    **Week 2: Application & Practice**
                    - Daily: 20min mixed problem solving
                    - Wed: Speed challenge session
                    - Fri: Comprehensive review
                    
                    **Goal:** Achieve 80% accuracy across all topics
                    **Resources:** Visual geometry tools, step-by-step videos
                    """)
            
            # API Status
            st.markdown("---")
            api_status = "🟢 Live AI Integration" if not self.mock_mode else "🟡 Demo Mode (Smart Responses)"
            st.markdown(f"**Status:** {api_status}")
            
            if self.mock_mode:
                st.info("💡 This demo uses intelligent mock responses. With API integration, responses become even more personalized and adaptive!")
            
        except Exception as e:
            logger.error(f"Error rendering AI features demo: {e}")
            st.error("Unable to load AI features demo.")
