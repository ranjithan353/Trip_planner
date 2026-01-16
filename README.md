# ✈️ Agentic AI Travel Planner

A production-grade, multi-agent AI system for creating intelligent travel itineraries using AutoGen, Ollama, and Streamlit.

## 🎯 Features

- **Multi-Agent Architecture**: Four specialized AI agents working together
- **Autonomous Tool Usage**: Agents decide which tools to use
- **Self-Reflection**: Critic agent reviews and improves itineraries
- **Web-Based Research**: Real-time activity search using DuckDuckGo
- **Weather-Aware Planning**: Considers weather conditions in recommendations
- **Human-Like Output**: Natural, narrative-style itineraries
- **Local LLM**: Runs entirely on Ollama (no cloud APIs required)

## 🏗️ Architecture

### Agents

1. **Planner Agent** - Central controller that orchestrates planning
2. **Activity Agent** - Researches attractions and activities via web search
3. **Weather Agent** - Provides weather information and recommendations
4. **Critic Agent** - Reviews itineraries and identifies improvements

### Tools

1. **Weather Tool** - Returns weather data for destinations
2. **Search Tool** - Web search using DuckDuckGo for activity research

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama installed and running
- Ollama model downloaded (llama3.2, mistral, or llama2)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install and start Ollama**:
```bash
# Download Ollama from https://ollama.ai
# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull llama3.2
# or
ollama pull mistral
```

4. **Configure (optional)**:
Edit `config/llm_config.py` to change model or settings:
```python
OLLAMA_MODEL = "llama3.2"  # Change to your preferred model
```

5. **Run the application**:
```bash
streamlit run app.py
```

6. **Open your browser**:
Navigate to `http://localhost:8501`

## 📁 Project Structure

```
agentic_travel_planner/
│
├── agents/
│   ├── __init__.py
│   ├── planner_agent.py      # Central planning agent
│   ├── activity_agent.py     # Activity research agent
│   ├── weather_agent.py       # Weather specialist agent
│   └── critic_agent.py        # Itinerary critic agent
│
├── tools/
│   ├── __init__.py
│   ├── weather_tool.py        # Weather information tool
│   └── search_tool.py         # Web search tool (DuckDuckGo)
│
├── config/
│   ├── __init__.py
│   └── llm_config.py          # LLM configuration
│
├── app.py                     # Streamlit UI
├── main.py                    # Agent orchestrator
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── PROJECT_DEMO.md            # Comprehensive documentation
```

## 🧠 How It Works

1. **User Input**: Destination and duration via Streamlit UI
2. **Weather Research**: Weather agent gathers climate information
3. **Activity Research**: Activity agent searches for attractions
4. **Itinerary Creation**: Planner agent creates initial itinerary
5. **Critique**: Critic agent reviews and provides feedback
6. **Refinement**: Planner agent improves itinerary based on critique
7. **Output**: Final refined itinerary displayed to user

## 📝 Example Usage

**Input:**
- Destination: Paris
- Duration: 3 days

**Output:**
- Weather summary for Paris
- Day-by-day itinerary with:
  - Morning activities (9 AM - 12 PM)
  - Afternoon activities (1 PM - 5 PM)
  - Evening activities (6 PM - 9 PM)
  - Meal suggestions (breakfast, lunch, dinner)
  - Travel tips and practical information
- Critique analysis
- Refined final version

## ⚙️ Configuration

Edit `config/llm_config.py`:

```python
OLLAMA_MODEL = "llama3.2"        # Model name
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama server URL
TEMPERATURE = 0.7                # LLM creativity (0-1)
MAX_ITERATIONS = 10              # Max agent conversation turns
```

## 🛠️ Customization

### Adding New Tools

1. Create tool function in `tools/` directory
2. Register with agents in respective agent files:

```python
@self.user_proxy.register_for_execution()
@self.assistant.register_for_llm(description="Tool description")
def new_tool(param: str) -> str:
    # Implementation
    return result
```

### Changing Agent Behavior

Edit system messages in agent files:
- `agents/planner_agent.py` - Planning behavior
- `agents/activity_agent.py` - Research behavior
- `agents/weather_agent.py` - Weather analysis
- `agents/critic_agent.py` - Critique criteria

## 🐛 Troubleshooting

### "Connection refused" to Ollama
- Ensure Ollama is running: `ollama serve`
- Check OLLAMA_BASE_URL in config

### "Model not found"
- Pull the model: `ollama pull llama3.2`
- Verify model name in config matches

### Slow responses
- Use smaller/faster models
- Reduce MAX_ITERATIONS in config
- Check system resources

### Web search not working
- Check internet connection
- DuckDuckGo search may be rate-limited
- System falls back to curated data

## 📚 entation

See `PROJECT_DEMO.md` for:
- Detailed architecture explanation
- Code walkthrough
- Input/output examples
- Advanced customization guide

## 🔒 Privacy

- **100% Local**: All processing happens on your machine
- **No API Keys**: No external API calls (except optional web search)
- **Data Privacy**: Your travel plans stay private

## 🎓 Key Technologies

- **AutoGen**: Multi-agent framework by Microsoft
- **Ollama**: Local LLM runtime
- **Streamlit**: Rapid web app development
- **DuckDuckGo**: Privacy-focused web search

## 📄 License

This project is open source and available for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Real weather API integration
- Additional activity data sources
- Export functionality (PDF, JSON)
- Multi-city trip support
- Budget planning features

## 📧 Support

For issues or questions:
1. Check `PROJECT_DEMO.md` for detailed explanations
2. Review troubleshooting section above
3. Verify Ollama is running and model is available

---

**Built with ❤️ using AutoGen, Ollama, and Streamlit**

