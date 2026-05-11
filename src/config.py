# Configuration module
# Load settings from .env file or use defaults

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""

    def __init__(self):
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
        self.OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.PORT = int(os.getenv("PORT", "8080"))
        self.DB_PATH = os.getenv("DB_PATH", "emails.db")
        self.SYSTEM_PROMPT = os.getenv(
            "SYSTEM_PROMPT",
            "You are an email analysis assistant. Analyze the given email and provide structured output."
        )

    def check_ollama(self):
        """Check if Ollama is running and model is available"""
        import httpx
        try:
            async def check():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    r = await client.get(f"{self.OLLAMA_HOST}/api/tags")
                    r.raise_for_status()
                    models = r.json().get("models", [])
                    model_names = [m["name"] for m in models]
                    return self.OLLAMA_MODEL in model_names
            import asyncio
            return asyncio.run(check())
        except Exception:
            return False


def get_config() -> Config:
    """Get application config singleton"""
    return Config()
