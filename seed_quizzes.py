"""
Quiz Database Seeder
File: seed_quizzes.py
Date: December 26, 2024
Version: 1.0.0

PURPOSE:
Simple script to populate the quiz database with sample content.
Upload this file to your GitHub repo, then visit /admin/seed-quizzes once.

USAGE:
1. Upload this file to your GitHub repo (project root)
2. Render will auto-deploy
3. Visit: https://news-analyzer-qtgb.onrender.com/admin/seed-quizzes
4. Done! Quizzes are loaded.

Last modified: December 26, 2024 - v1.0.0
"""

from flask import jsonify
from datetime import datetime

def seed_quiz_data(db, Quiz, Question, QuestionOption, Achievement):
    """
    Seed the database with sample quiz content
    
    Returns dict with success status and details
    """
    try:
        results = {
            'quizzes_added': 0,
            'questions_added': 0,
            'options_added': 0,
            'achievements_added': 0,
            'errors': []
        }
        
        # Check if quizzes already exist
        existing_quizzes = Quiz.query.count()
        if existing_quizzes > 0:
            return {
                'success': False,
                'message': f'Database already has {existing_quizzes} quizzes. Delete them first if you want to re-seed.',
                'existing_count': existing_quizzes
            }
        
        # =====================================================================
        # QUIZ 1: Clickbait Detection 101 (Beginner)
        # =====================================================================
        
        quiz1 = Quiz(
            title='Clickbait Detection 101',
            description='Learn to spot sensational headlines that prioritize clicks over accuracy. Master the art of identifying curiosity gaps and emotional manipulation.',
            category='Clickbait',
            difficulty=1,
            passing_score=70,
            is_active=True
        )
        db.session.add(quiz1)
        db.session.flush()  # Get quiz ID
        results['quizzes_added'] += 1
        
        # Question 1
        q1 = Question(
            quiz_id=quiz1.id,
            question_text='Which headline is clickbait?',
            question_type='multiple_choice',
            explanation='Clickbait uses sensational language like "You won\'t BELIEVE" to create curiosity gaps rather than inform. It prioritizes emotional reaction over accuracy.',
            order_index=0,
            difficulty_level=1,
            points_value=10
        )
        db.session.add(q1)
        db.session.flush()
        results['questions_added'] += 1
        
        options = [
            QuestionOption(question_id=q1.id, option_text='Study finds link between sleep and health', is_correct=False, order_index=0),
            QuestionOption(question_id=q1.id, option_text='You won\'t BELIEVE what scientists discovered about sleep!', is_correct=True, order_index=1),
            QuestionOption(question_id=q1.id, option_text='Research examines sleep patterns in adults', is_correct=False, order_index=2),
            QuestionOption(question_id=q1.id, option_text='Sleep study published in medical journal', is_correct=False, order_index=3)
        ]
        for opt in options:
            db.session.add(opt)
            results['options_added'] += 1
        
        # Question 2
        q2 = Question(
            quiz_id=quiz1.id,
            question_text='What is a "curiosity gap" in clickbait?',
            question_type='multiple_choice',
            explanation='A curiosity gap withholds crucial information to make you click. For example, "This ONE trick..." tells you there\'s a trick but not what it is.',
            order_index=1,
            difficulty_level=1,
            points_value=10
        )
        db.session.add(q2)
        db.session.flush()
        results['questions_added'] += 1
        
        options = [
            QuestionOption(question_id=q2.id, option_text='A gap in the journalist\'s research', is_correct=False, order_index=0),
            QuestionOption(question_id=q2.id, option_text='Withholding information to create suspense and force clicks', is_correct=True, order_index=1),
            QuestionOption(question_id=q2.id, option_text='A pause between publishing articles', is_correct=False, order_index=2),
            QuestionOption(question_id=q2.id, option_text='Empty space in the webpage layout', is_correct=False, order_index=3)
        ]
        for opt in options:
            db.session.add(opt)
            results['options_added'] += 1
        
        # Question 3
        q3 = Question(
            quiz_id=quiz1.id,
            question_text='Which phrase is commonly used in clickbait?',
            question_type='multiple_choice',
            explanation='Clickbait often uses phrases like "Number 7 will SHOCK you" to create artificial urgency and curiosity.',
            order_index=2,
            difficulty_level=1,
            points_value=10
        )
        db.session.add(q3)
        db.session.flush()
        results['questions_added'] += 1
        
        options = [
            QuestionOption(question_id=q3.id, option_text='According to the study...', is_correct=False, order_index=0),
            QuestionOption(question_id=q3.id, option_text='Researchers found that...', is_correct=False, order_index=1),
            QuestionOption(question_id=q3.id, option_text='Number 7 will SHOCK you!', is_correct=True, order_index=2),
            QuestionOption(question_id=q3.id, option_text='The data shows...', is_correct=False, order_index=3)
        ]
        for opt in options:
            db.session.add(opt)
            results['options_added'] += 1
        
        # =====================================================================
        # QUIZ 2: Bias Spotting 101 (Intermediate)
        # =====================================================================
        
        quiz2 = Quiz(
            title='Bias Spotting 101',
            description='Learn to identify subtle and not-so-subtle bias in news coverage. Understand loaded language, framing, and selective reporting.',
            category='Bias',
            difficulty=2,
            passing_score=70,
            is_active=True
        )
        db.session.add(quiz2)
        db.session.flush()
        results['quizzes_added'] += 1
        
        # Question 1
        q4 = Question(
            quiz_id=quiz2.id,
            question_text='Which word reveals bias in: "Politicians CLAIM economy is improving"',
            question_type='multiple_choice',
            explanation='"CLAIM" suggests doubt or skepticism. A neutral alternative would be "report" or "state." This is called loaded language.',
            order_index=0,
            difficulty_level=2,
            points_value=20
        )
        db.session.add(q4)
        db.session.flush()
        results['questions_added'] += 1
        
        options = [
            QuestionOption(question_id=q4.id, option_text='Politicians', is_correct=False, order_index=0),
            QuestionOption(question_id=q4.id, option_text='CLAIM', is_correct=True, order_index=1),
            QuestionOption(question_id=q4.id, option_text='Economy', is_correct=False, order_index=2),
            QuestionOption(question_id=q4.id, option_text='Improving', is_correct=False, order_index=3)
        ]
        for opt in options:
            db.session.add(opt)
            results['options_added'] += 1
        
        # Question 2
        q5 = Question(
            quiz_id=quiz2.id,
            question_text='Compare: "Freedom fighters defend territory" vs "Rebels occupy region". Same event, different framing. Which is more sympathetic?',
            question_type='multiple_choice',
            explanation='"Freedom fighters" carries positive connotations while "rebels" and "occupy" sound more negative. This is emotional framing in action.',
            order_index=1,
            difficulty_level=2,
            points_value=20
        )
        db.session.add(q5)
        db.session.flush()
        results['questions_added'] += 1
        
        options = [
            QuestionOption(question_id=q5.id, option_text='First headline (Freedom fighters)', is_correct=True, order_index=0),
            QuestionOption(question_id=q5.id, option_text='Second headline (Rebels)', is_correct=False, order_index=1),
            QuestionOption(question_id=q5.id, option_text='Both are equally neutral', is_correct=False, order_index=2),
            QuestionOption(question_id=q5.id, option_text='Neither shows bias', is_correct=False, order_index=3)
        ]
        for opt in options:
            db.session.add(opt)
            results['options_added'] += 1
        
        # =====================================================================
        # ACHIEVEMENTS
        # =====================================================================
        
        achievements_data = [
            {
                'name': 'First Quiz',
                'description': 'Complete your first quiz',
                'badge_icon': '🎓',
                'category': 'Beginner',
                'points_value': 10,
                'unlock_criteria': '{"type": "quiz_count", "value": 1}'
            },
            {
                'name': 'Perfect Score',
                'description': 'Get 100% on any quiz',
                'badge_icon': '⭐',
                'category': 'Intermediate',
                'points_value': 50,
                'unlock_criteria': '{"type": "perfect_score", "value": 100}'
            },
            {
                'name': 'Bias Detector',
                'description': 'Average score above 80%',
                'badge_icon': '🔍',
                'category': 'Intermediate',
                'points_value': 30,
                'unlock_criteria': '{"type": "average_score", "value": 80}'
            },
            {
                'name': 'Quiz Master',
                'description': 'Complete 10 quizzes',
                'badge_icon': '👑',
                'category': 'Expert',
                'points_value': 100,
                'unlock_criteria': '{"type": "quiz_count", "value": 10}'
            }
        ]
        
        for ach_data in achievements_data:
            achievement = Achievement(**ach_data)
            db.session.add(achievement)
            results['achievements_added'] += 1
        
        # Commit all changes
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Quiz database seeded successfully!',
            'results': results
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to seed quiz database'
        }


# I did no harm and this file is not truncated
# v1.0.0 - December 26, 2024 - Quiz Database Seeder
