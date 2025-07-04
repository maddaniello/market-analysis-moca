section += f"**URL:** {competitor.get('url', 'N/A')}\n"
            section += f"**Descrizione:** {competitor.get('description', 'N/A')}\n"
            
            # Analisi SEO competitor (se disponibile)
            if "seo_analysis" in competitor:
                seo_comp = competitor["seo_analysis"]
                overview = seo_comp.get("overview", {})
                if overview and "error" not in overview:
                    section += f"**Keywords SEO:** {overview.get('organic_keywords', 0):,}\n"
                    section += f"**Traffico Organico:** {overview.get('organic_traffic', 0):,}\n"
                    section += f"**Valore Traffico:** €{overview.get('organic_cost', 0):,.0f}\n"
            
            # Analisi dettagliata (se disponibile)
            if "detailed_research" in competitor:
                detailed = competitor["detailed_research"]
                # Estrai insights dalle ricerche dettagliate
                for search_key, search_data in detailed.items():
                    if isinstance(search_data, dict) and "results" in search_data:
                        results = search_data["results"]
                        if "organic" in results and len(results["organic"]) > 0:
                            first_result = results["organic"][0]
                            snippet = first_result.get("snippet", "")
                            if len(snippet) > 50:  # Solo se abbiamo info significative
                                section += f"**Info Business:** {snippet[:200]}...\n"
                                break
            
            section += "\n"
        
        # Analisi comparative
        section += "### Analisi Comparativa\n"
        
        # Confronto domini e presenza online
        total_competitors = len(competitors_data)
        section += f"**Numero competitor identificati:** {total_competitors}\n"
        
        # Analizza la distribuzione dei competitor per settore/tipologia
        domains = [comp.get("domain", "") for comp in competitors_data if comp.get("domain")]
        section += f"**Competitor con presenza web:** {len(domains)}\n"
        
        return section
    
    def _section_swot_analysis(self, swot_data: Dict[str, Any]) -> str:
        """Sezione 7: Analisi SWOT"""
        
        section = """
## 7. ANALISI SWOT

"""
        
        # Punti di forza
        punti_forza = swot_data.get('punti_forza', [])
        if punti_forza and punti_forza != ['N/A']:
            section += "### Punti di Forza\n"
            for punto in punti_forza:
                section += f"- {punto}\n"
        
        # Punti di debolezza
        punti_debolezza = swot_data.get('punti_debolezza', [])
        if punti_debolezza and punti_debolezza != ['N/A']:
            section += "\n### Punti di Debolezza\n"
            for punto in punti_debolezza:
                section += f"- {punto}\n"
        
        # Opportunità
        opportunita = swot_data.get('opportunita', [])
        if opportunita and opportunita != ['N/A']:
            section += "\n### Opportunità\n"
            for opportunita_item in opportunita:
                section += f"- {opportunita_item}\n"
        
        # Minacce
        minacce = swot_data.get('minacce', [])
        if minacce and minacce != ['N/A']:
            section += "\n### Minacce\n"
            for minaccia in minacce:
                section += f"- {minaccia}\n"
        
        # Proposizione di valore
        proposizione = swot_data.get('proposizione_valore', '')
        if proposizione and proposizione != 'N/A':
            section += f"\n## PROPOSIZIONE DI VALORE\n\n{proposizione}\n"
        
        return section
    
    def _section_strategic_recommendations(self, recommendations: Dict[str, Any]) -> str:
        """Sezione 8: Raccomandazioni Strategiche"""
        
        section = """
## 8. RACCOMANDAZIONI STRATEGICHE

"""
        
        recommendation_sections = [
            ('sviluppo_prodotto', 'Sviluppo del Prodotto'),
            ('marketing_comunicazione', 'Marketing e Comunicazione'),
            ('espansione_commerciale', 'Espansione Commerciale'),
            ('struttura_organizzativa', 'Struttura Organizzativa'),
            ('innovazione_digitale', 'Innovazione Digitale')
        ]
        
        for key, title in recommendation_sections:
            items = recommendations.get(key, [])
            if items and items != ['N/A']:
                section += f"### {title}\n"
                for item in items:
                    section += f"- {item}\n"
                section += "\n"
        
        # Priorità e timeline
        priorita = recommendations.get('priorita_immediate', [])
        if priorita and priorita != ['N/A']:
            section += "### Priorità Immediate (0-3 mesi)\n"
            for priorita_item in priorita:
                section += f"- {priorita_item}\n"
        
        obiettivi_medio = recommendations.get('obiettivi_medio_termine', [])
        if obiettivi_medio and obiettivi_medio != ['N/A']:
            section += "\n### Obiettivi Medio Termine (6-12 mesi)\n"
            for obiettivo in obiettivi_medio:
                section += f"- {obiettivo}\n"
        
        visione_lungo = recommendations.get('visione_lungo_termine', [])
        if visione_lungo and visione_lungo != ['N/A']:
            section += "\n### Visione Lungo Termine (2-3 anni)\n"
            for visione in visione_lungo:
                section += f"- {visione}\n"
        
        return section
    
    def _section_conclusions(self, company_name: str, all_analysis_data: Dict[str, Any]) -> str:
        """Sezione 9: Conclusioni"""
        
        section = """
## 9. CONCLUSIONI

"""
        
        # Genera conclusioni basate sui dati raccolti
        competitors_count = len(all_analysis_data.get("competitors_analysis", []))
        social_platforms = len(all_analysis_data.get("social_analysis", {}).get("platforms_found", {}))
        
        seo_data = all_analysis_data.get("seo_analysis", {})
        has_seo_data = seo_data and "error" not in seo_data
        
        section += f"{company_name} rappresenta "
        
        if has_seo_data:
            organic_keywords = seo_data.get("overview", {}).get("organic_keywords", 0)
            if organic_keywords > 1000:
                section += "un'azienda con una solida presenza digitale, "
            elif organic_keywords > 100:
                section += "un'azienda in crescita nella presenza digitale, "
            else:
                section += "un'azienda con opportunità di miglioramento nella presenza digitale, "
        else:
            section += "un'azienda "
        
        if competitors_count > 5:
            section += "operante in un mercato competitivo con numerosi player. "
        elif competitors_count > 2:
            section += "con una concorrenza moderata nel suo settore. "
        else:
            section += "in un mercato di nicchia o in fase di sviluppo. "
        
        if social_platforms >= 4:
            section += "L'azienda dimostra una buona maturità digitale con presenza su multiple piattaforme social."
        elif social_platforms >= 2:
            section += "La presenza social è presente ma può essere ampliata per raggiungere un pubblico più vasto."
        else:
            section += "Esiste un significativo potenziale di crescita nella presenza sui social media."
        
        section += "\n\n"
        
        # Sfide e opportunità chiave
        section += "### Sfide e Opportunità Chiave\n\n"
        
        if has_seo_data:
            keywords_1_3 = seo_data.get("keywords", {}).get("keywords_1_3", 0)
            total_keywords = seo_data.get("keywords", {}).get("total_keywords", 0)
            
            if total_keywords > 0:
                top_percentage = (keywords_1_3 / total_keywords) * 100
                if top_percentage < 10:
                    section += "**Opportunità SEO:** Significativo potenziale di miglioramento nel posizionamento delle keyword principali. "
                elif top_percentage > 25:
                    section += "**Punto di Forza SEO:** Buon posizionamento nelle prime posizioni per le keyword principali. "
        
        if competitors_count > 0:
            section += f"**Analisi Competitiva:** Identificati {competitors_count} competitor principali che richiedono monitoraggio strategico. "
        
        section += "\n\n"
        
        # Raccomandazioni finali
        section += "### Raccomandazioni Finali\n\n"
        section += "Per il futuro sviluppo, si raccomanda di:\n\n"
        section += "1. **Prioritizzare il miglioramento della presenza digitale** attraverso ottimizzazione SEO e content marketing\n"
        section += "2. **Sviluppare una strategia social media integrata** per aumentare engagement e reach\n"
        section += "3. **Monitorare costantemente i competitor** per identificare opportunità e minacce\n"
        section += "4. **Investire in analytics e measurement** per tracciare il progresso delle iniziative digitali\n"
        section += "5. **Considerare partnership strategiche** per accelerare la crescita nel mercato di riferimento\n\n"
        
        # Chiusura
        section += f"Con una strategia ben strutturata e un'implementazione coerente, {company_name} ha tutte le potenzialità per rafforzare significativamente la propria posizione di mercato e raggiungere nuovi livelli di successo.\n\n"
        
        section += "---\n"
        section += f"*Report generato automaticamente da Marketing Analyzer Pro il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}*\n"
        section += "*Questo report si basa su dati pubblici disponibili al momento dell'analisi*\n"
        
        return section

class AdvancedMarketingAnalyzer:
    """Analyzer principale avanzato che coordina tutte le analisi"""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.serper_agent = None
        self.semrush_agent = None
        self.openai_analyzer = None
        self.social_analyzer = None
        self.report_generator = None
    
    def setup_api_config(self, openai_key: str, semrush_key: str, serper_key: str):
        """Setup delle API keys"""
        self.api_config.openai_api_key = openai_key
        self.api_config.semrush_api_key = semrush_key
        self.api_config.serper_api_key = serper_key
        
        # Inizializza gli agenti disponibili
        if serper_key:
            self.serper_agent = AdvancedSerperAgent(serper_key)
            self.social_analyzer = AdvancedSocialMediaAnalyzer(self.serper_agent)
        
        if semrush_key:
            self.semrush_agent = AdvancedSEMRushAgent(semrush_key)
        
        if openai_key:
            self.openai_analyzer = OpenAIAnalyzer(openai_key)
        
        self.report_generator = ComprehensiveReportGenerator(self.openai_analyzer)
    
    def run_comprehensive_analysis(self, company_input: str) -> Dict[str, Any]:
        """Esegue l'analisi completa in stile Venezianico"""
        
        # Valida input
        is_valid, input_type, company_data = InputValidator.validate_company_input(company_input)
        
        if not is_valid:
            return {"error": "Input non valido"}
        
        st.info(f"🎯 Tipo input riconosciuto: **{input_type.upper()}**")
        
        # Inizializza risultati
        results = {
            "company_info": company_data,
            "input_type": input_type,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_status": {}
        }
        
        company_name = company_data.get("company_name", "")
        domain = company_data.get("domain", "") or InputValidator.extract_domain(company_data.get("website", ""))
        
        # Progress tracking con più dettagli
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 1. RICERCA APPROFONDITA AZIENDA (20%)
                status_text.text("🔍 Ricerca approfondita informazioni azienda...")
                progress_bar.progress(5)
                
                if self.serper_agent:
                    company_research = self.serper_agent.deep_company_research(company_name, domain)
                    results["company_research"] = company_research
                    results["analysis_status"]["company_research"] = "✅ Completata"
                    st.success("✅ Ricerca azienda completata")
                else:
                    results["analysis_status"]["company_research"] = "❌ Serper non disponibile"
                
                progress_bar.progress(20)
                
                # 2. ANALISI SEO COMPLETA (20%)
                status_text.text("📊 Analisi SEO completa con SEMRush...")
                
                if self.semrush_agent and domain:
                    seo_analysis = self.semrush_agent.comprehensive_seo_analysis(domain)
                    results["seo_analysis"] = seo_analysis
                    results["analysis_status"]["seo_analysis"] = "✅ Completata"
                    st.success("✅ Analisi SEO completata")
                else:
                    results["analysis_status"]["seo_analysis"] = "⚠️ SEMRush non disponibile o dominio mancante"
                    if not domain:
                        st.warning("⚠️ Dominio non identificato per analisi SEO")
                    else:
                        st.warning("⚠️ SEMRush API non configurata")
                
                progress_bar.progress(40)
                
                # 3. RICERCA E ANALISI COMPETITOR (25%)
                status_text.text("🎯 Ricerca e analisi competitor...")
                
                if self.serper_agent:
                    # Identifica settore dall'analisi precedente
                    sector = self._extract_sector_from_research(results.get("company_research", {}))
                    
                    competitors = self.serper_agent.research_competitors(company_name, sector)
                    
                    # Analisi dettagliata dei top 3 competitor
                    detailed_competitors = []
                    for i, competitor in enumerate(competitors[:3]):
                        status_text.text(f"🔍 Analizzando competitor {i+1}/3: {competitor.get('name', 'N/A')}")
                        
                        detailed_analysis = self.serper_agent.analyze_competitor_details(competitor)
                        
                        # Analisi SEO del competitor se disponibile
                        if self.semrush_agent and competitor.get("domain"):
                            comp_seo = self.semrush_agent.analyze_competitor_seo(competitor["domain"])
                            detailed_analysis["seo_analysis"] = comp_seo
                        
                        detailed_competitors.append(detailed_analysis)
                        
                        # Update progress
                        progress_bar.progress(40 + (i + 1) * 8)
                    
                    results["competitors_analysis"] = detailed_competitors
                    results["analysis_status"]["competitors_analysis"] = f"✅ Analizzati {len(detailed_competitors)} competitor"
                    st.success(f"✅ Analisi competitor completata ({len(detailed_competitors)} competitor)")
                else:
                    results["analysis_status"]["competitors_analysis"] = "❌ Serper non disponibile"
                
                progress_bar.progress(65)
                
                # 4. ANALISI SOCIAL MEDIA COMPLETA (15%)
                status_text.text("📱 Analisi completa social media...")
                
                if self.social_analyzer:
                    social_analysis = self.social_analyzer.comprehensive_social_analysis(company_name)
                    results["social_analysis"] = social_analysis
                    
                    platforms_found = len(social_analysis.get("platforms_found", {}))
                    results["analysis_status"]["social_analysis"] = f"✅ Trovate {platforms_found} piattaforme"
                    st.success(f"✅ Analisi social completata ({platforms_found} piattaforme)")
                else:
                    results["analysis_status"]["social_analysis"] = "❌ Social analyzer non disponibile"
                
                progress_bar.progress(80)
                
                # 5. RICERCA TREND DI MERCATO (10%)
                status_text.text("📈 Analisi trend di mercato...")
                
                if self.serper_agent:
                    sector = self._extract_sector_from_research(results.get("company_research", {}))
                    if sector:
                        market_trends = self.serper_agent.research_market_trends(sector, company_name)
                        results["market_trends"] = market_trends
                        results["analysis_status"]["market_trends"] = "✅ Completata"
                        st.success("✅ Analisi trend di mercato completata")
                    else:
                        results["analysis_status"]["market_trends"] = "⚠️ Settore non identificato"
                else:
                    results["analysis_status"]["market_trends"] = "❌ Serper non disponibile"
                
                progress_bar.progress(90)
                
                # 6. GENERAZIONE REPORT COMPLETO (10%)
                status_text.text("📋 Generazione report completo...")
                
                comprehensive_report = self.report_generator.generate_complete_report(
                    company_data, results
                )
                
                results["comprehensive_report"] = comprehensive_report
                results["analysis_status"]["report_generation"] = "✅ Report generato"
                
                progress_bar.progress(100)
                status_text.text("✅ Analisi completa terminata!")
                
                st.success("🎉 Analisi completa terminata con successo!")
                
                return results
                
            except Exception as e:
                st.error(f"Errore durante l'analisi: {str(e)}")
                results["error"] = str(e)
                return results
    
    def _extract_sector_from_research(self, company_research: Dict[str, Any]) -> str:
        """Estrae il settore dalle ricerche aziendali"""
        
        # Cerca in knowledge graph
        company_info = company_research.get("company_info", {})
        kg = company_info.get("knowledge_graph", {})
        
        if kg.get("type"):
            return kg["type"]
        
        # Cerca nei risultati di ricerca
        for search_key in ["company_info", "business_info"]:
            search_data = company_research.get(search_key, {})
            if "organic" in search_data:
                for result in search_data["organic"][:3]:
                    snippet = result.get("snippet", "").lower()
                    
                    # Pattern comuni per settori
                    sector_patterns = [
                        (r"settore\s+(\w+)", "settore"),
                        (r"industria\s+(\w+)", "industria"),
                        (r"azienda\s+di\s+(\w+)", "azienda"),
                        (r"leader\s+nel\s+(\w+)", "leader"),
                        (r"specializzata\s+in\s+(\w+)", "specializzazione")
                    ]
                    
                    for pattern, _ in sector_patterns:
                        match = re.search(pattern, snippet)
                        if match:
                            return match.group(1).capitalize()
        
        return "Generale"

def main():
    """Funzione principale dell'applicazione avanzata"""
    
    # Header con stile migliorato
    st.title("📊 Marketing Analyzer Pro")
    st.markdown("### 🚀 Analisi marketing completa in stile professionale")
    st.markdown("*Genera report dettagliati come quello di Venezianico con analisi AI avanzate*")
    st.markdown("---")
    
    # Inizializza analyzer
    if 'advanced_analyzer' not in st.session_state:
        st.session_state.advanced_analyzer = AdvancedMarketingAnalyzer()
    
    # Sidebar migliorata
    with st.sidebar:
        st.header("⚙️ Configurazione API")
        st.markdown("*Configura le API per abilitare funzionalità avanzate*")
        
        # API Keys con descrizioni migliorate
        openai_key = st.text_input(
            "🤖 OpenAI API Key",
            type="password",
            value=st.session_state.get('openai_key', ''),
            help="OBBLIGATORIA per analisi AI avanzate, SWOT, raccomandazioni strategiche"
        )
        
        semrush_key = st.text_input(
            "📊 SEMRush API Key",
            type="password",
            value=st.session_state.get('semrush_key', ''),
            help="Per analisi SEO dettagliate, keyword, backlink, competitor SEO"
        )
        
        serper_key = st.text_input(
            "🔍 Serper.dev API Key",
            type="password",
            value=st.session_state.get('serper_key', ''),
            help="OBBLIGATORIA per ricerca online, competitor, social media"
        )
        
        # Salva in session state
        st.session_state.openai_key = openai_key
        st.session_state.semrush_key = semrush_key
        st.session_state.serper_key = serper_key
        
        # Setup analyzer
        st.session_state.advanced_analyzer.setup_api_config(openai_key, semrush_key, serper_key)
        
        # Status API con icone migliorate
        st.markdown("---")
        st.subheader("🔌 Status API")
        
        api_status = [
            ("OpenAI", openai_key.startswith('sk-') if openai_key else False, "🤖"),
            ("SEMRush", len(semrush_key) > 10 if semrush_key else False, "📊"), 
            ("Serper", len(serper_key) > 10 if serper_key else False, "🔍")
        ]
        
        for api_name, is_valid, icon in api_status:
            if is_valid:
                st.success(f"{icon} {api_name}: Configurata")
            else:
                st.error(f"{icon} {api_name}: Non configurata")
        
        # Funzionalità disponibili
        st.markdown("---")
        st.subheader("⭐ Funzionalità Report")
        
        features = [
            ("✅ Profilo aziendale completo", True),
            ("✅ Analisi finanziaria", openai_key != ""),
            ("✅ Prodotti e servizi", openai_key != ""),
            ("✅ SEO e keyword analysis", semrush_key != ""),
            ("✅ Analisi competitor dettagliata", serper_key != ""),
            ("✅ Social media completo", serper_key != ""),
            ("✅ Trend di mercato", serper_key != ""),
            ("✅ Analisi SWOT", openai_key != ""),
            ("✅ Raccomandazioni strategiche", openai_key != "")
        ]
        
        for feature, enabled in features:
            if enabled:
                st.markdown(feature)
            else:
                st.markdown(feature.replace("✅", "⚠️"))
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Analisi Azienda Completa")
        
        # Form di input migliorato
        with st.form("comprehensive_analysis_form"):
            st.markdown("**Inserisci i dati dell'azienda da analizzare:**")
            
            company_input = st.text_input(
                "Nome azienda, URL sito web, o Partita IVA",
                placeholder="Es: Venezianico, https://venezianico.com, IT04427770278",
                help="Il sistema riconoscerà automaticamente il tipo di input e adatterà l'analisi"
            )
            
            # Opzioni di analisi
            st.markdown("**Opzioni di analisi:**")
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                deep_competitor = st.checkbox(
                    "🎯 Analisi competitor approfondita", 
                    value=True,
                    help="Analizza in dettaglio i primi 3 competitor"
                )
                comprehensive_seo = st.checkbox(
                    "📊 SEO analysis completa", 
                    value=True, 
                    disabled=not semrush_key,
                    help="Richiede SEMRush API"
                )
            
            with col_opt2:
                ai_insights = st.checkbox(
                    "🤖 AI insights avanzati", 
                    value=True, 
                    disabled=not openai_key,
                    help="Richiede OpenAI API"
                )
                market_research = st.checkbox(
                    "📈 Ricerca trend mercato", 
                    value=True,
                    help="Analizza trend e dinamiche di settore"
                )
            
            analyze_button = st.form_submit_button(
                "🚀 Avvia Analisi Completa", 
                type="primary",
                help="Genera un report completo in stile professionale"
            )
        
        # Risultati analisi
        if analyze_button:
            if not company_input:
                st.error("⚠️ Inserisci un'azienda da analizzare")
            elif not serper_key:
                st.error("⚠️ Serper.dev API key obbligatoria per l'analisi")
            else:
                # Avviso sui tempi
                st.info("⏱️ L'analisi completa richiede 3-5 minuti. Per favore attendi...")
                
                with st.spinner("Analisi in corso..."):
                    results = st.session_state.advanced_analyzer.run_comprehensive_analysis(company_input)
                    st.session_state.comprehensive_results = results
                
                if "error" not in results:
                    st.success("🎉 Analisi completa terminata!")
                    
                    # Mostra status delle analisi
                    with st.expander("📊 Status Analisi", expanded=True):
                        status_data = results.get("analysis_status", {})
                        for analysis, status in status_data.items():
                            st.markdown(f"**{analysis.replace('_', ' ').title()}:** {status}")
                    
                    # Mostra report completo
                    if "comprehensive_report" in results:
                        st.markdown("---")
                        display_comprehensive_report(results)
                    
                else:
                    st.error(f"❌ Errore: {results['error']}")
    
    with col2:
        st.subheader("📋 Guida Completa")
        
        st.markdown("""
        **Report generato include:**
        
        📊 **1. Profilo Aziendale**
        - Nome, P.IVA, sede legale
        - Anno fondazione, settore
        - Missione aziendale
        
        💰 **2. Analisi Finanziaria**
        - Evoluzione fatturato
        - Patrimonio netto, dipendenti
        - Trend di crescita
        
        🛍️ **3. Prodotti e Servizi**
        - Prodotti principali
        - Caratteristiche distintive
        - Altri servizi
        
        🌐 **4. Presenza Digitale**
        - Performance SEO completa
        - Social media dettagliato
        - Metriche engagement
        
        🎯 **5. Mercato e Competitor**
        - Competitor top 3 analizzati
        - Posizionamento mercato
        - Trend di settore
        
        ⚡ **6. Analisi SWOT**
        - Punti forza/debolezza
        - Opportunità/minacce
        - Proposizione valore
        
        📈 **7. Raccomandazioni**
        - Strategiche dettagliate
        - Timeline implementazione
        - Priorità immediate
        """)
        
        st.markdown("---")
        
        # Esempi di test migliorati
        st.subheader("🧪 Esempi Test")
        
        examples = [
            ("🏢 Venezianico (Orologi)", "Venezianico"),
            ("🌐 Apple Inc.", "https://apple.com"),
            ("📄 P.IVA Intesa Sanpaolo", "IT00359200447"),
            ("🚗 Ferrari", "Ferrari"),
            ("👕 Gucci", "https://gucci.com")
        ]
        
        for label, value in examples:
            if st.button(label, key=f"example_{value}"):
                st.session_state.example_input = value
                st.info(f"Esempio selezionato: {value}")

def display_comprehensive_report(results: Dict[str, Any]):
    """Mostra il report completo con interfaccia migliorata"""
    
    comprehensive_report = results.get("comprehensive_report", "")
    
    if not comprehensive_report:
        st.warning("⚠️ Report completo non disponibile")
        return
    
    # Tab per organizzare la visualizzazione
    tab1, tab2, tab3 = st.tabs(["📄 Report Completo", "📊 Dati Strutturati", "💾 Download"])
    
    with tab1:
        st.subheader("📄 Report Marketing Completo")
        st.markdown("*Report professionale in stile Venezianico*")
        
        # Mostra il report con formatting migliorato
        st.markdown(comprehensive_report)
        
        # Bottone per copiare il report
        if st.button("📋 Copia Report negli Appunti"):
            try:
                # Nota: questo funziona solo in alcuni browser
                st.write("📋 Report copiato! (Usa Ctrl+A, Ctrl+C se necessario)")
            except:
                st.info("💡 Usa Ctrl+A per selezionare tutto, poi Ctrl+C per copiare")
    
    with tab2:
        st.subheader("📊 Dati Strutturati JSON")
        st.markdown("*Tutti i dati raccolti durante l'analisi*")
        
        # Mostra dati strutturati con sezioni collassabili
        sections_to_show = [
            ("company_info", "🏢 Informazioni Azienda"),
            ("company_research", "🔍 Ricerca Approfondita"),
            ("seo_analysis", "📊 Analisi SEO"),
            ("competitors_analysis", "🎯 Analisi Competitor"),
            ("social_analysis", "📱 Analisi Social"),
            ("market_trends", "📈 Trend Mercato"),
            ("analysis_status", "✅ Status Analisi")
        ]
        
        for key, title in sections_to_show:
            if key in results:
                with st.expander(title):
                    st.json(results[key])
    
    with tab3:
        st.subheader("💾 Download Report")
        st.markdown("*Scarica il report in diversi formati*")
        
        company_name = results.get("company_info", {}).get("company_name", "azienda")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # Download Markdown
        st.download_button(
            label="📥 Scarica Report Markdown",
            data=comprehensive_report,
            file_name=f"report_marketing_{company_name.lower().replace(' ', '_')}_{timestamp}.md",
            mime="text/markdown",
            help="Report completo in formato Markdown"
        )
        
        # Download JSON completo
        json_data = json.dumps(results, ensure_ascii=False, indent=2)
        st.download_button(
            label="📊 Scarica Dati JSON",
            data=json_data,
            file_name=f"dati_analisi_{company_name.lower().replace(' ', '_')}_{timestamp}.json",
            mime="application/json",
            help="Tutti i dati strutturati in formato JSON"
        )
        
        # Download CSV competitor (se disponibili)
        competitors = results.get("competitors_analysis", [])
        if competitors:
            try:
                import pandas as pd
                
                # Prepara dati competitor per CSV
                competitor_rows = []
                for comp in competitors:
                    basic_info = comp.get("basic_info", {})
                    seo_data = comp.get("seo_analysis", {}).get("overview", {})
                    
                    row = {
                        "Nome": basic_info.get("name", ""),
                        "Dominio": basic_info.get("domain", ""),
                        "URL": basic_info.get("url", ""),
                        "Descrizione": basic_info.get("description", "")[:100] + "...",
                        "Keywords_SEO": seo_data.get("organic_keywords", 0),
                        "Traffico_Organico": seo_data.get("organic_traffic", 0),
                        "Valore_Traffico": seo_data.get("organic_cost", 0)
                    }
                    competitor_rows.append(row)
                
                df = pd.DataFrame(competitor_rows)
                csv_data = df.to_csv(index=False)
                
                st.download_button(
                    label="📊 Scarica CSV Competitor",
                    data=csv_data,
                    file_name=f"competitor_analysis_{company_name.lower().replace(' ', '_')}_{timestamp}.csv",
                    mime="text/csv",
                    help="Dati competitor in formato CSV per Excel"
                )
                
            except ImportError:
                st.warning("⚠️ Pandas non disponibile per export CSV")
        
        # Download report TXT semplificato
        txt_report = comprehensive_report.replace("#", "").replace("*", "").replace("**", "")
        st.download_button(
            label="📄 Scarica Report TXT",
            data=txt_report,
            file_name=f"report_semplice_{company_name.lower().replace(' ', '_')}_{timestamp}.txt",
            mime="text/plain",
            help="Report in formato testo semplice"
        )
        
        # Informazioni aggiuntive
        st.markdown("---")
        st.info("""
        💡 **Suggerimenti per l'utilizzo:**
        
        - **Markdown**: Perfetto per documentazione e condivisione
        - **JSON**: Per analisi tecniche e integrazioni
        - **CSV**: Per analisi competitor in Excel/Google Sheets
        - **TXT**: Per versioni semplificate e compatibilità universale
        """)

# Funzioni di utilità aggiuntive

def show_analysis_summary(results: Dict[str, Any]):
    """Mostra un riassunto dell'analisi in card visive"""
    
    st.subheader("📊 Riassunto Analisi")
    
    # Metriche principali in colonne
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Competitor trovati
    competitors_count = len(results.get("competitors_analysis", []))
    with col1:
        st.metric("🎯 Competitor", competitors_count)
    
    # Piattaforme social
    social_platforms = len(results.get("social_analysis", {}).get("platforms_found", {}))
    with col2:
        st.metric("📱 Social Platforms", social_platforms)
    
    # Keywords SEO
    seo_data = results.get("seo_analysis", {})
    keywords = seo_data.get("overview", {}).get("organic_keywords", 0) if seo_data else 0
    with col3:
        st.metric("📊 Keywords SEO", f"{keywords:,}")
    
    # Traffico organico
    traffic = seo_data.get("overview", {}).get("organic_traffic", 0) if seo_data else 0
    with col4:
        st.metric("🌐 Traffico Organico", f"{traffic:,}")
    
    # Authority Score
    authority = seo_data.get("backlinks", {}).get("authority_score", 0) if seo_data else 0
    with col5:
        st.metric("⭐ Authority Score", authority)

def generate_executive_summary(results: Dict[str, Any]) -> str:
    """Genera un executive summary basato sui risultati"""
    
    company_name = results.get("company_info", {}).get("company_name", "L'azienda")
    competitors_count = len(results.get("competitors_analysis", []))
    social_platforms = len(results.get("social_analysis", {}).get("platforms_found", {}))
    
    seo_data = results.get("seo_analysis", {})
    has_strong_seo = False
    if seo_data and "overview" in seo_data:
        keywords = seo_data["overview"].get("organic_keywords", 0)
        has_strong_seo = keywords > 500
    
    summary = f"""
## 📋 Executive Summary

{company_name} presenta {"una solida presenza digitale" if has_strong_seo else "opportunità di crescita digitale"} 
nel panorama competitivo del proprio settore.

**Highlights Principali:**
- 🎯 **Competitor identificati:** {competitors_count} principali player nel settore
- 📱 **Presenza social:** Attiva su {social_platforms} piattaforme principali
- 📊 **SEO Performance:** {"Posizionamento consolidato" if has_strong_seo else "Margini di miglioramento significativi"}

**Raccomandazioni immediate:**
1. {"Mantenere il vantaggio competitivo" if has_strong_seo else "Investire in ottimizzazione SEO"}
2. {"Espandere la presenza social" if social_platforms < 4 else "Ottimizzare l'engagement sui social"}
3. Monitorare costantemente le mosse dei competitor principali

*Analisi completa disponibile nelle sezioni seguenti del report.*
"""
    
    return summary

def add_branding_footer():
    """Aggiunge footer con branding"""
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin: 20px 0;'>
        <h4>📊 Marketing Analyzer Pro</h4>
        <p><em>Report professionale generato con intelligenza artificiale</em></p>
        <p>🤖 Powered by OpenAI GPT-4 | 📊 SEMRush API | 🔍 Serper.dev</p>
        <small>Versione: 2.0 | Ultima modifica: Dicembre 2024</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Esegui l'applicazione
    main()
    
    # Mostra riassunto se ci sono risultati
    if 'comprehensive_results' in st.session_state:
        results = st.session_state.comprehensive_results
        if "error" not in results:
            st.markdown("---")
            show_analysis_summary(results)
    
    # Footer con branding
    add_branding_footer()                "paid_traffic": overview.get("adwords_traffic", 0),
                "paid_cost": overview.get("adwords_cost", 0)
            }
        else:
            return overview

class AdvancedSocialMediaAnalyzer:
    """Analyzer avanzato per social media"""
    
    def __init__(self, serper_agent):
        self.serper_agent = serper_agent
    
    def comprehensive_social_analysis(self, company_name: str) -> Dict[str, Any]:
        """Analisi completa dei social media"""
        
        social_platforms = {
            "instagram": "instagram.com",
            "facebook": "facebook.com", 
            "linkedin": "linkedin.com",
            "twitter": "twitter.com",
            "youtube": "youtube.com",
            "tiktok": "tiktok.com"
        }
        
        social_analysis = {
            "platforms_found": {},
            "engagement_analysis": {},
            "content_analysis": {},
            "social_metrics": {}
        }
        
        for platform, domain in social_platforms.items():
            platform_data = self._analyze_platform(company_name, platform, domain)
            
            if platform_data and "url" in platform_data:
                social_analysis["platforms_found"][platform] = platform_data
                
                # Analisi metriche dettagliate per piattaforma
                if platform == "instagram":
                    detailed_metrics = self._get_instagram_metrics(company_name)
                    social_analysis["social_metrics"]["instagram"] = detailed_metrics
                elif platform == "facebook":
                    detailed_metrics = self._get_facebook_metrics(company_name)
                    social_analysis["social_metrics"]["facebook"] = detailed_metrics
                elif platform == "tiktok":
                    detailed_metrics = self._get_tiktok_metrics(company_name)
                    social_analysis["social_metrics"]["tiktok"] = detailed_metrics
                elif platform == "youtube":
                    detailed_metrics = self._get_youtube_metrics(company_name)
                    social_analysis["social_metrics"]["youtube"] = detailed_metrics
        
        # Analisi del contenuto social
        social_analysis["content_analysis"] = self._analyze_social_content(company_name)
        
        # Calcola engagement complessivo
        social_analysis["engagement_analysis"] = self._calculate_overall_engagement(social_analysis)
        
        return social_analysis
    
    def _analyze_platform(self, company_name: str, platform: str, domain: str) -> Dict[str, Any]:
        """Analizza una singola piattaforma social"""
        
        query = f"site:{domain} {company_name}"
        results = self.serper_agent._search(query)
        
        if "organic" in results and len(results["organic"]) > 0:
            result = results["organic"][0]
            link = result.get("link", "")
            
            if platform in link.lower():
                return {
                    "platform": platform,
                    "url": link,
                    "title": result.get("title", ""),
                    "description": result.get("snippet", "")
                }
        
        return {}
    
    def _get_instagram_metrics(self, company_name: str) -> Dict[str, Any]:
        """Cerca metriche specifiche di Instagram"""
        
        queries = [
            f"{company_name} instagram follower engagement",
            f"{company_name} instagram statistics metrics",
            f'"{company_name}" instagram insights'
        ]
        
        metrics = {
            "followers": "N/A",
            "engagement_rate": "N/A", 
            "avg_likes": "N/A",
            "avg_comments": "N/A",
            "verified": "N/A",
            "posts_count": "N/A"
        }
        
        for query in queries:
            try:
                results = self.serper_agent._search(query)
                
                # Analizza i risultati per estrarre metriche
                if "organic" in results:
                    for result in results["organic"]:
                        text = f"{result.get('title', '')} {result.get('snippet', '')}"
                        
                        # Cerca pattern per follower
                        follower_match = re.search(r'(\d+(?:\.\d+)?[KMkm]?)\s*(?:follower|seguaci)', text, re.IGNORECASE)
                        if follower_match and metrics["followers"] == "N/A":
                            metrics["followers"] = follower_match.group(1)
                        
                        # Cerca engagement rate
                        engagement_match = re.search(r'engagement.*?(\d+(?:\.\d+)?%)', text, re.IGNORECASE)
                        if engagement_match and metrics["engagement_rate"] == "N/A":
                            metrics["engagement_rate"] = engagement_match.group(1)
                        
                        # Cerca verificato
                        if "verificat" in text.lower() or "verified" in text.lower():
                            metrics["verified"] = "Sì"
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore metriche Instagram: {e}")
                continue
        
        return metrics
    
    def _get_facebook_metrics(self, company_name: str) -> Dict[str, Any]:
        """Cerca metriche specifiche di Facebook"""
        
        queries = [
            f"{company_name} facebook page followers",
            f"{company_name} facebook statistics engagement"
        ]
        
        metrics = {
            "followers": "N/A",
            "page_likes": "N/A",
            "engagement_rate": "N/A",
            "posts_per_week": "N/A"
        }
        
        for query in queries:
            try:
                results = self.serper_agent._search(query)
                
                if "organic" in results:
                    for result in results["organic"]:
                        text = f"{result.get('title', '')} {result.get('snippet', '')}"
                        
                        # Cerca follower/likes
                        follower_match = re.search(r'(\d+(?:\.\d+)?[KMkm]?)\s*(?:follower|like|mi piace)', text, re.IGNORECASE)
                        if follower_match and metrics["followers"] == "N/A":
                            metrics["followers"] = follower_match.group(1)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore metriche Facebook: {e}")
                continue
        
        return metrics
    
    def _get_tiktok_metrics(self, company_name: str) -> Dict[str, Any]:
        """Cerca metriche specifiche di TikTok"""
        
        queries = [
            f"{company_name} tiktok followers views",
            f"{company_name} tiktok statistics engagement"
        ]
        
        metrics = {
            "followers": "N/A",
            "total_videos": "N/A",
            "total_likes": "N/A",
            "engagement_rate": "N/A",
            "verified": "N/A"
        }
        
        for query in queries:
            try:
                results = self.serper_agent._search(query)
                
                if "organic" in results:
                    for result in results["organic"]:
                        text = f"{result.get('title', '')} {result.get('snippet', '')}"
                        
                        # Cerca follower
                        follower_match = re.search(r'(\d+(?:\.\d+)?[KMkm]?)\s*follower', text, re.IGNORECASE)
                        if follower_match and metrics["followers"] == "N/A":
                            metrics["followers"] = follower_match.group(1)
                        
                        # Cerca video count
                        video_match = re.search(r'(\d+)\s*video', text, re.IGNORECASE)
                        if video_match and metrics["total_videos"] == "N/A":
                            metrics["total_videos"] = video_match.group(1)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore metriche TikTok: {e}")
                continue
        
        return metrics
    
    def _get_youtube_metrics(self, company_name: str) -> Dict[str, Any]:
        """Cerca metriche specifiche di YouTube"""
        
        queries = [
            f"{company_name} youtube channel subscribers views",
            f"{company_name} youtube statistics"
        ]
        
        metrics = {
            "subscribers": "N/A",
            "total_views": "N/A",
            "total_videos": "N/A",
            "avg_views_per_video": "N/A"
        }
        
        for query in queries:
            try:
                results = self.serper_agent._search(query)
                
                if "organic" in results:
                    for result in results["organic"]:
                        text = f"{result.get('title', '')} {result.get('snippet', '')}"
                        
                        # Cerca subscriber
                        sub_match = re.search(r'(\d+(?:\.\d+)?[KMkm]?)\s*(?:subscriber|iscritti)', text, re.IGNORECASE)
                        if sub_match and metrics["subscribers"] == "N/A":
                            metrics["subscribers"] = sub_match.group(1)
                        
                        # Cerca visualizzazioni
                        views_match = re.search(r'(\d+(?:\.\d+)?[KMkm]?)\s*(?:view|visualizzazioni)', text, re.IGNORECASE)
                        if views_match and metrics["total_views"] == "N/A":
                            metrics["total_views"] = views_match.group(1)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore metriche YouTube: {e}")
                continue
        
        return metrics
    
    def _analyze_social_content(self, company_name: str) -> Dict[str, Any]:
        """Analizza il tipo di contenuto sui social"""
        
        content_queries = [
            f"{company_name} social media strategy content",
            f"{company_name} instagram posts type content",
            f"{company_name} social media marketing approach"
        ]
        
        content_analysis = {
            "content_types": [],
            "posting_frequency": "N/A",
            "content_themes": [],
            "hashtag_strategy": "N/A"
        }
        
        for query in content_queries:
            try:
                results = self.serper_agent._search(query)
                
                if "organic" in results:
                    for result in results["organic"]:
                        snippet = result.get("snippet", "")
                        
                        # Analizza tipi di contenuto
                        if "video" in snippet.lower():
                            content_analysis["content_types"].append("Video")
                        if "photo" in snippet.lower() or "immagini" in snippet.lower():
                            content_analysis["content_types"].append("Immagini")
                        if "stories" in snippet.lower():
                            content_analysis["content_types"].append("Stories")
                        if "reel" in snippet.lower():
                            content_analysis["content_types"].append("Reels")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore analisi contenuto: {e}")
                continue
        
        # Rimuovi duplicati
        content_analysis["content_types"] = list(set(content_analysis["content_types"]))
        
        return content_analysis
    
    def _calculate_overall_engagement(self, social_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcola engagement complessivo"""
        
        platforms_count = len(social_analysis.get("platforms_found", {}))
        
        # Calcola punteggio di presenza
        max_platforms = 6  # Instagram, Facebook, LinkedIn, Twitter, YouTube, TikTok
        presence_score = (platforms_count / max_platforms) * 100
        
        # Analizza metriche disponibili
        total_followers = 0
        engagement_rates = []
        
        for platform, metrics in social_analysis.get("social_metrics", {}).items():
            # Converti follower in numero
            followers_str = metrics.get("followers", "0")
            if followers_str != "N/A":
                followers_num = self._convert_social_number(followers_str)
                total_followers += followers_num
            
            # Raccogli engagement rates
            engagement_str = metrics.get("engagement_rate", "0%")
            if engagement_str != "N/A" and "%" in engagement_str:
                try:
                    rate = float(engagement_str.replace("%", ""))
                    engagement_rates.append(rate)
                except:
                    pass
        
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        return {
            "platforms_active": platforms_count,
            "presence_score": round(presence_score, 1),
            "total_followers_estimate": total_followers,
            "avg_engagement_rate": round(avg_engagement, 2),
            "social_maturity": "Alto" if platforms_count >= 4 else "Medio" if platforms_count >= 2 else "Basso"
        }
    
    def _convert_social_number(self, number_str: str) -> int:
        """Converte numeri social (es. 1.2K) in integer"""
        if not number_str or number_str == "N/A":
            return 0
        
        number_str = str(number_str).upper().replace(",", "")
        
        try:
            if "K" in number_str:
                return int(float(number_str.replace("K", "")) * 1000)
            elif "M" in number_str:
                return int(float(number_str.replace("M", "")) * 1000000)
            else:
                return int(float(number_str))
        except:
            return 0

class ComprehensiveReportGenerator:
    """Generatore di report completo in stile Venezianico"""
    
    def __init__(self, openai_analyzer: OpenAIAnalyzer = None):
        self.openai_analyzer = openai_analyzer
    
    def generate_complete_report(self, company_data: Dict[str, Any], 
                               all_analysis_data: Dict[str, Any]) -> str:
        """Genera il report completo strutturato"""
        
        company_name = company_data.get("company_name", "Azienda")
        analysis_date = datetime.now().strftime("%d/%m/%Y")
        
        # Estrae dati dalle varie analisi
        company_research = all_analysis_data.get("company_research", {})
        seo_analysis = all_analysis_data.get("seo_analysis", {})
        competitors_data = all_analysis_data.get("competitors_analysis", [])
        social_analysis = all_analysis_data.get("social_analysis", {})
        market_trends = all_analysis_data.get("market_trends", {})
        
        # Usa OpenAI per analisi avanzate se disponibile
        ai_insights = {}
        if self.openai_analyzer:
            ai_insights = {
                "company_profile": self.openai_analyzer.analyze_company_profile(
                    company_data, company_research
                ),
                "financial_analysis": self.openai_analyzer.analyze_financial_data(
                    company_name, company_research
                ),
                "products_services": self.openai_analyzer.analyze_products_services(
                    company_name, company_research
                ),
                "market_positioning": self.openai_analyzer.analyze_market_positioning(
                    company_name, competitors_data, company_research
                ),
                "swot_analysis": self.openai_analyzer.generate_swot_analysis(
                    company_data, all_analysis_data
                ),
                "strategic_recommendations": self.openai_analyzer.generate_strategic_recommendations(
                    all_analysis_data
                )
            }
        
        # Genera il report
        report = self._build_report_sections(
            company_name, analysis_date, company_data, 
            all_analysis_data, ai_insights
        )
        
        return report
    
    def _build_report_sections(self, company_name: str, analysis_date: str,
                             company_data: Dict[str, Any], all_analysis_data: Dict[str, Any],
                             ai_insights: Dict[str, Any]) -> str:
        """Costruisce tutte le sezioni del report"""
        
        report = f"""# REPORT ANALISI MARKETING COMPLETA
## {company_name}

**Data Analisi:** {analysis_date}
**Generato da:** Marketing Analyzer Pro

---

"""
        
        # 1. PROFILO AZIENDALE
        report += self._section_company_profile(company_data, ai_insights.get("company_profile", {}))
        
        # 2. ANALISI FINANZIARIA
        report += self._section_financial_analysis(ai_insights.get("financial_analysis", {}))
        
        # 3. PRODOTTI E SERVIZI
        report += self._section_products_services(ai_insights.get("products_services", {}))
        
        # 4. PRESENZA DIGITALE E SOCIAL MEDIA
        report += self._section_digital_presence(all_analysis_data)
        
        # 5. MERCATO E POSIZIONAMENTO
        report += self._section_market_positioning(ai_insights.get("market_positioning", {}), all_analysis_data)
        
        # 6. ANALISI COMPETITOR
        report += self._section_competitor_analysis(all_analysis_data.get("competitors_analysis", []))
        
        # 7. ANALISI SWOT
        report += self._section_swot_analysis(ai_insights.get("swot_analysis", {}))
        
        # 8. RACCOMANDAZIONI STRATEGICHE
        report += self._section_strategic_recommendations(ai_insights.get("strategic_recommendations", {}))
        
        # 9. CONCLUSIONI
        report += self._section_conclusions(company_name, all_analysis_data)
        
        return report
    
    def _section_company_profile(self, company_data: Dict[str, Any], ai_profile: Dict[str, Any]) -> str:
        """Sezione 1: Profilo Aziendale"""
        
        section = """
## 1. PROFILO AZIENDALE

"""
        
        # Informazioni base
        section += f"**Nome Azienda:** {ai_profile.get('nome_azienda', company_data.get('company_name', 'N/A'))}\n"
        
        if ai_profile.get('piva') and ai_profile['piva'] != "N/A":
            section += f"**P.IVA:** {ai_profile['piva']}\n"
        elif company_data.get('vat_number'):
            section += f"**P.IVA:** {company_data['vat_number']}\n"
        
        if ai_profile.get('sede_legale') and ai_profile['sede_legale'] != "N/A":
            section += f"**Sede Legale:** {ai_profile['sede_legale']}\n"
        
        if ai_profile.get('anno_fondazione') and ai_profile['anno_fondazione'] != "N/A":
            section += f"**Anno di Fondazione:** {ai_profile['anno_fondazione']}\n"
        
        if ai_profile.get('settore') and ai_profile['settore'] != "N/A":
            section += f"**Settore:** {ai_profile['settore']}\n"
        
        if ai_profile.get('ateco') and ai_profile['ateco'] != "N/A":
            section += f"**Codice ATECO:** {ai_profile['ateco']}\n"
        
        # Fondatori
        fondatori = ai_profile.get('fondatori', [])
        if fondatori and fondatori != ["N/A"]:
            section += f"**Fondatori:** {', '.join(fondatori)}\n"
        
        # Struttura societaria
        struttura = ai_profile.get('struttura_societaria', {})
        if struttura and struttura.get('descrizione') != "N/A":
            section += f"\n### Struttura Societaria\n{struttura.get('descrizione', 'N/A')}\n"
        
        # Missione aziendale
        missione = ai_profile.get('missione_aziendale', "")
        if missione and missione != "N/A":
            section += f"\n### Missione Aziendale\n{missione}\n"
        
        return section
    
    def _section_financial_analysis(self, financial_data: Dict[str, Any]) -> str:
        """Sezione 2: Analisi Finanziaria"""
        
        section = """
## 2. ANALISI FINANZIARIA

"""
        
        # Evoluzione fatturato
        evoluzione = financial_data.get('evoluzione_fatturato', {})
        if evoluzione:
            section += "### Evoluzione del Fatturato\n"
            
            for anno in sorted(evoluzione.keys(), reverse=True):
                data = evoluzione[anno]
                if isinstance(data, dict):
                    valore = data.get('valore', 'N/A')
                    crescita = data.get('crescita_percentuale', 'N/A')
                    if crescita != 'N/A':
                        section += f"**{anno}:** {valore} ({crescita} rispetto all'anno precedente)\n"
                    else:
                        section += f"**{anno}:** {valore}\n"
        
        # Altri indicatori finanziari
        section += "\n### Altri Indicatori Finanziari\n"
        
        indicatori = [
            ('patrimonio_netto', 'Patrimonio Netto'),
            ('capitale_sociale', 'Capitale Sociale'),
            ('totale_attivo', 'Totale Attivo'),
            ('costo_personale', 'Costo del Personale'),
            ('numero_dipendenti', 'Dipendenti'),
            ('stipendio_medio', 'Stipendio Medio Lordo')
        ]
        
        for key, label in indicatori:
            valore = financial_data.get(key, 'N/A')
            if valore and valore != 'N/A':
                section += f"**{label}:** {valore}\n"
        
        # Trend di crescita
        trend = financial_data.get('trend_crescita', '')
        if trend and trend != 'N/A':
            section += f"\n### Trend di Crescita\n{trend}\n"
        
        return section
    
    def _section_products_services(self, products_data: Dict[str, Any]) -> str:
        """Sezione 3: Prodotti e Servizi"""
        
        section = """
## 3. PRODOTTI E SERVIZI

"""
        
        # Prodotti principali
        prodotti = products_data.get('prodotti_principali', [])
        if prodotti and prodotti != ['N/A']:
            section += "### Prodotti Principali\n"
            for prodotto in prodotti:
                section += f"- {prodotto}\n"
        
        # Caratteristiche distintive
        caratteristiche = products_data.get('caratteristiche_distintive', [])
        if caratteristiche and caratteristiche != ['N/A']:
            section += "\n### Caratteristiche Distintive\n"
            for caratteristica in caratteristiche:
                section += f"- {caratteristica}\n"
        
        # Altri servizi
        servizi = products_data.get('altri_servizi', [])
        if servizi and servizi != ['N/A']:
            section += "\n### Altri Servizi\n"
            for servizio in servizi:
                section += f"- {servizio}\n"
        
        # Linee di prodotto
        linee = products_data.get('linee_prodotto', {})
        if linee:
            section += "\n### Linee di Prodotto\n"
            for linea_key, linea_data in linee.items():
                if isinstance(linea_data, dict):
                    nome = linea_data.get('nome', 'N/A')
                    descrizione = linea_data.get('descrizione', 'N/A')
                    if nome != 'N/A':
                        section += f"**{nome}:** {descrizione}\n"
        
        return section
    
    def _section_digital_presence(self, all_analysis_data: Dict[str, Any]) -> str:
        """Sezione 4: Presenza Digitale e Social Media"""
        
        section = """
## 4. PRESENZA DIGITALE E SOCIAL MEDIA

"""
        
        # Sito web
        company_data = all_analysis_data.get("company_info", {})
        if company_data.get("website"):
            section += f"### Sito Web\n"
            section += f"**URL Principale:** {company_data['website']}\n"
            
            # Versioni del sito (se disponibili)
            domain = company_data.get("domain", "")
            if domain:
                section += f"**Dominio:** {domain}\n"
        
        # Performance SEO
        seo_data = all_analysis_data.get("seo_analysis", {})
        if seo_data and "error" not in seo_data:
            section += "\n### Performance SEO\n"
            
            overview = seo_data.get("overview", {})
            if overview and "error" not in overview:
                section += f"**Keyword organiche:** {overview.get('organic_keywords', 0):,} posizionamenti\n"
                section += f"**Traffico organico stimato:** {overview.get('organic_traffic', 0):,} visite\n"
                section += f"**Valore stimato del traffico organico:** €{overview.get('organic_cost', 0):,.0f}\n"
            
            backlinks = seo_data.get("backlinks", {})
            if backlinks and "error" not in backlinks:
                section += f"**Backlink:** {backlinks.get('total_backlinks', 0):,}\n"
                section += f"**Domini referenti:** {backlinks.get('referring_domains', 0):,}\n"
                section += f"**Authority Score:** {backlinks.get('authority_score', 0)}\n"
        
        # Presenza sui Social Media
        social_data = all_analysis_data.get("social_analysis", {})
        if social_data:
            section += "\n### Presenza sui Social Media\n"
            
            platforms_found = social_data.get("platforms_found", {})
            social_metrics = social_data.get("social_metrics", {})
            
            for platform, platform_data in platforms_found.items():
                section += f"\n**{platform.title()}** ({platform_data.get('url', 'N/A')})\n"
                
                metrics = social_metrics.get(platform, {})
                if metrics:
                    for metric_key, metric_value in metrics.items():
                        if metric_value != "N/A":
                            metric_label = metric_key.replace("_", " ").title()
                            section += f"- {metric_label}: {metric_value}\n"
            
            # Engagement analysis
            engagement = social_data.get("engagement_analysis", {})
            if engagement:
                section += f"\n### Analisi Engagement Complessiva\n"
                section += f"**Piattaforme attive:** {engagement.get('platforms_active', 0)}\n"
                section += f"**Score di presenza:** {engagement.get('presence_score', 0)}%\n"
                section += f"**Follower totali stimati:** {engagement.get('total_followers_estimate', 0):,}\n"
                section += f"**Engagement rate medio:** {engagement.get('avg_engagement_rate', 0)}%\n"
                section += f"**Maturità social:** {engagement.get('social_maturity', 'N/A')}\n"
        
        return section
    
    def _section_market_positioning(self, positioning_data: Dict[str, Any], all_analysis_data: Dict[str, Any]) -> str:
        """Sezione 5: Mercato e Posizionamento"""
        
        section = """
## 5. MERCATO E POSIZIONAMENTO

"""
        
        # Mercato di riferimento
        mercato = positioning_data.get('mercato_riferimento', 'N/A')
        if mercato != 'N/A':
            section += f"### Mercato di Riferimento\n{mercato}\n"
        
        # Territorio geografico
        territorio = positioning_data.get('territorio_geografico', 'N/A')
        if territorio != 'N/A':
            section += f"\n### Territorio Geografico\n{territorio}\n"
        
        # Concorrenti diretti
        concorrenti = positioning_data.get('concorrenti_diretti', [])
        if concorrenti and concorrenti != ['N/A']:
            section += f"\n### Concorrenti Diretti\n"
            for concorrente in concorrenti:
                section += f"- {concorrente}\n"
        
        # Trend di mercato
        trend_mercato = positioning_data.get('trend_mercato', [])
        if trend_mercato and trend_mercato != ['N/A']:
            section += f"\n### Trend di Mercato\n"
            for trend in trend_mercato:
                section += f"- {trend}\n"
        
        # Quota di mercato
        quota = positioning_data.get('quota_mercato_stimata', 'N/A')
        if quota != 'N/A':
            section += f"\n### Quota di Mercato Stimata\n{quota}\n"
        
        # Posizionamento
        posizionamento = positioning_data.get('posizionamento', 'N/A')
        if posizionamento != 'N/A':
            section += f"\n### Posizionamento Competitivo\n{posizionamento}\n"
        
        return section
    
    def _section_competitor_analysis(self, competitors_data: List[Dict[str, Any]]) -> str:
        """Sezione 6: Analisi Competitor"""
        
        section = """
## 6. ANALISI COMPETITOR

"""
        
        if not competitors_data:
            section += "Nessun competitor identificato nell'analisi.\n"
            return section
        
        section += f"### Competitor Identificati ({len(competitors_data)})\n\n"
        
        for i, competitor in enumerate(competitors_data[:5], 1):  # Top 5 competitor
            comp_name = competitor.get("name", "N/A")
            section += f"#### {i}. {comp_name}\n"
            
            # Informazioni base
            section += f"**Dominio:** {competitor.get('domain', 'N/A')}\n"
            section += f"**URL:** {competitor.get('url', 'N/import streamlit as st
import requests
import json
import re
from typing import Dict, Any, Tuple, List, Optional
from urllib.parse import urlparse
from datetime import datetime
import logging
from dataclasses import dataclass
import time

# Configurazione pagina
st.set_page_config(
    page_title="Marketing Analyzer Pro",
    page_icon="📊",
    layout="wide"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configurazione API Keys"""
    openai_api_key: str = ""
    semrush_api_key: str = ""
    serper_api_key: str = ""

class InputValidator:
    """Validatore input avanzato"""
    
    @staticmethod
    def validate_company_input(input_text: str) -> Tuple[bool, str, Dict[str, Any]]:
        if not input_text or not input_text.strip():
            return False, "empty", {}
        
        input_text = input_text.strip()
        
        if InputValidator.is_url(input_text):
            domain = InputValidator.extract_domain(input_text)
            company_name = InputValidator.domain_to_company_name(domain)
            return True, "url", {
                "website": input_text,
                "domain": domain,
                "company_name": company_name
            }
        
        if InputValidator.is_italian_vat(input_text):
            return True, "vat", {
                "vat_number": input_text,
                "company_name": f"Azienda P.IVA {input_text}"
            }
        
        if len(input_text) >= 2:
            return True, "name", {
                "company_name": input_text
            }
        
        return False, "invalid", {}
    
    @staticmethod
    def is_url(text: str) -> bool:
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_italian_vat(text: str) -> bool:
        clean_text = re.sub(r'[^\d]', '', text.upper().replace('IT', ''))
        if len(clean_text) == 11 and clean_text.isdigit():
            return InputValidator._validate_italian_vat_checksum(clean_text)
        return False
    
    @staticmethod
    def _validate_italian_vat_checksum(vat: str) -> bool:
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
        if not domain:
            return ""
        
        extensions = ['.com', '.it', '.org', '.net', '.eu', '.co.uk']
        company_name = domain
        
        for ext in extensions:
            if company_name.endswith(ext):
                company_name = company_name[:-len(ext)]
                break
        
        return company_name.capitalize()

class OpenAIAnalyzer:
    """Analyzer che usa OpenAI per analisi avanzate"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_company_profile(self, company_data: Dict[str, Any], 
                              search_results: Dict[str, Any],
                              company_registry_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analizza e struttura il profilo aziendale"""
        
        # Prepara il contesto per l'AI
        context = f"""
        Dati azienda: {json.dumps(company_data, ensure_ascii=False)}
        Risultati ricerca: {json.dumps(search_results, ensure_ascii=False)}
        """
        
        if company_registry_data:
            context += f"\nDati registro imprese: {json.dumps(company_registry_data, ensure_ascii=False)}"
        
        prompt = f"""
        Analizza i seguenti dati aziendali e crea un profilo aziendale strutturato.
        
        {context}
        
        Genera un JSON con le seguenti informazioni (usa "N/A" se non disponibile):
        {{
            "nome_azienda": "nome completo",
            "piva": "partita IVA",
            "sede_legale": "indirizzo completo",
            "anno_fondazione": "anno",
            "fondatori": ["lista fondatori"],
            "settore": "settore di attività",
            "ateco": "codice ATECO se disponibile",
            "struttura_societaria": {{"descrizione": "tipo di società"}},
            "missione_aziendale": "descrizione della missione"
        }}
        
        Estrai le informazioni disponibili e inferisci quelle mancanti dal contesto.
        """
        
        return self._query_openai(prompt)
    
    def analyze_financial_data(self, company_name: str, 
                             search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i dati finanziari dell'azienda"""
        
        context = f"""
        Azienda: {company_name}
        Risultati ricerca: {json.dumps(search_results, ensure_ascii=False)}
        """
        
        prompt = f"""
        Analizza i seguenti dati per estrarre informazioni finanziarie sull'azienda.
        
        {context}
        
        Genera un JSON con le seguenti informazioni finanziarie:
        {{
            "evoluzione_fatturato": {{
                "2023": {{"valore": "€X", "crescita_percentuale": "X%"}},
                "2022": {{"valore": "€X", "crescita_percentuale": "X%"}},
                "2021": {{"valore": "€X", "crescita_percentuale": "X%"}}
            }},
            "patrimonio_netto": "€X",
            "capitale_sociale": "€X",
            "totale_attivo": "€X",
            "costo_personale": "€X",
            "numero_dipendenti": "X",
            "stipendio_medio": "€X",
            "trend_crescita": "descrizione del trend di crescita"
        }}
        
        Se i dati non sono disponibili, usa "N/A" e cerca di fare stime realistiche basate sul settore.
        """
        
        return self._query_openai(prompt)
    
    def analyze_products_services(self, company_name: str,
                                search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza prodotti e servizi dell'azienda"""
        
        context = f"""
        Azienda: {company_name}
        Risultati ricerca: {json.dumps(search_results, ensure_ascii=False)}
        """
        
        prompt = f"""
        Analizza i seguenti dati per identificare prodotti e servizi dell'azienda.
        
        {context}
        
        Genera un JSON con:
        {{
            "prodotti_principali": ["lista dei prodotti principali"],
            "caratteristiche_distintive": ["lista delle caratteristiche distintive"],
            "altri_servizi": ["altri servizi offerti"],
            "linee_prodotto": {{
                "linea1": {{"nome": "X", "descrizione": "Y"}},
                "linea2": {{"nome": "X", "descrizione": "Y"}}
            }}
        }}
        """
        
        return self._query_openai(prompt)
    
    def analyze_market_positioning(self, company_name: str,
                                 competitors: List[Dict[str, Any]],
                                 search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza posizionamento di mercato e competitor"""
        
        context = f"""
        Azienda: {company_name}
        Competitor: {json.dumps(competitors, ensure_ascii=False)}
        Risultati ricerca: {json.dumps(search_results, ensure_ascii=False)}
        """
        
        prompt = f"""
        Analizza il posizionamento di mercato dell'azienda rispetto ai competitor.
        
        {context}
        
        Genera un JSON con:
        {{
            "mercato_riferimento": "descrizione del mercato",
            "territorio_geografico": "area geografica di operatività",
            "concorrenti_diretti": ["lista dei 3-5 principali competitor"],
            "trend_mercato": ["trend principali del settore"],
            "quota_mercato_stimata": "stima della quota di mercato",
            "posizionamento": "descrizione del posizionamento competitivo"
        }}
        """
        
        return self._query_openai(prompt)
    
    def generate_swot_analysis(self, company_data: Dict[str, Any],
                             all_analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera analisi SWOT"""
        
        context = f"""
        Dati completi azienda: {json.dumps(all_analysis_data, ensure_ascii=False)}
        """
        
        prompt = f"""
        Basandoti sui dati raccolti, genera un'analisi SWOT completa per l'azienda.
        
        {context}
        
        Genera un JSON con:
        {{
            "punti_forza": ["lista di 4-6 punti di forza"],
            "punti_debolezza": ["lista di 4-6 punti di debolezza"],
            "opportunita": ["lista di 4-6 opportunità"],
            "minacce": ["lista di 4-6 minacce"],
            "proposizione_valore": "descrizione della proposizione di valore unica"
        }}
        """
        
        return self._query_openai(prompt)
    
    def generate_strategic_recommendations(self, all_analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera raccomandazioni strategiche"""
        
        context = f"""
        Analisi completa: {json.dumps(all_analysis_data, ensure_ascii=False)}
        """
        
        prompt = f"""
        Basandoti sull'analisi completa, genera raccomandazioni strategiche dettagliate.
        
        {context}
        
        Genera un JSON con:
        {{
            "sviluppo_prodotto": ["raccomandazioni per lo sviluppo prodotto"],
            "marketing_comunicazione": ["strategie di marketing e comunicazione"],
            "espansione_commerciale": ["strategie di espansione"],
            "struttura_organizzativa": ["miglioramenti organizzativi"],
            "innovazione_digitale": ["iniziative di innovazione digitale"],
            "priorita_immediate": ["azioni da intraprendere subito"],
            "obiettivi_medio_termine": ["obiettivi a 6-12 mesi"],
            "visione_lungo_termine": ["visione strategica a 2-3 anni"]
        }}
        """
        
        return self._query_openai(prompt)
    
    def _query_openai(self, prompt: str) -> Dict[str, Any]:
        """Effettua query a OpenAI"""
        try:
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Sei un consulente di business strategy esperto in analisi aziendali. Rispondi sempre in JSON valido e in italiano."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Prova a parsare come JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Se non è JSON valido, restituisci come testo
                    return {"analysis": content}
            else:
                return {"error": f"OpenAI API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Errore OpenAI: {str(e)}"}

class AdvancedSerperAgent:
    """Agente Serper con funzionalità avanzate"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def deep_company_research(self, company_name: str, domain: str = None) -> Dict[str, Any]:
        """Ricerca approfondita dell'azienda"""
        
        all_results = {
            "company_info": {},
            "financial_data": {},
            "news_mentions": {},
            "business_info": {}
        }
        
        # Query specifiche per diversi tipi di informazioni
        queries = [
            f"{company_name} azienda informazioni sede fatturato",
            f"{company_name} bilancio finanziario dipendenti",
            f"{company_name} prodotti servizi business",
            f"{company_name} storia fondazione chi è",
            f'"{company_name}" partita iva registro imprese'
        ]
        
        for i, query in enumerate(queries):
            try:
                results = self._search(query)
                
                if i == 0:
                    all_results["company_info"] = results
                elif i == 1:
                    all_results["financial_data"] = results
                elif i == 2:
                    all_results["business_info"] = results
                else:
                    # Aggiungi agli altri risultati
                    if "additional_searches" not in all_results:
                        all_results["additional_searches"] = []
                    all_results["additional_searches"].append({
                        "query": query,
                        "results": results
                    })
                
                # Delay per rispettare rate limits
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore ricerca '{query}': {e}")
                continue
        
        return all_results
    
    def research_competitors(self, company_name: str, sector: str = None) -> List[Dict[str, Any]]:
        """Ricerca approfondita dei competitor"""
        
        competitor_queries = [
            f"{company_name} competitor concorrenti settore",
            f"{company_name} alternative simili mercato",
            f"principali aziende {sector}" if sector else f"leader mercato {company_name}"
        ]
        
        all_competitors = []
        seen_domains = set()
        
        for query in competitor_queries:
            try:
                results = self._search(query)
                
                if "organic" in results:
                    for result in results["organic"][:5]:
                        domain = self._extract_domain(result.get("link", ""))
                        
                        if domain and domain not in seen_domains:
                            seen_domains.add(domain)
                            
                            competitor = {
                                "name": result.get("title", "").split(" - ")[0],
                                "domain": domain,
                                "url": result.get("link", ""),
                                "description": result.get("snippet", ""),
                                "found_via": query
                            }
                            
                            all_competitors.append(competitor)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore ricerca competitor '{query}': {e}")
                continue
        
        return all_competitors[:10]  # Limita ai primi 10
    
    def analyze_competitor_details(self, competitor: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza dettagli specifici di un competitor"""
        
        comp_name = competitor.get("name", "")
        if not comp_name:
            return {"error": "Nome competitor non disponibile"}
        
        # Query specifiche per il competitor
        queries = [
            f"{comp_name} fatturato dipendenti azienda",
            f"{comp_name} prodotti servizi business",
            f"{comp_name} sede sociale partita iva"
        ]
        
        competitor_analysis = {
            "basic_info": competitor,
            "detailed_research": {}
        }
        
        for i, query in enumerate(queries):
            try:
                results = self._search(query)
                
                key = f"search_{i+1}"
                competitor_analysis["detailed_research"][key] = {
                    "query": query,
                    "results": results
                }
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore analisi competitor '{query}': {e}")
                continue
        
        return competitor_analysis
    
    def research_market_trends(self, sector: str, company_name: str) -> Dict[str, Any]:
        """Ricerca trend di mercato del settore"""
        
        trend_queries = [
            f"trend mercato {sector} 2024 Italia",
            f"analisi settore {sector} crescita",
            f"mercato {sector} dimensioni previsioni",
            f"innovazioni {sector} tecnologie emergenti"
        ]
        
        market_analysis = {
            "sector": sector,
            "trend_research": {}
        }
        
        for i, query in enumerate(trend_queries):
            try:
                results = self._search(query)
                
                key = f"trend_{i+1}"
                market_analysis["trend_research"][key] = {
                    "query": query,
                    "results": results
                }
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore ricerca trend '{query}': {e}")
                continue
        
        return market_analysis
    
    def _search(self, query: str) -> Dict[str, Any]:
        """Effettua ricerca con Serper"""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "gl": "it",
                "hl": "it",
                "num": 10
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            return {"error": f"Errore ricerca: {str(e)}"}
    
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

class AdvancedSEMRushAgent:
    """Agente SEMRush con analisi dettagliate"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.semrush.com/"
    
    def comprehensive_seo_analysis(self, domain: str) -> Dict[str, Any]:
        """Analisi SEO completa"""
        
        if not domain:
            return {"error": "Dominio non fornito"}
        
        analysis = {
            "domain": domain,
            "overview": {},
            "keywords": {},
            "backlinks": {},
            "competitors": {},
            "traffic_analytics": {}
        }
        
        try:
            # Domain overview
            analysis["overview"] = self._get_domain_overview(domain)
            time.sleep(1)
            
            # Keywords analysis
            analysis["keywords"] = self._get_keywords_analysis(domain)
            time.sleep(1)
            
            # Backlinks analysis
            analysis["backlinks"] = self._get_backlinks_analysis(domain)
            time.sleep(1)
            
            # Competitors
            analysis["competitors"] = self._get_competitors_analysis(domain)
            time.sleep(1)
            
            # Traffic analytics
            analysis["traffic_analytics"] = self._get_traffic_analytics(domain)
            
        except Exception as e:
            analysis["error"] = f"Errore analisi SEO: {str(e)}"
        
        return analysis
    
    def analyze_competitor_seo(self, competitor_domain: str) -> Dict[str, Any]:
        """Analizza SEO di un competitor"""
        
        return {
            "domain": competitor_domain,
            "overview": self._get_domain_overview(competitor_domain),
            "top_keywords": self._get_top_keywords(competitor_domain),
            "traffic_estimate": self._get_traffic_estimate(competitor_domain)
        }
    
    def _get_domain_overview(self, domain: str) -> Dict[str, Any]:
        """Overview completa del dominio"""
        params = {
            "type": "domain_overview",
            "key": self.api_key,
            "domain": domain,
            "database": "it",
            "export_format": "json"
        }
        
        try:
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
                    "adwords_cost": item.get("Ac", 0),
                    "organic_budget": item.get("Ob", 0),
                    "paid_budget": item.get("Ab", 0)
                }
            
            return {"error": "Nessun dato overview disponibile"}
            
        except Exception as e:
            return {"error": f"Errore overview: {str(e)}"}
    
    def _get_keywords_analysis(self, domain: str) -> Dict[str, Any]:
        """Analisi dettagliata delle keywords"""
        params = {
            "type": "domain_organic",
            "key": self.api_key,
            "domain": domain,
            "database": "it",
            "export_format": "json",
            "display_limit": 50
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                keywords = []
                position_distribution = {
                    "1-3": 0,
                    "4-10": 0,
                    "11-20": 0,
                    "21-50": 0,
                    "51+": 0
                }
                
                total_volume = 0
                total_traffic_cost = 0
                
                for item in data:
                    if isinstance(item, dict):
                        pos = item.get("Po", 0)
                        volume = item.get("Nq", 0)
                        cpc = item.get("Cp", 0)
                        
                        keywords.append({
                            "keyword": item.get("Ph", ""),
                            "position": pos,
                            "volume": volume,
                            "cpc": cpc,
                            "url": item.get("Ur", ""),
                            "traffic_percent": item.get("Tr", 0)
                        })
                        
                        # Distribuzione posizioni
                        if 1 <= pos <= 3:
                            position_distribution["1-3"] += 1
                        elif 4 <= pos <= 10:
                            position_distribution["4-10"] += 1
                        elif 11 <= pos <= 20:
                            position_distribution["11-20"] += 1
                        elif 21 <= pos <= 50:
                            position_distribution["21-50"] += 1
                        else:
                            position_distribution["51+"] += 1
                        
                        total_volume += volume
                        total_traffic_cost += (volume * cpc)
                
                return {
                    "total_keywords": len(keywords),
                    "position_distribution": position_distribution,
                    "top_keywords": keywords[:20],
                    "total_search_volume": total_volume,
                    "estimated_traffic_value": total_traffic_cost,
                    "avg_position": sum([k["position"] for k in keywords]) / len(keywords) if keywords else 0
                }
            
            return {"error": "Nessuna keyword trovata"}
            
        except Exception as e:
            return {"error": f"Errore keywords: {str(e)}"}
    
    def _get_backlinks_analysis(self, domain: str) -> Dict[str, Any]:
        """Analisi backlinks"""
        # Per backlinks usiamo l'endpoint overview
        params = {
            "type": "backlinks_overview",
            "key": self.api_key,
            "target": domain,
            "target_type": "root_domain",
            "export_format": "json"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict):
                return {
                    "total_backlinks": data.get("backlinks_num", 0),
                    "referring_domains": data.get("domains_num", 0),
                    "referring_ips": data.get("ips_num", 0),
                    "authority_score": data.get("ascore", 0),
                    "follow_backlinks": data.get("follows_num", 0),
                    "nofollow_backlinks": data.get("nofollows_num", 0)
                }
            
            return {"error": "Nessun dato backlinks disponibile"}
            
        except Exception as e:
            return {"error": f"Errore backlinks: {str(e)}"}
    
    def _get_competitors_analysis(self, domain: str) -> Dict[str, Any]:
        """Analisi competitor SEO"""
        params = {
            "type": "domain_organic_organic",
            "key": self.api_key,
            "domain": domain,
            "database": "it",
            "export_format": "json",
            "display_limit": 20
        }
        
        try:
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
                            "competition_level": item.get("Cl", 0),
                            "organic_budget": item.get("Ob", 0)
                        })
            
            return {
                "seo_competitors": competitors,
                "total_competitors": len(competitors)
            }
            
        except Exception as e:
            return {"error": f"Errore competitor: {str(e)}"}
    
    def _get_traffic_analytics(self, domain: str) -> Dict[str, Any]:
        """Analytics del traffico"""
        # Placeholder per analytics avanzate
        return {
            "note": "Traffic analytics richiedono dati aggiuntivi",
            "available_metrics": ["organic_traffic", "paid_traffic", "referral_traffic"]
        }
    
    def _get_top_keywords(self, domain: str) -> List[Dict[str, Any]]:
        """Top keywords per competitor"""
        params = {
            "type": "domain_organic",
            "key": self.api_key,
            "domain": domain,
            "database": "it",
            "export_format": "json",
            "display_limit": 10
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            keywords = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        keywords.append({
                            "keyword": item.get("Ph", ""),
                            "position": item.get("Po", 0),
                            "volume": item.get("Nq", 0),
                            "cpc": item.get("Cp", 0)
                        })
            
            return keywords
            
        except Exception as e:
            return [{"error": f"Errore top keywords: {str(e)}"}]
    
    def _get_traffic_estimate(self, domain: str) -> Dict[str, Any]:
        """Stima del traffico"""
        # Usa i dati dell'overview per stimare il traffico
        overview = self._get_domain_overview(domain)
        
        if "error" not in overview:
            return {
                "monthly_organic_traffic": overview.get("organic_traffic", 0),
                "traffic_value": overview.get("organic_cost", 0),
                "pai
