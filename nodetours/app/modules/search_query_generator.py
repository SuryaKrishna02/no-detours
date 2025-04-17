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
    
    def generate_queries(self, features: Dict[str, Any]) -> List[str]:
        """
        Generate a list of search queries based on extracted features.
        
        Args:
            features: Dict with extracted travel features
            
        Returns:
            List of search queries
        """
        logger.info("Generating search queries based on extracted features")
        
        system_prompt = """
        You are a search query generator for a travel planning assistant.
        Your task is to create effective search queries based on extracted travel features.
        Generate multiple search queries that will retrieve relevant information for:
        
        1. Destination information and top attractions
        2. Weather information for the travel dates
        3. Transportation options
        4. Accommodation options
        5. Activity recommendations based on user preferences
        
        Return a JSON array of search query strings, with no additional text.
        Limit to 5-7 queries that cover the most important aspects.
        """
        
        # Format the features for the prompt
        destination = features.get('destination', '')
        if not destination:
            logger.warning("No destination specified in features")
            return self._generate_fallback_queries(features)
        
        dates = features.get('dates', '')
        duration = features.get('duration', '')
        preferences = features.get('preferences', [])
        constraints = features.get('constraints', [])
        transportation = features.get('transportation', '')
        accommodation = features.get('accommodation', '')
        weather_concerns = features.get('weather_concerns', False)
        travel_group = features.get('travel_group', '')
        
        user_prompt = f"""
        Generate search queries based on these travel features:
        
        Destination: {destination}
        Dates: {dates}
        Duration: {duration}
        Preferences: {', '.join(preferences) if preferences else 'Not specified'}
        Constraints: {', '.join(constraints) if constraints else 'Not specified'}
        Transportation: {transportation}
        Accommodation: {accommodation}
        Weather concerns: {'Yes' if weather_concerns else 'No'}
        Travel group: {travel_group}
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
                if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
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
    
    def _generate_fallback_queries(self, features: Dict[str, Any]) -> List[str]:
        """Generate fallback queries when LLM fails."""
        logger.info("Using fallback query generation")
        
        queries = []
        destination = features.get('destination', '')
        
        if not destination:
            return [
                "popular tourist destinations",
                "travel planning tips",
                "best vacation spots this year"
            ]
        
        # Basic destination queries
        queries.append(f"top attractions in {destination}")
        queries.append(f"things to do in {destination}")
        
        # Weather query if relevant
        dates = features.get('dates', '')
        if dates:
            queries.append(f"weather in {destination} {dates}")
        else:
            queries.append(f"best time to visit {destination}")
        
        # Transportation query
        transportation = features.get('transportation', '')
        if transportation:
            queries.append(f"{transportation} options in {destination}")
        else:
            queries.append(f"how to get around {destination}")
        
        # Accommodation query
        accommodation = features.get('accommodation', '')
        if accommodation:
            queries.append(f"{accommodation} in {destination}")
        else:
            queries.append(f"best places to stay in {destination}")
        
        # Preference-based queries
        preferences = features.get('preferences', [])
        if preferences:
            # Choose up to 2 preferences to avoid too many queries
            for preference in preferences[:2]:
                queries.append(f"best {preference} in {destination}")
        
        # Travel group specific query
        travel_group = features.get('travel_group', '')
        if travel_group:
            if "family" in travel_group.lower() or "kids" in travel_group.lower() or "children" in travel_group.lower():
                queries.append(f"family-friendly activities in {destination}")
            elif "couple" in travel_group.lower():
                queries.append(f"romantic things to do in {destination}")
            elif "solo" in travel_group.lower():
                queries.append(f"solo travel tips for {destination}")
            elif "friends" in travel_group.lower():
                queries.append(f"group activities in {destination}")
        
        return queries