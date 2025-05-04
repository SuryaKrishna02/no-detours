# app/modules/search_query_extractor.py
import json
import logging
import re
from typing import Dict, Any, List, Optional, Union
from api.llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchQueryExtractor:
    """Extracts search features from user text input."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        logger.info("Initialized Search Query Feature Extractor with provider")
    
    def extract_features(self, user_input: str) -> Dict[str, Any]:
        """
        Extract relevant travel features from user input.
        
        Returns:
            Dict with extracted features like place_to_visit, duration_days, cuisine_preferences, etc.
        """
        logger.info("Extracting travel features from user input")

        # First try to extract using LLM
        try:
            features = self._extract_with_llm(user_input)
            logger.info(f"Successfully extracted features with LLM: {features}")
            return features
        except Exception as e:
            logger.error(f"Error in LLM feature extraction: {e}", exc_info=True)
            
            # Fallback to regex-based extraction
            features = self._extract_features_fallback(user_input)
            logger.info(f"Extracted features with fallback: {features}")
            return features
    
    def _extract_with_llm(self, user_input: str) -> Dict[str, Any]:
        """Extract features using LLM."""
        system_prompt = """
        You are a feature extraction system for a travel planning assistant.
        Your task is to identify and extract key travel information from user input.
        Return a JSON object with the following fields:
        
        - place_to_visit: The main travel destination (city, country, or location) - REQUIRED
        - duration_days: Length of stay as an integer (e.g., 7) - Optional, can be null
        - cuisine_preferences: List of food and drink preferences - Optional, can be null
        - place_preferences: List of activity or place preferences (museums, beaches, etc.) - Optional, can be null
        - transport_preferences: Preferred mode of transport - Optional, can be null
        
        For any fields not mentioned in the input, use null.
        Provide only the JSON, with no additional text.
        """
        
        user_prompt = f"""
        Extract travel features from the following user input:
        
        {user_input}
        
        IMPORTANT: For place_to_visit, this field is REQUIRED. If it is not specified in the user input, 
        provide a reasonable assumption based on context.
        """
        
        extracted_features = self.llm_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        logger.info(f"Received LLM response: {extracted_features[:100]}...")
        
        # Try to parse JSON
        try:
            features = json.loads(extracted_features)
            logger.info(f"Successfully parsed features: {features}")
            
            # Validate and ensure required fields have values
            features = self._validate_and_fill_features(features, user_input)
            
            return features
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}", exc_info=True)
            
            # Try to extract JSON from the response (in case LLM added text)
            json_pattern = r'(\{[\s\S]*\})'
            match = re.search(json_pattern, extracted_features)
            
            if match:
                try:
                    logger.info("Attempting to extract JSON from response")
                    features = json.loads(match.group(1))
                    return self._validate_and_fill_features(features, user_input)
                except json.JSONDecodeError:
                    logger.error("Failed to parse extracted JSON", exc_info=True)
            
            # If JSON parsing fails, raise exception to trigger fallback
            raise ValueError("Failed to extract features from LLM response")
    
    def _validate_and_fill_features(self, features: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Validate features and fill in missing required fields."""
        
        # Ensure basic structure exists
        if not isinstance(features, dict):
            features = {}
        
        # Check for required field: place_to_visit
        if "place_to_visit" not in features or not features["place_to_visit"]:
            logger.warning("Required field place_to_visit missing or empty - using fallback")
            features["place_to_visit"] = self._extract_destination_fallback(user_input) or "Unknown destination"
        
        # Ensure lists for array fields or null if not present
        list_fields = ["cuisine_preferences", "place_preferences"]
        for field in list_fields:
            if field not in features:
                features[field] = None
            elif features[field] and not isinstance(features[field], list):
                features[field] = [features[field]]
            elif features[field] is not None and not features[field]:  # Empty list
                features[field] = None
        
        # Ensure duration_days is an integer or null
        if "duration_days" in features and features["duration_days"] is not None:
            try:
                features["duration_days"] = int(features["duration_days"])
            except (ValueError, TypeError):
                features["duration_days"] = None
        else:
            # Try to extract from user input
            duration = self._extract_duration_fallback(user_input)
            if duration:
                try:
                    days_match = re.search(r'(\d+)', duration)
                    if days_match:
                        features["duration_days"] = int(days_match.group(1))
                    else:
                        features["duration_days"] = None
                except:
                    features["duration_days"] = None
            else:
                features["duration_days"] = None
        
        # Handle transport_preferences
        if "transport_preferences" not in features:
            features["transport_preferences"] = None
            
        return features
    
    def _extract_destination_fallback(self, user_input: str) -> str:
        """Extract destination as fallback when LLM fails."""
        destination_patterns = [
            r'to\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'visiting\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'trip\s+to\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'vacation\s+in\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'travel(?:ing)?\s+to\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'itinerary\s+for\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)',
            r'plan\s+(?:a|my)?\s+(?:trip|visit)\s+(?:to)?\s+([A-Za-z\s]+)(?:,|\s+in|\s+for|\s+on|\.)'
        ]
        
        for pattern in destination_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown destination"  # Default value if no pattern matches
    
    def _extract_duration_fallback(self, user_input: str) -> str:
        """Extract duration as fallback when LLM fails."""
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
                return f"{match.group(1)} days"
        
        return ""  # No duration found
    
    def _extract_features_fallback(self, user_input: str) -> Dict[str, Any]:
        """Manual feature extraction as fallback when LLM fails."""
        logger.info("Using fallback feature extraction")
        
        features = {
            "place_to_visit": "",
            "duration_days": None,
            "cuisine_preferences": None,
            "place_preferences": None,
            "transport_preferences": None
        }
        
        # Extract place to visit (destination)
        place_to_visit = self._extract_destination_fallback(user_input)
        if place_to_visit and place_to_visit != "Unknown destination":
            features["place_to_visit"] = place_to_visit
        
        # Extract duration
        duration_str = self._extract_duration_fallback(user_input)
        if duration_str:
            days_match = re.search(r'(\d+)', duration_str)
            if days_match:
                features["duration_days"] = int(days_match.group(1))
        
        # Extract cuisine preferences
        cuisine_keywords = [
            'food', 'cuisine', 'restaurant', 'dining', 'eat', 'meal',
            'breakfast', 'lunch', 'dinner', 'snack', 'cafe', 'wine',
            'beer', 'drink', 'bar', 'pub', 'street food', 'local food',
            'traditional food', 'culinary', 'gastronomy', 'thai food'
        ]
        
        cuisine_matches = []
        for keyword in cuisine_keywords:
            if re.search(r'\b' + keyword + r'[s]?\b', user_input, re.IGNORECASE):
                cuisine_matches.append(keyword)
        
        if cuisine_matches:
            features["cuisine_preferences"] = cuisine_matches
        
        # Extract place preferences
        place_keywords = [
            'museum', 'art', 'history', 'beach', 'hiking', 'nature',
            'shopping', 'nightlife', 'adventure', 'relax', 'culture',
            'sightseeing', 'tour', 'park', 'festival', 'concert',
            'sport', 'outdoor', 'photography', 'historical', 'site',
            'monument', 'temple', 'church', 'cathedral', 'palace',
            'castle', 'ruin', 'ancient', 'market', 'water sport',
            'water sports', 'night market', 'activity', 'beaches'
        ]
        
        place_matches = []
        for keyword in place_keywords:
            if re.search(r'\b' + keyword + r'[s]?\b', user_input, re.IGNORECASE):
                place_matches.append(keyword)
        
        if place_matches:
            features["place_preferences"] = place_matches
        
        # Extract transport preferences
        transport_keywords = [
            'transport', 'bus', 'train', 'subway', 'metro', 'taxi',
            'car', 'rental', 'bike', 'walking', 'public transport',
            'tram', 'ferry', 'boat', 'scooter', 'motorcycle'
        ]
        
        for keyword in transport_keywords:
            if re.search(r'\b' + keyword + r'[s]?\b', user_input, re.IGNORECASE):
                features["transport_preferences"] = keyword
                break
        
        return features