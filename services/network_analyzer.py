# services/network_analyzer.py
"""
Network Analysis Service
Analyzes connections, citations, and link networks in articles
"""

import re
import logging
from typing import Dict, List, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    """Analyze network connections and citations in articles"""
    
    def analyze(self, article_data):
        """
        Analyze network connections in article
        
        Args:
            article_data: Dictionary containing article information
            
        Returns:
            Dictionary with network analysis
        """
        content = article_data.get('content') or article_data.get('text', '')
        links = article_data.get('links', [])
        
        if not content and not links:
            return self._get_empty_analysis()
        
        # Extract citations
        citations = self._extract_citations(content)
        
        # Analyze links
        link_analysis = self._analyze_links(links)
        
        # Extract references to other articles/sources
        references = self._extract_references(content)
        
        # Analyze connection patterns
        connection_patterns = self._analyze_connection_patterns(content)
        
        # Calculate network metrics
        metrics = self._calculate_network_metrics(citations, link_analysis, references)
        
        return {
            'citations': citations,
            'links': link_analysis,
            'references': references,
            'connection_patterns': connection_patterns,
            'metrics': metrics,
            'network_quality': self._assess_network_quality(metrics)
        }
    
    def _extract_citations(self, text):
        """Extract citations from text"""
        citations = []
        
        # Academic-style citations (Year)
        year_citations = re.findall(r'\((\d{4})\)', text)
        for year in year_citations:
            if 1900 <= int(year) <= 2030:  # Reasonable year range
                citations.append({
                    'type': 'year_only',
                    'year': year,
                    'context': self._get_context(text, year)
                })
        
        # Author (Year) style
        author_year = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\((\d{4})\)', text)
        for author, year in author_year:
            citations.append({
                'type': 'author_year',
                'author': author,
                'year': year,
                'context': self._get_context(text, f"{author} ({year})")
            })
        
        # "According to" style citations
        according_to = re.findall(r'[Aa]ccording to ([^,\.]+)', text)
        for source in according_to:
            if len(source) < 100:  # Avoid capturing entire sentences
                citations.append({
                    'type': 'attribution',
                    'source': source.strip(),
                    'context': self._get_context(text, f"according to {source}")
                })
        
        # Study/Research citations
        study_patterns = [
            r'[Aa] study (?:by|from|conducted by) ([^,\.]+)',
            r'[Rr]esearch (?:by|from|conducted by) ([^,\.]+)',
            r'[Aa] report (?:by|from) ([^,\.]+)'
        ]
        
        for pattern in study_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) < 100:
                    citations.append({
                        'type': 'study',
                        'source': match.strip(),
                        'context': self._get_context(text, match)
                    })
        
        # Remove duplicates
        seen = set()
        unique_citations = []
        for cite in citations:
            key = f"{cite.get('type')}_{cite.get('source', '')}_{cite.get('year', '')}"
            if key not in seen:
                seen.add(key)
                unique_citations.append(cite)
        
        return unique_citations[:20]  # Limit to 20 citations
    
    def _analyze_links(self, links):
        """Analyze external links"""
        if not links:
            return {
                'total': 0,
                'internal': 0,
                'external': 0,
                'domains': [],
                'link_types': {}
            }
        
        internal_links = 0
        external_links = 0
        domains = {}
        link_types = {
            'news': 0,
            'social_media': 0,
            'academic': 0,
            'government': 0,
            'other': 0
        }
        
        for link in links:
            if isinstance(link, str):
                url = link
            elif isinstance(link, dict) and 'url' in link:
                url = link['url']
            else:
                continue
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            # Count domains
            domains[domain] = domains.get(domain, 0) + 1
            
            # Categorize link type
            if any(social in domain for social in ['twitter.com', 'facebook.com', 'linkedin.com', 'instagram.com']):
                link_types['social_media'] += 1
            elif domain.endswith('.gov') or '.gov.' in domain:
                link_types['government'] += 1
            elif domain.endswith('.edu') or '.edu.' in domain or 'scholar' in domain:
                link_types['academic'] += 1
            elif any(news in domain for news in ['cnn.', 'bbc.', 'reuters.', 'nytimes.', 'wsj.']):
                link_types['news'] += 1
            else:
                link_types['other'] += 1
        
        # Get top domains
        top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total': len(links),
            'internal': internal_links,
            'external': len(links) - internal_links,
            'domains': [{'domain': d[0], 'count': d[1]} for d in top_domains],
            'link_types': link_types
        }
    
    def _extract_references(self, text):
        """Extract references to other articles/sources"""
        references = []
        
        # References to other articles
        article_refs = re.findall(r'(?:earlier|previous|recent)\s+(?:article|report|story)', text, re.IGNORECASE)
        references.extend([{'type': 'article_reference', 'text': ref} for ref in article_refs])
        
        # References to organizations
        org_patterns = [
            r'The\s+([A-Z][A-Za-z\s]+(?:Institute|Foundation|Center|Organisation|Organization|Agency))',
            r'([A-Z]{2,})\s+(?:reported|announced|stated)'
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            for match in matches[:5]:  # Limit to avoid too many
                references.append({
                    'type': 'organization',
                    'name': match.strip()
                })
        
        return references
    
    def _analyze_connection_patterns(self, text):
        """Analyze how ideas are connected in the text"""
        patterns = {
            'causal_connections': 0,
            'comparative_connections': 0,
            'temporal_connections': 0,
            'contradictory_connections': 0
        }
        
        # Causal connections
        causal_words = ['because', 'therefore', 'thus', 'consequently', 'as a result', 'leads to', 'causes']
        for word in causal_words:
            patterns['causal_connections'] += len(re.findall(rf'\b{word}\b', text, re.IGNORECASE))
        
        # Comparative connections
        comparative_words = ['compared to', 'in contrast', 'whereas', 'unlike', 'similar to', 'likewise']
        for word in comparative_words:
            patterns['comparative_connections'] += len(re.findall(rf'\b{word}\b', text, re.IGNORECASE))
        
        # Temporal connections
        temporal_words = ['before', 'after', 'during', 'meanwhile', 'subsequently', 'prior to']
        for word in temporal_words:
            patterns['temporal_connections'] += len(re.findall(rf'\b{word}\b', text, re.IGNORECASE))
        
        # Contradictory connections
        contradictory_words = ['however', 'but', 'although', 'despite', 'nevertheless', 'yet']
        for word in contradictory_words:
            patterns['contradictory_connections'] += len(re.findall(rf'\b{word}\b', text, re.IGNORECASE))
        
        return patterns
    
    def _calculate_network_metrics(self, citations, link_analysis, references):
        """Calculate network quality metrics"""
        metrics = {
            'citation_count': len(citations),
            'link_count': link_analysis['total'],
            'reference_count': len(references),
            'source_diversity': len(set(c.get('source', '') for c in citations if c.get('source'))),
            'link_diversity': len(link_analysis.get('domains', [])),
            'academic_sources': sum(1 for c in citations if c['type'] in ['author_year', 'study']),
            'news_sources': link_analysis['link_types'].get('news', 0),
            'government_sources': link_analysis['link_types'].get('government', 0)
        }
        
        # Calculate overall network score
        network_score = 0
        if metrics['citation_count'] > 0:
            network_score += 20
        if metrics['link_count'] > 0:
            network_score += 20
        if metrics['source_diversity'] >= 3:
            network_score += 20
        if metrics['academic_sources'] > 0:
            network_score += 20
        if metrics['government_sources'] > 0:
            network_score += 20
        
        metrics['network_score'] = network_score
        
        return metrics
    
    def _assess_network_quality(self, metrics):
        """Assess overall network quality"""
        score = metrics['network_score']
        
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        elif score >= 20:
            return 'poor'
        else:
            return 'very poor'
    
    def _get_context(self, text, search_term):
        """Get context around a search term"""
        index = text.lower().find(search_term.lower())
        if index == -1:
            return ""
        
        start = max(0, index - 50)
        end = min(len(text), index + len(search_term) + 50)
        
        return "..." + text[start:end].strip() + "..."
    
    def _get_empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'citations': [],
            'links': {
                'total': 0,
                'internal': 0,
                'external': 0,
                'domains': [],
                'link_types': {}
            },
            'references': [],
            'connection_patterns': {
                'causal_connections': 0,
                'comparative_connections': 0,
                'temporal_connections': 0,
                'contradictory_connections': 0
            },
            'metrics': {
                'citation_count': 0,
                'link_count': 0,
                'reference_count': 0,
                'source_diversity': 0,
                'link_diversity': 0,
                'network_score': 0
            },
            'network_quality': 'very poor'
        }
