import streamlit as st
import requests
import json
import re
from typing import Dict, Any, Tuple, List, Optional
from urllib.parse import urlparse
from datetime import datetime
import logging
from dataclasses import dataclass

# Configurazione pagina
st.set_page_config(
    page_title="Marketing Analyzer",
    page_icon="📊",
    layout="wide"
)

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configurazione API Keys"""
    openai_api_key: str = ""
    semrush_api_key: str = ""
    serper_api_key: str = ""

class InputValidator:
    """Validatore input standalone"""
    
    @staticmethod
    def validate_company_input(input_text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Valida l'input dell'azienda"""
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
        """Verifica se il testo è un URL"""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_italian_vat(text: str) -> bool:
        """Verifica se è una partita IVA italiana"""
        clean_text = re.sub(r'[^\d]', '', text.upper().replace('IT', ''))
        if len(clean_text) == 11 and clean_text.isdigit():
            return InputValidator._validate_italian_vat_checksum(clean_text)
        return False
    
    @staticmethod
    def _validate_italian_vat_checksum(vat: str) -> bool:
        """Valida il checksum della partita IVA italiana"""
        if len(vat) != 11:
            return False
        
        try:
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
        """Estrae dominio dall'URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    @staticmethod
    def domain_to_company_name(domain: str) -> str:
        """Converte dominio in nome azienda"""
        if not domain:
            return ""
        
        extensions = ['.com', '.it', '.org', '.net', '.eu', '.co.uk']
        company_name = domain
        
        for ext in extensions:
            if company_name.endswith(ext):
                company_name = company_name[:-len(ext)]
                break
        
        return company_name.capitalize()
    
    @staticmethod
    def validate_api_keys(api_keys: Dict[str, str]) -> Dict[str, bool]:
        """Valida le API keys"""
        return {
            'openai': bool(api_keys.get('openai_api_key', '').startswith('sk-')),
            'semrush': bool(api_keys.get('semrush_api_key', '') and len(api_keys.get('semrush_api_key', '')) > 10),
            'serper': bool(api_keys.get('serper_api_key', '') and len(api_keys.get('serper_api_key', '')) > 10)
        }

class SimpleSerperAgent:
    """Agente Serper semplificato"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def search_company_info(self, company_name: str) -> Dict[str, Any]:
        """Ricerca informazioni base sull'azienda"""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": f"{company_name} azienda Italia informazioni",
                "gl": "it",
                "hl": "it",
                "num": 10
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            results = {
                "search_results": [],
                "knowledge_graph": {},
                "related_searches": []
            }
            
            # Processa risultati organici
            if "organic" in data:
                for result in data["organic"][:5]:
                    results["search_results"].append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "position": result.get("position", 0)
                    })
            
            # Processa knowledge graph
            if "knowledgeGraph" in data:
                kg = data["knowledgeGraph"]
                results["knowledge_graph"] = {
                    "title": kg.get("title", ""),
                    "type": kg.get("type", ""),
                    "description": kg.get("description", ""),
                    "website": kg.get("website", "")
                }
            
            # Processa ricerche correlate
            if "relatedSearches" in data:
                for search in data["relatedSearches"][:5]:
                    results["related_searches"].append(search.get("query", ""))
            
            return results
            
        except Exception as e:
            return {"error": f"Errore ricerca azienda: {str(e)}"}
    
    def search_competitors(self, company_name: str) -> Dict[str, Any]:
        """Ricerca competitor"""
        queries = [
            f"{company_name} competitor concorrenti",
            f"{company_name} alternative simili"
        ]
        
        all_competitors = []
        competitor_domains = set()
        
        for query in queries:
            try:
                headers = {
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "q": query,
                    "gl": "it",
                    "hl": "it",
                    "num": 8
                }
                
                response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if "organic" in data:
                    for result in data["organic"][:4]:
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
                                
            except Exception as e:
                logger.error(f"Errore ricerca competitor con query '{query}': {e}")
                continue
        
        return {
            "total_found": len(all_competitors),
            "competitors": all_competitors[:8]
        }
    
    def search_social_presence(self, company_name: str) -> Dict[str, Any]:
        """Ricerca presenza social"""
        social_platforms = ["facebook", "instagram", "linkedin", "twitter", "youtube"]
        social_results = {}
        
        for platform in social_platforms:
            try:
                headers = {
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "q": f"site:{platform}.com {company_name}",
                    "gl": "it",
                    "hl": "it",
                    "num": 3
                }
                
                response = requests.post(self.base_url, headers=headers, json=payload, timeout=20)
                response.raise_for_status()
                
                data = response.json()
                
                if "organic" in data and len(data["organic"]) > 0:
                    result = data["organic"][0]
                    link = result.get("link", "")
                    if platform in link.lower():
                        social_results[platform] = {
                            "url": link,
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", "")
                        }
                        
            except Exception as e:
                logger.error(f"Errore ricerca {platform}: {e}")
                continue
        
        return social_results
    
    def _extract_domain(self, url: str) -> str:
        """Estrae dominio dall'URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""

class SimpleSEMRushAgent:
    """Agente SEMRush semplificato"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.semrush.com/"
    
    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analizza un dominio con SEMRush"""
        if not domain:
            return {"error": "Dominio non fornito"}
        
        results = {}
        
        # Domain overview
        try:
            overview = self._get_domain_overview(domain)
            results["overview"] = overview
        except Exception as e:
            results["overview"] = {"error": str(e)}
        
        # Organic keywords
        try:
            keywords = self._get_organic_keywords(domain)
            results["keywords"] = keywords
        except Exception as e:
            results["keywords"] = {"error": str(e)}
        
        # Competitors
        try:
            competitors = self._get_competitors(domain)
            results["competitors"] = competitors
        except Exception as e:
            results["competitors"] = {"error": str(e)}
        
        return results
    
    def _get_domain_overview(self, domain: str) -> Dict[str, Any]:
        """Ottiene overview del dominio"""
        params = {
            "type": "domain_overview",
            "key": self.api_key,
            "domain": domain,
            "database": "it",
            "export_format": "json"
        }
        
        response = requests.get(self.base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            return {
                "organic_keywords": item.get("Or", 0),
                "organic_traffic": item.get("Ot", 0),
                "organic_cost": item.get("Oc", 0),
                "adwords_keywords": item.get("Ad", 0),
                "adwords_traffic": item.get("At", 0),
                "adwords_cost": item.get("Ac", 0)
            }
        
        return {"error": "Nessun dato disponibile"}
    
    def _get_organic_keywords(self, domain: str) -> Dict[str, Any]:
        """Ottiene keywords organiche"""
        params = {
            "type": "domain_organic",
            "key": self.api_key,
            "domain": domain,
            "database": "it",
            "export_format": "json",
            "display_limit": 20
        }
        
        response = requests.get(self.base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, list):
            keywords = []
            positions_1_3 = 0
            positions_4_10 = 0
            
            for item in data:
                if isinstance(item, dict):
                    pos = item.get("Po", 0)
                    keywords.append({
                        "keyword": item.get("Ph", ""),
                        "position": pos,
                        "volume": item.get("Nq", 0),
                        "cpc": item.get("Cp", 0),
                        "url": item.get("Ur", "")
                    })
                    
                    if 1 <= pos <= 3:
                        positions_1_3 += 1
                    elif 4 <= pos <= 10:
                        positions_4_10 += 1
            
            return {
                "total_keywords": len(keywords),
                "keywords_1_3": positions_1_3,
                "keywords_4_10": positions_4_10,
                "top_keywords": keywords[:10]
            }
        
        return {"error": "Nessuna keyword trovata"}
    
    def _get_competitors(self, domain: str) -> List[Dict[str, Any]]:
        """Ottiene competitor del dominio"""
        params = {
            "type": "domain_organic_organic",
            "key": self.api_key,
            "domain": domain,
            "database": "it",
            "export_format": "json",
            "display_limit": 10
        }
        
        response = requests.get(self.base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
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

class MarketingAnalyzer:
    """Analyzer principale semplificato"""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.serper_agent = None
        self.semrush_agent = None
    
    def setup_api_config(self, openai_key: str, semrush_key: str, serper_key: str):
        """Setup API keys"""
        self.api_config.openai_api_key = openai_key
        self.api_config.semrush_api_key = semrush_key
        self.api_config.serper_api_key = serper_key
        
        if serper_key:
            self.serper_agent = SimpleSerperAgent(serper_key)
        
        if semrush_key:
            self.semrush_agent = SimpleSEMRushAgent(semrush_key)
    
    def run_analysis(self, company_input: str) -> Dict[str, Any]:
        """Esegue analisi completa"""
        
        # Valida input
        is_valid, input_type, company_data = InputValidator.validate_company_input(company_input)
        
        if not is_valid:
            return {"error": "Input non valido"}
        
        results = {
            "company_info": company_data,
            "input_type": input_type,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        company_name = company_data.get("company_name", "")
        domain = company_data.get("domain", "") or company_data.get("website", "")
        
        # Extract domain from website if needed
        if domain and not company_data.get("domain"):
            domain = InputValidator.extract_domain(domain)
        
        # Progress tracking
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 1. Ricerca informazioni azienda
                if self.serper_agent:
                    status_text.text("🔍 Cercando informazioni azienda...")
                    progress_bar.progress(20)
                    
                    company_info = self.serper_agent.search_company_info(company_name)
                    results["company_search"] = company_info
                    
                    if "error" not in company_info:
                        st.success("✅ Informazioni azienda trovate")
                    else:
                        st.warning(f"⚠️ {company_info['error']}")
                
                # 2. Analisi SEMRush
                if self.semrush_agent and domain:
                    status_text.text("📊 Analizzando SEO con SEMRush...")
                    progress_bar.progress(40)
                    
                    seo_analysis = self.semrush_agent.analyze_domain(domain)
                    results["seo_analysis"] = seo_analysis
                    
                    if not any("error" in v for v in seo_analysis.values() if isinstance(v, dict)):
                        st.success("✅ Analisi SEO completata")
                    else:
                        st.warning("⚠️ Analisi SEO parziale")
                
                # 3. Ricerca competitor
                if self.serper_agent:
                    status_text.text("🎯 Cercando competitor...")
                    progress_bar.progress(60)
                    
                    competitors = self.serper_agent.search_competitors(company_name)
                    results["competitors"] = competitors
                    
                    if "error" not in competitors:
                        st.success(f"✅ Trovati {competitors['total_found']} competitor")
                    else:
                        st.warning(f"⚠️ {competitors['error']}")
                
                # 4. Ricerca social
                if self.serper_agent:
                    status_text.text("📱 Cercando presenza social...")
                    progress_bar.progress(80)
                    
                    social_presence = self.serper_agent.search_social_presence(company_name)
                    results["social_presence"] = social_presence
                    
                    if social_presence:
                        st.success(f"✅ Trovati {len(social_presence)} profili social")
                    else:
                        st.warning("⚠️ Nessun profilo social trovato")
                
                progress_bar.progress(100)
                status_text.text("✅ Analisi completata!")
                
                return results
                
            except Exception as e:
                st.error(f"Errore durante l'analisi: {str(e)}")
                return {"error": str(e)}

def display_results(results: Dict[str, Any]):
    """Mostra i risultati dell'analisi"""
    
    if "error" in results:
        st.error(f"Errore: {results['error']}")
        return
    
    # Tabs per organizzare i risultati
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Info Azienda", 
        "📊 SEO Analysis", 
        "🎯 Competitor",
        "📱 Social Media", 
        "📄 Report Completo"
    ])
    
    with tab1:
        display_company_info(results)
    
    with tab2:
        display_seo_analysis(results)
    
    with tab3:
        display_competitors(results)
    
    with tab4:
        display_social_presence(results)
    
    with tab5:
        display_full_report(results)

def display_company_info(results: Dict[str, Any]):
    """Mostra informazioni azienda"""
    
    company_info = results.get("company_info", {})
    company_search = results.get("company_search", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Dati Input")
        st.markdown(f"**Nome:** {company_info.get('company_name', 'N/A')}")
        st.markdown(f"**Tipo:** {results.get('input_type', 'N/A')}")
        if company_info.get('website'):
            st.markdown(f"**Website:** {company_info.get('website')}")
        if company_info.get('domain'):
            st.markdown(f"**Dominio:** {company_info.get('domain')}")
        if company_info.get('vat_number'):
            st.markdown(f"**P.IVA:** {company_info.get('vat_number')}")
    
    with col2:
        st.subheader("🔍 Knowledge Graph")
        
        kg = company_search.get("knowledge_graph", {})
        if kg:
            st.markdown(f"**Titolo:** {kg.get('title', 'N/A')}")
            st.markdown(f"**Tipo:** {kg.get('type', 'N/A')}")
            st.markdown(f"**Descrizione:** {kg.get('description', 'N/A')}")
            if kg.get('website'):
                st.markdown(f"**Sito:** {kg.get('website')}")
        else:
            st.info("Nessun Knowledge Graph trovato")
    
    # Risultati di ricerca
    search_results = company_search.get("search_results", [])
    if search_results:
        st.subheader("🌐 Risultati Ricerca")
        
        for i, result in enumerate(search_results, 1):
            with st.expander(f"{i}. {result.get('title', 'N/A')}"):
                st.markdown(f"**URL:** {result.get('link', 'N/A')}")
                st.markdown(f"**Snippet:** {result.get('snippet', 'N/A')}")

def display_seo_analysis(results: Dict[str, Any]):
    """Mostra analisi SEO"""
    
    seo_analysis = results.get("seo_analysis", {})
    
    if not seo_analysis:
        st.warning("⚠️ Analisi SEO non disponibile - Inserisci SEMRush API key")
        return
    
    # Overview
    overview = seo_analysis.get("overview", {})
    if overview and "error" not in overview:
        st.subheader("📊 Overview SEO")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Keywords Organiche", overview.get("organic_keywords", 0))
        
        with col2:
            st.metric("Traffico Organico", overview.get("organic_traffic", 0))
        
        with col3:
            st.metric("Costo Organico", f"€{overview.get('organic_cost', 0):,.0f}")
        
        with col4:
            st.metric("Keywords ADV", overview.get("adwords_keywords", 0))
    
    # Keywords
    keywords = seo_analysis.get("keywords", {})
    if keywords and "error" not in keywords:
        st.subheader("🎯 Top Keywords")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Keywords Totali", keywords.get("total_keywords", 0))
            st.metric("Posizioni 1-3", keywords.get("keywords_1_3", 0))
            st.metric("Posizioni 4-10", keywords.get("keywords_4_10", 0))
        
        with col2:
            top_keywords = keywords.get("top_keywords", [])
            if top_keywords:
                st.markdown("**Prime 5 Keywords:**")
                for kw in top_keywords[:5]:
                    st.markdown(f"- **{kw.get('keyword', 'N/A')}** (Pos: {kw.get('position', 'N/A')}, Vol: {kw.get('volume', 'N/A')})")
    
    # Competitor SEO
    competitors = seo_analysis.get("competitors", [])
    if competitors and not (isinstance(competitors, dict) and "error" in competitors):
        st.subheader("🏆 Competitor SEO")
        
        for i, comp in enumerate(competitors[:5], 1):
            st.markdown(f"{i}. **{comp.get('domain', 'N/A')}** - Keywords: {comp.get('se_keywords', 0)}, Traffico: {comp.get('se_traffic', 0)}")

def display_competitors(results: Dict[str, Any]):
    """Mostra analisi competitor"""
    
    competitors_data = results.get("competitors", {})
    
    if not competitors_data or "error" in competitors_data:
        st.warning("⚠️ Dati competitor non disponibili")
        return
    
    competitors = competitors_data.get("competitors", [])
    total_found = competitors_data.get("total_found", 0)
    
    st.subheader(f"🎯 Competitor Identificati ({total_found})")
    
    if competitors:
        for i, comp in enumerate(competitors, 1):
            with st.expander(f"{i}. {comp.get('name', 'N/A')}"):
                st.markdown(f"**Dominio:** {comp.get('domain', 'N/A')}")
                st.markdown(f"**URL:** {comp.get('url', 'N/A')}")
                st.markdown(f"**Descrizione:** {comp.get('description', 'N/A')}")
    else:
        st.info("Nessun competitor trovato")

def display_social_presence(results: Dict[str, Any]):
    """Mostra presenza social"""
    
    social_presence = results.get("social_presence", {})
    
    if not social_presence:
        st.warning("⚠️ Nessun profilo social trovato")
        return
    
    st.subheader(f"📱 Presenza Social ({len(social_presence)} piattaforme)")
    
    for platform, data in social_presence.items():
        with st.expander(f"{platform.title()}"):
            st.markdown(f"**URL:** {data.get('url', 'N/A')}")
            st.markdown(f"**Titolo:** {data.get('title', 'N/A')}")
            st.markdown(f"**Descrizione:** {data.get('snippet', 'N/A')}")

def display_full_report(results: Dict[str, Any]):
    """Mostra report completo"""
    
    st.subheader("📄 Report Completo JSON")
    st.json(results)
    
    # Download
    json_data = json.dumps(results, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="📥 Scarica Report JSON",
        data=json_data,
        file_name=f"marketing_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )

def main():
    """Funzione principale"""
    
    # Header
    st.title("📊 Marketing Analyzer")
    st.markdown("### Analisi marketing digitale completa")
    st.markdown("---")
    
    # Inizializza analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = MarketingAnalyzer()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurazione API")
        
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get('openai_key', ''),
            help="Opzionale - per analisi AI avanzate"
        )
        
        semrush_key = st.text_input(
            "SEMRush API Key",
            type="password",
            value=st.session_state.get('semrush_key', ''),
            help="Per analisi SEO dettagliate"
        )
        
        serper_key = st.text_input(
            "Serper.dev API Key",
            type="password",
            value=st.session_state.get('serper_key', ''),
            help="OBBLIGATORIO - per ricerca online"
        )
        
        # Salva in session state
        st.session_state.openai_key = openai_key
        st.session_state.semrush_key = semrush_key
        st.session_state.serper_key = serper_key
        
        # Valida API keys
        api_keys = {
            'openai_api_key': openai_key,
            'semrush_api_key': semrush_key,
            'serper_api_key': serper_key
        }
        
        validation_results = InputValidator.validate_api_keys(api_keys)
        
        st.subheader("📊 Stato API")
        for api, is_valid in validation_results.items():
            if is_valid:
                st.success(f"✅ {api.upper()}")
            else:
                if api == 'serper':
                    st.error(f"❌ {api.upper()} - OBBLIGATORIO")
                else:
                    st.warning(f"⚠️ {api.upper()} - Opzionale")
        
        # Setup analyzer
        st.session_state.analyzer.setup_api_config(openai_key, semrush_key, serper_key)
        
        st.markdown("---")
        st.subheader("ℹ️ Funzionalità")
        st.info("""
        **Con Serper.dev:**
        ✅ Ricerca informazioni azienda
        ✅ Identificazione competitor  
        ✅ Ricerca profili social
        
        **Con SEMRush:**
        ✅ Analisi SEO approfondita
        ✅ Keywords e ranking
        ✅ Competitor SEO
        
        **Con OpenAI:**
        ✅ Analisi AI avanzate
        ✅ Insights strategici
        """)
        
        # Test connessione
        if st.button("🔍 Test Connessione Serper"):
            if serper_key:
                test_connection(serper_key)
            else:
                st.error("Inserisci prima la Serper API key")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Analisi Azienda")
        
        with st.form("analysis_form"):
            company_input = st.text_input(
                "Nome azienda, URL sito web, o Partita IVA",
                placeholder="Es: Microsoft, https://microsoft.com, IT12345678901",
                help="Inserisci nome azienda, URL completo, o partita IVA italiana"
            )
            
            # Opzioni
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                include_seo = st.checkbox("Analisi SEO", value=True, disabled=not semrush_key)
                include_social = st.checkbox("Ricerca Social", value=True)
            
            with col_opt2:
                include_competitors = st.checkbox("Analisi Competitor", value=True)
                detailed_analysis = st.checkbox("Analisi Dettagliata", value=False)
            
            analyze_button = st.form_submit_button("🚀 Avvia Analisi", type="primary")
        
        # Risultati
        if analyze_button:
            if not company_input:
                st.error("⚠️ Inserisci un'azienda da analizzare")
            elif not serper_key:
                st.error("⚠️ Serper.dev API key obbligatoria per l'analisi")
            else:
                with st.spinner("Analisi in corso..."):
                    results = st.session_state.analyzer.run_analysis(company_input)
                    st.session_state.analysis_results = results
                
                if "error" not in results:
                    st.success("🎉 Analisi completata!")
                    
                    # Mostra riassunto rapido
                    show_quick_summary(results)
                    
                    # Mostra risultati completi
                    st.markdown("---")
                    display_results(results)
                else:
                    st.error(f"Errore: {results['error']}")
    
    with col2:
        st.subheader("📋 Guida")
        
        st.markdown("""
        **Input supportati:**
        
        🏢 **Nome azienda**
        - "Apple Inc"
        - "Juventus Football Club"
        
        🌐 **URL completo**
        - "https://apple.com"
        - "www.juventus.com"
        
        📄 **Partita IVA**
        - "IT12345678901"
        - "12345678901"
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Analisi incluse:**
        
        📈 **Ricerca Online**
        - Informazioni azienda
        - Knowledge Graph Google
        - Risultati di ricerca
        
        🎯 **Competitor**
        - Identificazione automatica
        - Analisi domini
        - Descrizioni business
        
        📱 **Social Media**
        - Facebook, Instagram
        - LinkedIn, Twitter, YouTube
        - URLs e descrizioni
        
        📊 **SEO (con SEMRush)**
        - Keywords organiche
        - Traffico e posizioni
        - Competitor SEO
        """)
        
        # Esempi di test
        st.markdown("---")
        st.subheader("🧪 Test Rapidi")
        
        if st.button("Test: Ferrari"):
            st.session_state.test_input = "Ferrari"
        
        if st.button("Test: https://apple.com"):
            st.session_state.test_input = "https://apple.com"
        
        if st.button("Test: IT00159560366"):
            st.session_state.test_input = "IT00159560366"
        
        if 'test_input' in st.session_state:
            st.code(f"Input test: {st.session_state.test_input}")

def show_quick_summary(results: Dict[str, Any]):
    """Mostra riassunto rapido dei risultati"""
    
    st.subheader("⚡ Riassunto Rapido")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Info azienda
    company_info = results.get("company_info", {})
    with col1:
        st.metric(
            "Tipo Input", 
            results.get("input_type", "N/A").upper()
        )
    
    # Competitor
    competitors = results.get("competitors", {})
    with col2:
        competitor_count = competitors.get("total_found", 0) if isinstance(competitors, dict) else 0
        st.metric("Competitor", competitor_count)
    
    # Social
    social_presence = results.get("social_presence", {})
    with col3:
        social_count = len(social_presence) if isinstance(social_presence, dict) else 0
        st.metric("Profili Social", social_count)
    
    # SEO
    seo_analysis = results.get("seo_analysis", {})
    with col4:
        if seo_analysis:
            overview = seo_analysis.get("overview", {})
            keywords = overview.get("organic_keywords", 0) if isinstance(overview, dict) else 0
        else:
            keywords = "N/A"
        st.metric("Keywords SEO", keywords)

def test_connection(api_key: str):
    """Testa la connessione Serper"""
    try:
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": "test connection",
            "gl": "it",
            "num": 1
        }
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Connessione Serper OK")
            data = response.json()
            if "organic" in data:
                st.info(f"Test riuscito - {len(data['organic'])} risultati")
        else:
            st.error(f"❌ Errore HTTP {response.status_code}")
            if response.status_code == 401:
                st.error("API key non valida")
            elif response.status_code == 429:
                st.error("Limite rate raggiunto")
                
    except Exception as e:
        st.error(f"❌ Errore connessione: {str(e)}")

# Download dei risultati in sidebar
def add_download_section():
    """Aggiunge sezione download in sidebar"""
    if 'analysis_results' in st.session_state:
        with st.sidebar:
            st.markdown("---")
            st.subheader("💾 Download Risultati")
            
            results = st.session_state.analysis_results
            
            # JSON completo
            json_data = json.dumps(results, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSON Completo",
                data=json_data,
                file_name=f"analisi_completa_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
            
            # CSV competitor (se disponibili)
            competitors = results.get("competitors", {}).get("competitors", [])
            if competitors:
                import pandas as pd
                
                df = pd.DataFrame(competitors)
                csv_data = df.to_csv(index=False)
                
                st.download_button(
                    label="📊 CSV Competitor",
                    data=csv_data,
                    file_name=f"competitor_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            
            # Report testuale
            if st.button("📄 Genera Report Testuale"):
                generate_text_report(results)

def generate_text_report(results: Dict[str, Any]):
    """Genera report in formato testuale"""
    
    company_info = results.get("company_info", {})
    company_name = company_info.get("company_name", "Azienda")
    
    report = f"""
# Report Analisi Marketing - {company_name}

**Data Analisi:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Tipo Input:** {results.get('input_type', 'N/A')}

## 📋 Informazioni Azienda

**Nome:** {company_name}
"""
    
    if company_info.get('website'):
        report += f"**Website:** {company_info.get('website')}\n"
    
    if company_info.get('vat_number'):
        report += f"**Partita IVA:** {company_info.get('vat_number')}\n"
    
    # Knowledge Graph
    company_search = results.get("company_search", {})
    kg = company_search.get("knowledge_graph", {})
    if kg:
        report += f"""
## 🔍 Knowledge Graph Google

**Titolo:** {kg.get('title', 'N/A')}
**Tipo:** {kg.get('type', 'N/A')}
**Descrizione:** {kg.get('description', 'N/A')}
"""
    
    # Competitor
    competitors = results.get("competitors", {})
    if competitors and isinstance(competitors, dict):
        competitor_list = competitors.get("competitors", [])
        report += f"""
## 🎯 Competitor Identificati ({len(competitor_list)})

"""
        for i, comp in enumerate(competitor_list[:5], 1):
            report += f"{i}. **{comp.get('name', 'N/A')}**\n"
            report += f"   - Dominio: {comp.get('domain', 'N/A')}\n"
            report += f"   - Descrizione: {comp.get('description', 'N/A')}\n\n"
    
    # Social
    social_presence = results.get("social_presence", {})
    if social_presence:
        report += f"""
## 📱 Presenza Social Media ({len(social_presence)} piattaforme)

"""
        for platform, data in social_presence.items():
            report += f"**{platform.title()}:** {data.get('url', 'N/A')}\n"
    
    # SEO
    seo_analysis = results.get("seo_analysis", {})
    if seo_analysis:
        overview = seo_analysis.get("overview", {})
        if overview and "error" not in overview:
            report += f"""
## 📊 Analisi SEO

**Keywords Organiche:** {overview.get('organic_keywords', 0)}
**Traffico Organico:** {overview.get('organic_traffic', 0)}
**Costo Organico:** €{overview.get('organic_cost', 0):,.0f}
"""
        
        keywords = seo_analysis.get("keywords", {})
        if keywords and "error" not in keywords:
            report += f"""
**Posizioni 1-3:** {keywords.get('keywords_1_3', 0)}
**Posizioni 4-10:** {keywords.get('keywords_4_10', 0)}
"""
    
    report += f"""
---
*Report generato automaticamente da Marketing Analyzer*
*Timestamp: {results.get('analysis_timestamp', 'N/A')}*
"""
    
    # Download del report
    st.download_button(
        label="📥 Scarica Report Testuale",
        data=report,
        file_name=f"report_{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )

if __name__ == "__main__":
    main()
    add_download_section()
