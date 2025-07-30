# scrub-llm

A lightweight, drop-in LLM secret scrubber to prevent API key and credential leaks in your AI applications.

[![PyPI](https://img.shields.io/pypi/v/scrub-llm.svg)](https://pypi.org/project/scrub-llm/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/pypi/pyversions/scrub-llm.svg)](https://pypi.org/project/scrub-llm/)

## Features

- **Drop-in wrapper** for OpenAI/httpx - no code rewrite required
- **Bidirectional redaction** - scrubs secrets before requests and after responses
- **30+ built-in patterns** - AWS, GCP, GitHub, Slack, JWT tokens, and more
- **Entropy detection** - catches high-entropy strings that look like secrets
- **Placeholder system** - preserves secret functionality while hiding values
- **Zero-copy streaming** - works with `stream=True` responses
- **CLI tool** - scrub logs and files from the command line

## Installation

```bash
pip install scrub-llm
```

## Quick Start

### OpenAI Integration

```python
from scrub_llm import OpenAIScrubber
import openai

# Wrap your OpenAI client
client = openai.OpenAI(api_key="your-key")
scrubbed_client = OpenAIScrubber(client)

# Use normally - secrets are automatically redacted
response = scrubbed_client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": "My AWS key is AKIAIOSFODNN7EXAMPLE"  # ← Automatically redacted
    }]
)

# Response secrets are also redacted
print(response.choices[0].message.content)
# "Your AWS key <REDACTED_AWS_ACCESS_KEY_ID> has been hidden"
```

### Direct Usage

```python
from scrub_llm import Scrubber

scrubber = Scrubber()

# Scrub prompts (with placeholder mapping)
text = "My GitHub token is ghp_1234567890abcdefghijklmnopqrstuvwxyz"
clean_text, mappings = scrubber.scrub_prompt(text)
print(clean_text)  # "My GitHub token is <SECRET_1>"

# Scrub responses (one-way redaction)  
response = "Generated API key: sk-proj-abc123xyz789"
clean_response = scrubber.scrub_response(response)
print(clean_response)  # "Generated API key: <REDACTED_OPENAI_API_KEY>"
```

### CLI Usage

```bash
# Check files for secrets
scrub-llm scan file.log

# Scrub secrets from files
scrub-llm scan file.log -o cleaned.log

# Pipe from stdin
cat production.log | scrub-llm scan

# Scan multiple files
scrub-llm scan *.log
```

## Detected Secret Types

The library detects 30+ secret patterns out of the box:

- **Cloud Providers**: AWS keys, GCP keys, Azure credentials
- **Source Control**: GitHub, GitLab, Bitbucket tokens  
- **API Services**: OpenAI, Anthropic, Stripe, Twilio, Mailgun keys
- **Communication**: Slack tokens/webhooks, Discord tokens
- **Package Managers**: npm, PyPI tokens
- **Monitoring**: DataDog, New Relic keys
- **Authentication**: JWTs, OAuth tokens, passwords in URLs
- **Encryption**: Private keys (RSA, SSH, PGP)
- **High Entropy**: Any string with high randomness (configurable)

## Advanced Usage

### Custom Detectors

```python
from scrub_llm import Scrubber
from scrub_llm.detectors import RegexDetector

# Add custom patterns
scrubber = Scrubber()
custom_detector = RegexDetector()
custom_detector.patterns["my_pattern"] = re.compile(r"CUSTOM-[A-Z0-9]{16}")
scrubber.add_detector(custom_detector)
```

### Entropy Configuration

```python
# Adjust entropy detection sensitivity
scrubber = Scrubber(
    enable_entropy=True,
    min_entropy=4.0,      # Higher = more selective (default: 3.5)
    min_entropy_length=25  # Minimum length to check (default: 20)
)
```

### Streaming Responses

```python
# Works seamlessly with streaming
response = scrubbed_client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    stream=True
)

for chunk in response:
    if chunk.flagged:  # True if secrets detected
        print(f"Secrets found: {chunk.secrets}")
    print(chunk.safe_text())  # Always safe to display
```

### httpx Integration

```python
from scrub_llm.transport import ScrubberHTTPXHook

# Create a scrubbed httpx client
hook = ScrubberHTTPXHook()
client = hook.create_client()

# All requests/responses are automatically scrubbed
response = client.post("https://api.example.com", json={
    "api_key": "sk-1234567890abcdef"  # Automatically redacted
})
```

## How It Works

1. **Pattern Matching**: Detects secrets using regex patterns for known formats
2. **Entropy Analysis**: Identifies high-entropy strings that look like secrets  
3. **Placeholder Mapping**: Replaces secrets with placeholders, maintaining a secure mapping
4. **Streaming Safety**: Processes streaming responses chunk-by-chunk
5. **Bidirectional**: Scrubs both outgoing prompts and incoming responses

## Development

```bash
# Clone the repository
git clone https://github.com/haasonsaas/scrub-llm.git
cd scrub-llm

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
mypy .
```

## Security Notes

- Placeholders are stored in thread-local storage for safety
- Original secrets never leave your application
- No external API calls or network access required
- All processing happens locally in-memory
- Safe for concurrent/async usage

## Performance

- Minimal overhead (<1ms for typical prompts)
- Zero-copy streaming responses
- Efficient regex compilation and caching
- Thread-safe for production use

## License

MIT License - This project is released under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Roadmap

- [ ] LangChain & LlamaIndex middleware  
- [ ] Automatic PII detection (names, emails, phone numbers)
- [ ] ML-based false positive reduction
- [ ] Vault/secrets manager integration
- [ ] Rust port for performance-critical paths
- [ ] YARA rule support for advanced patterns

## Support

- Issues: [GitHub Issues](https://github.com/haasonsaas/scrub-llm/issues)
- Discussions: [GitHub Discussions](https://github.com/haasonsaas/scrub-llm/discussions)

---

Built with ❤️ to keep your secrets secret.