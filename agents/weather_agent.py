"""
Weather Agent - Specialized agent for weather information
"""
from typing import Dict, Any
import autogen
from config.llm_config import get_llm_config, MAX_ITERATIONS
from tools.weather_tool import get_weather_info


class WeatherAgent:
    """AutoGen agent specialized in weather information"""
    
    def __init__(self):
        """Initialize the weather agent"""
        self.llm_config = get_llm_config()
        
        # Create weather assistant agent
        self.assistant = autogen.AssistantAgent(
            name="weather_specialist",
            system_message="""You are a weather information specialist for travel planning.
            Your role is to provide accurate weather information and recommendations for destinations.
            Always use the weather tool to get current weather data.
            Provide clear, actionable weather-based recommendations for travelers.
            Consider how weather affects outdoor activities, packing, and daily planning.""",
            llm_config=self.llm_config,
        )
        
        # Create user proxy
        self.user_proxy = autogen.UserProxyAgent(
            name="weather_user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=MAX_ITERATIONS,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
            llm_config=self.llm_config,
        )
        
        # Register weather tool
        self._register_tool()
    
    def _register_tool(self):
        """Register weather tool with the agent"""
        def weather_tool(destination: str, date: str = None) -> str:
            """Get weather information for a destination. Returns temperature, conditions, humidity, and recommendations."""
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
        
        # Register function with AutoGen 0.2.0 API
        self.user_proxy.register_function(
            function_map={"weather_tool": weather_tool}
        )
    
    def get_weather_report(self, destination: str, date: str = None) -> Dict[str, Any]:
        """
        Get weather report for a destination
        
        Args:
            destination: Destination name
            date: Optional date
        
        Returns:
            Dictionary with weather information
        """
        try:
            # Direct tool call - much faster than agent conversation
            raw_weather = get_weather_info(destination, date)
            
            # Create a simple formatted report without LLM call
            weather_text = f"""Weather in {raw_weather.get('destination', destination)}:
Temperature: {raw_weather.get('temperature', 'N/A')}
Condition: {raw_weather.get('condition', 'N/A')}
Humidity: {raw_weather.get('humidity', 'N/A')}
Wind Speed: {raw_weather.get('wind_speed', 'N/A')}

Recommendation: {raw_weather.get('recommendation', 'Check weather conditions before planning outdoor activities.')}"""
            
            return {
                "success": True,
                "destination": destination,
                "weather_report": weather_text,
                "raw_data": raw_weather
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

