"""
Planner Agent - Central controller that orchestrates trip planning
"""
from typing import Dict, Any
import autogen
from config.llm_config import get_llm_config, MAX_ITERATIONS
from tools.weather_tool import get_weather_info
from tools.search_tool import search_activities


class PlannerAgent:
    """Central planner agent that coordinates trip planning"""
    
    def __init__(self):
        """Initialize the planner agent"""
        self.llm_config = get_llm_config()
        
        # Create planner assistant with concise system message for faster processing
        self.assistant = autogen.AssistantAgent(
            name="travel_planner",
            system_message="""Create concise day-by-day travel itineraries with Morning/Afternoon/Evening activities, meals, and tips. 
            Be realistic with time allocations. Write in a friendly, narrative style. End with TERMINATE.""",
            llm_config=self.llm_config,
        )
        
        # Create user proxy
        self.user_proxy = autogen.UserProxyAgent(
            name="planner_user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=MAX_ITERATIONS,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
            llm_config=self.llm_config,
        )
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register tools with the planner agent"""
        def weather_tool(destination: str, date: str = None) -> str:
            """Get weather information for a destination. Essential for planning outdoor activities and packing recommendations."""
            try:
                weather = get_weather_info(destination, date)
                return (
                    f"Weather in {weather['destination']}:\n"
                    f"Temperature: {weather['temperature']}\n"
                    f"Condition: {weather['condition']}\n"
                    f"Humidity: {weather['humidity']}\n"
                    f"Wind: {weather['wind_speed']}\n"
                    f"Recommendation: {weather['recommendation']}"
                )
            except Exception as e:
                return f"Error getting weather: {str(e)}"
        
        def activity_search_tool(destination: str, activity_type: str = None) -> str:
            """Search for activities, attractions, restaurants, and things to do in a destination. Use this to find what's available to visit."""
            try:
                results = search_activities(destination, activity_type)
                if results.get("activities"):
                    activities_list = "\n\n".join([
                        f"• {act['name']} ({act.get('type', 'activity')})\n  {act.get('description', '')}"
                        for act in results["activities"]
                    ])
                    return f"Found {results['count']} activities in {destination}:\n\n{activities_list}"
                else:
                    return f"Activities search completed for {destination}"
            except Exception as e:
                return f"Error searching activities: {str(e)}"
        
        # Register functions with AutoGen 0.2.0 API
        # Functions are registered with user_proxy for execution
        self.user_proxy.register_function(
            function_map={
                "weather_tool": weather_tool,
                "activity_search_tool": activity_search_tool,
            }
        )
    
    def create_itinerary(self, destination: str, duration: int, activity_data: str = None, weather_data: str = None) -> Dict[str, Any]:
        """
        Create a trip itinerary
        
        Args:
            destination: Destination name
            duration: Number of days
            activity_data: Optional pre-researched activity data
            weather_data: Optional pre-researched weather data
        
        Returns:
            Dictionary containing the itinerary
        """
        try:
            # Create ultra-concise prompt for fastest LLM response
            prompt = f"Create {duration}-day itinerary for {destination}."
            if weather_data:
                # Extract only key info
                if 'Temperature' in weather_data:
                    temp = weather_data.split('Temperature:')[1].split('\n')[0].strip()[:20] if 'Temperature:' in weather_data else ""
                    prompt += f" Weather: {temp}"
            if activity_data:
                # Use only first activity name
                first_activity = activity_data.split('•')[1].split('-')[0].strip()[:30] if '•' in activity_data else ""
                if first_activity:
                    prompt += f" Activities: {first_activity}..."
            
            prompt += " Format: Day X - Morning/Afternoon/Evening. Include meals. TERMINATE."
            
            self.user_proxy.initiate_chat(
                self.assistant,
                message=prompt,
                max_turns=1  # Single turn for fastest response
            )
            
            messages = self.user_proxy.chat_messages[self.assistant]
            if messages:
                itinerary = messages[-1].get("content", "")
                
                return {
                    "success": True,
                    "destination": destination,
                    "duration": duration,
                    "itinerary": itinerary
                }
            else:
                return {
                    "success": False,
                    "error": "No response from planner agent"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

