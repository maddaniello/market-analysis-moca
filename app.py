import streamlit as st
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Import degli agenti
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
        self.app_config = AppConfig()
        self.agents = {}
        
    def setup_api_config(self) -> bool:
        """Configura le API keys"""
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
        if not self.api_config:
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

def main():
    """Funzione principale dell'applicazione"""
    
    # Header
    st.title("📊 Marketing Analyzer")
    st.markdown("### Analisi completa per il marketing digitale")
    st.markdown("---")
    
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
            
            # Opzioni avanzate
            with st.expander("🔧 Opzioni avanzate"):
                include_social = st.checkbox("Includi analisi social media", value=True)
                include_competitors = st.checkbox("Includi analisi competitor", value=True)
                include_company_data = st.checkbox("Includi dati aziendali ufficiali", value=True)
                deep_analysis = st.checkbox("Analisi approfondita (più lenta)", value=False)
            
            submit_button = st.form_submit_button("🚀 Avvia Analisi")
        
        # Risultati dell'analisi
        if submit_button:
            if not company_input:
                st.error("⚠️ Inserisci un nome azienda, URL o partita IVA")
            elif not any(validation_results.values()):
                st.error("⚠️ Configura almeno una API key nella sidebar")
            else:
                # Setup e avvio analisi
                if st.session_state.analyzer.setup_api_config():
                    if st.session_state.analyzer.initialize_agents():
                        
                        with st.spinner("Analisi in corso..."):
                            results = st.session_state.analyzer.run_analysis(company_input)
                            st.session_state.analysis_results = results
                        
                        if "error" not in results:
                            st.success("🎉 Analisi completata con successo!")
                            
                            # Mostra risultati principali
                            display_results(results)
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

def display_results(results: Dict[str, Any]):
    """Mostra i risultati dell'analisi"""
    
    if "final_report" not in results:
        st.warning("Report non disponibile")
        return
    
    report_data = results["final_report"]
    
    # Tab per organizzare i risultati
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary", 
        "🏢 Profilo Azienda", 
        "📈 Presenza Digitale",
        "🎯 Competitor", 
        "📋 Report Completo"
    ])
    
    with tab1:
        display_executive_summary(report_data)
    
    with tab2:
        display_company_profile(results)
    
    with tab3:
        display_digital_presence(results)
    
    with tab4:
        display_competitor_analysis(results)
    
    with tab5:
        display_full_report(report_data)

def display_executive_summary(report_data: Dict[str, Any]):
    """Mostra executive summary"""
    
    structured_report = report_data.get("structured_report", {})
    executive_summary = structured_report.get("executive_summary", {})
    
    # AI Summary
    if "ai_generated_summary" in executive_summary:
        st.subheader("🎯 Riassunto Esecutivo")
        st.markdown(executive_summary["ai_generated_summary"])
    
    # Metriche chiave
    key_metrics = executive_summary.get("key_metrics", {})
    if key_metrics:
        st.subheader("📊 Metriche Chiave")
        
        # Crea colonne per le metriche
        metrics_cols = st.columns(4)
        
        metric_items = list(key_metrics.items())
        for i, (metric, value) in enumerate(metric_items[:4]):
            with metrics_cols[i % 4]:
                st.metric(
                    label=metric.replace("_", " ").title(),
                    value=value
                )
    
    # Findings critici
    critical_findings = executive_summary.get("critical_findings", [])
    if critical_findings:
        st.subheader("🚨 Risultati Critici")
        for finding in critical_findings:
            if "🔴" in finding:
                st.error(finding)
            elif "🟡" in finding:
                st.warning(finding)
            else:
                st.info(finding)
    
    # Azioni immediate
    immediate_actions = executive_summary.get("immediate_actions", [])
    if immediate_actions:
        st.subheader("⚡ Azioni Immediate")
        for action in immediate_actions:
            st.markdown(f"- {action}")

def display_company_profile(results: Dict[str, Any]):
    """Mostra profilo azienda"""
    
    company_data = results.get("company_info", {})
    company_analysis = results.get("company_analysis", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Informazioni Base")
        
        if company_data:
            st.markdown(f"**Nome:** {company_data.get('company_name', 'N/A')}")
            st.markdown(f"**Sito Web:** {company_data.get('website', 'N/A')}")
            st.markdown(f"**Tipo Input:** {results.get('input_type', 'N/A')}")
        
        # Dati consolidati
        consolidated = company_analysis.get("consolidated", {})
        if consolidated:
            st.markdown("---")
            st.subheader("🏢 Dati Aziendali")
            
            st.markdown(f"**P.IVA:** {consolidated.get('vat_number', 'N/A')}")
            st.markdown(f"**Forma Giuridica:** {consolidated.get('legal_form', 'N/A')}")
            st.markdown(f"**Sede:** {consolidated.get('headquarters', 'N/A')}")
            st.markdown(f"**Settore:** {consolidated.get('sector', 'N/A')}")
    
    with col2:
        st.subheader("📊 Metriche Business")
        
        if consolidated:
            st.metric("Dipendenti", consolidated.get('employees', 'N/A'))
            st.metric("Fatturato", consolidated.get('revenue', 'N/A'))
            st.metric("Capitale Sociale", consolidated.get('share_capital', 'N/A'))
            
            # Confidence score
            confidence = consolidated.get('confidence_score', 0)
            st.metric(
                "Affidabilità Dati", 
                f"{confidence:.1%}",
                help="Indica l'affidabilità dei dati raccolti basata su numero e coerenza delle fonti"
            )

def display_digital_presence(results: Dict[str, Any]):
    """Mostra analisi presenza digitale"""
    
    semrush_data = results.get("semrush_analysis", {})
    social_data = results.get("social_analysis", {})
    
    # SEO Performance
    if semrush_data and not semrush_data.get("error"):
        st.subheader("🔍 Performance SEO")
        
        col1, col2, col3, col4 = st.columns(4)
        
        keyword_data = semrush_data.get("keywords", {})
        backlink_data = semrush_data.get("backlinks", {})
        
        with col1:
            st.metric("Keyword Organiche", keyword_data.get("total_keywords", 0))
        
        with col2:
            st.metric("Posizioni Top 3", keyword_data.get("keywords_1_3", 0))
        
        with col3:
            st.metric("Backlink Totali", backlink_data.get("total_backlinks", 0))
        
        with col4:
            st.metric("Authority Score", backlink_data.get("authority_score", 0))
        
        # Top Keywords
        top_keywords = keyword_data.get("keyword_list", [])
        if top_keywords:
            st.subheader("🎯 Top Keywords")
            
            keywords_df = []
            for kw in top_keywords[:10]:
                keywords_df.append({
                    "Keyword": kw.get("keyword", ""),
                    "Posizione": kw.get("position", 0),
                    "Volume": kw.get("volume", 0),
                    "Difficoltà": kw.get("difficulty", 0)
                })
            
            if keywords_df:
                import pandas as pd
                st.dataframe(pd.DataFrame(keywords_df))
    else:
        st.warning("⚠️ Dati SEO non disponibili")
    
    # Social Media
    if social_data and not social_data.get("error"):
        st.subheader("📱 Presenza Social Media")
        
        social_analytics = social_data.get("social_analytics", {})
        
        if social_analytics:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Piattaforme Attive", len(social_analytics))
                
                total_followers = 0
                for platform_data in social_analytics.values():
                    if not platform_data.get("error"):
                        followers = platform_data.get("followers", 0) or platform_data.get("subscribers", 0)
                        total_followers += followers if isinstance(followers, int) else 0
                
                st.metric("Follower Totali", total_followers)
            
            with col2:
                # Dettagli per piattaforma
                st.markdown("**Dettagli per piattaforma:**")
                for platform, data in social_analytics.items():
                    if not data.get("error"):
                        followers = data.get("followers", 0) or data.get("subscribers", 0)
                        st.markdown(f"- **{platform.title()}:** {followers:,} follower")
    else:
        st.warning("⚠️ Dati social non disponibili")

def display_competitor_analysis(results: Dict[str, Any]):
    """Mostra analisi competitor"""
    
    serper_data = results.get("serper_analysis", {})
    semrush_data = results.get("semrush_analysis", {})
    
    # Competitor da Serper
    if serper_data and not serper_data.get("error"):
        competitors = serper_data.get("competitors", {}).get("competitors", [])
        
        if competitors:
            st.subheader("🎯 Competitor Identificati")
            
            for i, comp in enumerate(competitors[:5], 1):
                with st.expander(f"{i}. {comp.get('name', 'N/A')}"):
                    st.markdown(f"**Dominio:** {comp.get('domain', 'N/A')}")
                    st.markdown(f"**Descrizione:** {comp.get('description', 'N/A')}")
                    if comp.get('url'):
                        st.markdown(f"**URL:** {comp.get('url')}")
        
        # Dettagli competitor
        competitor_details = serper_data.get("competitor_details", [])
        if competitor_details:
            st.subheader("📊 Analisi Dettagliata Competitor")
            
            for detail in competitor_details[:3]:
                comp_name = detail.get("name", "N/A")
                
                with st.expander(f"📈 {comp_name}"):
                    if detail.get("services"):
                        st.markdown("**Servizi:**")
                        for service in detail["services"][:5]:
                            st.markdown(f"- {service}")
                    
                    if detail.get("products"):
                        st.markdown("**Prodotti:**")
                        for product in detail["products"][:5]:
                            st.markdown(f"- {product}")
                    
                    if detail.get("sector"):
                        st.markdown(f"**Settore:** {detail['sector']}")
    
    # Competitor SEO da SEMRush
    if semrush_data and not semrush_data.get("error"):
        seo_competitors = semrush_data.get("competitors", [])
        
        if seo_competitors:
            st.subheader("🔍 Competitor SEO")
            
            import pandas as pd
            
            comp_df = []
            for comp in seo_competitors[:10]:
                comp_df.append({
                    "Dominio": comp.get("domain", ""),
                    "Keywords Comuni": comp.get("common_keywords", 0),
                    "Keywords SEO": comp.get("se_keywords", 0),
                    "Traffico SEO": comp.get("se_traffic", 0),
                    "Livello Competizione": comp.get("competition_level", 0)
                })
            
            if comp_df:
                st.dataframe(pd.DataFrame(comp_df))

def display_full_report(report_data: Dict[str, Any]):
    """Mostra report completo formattato"""
    
    formatted_report = report_data.get("formatted_report", "")
    
    if formatted_report:
        st.subheader("📋 Report Completo")
        st.markdown(formatted_report)
        
        # Download del report
        st.download_button(
            label="📥 Scarica Report",
            data=formatted_report,
            file_name=f"marketing_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )
    else:
        st.warning("Report formattato non disponibile")
    
    # Dati raw per debugging (collassabile)
    with st.expander("🔧 Dati Raw (Debug)"):
        st.json(report_data)

if __name__ == "__main__":
    main()