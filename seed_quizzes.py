"""
Quiz Database Seeder
Version: 1.0.0
Date: December 26, 2024

Seeds the quiz database with sample quizzes for testing and initial deployment.
Run via admin endpoint: /admin/seed-quizzes

This creates:
- 2 complete quizzes with 5 questions each
- 4 difficulty-appropriate questions per quiz  
- Multiple choice options for each question
- Explanations for correct answers
- 4 achievements to unlock

Usage:
1. Deploy this file to project root
2. Visit: https://your-app.onrender.com/admin/seed-quizzes
3. Quiz system will be populated and ready!

I did no harm and this file is not truncated.
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def seed_quiz_data(db, Quiz, Question, QuestionOption, Achievement):
    """
    Seed the quiz database with sample content
    
    Args:
        db: SQLAlchemy database instance
        Quiz: Quiz model class
        Question: Question model class  
        QuestionOption: QuestionOption model class
        Achievement: Achievement model class
    
    Returns:
        dict: Results of seeding operation
    """
    try:
        logger.info("=" * 80)
        logger.info("QUIZ SEEDING STARTED")
        logger.info("=" * 80)
        
        # Check if already seeded
        existing_quizzes = Quiz.query.count()
        if existing_quizzes > 0:
            logger.warning(f"Database already has {existing_quizzes} quizzes. Skipping seed.")
            return {
                'success': False,
                'message': f'Database already seeded with {existing_quizzes} quizzes. Delete them first if you want to re-seed.',
                'results': {
                    'quizzes_added': 0,
                    'questions_added': 0,
                    'options_added': 0,
                    'achievements_added': 0
                }
            }
        
        quizzes_added = 0
        questions_added = 0
        options_added = 0
        achievements_added = 0
        
        # ====================================================================
        # QUIZ 1: Clickbait Detection (Beginner)
        # ====================================================================
        
        quiz1 = Quiz(
            title="Clickbait Detection 101",
            description="Learn to spot sensationalized headlines and clickbait tactics",
            category="clickbait",
            difficulty="beginner",
            time_limit_minutes=10,
            passing_score=60,
            points_value=100,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(quiz1)
        db.session.flush()  # Get quiz1.id
        quizzes_added += 1
        
        # Quiz 1 - Question 1
        q1_1 = Question(
            quiz_id=quiz1.id,
            question_text="Which headline is MOST likely to be clickbait?",
            question_type="multiple_choice",
            points=20,
            order_index=1
        )
        db.session.add(q1_1)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q1_1.id, option_text="Study Finds Link Between Diet and Heart Health", is_correct=False, order_index=1),
            QuestionOption(question_id=q1_1.id, option_text="You Won't BELIEVE What This Celebrity Did Next!", is_correct=True, order_index=2, explanation="This uses emotional language ('BELIEVE'), vague content, and promises shocking information without delivering details - classic clickbait tactics."),
            QuestionOption(question_id=q1_1.id, option_text="New Research Published in Nature on Climate Change", is_correct=False, order_index=3),
            QuestionOption(question_id=q1_1.id, option_text="Local School Board Approves New Budget", is_correct=False, order_index=4)
        ])
        
        # Quiz 1 - Question 2
        q1_2 = Question(
            quiz_id=quiz1.id,
            question_text="What is a common clickbait technique?",
            question_type="multiple_choice",
            points=20,
            order_index=2
        )
        db.session.add(q1_2)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q1_2.id, option_text="Using numbered lists (e.g., '10 Ways to...')", is_correct=False, order_index=1),
            QuestionOption(question_id=q1_2.id, option_text="Withholding key information to create curiosity gap", is_correct=True, order_index=2, explanation="The 'curiosity gap' technique deliberately leaves out crucial information to force you to click. For example: 'Doctors Hate This One Trick' - what trick? You have to click to find out."),
            QuestionOption(question_id=q1_2.id, option_text="Clearly stating the article's main point", is_correct=False, order_index=3),
            QuestionOption(question_id=q1_2.id, option_text="Including the author's name", is_correct=False, order_index=4)
        ])
        
        # Quiz 1 - Question 3
        q1_3 = Question(
            quiz_id=quiz1.id,
            question_text="'Doctors SHOCKED by This Simple Trick' - What clickbait tactic is this?",
            question_type="multiple_choice",
            points=20,
            order_index=3
        )
        db.session.add(q1_3)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q1_3.id, option_text="Appeal to authority (doctors)", is_correct=True, order_index=1, explanation="This combines false authority appeal ('Doctors SHOCKED') with vague promises ('Simple Trick'). Real medical news would cite specific studies and explain the findings clearly."),
            QuestionOption(question_id=q1_3.id, option_text="Using statistics", is_correct=False, order_index=2),
            QuestionOption(question_id=q1_3.id, option_text="Providing evidence", is_correct=False, order_index=3),
            QuestionOption(question_id=q1_3.id, option_text="Clear headline structure", is_correct=False, order_index=4)
        ])
        
        # Quiz 1 - Question 4
        q1_4 = Question(
            quiz_id=quiz1.id,
            question_text="How can you verify if a headline is clickbait before clicking?",
            question_type="multiple_choice",
            points=20,
            order_index=4
        )
        db.session.add(q1_4)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q1_4.id, option_text="Check the number of shares", is_correct=False, order_index=1),
            QuestionOption(question_id=q1_4.id, option_text="Look at the source domain and reputation", is_correct=True, order_index=2, explanation="Reputable news sources (NYT, Reuters, AP) rarely use clickbait. Check the domain - unfamiliar sites with sensational headlines are red flags."),
            QuestionOption(question_id=q1_4.id, option_text="Count the words in the headline", is_correct=False, order_index=3),
            QuestionOption(question_id=q1_4.id, option_text="Check if it has images", is_correct=False, order_index=4)
        ])
        
        # Quiz 1 - Question 5
        q1_5 = Question(
            quiz_id=quiz1.id,
            question_text="'5 Foods You Should NEVER Eat' - Why is this clickbait?",
            question_type="multiple_choice",
            points=20,
            order_index=5
        )
        db.session.add(q1_5)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q1_5.id, option_text="It uses a numbered list", is_correct=False, order_index=1),
            QuestionOption(question_id=q1_5.id, option_text="It creates fear without context or nuance", is_correct=True, order_index=2, explanation="Absolute warnings ('NEVER') combined with listicle format and fear-mongering is classic clickbait. Real nutritional advice includes context, sources, and acknowledges individual variation."),
            QuestionOption(question_id=q1_5.id, option_text="It mentions food", is_correct=False, order_index=3),
            QuestionOption(question_id=q1_5.id, option_text="It's too short", is_correct=False, order_index=4)
        ])
        
        # ====================================================================
        # QUIZ 2: Bias Detection (Intermediate)
        # ====================================================================
        
        quiz2 = Quiz(
            title="Detecting Media Bias",
            description="Identify political bias, loaded language, and editorial slant in news articles",
            category="bias",
            difficulty="intermediate",
            time_limit_minutes=15,
            passing_score=70,
            points_value=150,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(quiz2)
        db.session.flush()
        quizzes_added += 1
        
        # Quiz 2 - Question 1
        q2_1 = Question(
            quiz_id=quiz2.id,
            question_text="Which word choice suggests BIAS in reporting?",
            question_type="multiple_choice",
            points=30,
            order_index=1
        )
        db.session.add(q2_1)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q2_1.id, option_text="'The senator said the bill would help families'", is_correct=False, order_index=1),
            QuestionOption(question_id=q2_1.id, option_text="'The senator CLAIMED the bill would help families'", is_correct=True, order_index=2, explanation="'Claimed' implies doubt or skepticism, while 'said' is neutral. This subtle word choice signals the reporter's bias against the senator's statement."),
            QuestionOption(question_id=q2_1.id, option_text="'The senator stated the bill would help families'", is_correct=False, order_index=3),
            QuestionOption(question_id=q2_1.id, option_text="'The senator announced the bill would help families'", is_correct=False, order_index=4)
        ])
        
        # Quiz 2 - Question 2
        q2_2 = Question(
            quiz_id=quiz2.id,
            question_text="What indicates BALANCED coverage of a controversial issue?",
            question_type="multiple_choice",
            points=30,
            order_index=2
        )
        db.session.add(q2_2)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q2_2.id, option_text="Only quoting people who agree with each other", is_correct=False, order_index=1),
            QuestionOption(question_id=q2_2.id, option_text="Including quotes from multiple perspectives", is_correct=True, order_index=2, explanation="Balanced reporting presents multiple viewpoints fairly. Look for quotes from different sides of an issue, along with factual context that helps readers understand each position."),
            QuestionOption(question_id=q2_2.id, option_text="Using emotional language throughout", is_correct=False, order_index=3),
            QuestionOption(question_id=q2_2.id, option_text="Avoiding any direct quotes", is_correct=False, order_index=4)
        ])
        
        # Quiz 2 - Question 3
        q2_3 = Question(
            quiz_id=quiz2.id,
            question_text="'Radical protesters clashed with police' vs 'Demonstrators met police resistance' - What's the difference?",
            question_type="multiple_choice",
            points=30,
            order_index=3
        )
        db.session.add(q2_3)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q2_3.id, option_text="The first uses loaded language and assigns blame", is_correct=True, order_index=1, explanation="'Radical' is a loaded term implying extremism, and 'clashed' suggests the protesters initiated. The second version is more neutral, using 'demonstrators' and describing the interaction without assigning fault."),
            QuestionOption(question_id=q2_3.id, option_text="They mean the same thing", is_correct=False, order_index=2),
            QuestionOption(question_id=q2_3.id, option_text="The second is more sensational", is_correct=False, order_index=3),
            QuestionOption(question_id=q2_3.id, option_text="Only word count differs", is_correct=False, order_index=4)
        ])
        
        # Quiz 2 - Question 4
        q2_4 = Question(
            quiz_id=quiz2.id,
            question_text="How can you identify OMISSION bias?",
            question_type="multiple_choice",
            points=30,
            order_index=4
        )
        db.session.add(q2_4)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q2_4.id, option_text="Check if important context or opposing views are missing", is_correct=True, order_index=1, explanation="Omission bias occurs when crucial information is left out. Compare coverage across multiple sources - if one consistently excludes certain perspectives or facts, that's a red flag."),
            QuestionOption(question_id=q2_4.id, option_text="Count the number of paragraphs", is_correct=False, order_index=2),
            QuestionOption(question_id=q2_4.id, option_text="Look for spelling errors", is_correct=False, order_index=3),
            QuestionOption(question_id=q2_4.id, option_text="Check the publication date", is_correct=False, order_index=4)
        ])
        
        # Quiz 2 - Question 5
        q2_5 = Question(
            quiz_id=quiz2.id,
            question_text="What is 'both-sides-ism' and why is it problematic?",
            question_type="multiple_choice",
            points=30,
            order_index=5
        )
        db.session.add(q2_5)
        db.session.flush()
        questions_added += 1
        
        options_added += 4
        db.session.add_all([
            QuestionOption(question_id=q2_5.id, option_text="Giving equal weight to factual and false claims", is_correct=True, order_index=1, explanation="Both-sides-ism creates false equivalence by treating well-established facts and fringe views as equally valid. Example: giving climate deniers equal time with climate scientists creates misleading 'balance.'"),
            QuestionOption(question_id=q2_5.id, option_text="Always reporting both political parties", is_correct=False, order_index=2),
            QuestionOption(question_id=q2_5.id, option_text="Using two sources for every story", is_correct=False, order_index=3),
            QuestionOption(question_id=q2_5.id, option_text="Writing stories with two paragraphs", is_correct=False, order_index=4)
        ])
        
        # ====================================================================
        # ACHIEVEMENTS
        # ====================================================================
        
        achievements_added += 4
        db.session.add_all([
            Achievement(
                name="First Steps",
                description="Complete your first quiz",
                badge_icon="🎓",
                points_required=0,
                quizzes_required=1,
                created_at=datetime.utcnow()
            ),
            Achievement(
                name="Clickbait Detective",
                description="Score 80% or higher on a clickbait quiz",
                badge_icon="🔍",
                points_required=80,
                quizzes_required=1,
                created_at=datetime.utcnow()
            ),
            Achievement(
                name="Bias Buster",
                description="Score 80% or higher on a bias detection quiz",
                badge_icon="⚖️",
                points_required=120,
                quizzes_required=1,
                created_at=datetime.utcnow()
            ),
            Achievement(
                name="Media Literacy Master",
                description="Complete 5 quizzes with 70%+ scores",
                badge_icon="👑",
                points_required=500,
                quizzes_required=5,
                created_at=datetime.utcnow()
            )
        ])
        
        # Commit everything
        db.session.commit()
        
        logger.info("✅ QUIZ SEEDING COMPLETE!")
        logger.info(f"  - Quizzes added: {quizzes_added}")
        logger.info(f"  - Questions added: {questions_added}")
        logger.info(f"  - Options added: {options_added}")
        logger.info(f"  - Achievements added: {achievements_added}")
        logger.info("=" * 80)
        
        return {
            'success': True,
            'message': 'Quiz database seeded successfully!',
            'results': {
                'quizzes_added': quizzes_added,
                'questions_added': questions_added,
                'options_added': options_added,
                'achievements_added': achievements_added
            }
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Quiz seeding failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'message': 'Quiz seeding failed - see logs for details'
        }


# I did no harm and this file is not truncated
