from typing import Dict, Any, List
import requests
import json
from agents.base_agent import BaseAgent
from config import SERPER_BASE_URL

class SerperAgent(BaseAgent):
    """Agente per la ricerca di informazioni online tramite Serper.dev"""
    
    def __init__(self, api_config, app_config):
        super().__init__(api_config, app_config)
        self.base_url = SERPER_BASE_URL
        
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza e cerca informazioni sui competitor online"""
        if not self.api_config.serper_api_key:
            return {"error": "Serper API key non configurata"}
        
        company_name = company_data.get("company_name", "")
        if not company_name:
            return {"error": "Nome azienda non fornito"}
        
        self.log_progress(f"Cercando informazioni su {company_name} e competitor...")
        
        results = {}
        
        # 1. Ricerca generale sull'azienda
        company_info = self._search_company_info(company_name)
        results["company_info"] = company_info
        
        # 2. Ricerca competitor
        competitors = self._search_competitors(company_name)
        results["competitors"] = competitors
        
        # 3. Ricerca informazioni dettagliate sui competitor
        competitor_details = []
        for competitor in competitors.get("competitors", [])[:5]:  # Primi 5 competitor
            details = self._get_competitor_details(competitor.get("name", ""))
            competitor_details.append(details)
        
        results["competitor_details"] = competitor_details
        
        # 4. Ricerca presenza social
        social_presence = self._search_social_presence(company_name)
        results["social_presence"] = social_presence
        
        return results
    
    def _make_serper_request(self, endpoint: str, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Effettua una richiesta all'API Serper"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "X-API-KEY": self.api_config.serper_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "gl": "it",  # Geolocalizzazione Italia
            "hl": "it",  # Lingua italiana
            "num": 10
        }
        
        if params:
            payload.update(params)
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log_progress(f"Serper request failed: {str(e)}", "error")
            return {"error": str(e)}
    
    def _search_company_info(self, company_name: str) -> Dict[str, Any]:
        """Ricerca informazioni generali sull'azienda"""
        query = f"{company_name} azienda Italia informazioni"
        
        data = self._make_serper_request("search", query)
        
        if "error" in data:
            return data
        
        processed_data = {
            "search_results": [],
            "knowledge_graph": {},
            "related_searches": []
        }
        
        # Processa i risultati organici
        if "organic" in data:
            for result in data["organic"][:5]:
                processed_data["search_results"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0)
                })
        
        # Processa knowledge graph se disponibile
        if "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            processed_data["knowledge_graph"] = {
                "title": kg.get("title", ""),
                "type": kg.get("type", ""),
                "description": kg.get("description", ""),
                "attributes": kg.get("attributes", {}),
                "website": kg.get("website", "")
            }
        
        # Processa ricerche correlate
        if "relatedSearches" in data:
            for search in data["relatedSearches"][:5]:
                processed_data["related_searches"].append(search.get("query", ""))
        
        return processed_data
    
    def _search_competitors(self, company_name: str) -> Dict[str, Any]:
        """Ricerca competitor dell'azienda"""
        queries = [
            f"{company_name} competitor concorrenti",
            f"{company_name} alternative simili",
            f"aziende come {company_name}"
        ]
        
        all_competitors = []
        competitor_domains = set()
        
        for query in queries:
            data = self._make_serper_request("search", query)
            
            if "error" not in data and "organic" in data:
                for result in data["organic"][:5]:
                    # Estrae dominio
                    link = result.get("link", "")
                    if link:
                        domain = self._extract_domain(link)
                        if domain and domain not in competitor_domains:
                            competitor_domains.add(domain)
                            all_competitors.append({
                                "name": result.get("title", "").split(" - ")[0],
                                "domain": domain,
                                "description": result.get("snippet", ""),
                                "url": link
                            })
        
        return {
            "total_found": len(all_competitors),
            "competitors": all_competitors[:10]  # Primi 10 competitor
        }
    
    def _get_competitor_details(self, competitor_name: str) -> Dict[str, Any]:
        """Ottiene dettagli specifici su un competitor"""
        if not competitor_name:
            return {"error": "Nome competitor non fornito"}
        
        queries = [
            f"{competitor_name} azienda servizi prodotti",
            f"{competitor_name} partita iva codice fiscale",
            f"{competitor_name} fatturato dipendenti"
        ]
        
        details = {
            "name": competitor_name,
            "services": [],
            "products": [],
            "company_info": {},
            "search_results": []
        }
        
        for query in queries:
            data = self._make_serper_request("search", query)
            
            if "error" not in data and "organic" in data:
                for result in data["organic"][:3]:
                    details["search_results"].append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("link", ""),
                        "query": query
                    })
        
        # Usa AI per estrarre informazioni strutturate
        if details["search_results"]:
            ai_analysis = self._analyze_competitor_with_ai(competitor_name, details["search_results"])
            details.update(ai_analysis)
        
        return details
    
    def _search_social_presence(self, company_name: str) -> Dict[str, Any]:
        """Ricerca presenza social dell'azienda"""
        social_platforms = ["facebook", "instagram", "linkedin", "twitter", "youtube", "tiktok"]
        
        social_results = {}
        
        for platform in social_platforms:
            query = f"{company_name} {platform}"
            data = self._make_serper_request("search", query)
            
            if "error" not in data and "organic" in data:
                for result in data["organic"][:3]:
                    link = result.get("link", "")
                    if platform in link.lower():
                        social_results[platform] = {
                            "url": link,
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", "")
                        }
                        break
        
        return social_results
    
    def _analyze_competitor_with_ai(self, competitor_name: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Analizza i risultati di ricerca con AI per estrarre informazioni strutturate"""
        
        # Prepara il testo per l'analisi
        text_to_analyze = f"Azienda: {competitor_name}\n\n"
        for result in search_results:
            text_to_analyze += f"Titolo: {result['title']}\n"
            text_to_analyze += f"Descrizione: {result['snippet']}\n"
            text_to_analyze += f"URL: {result['url']}\n\n"
        
        system_prompt = """Analizza le informazioni sulla seguente azienda e estrai:
        1. Servizi principali offerti
        2. Prodotti principali
        3. Settore di attività
        4. Informazioni aziendali (se disponibili): partita IVA, codice fiscale, sede
        5. Dimensioni azienda (se disponibili): fatturato, dipendenti
        
        Rispondi in formato JSON con le seguenti chiavi:
        - services: lista dei servizi
        - products: lista dei prodotti
        - sector: settore di attività
        - vat_number: partita IVA (se trovata)
        - fiscal_code: codice fiscale (se trovato)
        - headquarters: sede principale (se trovata)
        - revenue: fatturato (se trovato)
        - employees: numero dipendenti (se trovato)
        """
        
        prompt = f"Analizza questi dati aziendali:\n\n{text_to_analyze}"
        
        result = self.query_openai(prompt, system_prompt)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "services": [],
                "products": [],
                "sector": "Non identificato",
                "analysis_raw": result
            }
    
    def _extract_domain(self, url: str) -> str:
        """Estrae il dominio dall'URL"""
        if not url:
            return ""
        
        # Rimuove protocollo
        domain = url.replace("https://", "").replace("http://", "")
        
        # Rimuove www
        if domain.startswith("www."):
            domain = domain[4:]
        
        # Prende solo la parte del dominio
        if "/" in domain:
            domain = domain.split("/")[0]
        
        return domain
