from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import time
import requests
from openai import OpenAI
from config import APIConfig, AppConfig

class BaseAgent(ABC):
    """Classe base per tutti gli agenti AI"""
    
    def __init__(self, api_config: APIConfig, app_config: AppConfig):
        self.api_config = api_config
        self.app_config = app_config
        self.client = OpenAI(api_key=api_config.openai_api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Metodo principale per l'analisi - deve essere implementato da ogni agente"""
        pass
    
    def make_request(self, url: str, headers: Optional[Dict] = None, 
                    params: Optional[Dict] = None, timeout: int = None) -> requests.Response:
        """Effettua una richiesta HTTP con retry logic"""
        if timeout is None:
            timeout = self.app_config.timeout
            
        if headers is None:
            headers = {"User-Agent": self.app_config.user_agents[0]}
        
        for attempt in range(self.app_config.max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.app_config.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def query_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Effettua una query a OpenAI"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return f"Errore nell'analisi AI: {str(e)}"
    
    def extract_company_info(self, input_data: str) -> Dict[str, Any]:
        """Estrae informazioni dell'azienda da input (nome, URL, P.IVA)"""
        system_prompt = """Sei un esperto nell'identificazione di aziende. 
        Dato un input che può essere un nome azienda, URL del sito web, o partita IVA, 
        estrai le seguenti informazioni in formato JSON:
        - company_name: nome dell'azienda
        - website: URL del sito web (se disponibile)
        - vat_number: numero di partita IVA (se disponibile)
        - input_type: tipo di input ricevuto (name/url/vat)
        
        Se l'input è un URL, estrai il nome dell'azienda dal dominio.
        Se l'input è una P.IVA, cerca di identificare l'azienda associata.
        """
        
        prompt = f"Analizza questo input aziendale: {input_data}"
        
        result = self.query_openai(prompt, system_prompt)
        
        try:
            import json
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "company_name": input_data,
                "website": None,
                "vat_number": None,
                "input_type": "name"
            }
    
    def log_progress(self, message: str, level: str = "info"):
        """Log del progresso dell'analisi"""
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        
        # Anche per Streamlit
        print(f"[{self.__class__.__name__}] {message}")
    
    def validate_api_keys(self) -> bool:
        """Valida che le API keys siano configurate"""
        required_keys = []
        
        if not self.api_config.openai_api_key:
            required_keys.append("OPENAI_API_KEY")
        
        if required_keys:
            self.logger.error(f"Missing API keys: {', '.join(required_keys)}")
            return False
        
        return True
