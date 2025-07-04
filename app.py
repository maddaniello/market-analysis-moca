import streamlit as st
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Aggiungi la directory corrente al path Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    # Import degli agenti con gestione errori
    from agents.base_agent import BaseAgent
    from agents.semrush_agent import SEMRushAgent
    from agents.serper_agent import SerperAgent
    from agents.social_agent import SocialAgent
    from agents.company_agent import CompanyAgent
    from agents.report_agent import ReportAgent
    
    # Import delle utilities
    from utils.validators import InputValidator
    from utils.data_processor import DataProcessor
    
    # Import delle configurazioni
    from config import APIConfig, AppConfig
    
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    IMPORT_ERROR = str(e)

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="Marketing Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MarketingAnalyzer:
    """Classe principale per l'analisi marketing"""
    
    def __init__(self):
        self.api_config = None
        self.app_config = AppConfig() if MODULES_LOADED else None
        self.agents = {}
        
    def setup_api_config(self) -> bool:
        """Configura le API keys"""
        if not MODULES_LOADED:
            return False
            
        try:
            # Prova prima dalle variabili d'ambiente
            self.api_config = APIConfig.from_env()
            
            # Se non trovate, usa quelle da Streamlit
            if not self.api_config.openai_api_key:
                self.api_config.openai_api_key = st.session_state.get('openai_key', '')
            if not self.api_config.semrush_api_key:
                self.api_config.semrush_api_key = st.session_state.get('semrush_key', '')
            if not self.api_config.serper_api_key:
                self.api_config.serper_api_key = st.session_state.get('serper_key', '')
            
            return True
        except Exception as e:
            st.error(f"Errore configurazione API: {str(e)}")
            return False
    
    def initialize_agents(self):
        """Inizializza tutti gli agenti"""
        if not self.api_config or not MODULES_LOADED:
            return False
        
        try:
            self.agents = {
                'semrush': SEMRushAgent(self.api_config, self.app_config),
                'serper': SerperAgent(self.api_config, self.app_config),
                'social': SocialAgent(self.api_config, self.app_config),
                'company': CompanyAgent(self.api_config, self.app_config),
                'report': ReportAgent(self.api_config, self.app_config)
            }
            return True
        except Exception as e:
            st.error(f"Errore inizializzazione agenti: {str(e)}")
            return False
    
    def run_analysis(self, company_input: str) -> Dict[str, Any]:
        """Esegue l'analisi completa"""
        
        if not MODULES_LOADED:
            return {"error": "Moduli non caricati correttamente"}
        
        # Valida input
        is_valid, input_type, company_data = InputValidator.validate_company_input(company_input)
        
        if not is_valid:
            return {"error": "Input non valido"}
        
        st.info(f"Tipo input riconosciuto: {input_type}")
        st.json(company_data)
        
        results = {
            "company_info": company_data,
            "input_type": input_type
        }
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. Analisi SEMRush
            status_text.text("🔍 Analizzando dati SEO con SEMRush...")
            progress_bar.progress(10)
            
            if 'semrush' in self.agents:
                semrush_results = self.agents['semrush'].analyze(company_data)
                results["semrush_analysis"] = semrush_results
                
                if not semrush_results.get("error"):
                    st.success("✅ Analisi SEMRush completata")
                else:
                    st.warning(f"⚠️ SEMRush: {semrush_results.get('error')}")
            
            progress_bar.progress(25)
            
            # 2. Ricerca competitor con Serper
            status_text.text("🌐 Cercando competitor online...")
            
            if 'serper' in self.agents:
                serper_results = self.agents['serper'].analyze(company_data)
                results["serper_analysis"] = serper_results
                
                if not serper_results.get("error"):
                    st.success("✅ Ricerca competitor completata")
                    
                    # Aggiorna company_data con competitor trovati
                    competitors = serper_results.get("competitors", {}).get("competitors", [])
                    company_data["competitors"] = competitors
                else:
                    st.warning(f"⚠️ Serper: {serper_results.get('error')}")
            
            progress_bar.progress(50)
            
            # 3. Analisi social media
            status_text.text("📱 Analizzando presenza social media...")
            
            if 'social' in self.agents:
                social_results = self.agents['social'].analyze(company_data)
                results["social_analysis"] = social_results
                
                if not social_results.get("error"):
                    st.success("✅ Analisi social completata")
                else:
                    st.warning(f"⚠️ Social: {social_results.get('error')}")
            
            progress_bar.progress(75)
            
            # 4. Dati aziendali ufficiali
            status_text.text("🏢 Raccogliendo dati aziendali ufficiali...")
            
            if 'company' in self.agents:
                company_results = self.agents['company'].analyze(company_data)
                results["company_analysis"] = company_results
                
                if not company_results.get("error"):
                    st.success("✅ Dati aziendali raccolti")
                else:
                    st.warning(f"⚠️ Company: {company_results.get('error')}")
            
            progress_bar.progress(90)
            
            # 5. Generazione report
            status_text.text("📊 Generando report completo...")
            
            if 'report' in self.agents:
                report_results = self.agents['report'].analyze(results)
                results["final_report"] = report_results
                
                if not report_results.get("error"):
                    st.success("✅ Report generato con successo!")
                else:
                    st.warning(f"⚠️ Report: {report_results.get('error')}")
            
            progress_bar.progress(100)
            status_text.text("✅ Analisi completata!")
            
            return results
            
        except Exception as e:
            st.error(f"Errore durante l'analisi: {str(e)}")
            return {"error": str(e)}

def check_modules_status():
    """Verifica lo stato dei moduli"""
    if not MODULES_LOADED:
        st.error("❌ Errore nel caricamento dei moduli")
        st.error(f"Dettaglio errore: {IMPORT_ERROR}")
        
        st.markdown("""
        ### 🔧 Come risolvere:
        
        1. **Verifica la struttura dei file**:
        ```
        marketing_analyzer/
        ├── app.py
        ├── config.py
        ├── requirements.txt
        ├── agents/
        │   ├── __init__.py
        │   ├── base_agent.py
        │   ├── semrush_agent.py
        │   ├── serper_agent.py
        │   ├── social_agent.py
        │   ├── company_agent.py
        │   └── report_agent.py
        └── utils/
            ├── __init__.py
            ├── validators.py
            └── data_processor.py
        ```
        
        2. **Assicurati che tutti i file __init__.py esistano**
        
        3. **Verifica che non ci siano errori di sintassi nei file Python**
        
        4. **Riavvia l'applicazione**
        """)
        
        return False
    
    st.success("✅ Tutti i moduli caricati correttamente")
    return True

def main():
    """Funzione principale dell'applicazione"""
    
    # Header
    st.title("📊 Marketing Analyzer")
    st.markdown("### Analisi completa per il marketing digitale")
    st.markdown("---")
    
    # Verifica stato moduli
    if not check_modules_status():
        st.stop()
    
    # Inizializza l'analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = MarketingAnalyzer()
    
    # Sidebar per configurazione
    with st.sidebar:
        st.header("⚙️ Configurazione")
        
        # API Keys
        st.subheader("🔑 API Keys")
        
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get('openai_key', ''),
            help="Inserisci la tua OpenAI API key"
        )
        
        semrush_key = st.text_input(
            "SEMRush API Key",
            type="password", 
            value=st.session_state.get('semrush_key', ''),
            help="Inserisci la tua SEMRush API key"
        )
        
        serper_key = st.text_input(
            "Serper.dev API Key",
            type="password",
            value=st.session_state.get('serper_key', ''),
            help="Inserisci la tua Serper.dev API key"
        )
        
        # Salva le chiavi in session state
        st.session_state.openai_key = openai_key
        st.session_state.semrush_key = semrush_key
        st.session_state.serper_key = serper_key
        
        # Valida API keys
        if MODULES_LOADED:
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
                    st.error(f"❌ {api.upper()}")
        
        # Info sull'app
        st.markdown("---")
        st.subheader("ℹ️ Info")
        st.info("""
        **Fonti dati:**
        - SEMRush API (SEO, competitor)
        - Serper.dev (ricerca online)
        - Social Media (scraping)
        - Registro Imprese
        - Ufficio Camerale
        - ReportAziende.it
        """)
        
        # Download dei risultati
        if 'analysis_results' in st.session_state:
            st.markdown("---")
            st.subheader("💾 Download")
            
            # JSON download
            json_data = json.dumps(
                st.session_state.analysis_results,
                ensure_ascii=False,
                indent=2
            )
            
            st.download_button(
                label="📥 Scarica JSON",
                data=json_data,
                file_name=f"analisi_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Inserisci i dati dell'azienda")
        
        # Input form
        with st.form("company_input_form"):
            company_input = st.text_input(
                "Nome azienda, URL sito web, o Partita IVA",
                placeholder="Es: Microsoft, https://microsoft.com, o IT12345678901",
                help="Puoi inserire il nome dell'azienda, l'URL del sito web, o la partita IVA italiana"
            )
            
            submit_button = st.form_submit_button("🚀 Avvia Analisi")
        
        # Risultati dell'analisi
        if submit_button:
            if not company_input:
                st.error("⚠️ Inserisci un nome azienda, URL o partita IVA")
            elif not MODULES_LOADED:
                st.error("⚠️ I moduli non sono caricati correttamente")
            else:
                # Setup e avvio analisi
                if st.session_state.analyzer.setup_api_config():
                    if st.session_state.analyzer.initialize_agents():
                        
                        with st.spinner("Analisi in corso..."):
                            results = st.session_state.analyzer.run_analysis(company_input)
                            st.session_state.analysis_results = results
                        
                        if "error" not in results:
                            st.success("🎉 Analisi completata con successo!")
                            
                            # Mostra risultati di base
                            st.json(results)
                        else:
                            st.error(f"Errore: {results['error']}")
    
    with col2:
        st.subheader("📋 Guida rapida")
        
        st.markdown("""
        **Tipi di input supportati:**
        
        🏢 **Nome azienda**
        - Es: "Apple Inc"
        - Es: "Juventus Football Club"
        
        🌐 **URL sito web** 
        - Es: "https://apple.com"
        - Es: "www.juventus.com"
        
        📄 **Partita IVA italiana**
        - Es: "IT12345678901"
        - Es: "12345678901"
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Cosa analizza:**
        
        📈 **SEO & Traffico**
        - Keywords organiche
        - Backlink profile
        - Authority score
        - Competitor SEO
        
        📱 **Social Media**
        - Presenza su piattaforme
        - Follower e engagement
        - Confronto competitor
        
        🏢 **Dati Aziendali**
        - Informazioni legali
        - Fatturato e dipendenti
        - Sede e contatti
        """)

if __name__ == "__main__":
    main()
