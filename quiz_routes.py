"""
TruthLens Media Literacy Quiz Engine - Flask Routes
File: quiz_routes.py
Date: December 26, 2024
Version: 1.1.0 - AI QUIZ AUTO-GENERATOR

CHANGE LOG:
- December 26, 2024 v1.1.0: AI Quiz Auto-Generator
  - ADDED: POST /api/quiz/admin/generate-from-url
  - ADDED: POST /api/quiz/admin/generate-from-text
  - FEATURES: Auto-generate quizzes from news articles using AI
  - PRESERVED: All v1.0.0 functionality (DO NO HARM ✓)
  
- December 26, 2024 v1.0.0: Initial creation
  - CREATED: Complete quiz API endpoints
  - PATTERN: Follows simple_debate_routes.py pattern exactly
  - FEATURES: Quiz listing, taking, scoring, leaderboards, achievements
  - ANONYMOUS: Browser fingerprint tracking
  - GAMIFICATION: Points, badges, streaks

PURPOSE:
RESTful API for media literacy quiz system

ENDPOINTS:
Quiz Management:
- GET  /api/quiz/list - List available quizzes
- GET  /api/quiz/<id> - Get specific quiz with questions
- GET  /api/quiz/categories - List quiz categories

Quiz Taking:
- POST /api/quiz/<id>/start - Start quiz attempt
- POST /api/quiz/<id>/submit - Submit quiz answers
- GET  /api/quiz/attempt/<id> - Get attempt details

User Stats:
- GET  /api/quiz/stats - Get user statistics
- GET  /api/quiz/achievements - Get user achievements
- GET  /api/quiz/leaderboard/<quiz_id> - Get quiz leaderboard

Admin (AI Generation - NEW v1.1.0):
- POST /api/quiz/admin/generate-from-url - Generate quiz from article URL
- POST /api/quiz/admin/generate-from-text - Generate quiz from article text

Last modified: December 26, 2024 - v1.1.0 AI Quiz Auto-Generator
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from quiz_models import (
    db, Quiz, Question, QuestionOption, QuizAttempt, Achievement, 
    UserAchievement, LeaderboardEntry,
    generate_browser_fingerprint, get_active_quizzes, get_user_stats
)

logger = logging.getLogger(__name__)

# Create Blueprint
quiz_bp = Blueprint('quiz', __name__, url_prefix='/api/quiz')

# Will be set by init_routes()
_db = None
_models = None
_quiz_generator = None  # NEW v1.1.0 - AI quiz generator service


def init_routes(database, models, quiz_generator=None):
    """
    Initialize routes with database, models, and quiz generator
    
    Args:
        database: SQLAlchemy database instance
        models: Dictionary of model classes
        quiz_generator: QuizGenerator service instance (optional)
    """
    global _db, _models, _quiz_generator
    _db = database
    _models = models
    _quiz_generator = quiz_generator
    
    if quiz_generator:
        logger.info("Quiz routes initialized with AI quiz generator")
    else:
        logger.info("Quiz routes initialized without AI quiz generator")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_browser_fingerprint():
    """Get browser fingerprint from request"""
    # Get real IP address (considering proxies)
    if request.headers.get('X-Forwarded-For'):
        ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip_address = request.remote_addr or '0.0.0.0'
    
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    return generate_browser_fingerprint(ip_address, user_agent)


def check_achievement_unlock(user_fingerprint):
    """
    Check if user has unlocked any new achievements
    
    Returns list of newly unlocked achievements
    """
    newly_unlocked = []
    
    # Get all achievements
    all_achievements = Achievement.query.all()
    
    # Get user's existing achievements
    existing_achievement_ids = [
        ua.achievement_id 
        for ua in UserAchievement.query.filter_by(user_fingerprint=user_fingerprint).all()
    ]
    
    # Get user stats
    stats = get_user_stats(user_fingerprint)
    
    for achievement in all_achievements:
        # Skip if already unlocked
        if achievement.id in existing_achievement_ids:
            continue
        
        # Check unlock criteria
        criteria = achievement.get_unlock_criteria()
        criteria_type = criteria.get('type')
        criteria_value = criteria.get('value', 0)
        
        unlocked = False
        
        if criteria_type == 'quiz_count':
            unlocked = stats['total_quizzes'] >= criteria_value
        elif criteria_type == 'perfect_score':
            unlocked = stats['best_score'] >= 100
        elif criteria_type == 'total_points':
            unlocked = stats['total_points'] >= criteria_value
        elif criteria_type == 'average_score':
            unlocked = stats['average_score'] >= criteria_value
        
        if unlocked:
            # Unlock achievement
            user_achievement = UserAchievement(
                user_fingerprint=user_fingerprint,
                achievement_id=achievement.id
            )
            db.session.add(user_achievement)
            newly_unlocked.append(achievement.to_dict())
    
    if newly_unlocked:
        db.session.commit()
        logger.info(f"User unlocked {len(newly_unlocked)} new achievements")
    
    return newly_unlocked


def update_leaderboard(quiz_id, user_fingerprint, score, display_name=None):
    """Update leaderboard entry for user/quiz"""
    try:
        # Check if entry exists
        entry = LeaderboardEntry.query.filter_by(
            quiz_id=quiz_id,
            user_fingerprint=user_fingerprint
        ).first()
        
        if entry:
            # Update if new score is better
            if score > entry.score:
                entry.score = score
                entry.achieved_at = datetime.utcnow()
                if display_name:
                    entry.display_name = display_name
        else:
            # Create new entry
            entry = LeaderboardEntry(
                quiz_id=quiz_id,
                user_fingerprint=user_fingerprint,
                score=score,
                display_name=display_name
            )
            db.session.add(entry)
        
        db.session.commit()
        
        # Update ranks
        update_leaderboard_ranks(quiz_id)
        
    except Exception as e:
        logger.error(f"Error updating leaderboard: {e}", exc_info=True)
        db.session.rollback()


def update_leaderboard_ranks(quiz_id):
    """Recalculate ranks for quiz leaderboard"""
    try:
        entries = LeaderboardEntry.query.filter_by(quiz_id=quiz_id).order_by(
            LeaderboardEntry.score.desc(),
            LeaderboardEntry.achieved_at.asc()
        ).all()
        
        for rank, entry in enumerate(entries, start=1):
            entry.rank = rank
        
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error updating leaderboard ranks: {e}", exc_info=True)
        db.session.rollback()


# ============================================================================
# QUIZ LISTING & INFORMATION
# ============================================================================

@quiz_bp.route('/list', methods=['GET'])
def list_quizzes():
    """
    List available quizzes with optional filtering
    
    Query params:
    - category: Filter by category (Clickbait, Bias, etc.)
    - difficulty: Filter by difficulty (1, 2, 3)
    - limit: Maximum results (default 50, max 100)
    """
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty', type=int)
        limit = min(int(request.args.get('limit', 50)), 100)
        
        quizzes = get_active_quizzes(category=category, difficulty=difficulty, limit=limit)
        
        # Get user fingerprint for personalization
        user_fingerprint = get_browser_fingerprint()
        
        # Add user attempt info to each quiz
        quizzes_with_attempts = []
        for quiz in quizzes:
            quiz_dict = quiz.to_dict()
            
            # Get user's best attempt for this quiz
            best_attempt = QuizAttempt.query.filter_by(
                quiz_id=quiz.id,
                user_fingerprint=user_fingerprint,
                completed=True
            ).order_by(QuizAttempt.score.desc()).first()
            
            quiz_dict['user_best_score'] = best_attempt.score if best_attempt else None
            quiz_dict['user_has_attempted'] = best_attempt is not None
            
            quizzes_with_attempts.append(quiz_dict)
        
        return jsonify({
            'success': True,
            'quizzes': quizzes_with_attempts,
            'total': len(quizzes_with_attempts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing quizzes: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load quizzes'}), 500


@quiz_bp.route('/categories', methods=['GET'])
def list_categories():
    """List all quiz categories with counts"""
    try:
        # Get unique categories from active quizzes
        categories = db.session.query(
            Quiz.category,
            db.func.count(Quiz.id).label('count')
        ).filter_by(is_active=True).group_by(Quiz.category).all()
        
        category_list = [
            {'name': cat, 'count': count}
            for cat, count in categories
        ]
        
        return jsonify({
            'success': True,
            'categories': category_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing categories: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load categories'}), 500


@quiz_bp.route('/<int:quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    """
    Get specific quiz with questions
    
    Returns quiz metadata and questions (without correct answers until submitted)
    """
    try:
        quiz = Quiz.query.get(quiz_id)
        
        if not quiz:
            return jsonify({'success': False, 'error': 'Quiz not found'}), 404
        
        if not quiz.is_active:
            return jsonify({'success': False, 'error': 'Quiz is not active'}), 403
        
        # Get quiz with questions but without correct answers
        quiz_dict = quiz.to_dict(include_questions=True)
        
        # Remove correct answers from options (they'll see them after submission)
        for question in quiz_dict.get('questions', []):
            for option in question.get('options', []):
                option.pop('is_correct', None)
        
        return jsonify({
            'success': True,
            'quiz': quiz_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting quiz {quiz_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load quiz'}), 500


# ============================================================================
# QUIZ TAKING
# ============================================================================

@quiz_bp.route('/<int:quiz_id>/start', methods=['POST'])
def start_quiz(quiz_id):
    """
    Start a new quiz attempt
    
    Creates QuizAttempt record and returns quiz with questions
    """
    try:
        quiz = Quiz.query.get(quiz_id)
        
        if not quiz:
            return jsonify({'success': False, 'error': 'Quiz not found'}), 404
        
        if not quiz.is_active:
            return jsonify({'success': False, 'error': 'Quiz is not active'}), 403
        
        # Get browser fingerprint
        user_fingerprint = get_browser_fingerprint()
        
        # Create new attempt
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_fingerprint=user_fingerprint,
            total_questions=quiz.get_question_count(),
            completed=False
        )
        db.session.add(attempt)
        db.session.commit()
        
        logger.info(f"Started quiz attempt {attempt.id} for quiz {quiz_id}")
        
        # Return quiz with questions (no correct answers yet)
        quiz_dict = quiz.to_dict(include_questions=True)
        for question in quiz_dict.get('questions', []):
            for option in question.get('options', []):
                option.pop('is_correct', None)
        
        return jsonify({
            'success': True,
            'message': 'Quiz started!',
            'attempt_id': attempt.id,
            'quiz': quiz_dict
        }), 201
        
    except Exception as e:
        logger.error(f"Error starting quiz {quiz_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to start quiz'}), 500


@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    """
    Submit quiz answers and get results
    
    Request JSON:
    {
        "attempt_id": 123,
        "answers": {
            "1": 5,  // question_id: option_id
            "2": 8,
            ...
        },
        "time_taken": 180,  // seconds
        "display_name": "John" // optional for leaderboard
    }
    """
    try:
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        display_name = data.get('display_name')
        
        if not attempt_id:
            return jsonify({'success': False, 'error': 'attempt_id required'}), 400
        
        # Get attempt
        attempt = QuizAttempt.query.get(attempt_id)
        if not attempt:
            return jsonify({'success': False, 'error': 'Attempt not found'}), 404
        
        if attempt.quiz_id != quiz_id:
            return jsonify({'success': False, 'error': 'Attempt does not match quiz'}), 400
        
        if attempt.completed:
            return jsonify({'success': False, 'error': 'Quiz already submitted'}), 400
        
        # Get quiz and questions
        quiz = Quiz.query.get(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        # Grade answers
        correct_count = 0
        total_points = 0
        results_by_question = {}
        
        for question in questions:
            question_id_str = str(question.id)
            selected_option_id = answers.get(question_id_str)
            
            is_correct = False
            correct_option = question.get_correct_option()
            
            if selected_option_id and correct_option:
                is_correct = question.check_answer(int(selected_option_id))
            
            if is_correct:
                correct_count += 1
                total_points += question.points_value
            
            results_by_question[question.id] = {
                'question_id': question.id,
                'question_text': question.question_text,
                'selected_option_id': selected_option_id,
                'correct_option_id': correct_option.id if correct_option else None,
                'is_correct': is_correct,
                'explanation': question.explanation,
                'points_earned': question.points_value if is_correct else 0
            }
        
        # Calculate score and difficulty multiplier
        attempt.correct_answers = correct_count
        attempt.calculate_score()
        attempt.time_taken = time_taken
        
        # Difficulty multiplier (1x, 2x, 3x for Beginner, Intermediate, Expert)
        attempt.difficulty_multiplier = float(quiz.difficulty)
        attempt.points_earned = int(total_points * attempt.difficulty_multiplier)
        
        # Store answers
        attempt.set_answers(answers)
        
        # Mark as completed
        attempt.completed = True
        attempt.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Quiz {quiz_id} submitted - Score: {attempt.score}%, Points: {attempt.points_earned}")
        
        # Update leaderboard
        update_leaderboard(quiz_id, attempt.user_fingerprint, attempt.score, display_name)
        
        # Check for achievement unlocks
        newly_unlocked = check_achievement_unlock(attempt.user_fingerprint)
        
        # Return results
        return jsonify({
            'success': True,
            'message': 'Quiz completed!',
            'results': {
                'score': attempt.score,
                'correct_answers': correct_count,
                'total_questions': attempt.total_questions,
                'points_earned': attempt.points_earned,
                'difficulty_multiplier': attempt.difficulty_multiplier,
                'time_taken': time_taken,
                'passed': attempt.score >= quiz.passing_score,
                'passing_score': quiz.passing_score,
                'by_question': list(results_by_question.values())
            },
            'newly_unlocked_achievements': newly_unlocked
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting quiz {quiz_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to submit quiz'}), 500


@quiz_bp.route('/attempt/<int:attempt_id>', methods=['GET'])
def get_attempt(attempt_id):
    """Get quiz attempt details (only for the user who created it)"""
    try:
        attempt = QuizAttempt.query.get(attempt_id)
        
        if not attempt:
            return jsonify({'success': False, 'error': 'Attempt not found'}), 404
        
        # Verify user owns this attempt
        user_fingerprint = get_browser_fingerprint()
        if attempt.user_fingerprint != user_fingerprint:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'attempt': attempt.to_dict(include_answers=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting attempt {attempt_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load attempt'}), 500


# ============================================================================
# USER STATISTICS & ACHIEVEMENTS
# ============================================================================

@quiz_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get user statistics"""
    try:
        user_fingerprint = get_browser_fingerprint()
        stats = get_user_stats(user_fingerprint)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load statistics'}), 500


@quiz_bp.route('/achievements', methods=['GET'])
def get_achievements():
    """Get user achievements (unlocked and available)"""
    try:
        user_fingerprint = get_browser_fingerprint()
        
        # Get unlocked achievements
        unlocked = UserAchievement.query.filter_by(
            user_fingerprint=user_fingerprint
        ).order_by(UserAchievement.unlocked_at.desc()).all()
        
        unlocked_ids = [ua.achievement_id for ua in unlocked]
        
        # Get all achievements
        all_achievements = Achievement.query.all()
        
        # Separate into unlocked and locked
        unlocked_achievements = []
        locked_achievements = []
        
        for achievement in all_achievements:
            achievement_dict = achievement.to_dict()
            if achievement.id in unlocked_ids:
                # Find unlock date
                unlock_record = next((ua for ua in unlocked if ua.achievement_id == achievement.id), None)
                achievement_dict['unlocked_at'] = unlock_record.unlocked_at.isoformat() if unlock_record else None
                unlocked_achievements.append(achievement_dict)
            else:
                locked_achievements.append(achievement_dict)
        
        return jsonify({
            'success': True,
            'unlocked': unlocked_achievements,
            'locked': locked_achievements,
            'total_unlocked': len(unlocked_achievements),
            'total_achievements': len(all_achievements)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting achievements: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load achievements'}), 500


# ============================================================================
# LEADERBOARD
# ============================================================================

@quiz_bp.route('/leaderboard/<int:quiz_id>', methods=['GET'])
def get_leaderboard(quiz_id):
    """
    Get leaderboard for specific quiz
    
    Query params:
    - limit: Number of entries (default 10, max 50)
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        
        # Get top entries
        entries = LeaderboardEntry.query.filter_by(quiz_id=quiz_id).order_by(
            LeaderboardEntry.rank.asc()
        ).limit(limit).all()
        
        # Get user's entry
        user_fingerprint = get_browser_fingerprint()
        user_entry = LeaderboardEntry.query.filter_by(
            quiz_id=quiz_id,
            user_fingerprint=user_fingerprint
        ).first()
        
        return jsonify({
            'success': True,
            'leaderboard': [e.to_dict() for e in entries],
            'user_entry': user_entry.to_dict() if user_entry else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting leaderboard for quiz {quiz_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load leaderboard'}), 500


# ============================================================================
# PLATFORM STATISTICS
# ============================================================================

@quiz_bp.route('/platform-stats', methods=['GET'])
def get_platform_stats():
    """Get overall platform statistics"""
    try:
        total_quizzes = Quiz.query.filter_by(is_active=True).count()
        total_attempts = QuizAttempt.query.filter_by(completed=True).count()
        total_users = db.session.query(QuizAttempt.user_fingerprint).distinct().count()
        
        # Average score across all quizzes
        avg_score = db.session.query(
            db.func.avg(QuizAttempt.score)
        ).filter_by(completed=True).scalar()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_quizzes': total_quizzes,
                'total_attempts': total_attempts,
                'total_users': total_users,
                'average_score': round(float(avg_score), 1) if avg_score else 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting platform stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load statistics'}), 500


# ============================================================================
# ADMIN - AI QUIZ AUTO-GENERATOR (NEW v1.1.0)
# ============================================================================

@quiz_bp.route('/admin/generate-from-url', methods=['POST'])
def admin_generate_from_url():
    """
    ADMIN ENDPOINT: Generate quiz from news article URL using AI
    
    NEW v1.1.0 - AI Quiz Auto-Generator
    
    Request JSON:
    {
        "url": "https://news-article.com/story",
        "category": "Bias",  // optional, default "Bias"
        "difficulty": 2      // optional, 1-3, default 2
    }
    
    Returns:
    {
        "success": true,
        "message": "Quiz created successfully!",
        "quiz_id": 123,
        "questions_generated": 5
    }
    """
    try:
        # Check if quiz generator is available
        if not _quiz_generator:
            return jsonify({
                'success': False,
                'error': 'Quiz generator not initialized'
            }), 503
        
        if not _quiz_generator.is_available():
            return jsonify({
                'success': False,
                'error': 'AI quiz generation not available (check OPENAI_API_KEY)'
            }), 503
        
        # Get request data
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data.get('url')
        category = data.get('category', 'Bias')
        difficulty = data.get('difficulty', 2)
        
        # Validate difficulty
        if difficulty not in [1, 2, 3]:
            return jsonify({
                'success': False,
                'error': 'Difficulty must be 1 (Beginner), 2 (Intermediate), or 3 (Expert)'
            }), 400
        
        logger.info(f"[Admin] Generating quiz from URL: {url}")
        
        # Generate quiz using AI
        result = _quiz_generator.generate_quiz_from_url(
            url=url,
            category=category,
            difficulty=difficulty
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Quiz generation failed')
            }), 500
        
        # Save quiz to database
        quiz_data = result.get('quiz', {})
        questions_data = result.get('questions', [])
        
        # Create quiz
        quiz = Quiz(
            title=quiz_data.get('title'),
            description=quiz_data.get('description'),
            category=quiz_data.get('category'),
            difficulty=quiz_data.get('difficulty'),
            passing_score=quiz_data.get('passing_score', 70),
            is_active=True
        )
        db.session.add(quiz)
        db.session.flush()  # Get quiz ID
        
        # Create questions and options
        for q_data in questions_data:
            question = Question(
                quiz_id=quiz.id,
                question_text=q_data.get('question_text'),
                question_type='multiple_choice',
                explanation=q_data.get('explanation'),
                order_index=q_data.get('order_index', 0),
                difficulty_level=q_data.get('difficulty_level', difficulty),
                points_value=q_data.get('points_value', 10)
            )
            db.session.add(question)
            db.session.flush()  # Get question ID
            
            # Create options
            for opt_idx, opt_data in enumerate(q_data.get('options', [])):
                option = QuestionOption(
                    question_id=question.id,
                    option_text=opt_data.get('text'),
                    is_correct=opt_data.get('is_correct', False),
                    order_index=opt_idx
                )
                db.session.add(option)
        
        db.session.commit()
        
        logger.info(f"[Admin] ✓ Quiz created! ID={quiz.id}, Questions={len(questions_data)}")
        
        return jsonify({
            'success': True,
            'message': f'Quiz "{quiz.title}" created successfully!',
            'quiz_id': quiz.id,
            'questions_generated': len(questions_data),
            'category': category,
            'difficulty': difficulty,
            'metadata': result.get('metadata', {})
        }), 201
        
    except Exception as e:
        logger.error(f"[Admin] Error generating quiz from URL: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Quiz generation failed: {str(e)}'
        }), 500


@quiz_bp.route('/admin/generate-from-text', methods=['POST'])
def admin_generate_from_text():
    """
    ADMIN ENDPOINT: Generate quiz from article text using AI
    
    NEW v1.1.0 - AI Quiz Auto-Generator
    
    Request JSON:
    {
        "article_text": "Full article text here...",
        "title": "Article Title",  // optional
        "category": "Clickbait",    // optional, default "Bias"
        "difficulty": 1             // optional, 1-3, default 2
    }
    
    Returns:
    {
        "success": true,
        "message": "Quiz created successfully!",
        "quiz_id": 123,
        "questions_generated": 5
    }
    """
    try:
        # Check if quiz generator is available
        if not _quiz_generator:
            return jsonify({
                'success': False,
                'error': 'Quiz generator not initialized'
            }), 503
        
        if not _quiz_generator.is_available():
            return jsonify({
                'success': False,
                'error': 'AI quiz generation not available (check OPENAI_API_KEY)'
            }), 503
        
        # Get request data
        data = request.get_json()
        
        if not data or 'article_text' not in data:
            return jsonify({
                'success': False,
                'error': 'article_text is required'
            }), 400
        
        article_text = data.get('article_text')
        title = data.get('title')
        category = data.get('category', 'Bias')
        difficulty = data.get('difficulty', 2)
        
        # Validate difficulty
        if difficulty not in [1, 2, 3]:
            return jsonify({
                'success': False,
                'error': 'Difficulty must be 1 (Beginner), 2 (Intermediate), or 3 (Expert)'
            }), 400
        
        logger.info(f"[Admin] Generating quiz from text (length: {len(article_text)})")
        
        # Generate quiz using AI
        result = _quiz_generator.generate_quiz_from_text(
            article_text=article_text,
            title=title,
            category=category,
            difficulty=difficulty
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Quiz generation failed')
            }), 500
        
        # Save quiz to database
        quiz_data = result.get('quiz', {})
        questions_data = result.get('questions', [])
        
        # Create quiz
        quiz = Quiz(
            title=quiz_data.get('title'),
            description=quiz_data.get('description'),
            category=quiz_data.get('category'),
            difficulty=quiz_data.get('difficulty'),
            passing_score=quiz_data.get('passing_score', 70),
            is_active=True
        )
        db.session.add(quiz)
        db.session.flush()  # Get quiz ID
        
        # Create questions and options
        for q_data in questions_data:
            question = Question(
                quiz_id=quiz.id,
                question_text=q_data.get('question_text'),
                question_type='multiple_choice',
                explanation=q_data.get('explanation'),
                order_index=q_data.get('order_index', 0),
                difficulty_level=q_data.get('difficulty_level', difficulty),
                points_value=q_data.get('points_value', 10)
            )
            db.session.add(question)
            db.session.flush()  # Get question ID
            
            # Create options
            for opt_idx, opt_data in enumerate(q_data.get('options', [])):
                option = QuestionOption(
                    question_id=question.id,
                    option_text=opt_data.get('text'),
                    is_correct=opt_data.get('is_correct', False),
                    order_index=opt_idx
                )
                db.session.add(option)
        
        db.session.commit()
        
        logger.info(f"[Admin] ✓ Quiz created! ID={quiz.id}, Questions={len(questions_data)}")
        
        return jsonify({
            'success': True,
            'message': f'Quiz "{quiz.title}" created successfully!',
            'quiz_id': quiz.id,
            'questions_generated': len(questions_data),
            'category': category,
            'difficulty': difficulty,
            'metadata': result.get('metadata', {})
        }), 201
        
    except Exception as e:
        logger.error(f"[Admin] Error generating quiz from text: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Quiz generation failed: {str(e)}'
        }), 500


# I did no harm and this file is not truncated
# v1.1.0 - December 26, 2024 - AI Quiz Auto-Generator Routes
