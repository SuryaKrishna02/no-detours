"""
utils/helpers.py
Utility functions for handling date parsing, formatting, and data conversion operations.
These helpers support the travel planner application with common data manipulation tasks.
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, Optional

def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object using multiple common formats.
    
    Args:
        date_str (str): The date string to parse
        
    Returns:
        Optional[datetime]: A datetime object if parsing succeeds, None otherwise
    """
    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%d %b %Y"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None

def extract_date_range(dates_str: str) -> Dict[str, datetime]:
    """
    Extract start and end dates from a date range string.
    
    Attempts to identify date ranges separated by common delimiters or 
    extract up to two dates using regular expressions.
    
    Args:
        dates_str (str): String containing date range information
        
    Returns:
        Dict[str, datetime]: Dictionary with 'start_date' and 'end_date' keys,
                             values are datetime objects or None if parsing fails
    """
    result = {
        "start_date": None,
        "end_date": None
    }
    
    # Try to split by common separators
    separators = [" to ", " - ", " – ", " through ", " til ", " until "]
    date_parts = []
    
    for sep in separators:
        if sep in dates_str:
            date_parts = dates_str.split(sep, 1)
            break
    
    if not date_parts:
        # Try to find dates using regex
        date_matches = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|\b\w+\s+\d{1,2},\s+\d{4}\b|\b\d{1,2}\s+\w+\s+\d{4}\b', dates_str)
        date_parts = date_matches if len(date_matches) <= 2 else date_matches[:2]
    
    if len(date_parts) >= 1:
        result["start_date"] = parse_date_string(date_parts[0])
        
        if len(date_parts) >= 2:
            result["end_date"] = parse_date_string(date_parts[1])
    
    return result

def format_itinerary_as_html(itinerary: str) -> str:
    """
    Convert a plain text itinerary to HTML format for improved display.
    
    Converts newlines to <br> tags, formats day headings, and converts
    bullet lists to HTML unordered lists.
    
    Args:
        itinerary (str): Plain text itinerary
        
    Returns:
        str: HTML-formatted version of the itinerary
    """
    # Replace newlines with <br>
    html = itinerary.replace('\n', '<br>')
    
    # Make headings
    html = re.sub(r'(Day \d+:.*?)(<br>)', r'<h3>\1</h3>', html)
    html = re.sub(r'(#+)\s+(.*?)(<br>)', lambda m: f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>', html)
    
    # Format lists
    html = re.sub(r'- (.*?)(<br>)', r'<li>\1</li>', html)
    html = html.replace('<li>', '<ul><li>').replace('</li><br><li>', '</li><li>').replace('</li><br></ul>', '</li></ul>')
    
    return html

def safe_json_loads(json_str: str, default_value: Any = None) -> Any:
    """
    Safely parse a JSON string with a fallback default value on error.
    
    Args:
        json_str (str): JSON string to parse
        default_value (Any, optional): Value to return if parsing fails.
                                      Defaults to None (returns empty dict if None)
        
    Returns:
        Any: Parsed JSON object or default value on failure
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return default_value if default_value is not None else {}
    
def set_to_list_converter(obj):
    """
    Custom JSON serializer for handling set objects.
    
    Converts Python set objects to lists for JSON serialization.
    Used as the 'default' parameter in json.dumps().
    
    Args:
        obj: Object to convert
        
    Returns:
        list: List representation of a set
        
    Raises:
        TypeError: If the object is not a set
    """
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")