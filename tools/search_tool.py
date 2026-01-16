"""
Web Search Tool - Uses DuckDuckGo for activity research
"""
from typing import Dict, Any, List
from duckduckgo_search import DDGS
from config.llm_config import SEARCH_TIMEOUT, MAX_SEARCH_RESULTS
import time

# Simple in-memory cache for search results (expires after 1 hour)
_search_cache = {}
_cache_timestamps = {}


def search_web(query: str, max_results: int = None) -> Dict[str, Any]:
    """
    Search the web using DuckDuckGo for travel-related information.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
    
    Returns:
        Dictionary containing search results
    """
    if max_results is None:
        max_results = MAX_SEARCH_RESULTS
    
    # Check cache first (cache valid for 1 hour)
    cache_key = f"{query}_{max_results}"
    current_time = time.time()
    if cache_key in _search_cache:
        cache_age = current_time - _cache_timestamps.get(cache_key, 0)
        if cache_age < 3600:  # 1 hour cache
            return _search_cache[cache_key]
    
    try:
        results = []
        # Use timeout to fail fast if search is slow
        start_time = time.time()
        with DDGS(timeout=SEARCH_TIMEOUT) as ddgs:
            # Search for the query with timeout
            search_results = list(ddgs.text(query, max_results=max_results))
            
            # Limit processing time - if taking too long, use what we have
            for result in search_results:
                if time.time() - start_time > SEARCH_TIMEOUT:
                    break
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("body", "")[:200],  # Limit snippet length
                    "url": result.get("href", "")
                })
        
        result_dict = {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        }
        
        # Cache the result
        _search_cache[cache_key] = result_dict
        _cache_timestamps[cache_key] = current_time
        
        return result_dict
    
    except Exception as e:
        # Fallback to curated data if search fails
        return {
            "success": False,
            "query": query,
            "count": 0,
            "results": [],
            "error": str(e),
            "fallback": _get_fallback_data(query)
        }


def search_activities(destination: str, activity_type: str = None) -> Dict[str, Any]:
    """
    Search for activities and attractions in a destination.
    
    Args:
        destination: Name of the destination
        activity_type: Optional filter (e.g., "museums", "restaurants", "parks")
    
    Returns:
        Dictionary containing activities
    """
    # Check cache first
    cache_key = f"activities_{destination}_{activity_type or 'general'}"
    current_time = time.time()
    if cache_key in _search_cache:
        cache_age = current_time - _cache_timestamps.get(cache_key, 0)
        if cache_age < 3600:  # 1 hour cache
            return _search_cache[cache_key]
    
    # Construct search query
    if activity_type:
        query = f"{activity_type} in {destination} travel attractions"
    else:
        query = f"top attractions things to do in {destination} travel guide"
    
    # Perform web search with timeout
    try:
        search_result = search_web(query, max_results=MAX_SEARCH_RESULTS)
    except Exception:
        # If search fails, use fallback immediately
        search_result = {
            "success": False,
            "query": query,
            "count": 0,
            "results": [],
            "fallback": _get_fallback_data(query)
        }
    
    # Extract and structure activity information
    activities = []
    if search_result.get("success") and search_result.get("results"):
        for result in search_result["results"]:
            activities.append({
                "name": result.get("title", ""),
                "description": result.get("snippet", ""),
                "source": result.get("url", ""),
                "type": activity_type or "general"
            })
    
    # If search failed, use fallback
    if not activities and search_result.get("fallback"):
        activities = search_result["fallback"]
    
    result_dict = {
        "destination": destination,
        "activity_type": activity_type or "general",
        "count": len(activities),
        "activities": activities,
        "search_successful": search_result.get("success", False)
    }
    
    # Cache the result
    _search_cache[cache_key] = result_dict
    _cache_timestamps[cache_key] = current_time
    
    return result_dict


def _get_fallback_data(query: str) -> List[Dict[str, Any]]:
    """Fallback curated data when web search fails"""
    # Extract destination from query
    dest_lower = query.lower()
    
    # Curated activities for popular destinations
    fallback_db = {
        "paris": [
            {"name": "Eiffel Tower", "description": "Iconic iron lattice tower, symbol of Paris", "type": "landmark"},
            {"name": "Louvre Museum", "description": "World's largest art museum with Mona Lisa", "type": "museum"},
            {"name": "Notre-Dame Cathedral", "description": "Gothic cathedral on Île de la Cité", "type": "landmark"},
            {"name": "Seine River Cruise", "description": "Scenic boat tour along the Seine", "type": "activity"},
            {"name": "Montmartre", "description": "Artistic hilltop district with Sacré-Cœur", "type": "neighborhood"},
        ],
        "tokyo": [
            {"name": "Senso-ji Temple", "description": "Ancient Buddhist temple in Asakusa", "type": "temple"},
            {"name": "Tokyo Skytree", "description": "Tallest tower in Japan with observation decks", "type": "landmark"},
            {"name": "Shibuya Crossing", "description": "World's busiest pedestrian intersection", "type": "landmark"},
            {"name": "Tsukiji Fish Market", "description": "Famous seafood market (outer market)", "type": "market"},
            {"name": "Meiji Shrine", "description": "Shinto shrine surrounded by forest", "type": "temple"},
        ],
    }
    
    # Try to match destination
    for dest, activities in fallback_db.items():
        if dest in dest_lower:
            return activities
    
    # Generic fallback
    return [
        {"name": "City Center", "description": "Explore the main city center area", "type": "general"},
        {"name": "Local Museum", "description": "Visit the main local museum", "type": "museum"},
        {"name": "Historic District", "description": "Walk through historic neighborhoods", "type": "general"},
    ]

