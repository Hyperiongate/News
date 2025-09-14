#!/usr/bin/env python3
"""
Script to fix the broken _get_domain_credibility_tier method in app.py
Run this in the same directory as your app.py file
"""

import re

# Read the current app.py file
with open('app.py', 'r') as f:
    content = f.read()

# Find and replace the broken method
# We'll look for the method definition and replace everything up to the next method or class

# The correct implementation of the method
correct_method = '''    def _get_domain_credibility_tier(self, domain: str) -> str:
        """Get credibility tier of the domain with better matching"""
        domain_lower = domain.lower().replace('www.', '')
        
        # First check direct domain mapping
        if domain_lower in self.domain_mapping:
            org_name = self.domain_mapping[domain_lower]
            
            # Check which tier the organization belongs to
            for org in self.credible_orgs['high']:
                if org.lower() == org_name.lower():
                    return 'high'
            
            for org in self.credible_orgs['medium']:
                if org.lower() == org_name.lower():
                    return 'medium'
        
        # Fallback to checking if org name is in domain
        for org in self.credible_orgs['high']:
            if org.lower().replace(' ', '') in domain_lower:
                return 'high'
        
        for org in self.credible_orgs['medium']:
            if org.lower().replace(' ', '') in domain_lower:
                return 'medium'
        
        return 'unknown'
'''

# Use regex to find and replace the broken method
# Look for the method definition and replace everything until the next method definition
pattern = r'(    def _get_domain_credibility_tier\(self, domain: str\) -> str:.*?)(?=\n    def |\n\nclass |\Z)'

# Replace the broken method with the correct one
fixed_content = re.sub(pattern, correct_method, content, flags=re.DOTALL)

# Check if the replacement was made
if fixed_content != content:
    # Save the fixed content
    with open('app.py', 'w') as f:
        f.write(fixed_content)
    print("✓ Fixed the _get_domain_credibility_tier method in app.py")
    print("✓ File saved successfully")
    print("\nNow commit and push to GitHub:")
    print("  git add app.py")
    print("  git commit -m 'Fix syntax error in _get_domain_credibility_tier method'")
    print("  git push")
else:
    print("✗ Could not find the broken method to fix")
    print("The pattern might have changed. Manual fix required.")
    
    # Try to at least find where line 1487 is
    lines = content.split('\n')
    if len(lines) >= 1487:
        print(f"\nLine 1487 content: {lines[1486]}")
        print(f"Line 1488 content: {lines[1487] if len(lines) > 1487 else 'EOF'}")
        
        # Provide manual fix instructions
        print("\nMANUAL FIX:")
        print("1. Open app.py")
        print("2. Go to line 1487")
        print("3. Find the _get_domain_credibility_tier method")
        print("4. Replace the entire method with this correct version:")
        print("-" * 50)
        print(correct_method)
        print("-" * 50)
