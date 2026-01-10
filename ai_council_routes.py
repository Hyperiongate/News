"""
TruthLens AI Council - Flask Routes
File: ai_council_routes.py
Date: January 9, 2026
Version: 1.0.0

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
    global db, AIQuery, AIResponse, AIConsensus, ai_council_service
    db = database
    AIQuery = models['AIQuery']
    AIResponse = models['AIResponse']
    AIConsensus = models['AIConsensus']
    ai_council_service = service


@ai_council_bp.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        
        if not data or not data.get('question'):
            return jsonify({'success': False, 'error': 'Question is required'}), 400
        
        question = data['question'].strip()
        
        if len(question) < 10:
            return jsonify({'success': False, 'error': 'Question must be at least 10 characters'}), 400
        
        logger.info(f"[AICouncil API] New question: {question[:100]}...")
        
        result = ai_council_service.query_all(question)
        
        if not result.get('success'):
            return jsonify(result), 500
        
        from ai_council_models import categorize_question
        category = categorize_question(question)
        
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
        
        claims_extracted = 0
        try:
            from claim_tracker_routes import extract_claims_from_text, auto_save_claims_from_analysis
            
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
        
        return jsonify({
            'success': True,
            'query_id': new_query.id,
            'question': question,
            'category': category,
            'responses': result['responses'],
            'consensus': consensus_data,
            'processing_time': result['processing_time'],
            'total_responses': result['total_responses'],
            'successful_responses': result['successful_responses'],
            'claims_extracted': claims_extracted
        })
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_council_bp.route('/recent', methods=['GET'])
def get_recent_queries():
    try:
        limit = int(request.args.get('limit', 20))
        days = int(request.args.get('days', 30))
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        queries = AIQuery.query.filter(
            AIQuery.created_at >= cutoff_date
        ).order_by(
            desc(AIQuery.created_at)
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(queries),
            'queries': [query.to_dict() for query in queries]
        })
    
    except Exception as e:
        logger.error(f"Error getting recent queries: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_council_bp.route('/<int:query_id>', methods=['GET'])
def get_query_details(query_id):
    try:
        query = AIQuery.query.get(query_id)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query not found'}), 404
        
        responses = [response.to_dict() for response in query.responses.all()]
        
        consensus = None
        if query.consensus:
            import json
            consensus_dict = query.consensus.to_dict()
            if consensus_dict.get('agreement_areas'):
                try:
                    consensus_dict['agreement_areas'] = json.loads(consensus_dict['agreement_areas'])
                except:
                    pass
            if consensus_dict.get('disagreement_areas'):
                try:
                    consensus_dict['disagreement_areas'] = json.loads(consensus_dict['disagreement_areas'])
                except:
                    pass
            consensus = consensus_dict
        
        result = query.to_dict()
        result['responses'] = responses
        result['consensus'] = consensus
        
        return jsonify({'success': True, 'query': result})
    
    except Exception as e:
        logger.error(f"Error getting query details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_council_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        total_queries = AIQuery.query.count()
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_queries = AIQuery.query.filter(
            AIQuery.created_at >= week_ago
        ).count()
        
        avg_time_result = db.session.query(
            db.func.avg(AIQuery.processing_time)
        ).scalar()
        avg_processing_time = round(avg_time_result, 2) if avg_time_result else 0
        
        total_claims_result = db.session.query(
            db.func.sum(AIQuery.claims_extracted)
        ).scalar()
        total_claims = int(total_claims_result) if total_claims_result else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_queries': total_queries,
                'recent_queries_7d': recent_queries,
                'avg_processing_time': avg_processing_time,
                'total_claims_extracted': total_claims
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# I did no harm and this file is not truncated
