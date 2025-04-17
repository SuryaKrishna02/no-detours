# app/modules/search_query_extractor.py
import json
import logging
import re
from typing import Dict, Any
from api.llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchQueryExtractor:
    """Extracts search features from user text input."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def extract_features(self, user_input: str) -> Dict[str, Any]:
        """
        Extract relevant travel features from user input.
        
        Returns:
            Dict with extracted features like destination, dates, preferences, etc.
        """
        logger.info("Extracting travel features from user input")
        
        system_prompt = """
        You are a feature extraction system for a travel planning assistant.
        Your task is to identify and extract key travel information from user input.
        Return a JSON object with the following fields (leave empty if not present):
        
        - destination: The main travel destination (city, country, or location)
        - dates: Travel dates (start and end)
        - duration: Length of stay (in days)
        - preferences: List of activities or themes the user wants (nature, culture, food, etc.)
        - constraints: Any limitations (budget, accessibility, etc.)
        - transportation: Preferred mode of transport
        - accommodation: Preferred type of lodging
        - weather_concerns: If the user mentions weather preferences or concerns
        - travel_group: Who is traveling (solo, couple, family with kids, etc.)
        
        Provide only the JSON, with no additional text.
        """
        
        user_prompt = f"""
        Extract travel features from the following user input:
        
        {user_input}
        """
        
        try:
            logger.info("Sending feature extraction request to LLM")
            extracted_features = self.llm_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            logger.info(f"Received LLM response: {extracted_features[:100]}...")
            
            # Try to parse JSON
            try:
                return json.loads(extracted_features)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}", exc_info=True)
                
                # Try to extract JSON from the response (in case LLM added text)
                json_pattern = r'(\{[\s\S]*\})'
                match = re.search(json_pattern, extracted_features)
                
                if match:
                    try:
                        logger.info("Attempting to extract JSON from response")
                        return json.loads(match.group(1))
                    except json.JSONDecodeError:
                        logger.error("Failed to parse extracted JSON", exc_info=True)
                
                # Manual extraction as fallback
                return self._extract_features_fallback(user_input)
        
        except Exception as e:
            logger.error(f"Error in feature extraction: {e}", exc_info=True)
            return self._extract_features_fallback(user_input)
    
    def _extract_features_fallback(self, user_input: str) -> Dict[str, Any]:
        """Manual feature extraction as fallback when LLM fails."""
        logger.info("Using fallback feature extraction")
        
        features = {
            "destination": "",
            "dates": "",
            "duration": "",
            "preferences": [],
            "constraints": [],
            "transportation": "",
            "accommodation": "",
            "weather_concerns": False,
            "travel_group": ""
        }
        
        # Extract destination
        destination_patterns = [
            r'to\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'visiting\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'trip\s+to\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'vacation\s+in\s+([A-Za-z\s]+)(?:,|\s+for|\s+on|\.)',
            r'travel(?:ing)?\s+to\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)'
        ]
        
        for pattern in destination_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                features["destination"] = match.group(1).strip()
                break
        
        # Extract duration
        duration_patterns = [
            r'(\d+)\s+day(?:s)?',
            r'(\d+)-day',
            r'for\s+(\d+)\s+day(?:s)?',
            r'for\s+(\d+)\s+night(?:s)?',
            r'for\s+about\s+(\d+)\s+day(?:s)?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                features["duration"] = f"{match.group(1)} days"
                break
        
        # Extract dates (simplified)
        date_patterns = [
            r'(?:in|during|on)\s+(January|February|March|April|May|June|July|August|September|October|November|December)',
            r'(?:in|during|on)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            r'(?:from|between)\s+([A-Za-z]+\s+\d{1,2})(?:\s*-\s*|\s+to\s+)([A-Za-z]+\s+\d{1,2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    features["dates"] = match.group(1)
                elif len(match.groups()) == 2:
                    features["dates"] = f"{match.group(1)} to {match.group(2)}"
                break
        
        # Extract preferences
        preference_keywords = [
            'museum', 'art', 'history', 'beach', 'hiking', 'nature', 'food', 'dining',
            'restaurant', 'shopping', 'nightlife', 'adventure', 'relax', 'culture',
            'sightseeing', 'tour', 'local', 'authentic', 'park', 'festival', 'concert',
            'sport', 'outdoor', 'photography'
        ]
        
        for keyword in preference_keywords:
            if re.search(r'\b' + keyword + r'(\w*)\b', user_input, re.IGNORECASE):
                features["preferences"].append(keyword)
        
        # Extract travel group
        group_patterns = [
            (r'\b(?:with|and)\s+(?:my)?\s*family\b', 'family'),
            (r'\b(?:with|and)\s+(?:my)?\s*kids\b', 'family with kids'),
            (r'\b(?:with|and)\s+(?:my)?\s*child(?:ren)?\b', 'family with kids'),
            (r'\b(?:with|and)\s+(?:my)?\s*partner\b', 'couple'),
            (r'\b(?:with|and)\s+(?:my)?\s*spouse\b', 'couple'),
            (r'\b(?:with|and)\s+(?:my)?\s*husband\b', 'couple'),
            (r'\b(?:with|and)\s+(?:my)?\s*wife\b', 'couple'),
            (r'\b(?:with|and)\s+(?:my)?\s*girlfriend\b', 'couple'),
            (r'\b(?:with|and)\s+(?:my)?\s*boyfriend\b', 'couple'),
            (r'\b(?:with|and)\s+friends\b', 'friends'),
            (r'\bsolo\b', 'solo'),
            (r'\balone\b', 'solo'),
            (r'\bby myself\b', 'solo')
        ]
        
        for pattern, group_type in group_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                features["travel_group"] = group_type
                break
        
        # Weather concerns
        weather_keywords = ['weather', 'rain', 'temperature', 'hot', 'cold', 'humid', 'snow', 'sunny', 'warm']
        for keyword in weather_keywords:
            if re.search(r'\b' + keyword + r'\b', user_input, re.IGNORECASE):
                features["weather_concerns"] = True
                break
        
        return features