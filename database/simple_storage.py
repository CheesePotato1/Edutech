"""
Simple data storage and persistence for EduTech AI Learning Platform
Copy this code into database/simple_storage.py
"""

import streamlit as st
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
import os
import pickle
import hashlib

logger = logging.getLogger(__name__)

class SimpleStorage:
    """Simple data storage system with SQLite backend and session state fallback"""
    
    def __init__(self, db_path: str = "data/edutech.db"):
        self.db_path = db_path
        self.use_database = self._init_database()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        if self.use_database:
            self._create_tables()
        else:
            logger.warning("Using session state storage - data will not persist between sessions")
    
    def _init_database(self) -> bool:
        """Initialize SQLite database connection"""
        try:
            # Test if we can create/access the database
            conn = sqlite3.connect(self.db_path)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Cannot initialize database: {e}")
            return False
    
    def _create_tables(self):
        """Create necessary database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    password_hash TEXT,
                    profile_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # User stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id TEXT PRIMARY KEY,
                    overall_progress REAL DEFAULT 0,
                    total_points INTEGER DEFAULT 0,
                    study_streak INTEGER DEFAULT 0,
                    study_time_today REAL DEFAULT 0,
                    total_study_time REAL DEFAULT 0,
                    sessions_completed INTEGER DEFAULT 0,
                    problems_solved INTEGER DEFAULT 0,
                    accuracy_rate REAL DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    experience_points INTEGER DEFAULT 0,
                    achievements INTEGER DEFAULT 0,
                    last_activity_date DATE,
                    stats_data TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Study sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    session_type TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'planned',
                    problems_solved INTEGER DEFAULT 0,
                    problems_correct INTEGER DEFAULT 0,
                    points_earned INTEGER DEFAULT 0,
                    difficulty_level TEXT,
                    session_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Achievements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    achievement_type TEXT NOT NULL,
                    achievement_name TEXT NOT NULL,
                    description TEXT,
                    points_awarded INTEGER DEFAULT 0,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    achievement_data TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Goals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_goals (
                    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    goal_type TEXT NOT NULL,
                    goal_title TEXT NOT NULL,
                    goal_description TEXT,
                    target_value REAL,
                    current_value REAL DEFAULT 0,
                    target_date DATE,
                    status TEXT DEFAULT 'active',
                    goal_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Chat history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    message_content TEXT NOT NULL,
                    subject TEXT,
                    response_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Practice problems table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS practice_attempts (
                    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    problem_type TEXT NOT NULL,
                    difficulty_level TEXT NOT NULL,
                    question TEXT NOT NULL,
                    user_answer TEXT,
                    correct_answer TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    time_taken_seconds INTEGER,
                    hints_used INTEGER DEFAULT 0,
                    attempt_data TEXT,
                    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            self.use_database = False
    
    def save_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Save user data"""
        try:
            if self.use_database:
                return self._save_user_to_db(user_id, user_data)
            else:
                return self._save_user_to_session(user_id, user_data)
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            return False
    
    def _save_user_to_db(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Save user data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hash password if present
            password_hash = None
            if 'password' in user_data:
                password_hash = self._hash_password(user_data['password'])
            
            # Prepare profile data (everything except core fields)
            profile_data = {k: v for k, v in user_data.items() 
                          if k not in ['name', 'email', 'role', 'password']}
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, name, email, role, password_hash, profile_data, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                user_data.get('name', ''),
                user_data.get('email', ''),
                user_data.get('role', ''),
                password_hash,
                json.dumps(profile_data),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving user to database: {e}")
            return False
    
    def _save_user_to_session(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Save user data to session state"""
        try:
            if 'all_users' not in st.session_state:
                st.session_state.all_users = {}
            
            st.session_state.all_users[user_id] = user_data
            return True
            
        except Exception as e:
            logger.error(f"Error saving user to session: {e}")
            return False
    
    def load_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user data"""
        try:
            if self.use_database:
                return self._load_user_from_db(user_id)
            else:
                return self._load_user_from_session(user_id)
        except Exception as e:
            logger.error(f"Error loading user: {e}")
            return None
    
    def _load_user_from_db(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, email, role, profile_data, created_at, last_login
                FROM users WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                name, email, role, profile_data, created_at, last_login = result
                
                user_data = {
                    'name': name,
                    'email': email,
                    'role': role,
                    'created_at': created_at,
                    'last_login': last_login
                }
                
                # Add profile data
                if profile_data:
                    profile = json.loads(profile_data)
                    user_data.update(profile)
                
                return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading user from database: {e}")
            return None
    
    def _load_user_from_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user data from session state"""
        try:
            return st.session_state.all_users.get(user_id)
        except Exception as e:
            logger.error(f"Error loading user from session: {e}")
            return None
    
    def save_user_stats(self, user_id: str, stats: Dict[str, Any]) -> bool:
        """Save user statistics"""
        try:
            if self.use_database:
                return self._save_stats_to_db(user_id, stats)
            else:
                return self._save_stats_to_session(user_id, stats)
        except Exception as e:
            logger.error(f"Error saving user stats: {e}")
            return False
    
    def _save_stats_to_db(self, user_id: str, stats: Dict[str, Any]) -> bool:
        """Save user stats to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract core stats
            core_stats = {
                'overall_progress': stats.get('overall_progress', 0),
                'total_points': stats.get('total_points', 0),
                'study_streak': stats.get('study_streak', 0),
                'study_time_today': stats.get('study_time_today', 0),
                'total_study_time': stats.get('total_study_time', 0),
                'sessions_completed': stats.get('sessions_completed', 0),
                'problems_solved': stats.get('problems_solved', 0),
                'accuracy_rate': stats.get('accuracy_rate', 0),
                'level': stats.get('level', 1),
                'experience_points': stats.get('experience_points', 0),
                'achievements': stats.get('achievements', 0),
                'last_activity_date': stats.get('last_activity_date')
            }
            
            # Everything else goes into stats_data
            extended_stats = {k: v for k, v in stats.items() if k not in core_stats}
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_stats 
                (user_id, overall_progress, total_points, study_streak, study_time_today,
                 total_study_time, sessions_completed, problems_solved, accuracy_rate,
                 level, experience_points, achievements, last_activity_date, 
                 stats_data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                core_stats['overall_progress'],
                core_stats['total_points'],
                core_stats['study_streak'],
                core_stats['study_time_today'],
                core_stats['total_study_time'],
                core_stats['sessions_completed'],
                core_stats['problems_solved'],
                core_stats['accuracy_rate'],
                core_stats['level'],
                core_stats['experience_points'],
                core_stats['achievements'],
                core_stats['last_activity_date'],
                json.dumps(extended_stats),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving stats to database: {e}")
            return False
    
    def _save_stats_to_session(self, user_id: str, stats: Dict[str, Any]) -> bool:
        """Save user stats to session state"""
        try:
            if 'user_stats' not in st.session_state:
                st.session_state.user_stats = {}
            
            st.session_state.user_stats[user_id] = stats
            return True
            
        except Exception as e:
            logger.error(f"Error saving stats to session: {e}")
            return False
    
    def load_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user statistics"""
        try:
            if self.use_database:
                return self._load_stats_from_db(user_id)
            else:
                return self._load_stats_from_session(user_id)
        except Exception as e:
            logger.error(f"Error loading user stats: {e}")
            return None
    
    def _load_stats_from_db(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user stats from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT overall_progress, total_points, study_streak, study_time_today,
                       total_study_time, sessions_completed, problems_solved, accuracy_rate,
                       level, experience_points, achievements, last_activity_date, 
                       stats_data, updated_at
                FROM user_stats WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                (overall_progress, total_points, study_streak, study_time_today,
                 total_study_time, sessions_completed, problems_solved, accuracy_rate,
                 level, experience_points, achievements, last_activity_date,
                 stats_data, updated_at) = result
                
                stats = {
                    'overall_progress': overall_progress,
                    'total_points': total_points,
                    'study_streak': study_streak,
                    'study_time_today': study_time_today,
                    'total_study_time': total_study_time,
                    'sessions_completed': sessions_completed,
                    'problems_solved': problems_solved,
                    'accuracy_rate': accuracy_rate,
                    'level': level,
                    'experience_points': experience_points,
                    'achievements': achievements,
                    'last_activity_date': last_activity_date,
                    'updated_at': updated_at
                }
                
                # Add extended stats
                if stats_data:
                    extended_stats = json.loads(stats_data)
                    stats.update(extended_stats)
                
                return stats
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading stats from database: {e}")
            return None
    
    def _load_stats_from_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user stats from session state"""
        try:
            return st.session_state.user_stats.get(user_id)
        except Exception as e:
            logger.error(f"Error loading stats from session: {e}")
            return None
    
    def save_study_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Save study session data"""
        try:
            if self.use_database:
                return self._save_session_to_db(user_id, session_data)
            else:
                return self._save_session_to_session_state(user_id, session_data)
        except Exception as e:
            logger.error(f"Error saving study session: {e}")
            return False
    
    def _save_session_to_db(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Save study session to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO study_sessions 
                (user_id, subject, session_type, duration_minutes, start_time, end_time,
                 status, problems_solved, problems_correct, points_earned, difficulty_level, session_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                session_data.get('subject', ''),
                session_data.get('type', ''),
                session_data.get('duration', 0),
                session_data.get('start_time', datetime.now()),
                session_data.get('end_time'),
                session_data.get('status', 'completed'),
                session_data.get('problems_solved', 0),
                session_data.get('problems_correct', 0),
                session_data.get('points_earned', 0),
                session_data.get('difficulty', ''),
                json.dumps(session_data)
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving session to database: {e}")
            return False
    
    def _save_session_to_session_state(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Save study session to session state"""
        try:
            if 'study_sessions' not in st.session_state:
                st.session_state.study_sessions = {}
            
            if user_id not in st.session_state.study_sessions:
                st.session_state.study_sessions[user_id] = []
            
            st.session_state.study_sessions[user_id].append(session_data)
            
            # Keep only last 50 sessions
            if len(st.session_state.study_sessions[user_id]) > 50:
                st.session_state.study_sessions[user_id] = st.session_state.study_sessions[user_id][-50:]
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving session to session state: {e}")
            return False
    
    def save_achievement(self, user_id: str, achievement_data: Dict[str, Any]) -> bool:
        """Save achievement data"""
        try:
            if self.use_database:
                return self._save_achievement_to_db(user_id, achievement_data)
            else:
                return self._save_achievement_to_session_state(user_id, achievement_data)
        except Exception as e:
            logger.error(f"Error saving achievement: {e}")
            return False
    
    def _save_achievement_to_db(self, user_id: str, achievement_data: Dict[str, Any]) -> bool:
        """Save achievement to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_achievements 
                (user_id, achievement_type, achievement_name, description, 
                 points_awarded, achievement_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                achievement_data.get('id', ''),
                achievement_data.get('name', ''),
                achievement_data.get('description', ''),
                achievement_data.get('points', 0),
                json.dumps(achievement_data)
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving achievement to database: {e}")
            return False
    
    def _save_achievement_to_session_state(self, user_id: str, achievement_data: Dict[str, Any]) -> bool:
        """Save achievement to session state"""
        try:
            if 'user_achievements' not in st.session_state:
                st.session_state.user_achievements = {}
            
            if user_id not in st.session_state.user_achievements:
                st.session_state.user_achievements[user_id] = []
            
            st.session_state.user_achievements[user_id].append(achievement_data)
            return True
            
        except Exception as e:
            logger.error(f"Error saving achievement to session state: {e}")
            return False
    
    def save_practice_attempt(self, user_id: str, attempt_data: Dict[str, Any]) -> bool:
        """Save practice problem attempt"""
        try:
            if self.use_database:
                return self._save_attempt_to_db(user_id, attempt_data)
            else:
                return self._save_attempt_to_session_state(user_id, attempt_data)
        except Exception as e:
            logger.error(f"Error saving practice attempt: {e}")
            return False
    
    def _save_attempt_to_db(self, user_id: str, attempt_data: Dict[str, Any]) -> bool:
        """Save practice attempt to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO practice_attempts 
                (user_id, subject, problem_type, difficulty_level, question, 
                 user_answer, correct_answer, is_correct, time_taken_seconds, 
                 hints_used, attempt_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                attempt_data.get('subject', ''),
                attempt_data.get('type', ''),
                attempt_data.get('difficulty', ''),
                attempt_data.get('question', ''),
                attempt_data.get('user_answer', ''),
                attempt_data.get('correct_answer', ''),
                attempt_data.get('is_correct', False),
                attempt_data.get('time_taken', 0),
                attempt_data.get('hints_used', 0),
                json.dumps(attempt_data)
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving attempt to database: {e}")
            return False
    
    def _save_attempt_to_session_state(self, user_id: str, attempt_data: Dict[str, Any]) -> bool:
        """Save practice attempt to session state"""
        try:
            if 'practice_attempts' not in st.session_state:
                st.session_state.practice_attempts = {}
            
            if user_id not in st.session_state.practice_attempts:
                st.session_state.practice_attempts[user_id] = []
            
            st.session_state.practice_attempts[user_id].append(attempt_data)
            
            # Keep only last 100 attempts
            if len(st.session_state.practice_attempts[user_id]) > 100:
                st.session_state.practice_attempts[user_id] = st.session_state.practice_attempts[user_id][-100:]
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving attempt to session state: {e}")
            return False
    
    def get_user_study_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's study sessions"""
        try:
            if self.use_database:
                return self._get_sessions_from_db(user_id, limit)
            else:
                return self._get_sessions_from_session_state(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting study sessions: {e}")
            return []
    
    def _get_sessions_from_db(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get study sessions from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT subject, session_type, duration_minutes, start_time, end_time,
                       status, problems_solved, problems_correct, points_earned, 
                       difficulty_level, session_data, created_at
                FROM study_sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in results:
                (subject, session_type, duration, start_time, end_time, status,
                 problems_solved, problems_correct, points_earned, difficulty,
                 session_data, created_at) = row
                
                session = {
                    'subject': subject,
                    'type': session_type,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'status': status,
                    'problems_solved': problems_solved,
                    'problems_correct': problems_correct,
                    'points_earned': points_earned,
                    'difficulty': difficulty,
                    'created_at': created_at
                }
                
                if session_data:
                    extended_data = json.loads(session_data)
                    session.update(extended_data)
                
                sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting sessions from database: {e}")
            return []
    
    def _get_sessions_from_session_state(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get study sessions from session state"""
        try:
            sessions = st.session_state.study_sessions.get(user_id, [])
            return sessions[-limit:] if limit else sessions
        except Exception as e:
            logger.error(f"Error getting sessions from session state: {e}")
            return []
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's achievements"""
        try:
            if self.use_database:
                return self._get_achievements_from_db(user_id)
            else:
                return self._get_achievements_from_session_state(user_id)
        except Exception as e:
            logger.error(f"Error getting achievements: {e}")
            return []
    
    def _get_achievements_from_db(self, user_id: str) -> List[Dict[str, Any]]:
        """Get achievements from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT achievement_type, achievement_name, description, 
                       points_awarded, earned_at, achievement_data
                FROM user_achievements 
                WHERE user_id = ? 
                ORDER BY earned_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            achievements = []
            for row in results:
                (achievement_type, name, description, points, earned_at, achievement_data) = row
                
                achievement = {
                    'id': achievement_type,
                    'name': name,
                    'description': description,
                    'points': points,
                    'earned_at': earned_at
                }
                
                if achievement_data:
                    extended_data = json.loads(achievement_data)
                    achievement.update(extended_data)
                
                achievements.append(achievement)
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error getting achievements from database: {e}")
            return []
    
    def _get_achievements_from_session_state(self, user_id: str) -> List[Dict[str, Any]]:
        """Get achievements from session state"""
        try:
            return st.session_state.user_achievements.get(user_id, [])
        except Exception as e:
            logger.error(f"Error getting achievements from session state: {e}")
            return []
    
    def backup_data(self, backup_path: str = None) -> bool:
        """Backup all data"""
        try:
            if not backup_path:
                backup_path = f"data/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            backup_data = {}
            
            if self.use_database:
                backup_data = self._backup_from_database()
            else:
                backup_data = self._backup_from_session_state()
            
            # Save backup
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"Data backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error backing up data: {e}")
            return False
    
    def _backup_from_database(self) -> Dict[str, Any]:
        """Backup data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            backup_data = {
                'backup_date': datetime.now().isoformat(),
                'data_source': 'database',
                'users': [],
                'user_stats': [],
                'study_sessions': [],
                'achievements': [],
                'practice_attempts': []
            }
            
    def _backup_from_database(self) -> Dict[str, Any]:
        """Backup data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            backup_data = {
                'backup_date': datetime.now().isoformat(),
                'data_source': 'database',
                'users': [],
                'user_stats': [],
                'study_sessions': [],
                'achievements': [],
                'practice_attempts': []
            }
            
            # Backup users
            users_df = pd.read_sql_query("SELECT * FROM users", conn)
            backup_data['users'] = users_df.to_dict('records')
            
            # Backup user stats
            stats_df = pd.read_sql_query("SELECT * FROM user_stats", conn)
            backup_data['user_stats'] = stats_df.to_dict('records')
            
            # Backup study sessions
            sessions_df = pd.read_sql_query("SELECT * FROM study_sessions", conn)
            backup_data['study_sessions'] = sessions_df.to_dict('records')
            
            # Backup achievements
            achievements_df = pd.read_sql_query("SELECT * FROM user_achievements", conn)
            backup_data['achievements'] = achievements_df.to_dict('records')
            
            # Backup practice attempts
            attempts_df = pd.read_sql_query("SELECT * FROM practice_attempts", conn)
            backup_data['practice_attempts'] = attempts_df.to_dict('records')
            
            conn.close()
            return backup_data
            
        except Exception as e:
            logger.error(f"Error backing up from database: {e}")
            return {}
    
    def _backup_from_session_state(self) -> Dict[str, Any]:
        """Backup data from session state"""
        try:
            return {
                'backup_date': datetime.now().isoformat(),
                'data_source': 'session_state',
                'all_users': st.session_state.get('all_users', {}),
                'user_stats': st.session_state.get('user_stats', {}),
                'study_sessions': st.session_state.get('study_sessions', {}),
                'user_achievements': st.session_state.get('user_achievements', {}),
                'practice_attempts': st.session_state.get('practice_attempts', {}),
                'chat_history': st.session_state.get('ai_conversation_log', [])
            }
        except Exception as e:
            logger.error(f"Error backing up from session state: {e}")
            return {}
    
    def restore_data(self, backup_path: str) -> bool:
        """Restore data from backup"""
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            if self.use_database:
                return self._restore_to_database(backup_data)
            else:
                return self._restore_to_session_state(backup_data)
                
        except Exception as e:
            logger.error(f"Error restoring data: {e}")
            return False
    
    def _restore_to_database(self, backup_data: Dict[str, Any]) -> bool:
        """Restore data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM practice_attempts")
            cursor.execute("DELETE FROM user_achievements")
            cursor.execute("DELETE FROM study_sessions")
            cursor.execute("DELETE FROM user_stats")
            cursor.execute("DELETE FROM users")
            
            # Restore users
            if 'users' in backup_data:
                for user in backup_data['users']:
                    cursor.execute('''
                        INSERT INTO users 
                        (user_id, name, email, role, password_hash, profile_data, 
                         created_at, last_login, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user.get('user_id'),
                        user.get('name'),
                        user.get('email'),
                        user.get('role'),
                        user.get('password_hash'),
                        user.get('profile_data'),
                        user.get('created_at'),
                        user.get('last_login'),
                        user.get('is_active', 1)
                    ))
            
            # Restore user stats
            if 'user_stats' in backup_data:
                for stats in backup_data['user_stats']:
                    cursor.execute('''
                        INSERT INTO user_stats 
                        (user_id, overall_progress, total_points, study_streak, 
                         study_time_today, total_study_time, sessions_completed, 
                         problems_solved, accuracy_rate, level, experience_points, 
                         achievements, last_activity_date, stats_data, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stats.get('user_id'),
                        stats.get('overall_progress', 0),
                        stats.get('total_points', 0),
                        stats.get('study_streak', 0),
                        stats.get('study_time_today', 0),
                        stats.get('total_study_time', 0),
                        stats.get('sessions_completed', 0),
                        stats.get('problems_solved', 0),
                        stats.get('accuracy_rate', 0),
                        stats.get('level', 1),
                        stats.get('experience_points', 0),
                        stats.get('achievements', 0),
                        stats.get('last_activity_date'),
                        stats.get('stats_data'),
                        stats.get('updated_at')
                    ))
            
            conn.commit()
            conn.close()
            
            logger.info("Data restored to database successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring to database: {e}")
            return False
    
    def _restore_to_session_state(self, backup_data: Dict[str, Any]) -> bool:
        """Restore data to session state"""
        try:
            if 'all_users' in backup_data:
                st.session_state.all_users = backup_data['all_users']
            
            if 'user_stats' in backup_data:
                st.session_state.user_stats = backup_data['user_stats']
            
            if 'study_sessions' in backup_data:
                st.session_state.study_sessions = backup_data['study_sessions']
            
            if 'user_achievements' in backup_data:
                st.session_state.user_achievements = backup_data['user_achievements']
            
            if 'practice_attempts' in backup_data:
                st.session_state.practice_attempts = backup_data['practice_attempts']
            
            if 'chat_history' in backup_data:
                st.session_state.ai_conversation_log = backup_data['chat_history']
            
            logger.info("Data restored to session state successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring to session state: {e}")
            return False
    
    def get_analytics_data(self, user_id: str = None) -> Dict[str, Any]:
        """Get analytics data for dashboard"""
        try:
            if self.use_database:
                return self._get_analytics_from_db(user_id)
            else:
                return self._get_analytics_from_session_state(user_id)
        except Exception as e:
            logger.error(f"Error getting analytics data: {e}")
            return {}
    
    def _get_analytics_from_db(self, user_id: str = None) -> Dict[str, Any]:
        """Get analytics data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            analytics = {}
            
            if user_id:
                # User-specific analytics
                cursor = conn.cursor()
                
                # Study sessions analytics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(duration_minutes) as total_minutes,
                        AVG(duration_minutes) as avg_duration,
                        SUM(problems_solved) as total_problems,
                        SUM(problems_correct) as total_correct
                    FROM study_sessions 
                    WHERE user_id = ?
                ''', (user_id,))
                
                session_stats = cursor.fetchone()
                if session_stats:
                    total_sessions, total_minutes, avg_duration, total_problems, total_correct = session_stats
                    analytics['sessions'] = {
                        'total': total_sessions or 0,
                        'total_time_hours': (total_minutes or 0) / 60,
                        'avg_duration_minutes': avg_duration or 0,
                        'total_problems': total_problems or 0,
                        'accuracy': (total_correct / total_problems * 100) if total_problems else 0
                    }
                
                # Subject progress
                cursor.execute('''
                    SELECT subject, COUNT(*) as sessions, SUM(duration_minutes) as time_spent
                    FROM study_sessions 
                    WHERE user_id = ?
                    GROUP BY subject
                    ORDER BY time_spent DESC
                ''', (user_id,))
                
                subject_data = cursor.fetchall()
                analytics['subjects'] = [
                    {'subject': row[0], 'sessions': row[1], 'time_hours': row[2] / 60}
                    for row in subject_data
                ]
                
                # Recent activity (last 30 days)
                cursor.execute('''
                    SELECT DATE(created_at) as date, COUNT(*) as sessions
                    FROM study_sessions 
                    WHERE user_id = ? AND created_at >= date('now', '-30 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date
                ''', (user_id,))
                
                activity_data = cursor.fetchall()
                analytics['daily_activity'] = [
                    {'date': row[0], 'sessions': row[1]}
                    for row in activity_data
                ]
            
            else:
                # Platform-wide analytics
                cursor = conn.cursor()
                
                # Total users
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                analytics['total_users'] = cursor.fetchone()[0]
                
                # Total sessions
                cursor.execute("SELECT COUNT(*) FROM study_sessions")
                analytics['total_sessions'] = cursor.fetchone()[0]
                
                # Total study time
                cursor.execute("SELECT SUM(duration_minutes) FROM study_sessions")
                total_minutes = cursor.fetchone()[0] or 0
                analytics['total_study_hours'] = total_minutes / 60
            
            conn.close()
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics from database: {e}")
            return {}
    
    def _get_analytics_from_session_state(self, user_id: str = None) -> Dict[str, Any]:
        """Get analytics data from session state"""
        try:
            analytics = {}
            
            if user_id:
                # User-specific analytics from session state
                sessions = st.session_state.study_sessions.get(user_id, [])
                stats = st.session_state.user_stats.get(user_id, {})
                
                analytics['sessions'] = {
                    'total': len(sessions),
                    'total_time_hours': stats.get('total_study_time', 0),
                    'total_problems': stats.get('problems_solved', 0),
                    'accuracy': stats.get('accuracy_rate', 0)
                }
                
                # Subject breakdown
                subject_time = {}
                for session in sessions:
                    subject = session.get('subject', 'Unknown')
                    duration = session.get('duration', 0) / 60  # Convert to hours
                    subject_time[subject] = subject_time.get(subject, 0) + duration
                
                analytics['subjects'] = [
                    {'subject': subject, 'time_hours': time}
                    for subject, time in subject_time.items()
                ]
            
            else:
                # Platform-wide analytics
                analytics['total_users'] = len(st.session_state.all_users)
                
                total_sessions = sum(
                    len(sessions) for sessions in st.session_state.study_sessions.values()
                )
                analytics['total_sessions'] = total_sessions
                
                total_time = sum(
                    stats.get('total_study_time', 0) 
                    for stats in st.session_state.user_stats.values()
                )
                analytics['total_study_hours'] = total_time
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics from session state: {e}")
            return {}
    
    def cleanup_old_data(self, days_old: int = 90) -> bool:
        """Clean up old data (database only)"""
        try:
            if not self.use_database:
                return True  # No cleanup needed for session state
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Clean up old study sessions
            cursor.execute('''
                DELETE FROM study_sessions 
                WHERE created_at < ? AND status = 'completed'
            ''', (cutoff_date,))
            
            # Clean up old practice attempts
            cursor.execute('''
                DELETE FROM practice_attempts 
                WHERE attempted_at < ?
            ''', (cutoff_date,))
            
            # Clean up old chat history
            cursor.execute('''
                DELETE FROM chat_history 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up data older than {days_old} days")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False
    
    def export_user_data(self, user_id: str, export_path: str = None) -> bool:
        """Export all data for a specific user"""
        try:
            if not export_path:
                export_path = f"data/export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                'user_id': user_id,
                'export_date': datetime.now().isoformat(),
                'user_profile': self.load_user(user_id),
                'user_stats': self.load_user_stats(user_id),
                'study_sessions': self.get_user_study_sessions(user_id, limit=None),
                'achievements': self.get_user_achievements(user_id),
                'analytics': self.get_analytics_data(user_id)
            }
            
            # Save export
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"User data exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return False
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get database status and statistics"""
        try:
            status = {
                'using_database': self.use_database,
                'database_path': self.db_path,
                'database_exists': os.path.exists(self.db_path) if self.use_database else False,
                'last_backup': None,
                'table_counts': {}
            }
            
            if self.use_database and os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get table counts
                tables = ['users', 'user_stats', 'study_sessions', 'user_achievements', 'practice_attempts', 'chat_history']
                
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        status['table_counts'][table] = count
                    except sqlite3.OperationalError:
                        status['table_counts'][table] = 0
                
                # Get database size
                status['database_size_bytes'] = os.path.getsize(self.db_path)
                status['database_size_mb'] = status['database_size_bytes'] / (1024 * 1024)
                
                conn.close()
            
            else:
                # Session state statistics
                status['session_data'] = {
                    'users': len(st.session_state.get('all_users', {})),
                    'user_stats': len(st.session_state.get('user_stats', {})),
                    'study_sessions': sum(len(sessions) for sessions in st.session_state.get('study_sessions', {}).values()),
                    'achievements': sum(len(achievements) for achievements in st.session_state.get('user_achievements', {}).values())
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting database status: {e}")
            return {'error': str(e)}
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password"""
        try:
            if self.use_database:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT password_hash FROM users WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    stored_hash = result[0]
                    return stored_hash == self._hash_password(password)
            
            else:
                # For session state, check plain password (demo mode)
                user_data = st.session_state.all_users.get(user_id)
                if user_data:
                    return user_data.get('password') == password
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def find_user_by_email(self, email: str) -> Optional[str]:
        """Find user ID by email address"""
        try:
            if self.use_database:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT user_id FROM users WHERE email = ? AND is_active = 1", (email,))
                result = cursor.fetchone()
                conn.close()
                
                return result[0] if result else None
            
            else:
                # Search in session state
                for user_id, user_data in st.session_state.all_users.items():
                    if user_data.get('email') == email:
                        return user_id
                
                return None
            
        except Exception as e:
            logger.error(f"Error finding user by email: {e}")
            return None
    
    def render_data_management_interface(self):
        """Render data management interface for admins"""
        try:
            st.subheader("🗄️ Data Management")
            
            # Database status
            status = self.get_database_status()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 System Status")
                
                if status['using_database']:
                    st.success("✅ Using SQLite Database")
                    st.info(f"📁 Database: {status['database_path']}")
                    
                    if 'database_size_mb' in status:
                        st.info(f"💾 Size: {status['database_size_mb']:.2f} MB")
                else:
                    st.warning("⚠️ Using Session State (Temporary)")
                    st.info("Data will be lost when session ends")
            
            with col2:
                st.markdown("#### 📈 Data Statistics")
                
                if status['using_database'] and 'table_counts' in status:
                    for table, count in status['table_counts'].items():
                        st.metric(table.replace('_', ' ').title(), count)
                
                elif 'session_data' in status:
                    for key, count in status['session_data'].items():
                        st.metric(key.replace('_', ' ').title(), count)
            
            # Data operations
            st.markdown("#### 🔧 Data Operations")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Backup Data", use_container_width=True):
                    if self.backup_data():
                        st.success("✅ Data backed up successfully!")
                    else:
                        st.error("❌ Backup failed!")
            
            with col2:
                if st.button("🧹 Cleanup Old Data", use_container_width=True):
                    if self.cleanup_old_data(90):
                        st.success("✅ Old data cleaned up!")
                    else:
                        st.error("❌ Cleanup failed!")
            
            with col3:
                if st.button("📊 Export Analytics", use_container_width=True):
                    analytics = self.get_analytics_data()
                    st.json(analytics)
            
            # File upload for restore
            st.markdown("#### 📥 Restore Data")
            uploaded_file = st.file_uploader("Choose backup file", type=['json'])
            
            if uploaded_file and st.button("🔄 Restore from Backup"):
                try:
                    backup_data = json.load(uploaded_file)
                    
                    if self.use_database:
                        success = self._restore_to_database(backup_data)
                    else:
                        success = self._restore_to_session_state(backup_data)
                    
                    if success:
                        st.success("✅ Data restored successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Restore failed!")
                        
                except Exception as e:
                    st.error(f"❌ Error reading backup file: {e}")
            
        except Exception as e:
            logger.error(f"Error rendering data management interface: {e}")
            st.error("Unable to load data management interface.")
