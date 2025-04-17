# app/utils/helpers.py
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

def parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse a date string into a datetime object."""
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
    """Extract start and end dates from a date range string."""
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
    """Format a text itinerary as HTML for better display."""
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
    """Safely load a JSON string with a default fallback."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return default_value if default_value is not None else {}