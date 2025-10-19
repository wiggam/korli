# Korli - Language Learning Chat Assistant

A conversational AI application powered by LangGraph for personalized language learning experiences. Korli creates adaptive chat conversations tailored to a student's proficiency level, native language, and learning goals.

## Features

- **Adaptive Language Learning**: Personalized conversations based on CEFR levels (A1-C2)
- **Multi-language Support**: Learn any language from any native language
- **Intelligent Conversation Management**: Automatic conversation summarization to maintain context
- **Topic-based Learning**: Focused conversations on specific topics
- **LangGraph Workflow**: Sophisticated state management and conversation flow
- **OpenAI Integration**: Powered by advanced language models
- **Observability**: Built-in Langfuse integration for monitoring and tracing

## Architecture

The application uses a LangGraph-based architecture with the following components:

### Chat Graph Flow

1. **Initialize State**: Sets up conversation parameters (student level, languages, topic)
2. **Initial Question**: Generates an opening question for new conversations
3. **Call Model**: Processes user messages and generates AI responses
4. **Summarization**: Automatically condenses conversation history when needed

### Key Components

- **State Management**: `ChatState` tracks messages, conversation summary, and prompt configuration
- **Graph Nodes**: Modular processing units for initialization, question generation, model calls, and summarization
- **Prompt System**: Hierarchical prompt management for different conversation phases
- **Services**: LLM integration, persistence, validation, and language support

## Installation

### Prerequisites

- Python 3.13+
- pip

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd korli
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:

```bash
# OpenAI API Key
OPENAI_API_KEY=your_api_key_here

# Langfuse Configuration (optional)
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

## Usage

### Running with LangGraph CLI

Start the development server:

```bash
langgraph dev
```

This will start an in-memory server with the LangGraph Studio interface where you can interact with the chat graph.

### Starting a New Conversation

Initialize a conversation with these parameters:

```json
{
	"student_level": "B2",
	"foreign_language": "Spanish (Spain)",
	"native_language": "English (US)",
	"topic": "travel and tourism"
}
```

**CEFR Levels Supported:**

- A1: Beginner
- A2: Elementary
- B1: Intermediate
- B2: Upper Intermediate
- C1: Advanced
- C2: Proficient

### Continuing a Conversation

Once initialized, simply send messages to continue the conversation. The graph automatically:

- Maintains conversation context
- Provides appropriate responses for the student's level
- Summarizes old messages when the conversation gets long (>30 messages)

## Configuration

### Chat Feature Settings

Located in `app/features/chat/config.py`:

- `MESSAGES_BEFORE_SUMMARY`: Number of messages before triggering summarization (default: 30)
- `MESSAGES_TO_KEEP`: Number of recent messages to keep after summarization (default: 20)

## Project Structure

```
korli/
├── app/
│   ├── features/
│   │   ├── chat/               # Chat feature implementation
│   │   │   ├── config.py       # Configuration settings
│   │   │   ├── graph.py        # LangGraph workflow definition
│   │   │   ├── nodes.py        # Graph node implementations
│   │   │   ├── state.py        # State management
│   │   │   └── utils.py        # Utility functions
│   │   ├── lessons/            # Lesson management features
│   │   └── prompts/            # Prompt templates
│   │       ├── chat/           # Chat-specific prompts
│   │       │   ├── chat_system/
│   │       │   ├── initial_question/
│   │       │   ├── summary/
│   │       │   └── topic/
│   │       └── level_information.py
│   ├── services/               # Core services
│   │   ├── config.py           # Service configuration
│   │   ├── language_validation.py
│   │   ├── llm.py              # LLM integration
│   │   ├── persistence.py      # Data persistence
│   │   └── validation.py       # Input validation
│   └── main.py                 # Application entry point
├── langgraph.json              # LangGraph configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Technology Stack

- **LangGraph 1.0.0**: State machine and workflow management
- **LangChain 1.0**: LLM framework and integrations
- **LangChain-OpenAI**: OpenAI model integration
- **Langfuse 3.7.0**: Observability and tracing
- **Python-dotenv**: Environment configuration
- **TikToken**: Token counting and management
- **orjson**: Fast JSON serialization

## Development

### LangGraph Studio

The project includes a `langgraph.json` configuration for use with LangGraph Studio, which provides:

- Visual graph debugging
- State inspection
- Message history tracking
- Interactive testing

### Adding New Features

1. Create a new feature directory under `app/features/`
2. Define state, nodes, and graph logic
3. Register the graph in `langgraph.json`
4. Update services as needed

## Contributing

Contributions are welcome! Please ensure:

- Code follows existing patterns and conventions
- New features include appropriate prompts and state management
- Services remain modular and reusable

## License

[Add your license information here]

## Support

For questions or issues, please [add contact information or issue tracker link].
