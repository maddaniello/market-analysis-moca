import re
from typing import Dict, Any, Tuple
from urllib.parse import urlparse

class InputValidator:
    """Classe per validare gli input dell'utente"""
    
    @staticmethod
    def validate_company_input(input_text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Valida l'input dell'azienda e determina il tipo
        
        Returns:
            Tuple[bool, str, Dict]: (is_valid, input_type, extracted_data)
        """
        if not input_text or not input_text.strip():
            return False, "empty", {}
        
        input_text = input_text.strip()
        
        # Verifica se è un URL
        if InputValidator.is_url(input_text):
            domain = InputValidator.extract_domain(input_text)
            company_name = InputValidator.domain_to_company_name(domain)
            return True, "url", {
                "website": input_text,
                "domain": domain,
                "company_name": company_name
            }
        
        # Verifica se è una Partita IVA italiana
        if InputValidator.is_italian_vat(input_text):
            return True, "vat", {
                "vat_number": input_text,
                "company_name": f"Azienda P.IVA {input_text}"
            }
        
        # Altrimenti è un nome azienda
        if len(input_text) >= 2:
            return True, "name", {
                "company_name": input_text
            }
        
        return False, "invalid", {}
    
    @staticmethod
    def is_url(text: str) -> bool:
        """Verifica se il testo è un URL valido"""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_italian_vat(text: str) -> bool:
        """Verifica se il testo è una partita IVA italiana valida"""
        # Rimuove spazi e caratteri non numerici eccetto IT
        clean_text = re.sub(r'[^\d]', '', text.upper().replace('IT', ''))
        
        # Partita IVA italiana: 11 cifre
        if len(clean_text) == 11 and clean_text.isdigit():
            # Algoritmo di controllo della partita IVA italiana
            return InputValidator._validate_italian_vat_checksum(clean_text)
        
        return False
    
    @staticmethod
    def _validate_italian_vat_checksum(vat: str) -> bool:
        """Valida il checksum della partita IVA italiana"""
        if len(vat) != 11:
            return False
        
        try:
            # Calcolo checksum
            odd_sum = sum(int(vat[i]) for i in range(0, 10, 2))
            even_sum = 0
            
            for i in range(1, 10, 2):
                double = int(vat[i]) * 2
                even_sum += double if double < 10 else double - 9
            
            total = odd_sum + even_sum
            check_digit = (10 - (total % 10)) % 10
            
            return int(vat[10]) == check_digit
        except:
            return False
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Estrae il dominio dall'URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Rimuove www.
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return ""
    
    @staticmethod
    def domain_to_company_name(domain: str) -> str:
        """Converte un dominio in un possibile nome azienda"""
        if not domain:
            return ""
        
        # Rimuove estensioni comuni
        extensions = ['.com', '.it', '.org', '.net', '.eu', '.co.uk']
        company_name = domain
        
        for ext in extensions:
            if company_name.endswith(ext):
                company_name = company_name[:-len(ext)]
                break
        
        # Capitalizza la prima lettera
        return company_name.capitalize()
    
    @staticmethod
    def validate_api_keys(api_keys: Dict[str, str]) -> Dict[str, bool]:
        """Valida le API keys"""
        validation_results = {}
        
        # OpenAI API Key
        openai_key = api_keys.get('openai_api_key', '')
        validation_results['openai'] = bool(openai_key and openai_key.startswith('sk-'))
        
        # SEMRush API Key  
        semrush_key = api_keys.get('semrush_api_key', '')
        validation_results['semrush'] = bool(semrush_key and len(semrush_key) > 10)
        
        # Serper API Key
        serper_key = api_keys.get('serper_api_key', '')
        validation_results['serper'] = bool(serper_key and len(serper_key) > 10)
        
        return validation_results
    
    @staticmethod
    def sanitize_company_name(name: str) -> str:
        """Sanitizza il nome dell'azienda per la ricerca"""
        if not name:
            return ""
        
        # Rimuove caratteri speciali eccetto spazi, punti e trattini
        sanitized = re.sub(r'[^\w\s\.\-]', '', name)
        
        # Rimuove spazi multipli
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_search_query(query: str) -> bool:
        """Valida una query di ricerca"""
        if not query or len(query.strip()) < 2:
            return False
        
        # Blocca query potenzialmente dannose
        blocked_patterns = [
            r'<script',
            r'javascript:',
            r'data:',
            r'vbscript:'
        ]
        
        query_lower = query.lower()
        for pattern in blocked_patterns:
            if re.search(pattern, query_lower):
                return False
        
        return True
