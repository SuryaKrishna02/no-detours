# app/modules/search_query_generator.py
import json
import logging
import re
from typing import Dict, List, Any
from api.llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchQueryGenerator:
    """Generates search queries based on extracted features."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        logger.info("Initialized Search Query Generator with provider")
    
    def generate_queries(self, features: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate a list of search queries based on extracted features.
        
        Args:
            features: Dict with extracted travel features
            
        Returns:
            List of dictionaries containing feature type, value, and search query
        """
        logger.info("Generating search queries based on extracted features")
        
        system_prompt = """
        You are a search query generator for a travel planning assistant.
        Your task is to create effective search queries based on extracted travel features.
        Generate search queries that will retrieve relevant information for each feature.
        
        Return a JSON array of objects, each containing:
        - "feature_type": The type of feature (place_to_visit, cuisine_preferences, place_preferences, transport_preferences)
        - "feature_value": The specific value of the feature
        - "search_query": An effective search query to get information about this feature
        
        For example:
        [
          {
            "feature_type": "place_to_visit",
            "feature_value": "Paris",
            "search_query": "Best time to visit Paris for tourists travel guide"
          },
          {
            "feature_type": "cuisine_preferences",
            "feature_value": "local food",
            "search_query": "Most authentic local food restaurants in Paris for tourists"
          }
        ]
        
        Return only the JSON, with no additional text.
        """
        
        # Format the features for the prompt
        place_to_visit = features.get('place_to_visit', '')
        if not place_to_visit:
            logger.warning("No destination specified in features")
            return self._generate_fallback_queries(features)
        
        duration_days = features.get('duration_days')
        cuisine_preferences = features.get('cuisine_preferences', [])
        place_preferences = features.get('place_preferences', [])
        transport_preferences = features.get('transport_preferences', '')
        
        user_prompt = f"""
        Generate search queries based on these travel features:
        
        Place to visit: {place_to_visit}
        Duration (days): {duration_days if duration_days is not None else 'Not specified'}
        Cuisine preferences: {', '.join(cuisine_preferences) if cuisine_preferences else 'Not specified'}
        Place preferences: {', '.join(place_preferences) if place_preferences else 'Not specified'}
        Transport preferences: {transport_preferences if transport_preferences else 'Not specified'}
        
        Create at least one query for the place to visit, and one query for each preference if specified.
        Each query should be specifically designed to retrieve the most relevant information for planning a trip.
        """
        
        try:
            logger.info("Sending query generation request to LLM")
            query_list = self.llm_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            logger.info(f"Received LLM response: {query_list[:100]}...")
            
            # Try to parse JSON
            try:
                queries = json.loads(query_list)
                
                # Validate queries
                if isinstance(queries, list) and all(
                    isinstance(q, dict) and 
                    "feature_type" in q and 
                    "feature_value" in q and 
                    "search_query" in q 
                    for q in queries
                ):
                    logger.info(f"Generated {len(queries)} search queries")
                    return queries
                else:
                    logger.warning("LLM returned invalid query list format")
                    return self._generate_fallback_queries(features)
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}", exc_info=True)
                
                # Try to extract JSON from the response (in case LLM added text)
                json_pattern = r'(\[[\s\S]*\])'
                match = re.search(json_pattern, query_list)
                
                if match:
                    try:
                        logger.info("Attempting to extract JSON array from response")
                        return json.loads(match.group(1))
                    except json.JSONDecodeError:
                        logger.error("Failed to parse extracted JSON array", exc_info=True)
                
                return self._generate_fallback_queries(features)
        
        except Exception as e:
            logger.error(f"Error in query generation: {e}", exc_info=True)
            return self._generate_fallback_queries(features)
    
    def _generate_fallback_queries(self, features: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate fallback queries when LLM fails."""
        logger.info("Using fallback query generation")
        
        queries = []
        place_to_visit = features.get('place_to_visit', '')
        
        if not place_to_visit:
            return [
                {
                    "feature_type": "general",
                    "feature_value": "travel",
                    "search_query": "popular tourist destinations"
                },
                {
                    "feature_type": "general",
                    "feature_value": "travel planning",
                    "search_query": "travel planning tips"
                }
            ]
        
        # Basic destination query
        queries.append({
            "feature_type": "place_to_visit",
            "feature_value": place_to_visit,
            "search_query": f"top attractions in {place_to_visit} tourist guide"
        })
        
        # Weather/best time query
        queries.append({
            "feature_type": "place_to_visit",
            "feature_value": place_to_visit,
            "search_query": f"best time to visit {place_to_visit} weather guide"
        })
        
        # Transportation query
        transport_preferences = features.get('transport_preferences', '')
        if transport_preferences:
            queries.append({
                "feature_type": "transport_preferences",
                "feature_value": transport_preferences,
                "search_query": f"{transport_preferences} options in {place_to_visit} for tourists"
            })
        else:
            queries.append({
                "feature_type": "transport_preferences",
                "feature_value": "public transport",
                "search_query": f"how to get around {place_to_visit} public transportation"
            })
        
        # Cuisine preferences queries
        cuisine_preferences = features.get('cuisine_preferences', [])
        if cuisine_preferences:
            for cuisine in cuisine_preferences:
                queries.append({
                    "feature_type": "cuisine_preferences",
                    "feature_value": cuisine,
                    "search_query": f"best {cuisine} in {place_to_visit} for tourists"
                })
        else:
            queries.append({
                "feature_type": "cuisine_preferences",
                "feature_value": "local food",
                "search_query": f"must try local food in {place_to_visit} for tourists"
            })
        
        # Place preferences queries
        place_preferences = features.get('place_preferences', [])
        if place_preferences:
            for preference in place_preferences:
                queries.append({
                    "feature_type": "place_preferences",
                    "feature_value": preference,
                    "search_query": f"best {preference} in {place_to_visit} tourist guide"
                })
        
        return queries