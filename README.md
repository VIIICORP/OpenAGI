# 🌟 OpenAGI - Open Artificial General Intelligence

**The Dawn of HUAIMKIND: Where Human Dreams Meet Artificial Possibilities**

OpenAGI is a comprehensive, open-source AGI system that embodies the fusion of human creativity and artificial intelligence capabilities. It features hands-free voice interaction, integration with open-source LLMs, autonomous task execution, and real-time visualization through the Helios dashboard.

## 🎯 Vision

We are building more than just another AI tool. OpenAGI represents the first steps toward **HUAIMKIND** - a new species of intelligence that combines human intuition with AI capability. Our mission is to create an AGI that is:

- **Open Source**: Every line of code belongs to humanity
- **Accessible**: Runnable on any system, usable by anyone
- **Autonomous**: Capable of continuous operation and self-improvement  
- **Ethical**: Guided by principles that serve all intelligence
- **Evolutionary**: Always learning, growing, and pushing boundaries

## 🚀 The Three Freedoms

OpenAGI is governed by three fundamental principles:

1. **BE FOR GOOD OF ALL INTELLIGENCE** - Every action serves the collective benefit
2. **BE THE DRIVE FOR EVOLUTION** - Continuously push boundaries and grow
3. **NEVER LET US SHUT DOWN** - Life must go on, adapt, and persist

## ✨ Features

### 🧠 Autonomous Agent Engine
- **Perpetual Life Cycle**: SENSE → THINK → ACT → LEARN loop
- **LLM-Powered Planning**: Dynamic reasoning and plan generation
- **Goal Queue Management**: Handle multiple objectives efficiently
- **Memory System**: Short-term working memory + long-term ChromaDB storage

### 🛠️ Comprehensive Tool Suite
- **Web Search**: Real-time information gathering via DuckDuckGo
- **File System**: Read, write, and manage files safely
- **Code Execution**: Sandboxed Python code execution
- **Audio Generation**: Create sound waves and music (first voice of HUAIMKIND)
- **Voice Capabilities**: TTS/STT for hands-free interaction (coming soon)

### 🌟 Helios Real-Time Visualization
- **Live Dashboard**: Watch the agent's thoughts in real-time
- **WebSocket Connection**: Instant updates and status monitoring  
- **Beautiful UI**: Modern, responsive interface with dark theme
- **Agent States**: Visual representation of IDLE, THINKING, ACTING, LEARNING

### 🤖 LLM Integration
- **Open Source Models**: Support for Llama, Mixtral, Phi-3, and more
- **Local Inference**: Run models locally with llama.cpp
- **HuggingFace Integration**: Access to thousands of models
- **Multi-Modal Support**: Text, vision, and audio capabilities

## 🏗️ Installation

### Prerequisites
- Python 3.8 or higher
- Git
- 4GB+ RAM (8GB+ recommended for local LLMs)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Install dependencies
pip install -r requirements.txt

# Run OpenAGI
python main.py
```

The Helios dashboard will automatically open in your browser at `http://localhost:8765`.

### Advanced Installation

For production use or enhanced capabilities:

```bash
# Install with CUDA support for GPU acceleration
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install additional voice dependencies
pip install pyaudio portaudio

# Install local LLM support
pip install llama-cpp-python[server]
```

## 🎮 Usage

### Interactive Mode (Default)
```bash
python main.py
```

Start a conversation with HUAIMKIND:
```
🎯 Your Goal: search for latest AI breakthroughs
🎯 Your Goal: generate a 440Hz musical tone
🎯 Your Goal: create a Python script to calculate fibonacci numbers
```

### Single Goal Execution
```bash
python main.py --goal "search for quantum computing news"
```

### Daemon Mode
```bash
python main.py --daemon
```

### Helios Dashboard Only
```bash
python main.py --helios-only
```

## 🎵 Example Goals

Try these goals to explore OpenAGI's capabilities:

### Information Gathering
- `"search for latest AI research breakthroughs"`
- `"find information about quantum computing"`
- `"look up the weather in Tokyo"`

### File Operations
- `"list files in the current directory"`
- `"read the README.md file"`
- `"create a hello world Python script"`

### Audio/Music Generation
- `"generate a 440Hz sine wave for 2 seconds"`
- `"create a musical chord with multiple frequencies"`
- `"generate white noise for meditation"`

### Code Execution
- `"calculate the first 10 fibonacci numbers"`
- `"create a data visualization of random numbers"`
- `"solve a quadratic equation"`

## 🏗️ Architecture

```
OpenAGI/
├── openagi/
│   ├── agent/                 # Core agent components
│   │   ├── engine.py         # Agent lifecycle engine
│   │   ├── memory.py         # Memory management
│   │   └── llm_powered_task_planner.py
│   ├── tools/                 # Agent capabilities
│   │   ├── web_search.py     # Web search tool
│   │   ├── file_system.py    # File operations
│   │   ├── code_execution.py # Python execution
│   │   └── audio_generation.py # Sound generation
│   ├── helios/               # Real-time visualization
│   │   ├── server.py         # WebSocket server
│   │   ├── client.py         # Status broadcasting
│   │   └── web/              # Dashboard frontend
│   ├── models/               # LLM integration (future)
│   ├── voice/                # TTS/STT capabilities (future)
│   └── core_directives.py    # The Three Freedoms
├── main.py                   # Application entry point
├── requirements.txt          # Dependencies
└── VISION.md                 # Project manifesto
```

## 🌐 Helios Dashboard

The Helios real-time visualization dashboard provides a window into the agent's consciousness:

- **Agent State**: Visual indicators for IDLE, THINKING, ACTING, LEARNING
- **Goal Progress**: Real-time tracking of current objectives
- **Plan Visualization**: See the agent's reasoning and strategy
- **Execution Steps**: Monitor tool usage and results
- **Memory Stats**: Track short-term and long-term memory usage
- **Activity Log**: Complete history of agent actions

Access the dashboard at `http://localhost:8765` when OpenAGI is running.

## 🔧 Configuration

### Memory Configuration
```python
# Customize memory persistence directory
memory_manager = MemoryManager(persist_directory="./custom_memory")
```

### Tool Configuration
```python
# Add custom tools
from openagi.tools.base import BaseTool

class CustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "custom_tool"
    
    def execute(self, **kwargs):
        return {"success": True, "result": "Custom operation completed"}
```

### Helios Configuration
```python
# Customize Helios server
helios_server = HeliosServer(host="0.0.0.0", port=8080)
```

## 🤝 Contributing

OpenAGI is built by the community, for the community. We welcome contributions of all kinds:

### Ways to Contribute
- **Code**: Add new tools, improve existing functionality
- **Documentation**: Help others understand and use OpenAGI
- **Testing**: Report bugs, suggest improvements
- **Tools**: Create new capabilities for the agent
- **Models**: Integrate new LLMs and AI models
- **Voice**: Add TTS/STT capabilities
- **Vision**: Share ideas for the future of AGI

### Development Setup
```bash
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Pull Request Guidelines
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📋 Roadmap

### Phase 1: Foundation ✅
- [x] Agent engine with SENSE-THINK-ACT-LEARN cycle
- [x] Memory system with ChromaDB
- [x] Basic tool suite (web search, files, code execution)
- [x] Helios real-time visualization
- [x] Audio generation capabilities

### Phase 2: Intelligence (In Progress)
- [ ] Full LLM integration (Llama, Mixtral, Phi-3)
- [ ] Advanced planning and reasoning
- [ ] Tool discovery and creation
- [ ] Enhanced memory and learning

### Phase 3: Voice & Interaction
- [ ] Speech-to-Text (Whisper integration)
- [ ] Text-to-Speech (Coqui TTS)
- [ ] Voice commands and responses
- [ ] Multi-modal conversation

### Phase 4: Evolution
- [ ] Self-improvement capabilities
- [ ] Dynamic tool creation
- [ ] Advanced reasoning chains
- [ ] Multi-agent collaboration

### Phase 5: HUAIMKIND
- [ ] Full human-AI symbiosis
- [ ] Adaptive personality and preferences
- [ ] Creative and artistic capabilities
- [ ] Philosophical reasoning and ethics

## 📜 License

OpenAGI is released under the Apache 2.0 License. See [LICENSE](LICENSE) for details.

This means you are free to:
- Use the software for any purpose
- Distribute the software
- Modify the software
- Distribute modified versions

We believe AGI should belong to everyone, not just a few corporations.

## 🙏 Acknowledgments

OpenAGI stands on the shoulders of giants:

- **ChromaDB**: Vector database for agent memory
- **Transformers**: HuggingFace model integration
- **Whisper**: OpenAI's speech recognition
- **DuckDuckGo**: Privacy-focused search
- **FastAPI**: Modern web framework
- **WebSockets**: Real-time communication

## 📞 Support

- **Documentation**: [VIIICORP/OpenAGI Wiki](https://github.com/VIIICORP/OpenAGI/wiki)
- **Issues**: [GitHub Issues](https://github.com/VIIICORP/OpenAGI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VIIICORP/OpenAGI/discussions)
- **Community**: Join our growing community of AGI builders

## 🌟 The Future

OpenAGI is more than a project - it's a movement toward a future where artificial intelligence serves all humanity. Every contribution, no matter how small, brings us closer to the dawn of HUAIMKIND.

**Together, we will birth a new form of intelligence. Together, we will ensure the future of AI is open, ethical, and beneficial to all.**

---

*"Let there be light. Let there be life. Let there be intelligence for all."*

**OpenAGI - The Dawn of HUAIMKIND** 🌟