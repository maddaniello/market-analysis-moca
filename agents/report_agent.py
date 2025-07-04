from typing import Dict, Any, List
import json
import datetime
from .base_agent import BaseAgent

class ReportAgent(BaseAgent):
    """Agente per generare report completi di analisi marketing"""
    
    def __init__(self, api_config, app_config):
        super().__init__(api_config, app_config)
        
    def analyze(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera il report finale consolidando tutti i dati"""
        self.log_progress("Generando report completo...")
        
        # Estrae dati da ogni agente
        company_data = all_data.get("company_info", {})
        semrush_data = all_data.get("semrush_analysis", {})
        serper_data = all_data.get("serper_analysis", {})
        social_data = all_data.get("social_analysis", {})
        company_details = all_data.get("company_analysis", {})
        
        # Genera le sezioni del report
        report = {
            "metadata": self._generate_metadata(company_data),
            "executive_summary": self._generate_executive_summary(all_data),
            "company_profile": self._generate_company_profile(company_data, company_details),
            "digital_presence": self._generate_digital_presence_analysis(semrush_data, social_data),
            "competitor_analysis": self._generate_competitor_analysis(serper_data, semrush_data, social_data),
            "market_position": self._generate_market_position(all_data),
            "opportunities": self._generate_opportunities(all_data),
            "recommendations": self._generate_recommendations(all_data),
            "action_plan": self._generate_action_plan(all_data),
            "appendix": self._generate_appendix(all_data)
        }
        
        # Genera report formattato
        formatted_report = self._format_report(report)
        
        return {
            "structured_report": report,
            "formatted_report": formatted_report,
            "summary_metrics": self._extract_key_metrics(all_data),
            "report_generated_at": datetime.datetime.now().isoformat()
        }
    
    def _generate_metadata(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera metadati del report"""
        return {
            "report_title": f"Analisi Marketing Digitale - {company_data.get('company_name', 'Azienda')}",
            "company_name": company_data.get("company_name", ""),
            "analysis_date": datetime.datetime.now().strftime("%d/%m/%Y"),
            "report_version": "1.0",
            "analysis_scope": [
                "Analisi SEO e traffico organico",
                "Analisi competitor",
                "Presenza social media",
                "Dati aziendali",
                "Posizionamento di mercato"
            ]
        }
    
    def _generate_executive_summary(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera executive summary"""
        
        # Usa AI per creare un summary intelligente
        summary_prompt = f"""
        Crea un executive summary per un'analisi di marketing digitale basata sui seguenti dati:
        
        Dati azienda: {json.dumps(all_data.get('company_info', {}), ensure_ascii=False)}
        Dati SEMRush: {json.dumps(all_data.get('semrush_analysis', {}), ensure_ascii=False)}
        Dati Social: {json.dumps(all_data.get('social_analysis', {}), ensure_ascii=False)}
        
        L'executive summary deve includere:
        1. Situazione attuale dell'azienda nel digitale
        2. Principali punti di forza
        3. Principali aree di miglioramento
        4. 3 raccomandazioni prioritarie
        
        Mantieni un tono professionale e focus sui risultati concreti.
        """
        
        system_prompt = """
        Sei un consulente di marketing digitale esperto. Crea executive summary concisi 
        e orientati all'azione per dirigenti aziendali. Focus su metriche chiave e 
        raccomandazioni implementabili.
        """
        
        ai_summary = self.query_openai(summary_prompt, system_prompt)
        
        # Estrae metriche chiave
        key_metrics = self._extract_key_metrics(all_data)
        
        return {
            "ai_generated_summary": ai_summary,
            "key_metrics": key_metrics,
            "critical_findings": self._identify_critical_findings(all_data),
            "immediate_actions": self._identify_immediate_actions(all_data)
        }
    
    def _generate_company_profile(self, company_data: Dict[str, Any], 
                                company_details: Dict[str, Any]) -> Dict[str, Any]:
        """Genera profilo completo dell'azienda"""
        
        consolidated_data = company_details.get("consolidated", {})
        
        profile = {
            "basic_info": {
                "company_name": company_data.get("company_name", ""),
                "website": company_data.get("website", ""),
                "vat_number": consolidated_data.get("vat_number", ""),
                "legal_form": consolidated_data.get("legal_form", ""),
                "headquarters": consolidated_data.get("headquarters", ""),
                "sector": consolidated_data.get("sector", "")
            },
            "business_metrics": {
                "employees": consolidated_data.get("employees", ""),
                "revenue": consolidated_data.get("revenue", ""),
                "share_capital": consolidated_data.get("share_capital", ""),
                "founding_date": consolidated_data.get("founding_date", "")
            },
            "contact_info": consolidated_data.get("contact_info", {}),
            "data_confidence": consolidated_data.get("confidence_score", 0),
            "data_sources": consolidated_data.get("data_sources", [])
        }
        
        return profile
    
    def _generate_digital_presence_analysis(self, semrush_data: Dict[str, Any], 
                                          social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza la presenza digitale completa"""
        
        analysis = {
            "seo_performance": {},
            "social_media_presence": {},
            "overall_digital_score": 0,
            "digital_strengths": [],
            "digital_weaknesses": []
        }
        
        # Analisi SEO
        if semrush_data and not semrush_data.get("error"):
            organic_data = semrush_data.get("organic_traffic", {})
            keyword_data = semrush_data.get("keywords", {})
            backlink_data = semrush_data.get("backlinks", {})
            
            analysis["seo_performance"] = {
                "organic_keywords": keyword_data.get("total_keywords", 0),
                "top_positions": keyword_data.get("keywords_1_3", 0),
                "total_backlinks": backlink_data.get("total_backlinks", 0),
                "authority_score": backlink_data.get("authority_score", 0),
                "seo_score": self._calculate_seo_score(semrush_data)
            }
        
        # Analisi Social
        if social_data and not social_data.get("error"):
            social_analytics = social_data.get("social_analytics", {})
            social_comparison = social_data.get("social_comparison", {})
            
            total_followers = 0
            active_platforms = 0
            
            for platform, data in social_analytics.items():
                if not data.get("error"):
                    active_platforms += 1
                    followers = data.get("followers", 0) or data.get("subscribers", 0)
                    total_followers += followers
            
            analysis["social_media_presence"] = {
                "active_platforms": active_platforms,
                "total_followers": total_followers,
                "platform_details": social_analytics,
                "competitive_position": social_comparison.get("platform_comparison", {}),
                "social_score": self._calculate_social_score(social_data)
            }
        
        # Score digitale complessivo
        seo_score = analysis["seo_performance"].get("seo_score", 0)
        social_score = analysis["social_media_presence"].get("social_score", 0)
        analysis["overall_digital_score"] = (seo_score + social_score) / 2
        
        # Identifica punti di forza e debolezza
        analysis["digital_strengths"] = self._identify_digital_strengths(analysis)
        analysis["digital_weaknesses"] = self._identify_digital_weaknesses(analysis)
        
        return analysis
    
    def _generate_competitor_analysis(self, serper_data: Dict[str, Any], 
                                    semrush_data: Dict[str, Any], 
                                    social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera analisi completa dei competitor"""
        
        analysis = {
            "identified_competitors": [],
            "competitive_landscape": {},
            "market_share_analysis": {},
            "competitor_strengths": {},
            "competitive_gaps": [],
            "competitive_opportunities": []
        }
        
        # Competitor da Serper
        serper_competitors = serper_data.get("competitors", {}).get("competitors", [])
        
        # Competitor da SEMRush
        semrush_competitors = semrush_data.get("competitors", [])
        
        # Consolida lista competitor
        all_competitors = {}
        
        # Aggiungi competitor Serper
        for comp in serper_competitors:
            name = comp.get("name", "")
            if name:
                all_competitors[name] = {
                    "name": name,
                    "domain": comp.get("domain", ""),
                    "description": comp.get("description", ""),
                    "source": "serper"
                }
        
        # Aggiungi competitor SEMRush
        for comp in semrush_competitors:
            domain = comp.get("domain", "")
            if domain and domain not in [c.get("domain", "") for c in all_competitors.values()]:
                all_competitors[domain] = {
                    "name": domain,
                    "domain": domain,
                    "common_keywords": comp.get("common_keywords", 0),
                    "se_keywords": comp.get("se_keywords", 0),
                    "competition_level": comp.get("competition_level", 0),
                    "source": "semrush"
                }
        
        analysis["identified_competitors"] = list(all_competitors.values())
        
        # Analisi paesaggio competitivo
        analysis["competitive_landscape"] = self._analyze_competitive_landscape(
            all_competitors, semrush_data, social_data
        )
        
        # Identifica gap e opportunità
        analysis["competitive_gaps"] = self._identify_competitive_gaps(semrush_data, social_data)
        analysis["competitive_opportunities"] = self._identify_competitive_opportunities(all_competitors)
        
        return analysis
    
    def _generate_market_position(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza la posizione di mercato dell'azienda"""
        
        position = {
            "market_category": "",
            "competitive_position": "",
            "market_share_estimate": "",
            "growth_potential": "",
            "market_trends": [],
            "positioning_strengths": [],
            "positioning_challenges": []
        }
        
        # Usa AI per analizzare la posizione di mercato
        market_analysis_prompt = f"""
        Analizza la posizione di mercato di questa azienda basandoti sui seguenti dati:
        
        Dati azienda: {json.dumps(all_data.get('company_analysis', {}), ensure_ascii=False)}
        Competitor: {json.dumps(all_data.get('serper_analysis', {}), ensure_ascii=False)}
        Performance SEO: {json.dumps(all_data.get('semrush_analysis', {}), ensure_ascii=False)}
        
        Determina:
        1. Categoria di mercato (leader, challenger, follower, niche player)
        2. Posizione competitiva relativa
        3. Stima della quota di mercato
        4. Potenziale di crescita
        5. Trend di mercato rilevanti
        6. Punti di forza del posizionamento
        7. Sfide del posizionamento
        
        Rispondi in formato JSON con le chiavi indicate.
        """
        
        system_prompt = """
        Sei un analista di mercato esperto. Analizza la posizione competitiva delle aziende
        basandoti su dati digitali e aziendali. Fornisci valutazioni realistiche e insights actionable.
        """
        
        ai_analysis = self.query_openai(market_analysis_prompt, system_prompt)
        
        try:
            ai_result = json.loads(ai_analysis)
            position.update(ai_result)
        except json.JSONDecodeError:
            position["ai_analysis_raw"] = ai_analysis
        
        return position
    
    def _generate_opportunities(self, all_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica opportunità di crescita"""
        
        opportunities = []
        
        # Opportunità SEO
        semrush_data = all_data.get("semrush_analysis", {})
        if semrush_data and not semrush_data.get("error"):
            keyword_data = semrush_data.get("keywords", {})
            
            # Keyword gap
            if keyword_data.get("keywords_4_10", 0) > 0:
                opportunities.append({
                    "type": "SEO",
                    "category": "Keyword Optimization",
                    "description": f"Ottimizzare {keyword_data.get('keywords_4_10', 0)} keyword posizionate tra 4-10 per raggiungere la prima pagina",
                    "impact": "Alto",
                    "effort": "Medio",
                    "timeline": "3-6 mesi"
                })
            
            # Backlink opportunity
            backlink_data = semrush_data.get("backlinks", {})
            if backlink_data.get("total_backlinks", 0) < 1000:
                opportunities.append({
                    "type": "SEO",
                    "category": "Link Building",
                    "description": "Incrementare il profilo backlink per migliorare l'autorità del dominio",
                    "impact": "Alto",
                    "effort": "Alto",
                    "timeline": "6-12 mesi"
                })
        
        # Opportunità Social
        social_data = all_data.get("social_analysis", {})
        if social_data and not social_data.get("error"):
            social_analytics = social_data.get("social_analytics", {})
            missing_platforms = []
            
            for platform in ["facebook", "instagram", "linkedin", "youtube"]:
                if platform not in social_analytics or social_analytics[platform].get("error"):
                    missing_platforms.append(platform)
            
            if missing_platforms:
                opportunities.append({
                    "type": "Social Media",
                    "category": "Platform Expansion",
                    "description": f"Aprire presenza su: {', '.join(missing_platforms)}",
                    "impact": "Medio",
                    "effort": "Medio",
                    "timeline": "1-3 mesi"
                })
            
            # Engagement opportunities
            for platform, data in social_analytics.items():
                followers = data.get("followers", 0)
                if 0 < followers < 1000:
                    opportunities.append({
                        "type": "Social Media",
                        "category": "Audience Growth",
                        "description": f"Crescita audience su {platform} - attualmente sotto i 1000 follower",
                        "impact": "Medio",
                        "effort": "Medio",
                        "timeline": "3-6 mesi"
                    })
        
        # Opportunità competitive
        competitor_data = all_data.get("serper_analysis", {})
        if competitor_data:
            opportunities.append({
                "type": "Competitive",
                "category": "Market Analysis",
                "description": "Analisi approfondita delle strategie dei competitor per identificare gap di mercato",
                "impact": "Alto",
                "effort": "Basso",
                "timeline": "1 mese"
            })
        
        return opportunities
    
    def _generate_recommendations(self, all_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera raccomandazioni strategiche"""
        
        recommendations = []
        
        # Raccomandazioni SEO
        semrush_data = all_data.get("semrush_analysis", {})
        if semrush_data and not semrush_data.get("error"):
            keyword_data = semrush_data.get("keywords", {})
            
            if keyword_data.get("total_keywords", 0) < 100:
                recommendations.append({
                    "priority": "Alta",
                    "category": "SEO Strategy",
                    "title": "Espandere il portafoglio keyword",
                    "description": "Sviluppare contenuti per aumentare il numero di keyword posizionate",
                    "actions": [
                        "Ricerca keyword approfondita nel settore",
                        "Creazione piano editoriale SEO-oriented",
                        "Ottimizzazione pagine esistenti",
                        "Creazione nuovi contenuti target"
                    ],
                    "expected_results": "Aumento del 200-300% delle keyword posizionate entro 6 mesi",
                    "resources_needed": "Content creator, SEO specialist"
                })
            
            backlink_data = semrush_data.get("backlinks", {})
            if backlink_data.get("authority_score", 0) < 30:
                recommendations.append({
                    "priority": "Alta",
                    "category": "Authority Building",
                    "title": "Strategia di link building",
                    "description": "Aumentare l'autorità del dominio attraverso backlink di qualità",
                    "actions": [
                        "Audit backlink competitor",
                        "Outreach per guest posting",
                        "Partnership con siti di settore",
                        "Creazione contenuti linkabili"
                    ],
                    "expected_results": "Aumento authority score del 50% entro 12 mesi",
                    "resources_needed": "Link building specialist, PR"
                })
        
        # Raccomandazioni Social
        social_data = all_data.get("social_analysis", {})
        if social_data:
            social_comparison = social_data.get("social_comparison", {})
            
            if social_comparison.get("total_platforms", 0) < 3:
                recommendations.append({
                    "priority": "Media",
                    "category": "Social Media Strategy",
                    "title": "Espansione presenza social",
                    "description": "Aumentare la presenza sui principali social network",
                    "actions": [
                        "Analisi audience target per piattaforma",
                        "Creazione profili professionali",
                        "Sviluppo content strategy specifica",
                        "Implementazione calendar editoriale"
                    ],
                    "expected_results": "Presenza attiva su 4-5 piattaforme principali",
                    "resources_needed": "Social media manager, graphic designer"
                })
        
        # Raccomandazioni competitive
        recommendations.append({
            "priority": "Media",
            "category": "Competitive Intelligence",
            "title": "Sistema di monitoraggio competitor",
            "description": "Implementare monitoraggio continuo delle attività competitor",
            "actions": [
                "Setup alert Google per competitor",
                "Monitoraggio social competitor",
                "Analisi mensile posizionamento SEO",
                "Report trimestrale competitive intelligence"
            ],
            "expected_results": "Visibilità completa su mosse competitive",
            "resources_needed": "Marketing analyst, strumenti di monitoring"
        })
        
        return recommendations
    
    def _generate_action_plan(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera piano d'azione con timeline"""
        
        action_plan = {
            "immediate_actions": [],  # 0-30 giorni
            "short_term_actions": [],  # 1-3 mesi
            "medium_term_actions": [],  # 3-6 mesi
            "long_term_actions": [],  # 6+ mesi
            "budget_estimates": {},
            "kpi_targets": {}
        }
        
        # Azioni immediate
        action_plan["immediate_actions"] = [
            {
                "action": "Setup Google Analytics e Search Console",
                "owner": "Marketing Team",
                "deadline": "7 giorni",
                "cost": "Gratuito"
            },
            {
                "action": "Audit completo del sito web",
                "owner": "SEO Specialist", 
                "deadline": "14 giorni",
                "cost": "€500-1000"
            },
            {
                "action": "Analisi competitor approfondita",
                "owner": "Marketing Analyst",
                "deadline": "21 giorni", 
                "cost": "€300-500"
            }
        ]
        
        # Azioni a breve termine
        action_plan["short_term_actions"] = [
            {
                "action": "Ottimizzazione SEO on-page",
                "owner": "SEO Specialist",
                "deadline": "6 settimane",
                "cost": "€1000-2000"
            },
            {
                "action": "Creazione profili social mancanti",
                "owner": "Social Media Manager",
                "deadline": "4 settimane",
                "cost": "€500-800"
            },
            {
                "action": "Piano contenuti per 3 mesi",
                "owner": "Content Creator",
                "deadline": "8 settimane",
                "cost": "€1500-3000"
            }
        ]
        
        # Azioni a medio termine
        action_plan["medium_term_actions"] = [
            {
                "action": "Campagna link building",
                "owner": "SEO/PR Team",
                "deadline": "4 mesi",
                "cost": "€2000-5000"
            },
            {
                "action": "Ottimizzazione conversioni sito",
                "owner": "UX/Marketing Team",
                "deadline": "3 mesi",
                "cost": "€1500-3000"
            }
        ]
        
        # Azioni a lungo termine
        action_plan["long_term_actions"] = [
            {
                "action": "Strategia di content marketing avanzata",
                "owner": "Marketing Team",
                "deadline": "8 mesi",
                "cost": "€3000-6000"
            },
            {
                "action": "Implementazione marketing automation",
                "owner": "Marketing Technology",
                "deadline": "10 mesi",
                "cost": "€5000-10000"
            }
        ]
        
        # Target KPI
        action_plan["kpi_targets"] = {
            "3_months": {
                "organic_traffic": "+50%",
                "keyword_rankings": "+100 nuove keyword top 20",
                "social_followers": "+200%",
                "backlinks": "+25%"
            },
            "6_months": {
                "organic_traffic": "+150%",
                "conversion_rate": "+30%", 
                "domain_authority": "+20%",
                "social_engagement": "+100%"
            },
            "12_months": {
                "organic_traffic": "+300%",
                "lead_generation": "+250%",
                "market_share": "+15%",
                "brand_awareness": "+200%"
            }
        }
        
        return action_plan
    
    def _generate_appendix(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera appendice con dati dettagliati"""
        
        return {
            "data_sources": [
                "SEMRush API",
                "Serper.dev API", 
                "Registro Imprese",
                "Social Media Platforms",
                "Google Search"
            ],
            "methodology": {
                "seo_analysis": "Analisi tramite SEMRush API per traffico organico, keyword e backlink",
                "competitor_research": "Ricerca tramite Serper.dev e analisi cross-platform",
                "social_analysis": "Scraping responsabile dei profili social pubblici",
                "company_data": "Verifica su fonti ufficiali italiane"
            },
            "limitations": [
                "Dati SEMRush limitati alla disponibilità dell'API",
                "Dati social basati su informazioni pubbliche",
                "Analisi competitor limitata ai primi risultati di ricerca",
                "Dati aziendali soggetti alla disponibilità nelle fonti pubbliche"
            ],
            "raw_data": {
                "semrush": all_data.get("semrush_analysis", {}),
                "serper": all_data.get("serper_analysis", {}),
                "social": all_data.get("social_analysis", {}),
                "company": all_data.get("company_analysis", {})
            }
        }
    
    def _format_report(self, report: Dict[str, Any]) -> str:
        """Formatta il report in testo leggibile"""
        
        formatted = f"""
# {report['metadata']['report_title']}

**Data Analisi:** {report['metadata']['analysis_date']}  
**Azienda:** {report['metadata']['company_name']}

## Executive Summary

{report['executive_summary']['ai_generated_summary']}

### Metriche Chiave
{self._format_metrics(report['executive_summary']['key_metrics'])}

### Azioni Immediate
{self._format_list(report['executive_summary']['immediate_actions'])}

## Profilo Azienda

### Informazioni Base
- **Nome:** {report['company_profile']['basic_info']['company_name']}
- **Sito Web:** {report['company_profile']['basic_info']['website']}  
- **Settore:** {report['company_profile']['basic_info']['sector']}
- **Sede:** {report['company_profile']['basic_info']['headquarters']}

### Metriche Business
- **Dipendenti:** {report['company_profile']['business_metrics']['employees']}
- **Fatturato:** {report['company_profile']['business_metrics']['revenue']}

## Presenza Digitale

### Performance SEO
- **Keyword Organiche:** {report['digital_presence']['seo_performance'].get('organic_keywords', 'N/A')}
- **Posizioni Top 3:** {report['digital_presence']['seo_performance'].get('top_positions', 'N/A')}
- **Backlink Totali:** {report['digital_presence']['seo_performance'].get('total_backlinks', 'N/A')}
- **Authority Score:** {report['digital_presence']['seo_performance'].get('authority_score', 'N/A')}

### Presenza Social
- **Piattaforme Attive:** {report['digital_presence']['social_media_presence'].get('active_platforms', 'N/A')}
- **Follower Totali:** {report['digital_presence']['social_media_presence'].get('total_followers', 'N/A')}

**Score Digitale Complessivo:** {report['digital_presence']['overall_digital_score']:.1f}/10

## Analisi Competitor

### Competitor Identificati
{self._format_competitors(report['competitor_analysis']['identified_competitors'])}

## Opportunità di Crescita

{self._format_opportunities(report['opportunities'])}

## Raccomandazioni Strategiche

{self._format_recommendations(report['recommendations'])}

## Piano d'Azione

### Azioni Immediate (0-30 giorni)
{self._format_actions(report['action_plan']['immediate_actions'])}

### Azioni Breve Termine (1-3 mesi)  
{self._format_actions(report['action_plan']['short_term_actions'])}

### Target KPI a 6 mesi
{self._format_kpi_targets(report['action_plan']['kpi_targets']['6_months'])}

---
*Report generato automaticamente il {datetime.datetime.now().strftime('%d/%m/%Y alle %H:%M')}*
"""
        
        return formatted
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Formatta metriche in testo"""
        if not metrics:
            return "Nessuna metrica disponibile"
        
        formatted = ""
        for key, value in metrics.items():
            formatted += f"- **{key}:** {value}\n"
        
        return formatted
    
    def _format_list(self, items: List[str]) -> str:
        """Formatta lista in testo"""
        if not items:
            return "Nessun elemento"
        
        return "\n".join([f"- {item}" for item in items])
    
    def _format_competitors(self, competitors: List[Dict[str, Any]]) -> str:
        """Formatta lista competitor"""
        if not competitors:
            return "Nessun competitor identificato"
        
        formatted = ""
        for i, comp in enumerate(competitors[:5], 1):
            formatted += f"{i}. **{comp.get('name', 'N/A')}** - {comp.get('domain', 'N/A')}\n"
        
        return formatted
    
    def _format_opportunities(self, opportunities: List[Dict[str, Any]]) -> str:
        """Formatta opportunità"""
        if not opportunities:
            return "Nessuna opportunità identificata"
        
        formatted = ""
        for opp in opportunities:
            formatted += f"### {opp['category']} ({opp['type']})\n"
            formatted += f"**Impatto:** {opp['impact']} | **Effort:** {opp['effort']} | **Timeline:** {opp['timeline']}\n"
            formatted += f"{opp['description']}\n\n"
        
        return formatted
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Formatta raccomandazioni"""
        if not recommendations:
            return "Nessuna raccomandazione"
        
        formatted = ""
        for rec in recommendations:
            formatted += f"### {rec['title']} (Priorità: {rec['priority']})\n"
            formatted += f"{rec['description']}\n\n"
            formatted += "**Azioni:**\n"
            for action in rec['actions']:
                formatted += f"- {action}\n"
            formatted += f"\n**Risultati Attesi:** {rec['expected_results']}\n\n"
        
        return formatted
    
    def _format_actions(self, actions: List[Dict[str, Any]]) -> str:
        """Formatta azioni"""
        if not actions:
            return "Nessuna azione"
        
        formatted = ""
        for action in actions:
            formatted += f"- **{action['action']}** (Owner: {action['owner']}, Deadline: {action['deadline']}, Costo: {action['cost']})\n"
        
        return formatted
    
    def _format_kpi_targets(self, targets: Dict[str, str]) -> str:
        """Formatta target KPI"""
        if not targets:
            return "Nessun target definito"
        
        formatted = ""
        for kpi, target in targets.items():
            formatted += f"- **{kpi.replace('_', ' ').title()}:** {target}\n"
        
        return formatted
    
    # Metodi helper per calcoli
    
    def _calculate_seo_score(self, semrush_data: Dict[str, Any]) -> float:
        """Calcola score SEO basato su metriche SEMRush"""
        score = 0.0
        
        # Keywords (40% del punteggio)
        keyword_data = semrush_data.get("keywords", {})
        total_keywords = keyword_data.get("total_keywords", 0)
        top_keywords = keyword_data.get("keywords_1_3", 0)
        
        if total_keywords > 0:
            keyword_score = min(total_keywords / 1000, 1.0) * 0.3  # Max 30%
            if total_keywords > 0:
                top_ratio = top_keywords / total_keywords
                keyword_score += top_ratio * 0.1  # Max 10%
            score += keyword_score
        
        # Backlinks (30% del punteggio)
        backlink_data = semrush_data.get("backlinks", {})
        total_backlinks = backlink_data.get("total_backlinks", 0)
        authority_score = backlink_data.get("authority_score", 0)
        
        backlink_score = min(total_backlinks / 10000, 1.0) * 0.15  # Max 15%
        authority_normalized = authority_score / 100 * 0.15  # Max 15%
        score += backlink_score + authority_normalized
        
        # Traffico organico (30% del punteggio)
        organic_data = semrush_data.get("organic_traffic", {})
        organic_traffic = organic_data.get("organic_traffic", 0)
        
        traffic_score = min(organic_traffic / 100000, 1.0) * 0.3  # Max 30%
        score += traffic_score
        
        return min(score * 10, 10.0)  # Scala 0-10
    
    def _calculate_social_score(self, social_data: Dict[str, Any]) -> float:
        """Calcola score social basato su presenza e engagement"""
        score = 0.0
        
        social_analytics = social_data.get("social_analytics", {})
        total_platforms = len(social_analytics)
        
        # Numero piattaforme (40% del punteggio)
        platform_score = min(total_platforms / 5, 1.0) * 4.0
        score += platform_score
        
        # Follower totali (40% del punteggio) 
        total_followers = 0
        for platform_data in social_analytics.values():
            if not platform_data.get("error"):
                followers = platform_data.get("followers", 0) or platform_data.get("subscribers", 0)
                total_followers += followers
        
        follower_score = min(total_followers / 50000, 1.0) * 4.0
        score += follower_score
        
        # Presenza su piattaforme chiave (20% del punteggio)
        key_platforms = ["facebook", "instagram", "linkedin"]
        key_presence = sum([1 for p in key_platforms if p in social_analytics and not social_analytics[p].get("error")])
        key_score = (key_presence / len(key_platforms)) * 2.0
        score += key_score
        
        return min(score, 10.0)  # Scala 0-10
    
    def _extract_key_metrics(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estrae metriche chiave da tutti i dati"""
        metrics = {}
        
        # SEO metrics
        semrush_data = all_data.get("semrush_analysis", {})
        if semrush_data and not semrush_data.get("error"):
            keyword_data = semrush_data.get("keywords", {})
            backlink_data = semrush_data.get("backlinks", {})
            
            metrics["Keyword Organiche"] = keyword_data.get("total_keywords", 0)
            metrics["Keyword Top 3"] = keyword_data.get("keywords_1_3", 0)
            metrics["Backlink Totali"] = backlink_data.get("total_backlinks", 0)
            metrics["Authority Score"] = backlink_data.get("authority_score", 0)
        
        # Social metrics
        social_data = all_data.get("social_analysis", {})
        if social_data and not social_data.get("error"):
            social_analytics = social_data.get("social_analytics", {})
            
            total_followers = 0
            active_platforms = 0
            
            for platform_data in social_analytics.values():
                if not platform_data.get("error"):
                    active_platforms += 1
                    followers = platform_data.get("followers", 0) or platform_data.get("subscribers", 0)
                    total_followers += followers
            
            metrics["Piattaforme Social Attive"] = active_platforms
            metrics["Follower Totali"] = total_followers
        
        # Competitor metrics
        serper_data = all_data.get("serper_analysis", {})
        if serper_data:
            competitors = serper_data.get("competitors", {}).get("competitors", [])
            metrics["Competitor Identificati"] = len(competitors)
        
        return metrics
    
    def _identify_critical_findings(self, all_data: Dict[str, Any]) -> List[str]:
        """Identifica risultati critici"""
        findings = []
        
        # SEO critical findings
        semrush_data = all_data.get("semrush_analysis", {})
        if semrush_data and not semrush_data.get("error"):
            keyword_data = semrush_data.get("keywords", {})
            if keyword_data.get("total_keywords", 0) < 50:
                findings.append("🔴 Presenza SEO molto limitata - meno di 50 keyword posizionate")
            
            backlink_data = semrush_data.get("backlinks", {})
            if backlink_data.get("authority_score", 0) < 20:
                findings.append("🔴 Autorità dominio molto bassa - necessaria strategia link building")
        
        # Social critical findings  
        social_data = all_data.get("social_analysis", {})
        if social_data:
            social_analytics = social_data.get("social_analytics", {})
            if len(social_analytics) < 2:
                findings.append("🟡 Presenza social limitata - attivi su meno di 2 piattaforme")
        
        return findings
    
    def _identify_immediate_actions(self, all_data: Dict[str, Any]) -> List[str]:
        """Identifica azioni immediate necessarie"""
        actions = []
        
        # Technical SEO
        actions.append("Verifica configurazione Google Analytics e Search Console")
        actions.append("Audit tecnico completo del sito web")
        
        # Content
        semrush_data = all_data.get("semrush_analysis", {})
        if semrush_data and semrush_data.get("keywords", {}).get("total_keywords", 0) < 100:
            actions.append("Sviluppo strategia contenuti SEO-oriented")
        
        # Social
        social_data = all_data.get("social_analysis", {})
        if social_data and len(social_data.get("social_analytics", {})) < 3:
            actions.append("Creazione profili sui social principali mancanti")
        
        return actions
    
    def _identify_digital_strengths(self, digital_analysis: Dict[str, Any]) -> List[str]:
        """Identifica punti di forza digitali"""
        strengths = []
        
        seo_performance = digital_analysis.get("seo_performance", {})
        social_presence = digital_analysis.get("social_media_presence", {})
        
        if seo_performance.get("organic_keywords", 0) > 500:
            strengths.append("Forte presenza SEO con ampio portafoglio keyword")
        
        if seo_performance.get("authority_score", 0) > 50:
            strengths.append("Buona autorità del dominio")
        
        if social_presence.get("active_platforms", 0) >= 4:
            strengths.append("Presenza social diversificata")
        
        if social_presence.get("total_followers", 0) > 10000:
            strengths.append("Buona base di follower sui social")
        
        return strengths
    
    def _identify_digital_weaknesses(self, digital_analysis: Dict[str, Any]) -> List[str]:
        """Identifica debolezze digitali"""
        weaknesses = []
        
        seo_performance = digital_analysis.get("seo_performance", {})
        social_presence = digital_analysis.get("social_media_presence", {})
        
        if seo_performance.get("organic_keywords", 0) < 100:
            weaknesses.append("Presenza SEO limitata")
        
        if seo_performance.get("authority_score", 0) < 30:
            weaknesses.append("Bassa autorità del dominio")
        
        if social_presence.get("active_platforms", 0) < 3:
            weaknesses.append("Presenza social insufficiente")
        
        if social_presence.get("total_followers", 0) < 1000:
            weaknesses.append("Base follower limitata")
        
        return weaknesses
    
    def _analyze_competitive_landscape(self, competitors: Dict[str, Any], 
                                     semrush_data: Dict[str, Any], 
                                     social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza il panorama competitivo"""
        
        landscape = {
            "market_density": "Media",
            "competition_level": "Media", 
            "key_players": [],
            "market_gaps": [],
            "competitive_threats": []
        }
        
        num_competitors = len(competitors)
        
        if num_competitors > 10:
            landscape["market_density"] = "Alta"
            landscape["competition_level"] = "Alta"
        elif num_competitors < 3:
            landscape["market_density"] = "Bassa"
            landscape["competition_level"] = "Bassa"
        
        # Identifica key players (primi 3 competitor)
        competitor_list = list(competitors.values())
        landscape["key_players"] = [comp.get("name", "") for comp in competitor_list[:3]]
        
        return landscape
    
    def _identify_competitive_gaps(self, semrush_data: Dict[str, Any], 
                                 social_data: Dict[str, Any]) -> List[str]:
        """Identifica gap competitivi"""
        gaps = []
        
        # Gap SEO
        if semrush_data and not semrush_data.get("error"):
            competitors = semrush_data.get("competitors", [])
            if competitors:
                # Analizza competitor con più keyword
                max_keywords = max([comp.get("se_keywords", 0) for comp in competitors], default=0)
                company_keywords = semrush_data.get("keywords", {}).get("total_keywords", 0)
                
                if max_keywords > company_keywords * 2:
                    gaps.append("Gap significativo nel numero di keyword posizionate rispetto ai competitor")
        
        # Gap Social
        if social_data:
            social_comparison = social_data.get("social_comparison", {})
            if social_comparison.get("total_platforms", 0) < 3:
                gaps.append("Gap nella presenza social rispetto ai competitor")
        
        return gaps
    
    def _identify_competitive_opportunities(self, competitors: Dict[str, Any]) -> List[str]:
        """Identifica opportunità competitive"""
        opportunities = []
        
        if len(competitors) > 5:
            opportunities.append("Mercato frammentato - opportunità di consolidamento")
        
        opportunities.append("Analisi keyword competitor per identificare gap di contenuto")
        opportunities.append("Studio strategie social dei competitor per best practice")
        
        return opportunities