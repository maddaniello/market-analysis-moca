from typing import Dict, Any, List
import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from agents.base_agent import BaseAgent
from config import COMPANY_VERIFICATION_URLS

class CompanyAgent(BaseAgent):
    """Agente per raccogliere dati aziendali da fonti ufficiali"""
    
    def __init__(self, api_config, app_config):
        super().__init__(api_config, app_config)
        self.verification_sources = COMPANY_VERIFICATION_URLS
        
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i dati aziendali da fonti ufficiali"""
        company_name = company_data.get("company_name", "")
        vat_number = company_data.get("vat_number", "")
        
        if not company_name and not vat_number:
            return {"error": "Nome azienda o partita IVA non forniti"}
        
        self.log_progress(f"Raccogliendo dati aziendali per {company_name}...")
        
        results = {}
        
        # 1. Cerca dati nel Registro Imprese
        registro_data = self._search_registro_imprese(company_name, vat_number)
        results["registro_imprese"] = registro_data
        
        # 2. Cerca dati in Ufficio Camerale
        camerale_data = self._search_ufficio_camerale(company_name, vat_number)
        results["ufficio_camerale"] = camerale_data
        
        # 3. Cerca dati in ReportAziende
        report_data = self._search_reportaziende(company_name, vat_number)
        results["reportaziende"] = report_data
        
        # 4. Cerca altri dati aziendali tramite Serper
        additional_data = self._search_additional_company_data(company_name, vat_number)
        results["additional_sources"] = additional_data
        
        # 5. Consolida tutti i dati
        consolidated_data = self._consolidate_company_data(results)
        results["consolidated"] = consolidated_data
        
        # 6. Analizza competitor aziendali
        competitor_analysis = self._analyze_competitor_companies(
            consolidated_data, company_data.get("competitors", [])
        )
        results["competitor_analysis"] = competitor_analysis
        
        return results
    
    def _search_registro_imprese(self, company_name: str, vat_number: str) -> Dict[str, Any]:
        """Cerca dati nel Registro Imprese"""
        self.log_progress("Cercando dati nel Registro Imprese...")
        
        search_results = {}
        
        # Diverse strategie di ricerca
        search_terms = []
        if company_name:
            search_terms.append(company_name)
        if vat_number:
            search_terms.append(vat_number)
        
        for term in search_terms:
            try:
                # Cerca tramite Serper se disponibile
                if self.api_config.serper_api_key:
                    serper_results = self._search_with_serper(
                        f"site:registroimprese.it {term}"
                    )
                    if serper_results:
                        search_results["serper_results"] = serper_results
                
                # Cerca informazioni specifiche
                company_info = self._extract_company_info_from_search(term, "registroimprese.it")
                if company_info:
                    search_results["company_info"] = company_info
                
            except Exception as e:
                self.log_progress(f"Errore ricerca Registro Imprese: {str(e)}", "error")
        
        return search_results
    
    def _search_ufficio_camerale(self, company_name: str, vat_number: str) -> Dict[str, Any]:
        """Cerca dati in Ufficio Camerale"""
        self.log_progress("Cercando dati in Ufficio Camerale...")
        
        search_results = {}
        
        search_terms = []
        if company_name:
            search_terms.append(company_name)
        if vat_number:
            search_terms.append(vat_number)
        
        for term in search_terms:
            try:
                # Cerca tramite Serper se disponibile
                if self.api_config.serper_api_key:
                    serper_results = self._search_with_serper(
                        f"site:ufficiocamerale.it {term}"
                    )
                    if serper_results:
                        search_results["serper_results"] = serper_results
                
                # Cerca informazioni specifiche
                company_info = self._extract_company_info_from_search(term, "ufficiocamerale.it")
                if company_info:
                    search_results["company_info"] = company_info
                
            except Exception as e:
                self.log_progress(f"Errore ricerca Ufficio Camerale: {str(e)}", "error")
        
        return search_results
    
    def _search_reportaziende(self, company_name: str, vat_number: str) -> Dict[str, Any]:
        """Cerca dati in ReportAziende"""
        self.log_progress("Cercando dati in ReportAziende...")
        
        search_results = {}
        
        search_terms = []
        if company_name:
            search_terms.append(company_name)
        if vat_number:
            search_terms.append(vat_number)
        
        for term in search_terms:
            try:
                # Cerca tramite Serper se disponibile
                if self.api_config.serper_api_key:
                    serper_results = self._search_with_serper(
                        f"site:reportaziende.it {term}"
                    )
                    if serper_results:
                        search_results["serper_results"] = serper_results
                
                # Cerca informazioni specifiche
                company_info = self._extract_company_info_from_search(term, "reportaziende.it")
                if company_info:
                    search_results["company_info"] = company_info
                
            except Exception as e:
                self.log_progress(f"Errore ricerca ReportAziende: {str(e)}", "error")
        
        return search_results
    
    def _search_additional_company_data(self, company_name: str, vat_number: str) -> Dict[str, Any]:
        """Cerca dati aziendali aggiuntivi"""
        self.log_progress("Cercando dati aziendali aggiuntivi...")
        
        additional_data = {}
        
        # Query di ricerca specifiche
        queries = [
            f"{company_name} fatturato bilancio",
            f"{company_name} dipendenti sede legale",
            f"{company_name} codice fiscale partita iva",
            f"{company_name} capitale sociale settore"
        ]
        
        if vat_number:
            queries.append(f"partita iva {vat_number} azienda")
        
        for query in queries:
            try:
                if self.api_config.serper_api_key:
                    results = self._search_with_serper(query)
                    if results:
                        additional_data[query] = results
            except Exception as e:
                self.log_progress(f"Errore ricerca aggiuntiva: {str(e)}", "error")
        
        return additional_data
    
    def _search_with_serper(self, query: str) -> Dict[str, Any]:
        """Effettua ricerca tramite Serper"""
        if not self.api_config.serper_api_key:
            return {}
        
        headers = {
            "X-API-KEY": self.api_config.serper_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "gl": "it",
            "hl": "it",
            "num": 10
        }
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log_progress(f"Errore Serper: {str(e)}", "error")
            return {}
    
    def _extract_company_info_from_search(self, search_term: str, source: str) -> Dict[str, Any]:
        """Estrae informazioni aziendali dai risultati di ricerca"""
        
        # Cerca informazioni tramite AI
        system_prompt = f"""
        Stai analizzando risultati di ricerca per raccogliere informazioni aziendali da {source}.
        Estrai le seguenti informazioni se disponibili:
        
        - company_name: nome della società
        - vat_number: partita IVA
        - fiscal_code: codice fiscale
        - legal_form: forma giuridica (SRL, SPA, etc.)
        - share_capital: capitale sociale
        - revenue: fatturato
        - employees: numero dipendenti
        - headquarters: sede legale
        - sector: settore di attività
        - founding_date: data costituzione
        - legal_representative: rappresentante legale
        - pec_email: email PEC
        - phone: telefono
        - website: sito web
        
        Rispondi in formato JSON.
        """
        
        prompt = f"Analizza questi dati per l'azienda cercata '{search_term}' da {source}"
        
        result = self.query_openai(prompt, system_prompt)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw_analysis": result}
    
    def _consolidate_company_data(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida tutti i dati aziendali raccolti"""
        self.log_progress("Consolidando dati aziendali...")
        
        consolidated = {
            "company_name": "",
            "vat_number": "",
            "fiscal_code": "",
            "legal_form": "",
            "share_capital": "",
            "revenue": "",
            "employees": "",
            "headquarters": "",
            "sector": "",
            "founding_date": "",
            "legal_representative": "",
            "contact_info": {},
            "financial_data": {},
            "data_sources": [],
            "confidence_score": 0
        }
        
        # Raccoglie dati da tutte le fonti
        sources_data = []
        
        for source_name, source_data in all_results.items():
            if source_name == "consolidated":
                continue
                
            if isinstance(source_data, dict):
                if "company_info" in source_data:
                    sources_data.append(source_data["company_info"])
                    consolidated["data_sources"].append(source_name)
                
                # Estrae dati da risultati Serper
                if "serper_results" in source_data:
                    serper_info = self._extract_from_serper_results(source_data["serper_results"])
                    if serper_info:
                        sources_data.append(serper_info)
        
        # Consolida i dati usando AI
        if sources_data:
            ai_consolidation = self._ai_consolidate_data(sources_data)
            consolidated.update(ai_consolidation)
        
        # Calcola confidence score
        consolidated["confidence_score"] = self._calculate_confidence_score(sources_data)
        
        return consolidated
    
    def _extract_from_serper_results(self, serper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estrae informazioni dai risultati Serper"""
        extracted_info = {}
        
        if "organic" in serper_data:
            # Combina titoli e snippet per analisi AI
            text_content = ""
            for result in serper_data["organic"][:5]:
                text_content += f"Titolo: {result.get('title', '')}\n"
                text_content += f"Descrizione: {result.get('snippet', '')}\n"
                text_content += f"URL: {result.get('link', '')}\n\n"
            
            if text_content:
                system_prompt = """
                Estrai informazioni aziendali strutturate dal seguente testo.
                Cerca specificamente:
                - Nome azienda
                - Partita IVA (formato italiano)
                - Codice fiscale
                - Forma giuridica (SRL, SPA, etc.)
                - Capitale sociale
                - Fatturato
                - Numero dipendenti
                - Sede legale
                - Settore di attività
                
                Restituisci solo le informazioni che trovi esplicitamente nel testo.
                Formato JSON.
                """
                
                result = self.query_openai(text_content, system_prompt)
                
                try:
                    extracted_info = json.loads(result)
                except json.JSONDecodeError:
                    extracted_info = {"raw_text": result}
        
        return extracted_info
    
    def _ai_consolidate_data(self, sources_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Usa AI per consolidare dati da multiple fonti"""
        
        # Prepara il testo con tutti i dati
        all_data_text = ""
        for i, source in enumerate(sources_data):
            all_data_text += f"Fonte {i+1}:\n"
            all_data_text += json.dumps(source, indent=2, ensure_ascii=False)
            all_data_text += "\n\n"
        
        system_prompt = """
        Hai ricevuto dati aziendali da multiple fonti. Consolidali in un unico record accurato.
        
        Regole per il consolidamento:
        1. Se una informazione è presente in più fonti con lo stesso valore, usa quel valore
        2. Se una informazione ha valori diversi, scegli il più dettagliato/preciso
        3. Se una informazione è presente solo in una fonte, includila se sembra affidabile
        4. Normalizza i formati (es. partita IVA con 11 cifre)
        5. Rimuovi duplicati e informazioni palesemente errate
        
        Restituisci un JSON con le seguenti chiavi:
        - company_name
        - vat_number (formato italiano IT + 11 cifre)
        - fiscal_code
        - legal_form
        - share_capital (con valuta)
        - revenue (con valuta e anno se disponibile)
        - employees (numero)
        - headquarters (indirizzo completo)
        - sector
        - founding_date
        - legal_representative
        - contact_info (telefono, email, pec, sito web)
        - financial_data (altri dati finanziari)
        """
        
        result = self.query_openai(all_data_text, system_prompt)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"consolidation_error": result}
    
    def _calculate_confidence_score(self, sources_data: List[Dict[str, Any]]) -> float:
        """Calcola un punteggio di affidabilità dei dati"""
        if not sources_data:
            return 0.0
        
        # Fattori per il calcolo della confidence
        score = 0.0
        
        # Numero di fonti
        num_sources = len(sources_data)
        score += min(num_sources * 0.2, 0.6)  # Max 60% per numero fonti
        
        # Presenza di dati chiave
        key_fields = ["company_name", "vat_number", "headquarters", "sector"]
        fields_found = 0
        
        for source in sources_data:
            for field in key_fields:
                if source.get(field):
                    fields_found += 1
                    break
        
        score += (fields_found / len(key_fields)) * 0.3  # Max 30% per campi chiave
        
        # Coerenza tra fonti
        if num_sources > 1:
            consistency_score = self._check_data_consistency(sources_data)
            score += consistency_score * 0.1  # Max 10% per coerenza
        
        return min(score, 1.0)
    
    def _check_data_consistency(self, sources_data: List[Dict[str, Any]]) -> float:
        """Verifica la coerenza dei dati tra le fonti"""
        if len(sources_data) < 2:
            return 1.0
        
        # Campi da verificare per coerenza
        check_fields = ["company_name", "vat_number", "sector"]
        consistent_fields = 0
        total_checks = 0
        
        for field in check_fields:
            values = []
            for source in sources_data:
                if source.get(field):
                    values.append(source[field].lower().strip())
            
            if len(values) > 1:
                total_checks += 1
                # Verifica se tutti i valori sono simili
                unique_values = set(values)
                if len(unique_values) == 1:
                    consistent_fields += 1
                elif len(unique_values) == 2:
                    # Verifica similarità
                    val1, val2 = list(unique_values)
                    if self._similarity_check(val1, val2) > 0.8:
                        consistent_fields += 1
        
        return consistent_fields / total_checks if total_checks > 0 else 1.0
    
    def _similarity_check(self, str1: str, str2: str) -> float:
        """Verifica la similarità tra due stringhe"""
        # Semplice check di similarità
        if str1 == str2:
            return 1.0
        
        # Rimuove spazi e caratteri speciali
        clean1 = re.sub(r'[^\w]', '', str1.lower())
        clean2 = re.sub(r'[^\w]', '', str2.lower())
        
        if clean1 == clean2:
            return 0.9
        
        # Check se una è contenuta nell'altra
        if clean1 in clean2 or clean2 in clean1:
            return 0.8
        
        return 0.0
    
    def _analyze_competitor_companies(self, company_data: Dict[str, Any], 
                                   competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizza i dati aziendali dei competitor"""
        self.log_progress("Analizzando dati aziendali dei competitor...")
        
        analysis = {
            "company_profile": company_data,
            "competitor_profiles": [],
            "market_comparison": {},
            "competitive_insights": []
        }
        
        # Analizza ogni competitor
        for competitor in competitors[:3]:  # Primi 3 competitor
            comp_name = competitor.get("name", "")
            if comp_name:
                comp_data = self._quick_company_lookup(comp_name)
                analysis["competitor_profiles"].append({
                    "name": comp_name,
                    "data": comp_data
                })
        
        # Genera confronto di mercato
        if analysis["competitor_profiles"]:
            market_comparison = self._generate_market_comparison(
                company_data, analysis["competitor_profiles"]
            )
            analysis["market_comparison"] = market_comparison
        
        # Genera insights competitivi
        insights = self._generate_competitive_insights(
            company_data, analysis["competitor_profiles"]
        )
        analysis["competitive_insights"] = insights
        
        return analysis
    
    def _quick_company_lookup(self, company_name: str) -> Dict[str, Any]:
        """Ricerca rapida di dati aziendali per un competitor"""
        try:
            # Ricerca veloce con query mirata
            query = f"{company_name} partita iva sede fatturato dipendenti"
            
            if self.api_config.serper_api_key:
                serper_results = self._search_with_serper(query)
                if serper_results:
                    return self._extract_from_serper_results(serper_results)
            
            return {"company_name": company_name, "data_found": False}
            
        except Exception as e:
            self.log_progress(f"Errore lookup {company_name}: {str(e)}", "error")
            return {"company_name": company_name, "error": str(e)}
    
    def _generate_market_comparison(self, company_data: Dict[str, Any], 
                                  competitor_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera un confronto di mercato"""
        
        comparison = {
            "size_comparison": {},
            "geographic_comparison": {},
            "sector_analysis": {},
            "financial_comparison": {}
        }
        
        # Confronto dimensioni (dipendenti)
        company_employees = self._extract_number(company_data.get("employees", ""))
        competitor_employees = []
        
        for comp in competitor_profiles:
            comp_emp = self._extract_number(comp["data"].get("employees", ""))
            if comp_emp > 0:
                competitor_employees.append(comp_emp)
        
        if competitor_employees:
            avg_comp_employees = sum(competitor_employees) / len(competitor_employees)
            comparison["size_comparison"] = {
                "company_employees": company_employees,
                "avg_competitor_employees": avg_comp_employees,
                "position": "larger" if company_employees > avg_comp_employees else "smaller"
            }
        
        # Confronto geografico (sedi)
        company_location = company_data.get("headquarters", "")
        competitor_locations = [
            comp["data"].get("headquarters", "") 
            for comp in competitor_profiles 
            if comp["data"].get("headquarters")
        ]
        
        comparison["geographic_comparison"] = {
            "company_location": company_location,
            "competitor_locations": competitor_locations,
            "geographic_concentration": self._analyze_geographic_concentration(
                company_location, competitor_locations
            )
        }
        
        return comparison
    
    def _generate_competitive_insights(self, company_data: Dict[str, Any], 
                                     competitor_profiles: List[Dict[str, Any]]) -> List[str]:
        """Genera insights competitivi"""
        insights = []
        
        # Analisi dimensioni
        company_employees = self._extract_number(company_data.get("employees", ""))
        if company_employees > 0:
            competitor_sizes = [
                self._extract_number(comp["data"].get("employees", ""))
                for comp in competitor_profiles
            ]
            competitor_sizes = [size for size in competitor_sizes if size > 0]
            
            if competitor_sizes:
                avg_size = sum(competitor_sizes) / len(competitor_sizes)
                if company_employees > avg_size * 2:
                    insights.append("L'azienda è significativamente più grande dei competitor principali")
                elif company_employees < avg_size * 0.5:
                    insights.append("L'azienda è più piccola rispetto ai competitor principali")
        
        # Analisi geografica
        company_location = company_data.get("headquarters", "").lower()
        if "milano" in company_location or "roma" in company_location:
            insights.append("L'azienda ha sede in una delle principali città italiane")
        
        # Analisi settore
        company_sector = company_data.get("sector", "").lower()
        competitor_sectors = [
            comp["data"].get("sector", "").lower()
            for comp in competitor_profiles
            if comp["data"].get("sector")
        ]
        
        if competitor_sectors:
            common_sectors = [sector for sector in competitor_sectors if company_sector in sector or sector in company_sector]
            if len(common_sectors) == len(competitor_sectors):
                insights.append("Tutti i competitor operano nello stesso settore specifico")
            elif len(common_sectors) > len(competitor_sectors) * 0.5:
                insights.append("La maggior parte dei competitor opera nello stesso settore")
        
        return insights
    
    def _extract_number(self, text: str) -> int:
        """Estrae un numero da una stringa"""
        if not text:
            return 0
        
        # Cerca numeri nella stringa
        numbers = re.findall(r'\d+', str(text).replace(',', '').replace('.', ''))
        if numbers:
            return int(numbers[0])
        
        return 0
    
    def _analyze_geographic_concentration(self, company_location: str, 
                                        competitor_locations: List[str]) -> str:
        """Analizza la concentrazione geografica"""
        if not competitor_locations:
            return "Nessun dato sui competitor"
        
        # Estrae città principali
        major_cities = ["milano", "roma", "torino", "napoli", "bologna", "firenze"]
        
        company_city = None
        for city in major_cities:
            if city in company_location.lower():
                company_city = city
                break
        
        if not company_city:
            return "Localizzazione geografica non identificata"
        
        # Conta competitor nella stessa città
        same_city_count = 0
        for location in competitor_locations:
            if company_city in location.lower():
                same_city_count += 1
        
        if same_city_count == len(competitor_locations):
            return f"Alta concentrazione: tutti i competitor sono a {company_city.title()}"
        elif same_city_count > len(competitor_locations) * 0.5:
            return f"Media concentrazione: molti competitor sono a {company_city.title()}"
        else:
            return f"Bassa concentrazione: pochi competitor sono a {company_city.title()}"
