"""
psuti1s.regex
------------
Some regex helper functions.
"""

import re

def find_matches(pattern, text):
    """Return all matches of pattern in text."""
    return re.findall(pattern, text)
