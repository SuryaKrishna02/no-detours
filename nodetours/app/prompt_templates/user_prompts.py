# app/prompt_templates/user_prompts.py
def feature_extraction_prompt(user_input: str) -> str:
    return f"""
    Extract travel features from the following user input:
    
    {user_input}
    """

def query_generation_prompt(features: dict) -> str:
    return f"""
    Generate search queries based on these travel features:
    
    Place to visit: {features.get('place_to_visit', 'Not specified')}
    Duration (days): {features.get('duration_days') or 'Not specified'}
    Cuisine preferences: {', '.join(features.get('cuisine_preferences', []) or []) or 'Not specified'}
    Place preferences: {', '.join(features.get('place_preferences', []) or []) or 'Not specified'}
    Transport preferences: {features.get('transport_preferences') or 'Not specified'}
    """

def itinerary_generation_prompt(features: dict, context: dict) -> str:
    # Prepare context for the prompt
    search_context = ""
    for query_results in context.get("search_results", []):
        search_context += f"Query: {query_results['query']}\n"
        for result in query_results.get("results", []):
            search_context += f"- {result.get('title', '')}: {result.get('snippet', '')}\n"
    
    weather_context = ""
    if context.get("weather_info"):
        weather = context["weather_info"]
        weather_context = f"Weather forecast for {features.get('place_to_visit', '')}: {weather}"
    
    return f"""
    Please create a travel itinerary for me based on the following information:
    
    ## My Travel Details
    Destination: {features.get('place_to_visit', 'Not specified')}
    Duration: {features.get('duration_days', 'Not specified')} days
    Cuisine Preferences: {', '.join(features.get('cuisine_preferences', []) or []) or 'Not specified'}
    Place Preferences: {', '.join(features.get('place_preferences', []) or []) or 'Not specified'}
    Transport Preferences: {features.get('transport_preferences', 'Not specified')}
    
    ## Destination Information
    {search_context}
    
    ## Weather Information
    {weather_context}
    """

def packing_list_prompt(features: dict, weather_info: dict) -> str:
    weather_summary = str(weather_info)  # Simplified for demo
    
    return f"""
    Please create a packing list for a trip to {features.get('place_to_visit', '')}.
    
    Trip details:
    - Duration: {features.get('duration_days', 'Not specified')} days
    - Weather: {weather_summary}
    - Activities: {', '.join(features.get('place_preferences', []) or []) or 'Not specified'}
    - Food interests: {', '.join(features.get('cuisine_preferences', []) or []) or 'Not specified'}
    """

def budget_estimation_prompt(features: dict) -> str:
    return f"""
    Please estimate a budget for a trip to {features.get('place_to_visit', '')}.
    
    Trip details:
    - Duration: {features.get('duration_days', 'Not specified')} days
    - Transportation: {features.get('transport_preferences') or 'Public transportation and walking'}
    - Activities: {', '.join(features.get('place_preferences', []) or []) or 'General sightseeing'}
    - Food interests: {', '.join(features.get('cuisine_preferences', []) or []) or 'Local cuisine'}
    """

def calendar_generation_prompt(itinerary: str, start_date: str) -> str:
    return f"""
    Please generate calendar events for the following travel itinerary.
    The trip starts on {start_date}.
    
    Itinerary:
    {itinerary}
    """

def evaluation_prompt(itinerary: str, features: dict, metric: str) -> str:
    return f"""
    Here are the user's travel details:
    
    Destination: {features.get('place_to_visit', 'Not specified')}
    Duration: {features.get('duration_days', 'Not specified')} days
    Cuisine Preferences: {', '.join(features.get('cuisine_preferences', []) or []) or 'Not specified'}
    Place Preferences: {', '.join(features.get('place_preferences', []) or []) or 'Not specified'}
    Transport Preferences: {features.get('transport_preferences', 'Not specified')}
    
    Here is the generated itinerary:
    
    {itinerary}
    
    Please rate this itinerary on '{metric}' according to the criteria.
    """