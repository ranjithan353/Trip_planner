"""
Main Orchestrator - Coordinates all agents for trip planning
"""
import warnings
# Suppress flaml.automl warning from pyautogen
warnings.filterwarnings('ignore', message='.*flaml.automl.*', category=UserWarning)

from typing import Dict, Any
from agents.planner_agent import PlannerAgent
from agents.activity_agent import ActivityAgent
from agents.weather_agent import WeatherAgent
from agents.critic_agent import CriticAgent
from config.llm_config import ENABLE_CRITIQUE, ENABLE_REFINEMENT


class TripPlannerOrchestrator:
    """Orchestrates the multi-agent trip planning system"""
    
    # Class-level cache for results (persists across instances)
    _result_cache = {}
    
    def __init__(self):
        """Initialize all agents"""
        self.planner = PlannerAgent()
        self.activity_agent = ActivityAgent()
        self.weather_agent = WeatherAgent()
        self.critic = CriticAgent()
    
    def plan_trip(self, destination: str, duration: int, progress_callback=None) -> Dict[str, Any]:
        """
        Plan a complete trip using multi-agent system
        
        Args:
            destination: Destination name
            duration: Number of days
        
        Returns:
            Dictionary containing complete planning results
        """
        try:
            # Validate inputs
            if not destination or not isinstance(destination, str) or len(destination.strip()) < 2:
                return {
                    "success": False,
                    "error": "Invalid destination. Please provide a valid destination name."
                }
            
            if not isinstance(duration, int) or duration < 1 or duration > 30:
                return {
                    "success": False,
                    "error": "Duration must be an integer between 1 and 30 days."
                }
            
            destination = destination.strip()
            
            # Check cache first
            cache_key = f"{destination}_{duration}"
            if cache_key in TripPlannerOrchestrator._result_cache:
                cached_result = TripPlannerOrchestrator._result_cache[cache_key]
                print(f"[Cache Hit] Returning cached result for {destination}")
                if progress_callback:
                    progress_callback(100, "✅ Using cached result...")
                return cached_result
            
            # Additional validation: Ensure destination is a place name, not random words
            import re
            invalid_words = ['hello', 'hi', 'test', 'testing', 'abc', 'xyz', 'sample', 'example',
                           'demo', 'asdf', 'qwerty', 'password', 'admin', 'user', 'name', 'word',
                           'paper', 'book', 'table', 'chair', 'computer', 'phone', 'car', 'house',
                           'dog', 'cat', 'bird', 'tree', 'water', 'food', 'coffee', 'bread']
            
            if destination.lower() in invalid_words:
                return {
                    "success": False,
                    "error": f"'{destination}' is not a valid place name. Please enter a city or destination (e.g., Paris, Tokyo, New York)."
                }
            
            # Check if single lowercase word (likely a common noun, not a place)
            if len(destination.split()) == 1 and destination[0].islower():
                # Allow if it's a known place (will be checked by activity search anyway)
                # But reject obvious common nouns
                if destination.lower() in ['paper', 'book', 'table', 'chair', 'water', 'food', 'coffee']:
                    return {
                        "success": False,
                        "error": f"'{destination}' is not a place name. Please enter a city or destination."
                    }
            
            # Check if destination contains only numbers
            if destination.replace(' ', '').isdigit():
                return {
                    "success": False,
                    "error": "Destination cannot be only numbers. Please enter a place name."
                }
            
            # Check if destination has at least one letter
            if not re.search(r'[a-zA-Z]', destination):
                return {
                    "success": False,
                    "error": "Destination must contain letters. Please enter a valid place name."
                }
            
            # Step 1: Get weather information
            print(f"[Step 1/5] Getting weather information for {destination}...")
            if progress_callback:
                progress_callback(30, "🌤️ Getting weather information...")
            weather_result = self.weather_agent.get_weather_report(destination)
            weather_info = weather_result.get("weather_report", "") if weather_result.get("success") else ""
            weather_raw = weather_result.get("raw_data", {})
            
            # Step 2: Research activities (quick search)
            print(f"[Step 2/5] Researching activities in {destination}...")
            if progress_callback:
                progress_callback(45, "🔍 Finding top attractions...")
            activity_result = self.activity_agent.research_activities(destination)
            activity_info = activity_result.get("research_report", "") if activity_result.get("success") else ""
            activities_data = activity_result.get("activities_data", {})
            
            # Step 3: Create initial itinerary
            print(f"[Step 3/5] Creating initial itinerary...")
            if progress_callback:
                progress_callback(70, "✍️ Creating your itinerary...")
            itinerary_result = self.planner.create_itinerary(
                destination=destination,
                duration=duration,
                activity_data=activity_info,
                weather_data=weather_info
            )
            
            if not itinerary_result.get("success"):
                return {
                    "success": False,
                    "error": itinerary_result.get("error", "Failed to create itinerary"),
                    "weather_info": weather_info,
                    "activity_info": activity_info
                }
            
            initial_itinerary = itinerary_result.get("itinerary", "")
            
            # Step 4: Critique the itinerary (optional - can be disabled for speed)
            critique = ""
            critique_result = {"success": False}  # Initialize to avoid reference errors
            if ENABLE_CRITIQUE:
                print(f"[Step 4/5] Critiquing itinerary...")
                if progress_callback:
                    progress_callback(85, "🔍 Reviewing itinerary quality...")
                critique_result = self.critic.critique_itinerary(
                    itinerary=initial_itinerary,
                    destination=destination,
                    duration=duration,
                    weather_info=weather_info
                )
                critique = critique_result.get("critique", "") if critique_result.get("success") else ""
            else:
                print(f"[Step 4/5] Skipping critique for faster planning...")
            
            # Step 5: Refine itinerary based on critique (optional - can be disabled for speed)
            print(f"[Step 5/5] Finalizing itinerary...")
            if progress_callback:
                progress_callback(95, "✨ Finalizing your trip plan...")
            if ENABLE_REFINEMENT and critique:
                # Create refinement prompt with critique
                refinement_prompt = f"""Original {duration}-day itinerary for {destination}:

{initial_itinerary}

Critique and feedback:
{critique}

Now create an improved, refined version of this itinerary that addresses ALL concerns raised in the critique.
Make sure to:
- Include all missing meals (breakfast, lunch, dinner for each day)
- Fix overcrowded schedules with realistic time allocations
- Improve activity sequencing for logical flow
- Match activities to weather conditions
- Add missing important attractions
- Ensure variety in activities
- Include practical information (transport, costs, booking tips)
- Allow realistic pacing with rest breaks
- Include cultural experiences

Maintain the engaging, narrative, human-like style. Write as if you're a knowledgeable local guide.
Format clearly with Day X sections, Morning/Afternoon/Evening, and meal suggestions.

End with TERMINATE."""
                
                # Use planner's user proxy to send refinement request
                self.planner.user_proxy.initiate_chat(
                    self.planner.assistant,
                    message=refinement_prompt,
                    max_turns=2  # Reduced from 5 for faster refinement
                )
                
                refinement_messages = self.planner.user_proxy.chat_messages[self.planner.assistant]
                if refinement_messages:
                    final_itinerary = refinement_messages[-1].get("content", initial_itinerary)
                else:
                    final_itinerary = initial_itinerary
            else:
                final_itinerary = initial_itinerary
            
            # Compile final result
            final_result = {
                "success": True,
                "destination": destination,
                "duration": duration,
                "weather": {
                    "report": weather_info,
                    "raw": weather_raw
                },
                "activities": {
                    "research": activity_info,
                    "data": activities_data
                },
                "itinerary": {
                    "initial": initial_itinerary,
                    "final": final_itinerary,
                    "critique": critique
                },
                "process": {
                    "steps_completed": 5,
                    "weather_success": weather_result.get("success", False),
                    "activity_success": activity_result.get("success", False),
                    "itinerary_success": itinerary_result.get("success", False),
                    "critique_success": critique_result.get("success", False)
                }
            }
            
            # Cache the result (limit cache size to 10 entries)
            if len(TripPlannerOrchestrator._result_cache) >= 10:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(TripPlannerOrchestrator._result_cache))
                del TripPlannerOrchestrator._result_cache[oldest_key]
            TripPlannerOrchestrator._result_cache[cache_key] = final_result
            
            return final_result
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "destination": destination if 'destination' in locals() else None,
                "duration": duration if 'duration' in locals() else None
            }

