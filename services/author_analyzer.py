"""
Author Analyzer Service - ENHANCED VISUAL VERSION
Creates rich, educational, and visually engaging author credibility analysis
"""

import os
import logging
import re
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import hashlib
from collections import Counter, defaultdict

import requests
from bs4 import BeautifulSoup

from config import Config
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class AuthorAnalyzer(BaseAnalyzer):
    """
    Enhanced author analysis with visual storytelling and educational insights
    """
    
    def __init__(self):
        """Initialize the author analyzer with enhanced features"""
        super().__init__('author_analyzer')
        
        # API key for NewsAPI
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        
        # Session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NewsAnalyzer/1.0 (Enhanced Author Analyzer)'
        })
        
        # Initialize enhanced journalist database with visual elements
        self.journalist_db = self._initialize_enhanced_journalist_database()
        
        # Cache for API results
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours
        
        # Enhanced publication scoring with trust indicators
        self.publication_scores = self._initialize_enhanced_publication_scores()
        
        # Initialize visual elements and educational content
        self.expertise_icons = self._initialize_expertise_icons()
        self.trust_badges = self._initialize_trust_badges()
        self.career_milestones = self._initialize_career_milestones()
        
        logger.info(f"Enhanced AuthorAnalyzer initialized - NewsAPI: {bool(self.news_api_key)}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create rich, visual author analysis
        """
        try:
            start_time = time.time()
            
            # Extract author name
            author = data.get('author')
            if not author or author.lower() in ['unknown', 'staff', 'editor', 'admin', 'null', 'none']:
                return self._handle_anonymous_author(data)
            
            # Get enhanced author profile
            author_profile = self._build_enhanced_author_profile(author, data)
            
            # Create visual credibility story
            credibility_story = self._create_credibility_story(author_profile)
            
            # Generate trust visualization data
            trust_visualization = self._generate_trust_visualization(author_profile)
            
            # Create educational insights
            educational_insights = self._generate_educational_insights(author_profile)
            
            # Calculate enhanced credibility score
            credibility_score = self._calculate_visual_credibility_score(author_profile)
            
            # Determine author level with visual badge
            author_level = self._determine_author_level(author_profile)
            
            # Create findings for UI
            findings = self._generate_visual_findings(author_profile, credibility_score)
            
            # Generate engaging summary
            summary = self._generate_engaging_summary(author_profile, credibility_score)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': credibility_score,
                    'level': author_level['label'],
                    'findings': findings,
                    'summary': summary,
                    
                    # Enhanced visual data
                    'author_profile': author_profile,
                    'credibility_story': credibility_story,
                    'trust_visualization': trust_visualization,
                    'educational_insights': educational_insights,
                    'author_badge': author_level,
                    
                    # Backward compatibility
                    'credibility_score': credibility_score,
                    'author_name': author,
                    'verification_status': author_profile.get('verification_status', {}),
                    
                    # Rich details
                    'details': {
                        'years_experience': author_profile.get('years_experience', 0),
                        'article_count': author_profile.get('total_articles', 0),
                        'expertise_areas': author_profile.get('expertise_areas', []),
                        'publications': author_profile.get('publications', []),
                        'trust_indicators': author_profile.get('trust_indicators', {}),
                        'visual_elements': author_profile.get('visual_elements', {})
                    }
                },
                'metadata': {
                    'processing_time': time.time() - start_time,
                    'data_sources': author_profile.get('data_sources', []),
                    'visual_elements_count': len(author_profile.get('visual_elements', {}))
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced author analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _build_enhanced_author_profile(self, author: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive author profile with visual elements"""
        profile = {
            'name': author,
            'display_name': self._format_author_name(author),
            'data_sources': []
        }
        
        # Check journalist database first
        db_info = self._check_journalist_database(author)
        if db_info:
            profile.update(db_info)
            profile['data_sources'].append('journalist_database')
        
        # Fetch article history from NewsAPI
        if self.news_api_key:
            article_history = self._fetch_article_history(author)
            if article_history:
                profile.update(self._analyze_article_history(article_history))
                profile['data_sources'].append('news_api')
        
        # Generate visual elements
        profile['visual_elements'] = self._generate_visual_elements(profile)
        
        # Calculate trust indicators
        profile['trust_indicators'] = self._calculate_trust_indicators(profile)
        
        # Add expertise analysis
        profile['expertise_areas'] = self._analyze_expertise_areas(profile)
        
        # Add publication diversity
        profile['publications'] = self._analyze_publications(profile)
        
        # Create timeline visualization data
        profile['career_timeline'] = self._create_career_timeline(profile)
        
        # Add verification status
        profile['verification_status'] = self._determine_verification_status(profile)
        
        return profile
    
    def _initialize_enhanced_journalist_database(self) -> Dict[str, Any]:
        """Enhanced database with visual elements and rich profiles"""
        return {
            # Pulitzer Prize Winners with visual badges
            'maggie haberman': {
                'verified': True,
                'credibility': 95,
                'organization': 'The New York Times',
                'expertise': ['Politics', 'White House', 'Investigative'],
                'awards': ['Pulitzer Prize 2018', 'White House Correspondents Award'],
                'years_experience': 20,
                'badge': '🏆',
                'visual_credibility': {
                    'color': 'gold',
                    'icon': 'trophy',
                    'description': 'Award-Winning Journalist'
                },
                'trust_factors': {
                    'pulitzer_winner': True,
                    'decades_experience': True,
                    'major_publication': True,
                    'verified_identity': True
                }
            },
            'david fahrenthold': {
                'verified': True,
                'credibility': 94,
                'organization': 'The Washington Post',
                'expertise': ['Investigative', 'Politics', 'Nonprofits'],
                'awards': ['Pulitzer Prize 2017'],
                'years_experience': 20,
                'badge': '🏆',
                'visual_credibility': {
                    'color': 'gold',
                    'icon': 'trophy',
                    'description': 'Pulitzer Prize Winner'
                }
            },
            
            # Specialist Reporters with domain expertise
            'gretchen morgenson': {
                'verified': True,
                'credibility': 90,
                'organization': 'NBC News',
                'expertise': ['Finance', 'Wall Street', 'Corporate Accountability'],
                'awards': ['Pulitzer Prize 2002', 'Gerald Loeb Award'],
                'years_experience': 30,
                'badge': '💼',
                'visual_credibility': {
                    'color': 'blue',
                    'icon': 'chart-line',
                    'description': 'Financial Expertise'
                }
            },
            'john carreyrou': {
                'verified': True,
                'credibility': 92,
                'organization': 'The Wall Street Journal',
                'expertise': ['Healthcare', 'Investigative', 'Corporate Fraud'],
                'awards': ['Pulitzer Prize finalist', 'Theranos Investigation'],
                'years_experience': 20,
                'badge': '🔍',
                'visual_credibility': {
                    'color': 'purple',
                    'icon': 'microscope',
                    'description': 'Investigative Specialist'
                }
            },
            
            # Science and Technology Experts
            'ed yong': {
                'verified': True,
                'credibility': 91,
                'organization': 'The Atlantic',
                'expertise': ['Science', 'Biology', 'COVID-19', 'Zoology'],
                'awards': ['Pulitzer Prize 2021', 'National Magazine Award'],
                'years_experience': 15,
                'badge': '🔬',
                'visual_credibility': {
                    'color': 'green',
                    'icon': 'dna',
                    'description': 'Science Communicator'
                }
            },
            'zeynep tufekci': {
                'verified': True,
                'credibility': 88,
                'organization': 'The New York Times',
                'expertise': ['Technology', 'Society', 'COVID-19', 'Social Media'],
                'awards': ['Andrew Carnegie Fellow'],
                'years_experience': 15,
                'badge': '💻',
                'visual_credibility': {
                    'color': 'cyan',
                    'icon': 'network',
                    'description': 'Tech & Society Expert'
                }
            }
        }
    
    def _initialize_enhanced_publication_scores(self) -> Dict[str, Any]:
        """Publication scores with visual trust indicators"""
        return {
            'The New York Times': {
                'score': 90,
                'tier': 'Elite',
                'trust_color': '#1a73e8',
                'icon': 'newspaper',
                'description': 'America\'s Paper of Record'
            },
            'The Washington Post': {
                'score': 89,
                'tier': 'Elite',
                'trust_color': '#1a73e8',
                'icon': 'newspaper',
                'description': 'Democracy Dies in Darkness'
            },
            'BBC': {
                'score': 91,
                'tier': 'Elite',
                'trust_color': '#1a73e8',
                'icon': 'broadcast',
                'description': 'British Public Service Broadcaster'
            },
            'Reuters': {
                'score': 92,
                'tier': 'Elite',
                'trust_color': '#ff6900',
                'icon': 'globe',
                'description': 'Global News Agency'
            },
            'Associated Press': {
                'score': 93,
                'tier': 'Elite',
                'trust_color': '#ff0000',
                'icon': 'wire',
                'description': 'Not-for-profit News Cooperative'
            },
            'The Guardian': {
                'score': 85,
                'tier': 'Premium',
                'trust_color': '#052962',
                'icon': 'shield',
                'description': 'Independent British News'
            },
            'The Wall Street Journal': {
                'score': 88,
                'tier': 'Elite',
                'trust_color': '#0274b6',
                'icon': 'chart',
                'description': 'Business & Financial News'
            },
            'The Atlantic': {
                'score': 84,
                'tier': 'Premium',
                'trust_color': '#ed1c24',
                'icon': 'book',
                'description': 'Ideas & Culture Magazine'
            }
        }
    
    def _initialize_expertise_icons(self) -> Dict[str, str]:
        """Map expertise areas to visual icons"""
        return {
            'Politics': '🏛️',
            'Technology': '💻',
            'Science': '🔬',
            'Health': '🏥',
            'Business': '💼',
            'Climate': '🌍',
            'Education': '🎓',
            'Sports': '⚽',
            'Culture': '🎭',
            'Investigative': '🔍',
            'Finance': '💰',
            'International': '🌐',
            'Legal': '⚖️',
            'Defense': '🛡️',
            'Energy': '⚡'
        }
    
    def _initialize_trust_badges(self) -> List[Dict[str, Any]]:
        """Define visual trust badges"""
        return [
            {
                'id': 'verified',
                'name': 'Verified Journalist',
                'icon': '✓',
                'color': 'green',
                'requirement': 'in_database'
            },
            {
                'id': 'veteran',
                'name': 'Veteran Reporter',
                'icon': '⭐',
                'color': 'gold',
                'requirement': 'years_experience >= 10'
            },
            {
                'id': 'specialist',
                'name': 'Subject Specialist',
                'icon': '🎯',
                'color': 'blue',
                'requirement': 'focused_expertise'
            },
            {
                'id': 'award_winner',
                'name': 'Award Winner',
                'icon': '🏆',
                'color': 'gold',
                'requirement': 'has_awards'
            },
            {
                'id': 'prolific',
                'name': 'Prolific Writer',
                'icon': '📝',
                'color': 'purple',
                'requirement': 'articles >= 100'
            }
        ]
    
    def _initialize_career_milestones(self) -> List[Dict[str, Any]]:
        """Define career milestone visualizations"""
        return [
            {'years': 1, 'label': 'New Voice', 'icon': '🌱', 'color': 'green'},
            {'years': 3, 'label': 'Established', 'icon': '🌿', 'color': 'teal'},
            {'years': 5, 'label': 'Experienced', 'icon': '🌳', 'color': 'blue'},
            {'years': 10, 'label': 'Veteran', 'icon': '🎋', 'color': 'purple'},
            {'years': 15, 'label': 'Senior', 'icon': '🏔️', 'color': 'indigo'},
            {'years': 20, 'label': 'Distinguished', 'icon': '⭐', 'color': 'gold'}
        ]
    
    def _create_credibility_story(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create a visual story about the author's credibility"""
        story = {
            'chapters': [],
            'overall_narrative': '',
            'trust_journey': []
        }
        
        # Chapter 1: Identity
        identity_chapter = {
            'title': 'Identity & Verification',
            'icon': '👤',
            'content': []
        }
        
        if profile.get('verified'):
            identity_chapter['content'].append({
                'type': 'achievement',
                'text': f"✓ {profile['display_name']} is a verified journalist",
                'impact': 'positive'
            })
        else:
            identity_chapter['content'].append({
                'type': 'note',
                'text': f"ℹ️ {profile['display_name']} - verification pending",
                'impact': 'neutral'
            })
        
        story['chapters'].append(identity_chapter)
        
        # Chapter 2: Experience Journey
        experience_chapter = {
            'title': 'Experience & Journey',
            'icon': '📈',
            'content': []
        }
        
        years = profile.get('years_experience', 0)
        if years > 0:
            milestone = self._get_career_milestone(years)
            experience_chapter['content'].append({
                'type': 'milestone',
                'text': f"{milestone['icon']} {milestone['label']} journalist with {years} years experience",
                'impact': 'positive'
            })
        
        story['chapters'].append(experience_chapter)
        
        # Chapter 3: Expertise Areas
        if profile.get('expertise_areas'):
            expertise_chapter = {
                'title': 'Areas of Expertise',
                'icon': '🎯',
                'content': []
            }
            
            for area in profile['expertise_areas'][:3]:
                icon = self.expertise_icons.get(area['topic'], '📰')
                expertise_chapter['content'].append({
                    'type': 'expertise',
                    'text': f"{icon} {area['topic']}: {area['article_count']} articles over {area['years']} years",
                    'impact': 'positive'
                })
            
            story['chapters'].append(expertise_chapter)
        
        # Generate overall narrative
        story['overall_narrative'] = self._generate_narrative(profile)
        
        return story
    
    def _generate_trust_visualization(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for trust visualization"""
        return {
            'trust_wheel': {
                'segments': [
                    {
                        'label': 'Identity',
                        'value': 100 if profile.get('verified') else 50,
                        'color': '#4CAF50',
                        'icon': '👤'
                    },
                    {
                        'label': 'Experience',
                        'value': min(100, profile.get('years_experience', 0) * 5),
                        'color': '#2196F3',
                        'icon': '📅'
                    },
                    {
                        'label': 'Expertise',
                        'value': min(100, len(profile.get('expertise_areas', [])) * 20),
                        'color': '#9C27B0',
                        'icon': '🎯'
                    },
                    {
                        'label': 'Publications',
                        'value': self._calculate_publication_score(profile),
                        'color': '#FF9800',
                        'icon': '📰'
                    },
                    {
                        'label': 'Consistency',
                        'value': self._calculate_consistency_score(profile),
                        'color': '#F44336',
                        'icon': '📊'
                    }
                ]
            },
            'trust_timeline': self._create_trust_timeline(profile),
            'credibility_badges': self._assign_badges(profile)
        }
    
    def _generate_educational_insights(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate educational content about journalism credibility"""
        insights = []
        
        # Insight about verification
        if profile.get('verified'):
            insights.append({
                'type': 'learn',
                'icon': '💡',
                'title': 'Why Verification Matters',
                'content': 'Verified journalists have established identities and track records, making them more accountable for their reporting.',
                'visual': 'shield_check'
            })
        
        # Insight about expertise
        if profile.get('expertise_areas'):
            top_area = profile['expertise_areas'][0]['topic']
            insights.append({
                'type': 'learn',
                'icon': '🎓',
                'title': 'Subject Matter Expertise',
                'content': f'Journalists who specialize in {top_area} develop deep knowledge and reliable source networks in their field.',
                'visual': 'expertise_graph'
            })
        
        # Insight about publication diversity
        pub_count = len(profile.get('publications', []))
        if pub_count > 1:
            insights.append({
                'type': 'learn',
                'icon': '🌐',
                'title': 'Publication Diversity',
                'content': 'Writing for multiple reputable outlets suggests editorial independence and broad credibility.',
                'visual': 'publication_network'
            })
        
        return insights
    
    def _calculate_visual_credibility_score(self, profile: Dict[str, Any]) -> int:
        """Calculate credibility score with visual weighting"""
        score = 0
        max_score = 0
        
        # Verification (25 points)
        max_score += 25
        if profile.get('verified'):
            score += 25
        elif profile.get('years_experience', 0) > 0:
            score += 10
        
        # Experience (20 points)
        max_score += 20
        years = profile.get('years_experience', 0)
        score += min(20, years * 2)
        
        # Expertise focus (20 points)
        max_score += 20
        expertise_areas = profile.get('expertise_areas', [])
        if expertise_areas:
            # Reward depth over breadth
            top_area_articles = expertise_areas[0].get('article_count', 0)
            score += min(20, top_area_articles // 5)
        
        # Publication quality (20 points)
        max_score += 20
        pub_score = self._calculate_publication_score(profile)
        score += pub_score * 0.2
        
        # Awards and recognition (15 points)
        max_score += 15
        if profile.get('awards'):
            score += min(15, len(profile['awards']) * 5)
        
        # Calculate percentage
        final_score = int((score / max_score) * 100)
        
        return min(100, final_score)
    
    def _determine_author_level(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Determine author level with visual badge"""
        score = profile.get('credibility_score', 0)
        years = profile.get('years_experience', 0)
        
        if score >= 90 or profile.get('awards'):
            return {
                'label': 'Distinguished',
                'icon': '⭐',
                'color': 'gold',
                'description': 'Exceptional credibility and recognition'
            }
        elif score >= 75 or years >= 10:
            return {
                'label': 'Trusted',
                'icon': '🏆',
                'color': 'blue',
                'description': 'Established journalist with strong credibility'
            }
        elif score >= 60 or years >= 5:
            return {
                'label': 'Established',
                'icon': '✓',
                'color': 'green',
                'description': 'Proven track record and growing reputation'
            }
        elif score >= 40 or years >= 2:
            return {
                'label': 'Developing',
                'icon': '📈',
                'color': 'teal',
                'description': 'Building credibility and experience'
            }
        else:
            return {
                'label': 'Emerging',
                'icon': '🌱',
                'color': 'gray',
                'description': 'New voice in journalism'
            }
    
    def _generate_visual_findings(self, profile: Dict[str, Any], score: int) -> List[Dict[str, Any]]:
        """Generate visually rich findings"""
        findings = []
        
        # Positive findings
        if profile.get('verified'):
            findings.append({
                'type': 'author',
                'severity': 'positive',
                'text': f"✓ Verified journalist with established credibility",
                'finding': 'Verified Author',
                'visual': {'icon': 'shield-check', 'color': 'green'}
            })
        
        if profile.get('years_experience', 0) >= 10:
            findings.append({
                'type': 'author',
                'severity': 'positive',
                'text': f"⭐ {profile['years_experience']} years of journalism experience",
                'finding': 'Veteran Journalist',
                'visual': {'icon': 'star', 'color': 'gold'}
            })
        
        # Expertise finding
        if profile.get('expertise_areas'):
            top_area = profile['expertise_areas'][0]
            findings.append({
                'type': 'author',
                'severity': 'positive',
                'text': f"🎯 Specialist in {top_area['topic']} ({top_area['article_count']} articles)",
                'finding': 'Subject Expert',
                'visual': {'icon': 'target', 'color': 'blue'}
            })
        
        # Neutral/negative findings
        if not profile.get('verified') and score < 60:
            findings.append({
                'type': 'author',
                'severity': 'medium',
                'text': 'ℹ️ Limited verification data available',
                'finding': 'Unverified Author',
                'visual': {'icon': 'info', 'color': 'orange'}
            })
        
        return findings[:4]  # Limit to 4 most relevant findings
    
    def _generate_engaging_summary(self, profile: Dict[str, Any], score: int) -> str:
        """Generate an engaging, educational summary"""
        name = profile['display_name']
        
        if score >= 80:
            if profile.get('awards'):
                return f"{name} is an award-winning journalist with exceptional credibility (score: {score}%). Their distinguished career spans {profile.get('years_experience', 'many')} years with recognized excellence in {profile.get('expertise_areas', [{}])[0].get('topic', 'journalism')}."
            else:
                return f"{name} is a highly credible journalist (score: {score}%) with {profile.get('years_experience', 'extensive')} years of experience. They've established themselves as a trusted voice in {profile.get('expertise_areas', [{}])[0].get('topic', 'their field')}."
        elif score >= 60:
            return f"{name} is an established journalist (score: {score}%) with {profile.get('years_experience', 'several')} years of experience. They regularly cover {profile.get('expertise_areas', [{}])[0].get('topic', 'various topics')} with growing expertise."
        else:
            if profile.get('years_experience', 0) < 3:
                return f"{name} appears to be an emerging journalist (score: {score}%). While they have limited track record, everyone starts somewhere. Look for additional credibility indicators in their reporting."
            else:
                return f"{name} has a moderate credibility score ({score}%). Limited information is available about their journalism background. Consider evaluating their sources and fact-checking their claims."
    
    def _handle_anonymous_author(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle anonymous or staff authors with educational context"""
        return {
            'service': self.service_name,
            'success': True,
            'data': {
                'score': 20,
                'level': 'Anonymous',
                'findings': [{
                    'type': 'author',
                    'severity': 'high',
                    'text': '⚠️ No author attribution provided',
                    'finding': 'Anonymous Article',
                    'visual': {'icon': 'alert', 'color': 'red'}
                }],
                'summary': 'This article lacks author attribution, making it impossible to verify the writer\'s credibility or expertise.',
                'educational_insights': [{
                    'type': 'learn',
                    'icon': '💡',
                    'title': 'Why Bylines Matter',
                    'content': 'Author bylines create accountability. Anonymous articles should be evaluated extra carefully, checking sources and cross-referencing claims.'
                }],
                'credibility_score': 20,
                'author_name': 'Unknown',
                'verification_status': {'verified': False, 'anonymous': True}
            }
        }
    
    # Helper methods
    def _format_author_name(self, author: str) -> str:
        """Format author name for display"""
        return ' '.join(word.capitalize() for word in author.split())
    
    def _get_career_milestone(self, years: int) -> Dict[str, Any]:
        """Get career milestone based on years"""
        for milestone in reversed(self.career_milestones):
            if years >= milestone['years']:
                return milestone
        return self.career_milestones[0]
    
    def _calculate_publication_score(self, profile: Dict[str, Any]) -> int:
        """Calculate score based on publication quality"""
        score = 0
        for pub in profile.get('publications', []):
            pub_info = self.publication_scores.get(pub['name'], {})
            score += pub_info.get('score', 50)
        return min(100, score // max(1, len(profile.get('publications', [1]))))
    
    def _calculate_consistency_score(self, profile: Dict[str, Any]) -> int:
        """Calculate consistency score"""
        # Reward consistent byline usage and regular publishing
        base_score = 50
        if profile.get('years_experience', 0) > 2:
            base_score += 20
        if len(profile.get('expertise_areas', [])) > 0:
            base_score += 20
        if profile.get('verified'):
            base_score += 10
        return min(100, base_score)
    
    def _create_trust_timeline(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create timeline visualization data"""
        timeline = []
        current_year = datetime.now().year
        years_exp = profile.get('years_experience', 0)
        
        if years_exp > 0:
            start_year = current_year - years_exp
            
            # Add key milestones
            timeline.append({
                'year': start_year,
                'event': 'Started journalism career',
                'icon': '🌱',
                'impact': 'neutral'
            })
            
            # Add expertise development
            for area in profile.get('expertise_areas', [])[:2]:
                timeline.append({
                    'year': start_year + area.get('years', 1),
                    'event': f'Began covering {area["topic"]}',
                    'icon': self.expertise_icons.get(area['topic'], '📰'),
                    'impact': 'positive'
                })
            
            # Add awards
            for award in profile.get('awards', []):
                timeline.append({
                    'year': current_year - 2,  # Approximate
                    'event': f'Won {award}',
                    'icon': '🏆',
                    'impact': 'major'
                })
        
        return sorted(timeline, key=lambda x: x['year'])
    
    def _assign_badges(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assign visual badges based on achievements"""
        badges = []
        
        if profile.get('verified'):
            badges.append({
                'id': 'verified',
                'name': 'Verified Journalist',
                'icon': '✓',
                'color': 'green'
            })
        
        if profile.get('years_experience', 0) >= 10:
            badges.append({
                'id': 'veteran',
                'name': 'Veteran Reporter',
                'icon': '⭐',
                'color': 'gold'
            })
        
        if profile.get('awards'):
            badges.append({
                'id': 'award_winner',
                'name': 'Award Winner',
                'icon': '🏆',
                'color': 'gold'
            })
        
        if len(profile.get('expertise_areas', [])) > 0:
            badges.append({
                'id': 'specialist',
                'name': 'Subject Specialist',
                'icon': '🎯',
                'color': 'blue'
            })
        
        return badges
    
    def _generate_narrative(self, profile: Dict[str, Any]) -> str:
        """Generate a narrative description of the author's credibility journey"""
        parts = []
        
        name = profile['display_name']
        
        # Opening
        if profile.get('verified'):
            parts.append(f"{name} is a verified journalist")
        else:
            parts.append(f"{name} is a journalist")
        
        # Experience
        years = profile.get('years_experience', 0)
        if years > 15:
            parts.append(f"with over {years} years of distinguished service")
        elif years > 5:
            parts.append(f"with {years} years of solid experience")
        elif years > 0:
            parts.append(f"with {years} years in the field")
        
        # Expertise
        if profile.get('expertise_areas'):
            top_area = profile['expertise_areas'][0]['topic']
            parts.append(f"specializing in {top_area}")
        
        # Awards
        if profile.get('awards'):
            parts.append(f"and recipient of {len(profile['awards'])} major awards")
        
        return ' '.join(parts) + '.'
    
    # Existing methods continue...
    def _check_journalist_database(self, author: str) -> Optional[Dict[str, Any]]:
        """Check if author is in enhanced journalist database"""
        author_lower = author.lower().strip()
        
        # Direct lookup
        if author_lower in self.journalist_db:
            return self.journalist_db[author_lower].copy()
        
        # Partial match
        for db_name, info in self.journalist_db.items():
            if author_lower in db_name or db_name in author_lower:
                return info.copy()
        
        return None
    
    def _fetch_article_history(self, author: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch article history from NewsAPI"""
        if not self.news_api_key:
            return None
        
        # Check cache
        cache_key = f"author_{author.lower()}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        try:
            articles = []
            
            # Search for articles by this author
            url = "https://newsapi.org/v2/everything"
            params = {
                'apiKey': self.news_api_key,
                'q': f'"{author}"',
                'searchIn': 'author',
                'sortBy': 'publishedAt',
                'pageSize': 100,
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Cache the result
                self._cache_result(cache_key, articles)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching article history: {e}")
            return None
    
    def _analyze_article_history(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze article history for patterns and expertise"""
        if not articles:
            return {}
        
        analysis = {
            'total_articles': len(articles),
            'publications': defaultdict(int),
            'topics': defaultdict(int),
            'timeline': []
        }
        
        # Analyze each article
        for article in articles:
            # Track publications
            source = article.get('source', {}).get('name', 'Unknown')
            analysis['publications'][source] += 1
            
            # Extract topics from title and description
            text = f"{article.get('title', '')} {article.get('description', '')}"
            topics = self._extract_topics(text)
            for topic in topics:
                analysis['topics'][topic] += 1
            
            # Build timeline
            pub_date = article.get('publishedAt')
            if pub_date:
                analysis['timeline'].append(pub_date)
        
        # Calculate years of experience
        if analysis['timeline']:
            oldest = min(analysis['timeline'])
            newest = max(analysis['timeline'])
            oldest_date = datetime.fromisoformat(oldest.replace('Z', '+00:00'))
            newest_date = datetime.fromisoformat(newest.replace('Z', '+00:00'))
            years = (newest_date - oldest_date).days / 365.25
            analysis['years_experience'] = max(1, int(years))
        
        return analysis
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()
        
        # Topic keywords mapping
        topic_keywords = {
            'Politics': ['election', 'president', 'congress', 'senate', 'political', 'government', 'democracy'],
            'Technology': ['tech', 'software', 'ai', 'artificial intelligence', 'computer', 'digital', 'cyber'],
            'Business': ['business', 'economy', 'market', 'finance', 'company', 'corporate', 'stock'],
            'Health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'treatment', 'covid'],
            'Climate': ['climate', 'environment', 'warming', 'carbon', 'renewable', 'sustainability'],
            'Science': ['science', 'research', 'study', 'scientist', 'discovery', 'experiment']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:3]  # Return top 3 topics
    
    def _analyze_expertise_areas(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze and structure expertise areas"""
        topics = profile.get('topics', {})
        if not topics:
            return []
        
        expertise_areas = []
        
        # Sort topics by frequency
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        
        for topic, count in sorted_topics[:5]:
            # Calculate approximate years covering this topic
            years = min(profile.get('years_experience', 1), count // 10 + 1)
            
            expertise_areas.append({
                'topic': topic,
                'article_count': count,
                'years': years,
                'level': 'Expert' if count > 30 else 'Specialist' if count > 10 else 'Familiar'
            })
        
        return expertise_areas
    
    def _analyze_publications(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze publication history"""
        pubs = profile.get('publications', {})
        if not pubs:
            return []
        
        publications = []
        
        # Sort by article count
        sorted_pubs = sorted(pubs.items(), key=lambda x: x[1], reverse=True)
        
        for pub_name, count in sorted_pubs[:5]:
            pub_info = self.publication_scores.get(pub_name, {})
            
            publications.append({
                'name': pub_name,
                'article_count': count,
                'tier': pub_info.get('tier', 'Standard'),
                'trust_score': pub_info.get('score', 70),
                'primary': count == sorted_pubs[0][1]  # Is this their primary publication?
            })
        
        return publications
    
    def _create_career_timeline(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create career timeline data"""
        return {
            'start_year': datetime.now().year - profile.get('years_experience', 0),
            'milestones': self._create_trust_timeline(profile),
            'current_status': self._determine_author_level(profile)
        }
    
    def _determine_verification_status(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Determine detailed verification status"""
        return {
            'verified': profile.get('verified', False),
            'verification_source': 'journalist_database' if profile.get('verified') else None,
            'confidence': 'high' if profile.get('verified') else 'medium' if profile.get('years_experience', 0) > 2 else 'low',
            'factors': {
                'has_byline': True,
                'in_database': profile.get('verified', False),
                'has_history': profile.get('total_articles', 0) > 0,
                'consistent_name': True  # Could be enhanced with name variation checking
            }
        }
    
    def _generate_visual_elements(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visual elements for UI"""
        return {
            'primary_badge': self._determine_author_level(profile),
            'trust_badges': self._assign_badges(profile),
            'expertise_icons': [
                {
                    'topic': area['topic'],
                    'icon': self.expertise_icons.get(area['topic'], '📰'),
                    'count': area['article_count']
                }
                for area in profile.get('expertise_areas', [])[:3]
            ],
            'publication_logos': [
                {
                    'name': pub['name'],
                    'color': self.publication_scores.get(pub['name'], {}).get('trust_color', '#666')
                }
                for pub in profile.get('publications', [])[:3]
            ]
        }
    
    def _calculate_trust_indicators(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed trust indicators"""
        return {
            'identity_verified': profile.get('verified', False),
            'experience_depth': min(100, profile.get('years_experience', 0) * 10),
            'expertise_focus': len(profile.get('expertise_areas', [])) > 0,
            'publication_quality': self._calculate_publication_score(profile),
            'consistency_score': self._calculate_consistency_score(profile),
            'transparency_level': 'high' if profile.get('verified') else 'medium'
        }
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if available"""
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return result
        return None
    
    def _cache_result(self, cache_key: str, result: Any):
        """Cache result"""
        self.cache[cache_key] = (time.time(), result)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Visual credibility assessment',
                'Career timeline visualization',
                'Expertise area mapping',
                'Trust badge assignment',
                'Publication history analysis',
                'Educational insights',
                'Interactive credibility story',
                'Award recognition'
            ],
            'visual_elements': len(self.expertise_icons),
            'journalists_in_database': len(self.journalist_db),
            'trust_badges_available': len(self.trust_badges)
        })
        return info"""
Author Analyzer Service - ENHANCED VISUAL VERSION
Creates rich, educational, and visually engaging author credibility analysis
"""

import os
import logging
import re
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import hashlib
from collections import Counter, defaultdict

import requests
from bs4 import BeautifulSoup

from config import Config
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class AuthorAnalyzer(BaseAnalyzer):
    """
    Enhanced author analysis with visual storytelling and educational insights
    """
    
    def __init__(self):
        """Initialize the author analyzer with enhanced features"""
        super().__init__('author_analyzer')
        
        # API key for NewsAPI
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        
        # Session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NewsAnalyzer/1.0 (Enhanced Author Analyzer)'
        })
        
        # Initialize enhanced journalist database with visual elements
        self.journalist_db = self._initialize_enhanced_journalist_database()
        
        # Cache for API results
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours
        
        # Enhanced publication scoring with trust indicators
        self.publication_scores = self._initialize_enhanced_publication_scores()
        
        # Initialize visual elements and educational content
        self.expertise_icons = self._initialize_expertise_icons()
        self.trust_badges = self._initialize_trust_badges()
        self.career_milestones = self._initialize_career_milestones()
        
        logger.info(f"Enhanced AuthorAnalyzer initialized - NewsAPI: {bool(self.news_api_key)}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create rich, visual author analysis
        """
        try:
            start_time = time.time()
            
            # Extract author name
            author = data.get('author')
            if not author or author.lower() in ['unknown', 'staff', 'editor', 'admin', 'null', 'none']:
                return self._handle_anonymous_author(data)
            
            # Get enhanced author profile
            author_profile = self._build_enhanced_author_profile(author, data)
            
            # Create visual credibility story
            credibility_story = self._create_credibility_story(author_profile)
            
            # Generate trust visualization data
            trust_visualization = self._generate_trust_visualization(author_profile)
            
            # Create educational insights
            educational_insights = self._generate_educational_insights(author_profile)
            
            # Calculate enhanced credibility score
            credibility_score = self._calculate_visual_credibility_score(author_profile)
            
            # Determine author level with visual badge
            author_level = self._determine_author_level(author_profile)
            
            # Create findings for UI
            findings = self._generate_visual_findings(author_profile, credibility_score)
            
            # Generate engaging summary
            summary = self._generate_engaging_summary(author_profile, credibility_score)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': credibility_score,
                    'level': author_level['label'],
                    'findings': findings,
                    'summary': summary,
                    
                    # Enhanced visual data
                    'author_profile': author_profile,
                    'credibility_story': credibility_story,
                    'trust_visualization': trust_visualization,
                    'educational_insights': educational_insights,
                    'author_badge': author_level,
                    
                    # Backward compatibility
                    'credibility_score': credibility_score,
                    'author_name': author,
                    'verification_status': author_profile.get('verification_status', {}),
                    
                    # Rich details
                    'details': {
                        'years_experience': author_profile.get('years_experience', 0),
                        'article_count': author_profile.get('total_articles', 0),
                        'expertise_areas': author_profile.get('expertise_areas', []),
                        'publications': author_profile.get('publications', []),
                        'trust_indicators': author_profile.get('trust_indicators', {}),
                        'visual_elements': author_profile.get('visual_elements', {})
                    }
                },
                'metadata': {
                    'processing_time': time.time() - start_time,
                    'data_sources': author_profile.get('data_sources', []),
                    'visual_elements_count': len(author_profile.get('visual_elements', {}))
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced author analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _build_enhanced_author_profile(self, author: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive author profile with visual elements"""
        profile = {
            'name': author,
            'display_name': self._format_author_name(author),
            'data_sources': []
        }
        
        # Check journalist database first
        db_info = self._check_journalist_database(author)
        if db_info:
            profile.update(db_info)
            profile['data_sources'].append('journalist_database')
        
        # Fetch article history from NewsAPI
        if self.news_api_key:
            article_history = self._fetch_article_history(author)
            if article_history:
                profile.update(self._analyze_article_history(article_history))
                profile['data_sources'].append('news_api')
        
        # Generate visual elements
        profile['visual_elements'] = self._generate_visual_elements(profile)
        
        # Calculate trust indicators
        profile['trust_indicators'] = self._calculate_trust_indicators(profile)
        
        # Add expertise analysis
        profile['expertise_areas'] = self._analyze_expertise_areas(profile)
        
        # Add publication diversity
        profile['publications'] = self._analyze_publications(profile)
        
        # Create timeline visualization data
        profile['career_timeline'] = self._create_career_timeline(profile)
        
        # Add verification status
        profile['verification_status'] = self._determine_verification_status(profile)
        
        return profile
    
    def _initialize_enhanced_journalist_database(self) -> Dict[str, Any]:
        """Enhanced database with visual elements and rich profiles"""
        return {
            # Pulitzer Prize Winners with visual badges
            'maggie haberman': {
                'verified': True,
                'credibility': 95,
                'organization': 'The New York Times',
                'expertise': ['Politics', 'White House', 'Investigative'],
                'awards': ['Pulitzer Prize 2018', 'White House Correspondents Award'],
                'years_experience': 20,
                'badge': '🏆',
                'visual_credibility': {
                    'color': 'gold',
                    'icon': 'trophy',
                    'description': 'Award-Winning Journalist'
                },
                'trust_factors': {
                    'pulitzer_winner': True,
                    'decades_experience': True,
                    'major_publication': True,
                    'verified_identity': True
                }
            },
            'david fahrenthold': {
                'verified': True,
                'credibility': 94,
                'organization': 'The Washington Post',
                'expertise': ['Investigative', 'Politics', 'Nonprofits'],
                'awards': ['Pulitzer Prize 2017'],
                'years_experience': 20,
                'badge': '🏆',
                'visual_credibility': {
                    'color': 'gold',
                    'icon': 'trophy',
                    'description': 'Pulitzer Prize Winner'
                }
            },
            
            # Specialist Reporters with domain expertise
            'gretchen morgenson': {
                'verified': True,
                'credibility': 90,
                'organization': 'NBC News',
                'expertise': ['Finance', 'Wall Street', 'Corporate Accountability'],
                'awards': ['Pulitzer Prize 2002', 'Gerald Loeb Award'],
                'years_experience': 30,
                'badge': '💼',
                'visual_credibility': {
                    'color': 'blue',
                    'icon': 'chart-line',
                    'description': 'Financial Expertise'
                }
            },
            'john carreyrou': {
                'verified': True,
                'credibility': 92,
                'organization': 'The Wall Street Journal',
                'expertise': ['Healthcare', 'Investigative', 'Corporate Fraud'],
                'awards': ['Pulitzer Prize finalist', 'Theranos Investigation'],
                'years_experience': 20,
                'badge': '🔍',
                'visual_credibility': {
                    'color': 'purple',
                    'icon': 'microscope',
                    'description': 'Investigative Specialist'
                }
            },
            
            # Science and Technology Experts
            'ed yong': {
                'verified': True,
                'credibility': 91,
                'organization': 'The Atlantic',
                'expertise': ['Science', 'Biology', 'COVID-19', 'Zoology'],
                'awards': ['Pulitzer Prize 2021', 'National Magazine Award'],
                'years_experience': 15,
                'badge': '🔬',
                'visual_credibility': {
                    'color': 'green',
                    'icon': 'dna',
                    'description': 'Science Communicator'
                }
            },
            'zeynep tufekci': {
                'verified': True,
                'credibility': 88,
                'organization': 'The New York Times',
                'expertise': ['Technology', 'Society', 'COVID-19', 'Social Media'],
                'awards': ['Andrew Carnegie Fellow'],
                'years_experience': 15,
                'badge': '💻',
                'visual_credibility': {
                    'color': 'cyan',
                    'icon': 'network',
                    'description': 'Tech & Society Expert'
                }
            }
        }
    
    def _initialize_enhanced_publication_scores(self) -> Dict[str, Any]:
        """Publication scores with visual trust indicators"""
        return {
            'The New York Times': {
                'score': 90,
                'tier': 'Elite',
                'trust_color': '#1a73e8',
                'icon': 'newspaper',
                'description': 'America\'s Paper of Record'
            },
            'The Washington Post': {
                'score': 89,
                'tier': 'Elite',
                'trust_color': '#1a73e8',
                'icon': 'newspaper',
                'description': 'Democracy Dies in Darkness'
            },
            'BBC': {
                'score': 91,
                'tier': 'Elite',
                'trust_color': '#1a73e8',
                'icon': 'broadcast',
                'description': 'British Public Service Broadcaster'
            },
            'Reuters': {
                'score': 92,
                'tier': 'Elite',
                'trust_color': '#ff6900',
                'icon': 'globe',
                'description': 'Global News Agency'
            },
            'Associated Press': {
                'score': 93,
                'tier': 'Elite',
                'trust_color': '#ff0000',
                'icon': 'wire',
                'description': 'Not-for-profit News Cooperative'
            },
            'The Guardian': {
                'score': 85,
                'tier': 'Premium',
                'trust_color': '#052962',
                'icon': 'shield',
                'description': 'Independent British News'
            },
            'The Wall Street Journal': {
                'score': 88,
                'tier': 'Elite',
                'trust_color': '#0274b6',
                'icon': 'chart',
                'description': 'Business & Financial News'
            },
            'The Atlantic': {
                'score': 84,
                'tier': 'Premium',
                'trust_color': '#ed1c24',
                'icon': 'book',
                'description': 'Ideas & Culture Magazine'
            }
        }
    
    def _initialize_expertise_icons(self) -> Dict[str, str]:
        """Map expertise areas to visual icons"""
        return {
            'Politics': '🏛️',
            'Technology': '💻',
            'Science': '🔬',
            'Health': '🏥',
            'Business': '💼',
            'Climate': '🌍',
            'Education': '🎓',
            'Sports': '⚽',
            'Culture': '🎭',
            'Investigative': '🔍',
            'Finance': '💰',
            'International': '🌐',
            'Legal': '⚖️',
            'Defense': '🛡️',
            'Energy': '⚡'
        }
    
    def _initialize_trust_badges(self) -> List[Dict[str, Any]]:
        """Define visual trust badges"""
        return [
            {
                'id': 'verified',
                'name': 'Verified Journalist',
                'icon': '✓',
                'color': 'green',
                'requirement': 'in_database'
            },
            {
                'id': 'veteran',
                'name': 'Veteran Reporter',
                'icon': '⭐',
                'color': 'gold',
                'requirement': 'years_experience >= 10'
            },
            {
                'id': 'specialist',
                'name': 'Subject Specialist',
                'icon': '🎯',
                'color': 'blue',
                'requirement': 'focused_expertise'
            },
            {
                'id': 'award_winner',
                'name': 'Award Winner',
                'icon': '🏆',
                'color': 'gold',
                'requirement': 'has_awards'
            },
            {
                'id': 'prolific',
                'name': 'Prolific Writer',
                'icon': '📝',
                'color': 'purple',
                'requirement': 'articles >= 100'
            }
        ]
    
    def _initialize_career_milestones(self) -> List[Dict[str, Any]]:
        """Define career milestone visualizations"""
        return [
            {'years': 1, 'label': 'New Voice', 'icon': '🌱', 'color': 'green'},
            {'years': 3, 'label': 'Established', 'icon': '🌿', 'color': 'teal'},
            {'years': 5, 'label': 'Experienced', 'icon': '🌳', 'color': 'blue'},
            {'years': 10, 'label': 'Veteran', 'icon': '🎋', 'color': 'purple'},
            {'years': 15, 'label': 'Senior', 'icon': '🏔️', 'color': 'indigo'},
            {'years': 20, 'label': 'Distinguished', 'icon': '⭐', 'color': 'gold'}
        ]
    
    def _create_credibility_story(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create a visual story about the author's credibility"""
        story = {
            'chapters': [],
            'overall_narrative': '',
            'trust_journey': []
        }
        
        # Chapter 1: Identity
        identity_chapter = {
            'title': 'Identity & Verification',
            'icon': '👤',
            'content': []
        }
        
        if profile.get('verified'):
            identity_chapter['content'].append({
                'type': 'achievement',
                'text': f"✓ {profile['display_name']} is a verified journalist",
                'impact': 'positive'
            })
        else:
            identity_chapter['content'].append({
                'type': 'note',
                'text': f"ℹ️ {profile['display_name']} - verification pending",
                'impact': 'neutral'
            })
        
        story['chapters'].append(identity_chapter)
        
        # Chapter 2: Experience Journey
        experience_chapter = {
            'title': 'Experience & Journey',
            'icon': '📈',
            'content': []
        }
        
        years = profile.get('years_experience', 0)
        if years > 0:
            milestone = self._get_career_milestone(years)
            experience_chapter['content'].append({
                'type': 'milestone',
                'text': f"{milestone['icon']} {milestone['label']} journalist with {years} years experience",
                'impact': 'positive'
            })
        
        story['chapters'].append(experience_chapter)
        
        # Chapter 3: Expertise Areas
        if profile.get('expertise_areas'):
            expertise_chapter = {
                'title': 'Areas of Expertise',
                'icon': '🎯',
                'content': []
            }
            
            for area in profile['expertise_areas'][:3]:
                icon = self.expertise_icons.get(area['topic'], '📰')
                expertise_chapter['content'].append({
                    'type': 'expertise',
                    'text': f"{icon} {area['topic']}: {area['article_count']} articles over {area['years']} years",
                    'impact': 'positive'
                })
            
            story['chapters'].append(expertise_chapter)
        
        # Generate overall narrative
        story['overall_narrative'] = self._generate_narrative(profile)
        
        return story
    
    def _generate_trust_visualization(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for trust visualization"""
        return {
            'trust_wheel': {
                'segments': [
                    {
                        'label': 'Identity',
                        'value': 100 if profile.get('verified') else 50,
                        'color': '#4CAF50',
                        'icon': '👤'
                    },
                    {
                        'label': 'Experience',
                        'value': min(100, profile.get('years_experience', 0) * 5),
                        'color': '#2196F3',
                        'icon': '📅'
                    },
                    {
                        'label': 'Expertise',
                        'value': min(100, len(profile.get('expertise_areas', [])) * 20),
                        'color': '#9C27B0',
                        'icon': '🎯'
                    },
                    {
                        'label': 'Publications',
                        'value': self._calculate_publication_score(profile),
                        'color': '#FF9800',
                        'icon': '📰'
                    },
                    {
                        'label': 'Consistency',
                        'value': self._calculate_consistency_score(profile),
                        'color': '#F44336',
                        'icon': '📊'
                    }
                ]
            },
            'trust_timeline': self._create_trust_timeline(profile),
            'credibility_badges': self._assign_badges(profile)
        }
    
    def _generate_educational_insights(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate educational content about journalism credibility"""
        insights = []
        
        # Insight about verification
        if profile.get('verified'):
            insights.append({
                'type': 'learn',
                'icon': '💡',
                'title': 'Why Verification Matters',
                'content': 'Verified journalists have established identities and track records, making them more accountable for their reporting.',
                'visual': 'shield_check'
            })
        
        # Insight about expertise
        if profile.get('expertise_areas'):
            top_area = profile['expertise_areas'][0]['topic']
            insights.append({
                'type': 'learn',
                'icon': '🎓',
                'title': 'Subject Matter Expertise',
                'content': f'Journalists who specialize in {top_area} develop deep knowledge and reliable source networks in their field.',
                'visual': 'expertise_graph'
            })
        
        # Insight about publication diversity
        pub_count = len(profile.get('publications', []))
        if pub_count > 1:
            insights.append({
                'type': 'learn',
                'icon': '🌐',
                'title': 'Publication Diversity',
                'content': 'Writing for multiple reputable outlets suggests editorial independence and broad credibility.',
                'visual': 'publication_network'
            })
        
        return insights
    
    def _calculate_visual_credibility_score(self, profile: Dict[str, Any]) -> int:
        """Calculate credibility score with visual weighting"""
        score = 0
        max_score = 0
        
        # Verification (25 points)
        max_score += 25
        if profile.get('verified'):
            score += 25
        elif profile.get('years_experience', 0) > 0:
            score += 10
        
        # Experience (20 points)
        max_score += 20
        years = profile.get('years_experience', 0)
        score += min(20, years * 2)
        
        # Expertise focus (20 points)
        max_score += 20
        expertise_areas = profile.get('expertise_areas', [])
        if expertise_areas:
            # Reward depth over breadth
            top_area_articles = expertise_areas[0].get('article_count', 0)
            score += min(20, top_area_articles // 5)
        
        # Publication quality (20 points)
        max_score += 20
        pub_score = self._calculate_publication_score(profile)
        score += pub_score * 0.2
        
        # Awards and recognition (15 points)
        max_score += 15
        if profile.get('awards'):
            score += min(15, len(profile['awards']) * 5)
        
        # Calculate percentage
        final_score = int((score / max_score) * 100)
        
        return min(100, final_score)
    
    def _determine_author_level(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Determine author level with visual badge"""
        score = profile.get('credibility_score', 0)
        years = profile.get('years_experience', 0)
        
        if score >= 90 or profile.get('awards'):
            return {
                'label': 'Distinguished',
                'icon': '⭐',
                'color': 'gold',
                'description': 'Exceptional credibility and recognition'
            }
        elif score >= 75 or years >= 10:
            return {
                'label': 'Trusted',
                'icon': '🏆',
                'color': 'blue',
                'description': 'Established journalist with strong credibility'
            }
        elif score >= 60 or years >= 5:
            return {
                'label': 'Established',
                'icon': '✓',
                'color': 'green',
                'description': 'Proven track record and growing reputation'
            }
        elif score >= 40 or years >= 2:
            return {
                'label': 'Developing',
                'icon': '📈',
                'color': 'teal',
                'description': 'Building credibility and experience'
            }
        else:
            return {
                'label': 'Emerging',
                'icon': '🌱',
                'color': 'gray',
                'description': 'New voice in journalism'
            }
    
    def _generate_visual_findings(self, profile: Dict[str, Any], score: int) -> List[Dict[str, Any]]:
        """Generate visually rich findings"""
        findings = []
        
        # Positive findings
        if profile.get('verified'):
            findings.append({
                'type': 'author',
                'severity': 'positive',
                'text': f"✓ Verified journalist with established credibility",
                'finding': 'Verified Author',
                'visual': {'icon': 'shield-check', 'color': 'green'}
            })
        
        if profile.get('years_experience', 0) >= 10:
            findings.append({
                'type': 'author',
                'severity': 'positive',
                'text': f"⭐ {profile['years_experience']} years of journalism experience",
                'finding': 'Veteran Journalist',
                'visual': {'icon': 'star', 'color': 'gold'}
            })
        
        # Expertise finding
        if profile.get('expertise_areas'):
            top_area = profile['expertise_areas'][0]
            findings.append({
                'type': 'author',
                'severity': 'positive',
                'text': f"🎯 Specialist in {top_area['topic']} ({top_area['article_count']} articles)",
                'finding': 'Subject Expert',
                'visual': {'icon': 'target', 'color': 'blue'}
            })
        
        # Neutral/negative findings
        if not profile.get('verified') and score < 60:
            findings.append({
                'type': 'author',
                'severity': 'medium',
                'text': 'ℹ️ Limited verification data available',
                'finding': 'Unverified Author',
                'visual': {'icon': 'info', 'color': 'orange'}
            })
        
        return findings[:4]  # Limit to 4 most relevant findings
    
    def _generate_engaging_summary(self, profile: Dict[str, Any], score: int) -> str:
        """Generate an engaging, educational summary"""
        name = profile['display_name']
        
        if score >= 80:
            if profile.get('awards'):
                return f"{name} is an award-winning journalist with exceptional credibility (score: {score}%). Their distinguished career spans {profile.get('years_experience', 'many')} years with recognized excellence in {profile.get('expertise_areas', [{}])[0].get('topic', 'journalism')}."
            else:
                return f"{name} is a highly credible journalist (score: {score}%) with {profile.get('years_experience', 'extensive')} years of experience. They've established themselves as a trusted voice in {profile.get('expertise_areas', [{}])[0].get('topic', 'their field')}."
        elif score >= 60:
            return f"{name} is an established journalist (score: {score}%) with {profile.get('years_experience', 'several')} years of experience. They regularly cover {profile.get('expertise_areas', [{}])[0].get('topic', 'various topics')} with growing expertise."
        else:
            if profile.get('years_experience', 0) < 3:
                return f"{name} appears to be an emerging journalist (score: {score}%). While they have limited track record, everyone starts somewhere. Look for additional credibility indicators in their reporting."
            else:
                return f"{name} has a moderate credibility score ({score}%). Limited information is available about their journalism background. Consider evaluating their sources and fact-checking their claims."
    
    def _handle_anonymous_author(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle anonymous or staff authors with educational context"""
        return {
            'service': self.service_name,
            'success': True,
            'data': {
                'score': 20,
                'level': 'Anonymous',
                'findings': [{
                    'type': 'author',
                    'severity': 'high',
                    'text': '⚠️ No author attribution provided',
                    'finding': 'Anonymous Article',
                    'visual': {'icon': 'alert', 'color': 'red'}
                }],
                'summary': 'This article lacks author attribution, making it impossible to verify the writer\'s credibility or expertise.',
                'educational_insights': [{
                    'type': 'learn',
                    'icon': '💡',
                    'title': 'Why Bylines Matter',
                    'content': 'Author bylines create accountability. Anonymous articles should be evaluated extra carefully, checking sources and cross-referencing claims.'
                }],
                'credibility_score': 20,
                'author_name': 'Unknown',
                'verification_status': {'verified': False, 'anonymous': True}
            }
        }
    
    # Helper methods
    def _format_author_name(self, author: str) -> str:
        """Format author name for display"""
        return ' '.join(word.capitalize() for word in author.split())
    
    def _get_career_milestone(self, years: int) -> Dict[str, Any]:
        """Get career milestone based on years"""
        for milestone in reversed(self.career_milestones):
            if years >= milestone['years']:
                return milestone
        return self.career_milestones[0]
    
    def _calculate_publication_score(self, profile: Dict[str, Any]) -> int:
        """Calculate score based on publication quality"""
        score = 0
        for pub in profile.get('publications', []):
            pub_info = self.publication_scores.get(pub['name'], {})
            score += pub_info.get('score', 50)
        return min(100, score // max(1, len(profile.get('publications', [1]))))
    
    def _calculate_consistency_score(self, profile: Dict[str, Any]) -> int:
        """Calculate consistency score"""
        # Reward consistent byline usage and regular publishing
        base_score = 50
        if profile.get('years_experience', 0) > 2:
            base_score += 20
        if len(profile.get('expertise_areas', [])) > 0:
            base_score += 20
        if profile.get('verified'):
            base_score += 10
        return min(100, base_score)
    
    def _create_trust_timeline(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create timeline visualization data"""
        timeline = []
        current_year = datetime.now().year
        years_exp = profile.get('years_experience', 0)
        
        if years_exp > 0:
            start_year = current_year - years_exp
            
            # Add key milestones
            timeline.append({
                'year': start_year,
                'event': 'Started journalism career',
                'icon': '🌱',
                'impact': 'neutral'
            })
            
            # Add expertise development
            for area in profile.get('expertise_areas', [])[:2]:
                timeline.append({
                    'year': start_year + area.get('years', 1),
                    'event': f'Began covering {area["topic"]}',
                    'icon': self.expertise_icons.get(area['topic'], '📰'),
                    'impact': 'positive'
                })
            
            # Add awards
            for award in profile.get('awards', []):
                timeline.append({
                    'year': current_year - 2,  # Approximate
                    'event': f'Won {award}',
                    'icon': '🏆',
                    'impact': 'major'
                })
        
        return sorted(timeline, key=lambda x: x['year'])
    
    def _assign_badges(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assign visual badges based on achievements"""
        badges = []
        
        if profile.get('verified'):
            badges.append({
                'id': 'verified',
                'name': 'Verified Journalist',
                'icon': '✓',
                'color': 'green'
            })
        
        if profile.get('years_experience', 0) >= 10:
            badges.append({
                'id': 'veteran',
                'name': 'Veteran Reporter',
                'icon': '⭐',
                'color': 'gold'
            })
        
        if profile.get('awards'):
            badges.append({
                'id': 'award_winner',
                'name': 'Award Winner',
                'icon': '🏆',
                'color': 'gold'
            })
        
        if len(profile.get('expertise_areas', [])) > 0:
            badges.append({
                'id': 'specialist',
                'name': 'Subject Specialist',
                'icon': '🎯',
                'color': 'blue'
            })
        
        return badges
    
    def _generate_narrative(self, profile: Dict[str, Any]) -> str:
        """Generate a narrative description of the author's credibility journey"""
        parts = []
        
        name = profile['display_name']
        
        # Opening
        if profile.get('verified'):
            parts.append(f"{name} is a verified journalist")
        else:
            parts.append(f"{name} is a journalist")
        
        # Experience
        years = profile.get('years_experience', 0)
        if years > 15:
            parts.append(f"with over {years} years of distinguished service")
        elif years > 5:
            parts.append(f"with {years} years of solid experience")
        elif years > 0:
            parts.append(f"with {years} years in the field")
        
        # Expertise
        if profile.get('expertise_areas'):
            top_area = profile['expertise_areas'][0]['topic']
            parts.append(f"specializing in {top_area}")
        
        # Awards
        if profile.get('awards'):
            parts.append(f"and recipient of {len(profile['awards'])} major awards")
        
        return ' '.join(parts) + '.'
    
    # Existing methods continue...
    def _check_journalist_database(self, author: str) -> Optional[Dict[str, Any]]:
        """Check if author is in enhanced journalist database"""
        author_lower = author.lower().strip()
        
        # Direct lookup
        if author_lower in self.journalist_db:
            return self.journalist_db[author_lower].copy()
        
        # Partial match
        for db_name, info in self.journalist_db.items():
            if author_lower in db_name or db_name in author_lower:
                return info.copy()
        
        return None
    
    def _fetch_article_history(self, author: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch article history from NewsAPI"""
        if not self.news_api_key:
            return None
        
        # Check cache
        cache_key = f"author_{author.lower()}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        try:
            articles = []
            
            # Search for articles by this author
            url = "https://newsapi.org/v2/everything"
            params = {
                'apiKey': self.news_api_key,
                'q': f'"{author}"',
                'searchIn': 'author',
                'sortBy': 'publishedAt',
                'pageSize': 100,
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Cache the result
                self._cache_result(cache_key, articles)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching article history: {e}")
            return None
    
    def _analyze_article_history(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze article history for patterns and expertise"""
        if not articles:
            return {}
        
        analysis = {
            'total_articles': len(articles),
            'publications': defaultdict(int),
            'topics': defaultdict(int),
            'timeline': []
        }
        
        # Analyze each article
        for article in articles:
            # Track publications
            source = article.get('source', {}).get('name', 'Unknown')
            analysis['publications'][source] += 1
            
            # Extract topics from title and description
            text = f"{article.get('title', '')} {article.get('description', '')}"
            topics = self._extract_topics(text)
            for topic in topics:
                analysis['topics'][topic] += 1
            
            # Build timeline
            pub_date = article.get('publishedAt')
            if pub_date:
                analysis['timeline'].append(pub_date)
        
        # Calculate years of experience
        if analysis['timeline']:
            oldest = min(analysis['timeline'])
            newest = max(analysis['timeline'])
            oldest_date = datetime.fromisoformat(oldest.replace('Z', '+00:00'))
            newest_date = datetime.fromisoformat(newest.replace('Z', '+00:00'))
            years = (newest_date - oldest_date).days / 365.25
            analysis['years_experience'] = max(1, int(years))
        
        return analysis
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()
        
        # Topic keywords mapping
        topic_keywords = {
            'Politics': ['election', 'president', 'congress', 'senate', 'political', 'government', 'democracy'],
            'Technology': ['tech', 'software', 'ai', 'artificial intelligence', 'computer', 'digital', 'cyber'],
            'Business': ['business', 'economy', 'market', 'finance', 'company', 'corporate', 'stock'],
            'Health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'treatment', 'covid'],
            'Climate': ['climate', 'environment', 'warming', 'carbon', 'renewable', 'sustainability'],
            'Science': ['science', 'research', 'study', 'scientist', 'discovery', 'experiment']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:3]  # Return top 3 topics
    
    def _analyze_expertise_areas(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze and structure expertise areas"""
        topics = profile.get('topics', {})
        if not topics:
            return []
        
        expertise_areas = []
        
        # Sort topics by frequency
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        
        for topic, count in sorted_topics[:5]:
            # Calculate approximate years covering this topic
            years = min(profile.get('years_experience', 1), count // 10 + 1)
            
            expertise_areas.append({
                'topic': topic,
                'article_count': count,
                'years': years,
                'level': 'Expert' if count > 30 else 'Specialist' if count > 10 else 'Familiar'
            })
        
        return expertise_areas
    
    def _analyze_publications(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze publication history"""
        pubs = profile.get('publications', {})
        if not pubs:
            return []
        
        publications = []
        
        # Sort by article count
        sorted_pubs = sorted(pubs.items(), key=lambda x: x[1], reverse=True)
        
        for pub_name, count in sorted_pubs[:5]:
            pub_info = self.publication_scores.get(pub_name, {})
            
            publications.append({
                'name': pub_name,
                'article_count': count,
                'tier': pub_info.get('tier', 'Standard'),
                'trust_score': pub_info.get('score', 70),
                'primary': count == sorted_pubs[0][1]  # Is this their primary publication?
            })
        
        return publications
    
    def _create_career_timeline(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create career timeline data"""
        return {
            'start_year': datetime.now().year - profile.get('years_experience', 0),
            'milestones': self._create_trust_timeline(profile),
            'current_status': self._determine_author_level(profile)
        }
    
    def _determine_verification_status(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Determine detailed verification status"""
        return {
            'verified': profile.get('verified', False),
            'verification_source': 'journalist_database' if profile.get('verified') else None,
            'confidence': 'high' if profile.get('verified') else 'medium' if profile.get('years_experience', 0) > 2 else 'low',
            'factors': {
                'has_byline': True,
                'in_database': profile.get('verified', False),
                'has_history': profile.get('total_articles', 0) > 0,
                'consistent_name': True  # Could be enhanced with name variation checking
            }
        }
    
    def _generate_visual_elements(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visual elements for UI"""
        return {
            'primary_badge': self._determine_author_level(profile),
            'trust_badges': self._assign_badges(profile),
            'expertise_icons': [
                {
                    'topic': area['topic'],
                    'icon': self.expertise_icons.get(area['topic'], '📰'),
                    'count': area['article_count']
                }
                for area in profile.get('expertise_areas', [])[:3]
            ],
            'publication_logos': [
                {
                    'name': pub['name'],
                    'color': self.publication_scores.get(pub['name'], {}).get('trust_color', '#666')
                }
                for pub in profile.get('publications', [])[:3]
            ]
        }
    
    def _calculate_trust_indicators(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed trust indicators"""
        return {
            'identity_verified': profile.get('verified', False),
            'experience_depth': min(100, profile.get('years_experience', 0) * 10),
            'expertise_focus': len(profile.get('expertise_areas', [])) > 0,
            'publication_quality': self._calculate_publication_score(profile),
            'consistency_score': self._calculate_consistency_score(profile),
            'transparency_level': 'high' if profile.get('verified') else 'medium'
        }
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if available"""
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return result
        return None
    
    def _cache_result(self, cache_key: str, result: Any):
        """Cache result"""
        self.cache[cache_key] = (time.time(), result)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Visual credibility assessment',
                'Career timeline visualization',
                'Expertise area mapping',
                'Trust badge assignment',
                'Publication history analysis',
                'Educational insights',
                'Interactive credibility story',
                'Award recognition'
            ],
            'visual_elements': len(self.expertise_icons),
            'journalists_in_database': len(self.journalist_db),
            'trust_badges_available': len(self.trust_badges)
        })
        return info
