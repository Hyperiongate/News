"""
Author Analyzer Profile Matching Fix
CRITICAL FIX: Prevents matching wrong LinkedIn profiles like in the logs

This is a patch that should be added to your services/author_analyzer.py file
in the comprehensive research method that was returning wrong LinkedIn profiles.
"""

def _search_linkedin_profile_fixed(self, author_name: str) -> Optional[str]:
    """
    FIXED: LinkedIn profile search with proper name validation
    Prevents returning profiles for different people
    """
    if not author_name or author_name.lower() in ['unknown', 'anonymous', '']:
        return None
    
    try:
        # Clean and normalize author name for search
        clean_name = self._clean_author_name(author_name)
        if not clean_name or len(clean_name) < 3:
            self.logger.warning(f"Author name too short or invalid: {author_name}")
            return None
        
        # Search for LinkedIn profile
        search_query = f'"{clean_name}" site:linkedin.com/in journalist writer author reporter'
        
        # Use SerpAPI or web search
        if hasattr(self, 'serpapi_key') and self.serpapi_key:
            results = self._search_with_serpapi(search_query)
        else:
            results = self._search_with_requests(search_query)
        
        # CRITICAL FIX: Validate profile matches before returning
        for result in results:
            profile_url = result.get('url', '')
            profile_title = result.get('title', '')
            
            if 'linkedin.com/in/' not in profile_url:
                continue
            
            # CRITICAL: Check if the profile actually matches the author
            if self._validate_linkedin_profile_match(clean_name, profile_url, profile_title):
                self.logger.info(f"Found validated LinkedIn profile for {author_name}: {profile_url}")
                return profile_url
            else:
                self.logger.warning(f"LinkedIn profile rejected for {author_name} - name mismatch: {profile_url}")
        
        self.logger.info(f"No matching LinkedIn profile found for {author_name}")
        return None
        
    except Exception as e:
        self.logger.error(f"LinkedIn search failed for {author_name}: {e}")
        return None

def _clean_author_name(self, name: str) -> str:
    """Clean author name for search"""
    if not name:
        return ""
    
    # Remove common prefixes/suffixes
    prefixes = ['by ', 'author: ', 'written by ', 'reporter: ']
    suffixes = [' | cnn', ' | reuters', ' | ap', ' - cnn', ' - reuters']
    
    clean = name.lower().strip()
    
    for prefix in prefixes:
        if clean.startswith(prefix):
            clean = clean[len(prefix):].strip()
    
    for suffix in suffixes:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)].strip()
    
    # Remove extra whitespace and normalize
    clean = ' '.join(clean.split())
    
    # Convert back to title case
    return clean.title()

def _validate_linkedin_profile_match(self, author_name: str, profile_url: str, profile_title: str) -> bool:
    """
    CRITICAL FIX: Validate that LinkedIn profile actually matches the author
    This prevents the wrong profile matching issue from your logs
    """
    try:
        # Extract name components
        author_parts = set(author_name.lower().split())
        author_parts = {part for part in author_parts if len(part) > 2}  # Remove short words
        
        # Extract profile name from URL and title
        profile_name_parts = set()
        
        # From URL: linkedin.com/in/john-doe-123 -> john doe
        url_path = profile_url.split('/in/')[-1].split('?')[0].split('-')
        url_name_parts = {part.lower() for part in url_path if part.isalpha() and len(part) > 2}
        profile_name_parts.update(url_name_parts)
        
        # From title: "John Doe - Senior Writer at CNN | LinkedIn"
        if profile_title:
            title_clean = profile_title.replace(' | LinkedIn', '').replace(' - LinkedIn', '')
            # Split on common separators
            for separator in [' - ', ' | ', ' at ', ' @', ',']:
                title_clean = title_clean.split(separator)[0]
            
            title_parts = {part.lower().strip() for part in title_clean.split() 
                          if part.isalpha() and len(part) > 2}
            profile_name_parts.update(title_parts)
        
        # CRITICAL VALIDATION: Check if author name parts match profile
        if not author_parts:
            self.logger.warning(f"No valid author name parts found: {author_name}")
            return False
        
        if not profile_name_parts:
            self.logger.warning(f"No valid profile name parts found: {profile_url}")
            return False
        
        # Calculate match ratio
        matching_parts = author_parts.intersection(profile_name_parts)
        match_ratio = len(matching_parts) / len(author_parts)
        
        # STRICT MATCHING: Require at least 70% of author name parts to match
        min_match_ratio = 0.7
        
        if match_ratio >= min_match_ratio:
            self.logger.info(f"Profile validation PASSED: {author_name} -> {profile_url} (match: {match_ratio:.2f})")
            return True
        else:
            self.logger.warning(f"Profile validation FAILED: {author_name} -> {profile_url} (match: {match_ratio:.2f})")
            self.logger.warning(f"  Author parts: {author_parts}")
            self.logger.warning(f"  Profile parts: {profile_name_parts}")
            self.logger.warning(f"  Matching: {matching_parts}")
            return False
            
    except Exception as e:
        self.logger.error(f"Profile validation error: {e}")
        return False

def _comprehensive_research_fixed(self, author_name: str) -> Dict[str, Any]:
    """
    FIXED: Comprehensive author research with proper profile matching
    This replaces the method that was returning wrong LinkedIn profiles
    """
    research_data = {
        'linkedin_profile': None,
        'wikipedia_page': None,
        'personal_website': None,
        'muckrack_profile': None,
        'profile_links': []
    }
    
    if not author_name or author_name.lower() in ['unknown', 'anonymous', '']:
        self.logger.info("Skipping research for unknown author")
        return research_data
    
    self.logger.info(f"Starting comprehensive research for author: {author_name}")
    
    try:
        # 1. FIXED LinkedIn Search
        linkedin_url = self._search_linkedin_profile_fixed(author_name)
        if linkedin_url:
            research_data['linkedin_profile'] = linkedin_url
            research_data['profile_links'].append({
                'type': 'linkedin',
                'url': linkedin_url,
                'verified': True  # We validated it
            })
        
        # 2. Wikipedia Search (less risky, keep existing logic)
        wikipedia_url = self._search_wikipedia_page(author_name)
        if wikipedia_url:
            research_data['wikipedia_page'] = wikipedia_url
            research_data['profile_links'].append({
                'type': 'wikipedia',
                'url': wikipedia_url,
                'verified': True
            })
        
        # 3. Personal Website Search (add validation)
        website_url = self._search_personal_website_validated(author_name)
        if website_url:
            research_data['personal_website'] = website_url
            research_data['profile_links'].append({
                'type': 'website',
                'url': website_url,
                'verified': True
            })
        
        # 4. Muck Rack Search (journalist database - safer)
        muckrack_url = self._search_muckrack_profile(author_name)
        if muckrack_url:
            research_data['muckrack_profile'] = muckrack_url
            research_data['profile_links'].append({
                'type': 'muckrack',
                'url': muckrack_url,
                'verified': True
            })
        
        profiles_found = len(research_data['profile_links'])
        self.logger.info(f"Research completed for {author_name}: {profiles_found} profiles found")
        
        if profiles_found == 0:
            self.logger.info(f"No verified profiles found for {author_name}")
        
        return research_data
        
    except Exception as e:
        self.logger.error(f"Comprehensive research failed for {author_name}: {e}")
        return research_data

def _search_personal_website_validated(self, author_name: str) -> Optional[str]:
    """
    Search for personal website with validation to prevent wrong matches
    """
    try:
        # Search for personal website/blog
        search_query = f'"{author_name}" personal website OR blog journalist -twitter -linkedin -facebook'
        
        results = self._search_with_requests(search_query) if hasattr(self, '_search_with_requests') else []
        
        for result in results[:5]:  # Check first 5 results
            url = result.get('url', '')
            title = result.get('title', '')
            
            # Skip social media and news sites
            skip_domains = [
                'twitter.com', 'linkedin.com', 'facebook.com', 'instagram.com',
                'cnn.com', 'reuters.com', 'bbc.com', 'nytimes.com', 'washingtonpost.com'
            ]
            
            if any(domain in url.lower() for domain in skip_domains):
                continue
            
            # Look for personal indicators in URL or title
            personal_indicators = ['blog', 'personal', author_name.lower().replace(' ', '')]
            
            if any(indicator in url.lower() or indicator in title.lower
