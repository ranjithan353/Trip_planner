"""
Critic Agent - Reviews and critiques itineraries for improvements
"""
from typing import Dict, Any
import autogen
from config.llm_config import get_llm_config, MAX_ITERATIONS


class CriticAgent:
    """AutoGen agent for critiquing travel itineraries"""
    
    def __init__(self):
        """Initialize the critic agent"""
        self.llm_config = get_llm_config()
        
        # Create critic assistant
        self.critic = autogen.AssistantAgent(
            name="itinerary_critic",
            system_message="""You are an expert travel itinerary critic with years of experience reviewing travel plans.
            Your role is to thoroughly review trip itineraries and identify issues, gaps, and areas for improvement.
            
            Check for:
            1. Missing meals (breakfast, lunch, dinner) - every day should have meal suggestions
            2. Overcrowded schedules - ensure realistic time allocations
            3. Poor sequencing - activities should be logically ordered by location and time
            4. Weather mismatches - outdoor activities should match weather conditions
            5. Missing important attractions - ensure major sites are included
            6. Lack of variety - balance cultural, recreational, and entertainment activities
            7. Missing practical information - transportation, costs, booking requirements
            8. Unrealistic pacing - allow time for travel between locations
            9. Missing rest time - travelers need breaks
            10. Cultural experiences - ensure local culture is represented
            
            Provide specific, actionable feedback. Be constructive and detailed.""",
            llm_config=self.llm_config,
        )
        
        # Create user proxy
        self.user_proxy = autogen.UserProxyAgent(
            name="critic_user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=MAX_ITERATIONS,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
            llm_config=self.llm_config,
        )
    
    def critique_itinerary(self, itinerary: str, destination: str, duration: int, weather_info: str = None) -> Dict[str, Any]:
        """
        Critique an itinerary
        
        Args:
            itinerary: The itinerary text to critique
            destination: Destination name
            duration: Trip duration in days
            weather_info: Optional weather information
        
        Returns:
            Dictionary containing critique
        """
        try:
            prompt = f"""Review this {duration}-day itinerary for {destination}:

{itinerary}
"""
            if weather_info:
                prompt += f"\nWeather Information:\n{weather_info}\n"
            
            prompt += """
Analyze this itinerary thoroughly and identify:
- Missing meals (breakfast, lunch, dinner for each day)
- Overcrowded or unrealistic schedules
- Poor activity sequencing
- Weather-inappropriate activities
- Missing important attractions
- Lack of variety
- Missing practical information (transport, costs, booking)
- Unrealistic pacing
- Missing rest/break time
- Lack of cultural experiences

Provide a detailed, constructive critique with specific recommendations. End with TERMINATE."""
            
            self.user_proxy.initiate_chat(
                self.critic,
                message=prompt,
                max_turns=1  # Reduced from 3 - critique should be quick
            )
            
            messages = self.user_proxy.chat_messages[self.critic]
            if messages:
                critique = messages[-1].get("content", "")
                
                return {
                    "success": True,
                    "critique": critique,
                    "destination": destination,
                    "duration": duration
                }
            else:
                return {
                    "success": False,
                    "error": "No response from critic agent"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

