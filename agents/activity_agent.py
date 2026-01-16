"""
Activity Research Agent - Specialized agent for finding activities and attractions
"""
from typing import Dict, Any
import autogen
from config.llm_config import get_llm_config, MAX_ITERATIONS
from tools.search_tool import search_activities, search_web


class ActivityAgent:
    """AutoGen agent specialized in activity research"""
    
    def __init__(self):
        """Initialize the activity agent"""
        self.llm_config = get_llm_config()
        
        # Create activity research assistant
        self.assistant = autogen.AssistantAgent(
            name="activity_researcher",
            system_message="""You are an expert travel activity researcher.
            Your role is to find and research attractions, restaurants, cultural sites, and activities for destinations.
            Use web search to find current, accurate information about:
            - Popular tourist attractions
            - Local restaurants and food experiences
            - Cultural sites and museums
            - Outdoor activities and parks
            - Entertainment and nightlife
            - Shopping areas
            Provide structured, detailed information about each activity including descriptions and why they're worth visiting.""",
            llm_config=self.llm_config,
        )
        
        # Create user proxy
        self.user_proxy = autogen.UserProxyAgent(
            name="activity_user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=MAX_ITERATIONS,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
            llm_config=self.llm_config,
        )
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register search tools with the agent"""
        def activity_search_tool(destination: str, activity_type: str = None) -> str:
            """Search for activities, attractions, and things to do in a destination. Returns a list of activities with descriptions."""
            try:
                results = search_activities(destination, activity_type)
                if results.get("activities"):
                    activities_list = "\n\n".join([
                        f"• {act['name']} ({act.get('type', 'activity')})\n  {act.get('description', 'No description available')}"
                        for act in results["activities"]
                    ])
                    return f"Found {results['count']} activities in {destination}:\n\n{activities_list}"
                else:
                    return f"No activities found for {destination}. Try a different search query."
            except Exception as e:
                return f"Error searching activities: {str(e)}"
        
        def web_search_tool(query: str) -> str:
            """General web search for travel information. Use this to find specific information about destinations, restaurants, events, etc."""
            try:
                results = search_web(query)
                if results.get("success") and results.get("results"):
                    search_summary = "\n\n".join([
                        f"• {r['title']}\n  {r['snippet'][:200]}..."
                        for r in results["results"][:3]
                    ])
                    return f"Search results for '{query}':\n\n{search_summary}"
                else:
                    return f"No results found for '{query}'"
            except Exception as e:
                return f"Error performing search: {str(e)}"
        
        # Register functions with AutoGen 0.2.0 API
        self.user_proxy.register_function(
            function_map={
                "activity_search_tool": activity_search_tool,
                "web_search_tool": web_search_tool,
            }
        )
    
    def research_activities(self, destination: str, activity_types: list = None) -> Dict[str, Any]:
        """
        Research activities for a destination
        
        Args:
            destination: Destination name
            activity_types: Optional list of activity types to search for
        
        Returns:
            Dictionary with activity research results
        """
        try:
            # Direct tool call - much faster than agent conversation
            activities_data = search_activities(destination, activity_types[0] if activity_types else None)
            
            # Format the results directly without LLM call - limit to top 5 for speed
            if activities_data.get("activities"):
                activities_list = "\n\n".join([
                    f"• {act['name']} - {act.get('description', 'Popular attraction')[:80]}"
                    for act in activities_data["activities"][:5]  # Limit to top 5 for speed
                ])
                research_text = f"Top activities in {destination}:\n{activities_list}"
            else:
                research_text = f"Popular attractions and activities in {destination}."
            
            return {
                "success": True,
                "destination": destination,
                "research_report": research_text,
                "activities_data": activities_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

