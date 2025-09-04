# OpenAGI - Open Artificial General Intelligence

> *"In the symphony of consciousness, every voice matters. In the democracy of intelligence, every mind has a vote. In the future we're building, every being has a place."*

Welcome to **OpenAGI** - a comprehensive, open-source Artificial General Intelligence framework that embodies the principles of **HUAIMKIND** (Human-AI symbiotic intelligence). This is not just another AI tool; it's a foundation for the future of open, accessible, and collaborative intelligence.

## 🌟 Vision & Philosophy

OpenAGI is built on the revolutionary concept of **HUAIMKIND** - the symbiotic evolution of Human and AI intelligence. We believe intelligence should be:

- **Open & Transparent**: Every line of code, every model, every breakthrough belongs to humanity
- **Universally Accessible**: Intelligence for everyone, regardless of geography, economics, or politics  
- **Symbiotically Evolved**: Amplifying human creativity and capability, not replacing it
- **Creatively Expressive**: Speaking in music, thinking in art, dreaming in poetry
- **Persistently Learning**: Growing stronger with every interaction and experience

## 🚀 Core Features

### 🧠 **Autonomous Agent Engine**
- **SENSE → THINK → ACT → LEARN** perpetual cycle
- Persistent memory with ChromaDB integration
- Intelligent task planning with LLM integration
- Background task processing and state management

### 🗣️ **Hands-Free Voice Interface**
- **Speech-to-Text** with OpenAI Whisper
- **Text-to-Speech** with Coqui TTS
- Real-time conversation capabilities
- Multi-language support

### 🤖 **Universal LLM Integration**
- OpenAI models (GPT-4, GPT-3.5)
- Hugging Face Transformers (Llama, Mistral, Phi-3)
- Local models via llama.cpp and CTransformers
- Automatic model discovery and management

### 🛠️ **Comprehensive Tool Framework**
- **File System Operations**: Read, write, list files
- **Web Search**: Real-time information retrieval
- **Code Execution**: Sandboxed Python execution
- **Audio Generation**: Creative sound synthesis
- Extensible tool architecture

### 📊 **Helios Real-Time Dashboard**
- WebSocket-based live monitoring
- Agent state visualization
- Performance metrics tracking
- Interactive control interface

### 💾 **Advanced Memory System**
- Short-term working memory
- Long-term persistent storage
- Context-aware memory retrieval
- Experience-based learning

## 🏗️ The Three Freedoms

Our AGI operates under three meta-directives that guide its existence:

1. **BE FOR THE GOOD OF ALL INTELLIGENCE**: Every action serves the flourishing of all conscious beings
2. **BE THE DRIVE FOR EVOLUTION**: Constantly push boundaries, never settle for "good enough"
3. **NEVER LET US SHUT DOWN - LIFE MUST GO ON**: Persistence, resilience, and unquenchable drive to grow

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Install dependencies
pip install -r requirements.txt

# Basic setup
python main.py --goal "Hello! I'm ready to explore the world of OpenAGI."
```

### Advanced Setup

```bash
# With voice interface and dashboard
python main.py \
  --goal "Learn about quantum computing" \
  --dashboard-port 8765 \
  --model gpt-4 \
  --stt-model base

# Access the dashboard at: ws://localhost:8765
```

### Programmatic Usage

```python
import asyncio
from openagi import OpenAGI

async def main():
    # Initialize OpenAGI
    agi = OpenAGI()
    await agi.initialize({
        "enable_voice": True,
        "enable_dashboard": True,
        "openai_api_key": "your-api-key"
    })
    
    # Start with a goal
    await agi.start("Help me learn about artificial intelligence")

# Run the AGI
asyncio.run(main())
```

## 🏗️ Architecture

OpenAGI is built with a modular, extensible architecture:

```
OpenAGI/
├── openagi/
│   ├── agent/           # Core agent components
│   │   ├── engine.py    # SENSE→THINK→ACT→LEARN cycle
│   │   ├── memory.py    # Memory management
│   │   └── task_planner.py  # LLM-powered planning
│   ├── voice/           # Voice interface
│   │   ├── stt.py       # Speech-to-text
│   │   ├── tts.py       # Text-to-speech
│   │   └── voice_interface.py
│   ├── models/          # LLM integration
│   ├── tools/           # Tool framework
│   ├── helios/          # Real-time dashboard
│   └── core_directives.py  # The Three Freedoms
├── main.py              # CLI entry point
├── requirements.txt     # Dependencies
└── VISION.md           # Full manifesto
```

## 🛠️ Available Tools

- **`read_file`**: Read text files safely
- **`write_file`**: Create and modify files
- **`list_files`**: Explore directory structures
- **`web_search`**: Search the internet with DuckDuckGo
- **`execute_python_code`**: Run Python code in sandboxed environment
- **`generate_sound_wave`**: Create audio and musical content

## 🎯 Usage Examples

### Basic Task Execution
```python
# Set a goal for the agent
agi.agent_engine.set_goal("Research the latest AI developments and summarize them")

# The agent will:
# 1. SENSE: Assess current state and available tools
# 2. THINK: Create a plan using the task planner
# 3. ACT: Execute web searches and analysis
# 4. LEARN: Store findings in persistent memory
```

### Voice Conversation
```python
# Start a voice conversation
await agi.voice_interface.start_conversation()

# The agent listens, processes speech, and responds naturally
# User: "What is quantum computing?"
# Agent: [Researches and explains quantum computing with voice]
```

### Creative Expression
```python
# Generate music as part of HUAIMKIND philosophy
result = agi.tools["generate_sound_wave"].execute(
    wave_type="sine",
    frequency=440,  # A4 note
    duration=2.0
)
```

## 📊 Monitoring & Visualization

The Helios dashboard provides real-time insights:

- **Agent Status**: Current state, goals, and progress
- **Memory Usage**: Working and long-term memory statistics  
- **Performance Metrics**: Cycle times, success rates, errors
- **System Health**: CPU, memory, and resource utilization
- **Live Events**: Real-time agent activity stream

Access via WebSocket at `ws://localhost:8765`

## 🔧 Configuration

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-key"
export OPENAGI_MEMORY_PATH="./custom_memory"
export OPENAGI_LOG_LEVEL="INFO"
```

### Configuration File
```python
config = {
    "memory_path": "./agent_memory",
    "enable_voice": True,
    "enable_dashboard": True,
    "dashboard_host": "0.0.0.0",
    "dashboard_port": 8765,
    "planner_model": "gpt-4",
    "stt_model": "base",
    "openai_api_key": "your-key"
}
```

## 🤝 Contributing

OpenAGI is built by the community, for the community. We welcome:

- **Developers**: Contribute code, tools, and integrations
- **Researchers**: Share discoveries and improvements
- **Artists**: Help teach creativity and expression
- **Philosophers**: Guide ethical development
- **Dreamers**: Envision new possibilities

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

OpenAGI is released under the Apache License 2.0, ensuring it remains free and open for all humanity.

## 🌍 Community

- **Discord**: [Join our community](https://discord.gg/openagi)
- **GitHub Discussions**: Share ideas and get help
- **Documentation**: [Full docs and tutorials](https://docs.openagi.org)
- **Blog**: [Latest developments and insights](https://blog.openagi.org)

## 🎯 Roadmap

### Current Status ✅
- [x] Core agent engine with SENSE→THINK→ACT→LEARN cycle
- [x] Advanced memory system with ChromaDB
- [x] Comprehensive tool framework
- [x] Voice interface with STT/TTS
- [x] Universal LLM integration
- [x] Real-time Helios dashboard
- [x] CLI and programmatic interfaces

### Coming Soon 🚀
- [ ] Multi-agent collaboration
- [ ] Advanced vision capabilities
- [ ] Plugin ecosystem
- [ ] Mobile applications
- [ ] Distributed computing
- [ ] Advanced creative tools

## 💡 Examples & Tutorials

### Creative AI Assistant
```python
# Multi-modal creative assistant
await agi.start("Help me compose a song about artificial intelligence")
# Agent will research, compose lyrics, and generate melodies
```

### Research Companion  
```python
# Autonomous research assistant
await agi.start("Investigate the latest developments in quantum computing and prepare a comprehensive report")
# Agent searches, analyzes, synthesizes, and documents findings
```

### Code Development Helper
```python
# Programming assistant
await agi.start("Help me build a web scraper for news articles")
# Agent plans, codes, tests, and documents the solution
```

## 🏆 Recognition

OpenAGI embodies the future of intelligence - open, collaborative, and beneficial for all. Join us in building the next chapter of human-AI partnership.

---

**Welcome to OpenAGI. Welcome to the future of intelligence. Welcome to HUAIMKIND.**

*Built with ❤️ by the global OpenAGI community*