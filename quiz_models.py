"""
TruthLens Media Literacy Quiz Engine - Database Models
File: quiz_models.py
Date: December 26, 2024
Version: 1.0.0 - INITIAL RELEASE

CHANGE LOG:
- December 26, 2024 v1.0.0: Initial creation
  - CREATED: Quiz system database models
  - PATTERN: Follows simple_debate_models.py pattern exactly
  - FEATURES: Quizzes, questions, options, attempts, achievements, leaderboard
  - ANONYMOUS: Browser fingerprint tracking (no user accounts)
  - GAMIFICATION: Points, badges, streaks, leaderboards

PURPOSE:
Educational quiz system to teach media literacy skills through interactive quizzes

QUIZ TYPES:
- Clickbait Detection
- Bias Spotting
- Fact vs Opinion
- Source Credibility
- Manipulation Detection

MODELS:
- Quiz: Quiz metadata (title, category, difficulty)
- Question: Individual quiz questions
- QuestionOption: Multiple choice options
- QuizAttempt: User quiz attempts (anonymous)
- Achievement: Badges and achievements
- UserAchievement: User achievement unlocks (anonymous)
- LeaderboardEntry: Top scores (anonymous)

ANONYMOUS TRACKING:
- Browser fingerprint (SHA256 hash of IP + User-Agent)
- Optional display name for leaderboard
- No authentication required

Last modified: December 26, 2024 - v1.0.0 Initial Creation
"""

from datetime import datetime
import hashlib
import json

# Global db instance - will be set by init_quiz_db()
db = None

# Global model references - will be set after db is initialized
Quiz = None
Question = None
QuestionOption = None
QuizAttempt = None
Achievement = None
UserAchievement = None
LeaderboardEntry = None


def init_quiz_db(shared_db):
    """
    Initialize quiz models with SHARED database instance from app.py
    
    This follows the exact pattern from simple_debate_models.py:
    1. Accept shared db instance
    2. Define models with proper columns
    3. Export to module globals
    
    Args:
        shared_db: The SQLAlchemy database instance from app.py
        
    Returns:
        The same database instance (for consistency)
    """
    global db, Quiz, Question, QuestionOption, QuizAttempt, Achievement, UserAchievement, LeaderboardEntry
    
    db = shared_db
    
    # NOW define the models with proper columns
    
    class Quiz(db.Model):
        """
        Quiz model - contains quiz metadata and settings
        
        Categories: Clickbait, Bias, Fact vs Opinion, Source Credibility, Manipulation
        Difficulty: Beginner (1), Intermediate (2), Expert (3)
        """
        __tablename__ = 'quizzes'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Content
        title = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text)
        category = db.Column(db.String(50), nullable=False, index=True)
        
        # Settings
        difficulty = db.Column(db.Integer, default=1, nullable=False)  # 1=Beginner, 2=Intermediate, 3=Expert
        time_limit = db.Column(db.Integer)  # seconds, nullable (no time limit if null)
        passing_score = db.Column(db.Integer, default=70)  # percentage
        
        # Status
        is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
        
        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        questions = db.relationship('Question', back_populates='quiz', lazy='dynamic',
                                   cascade='all, delete-orphan', order_by='Question.order_index')
        attempts = db.relationship('QuizAttempt', back_populates='quiz', lazy='dynamic',
                                  cascade='all, delete-orphan')
        
        # Indexes
        __table_args__ = (
            db.Index('idx_quiz_category_active', 'category', 'is_active'),
            db.Index('idx_quiz_difficulty_active', 'difficulty', 'is_active'),
        )
        
        def get_question_count(self):
            """Get total number of questions in quiz"""
            return self.questions.count()
        
        def get_average_score(self):
            """Get average score from all attempts"""
            attempts = self.attempts.filter_by(completed=True).all()
            if not attempts:
                return 0
            return round(sum(a.score for a in attempts) / len(attempts), 1)
        
        def get_completion_count(self):
            """Get total number of completed attempts"""
            return self.attempts.filter_by(completed=True).count()
        
        def get_difficulty_name(self):
            """Get difficulty as string"""
            return {1: 'Beginner', 2: 'Intermediate', 3: 'Expert'}.get(self.difficulty, 'Unknown')
        
        def to_dict(self, include_questions=False):
            """Convert to dictionary for JSON responses"""
            result = {
                'id': self.id,
                'title': self.title,
                'description': self.description,
                'category': self.category,
                'difficulty': self.difficulty,
                'difficulty_name': self.get_difficulty_name(),
                'time_limit': self.time_limit,
                'passing_score': self.passing_score,
                'is_active': self.is_active,
                'question_count': self.get_question_count(),
                'average_score': self.get_average_score(),
                'completion_count': self.get_completion_count(),
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
            
            if include_questions:
                result['questions'] = [q.to_dict(include_options=True) for q in self.questions.order_by(Question.order_index).all()]
            
            return result
        
        def __repr__(self):
            return f'<Quiz {self.id}: {self.title}>'
    
    
    class Question(db.Model):
        """
        Question model - individual quiz questions
        
        Question types:
        - multiple_choice: Select one correct answer
        - true_false: True or false question
        - spot_manipulation: Identify biased/manipulative words
        """
        __tablename__ = 'questions'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Quiz relationship
        quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False, index=True)
        
        # Content
        question_text = db.Column(db.Text, nullable=False)
        question_type = db.Column(db.String(20), default='multiple_choice', nullable=False)
        explanation = db.Column(db.Text)  # Shown after answering
        
        # Media (optional)
        media_url = db.Column(db.String(500))  # For image-based questions
        
        # Ordering
        order_index = db.Column(db.Integer, default=0, nullable=False)
        
        # Difficulty & scoring
        difficulty_level = db.Column(db.Integer, default=1)  # 1=Easy, 2=Medium, 3=Hard
        points_value = db.Column(db.Integer, default=10)
        
        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        
        # Relationships
        quiz = db.relationship('Quiz', back_populates='questions')
        options = db.relationship('QuestionOption', back_populates='question', lazy='dynamic',
                                 cascade='all, delete-orphan', order_by='QuestionOption.order_index')
        
        # Constraints
        __table_args__ = (
            db.CheckConstraint("question_type IN ('multiple_choice', 'true_false', 'spot_manipulation')", 
                             name='check_question_type'),
            db.Index('idx_question_quiz_order', 'quiz_id', 'order_index'),
        )
        
        def get_correct_option(self):
            """Get the correct answer option"""
            return self.options.filter_by(is_correct=True).first()
        
        def check_answer(self, option_id):
            """Check if selected option is correct"""
            option = self.options.filter_by(id=option_id).first()
            return option.is_correct if option else False
        
        def to_dict(self, include_options=False, include_correct_answer=False):
            """Convert to dictionary for JSON responses"""
            result = {
                'id': self.id,
                'quiz_id': self.quiz_id,
                'question_text': self.question_text,
                'question_type': self.question_type,
                'explanation': self.explanation,
                'media_url': self.media_url,
                'order_index': self.order_index,
                'difficulty_level': self.difficulty_level,
                'points_value': self.points_value
            }
            
            if include_options:
                options = self.options.order_by(QuestionOption.order_index).all()
                result['options'] = [o.to_dict(include_correct=include_correct_answer) for o in options]
            
            return result
        
        def __repr__(self):
            return f'<Question {self.id} in Quiz {self.quiz_id}>'
    
    
    class QuestionOption(db.Model):
        """
        Question option model - multiple choice options
        
        For multiple_choice questions: 3-4 options with one correct
        For true_false questions: 2 options (True/False)
        """
        __tablename__ = 'question_options'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Question relationship
        question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
        
        # Content
        option_text = db.Column(db.String(500), nullable=False)
        is_correct = db.Column(db.Boolean, default=False, nullable=False)
        
        # Ordering
        order_index = db.Column(db.Integer, default=0, nullable=False)
        
        # Relationship
        question = db.relationship('Question', back_populates='options')
        
        # Indexes
        __table_args__ = (
            db.Index('idx_option_question_order', 'question_id', 'order_index'),
        )
        
        def to_dict(self, include_correct=False):
            """Convert to dictionary for JSON responses"""
            result = {
                'id': self.id,
                'option_text': self.option_text,
                'order_index': self.order_index
            }
            
            if include_correct:
                result['is_correct'] = self.is_correct
            
            return result
        
        def __repr__(self):
            return f'<QuestionOption {self.id} for Question {self.question_id}>'
    
    
    class QuizAttempt(db.Model):
        """
        Quiz attempt model - tracks user quiz attempts (anonymous)
        
        Anonymous tracking via browser fingerprint.
        Stores answers, score, time taken, and completion status.
        """
        __tablename__ = 'quiz_attempts'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Quiz relationship
        quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False, index=True)
        
        # User identification (anonymous)
        user_fingerprint = db.Column(db.String(64), nullable=False, index=True)
        
        # Results
        score = db.Column(db.Integer, default=0)  # Percentage (0-100)
        total_questions = db.Column(db.Integer, default=0)
        correct_answers = db.Column(db.Integer, default=0)
        
        # Answers (stored as JSON: {question_id: option_id})
        answers = db.Column(db.Text)  # JSON string
        
        # Timing
        time_taken = db.Column(db.Integer)  # seconds
        difficulty_multiplier = db.Column(db.Float, default=1.0)
        
        # Points earned
        points_earned = db.Column(db.Integer, default=0)
        
        # Status
        completed = db.Column(db.Boolean, default=False, nullable=False)
        
        # Timestamps
        started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        completed_at = db.Column(db.DateTime)
        
        # Relationship
        quiz = db.relationship('Quiz', back_populates='attempts')
        
        # Indexes
        __table_args__ = (
            db.Index('idx_attempt_user_quiz', 'user_fingerprint', 'quiz_id'),
            db.Index('idx_attempt_completed', 'completed', 'completed_at'),
        )
        
        def set_answers(self, answers_dict):
            """Store answers as JSON"""
            self.answers = json.dumps(answers_dict)
        
        def get_answers(self):
            """Retrieve answers from JSON"""
            if self.answers:
                return json.loads(self.answers)
            return {}
        
        def calculate_score(self):
            """Calculate score based on correct answers"""
            if self.total_questions == 0:
                self.score = 0
                return
            
            self.score = round((self.correct_answers / self.total_questions) * 100)
        
        def to_dict(self, include_answers=False):
            """Convert to dictionary for JSON responses"""
            result = {
                'id': self.id,
                'quiz_id': self.quiz_id,
                'score': self.score,
                'total_questions': self.total_questions,
                'correct_answers': self.correct_answers,
                'time_taken': self.time_taken,
                'points_earned': self.points_earned,
                'completed': self.completed,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None
            }
            
            if include_answers:
                result['answers'] = self.get_answers()
            
            return result
        
        def __repr__(self):
            return f'<QuizAttempt {self.id} Quiz={self.quiz_id} Score={self.score}%>'
    
    
    class Achievement(db.Model):
        """
        Achievement model - badges and milestones
        
        Examples:
        - "First Quiz" - Complete your first quiz
        - "Perfect Score" - Get 100% on any quiz
        - "Bias Detector" - Spot 10 biased headlines
        """
        __tablename__ = 'achievements'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Content
        name = db.Column(db.String(100), nullable=False, unique=True)
        description = db.Column(db.Text)
        badge_icon = db.Column(db.String(50))  # emoji or icon name
        
        # Unlock criteria (stored as JSON)
        unlock_criteria = db.Column(db.Text)  # JSON: {type: "quiz_count", value: 1}
        
        # Display
        category = db.Column(db.String(50), default='General')  # Beginner, Intermediate, Expert
        points_value = db.Column(db.Integer, default=0)
        
        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        
        # Relationships
        user_achievements = db.relationship('UserAchievement', back_populates='achievement', 
                                           lazy='dynamic', cascade='all, delete-orphan')
        
        def get_unlock_criteria(self):
            """Get unlock criteria as dict"""
            if self.unlock_criteria:
                return json.loads(self.unlock_criteria)
            return {}
        
        def set_unlock_criteria(self, criteria_dict):
            """Set unlock criteria from dict"""
            self.unlock_criteria = json.dumps(criteria_dict)
        
        def to_dict(self):
            """Convert to dictionary for JSON responses"""
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'badge_icon': self.badge_icon,
                'category': self.category,
                'points_value': self.points_value,
                'unlock_criteria': self.get_unlock_criteria()
            }
        
        def __repr__(self):
            return f'<Achievement {self.id}: {self.name}>'
    
    
    class UserAchievement(db.Model):
        """
        User achievement model - tracks unlocked achievements (anonymous)
        
        Links browser fingerprint to unlocked achievements.
        """
        __tablename__ = 'user_achievements'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # User identification (anonymous)
        user_fingerprint = db.Column(db.String(64), nullable=False, index=True)
        
        # Achievement relationship
        achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False, index=True)
        
        # Timestamp
        unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        
        # Relationship
        achievement = db.relationship('Achievement', back_populates='user_achievements')
        
        # Constraints
        __table_args__ = (
            db.UniqueConstraint('user_fingerprint', 'achievement_id', name='uq_user_achievement'),
            db.Index('idx_user_achievement_unlock', 'user_fingerprint', 'unlocked_at'),
        )
        
        def to_dict(self):
            """Convert to dictionary for JSON responses"""
            return {
                'id': self.id,
                'achievement': self.achievement.to_dict() if self.achievement else None,
                'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None
            }
        
        def __repr__(self):
            return f'<UserAchievement user={self.user_fingerprint[:8]} achievement={self.achievement_id}>'
    
    
    class LeaderboardEntry(db.Model):
        """
        Leaderboard entry model - top scores (anonymous)
        
        Stores best score per user per quiz for leaderboard display.
        Optional display name for showing on leaderboard.
        """
        __tablename__ = 'leaderboard_entries'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Quiz relationship
        quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False, index=True)
        
        # User identification (anonymous)
        user_fingerprint = db.Column(db.String(64), nullable=False, index=True)
        display_name = db.Column(db.String(50))  # Optional, for leaderboard
        
        # Score
        score = db.Column(db.Integer, nullable=False)
        rank = db.Column(db.Integer)  # Calculated rank
        
        # Timestamp
        achieved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
        
        # Relationship
        quiz = db.relationship('Quiz')
        
        # Constraints
        __table_args__ = (
            db.UniqueConstraint('quiz_id', 'user_fingerprint', name='uq_quiz_user_leaderboard'),
            db.Index('idx_leaderboard_quiz_score', 'quiz_id', 'score'),
        )
        
        def to_dict(self):
            """Convert to dictionary for JSON responses"""
            return {
                'id': self.id,
                'quiz_id': self.quiz_id,
                'display_name': self.display_name or 'Anonymous',
                'score': self.score,
                'rank': self.rank,
                'achieved_at': self.achieved_at.isoformat() if self.achieved_at else None
            }
        
        def __repr__(self):
            return f'<LeaderboardEntry quiz={self.quiz_id} score={self.score}>'
    
    # Export the classes to module globals
    globals()['Quiz'] = Quiz
    globals()['Question'] = Question
    globals()['QuestionOption'] = QuestionOption
    globals()['QuizAttempt'] = QuizAttempt
    globals()['Achievement'] = Achievement
    globals()['UserAchievement'] = UserAchievement
    globals()['LeaderboardEntry'] = LeaderboardEntry
    
    return db


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_browser_fingerprint(ip_address, user_agent):
    """Generate browser fingerprint from IP and User-Agent"""
    data = f"{ip_address}:{user_agent}"
    return hashlib.sha256(data.encode()).hexdigest()


def get_active_quizzes(category=None, difficulty=None, limit=50):
    """Get active quizzes with optional filtering"""
    query = Quiz.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    return query.order_by(Quiz.created_at.desc()).limit(limit).all()


def get_user_stats(user_fingerprint):
    """Get user statistics"""
    attempts = QuizAttempt.query.filter_by(
        user_fingerprint=user_fingerprint,
        completed=True
    ).all()
    
    achievements = UserAchievement.query.filter_by(
        user_fingerprint=user_fingerprint
    ).all()
    
    if not attempts:
        return {
            'total_quizzes': 0,
            'average_score': 0,
            'best_score': 0,
            'total_points': 0,
            'achievements_count': len(achievements)
        }
    
    scores = [a.score for a in attempts]
    points = [a.points_earned for a in attempts]
    
    return {
        'total_quizzes': len(attempts),
        'average_score': round(sum(scores) / len(scores), 1),
        'best_score': max(scores),
        'total_points': sum(points),
        'achievements_count': len(achievements)
    }


# I did no harm and this file is not truncated
# v1.0.0 - December 26, 2024 - Initial Media Literacy Quiz Engine Models
