"""
FILE: services/source_credibility.py
LOCATION: news/services/source_credibility.py
PURPOSE: Database of known news source credibility ratings
DEPENDENCIES: None
SERVICE: Source credibility database
"""

# Known source credibility database
SOURCE_CREDIBILITY = {
    # High credibility sources
    'reuters.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
    'apnews.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
    'bbc.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'bbc.co.uk': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'npr.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'pbs.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'wsj.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Business News'},
    'bloomberg.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Business News'},
    'nature.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Scientific'},
    'science.org': {'credibility': 'High', 'bias': 'Center', 'type': 'Scientific'},
    'nytimes.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'washingtonpost.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'theguardian.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'economist.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Magazine'},
    
    # Medium credibility sources
    'cnn.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Cable News'},
    'foxnews.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Cable News'},
    'msnbc.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Cable News'},
    'usatoday.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Newspaper'},
    'politico.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital Media'},
    'thehill.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital Media'},
    'axios.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital Media'},
    'businessinsider.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'Business News'},
    'forbes.com': {'credibility': 'Medium', 'bias': 'Center-Right', 'type': 'Business Magazine'},
    'vox.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'slate.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'reason.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Magazine'},
    
    # Lower credibility sources
    'buzzfeed.com': {'credibility': 'Low', 'bias': 'Left', 'type': 'Digital Media'},
    'breitbart.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital Media'},
    'dailywire.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital Media'},
    'occupydemocrats.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital Media'},
    'thegatewaypundit.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital Media'},
    'commondreams.org': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital Media'},
    
    # Very low credibility sources
    'infowars.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
    'naturalnews.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
    'beforeitsnews.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
    'yournewswire.com': {'credibility': 'Very Low', 'bias': 'Mixed', 'type': 'Fake News'},
    'worldnewsdailyreport.com': {'credibility': 'Very Low', 'bias': 'Mixed', 'type': 'Satire/Fake'},
    
    # Tech news (generally reliable)
    'techcrunch.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Tech News'},
    'theverge.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Tech News'},
    'arstechnica.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Tech News'},
    'wired.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Tech Magazine'},
    
    # International sources
    'aljazeera.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'International'},
    'rt.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
    'sputniknews.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
    'xinhuanet.com': {'credibility': 'Low', 'bias': 'Pro-China', 'type': 'State Media'},
    'dw.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Public Media'},
    'france24.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Public Media'},
}

def get_source_info(domain):
    """Get credibility info for a domain"""
    return SOURCE_CREDIBILITY.get(domain, {
        'credibility': 'Unknown',
        'bias': 'Unknown',
        'type': 'Unknown'
    })

def get_all_sources():
    """Get all sources in the database"""
    return SOURCE_CREDIBILITY

def get_sources_by_credibility(credibility_level):
    """Get all sources with a specific credibility level"""
    return {
        domain: info 
        for domain, info in SOURCE_CREDIBILITY.items() 
        if info['credibility'] == credibility_level
    }

def get_sources_by_bias(bias_type):
    """Get all sources with a specific bias"""
    return {
        domain: info 
        for domain, info in SOURCE_CREDIBILITY.items() 
        if info['bias'] == bias_type
    }
