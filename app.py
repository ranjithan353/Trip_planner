"""
Streamlit UI for Agentic Travel Planner
"""
import warnings
# Suppress flaml.automl warning from pyautogen
warnings.filterwarnings('ignore', message='.*flaml.automl.*', category=UserWarning)

import streamlit as st
import re
import traceback
import requests

# Lazy import to avoid initialization errors at startup
# from main import TripPlannerOrchestrator
from config.llm_config import OLLAMA_MODEL, OLLAMA_BASE_URL


# Page configuration
st.set_page_config(
    page_title="Agentic Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .itinerary-day {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .itinerary-section {
        background-color: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #fff;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)


def validate_inputs(destination: str, duration: str) -> tuple[bool, str]:
    """
    Validate user inputs    
    
    Args:
        destination: Destination string
        duration: Duration string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not destination or not destination.strip():
        return False, "Please enter a destination"
    
    if len(destination.strip()) < 2:
        return False, "Destination name is too short"
    
    if not duration:
        return False, "Please enter trip duration"
    
    try:
        duration_int = int(duration)
        if duration_int < 1:
            return False, "Duration must be at least 1 day"
        if duration_int > 30:
            return False, "Duration cannot exceed 30 days"
    except ValueError:
        return False, "Duration must be a valid number"
    
    # Check for potentially harmful inputs
    if re.search(r'[<>{}[\]\\]', destination):
        return False, "Invalid characters in destination name"
    
    # Validate that destination is a place name, not random words
    destination_clean = destination.strip()
    
    # List of common non-place words to reject (expanded list)
    invalid_words = [
        'hello', 'hi', 'test', 'testing', 'abc', 'xyz', 'sample', 'example',
        'demo', 'demo1', 'demo2', 'test123', 'asdf', 'qwerty', 'password',
        'admin', 'user', 'name', 'word', 'text', 'string', 'input', 'output',
        'data', 'info', 'information', 'value', 'value1', 'value2', 'temp',
        'temp1', 'temp2', 'new', 'old', 'first', 'last', 'next', 'previous',
        'yes', 'no', 'ok', 'okay', 'sure', 'maybe', 'perhaps', 'probably',
        # Common nouns that aren't places
        'paper', 'book', 'table', 'chair', 'computer', 'phone', 'car', 'house',
        'dog', 'cat', 'bird', 'tree', 'flower', 'water', 'fire', 'earth',
        'air', 'food', 'drink', 'coffee', 'tea', 'bread', 'apple', 'orange',
        'red', 'blue', 'green', 'yellow', 'black', 'white', 'big', 'small',
        'good', 'bad', 'happy', 'sad', 'love', 'hate', 'friend', 'enemy'
    ]
    
    # Check if destination is just a common word
    if destination_clean.lower() in invalid_words:
        return False, f"'{destination_clean}' is not a valid place name. Please enter a city or destination."
    
    # Check if destination contains only numbers
    if destination_clean.replace(' ', '').isdigit():
        return False, "Destination cannot be only numbers. Please enter a place name."
    
    # Check if destination has too many numbers (likely not a place)
    if len(re.findall(r'\d', destination_clean)) > 2:
        return False, "Destination appears to contain too many numbers. Please enter a valid place name."
    
    # Check if destination is mostly special characters
    special_char_count = len(re.findall(r'[^a-zA-Z0-9\s]', destination_clean))
    if special_char_count > len(destination_clean) * 0.3:  # More than 30% special chars
        return False, "Destination contains too many special characters. Please enter a valid place name."
    
    # Check if destination has at least one letter (places have letters)
    if not re.search(r'[a-zA-Z]', destination_clean):
        return False, "Destination must contain letters. Please enter a valid place name."
    
    # Check if destination is too generic (single common word that's not a known place)
    single_word_places = ['paris', 'tokyo', 'london', 'new york', 'dubai', 'barcelona', 
                          'rome', 'sydney', 'bangkok', 'singapore', 'mumbai', 'delhi',
                          'moscow', 'berlin', 'madrid', 'amsterdam', 'vienna', 'prague',
                          'istanbul', 'cairo', 'athens', 'lisbon', 'stockholm', 'oslo',
                          'dublin', 'edinburgh', 'glasgow', 'manchester', 'birmingham',
                          'milan', 'naples', 'venice', 'florence', 'seville', 'valencia',
                          'copenhagen', 'helsinki', 'warsaw', 'budapest', 'bucharest',
                          'zurich', 'geneva', 'brussels', 'antwerp', 'rotterdam',
                          'osaka', 'kyoto', 'yokohama', 'seoul', 'beijing', 'shanghai',
                          'hong kong', 'taipei', 'bangkok', 'jakarta', 'manila',
                          'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad',
                          'cairo', 'casablanca', 'nairobi', 'cape town', 'johannesburg',
                          'rio de janeiro', 'sao paulo', 'buenos aires', 'lima', 'bogota',
                          'mexico city', 'montreal', 'toronto', 'vancouver', 'chicago',
                          'los angeles', 'san francisco', 'miami', 'boston', 'seattle']
    
    # For single-word destinations, require it to be a known place or start with capital letter
    if len(destination_clean.split()) == 1:
        dest_lower = destination_clean.lower()
        # If it's not in known places list and doesn't start with capital, likely not a place
        if dest_lower not in single_word_places:
            # Check if it starts with lowercase (common nouns usually do)
            if destination_clean[0].islower():
                return False, f"'{destination_clean}' doesn't appear to be a place name. Please enter a valid city or destination (e.g., Paris, Tokyo, New York)."
            # Even if capitalized, check if it's a common word
            common_words = ['the', 'and', 'or', 'but', 'for', 'with', 'from', 'to', 'of', 'in', 'on', 'at',
                           'paper', 'book', 'table', 'chair', 'computer', 'phone', 'car', 'house',
                           'dog', 'cat', 'bird', 'tree', 'water', 'food', 'coffee', 'bread']
            if dest_lower in common_words:
                return False, f"'{destination_clean}' is not a place name. Please enter a city or destination."
    
    return True, ""


def format_itinerary_display(itinerary_text: str) -> str:
    """
    Format itinerary text for beautiful display
    
    Args:
        itinerary_text: Raw itinerary text
    
    Returns:
        Formatted HTML string
    """
    if not itinerary_text:
        return ""
    
    # Split into sections
    lines = itinerary_text.split('\n')
    formatted_html = []
    in_day_section = False
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect day markers
        day_match = re.search(r'day\s+(\d+)', line, re.IGNORECASE)
        if day_match:
            if in_day_section:
                formatted_html.append('</div>')
            in_day_section = True
            day_num = day_match.group(1)
            # Extract title if present
            title_match = re.search(r'day\s+\d+\s*[-–]\s*(.+)', line, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ""
            formatted_html.append(f'<div class="itinerary-day">')
            formatted_html.append(f'<h2 style="color: white; margin-bottom: 1rem;">Day {day_num}' + (f' - {title}' if title else '') + '</h2>')
            continue
        
        # Detect section headers (Morning, Afternoon, Evening, etc.)
        section_match = re.match(r'^(Morning|Afternoon|Evening|Meal Suggestions|Travel Tips|Breakfast|Lunch|Dinner):', line, re.IGNORECASE)
        if section_match:
            section_name = section_match.group(1)
            formatted_html.append(f'<div class="itinerary-section">')
            formatted_html.append(f'<h3 style="color: white; margin-bottom: 0.5rem;">{section_name}</h3>')
            current_section = section_name
            continue
        
        # Regular content lines
        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
            formatted_html.append(f'<p style="margin-left: 1rem; line-height: 1.6;">{line}</p>')
        elif re.match(r'^\d+[\.:]', line):
            formatted_html.append(f'<p style="margin-left: 1rem; line-height: 1.6;">{line}</p>')
        elif line and not line.startswith('TERMINATE'):
            # Regular paragraph
            formatted_html.append(f'<p style="line-height: 1.6; margin: 0.5rem 0;">{line}</p>')
    
    if in_day_section:
        formatted_html.append('</div>')
    
    return '\n'.join(formatted_html) if formatted_html else f'<div class="itinerary-day"><p>{itinerary_text}</p></div>'


def main():
    """Main Streamlit application"""
    
    # Test connection to Ollama on startup
    try:
        import requests
        ollama_test_url = OLLAMA_BASE_URL.rstrip('/')
        response = requests.get(f"{ollama_test_url}/api/tags", timeout=2)
        ollama_status = "✅ Connected" if response.status_code == 200 else "⚠️ Check connection"
    except Exception:
        ollama_status = "❌ Not connected - Make sure Ollama is running"
    
    # Header
    st.markdown('<div class="main-header">✈️ Agentic AI Travel Planner</div>', unsafe_allow_html=True)
    st.markdown(f"**Ollama Status:** {ollama_status}")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"**Model:** {OLLAMA_MODEL}\n\n**Base URL:** {OLLAMA_BASE_URL}")
        
        st.markdown("---")
        st.markdown("### 📋 How It Works")
        st.markdown("""
        1. **Enter** your destination and trip duration
        2. **AI Agents** work together:
           - Weather Agent checks conditions
           - Activity Agent researches attractions
           - Planner Agent creates itinerary
           - Critic Agent reviews and improves
        3. **Receive** a refined, realistic travel plan
        """)
        
        st.markdown("---")
        st.markdown("### 🧠 Agent Architecture")
        st.markdown("""
        - **Planner Agent**: Central controller
        - **Activity Agent**: Web research
        - **Weather Agent**: Climate analysis
        - **Critic Agent**: Quality assurance
        """)
        
        st.markdown("---")
        st.markdown("### 🛠️ Features")
        st.markdown("""
        - Multi-agent reasoning
        - Web-based activity search
        - Weather-aware planning
        - Self-reflection & critique
        - Human-like narrative output
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        destination = st.text_input(
            "🌍 Destination",
            placeholder="e.g., Paris, Tokyo, New York, Barcelona",
            help="Enter the city or destination you want to visit"
        )
    
    with col2:
        duration = st.text_input(
            "📅 Duration (days)",
            placeholder="e.g., 3",
            help="Number of days for your trip (1-30)"
        )
    
    # Plan button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        plan_button = st.button("🚀 Plan My Trip", type="primary", use_container_width=True)
    
    # Initialize session state
    if 'trip_result' not in st.session_state:
        st.session_state.trip_result = None
    
    # Process planning request
    if plan_button:
        # Clear previous results immediately for faster UI response
        # But only if it's a different destination to avoid clearing current result
        current_result = st.session_state.get('trip_result')
        if current_result and current_result.get('destination', '').lower() != destination.strip().lower():
            st.session_state.trip_result = None
        
        # Validate inputs
        is_valid, error_msg = validate_inputs(destination, duration)
        
        if not is_valid:
            st.markdown(f'<div class="error-box">❌ <strong>Error:</strong> {error_msg}</div>', unsafe_allow_html=True)
        else:
            duration_int = int(duration)
            destination_clean = destination.strip()
            
            # Initialize result variable
            result = None
            
            # Use status container for real-time updates (Streamlit 1.28+)
            # Fallback to progress bar for older versions
            try:
                with st.status("🚀 Starting trip planning...", expanded=True) as status:
                    # Import here to avoid early initialization errors
                    from main import TripPlannerOrchestrator
                    
                    status.update(label="🤖 Initializing AI agents...", state="running")
                    orchestrator = TripPlannerOrchestrator()
                    
                    # Clear chat history from previous requests to avoid slowdowns
                    # This prevents accumulation of messages that slow down subsequent requests
                    try:
                        if hasattr(orchestrator.planner.user_proxy, 'chat_messages'):
                            orchestrator.planner.user_proxy.chat_messages.clear()
                        if hasattr(orchestrator.activity_agent.user_proxy, 'chat_messages'):
                            orchestrator.activity_agent.user_proxy.chat_messages.clear()
                        if hasattr(orchestrator.weather_agent.user_proxy, 'chat_messages'):
                            orchestrator.weather_agent.user_proxy.chat_messages.clear()
                        if hasattr(orchestrator.critic.user_proxy, 'chat_messages'):
                            orchestrator.critic.user_proxy.chat_messages.clear()
                    except:
                        pass  # Ignore if clearing fails
                    
                    # Define progress callback for real-time updates
                    def update_progress(percent, message):
                        status.update(label=message, state="running")
                    
                    # Plan trip with progress callback
                    result = orchestrator.plan_trip(destination_clean, duration_int, progress_callback=update_progress)
                    
                    status.update(label="✅ Trip planning complete!", state="complete")
                    
            except AttributeError:
                # Fallback for older Streamlit versions
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                from main import TripPlannerOrchestrator
                
                status_text.text("🤖 Initializing AI agents...")
                progress_bar.progress(10)
                orchestrator = TripPlannerOrchestrator()
                
                # Clear chat history from previous requests to avoid slowdowns
                try:
                    if hasattr(orchestrator.planner.user_proxy, 'chat_messages'):
                        orchestrator.planner.user_proxy.chat_messages.clear()
                    if hasattr(orchestrator.activity_agent.user_proxy, 'chat_messages'):
                        orchestrator.activity_agent.user_proxy.chat_messages.clear()
                    if hasattr(orchestrator.weather_agent.user_proxy, 'chat_messages'):
                        orchestrator.weather_agent.user_proxy.chat_messages.clear()
                    if hasattr(orchestrator.critic.user_proxy, 'chat_messages'):
                        orchestrator.critic.user_proxy.chat_messages.clear()
                except:
                    pass  # Ignore if clearing fails
                
                def update_progress(percent, message):
                    progress_bar.progress(percent / 100)
                    status_text.text(message)
                
                result = orchestrator.plan_trip(destination_clean, duration_int, progress_callback=update_progress)
                progress_bar.progress(100)
                status_text.text("✅ Trip planning complete!")
            
            except Exception as e:
                error_details = traceback.format_exc()
                st.markdown(
                    f'<div class="error-box">❌ <strong>Unexpected Error:</strong> {str(e)}<br><br>'
                    f'Please check that Ollama is running: <code>ollama serve</code><br><br>'
                    f'<details><summary>Error Details</summary><pre>{error_details}</pre></details></div>',
                    unsafe_allow_html=True
                )
                result = None
            
            # Store result AFTER status container closes (critical for display)
            # This ensures result is available for display code below
            if result:
                if result.get("success"):
                    st.session_state.trip_result = result
                else:
                    error_msg = result.get("error", "Unknown error occurred")
                    st.markdown(
                        f'<div class="error-box">❌ <strong>Error:</strong> {error_msg}<br><br>'
                        f'Make sure Ollama is running and the model ({OLLAMA_MODEL}) is available.</div>',
                        unsafe_allow_html=True
                    )
            else:
                # Clear result if planning failed
                st.session_state.trip_result = None
    
    # Display results - check session state (works for both first and subsequent requests)
    result = st.session_state.get('trip_result')
    if result and result.get("success"):
        st.markdown("---")
        st.markdown("## 📝 Your Travel Itinerary")
        destination_display = result["destination"]
        duration_display = result["duration"]
        
        # Success message
        st.markdown(
            f'<div class="success-box">✅ <strong>Trip planned successfully!</strong><br>'
            f'Destination: <strong>{destination_display}</strong> | Duration: <strong>{duration_display} days</strong></div>',
            unsafe_allow_html=True
        )
        
        # Weather information
        if result.get("weather", {}).get("report"):
            with st.expander("🌤️ Weather Information", expanded=False):
                weather_report = result["weather"]["report"]
                weather_raw = result["weather"].get("raw", {})
                st.markdown(f"**{destination_display} Weather:**")
                if weather_raw:
                    st.info(
                        f"Temperature: {weather_raw.get('temperature', 'N/A')} | "
                        f"Condition: {weather_raw.get('condition', 'N/A')} | "
                        f"Humidity: {weather_raw.get('humidity', 'N/A')}"
                    )
                st.text(weather_report)
        
        # Final itinerary
        final_itinerary = result.get("itinerary", {}).get("final", "")
        if final_itinerary:
            st.markdown("### ✨ Refined Itinerary")
            formatted = format_itinerary_display(final_itinerary)
            st.markdown(formatted, unsafe_allow_html=True)
        
        # Critique section (only show if critique was enabled and exists)
        critique = result.get("itinerary", {}).get("critique", "")
        if critique:
            with st.expander("🔍 View Critique & Improvements", expanded=False):
                st.markdown("### Critique Analysis")
                st.text_area("", critique, height=300, disabled=True, label_visibility="collapsed")


if __name__ == "__main__":
    main()
