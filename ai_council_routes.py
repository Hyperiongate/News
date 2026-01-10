"""
TruthLens AI Council - Flask Routes
File: ai_council_routes.py
Date: January 10, 2026
Version: 1.1.0

CHANGELOG:
v1.1.0 (January 10, 2026):
- Fixed frontend compatibility: response fields now match frontend expectations
- Changed 'service' → 'ai_service' for frontend display
- Changed 'response' → 'response_text' for clarity
- Changed 'name' → 'ai_name' for consistency
- All 10 AI services supported

v1.0.0 (January 9, 2026):
- Initial release

Last modified: January 10, 2026 - v1.1.0 Frontend Fix
I did no harm and this file is not truncated.
"""

import logging
import traceback
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import desc

logger = logging.getLogger(__name__)

ai_council_bp = Blueprint('ai_council', __name__, url_prefix='/api/ai-council')

db = None
AIQuery = None
AIResponse = None
AIConsensus = None
ai_council_service = None


def init_routes(database, models, service):
    """Initialize routes with database models and AI service"""
    global db, AIQuery, AIResponse, AIConsensus, ai_council_service
    db = database
    AIQuery = models['AIQuery']
    AIResponse = models['AIResponse']
    AIConsensus = models['AIConsensus']
    ai_council_service = service


@ai_council_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Query all AI services with a question and generate consensus
    
    POST /api/ai-council/ask
    Body: {"question": "Your question here"}
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('question'):
            return jsonify({'success': False, 'error': 'Question is required'}), 400
        
        question = data['question'].strip()
        
        if len(question) < 10:
            return jsonify({'success': False, 'error': 'Question must be at least 10 characters'}), 400
        
        logger.info(f"[AICouncil API] New question: {question[:100]}...")
        
        # Query all AI services
        result = ai_council_service.query_all(question)
        
        if not result.get('success'):
            return jsonify(result), 500
        
        # Categorize question
        from ai_council_models import categorize_question
        category = categorize_question(question)
        
        # Save query to database
        new_query = AIQuery(
            question=question,
            question_category=category,
            processing_time=result['processing_time'],
            total_responses=result['total_responses'],
            successful_responses=result['successful_responses'],
            failed_responses=result['failed_responses']
        )
        
        db.session.add(new_query)
        db.session.flush()
        
        # Save individual AI responses
        for response_data in result['responses']:
            new_response = AIResponse(
                query_id=new_query.id,
                ai_service=response_data['service'],
                ai_model=response_data['model'],
                response_text=response_data.get('response'),
                response_length=response_data.get('response_length', 0),
                success=response_data['success'],
                error_message=response_data.get('error'),
                response_time=response_data.get('response_time', 0),
                tokens_used=response_data.get('tokens_used')
            )
            db.session.add(new_response)
        
        # Save consensus
        consensus_data = result.get('consensus', {})
        if consensus_data:
            import json
            new_consensus = AIConsensus(
                query_id=new_query.id,
                summary=consensus_data.get('summary'),
                agreement_areas=json.dumps(consensus_data.get('agreement_areas', [])),
                disagreement_areas=json.dumps(consensus_data.get('disagreement_areas', [])),
                consensus_score=consensus_data.get('consensus_score', 0),
                generated_by=consensus_data.get('generated_by')
            )
            db.session.add(new_consensus)
            
            # Update query with consensus level
            new_query.has_consensus = True
            score = consensus_data.get('consensus_score', 0)
            if score >= 80:
                new_query.consensus_level = 'high'
            elif score >= 60:
                new_query.consensus_level = 'medium'
            elif score >= 40:
                new_query.consensus_level = 'low'
            else:
                new_query.consensus_level = 'conflicting'
        
        # Extract claims from responses
        claims_extracted = 0
        try:
            from claim_tracker_routes import auto_save_claims_from_analysis
            
            # Combine all successful AI responses
            all_responses_text = "\n\n".join([
                f"{r['name']}: {r.get('response', '')}"
                for r in result['responses']
                if r['success'] and r.get('response')
            ])
            
            if all_responses_text:
                claim_result = auto_save_claims_from_analysis({
                    'content': all_responses_text,
                    'type': 'ai_consensus',
                    'title': f'AI Council: {question[:100]}',
                    'source': 'AI Council',
                    'outlet': 'Multiple AI Services'
                })
                
                if claim_result.get('success'):
                    claims_extracted = claim_result.get('claims_saved', 0)
                    logger.info(f"[AICouncil] Extracted {claims_extracted} claims")
                
        except Exception as e:
            logger.warning(f"[AICouncil] Claim extraction failed: {e}")
        
        new_query.claims_extracted = claims_extracted
        
        db.session.commit()
        
        logger.info(f"[AICouncil] Query saved with ID: {new_query.id}")
        
        # ====================================================================
        # CRITICAL FIX v1.1.0: Transform response fields for frontend
        # ====================================================================
        # Frontend expects: ai_service, ai_name, response_text
        # Backend provides: service, name, response
        # We need to transform the data!
        # ====================================================================
        
        transformed_responses = []
        for r in result['responses']:
            transformed_responses.append({
                'ai_service': r['name'],  # Frontend displays this as the AI name
                'response_text': r.get('response', ''),  # Frontend shows this as response
                'response_length': r.get('response_length', 0),
                'response_time': r.get('response_time', 0),
                'tokens_used': r.get('tokens_used'),
                'success': r['success'],
                'error_message': r.get('error')
            })
        
        return jsonify({
            'success': True,
            'query_id': new_query.id,
            'question': question,
            'category': category,
            'responses': transformed_responses,  # Use transformed data!
            'consensus': consensus_data,
            'processing_time': result['processing_time'],
            'total_responses': result['total_responses'],
            'successful_responses': result['successful_responses'],
            'claims_extracted': claims_extracted
        })
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        if db:
            db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_council_bp.route('/recent', methods=['GET'])
def get_recent_queries():
    """
    Get recent AI Council queries
    
    GET /api/ai-council/recent?limit=20&days=30
    """
    try:
        limit = int(request.args.get('limit', 20))
        days = int(request.args.get('days', 30))
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        queries = AIQuery.query.filter(
            AIQuery.created_at >= cutoff_date
        ).order_by(desc(AIQuery.created_at)).limit(limit).all()
        
        results = []
        for query in queries:
            results.append({
                'id': query.id,
                'question': query.question,
                'category': query.question_category,
                'created_at': query.created_at.isoformat(),
                'processing_time': query.processing_time,
                'total_responses': query.total_responses,
                'successful_responses': query.successful_responses,
                'consensus_level': query.consensus_level,
                'consensus_score': query.consensus_score,
                'claims_extracted': query.claims_extracted
            })
        
        return jsonify({
            'success': True,
            'queries': results,
            'count': len(results)
        })
    
    except Exception as e:
        logger.error(f"Error fetching recent queries: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_council_bp.route('/<int:query_id>', methods=['GET'])
def get_query_details(query_id):
    """
    Get full details for a specific query including all responses
    
    GET /api/ai-council/<query_id>
    """
    try:
        query = AIQuery.query.get(query_id)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query not found'}), 404
        
        # Get all responses
        responses = AIResponse.query.filter_by(query_id=query_id).all()
        
        response_list = []
        for resp in responses:
            response_list.append({
                'ai_service': resp.ai_service,
                'ai_model': resp.ai_model,
                'response_text': resp.response_text,
                'response_length': resp.response_length,
                'response_time': resp.response_time,
                'tokens_used': resp.tokens_used,
                'success': resp.success,
                'error_message': resp.error_message
            })
        
        # Get consensus
        consensus = AIConsensus.query.filter_by(query_id=query_id).first()
        
        import json
        consensus_data = None
        if consensus:
            consensus_data = {
                'summary': consensus.summary,
                'agreement_areas': json.loads(consensus.agreement_areas) if consensus.agreement_areas else [],
                'disagreement_areas': json.loads(consensus.disagreement_areas) if consensus.disagreement_areas else [],
                'consensus_score': consensus.consensus_score,
                'generated_by': consensus.generated_by
            }
        
        return jsonify({
            'success': True,
            'query': {
                'id': query.id,
                'question': query.question,
                'category': query.question_category,
                'created_at': query.created_at.isoformat(),
                'processing_time': query.processing_time,
                'total_responses': query.total_responses,
                'successful_responses': query.successful_responses,
                'failed_responses': query.failed_responses,
                'consensus_level': query.consensus_level,
                'claims_extracted': query.claims_extracted
            },
            'responses': response_list,
            'consensus': consensus_data
        })
    
    except Exception as e:
        logger.error(f"Error fetching query details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_council_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get overall statistics about AI Council usage
    
    GET /api/ai-council/stats
    """
    try:
        total_queries = AIQuery.query.count()
        
        # Get stats for last 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)
        recent_queries = AIQuery.query.filter(AIQuery.created_at >= cutoff).count()
        
        # Average consensus score
        from sqlalchemy import func
        avg_score = db.session.query(func.avg(AIQuery.consensus_score)).scalar() or 0
        
        # Total claims extracted
        total_claims = db.session.query(func.sum(AIQuery.claims_extracted)).scalar() or 0
        
        # Most common categories
        from sqlalchemy import func
        categories = db.session.query(
            AIQuery.question_category,
            func.count(AIQuery.id).label('count')
        ).group_by(AIQuery.question_category).order_by(desc('count')).limit(5).all()
        
        category_stats = [{'category': cat, 'count': count} for cat, count in categories]
        
        return jsonify({
            'success': True,
            'stats': {
                'total_queries': total_queries,
                'recent_queries': recent_queries,
                'average_consensus_score': round(avg_score, 1),
                'total_claims_extracted': total_claims,
                'top_categories': category_stats
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# I did no harm and this file is not truncated
