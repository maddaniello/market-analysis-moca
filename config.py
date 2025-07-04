import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class APIConfig:
    """Configurazione per le API keys"""
    openai_api_key: str
    semrush_api_key: str
    serper_api_key: str
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Carica le configurazioni dalle variabili d'ambiente"""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            semrush_api_key=os.getenv("SEMRUSH_API_KEY", ""),
            serper_api_key=os.getenv("SERPER_API_KEY", "")
        )

@dataclass
class AppConfig:
    """Configurazioni generali dell'applicazione"""
    max_retries: int = 3
    timeout: int = 30
    user_agents: list = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]

# URLs per i siti di verifica aziende
COMPANY_VERIFICATION_URLS = {
    "registro_imprese": "https://www.registroimprese.it",
    "ufficio_camerale": "https://www.ufficiocamerale.it/trova-azienda",
    "reportaziende": "https://www.reportaziende.it"
}

# Endpoint API
SEMRUSH_BASE_URL = "https://api.semrush.com/"
SERPER_BASE_URL = "https://google.serper.dev/"

# Configurazioni OpenAI
OPENAI_MODEL = "gpt-4"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 2000