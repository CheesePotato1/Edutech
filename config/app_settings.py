"""
Configuration settings for EduTech AI Learning Platform
Copy this code into config/app_settings.py
"""

# Subject and learning style constants
SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "Literature", 
    "History", "Biology", "Geography", "Economics",
    "Computer Science", "Art", "Music", "Foreign Languages"
]

LEARNING_STYLES = [
    "Visual", "Auditory", "Kinesthetic", "Reading/Writing"
]

# Difficulty levels and progression
DIFFICULTY_LEVELS = {
    "Beginner": {
        "level": 1,
        "progress_threshold": 0,
        "points_multiplier": 1.0,
        "description": "Basic concepts and fundamental skills"
    },
    "Intermediate": {
        "level": 2,
        "progress_threshold": 30,
        "points_multiplier": 1.5,
        "description": "Applied knowledge and problem solving"
    },
    "Advanced": {
        "level": 3,
        "progress_threshold": 70,
        "points_multiplier": 2.0,
        "description": "Complex analysis and critical thinking"
    },
    "Expert": {
        "level": 4,
        "progress_threshold": 90,
        "points_multiplier": 2.5,
        "description": "Research-level understanding and innovation"
    }
}

# Achievement system configuration
ACHIEVEMENTS = {
    "first_login": {
        "name": "Welcome Aboard! 🎉",
        "description": "Complete your first login",
        "points": 10,
        "icon": "🎉"
    },
    "assessment_complete": {
        "name": "Self-Aware Learner 📋",
        "description": "Complete your learning assessment",
        "points": 25,
        "icon": "📋"
    },
    "first_practice": {
        "name": "Practice Rookie 🔰",
        "description": "Complete your first practice session",
        "points": 15,
        "icon": "🔰"
    },
    "problem_solver_10": {
        "name": "Problem Solver 🧮",
        "description": "Solve 10 practice problems",
        "points": 50,
        "icon": "🧮"
    },
    "problem_solver_50": {
        "name": "Problem Master 🎯",
        "description": "Solve 50 practice problems",
        "points": 150,
        "icon": "🎯"
    },
    "streak_7": {
        "name": "Week Warrior 🔥",
        "description": "Maintain a 7-day study streak",
        "points": 100,
        "icon": "🔥"
    },
    "streak_30": {
        "name": "Month Champion 🏆",
        "description": "Maintain a 30-day study streak",
        "points": 500,
        "icon": "🏆"
    },
    "progress_25": {
        "name": "Quarter Master 📈",
        "description": "Reach 25% overall progress",
        "points": 75,
        "icon": "📈"
    },
    "progress_50": {
        "name": "Halfway Hero 🎯",
        "description": "Reach 50% overall progress",
        "points": 150,
        "icon": "🎯"
    },
    "progress_75": {
        "name": "Progress Champion 🌟",
        "description": "Reach 75% overall progress",
        "points": 250,
        "icon": "🌟"
    },
    "progress_100": {
        "name": "Master Learner 👑",
        "description": "Achieve 100% progress",
        "points": 1000,
        "icon": "👑"
    },
    "tutor_favorite": {
        "name": "Tutor's Favorite ⭐",
        "description": "Receive a 5-star rating from your tutor",
        "points": 75,
        "icon": "⭐"
    },
    "session_milestone_5": {
        "name": "Session Starter 📚",
        "description": "Complete 5 learning sessions",
        "points": 50,
        "icon": "📚"
    },
    "session_milestone_25": {
        "name": "Dedicated Learner 💪",
        "description": "Complete 25 learning sessions",
        "points": 200,
        "icon": "💪"
    },
    "early_bird": {
        "name": "Early Bird 🌅",
        "description": "Study before 8 AM",
        "points": 30,
        "icon": "🌅"
    },
    "night_owl": {
        "name": "Night Owl 🦉",
        "description": "Study after 10 PM",
        "points": 30,
        "icon": "🦉"
    }
}

# Practice problem banks
PROBLEM_BANKS = {
    "Mathematics": {
        "Beginner": [
            {"question": "What is 15 + 27?", "answer": "42", "type": "arithmetic", "points": 2},
            {"question": "Solve for x: x + 5 = 12", "answer": "7", "type": "algebra", "points": 3},
            {"question": "What is 8 × 9?", "answer": "72", "type": "arithmetic", "points": 2},
            {"question": "What is 144 ÷ 12?", "answer": "12", "type": "arithmetic", "points": 2},
            {"question": "What is 25% of 80?", "answer": "20", "type": "percentage", "points": 3},
            {"question": "Round 47.8 to the nearest whole number", "answer": "48", "type": "rounding", "points": 2},
            {"question": "What is 6 × 7?", "answer": "42", "type": "arithmetic", "points": 2},
            {"question": "What is 50 - 23?", "answer": "27", "type": "arithmetic", "points": 2}
        ],
        "Intermediate": [
            {"question": "Solve: 2x + 7 = 19", "answer": "6", "type": "algebra", "points": 4},
            {"question": "Find the area of a circle with radius 5cm (use π ≈ 3.14)", "answer": "78.5", "type": "geometry", "points": 5},
            {"question": "Simplify: (3x²)(4x³)", "answer": "12x⁵", "type": "algebra", "points": 4},
            {"question": "What is 15% of 240?", "answer": "36", "type": "percentage", "points": 3},
            {"question": "Solve: x² - 4 = 0", "answer": "x = ±2", "type": "algebra", "points": 5},
            {"question": "Find the slope of the line through (2,3) and (6,11)", "answer": "2", "type": "geometry", "points": 4},
            {"question": "Factor: x² + 5x + 6", "answer": "(x+2)(x+3)", "type": "algebra", "points": 5}
        ],
        "Advanced": [
            {"question": "Find the derivative of f(x) = 3x² + 2x + 1", "answer": "6x + 2", "type": "calculus", "points": 6},
            {"question": "Solve the quadratic equation: x² - 5x + 6 = 0", "answer": "x = 2, 3", "type": "algebra", "points": 6},
            {"question": "Find the integral of 2x dx", "answer": "x² + C", "type": "calculus", "points": 6},
            {"question": "Find the limit: lim(x→0) sin(x)/x", "answer": "1", "type": "calculus", "points": 7},
            {"question": "Find the maximum of f(x) = -x² + 4x + 1", "answer": "x = 2", "type": "calculus", "points": 7}
        ]
    },
    "Physics": {
        "Beginner": [
            {"question": "What is the unit of force?", "answer": "Newton", "type": "concepts", "points": 2},
            {"question": "If a car travels 60 km in 2 hours, what is its speed?", "answer": "30 km/h", "type": "motion", "points": 3},
            {"question": "What happens to the volume of gas when heated?", "answer": "increases", "type": "concepts", "points": 2},
            {"question": "What is the acceleration due to gravity on Earth?", "answer": "9.8 m/s²", "type": "concepts", "points": 3}
        ],
        "Intermediate": [
            {"question": "A car accelerates at 2 m/s². What's its velocity after 5 seconds from rest?", "answer": "10 m/s", "type": "motion", "points": 4},
            {"question": "Calculate force: F = ma, where m = 10kg and a = 3 m/s²", "answer": "30 N", "type": "forces", "points": 4},
            {"question": "What's the kinetic energy of a 5kg object moving at 10 m/s? (KE = ½mv²)", "answer": "250 J", "type": "energy", "points": 5},
            {"question": "Find the momentum of a 2kg object moving at 15 m/s", "answer": "30 kg⋅m/s", "type": "motion", "points": 4}
        ],
        "Advanced": [
            {"question": "Calculate the electric field 2m from a 5μC charge (k = 9×10⁹)", "answer": "11,250 N/C", "type": "electricity", "points": 6},
            {"question": "Find the frequency of light with wavelength 500nm (c = 3×10⁸ m/s)", "answer": "6×10¹⁴ Hz", "type": "waves", "points": 6},
            {"question": "Calculate the magnetic force on a 2A current in a 0.5T field", "answer": "1 N per meter", "type": "magnetism", "points": 7}
        ]
    },
    "Chemistry": {
        "Beginner": [
            {"question": "What is the chemical symbol for water?", "answer": "H2O", "type": "formulas", "points": 2},
            {"question": "How many protons does carbon have?", "answer": "6", "type": "atoms", "points": 2},
            {"question": "What is the pH of pure water?", "answer": "7", "type": "acids", "points": 2},
            {"question": "What is the chemical symbol for sodium?", "answer": "Na", "type": "elements", "points": 2}
        ],
        "Intermediate": [
            {"question": "Balance: H₂ + O₂ → H₂O", "answer": "2H₂ + O₂ → 2H₂O", "type": "equations", "points": 4},
            {"question": "How many moles are in 36g of H₂O? (H₂O = 18 g/mol)", "answer": "2 moles", "type": "moles", "points": 4},
            {"question": "What's the molarity of 2 moles of NaCl in 1L solution?", "answer": "2 M", "type": "solutions", "points": 4}
        ],
        "Advanced": [
            {"question": "Calculate ΔG for a reaction with ΔH = -100 kJ/mol, T = 298K, ΔS = -50 J/mol⋅K", "answer": "-85.1 kJ/mol", "type": "thermodynamics", "points": 6},
            {"question": "What is the pH of 0.01 M HCl solution?", "answer": "2", "type": "acids", "points": 5}
        ]
    }
}

# Study goals and targets
DEFAULT_GOALS = {
    "daily": {
        "study_time": 2.0,  # hours
        "problems_solved": 10,
        "sessions_completed": 2
    },
    "weekly": {
        "study_time": 14.0,  # hours
        "problems_solved": 70,
        "sessions_completed": 14
    },
    "monthly": {
        "study_time": 60.0,  # hours
        "problems_solved": 300,
        "sessions_completed": 60
    }
}

# AI Model configurations (for future use)
AI_MODELS = {
    "GPT-4": {
        "description": "Primary tutoring, creative writing, complex problem-solving",
        "strengths": ["Reasoning", "Code generation", "Creative writing"],
        "use_cases": ["Math tutoring", "Essay help", "Programming assistance"],
        "api_endpoint": "openai"
    },
    "Claude": {
        "description": "Content summarization, reading comprehension, academic discussions",
        "strengths": ["Analysis", "Safety", "Helpful explanations"],
        "use_cases": ["Literature analysis", "Research help", "Academic discussions"],
        "api_endpoint": "anthropic"
    }
}

# Progress calculation settings
PROGRESS_SETTINGS = {
    "points_per_problem": {
        "Beginner": 2,
        "Intermediate": 4,
        "Advanced": 6,
        "Expert": 8
    },
    "streak_bonus_multiplier": 1.5,
    "accuracy_bonus_threshold": 0.8,  # 80% accuracy for bonus
    "time_spent_points_ratio": 10,  # 10 points per hour
    "max_daily_points": 200
}

# Notification settings
NOTIFICATION_TYPES = {
    "achievement": {"icon": "🏆", "color": "#FFD700"},
    "milestone": {"icon": "🎯", "color": "#4CAF50"},
    "reminder": {"icon": "⏰", "color": "#2196F3"},
    "warning": {"icon": "⚠️", "color": "#FF9800"},
    "success": {"icon": "✅", "color": "#4CAF50"},
    "info": {"icon": "ℹ️", "color": "#2196F3"}
}
