from typing import Dict, Any, List
import requests
import os
import sys
from agents.base_agent import BaseAgent


# Aggiungi il path per gli import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from agents.base_agent import BaseAgent
    from config import SEMRUSH_BASE_URL
except ImportError:
    # Fallback per import relativi
    from .base_agent import BaseAgent
    try:
        from config import SEMRUSH_BASE_URL
    except ImportError:
        SEMRUSH_BASE_URL = "https://api.semrush.com/"

class SEMRushAgent(BaseAgent):
    """Agente per l'analisi dei dati SEMRush"""
    
    def __init__(self, api_config, app_config):
        super().__init__(api_config, app_config)
        self.base_url = SEMRUSH_BASE_URL
        
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i dati SEMRush per l'azienda"""
        if not self.api_config.semrush_api_key:
            return {"error": "SEMRush API key non configurata"}
        
        domain = self._extract_domain(company_data.get("website", ""))
        if not domain:
            return {"error": "Dominio non valido per analisi SEMRush"}
        
        self.log_progress(f"Analizzando {domain} con SEMRush...")
        
        results = {}
        
        # 1. Dati sul traffico organico
        organic_data = self._get_organic_data(domain)
        results["organic_traffic"] = organic_data
        
        # 2. Dati sui backlink
        backlink_data = self._get_backlink_data(domain)
        results["backlinks"] = backlink_data
        
        # 3. Keyword ranking
        keyword_data = self._get_keyword_data(domain)
        results["keywords"] = keyword_data
        
        # 4. Competitor analysis
        competitors = self._get_competitors(domain)
        results["competitors"] = competitors
        
        # 5. Paid advertising data
        paid_data = self._get_paid_data(domain)
        results["paid_advertising"] = paid_data
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """Estrae il dominio dall'URL"""
        if not url:
            return ""
        
        # Rimuove protocollo e www
        domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
        
        # Prende solo la parte del dominio
        if "/" in domain:
            domain = domain.split("/")[0]
        
        return domain
    
    def _make_semrush_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Effettua una richiesta all'API SEMRush"""
        params["key"] = self.api_config.semrush_api_key
        params["export_format"] = "json"
        
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.make_request(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log_progress(f"SEMRush API error: {response.status_code}", "error")
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            self.log_progress(f"SEMRush request failed: {str(e)}", "error")
            return {"error": str(e)}
    
    def _get_organic_data(self, domain: str) -> Dict[str, Any]:
        """Ottiene i dati del traffico organico"""
        params = {
            "type": "domain_organic",
            "domain": domain,
            "database": "it"  # Database italiano
        }
        
        data = self._make_semrush_request("", params)
        
        if "error" in data:
            return data
        
        # Processa i dati
        processed_data = {
            "organic_keywords": 0,
            "organic_traffic": 0,
            "organic_cost": 0,
            "top_keywords": []
        }
        
        if isinstance(data, list) and len(data) > 0:
            for item in data[:10]:  # Prime 10 keyword
                if isinstance(item, dict):
                    processed_data["top_keywords"].append({
                        "keyword": item.get("Ph", ""),
                        "position": item.get("Po", 0),
                        "volume": item.get("Nq", 0),
                        "cpc": item.get("Cp", 0)
                    })
        
        return processed_data
    
    def _get_backlink_data(self, domain: str) -> Dict[str, Any]:
        """Ottiene i dati dei backlink"""
        params = {
            "type": "backlinks_overview",
            "target": domain,
            "target_type": "root_domain"
        }
        
        data = self._make_semrush_request("", params)
        
        if "error" in data:
            return data
        
        processed_data = {
            "total_backlinks": 0,
            "referring_domains": 0,
            "authority_score": 0,
            "top_referring_domains": []
        }
        
        # Processa i dati dei backlink
        if isinstance(data, dict):
            processed_data["total_backlinks"] = data.get("backlinks_num", 0)
            processed_data["referring_domains"] = data.get("domains_num", 0)
            processed_data["authority_score"] = data.get("ascore", 0)
        
        return processed_data
    
    def _get_keyword_data(self, domain: str) -> Dict[str, Any]:
        """Ottiene i dati delle keyword"""
        params = {
            "type": "domain_organic",
            "domain": domain,
            "database": "it",
            "display_limit": 20
        }
        
        data = self._make_semrush_request("", params)
        
        if "error" in data:
            return data
        
        processed_data = {
            "total_keywords": 0,
            "keywords_1_3": 0,
            "keywords_4_10": 0,
            "keywords_11_20": 0,
            "keyword_list": []
        }
        
        if isinstance(data, list):
            processed_data["total_keywords"] = len(data)
            
            for item in data:
                if isinstance(item, dict):
                    pos = item.get("Po", 0)
                    if 1 <= pos <= 3:
                        processed_data["keywords_1_3"] += 1
                    elif 4 <= pos <= 10:
                        processed_data["keywords_4_10"] += 1
                    elif 11 <= pos <= 20:
                        processed_data["keywords_11_20"] += 1
                    
                    processed_data["keyword_list"].append({
                        "keyword": item.get("Ph", ""),
                        "position": pos,
                        "volume": item.get("Nq", 0),
                        "difficulty": item.get("Kd", 0)
                    })
        
        return processed_data
    
    def _get_competitors(self, domain: str) -> List[Dict[str, Any]]:
        """Ottiene i competitor del dominio"""
        params = {
            "type": "domain_organic_organic",
            "domain": domain,
            "database": "it",
            "display_limit": 10
        }
        
        data = self._make_semrush_request("", params)
        
        if "error" in data:
            return [data]
        
        competitors = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    competitors.append({
                        "domain": item.get("Dn", ""),
                        "common_keywords": item.get("Cr", 0),
                        "se_keywords": item.get("Or", 0),
                        "se_traffic": item.get("Ot", 0),
                        "competition_level": item.get("Cl", 0)
                    })
        
        return competitors
    
    def _get_paid_data(self, domain: str) -> Dict[str, Any]:
        """Ottiene i dati della pubblicità a pagamento"""
        params = {
            "type": "domain_adwords",
            "domain": domain,
            "database": "it"
        }
        
        data = self._make_semrush_request("", params)
        
        if "error" in data:
            return data
        
        processed_data = {
            "paid_keywords": 0,
            "paid_traffic": 0,
            "paid_cost": 0,
            "ads_count": 0,
            "top_paid_keywords": []
        }
        
        if isinstance(data, list):
            processed_data["paid_keywords"] = len(data)
            
            for item in data[:5]:  # Prime 5 keyword a pagamento
                if isinstance(item, dict):
                    processed_data["top_paid_keywords"].append({
                        "keyword": item.get("Ph", ""),
                        "position": item.get("Po", 0),
                        "volume": item.get("Nq", 0),
                        "cpc": item.get("Cp", 0)
                    })
        
        return processed_data
