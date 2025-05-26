# Configuration TUI Usage Guide

Both `nothingburger` and `roborambo` now include interactive Text User Interfaces (TUIs) for generating configuration files. These tools make it easy to create properly formatted TOML configuration files without manually editing them.

## Installation

For the best experience, install the optional TUI dependencies:

```bash
# For nothingburger
pip install nothingburger[tui]

# For roborambo  
pip install roborambo[tui,all]

# Or install rich separately
pip install rich tomli-w
```

## Nothingburger Model Configuration TUI

### Quick Start

```bash
# Launch the model configuration TUI
nothingburger config-model

# Or use the direct command
burger-config

# Or use the module directly
python -m nothingburger.config_tui
```

### Features

- **Interactive Provider Selection**: Choose from OpenAI, Ollama, Llama.cpp, HuggingFace, and more
- **Smart Defaults**: Sensible defaults based on provider capabilities
- **API Format Support**: Configure for modern chat APIs or legacy completions
- **Generation Parameters**: Fine-tune temperature, tokens, sampling, and more
- **Validation**: Built-in validation for required fields
- **Rich Interface**: Enhanced UI with tables and panels (when `rich` is installed)

### Supported Providers

| Provider | Chat API | Completions | Local | Cloud |
|----------|----------|-------------|-------|--------|
| OpenAI | ✅ | ✅ | ❌ | ✅ |
| Ollama | ✅ | ✅ | ✅ | ❌ |
| Llama.cpp | ❌ | ✅ | ✅ | ❌ |
| HuggingFace | ❌ | ✅ | ✅ | ✅ |
| CTransformers | ❌ | ✅ | ✅ | ❌ |

### Example Session

```
Nothingburger Model Configuration Generator
==========================================

Available Providers:
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Key              ┃ Name                     ┃ Description                              ┃ Chat API ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ openai           │ OpenAI                   │ OpenAI GPT models (GPT-4, GPT-3.5, etc) │ ✓        │
│ ollama           │ Ollama                   │ Local Ollama server                      │ ✓        │
│ llama-cpp-python │ Llama.cpp (Python)       │ Direct llama.cpp integration             │ ✗        │
└──────────────────┴──────────────────────────┴──────────────────────────────────────────┴──────────┘

Select provider [openai]: openai

Configuring OpenAI
Base URL [https://api.openai.com/v1]: 
Model name [gpt-4-turbo-preview]: gpt-4o
API format [chat]: chat
Do you want to set an API key now? [y/N]: y
API key: sk-...

Model Metadata
Model display name [My Model]: GPT-4o
Author/Organization [Unknown]: OpenAI
License: MIT
Website/URL: https://openai.com

Generation Settings
Configure generation parameters? [Y/n]: y
Temperature [0.7]: 0.7
Max tokens [512]: 1024
...

Configuration Preview:
┏━━━━━━━━━━━━━━━━━━━━━ Generated Config ━━━━━━━━━━━━━━━━━━━━━━┓
┃ name = "GPT-4o"                                         ┃
┃ author = "OpenAI"                                       ┃
┃ license = "MIT"                                         ┃
┃ website = "https://openai.com"                          ┃
┃                                                         ┃
┃ [service]                                               ┃
┃ provider = "openai"                                     ┃
┃ base_url = "https://api.openai.com/v1"                  ┃
┃ model_key = "gpt-4o"                                    ┃
┃ api_format = "chat"                                     ┃
┃ api_key = "sk-..."                                      ┃
┃                                                         ┃
┃ [generation]                                            ┃
┃ temperature = 0.7                                       ┃
┃ max_tokens = 1024                                       ┃
┃ ...                                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Save this configuration? [Y/n]: y
Filename [/home/user/.config/nothingburger/model_library/openai/gpt-4o.toml]: 
✓ Configuration saved to /home/user/.config/nothingburger/model_library/openai/gpt-4o.toml
Model library location: /home/user/.config/nothingburger/model_library
```

## Roborambo Bot Configuration TUI

### Quick Start

```bash
# Launch the bot configuration TUI
roborambo config-bot

# Or use the direct command
rambo-config

# Or use the module directly
python -m roborambo.config_tui
```

### Features

- **Complete Bot Setup**: Configure personality, tools, interfaces, and model settings
- **Tool Selection**: Choose from web search, file browser, vector stores, and more
- **Interface Configuration**: Set up Zulip, Discord, Mattermost, Matrix connections
- **Personality Customization**: Define bot persona and behavior
- **Security Settings**: Configure privileged users and emergency cutoffs
- **Model Integration**: Link to nothingburger model configurations

### Available Tools

| Tool | Description | Default |
|------|-------------|---------|
| Web Engine | Search and navigate the web | ✅ |
| Tool Inspector | Inspect available tools | ✅ |
| File Browser | Read/write local files | ❌ |
| Chat Interface | Messaging system integration | ❌ |
| Knowledgebase | Search internal knowledge | ❌ |
| GraphQL | Query GraphQL endpoints | ❌ |
| Vector Store | Semantic search/storage | ❌ |
| Ask Expert | Get expert opinions | ❌ |
| Schedule Tool | Manage appointments | ❌ |

### Available Interfaces

| Interface | Description | Required Fields |
|-----------|-------------|-----------------|
| Zulip | Team chat platform | key, email, site |
| Discord | Gaming/community chat | token |
| Mattermost | Enterprise collaboration | url, token |
| Matrix | Decentralized chat | homeserver, username, password |

### Example Session

```
Roborambo Bot Configuration Generator
====================================

Basic Information:
Bot name [RoboRambo]: MyBot
Maintainer name [You]: Alice
Enable this bot? [Y/n]: y

Instructions & Personality:
Team/Organization name [Your Team]: Acme Corp
Site/Location [Your Site]: HQ
Customize bot personality? [y/N]: y
Bot personality/persona:
(Press Ctrl+D or enter empty line to finish)
> You are {name}, a helpful AI assistant for {team}.
> You're knowledgeable, friendly, and always ready to help with tasks.
> 

Emergency Cutoff:
Enable emergency cutoff phrase? [Y/n]: y
Cutoff phrase [bicycle built for two]: 
...

Available Tools:
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Key           ┃ Name                     ┃ Description                              ┃ Default ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ web           │ Web Engine               │ Search and navigate the web              │ ✓       │
│ inspector     │ Tool Inspector           │ Inspect and analyze available tools      │ ✓       │
│ file          │ File Browser             │ Search, read and write local files       │ ✗       │
└───────────────┴──────────────────────────┴──────────────────────────────────────────┴─────────┘

...

✓ Bot configuration saved to /home/user/.config/roborambo/bot_library/mybot/config.toml
Remember to:
  • Add the bot to your daemon config (bot_library/config.toml)
  • Configure your model files in the model library
  • Set up interface credentials before enabling
```

## Advanced Usage

### Environment Variables

Both TUIs respect environment variables for default paths:

```bash
# Nothingburger model library (default: ~/.config/nothingburger/model_library)
export BURGER_MODEL_LIBRARY="/path/to/models"

# Roborambo bot library (default: ~/.config/roborambo/bot_library)
export RAMBO_BOT_LIBRARY="/path/to/bots"
```

### Scripting/Automation

While the TUIs are interactive, you can pre-fill some responses:

```bash
# Use defaults for most questions
echo -e "\\n\\n\\n\\ny\\n" | nothingburger config-model

# Or create template responses
cat > responses.txt << EOF
openai
gpt-4o
chat
y
sk-your-key-here
MyGPT4
OpenAI
MIT
https://openai.com
y
0.7
1024
EOF

nothingburger config-model < responses.txt
```

### Integration with Existing Configs

The TUIs generate standard TOML files that work with existing configurations:

```python
# Load generated model config
from nothingburger.model_loader import initializeModel
model = initializeModel("models/openai/gpt-4o.toml")

# Load generated bot config
from roborambo.config import Reader
config = Reader().read()
```

## Troubleshooting

### Missing Dependencies

```bash
# Install required packages
pip install tomli-w rich

# Or install with extras
pip install nothingburger[tui] roborambo[all]
```

### Permission Errors

```bash
# Create directories first
mkdir -p ~/.config/nothingburger/model_library
mkdir -p ~/.config/roborambo/bot_library

# Or use custom paths
nothingburger config-model
# Then save to ./models/mymodel.toml
```

### Invalid Configuration

The TUIs include basic validation, but always test generated configs:

```bash
# Test a model config
python -c "
from nothingburger.model_loader import initializeModel
model = initializeModel('models/test.toml')
print('Model loaded successfully!')
"

# Test a bot config
roborambo chat --assistant TestBot
```

### Rich Display Issues

If the enhanced interface doesn't work:

```bash
# Check rich installation
python -c "import rich; print('Rich available')"

# Fall back to plain text
TERM=dumb nothingburger config-model
```

## Tips and Best Practices

### Model Configurations

1. **Use descriptive names**: `gpt-4-creative` instead of `model1`
2. **Organize by provider**: Store in `provider/model.toml` structure  
3. **Document settings**: Use clear license and website fields
4. **Test thoroughly**: Always test generated configs before production
5. **Version control**: Keep configs in git for change tracking

### Bot Configurations

1. **Clear personalities**: Define specific roles and behaviors
2. **Minimal tools**: Start with basic tools, add more as needed
3. **Security first**: Always configure privileged users
4. **Staged deployment**: Test in private channels before public
5. **Monitor usage**: Keep logs of bot interactions

### File Organization

```
~/.config/
├── nothingburger/
│   └── model_library/
│       ├── openai/
│       │   ├── gpt-4o.toml
│       │   └── gpt-3.5.toml
│       ├── ollama/
│       │   ├── llama2.toml
│       │   └── codellama.toml
│       └── local/
│           └── custom-model.toml
└── roborambo/
    └── bot_library/
        ├── config.toml              # Daemon config
        ├── helpbot/
        │   └── config.toml          # Bot config
        └── codebot/
            └── config.toml          # Bot config
```

This organization makes it easy to manage multiple models and bots while keeping configurations discoverable and maintainable.