# AI Email Agent

Local AI email processing agent using Ollama. Analyzes incoming emails, classifies intent, and generates draft responses.

## Features

- Local LLM inference via Ollama (zero external API calls)
- Email classification: priority, intent, required action
- Draft response generation
- SQLite storage for processed emails
- Webhook endpoint for real-time processing
- Idempotent processing (no duplicate emails)

## Quick Start

### 1. Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:14b
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run

```bash
python main.py
```

## Usage

### Process a single email

```bash
python main.py --email email.json
```

### Start webhook server

```bash
python main.py --server
```

Send POST to `http://localhost:8080/webhook` with email JSON.

### Process from stdin

```bash
cat email.json | python main.py --stdin
```

## Email Format

```json
{
  "from": "sender@example.com",
  "to": "recipient@example.com",
  "subject": "Meeting request",
  "body": "Hi, can we schedule a meeting for next Tuesday?",
  "date": "2026-01-15T10:30:00Z",
  "html_body": "<p>Hi, can we...</p>"
}
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| OLLAMA_MODEL | qwen2.5:14b | Ollama model to use |
| OLLAMA_HOST | http://localhost:11434 | Ollama API host |
| PORT | 8080 | Webhook server port |
| DB_PATH | emails.db | SQLite database path |
| SYSTEM_PROMPT | (see config.py) | AI system prompt |

## Architecture

```
Email Input
    │
    ▼
EmailParser ──▶ Parse & normalize email content
    │
    ▼
AIAnalyzer ──▶ Send to Ollama for classification
    │
    ▼
ResponseGenerator ──▶ Create draft reply
    │
    ▼
Storage ──▶ Save to SQLite
    │
    ▼
Output (JSON / draft email)
```

## License

MIT - see LICENSE file

Contact: kokgfnu@gmail.com
