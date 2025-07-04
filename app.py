import streamlit as st
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

class SimpleSerperAgent:
    """Agente Serper semplificato ma completo"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def deep_company_research(self, company_name: str, domain: str = None) -> Dict[str, Any]:
        """Ricerca approfondita dell'azienda"""
        
        all_results = {
            "company_info": {},
            "financial_data": {},
            "business_info": {}
        }
        
        # Query specifiche per diversi tipi di informazioni
        queries = [
            f"{company_name} azienda informazioni sede",
            f"{company_name} fatturato dipendenti",
            f"{company_name} prodotti servizi"
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
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore ricerca '{query}': {e}")
                continue
        
        return all_results
    
    def research_competitors(self, company_name: str, sector: str = None) -> List[Dict[str, Any]]:
        """Ricerca competitor"""
        
        competitor_queries = [
            f"{company_name} competitor concorrenti",
            f"{company_name} alternative simili"
        ]
        
        all_competitors = []
        seen_domains = set()
        
        for query in competitor_queries:
            try:
                results = self._search(query)
                
                if "organic" in results:
                    for result in results["organic"][:3]:
                        domain = self._extract_domain(result.get("link", ""))
                        
                        if domain and domain not in seen_domains:
                            seen_domains.add(domain)
                            
                            competitor = {
                                "name": result.get("title", "").split(" - ")[0],
                                "domain": domain,
                                "url": result.get("link", ""),
                                "description": result.get("snippet", "")
                            }
                            
                            all_competitors.append(competitor)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore ricerca competitor: {e}")
                continue
        
        return all_competitors[:5]
    
    def analyze_competitor_details(self, competitor: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza dettagli di un competitor"""
        
        comp_name = competitor.get("name", "")
        if not comp_name:
            return {"basic_info": competitor, "detailed_research": {}}
        
        try:
            query = f"{comp_name} azienda informazioni business"
            results = self._search(query)
            
            return {
                "basic_info": competitor,
                "detailed_research": {
                    "search_1": {
                        "query": query,
                        "results": results
                    }
                }
            }
        except Exception as e:
            logger.error(f"Errore analisi competitor: {e}")
            return {"basic_info": competitor, "detailed_research": {}}
    
    def comprehensive_social_analysis(self, company_name: str) -> Dict[str, Any]:
        """Analisi completa social media"""
        
        social_platforms = {
            "instagram": "instagram.com",
            "facebook": "facebook.com",
            "linkedin": "linkedin.com",
            "youtube": "youtube.com",
            "tiktok": "tiktok.com"
        }
        
        social_analysis = {
            "platforms_found": {},
            "social_metrics": {},
            "engagement_analysis": {}
        }
        
        for platform, domain in social_platforms.items():
            try:
                query = f"site:{domain} {company_name}"
                results = self._search(query)
                
                if "organic" in results and len(results["organic"]) > 0:
                    result = results["organic"][0]
                    link = result.get("link", "")
                    
                    if platform in link.lower():
                        social_analysis["platforms_found"][platform] = {
                            "url": link,
                            "title": result.get("title", ""),
                            "description": result.get("snippet", "")
                        }
                        
                        # Cerca metriche specifiche
                        metrics = self._get_platform_metrics(company_name, platform)
                        social_analysis["social_metrics"][platform] = metrics
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore analisi social {platform}: {e}")
                continue
        
        # Calcola engagement complessivo
        platforms_count = len(social_analysis["platforms_found"])
        total_followers = 0
        
        for platform, metrics in social_analysis["social_metrics"].items():
            followers_str = metrics.get("followers", "0")
            if followers_str != "N/A":
                total_followers += self._convert_social_number(followers_str)
        
        social_analysis["engagement_analysis"] = {
            "platforms_active": platforms_count,
            "presence_score": round((platforms_count / 5) * 100, 1),
            "total_followers_estimate": total_followers,
            "social_maturity": "Alto" if platforms_count >= 4 else "Medio" if platforms_count >= 2 else "Basso"
        }
        
        return social_analysis
    
    def _get_platform_metrics(self, company_name: str, platform: str) -> Dict[str, Any]:
        """Cerca metriche specifiche per piattaforma"""
        
        try:
            query = f"{company_name} {platform} follower statistics"
            results = self._search(query)
            
            metrics = {
                "followers": "N/A",
                "engagement_rate": "N/A",
                "verified": "N/A"
            }
            
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
            
            return metrics
            
        except Exception as e:
            logger.error(f"Errore metriche {platform}: {e}")
            return {"followers": "N/A", "engagement_rate": "N/A", "verified": "N/A"}
    
    def _convert_social_number(self, number_str: str) -> int:
        """Converte numeri social in integer"""
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

class SimpleSEMRushAgent:
    """Agente SEMRush semplificato"""
    
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
            "backlinks": {}
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
            
        except Exception as e:
            analysis["error"] = f"Errore analisi SEO: {str(e)}"
        
        return analysis
    
    def _get_domain_overview(self, domain: str) -> Dict[str, Any]:
        """Overview del dominio"""
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
                    "adwords_keywords": item.get("Ad", 0)
                }
            
            return {"error": "Nessun dato overview disponibile"}
            
        except Exception as e:
            return {"error": f"Errore overview: {str(e)}"}
    
    def _get_keywords_analysis(self, domain: str) -> Dict[str, Any]:
        """Analisi keywords"""
        params = {
            "type": "domain_organic",
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
            
            if isinstance(data, list):
                keywords = []
                position_distribution = {"1-3": 0, "4-10": 0, "11-20": 0, "21+": 0}
                
                for item in data:
                    if isinstance(item, dict):
                        pos = item.get("Po", 0)
                        keywords.append({
                            "keyword": item.get("Ph", ""),
                            "position": pos,
                            "volume": item.get("Nq", 0)
                        })
                        
                        if 1 <= pos <= 3:
                            position_distribution["1-3"] += 1
                        elif 4 <= pos <= 10:
                            position_distribution["4-10"] += 1
                        elif 11 <= pos <= 20:
                            position_distribution["11-20"] += 1
                        else:
                            position_distribution["21+"] += 1
                
                return {
                    "total_keywords": len(keywords),
                    "position_distribution": position_distribution,
                    "top_keywords": keywords[:10]
                }
            
            return {"error": "Nessuna keyword trovata"}
            
        except Exception as e:
            return {"error": f"Errore keywords: {str(e)}"}
    
    def _get_backlinks_analysis(self, domain: str) -> Dict[str, Any]:
        """Analisi backlinks"""
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
                    "authority_score": data.get("ascore", 0)
                }
            
            return {"error": "Nessun dato backlinks disponibile"}
            
        except Exception as e:
            return {"error": f"Errore backlinks: {str(e)}"}

class OpenAIAnalyzer:
    """Analyzer OpenAI per insights avanzati"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_insights(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera insights AI basati su tutti i dati"""
        
        context = json.dumps(all_data, ensure_ascii=False)[:3000]  # Limita la lunghezza
        
        prompt = f"""
        Analizza i seguenti dati aziendali e genera insights strutturati:
        
        {context}
        
        Genera un JSON con:
        {{
            "profilo_aziendale": {{
                "settore": "settore identificato",
                "posizionamento": "descrizione posizionamento",
                "punti_forza": ["lista punti forza"],
                "aree_miglioramento": ["lista aree da migliorare"]
            }},
            "analisi_swot": {{
                "strengths": ["punti di forza"],
                "weaknesses": ["punti di debolezza"], 
                "opportunities": ["opportunità"],
                "threats": ["minacce"]
            }},
            "raccomandazioni": {{
                "immediate": ["azioni immediate"],
                "breve_termine": ["azioni 3-6 mesi"],
                "lungo_termine": ["azioni 12+ mesi"]
            }}
        }}
        """
        
        return self._query_openai(prompt)
    
    def _query_openai(self, prompt: str) -> Dict[str, Any]:
        """Query OpenAI"""
        try:
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "Sei un consulente di business strategy. Rispondi sempre in JSON valido e in italiano."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
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
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"analysis": content}
            else:
                return {"error": f"OpenAI API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Errore OpenAI: {str(e)}"}

class ReportGenerator:
    """Generatore report completo"""
    
    def __init__(self, openai_analyzer: OpenAIAnalyzer = None):
        self.openai_analyzer = openai_analyzer
    
    def generate_complete_report(self, company_data: Dict[str, Any], 
                               all_analysis_data: Dict[str, Any]) -> str:
        """Genera report completo"""
        
        company_name = company_data.get("company_name", "Azienda")
        analysis_date = datetime.now().strftime("%d/%m/%Y")
        
        # Genera insights AI se disponibile
        ai_insights = {}
        if self.openai_analyzer:
            ai_insights = self.openai_analyzer.generate_insights(all_analysis_data)
        
        # Costruisci il report
        report = f"""# REPORT ANALISI MARKETING COMPLETA
## {company_name}

**Data Analisi:** {analysis_date}
**Generato da:** Marketing Analyzer Pro

---

"""
        
        # 1. PROFILO AZIENDALE
        report += self._section_company_profile(company_data, all_analysis_data, ai_insights)
        
        # 2. ANALISI FINANZIARIA
        report += self._section_financial_analysis(all_analysis_data)
        
        # 3. PRODOTTI E SERVIZI
        report += self._section_products_services(all_analysis_data)
        
        # 4. PRESENZA DIGITALE E SOCIAL MEDIA
        report += self._section_digital_presence(all_analysis_data)
        
        # 5. MERCATO E POSIZIONAMENTO
        report += self._section_market_positioning(all_analysis_data, ai_insights)
        
        # 6. ANALISI COMPETITOR
        report += self._section_competitor_analysis(all_analysis_data)
        
        # 7. ANALISI SWOT
        report += self._section_swot_analysis(ai_insights)
        
        # 8. RACCOMANDAZIONI STRATEGICHE
        report += self._section_recommendations(ai_insights)
        
        # 9. CONCLUSIONI
        report += self._section_conclusions(company_name, all_analysis_data)
        
        return report
    
    def _section_company_profile(self, company_data: Dict[str, Any], 
                                all_analysis_data: Dict[str, Any],
                                ai_insights: Dict[str, Any]) -> str:
        """Sezione profilo aziendale"""
        
        section = """
## 1. PROFILO AZIENDALE

"""
        
        # Informazioni base
        section += f"**Nome Azienda:** {company_data.get('company_name', 'N/A')}\n"
        
        if company_data.get('vat_number'):
            section += f"**P.IVA:** {company_data['vat_number']}\n"
        
        if company_data.get('website'):
            section += f"**Sito Web:** {company_data['website']}\n"
        
        # Settore da AI
        profilo_ai = ai_insights.get('profilo_aziendale', {})
        if profilo_ai.get('settore'):
            section += f"**Settore:** {profilo_ai['settore']}\n"
        
        # Knowledge Graph se disponibile
        company_research = all_analysis_data.get("company_research", {})
        company_info = company_research.get("company_info", {})
        kg = company_info.get("knowledge_graph", {})
        
        if kg.get("description"):
            section += f"\n### Descrizione\n{kg['description']}\n"
        
        # Posizionamento da AI
        if profilo_ai.get('posizionamento'):
            section += f"\n### Posizionamento di Mercato\n{profilo_ai['posizionamento']}\n"
        
        return section
    
    def _section_financial_analysis(self, all_analysis_data: Dict[str, Any]) -> str:
        """Sezione analisi finanziaria"""
        
        section = """
## 2. ANALISI FINANZIARIA

"""
        
        # Cerca informazioni finanziarie nei risultati di ricerca
        financial_data = all_analysis_data.get("company_research", {}).get("financial_data", {})
        
        if "organic" in financial_data:
            section += "### Informazioni Finanziarie Disponibili\n"
            
            for result in financial_data["organic"][:3]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                
                if any(word in snippet.lower() for word in ["fatturato", "bilancio", "dipendenti", "capitale"]):
                    section += f"**{title}**\n"
                    section += f"{snippet}\n\n"
        
        if section == """
## 2. ANALISI FINANZIARIA

""":
            section += "Dati finanziari dettagliati non disponibili dalle fonti pubbliche analizzate.\n"
        
        return section
    
    def _section_products_services(self, all_analysis_data: Dict[str, Any]) -> str:
        """Sezione prodotti e servizi"""
        
        section = """
## 3. PRODOTTI E SERVIZI

"""
        
        # Cerca informazioni sui prodotti
        business_data = all_analysis_data.get("company_research", {}).get("business_info", {})
        
        if "organic" in business_data:
            section += "### Prodotti e Servizi Principali\n"
            
            for result in business_data["organic"][:3]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                
                if any(word in snippet.lower() for word in ["prodotti", "servizi", "offerta", "soluzioni"]):
                    section += f"**{title}**\n"
                    section += f"{snippet}\n\n"
        
        if section == """
## 3. PRODOTTI E SERVIZI

""":
            section += "Informazioni dettagliate sui prodotti e servizi non disponibili dalle fonti analizzate.\n"
        
        return section
    
    def _section_digital_presence(self, all_analysis_data: Dict[str, Any]) -> str:
        """Sezione presenza digitale"""
        
        section = """
## 4. PRESENZA DIGITALE E SOCIAL MEDIA

"""
        
        # Sito web
        company_data = all_analysis_data.get("company_info", {})
        if company_data.get("website"):
            section += f"### Sito Web\n**URL Principale:** {company_data['website']}\n"
        
        # Performance SEO
        seo_data = all_analysis_data.get("seo_analysis", {})
        if seo_data and "error" not in seo_data:
            section += "\n### Performance SEO\n"
            
            overview = seo_data.get("overview", {})
            if overview and "error" not in overview:
                section += f"**Keyword organiche:** {overview.get('organic_keywords', 0):,} posizionamenti\n"
                section += f"**Traffico organico stimato:** {overview.get('organic_traffic', 0):,} visite/mese\n"
                section += f"**Valore stimato del traffico:** €{overview.get('organic_cost', 0):,.0f}\n"
            
            backlinks = seo_data.get("backlinks", {})
            if backlinks and "error" not in backlinks:
                section += f"**Backlink:** {backlinks.get('total_backlinks', 0):,}\n"
                section += f"**Domini referenti:** {backlinks.get('referring_domains', 0):,}\n"
                section += f"**Authority Score:** {backlinks.get('authority_score', 0)}\n"
        
        # Presenza social
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
                section += f"\n### Analisi Engagement\n"
                section += f"**Piattaforme attive:** {engagement.get('platforms_active', 0)}\n"
                section += f"**Score presenza:** {engagement.get('presence_score', 0)}%\n"
                section += f"**Follower totali stimati:** {engagement.get('total_followers_estimate', 0):,}\n"
                section += f"**Maturità social:** {engagement.get('social_maturity', 'N/A')}\n"
        
        return section
    
    def _section_market_positioning(self, all_analysis_data: Dict[str, Any], ai_insights: Dict[str, Any]) -> str:
        """Sezione mercato e posizionamento"""
        
        section = """
## 5. MERCATO E POSIZIONAMENTO

"""
        
        # Posizionamento da AI
        profilo_ai = ai_insights.get('profilo_aziendale', {})
        if profilo_ai.get('settore'):
            section += f"### Mercato di Riferimento\n{profilo_ai['settore']}\n"
        
        if profilo_ai.get('posizionamento'):
            section += f"\n### Posizionamento Competitivo\n{profilo_ai['posizionamento']}\n"
        
        # Competitor identificati
        competitors_data = all_analysis_data.get("competitors_analysis", [])
        if competitors_data:
            section += f"\n### Concorrenti Diretti\n"
            for i, comp in enumerate(competitors_data[:3], 1):
                basic_info = comp.get("basic_info", {})
                section += f"{i}. {basic_info.get('name', 'N/A')}\n"
        
        return section
    
    def _section_competitor_analysis(self, all_analysis_data: Dict[str, Any]) -> str:
        """Sezione analisi competitor"""
        
        section = """
## 6. ANALISI COMPETITOR

"""
        
        competitors_data = all_analysis_data.get("competitors_analysis", [])
        
        if not competitors_data:
            section += "Nessun competitor principale identificato nell'analisi.\n"
            return section
        
        section += f"### Competitor Identificati ({len(competitors_data)})\n\n"
        
        for i, competitor in enumerate(competitors_data, 1):
            basic_info = competitor.get("basic_info", {})
            comp_name = basic_info.get("name", "N/A")
            section += f"#### {i}. {comp_name}\n"
            section += f"**Dominio:** {basic_info.get('domain', 'N/A')}\n"
            section += f"**URL:** {basic_info.get('url', 'N/A')}\n"
            section += f"**Descrizione:** {basic_info.get('description', 'N/A')}\n"
            
            # Analisi dettagliata se disponibile
            detailed = competitor.get("detailed_research", {})
            if detailed:
                for search_key, search_data in detailed.items():
                    if isinstance(search_data, dict) and "results" in search_data:
                        results = search_data["results"]
                        if "organic" in results and len(results["organic"]) > 0:
                            first_result = results["organic"][0]
                            snippet = first_result.get("snippet", "")
                            if len(snippet) > 50:
                                section += f"**Info Aggiuntive:** {snippet[:200]}...\n"
                                break
            
            section += "\n"
        
        return section
    
    def _section_swot_analysis(self, ai_insights: Dict[str, Any]) -> str:
        """Sezione analisi SWOT"""
        
        section = """
## 7. ANALISI SWOT

"""
        
        swot = ai_insights.get('analisi_swot', {})
        profilo = ai_insights.get('profilo_aziendale', {})
        
        # Punti di forza
        strengths = swot.get('strengths', []) or profilo.get('punti_forza', [])
        if strengths:
            section += "### Punti di Forza\n"
            for punto in strengths:
                section += f"- {punto}\n"
        
        # Punti di debolezza
        weaknesses = swot.get('weaknesses', []) or profilo.get('aree_miglioramento', [])
        if weaknesses:
            section += "\n### Punti di Debolezza\n"
            for punto in weaknesses:
                section += f"- {punto}\n"
        
        # Opportunità
        opportunities = swot.get('opportunities', [])
        if opportunities:
            section += "\n### Opportunità\n"
            for opportunita in opportunities:
                section += f"- {opportunita}\n"
        
        # Minacce
        threats = swot.get('threats', [])
        if threats:
            section += "\n### Minacce\n"
            for minaccia in threats:
                section += f"- {minaccia}\n"
        
        if section == """
## 7. ANALISI SWOT

""":
            section += "Analisi SWOT non disponibile. Configurare OpenAI API per insights avanzati.\n"
        
        return section
    
    def _section_recommendations(self, ai_insights: Dict[str, Any]) -> str:
        """Sezione raccomandazioni"""
        
        section = """
## 8. RACCOMANDAZIONI STRATEGICHE

"""
        
        recommendations = ai_insights.get('raccomandazioni', {})
        
        # Azioni immediate
        immediate = recommendations.get('immediate', [])
        if immediate:
            section += "### Priorità Immediate (0-3 mesi)\n"
            for azione in immediate:
                section += f"- {azione}\n"
        
        # Breve termine
        breve_termine = recommendations.get('breve_termine', [])
        if breve_termine:
            section += "\n### Obiettivi Breve Termine (3-6 mesi)\n"
            for obiettivo in breve_termine:
                section += f"- {obiettivo}\n"
        
        # Lungo termine
        lungo_termine = recommendations.get('lungo_termine', [])
        if lungo_termine:
            section += "\n### Visione Lungo Termine (12+ mesi)\n"
            for visione in lungo_termine:
                section += f"- {visione}\n"
        
        if section == """
## 8. RACCOMANDAZIONI STRATEGICHE

""":
            section += """
### Raccomandazioni Generali

**Sviluppo Digitale:**
- Migliorare la presenza SEO attraverso content marketing
- Ottimizzare la strategia social media
- Implementare analytics per tracciare le performance

**Crescita Commerciale:**
- Monitorare costantemente i competitor
- Sviluppare partnerships strategiche
- Investire in customer experience

**Innovazione:**
- Adottare nuove tecnologie di marketing
- Automatizzare i processi dove possibile
- Formare il team sulle best practice digitali
"""
        
        return section
    
    def _section_conclusions(self, company_name: str, all_analysis_data: Dict[str, Any]) -> str:
        """Sezione conclusioni"""
        
        section = """
## 9. CONCLUSIONI

"""
        
        # Analizza i dati per generare conclusioni
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
                section += "un'azienda in crescita nel panorama digitale, "
            else:
                section += "un'azienda con significative opportunità di crescita digitale, "
        else:
            section += "un'azienda "
        
        if competitors_count > 3:
            section += "operante in un mercato competitivo. "
        elif competitors_count > 1:
            section += "con una concorrenza moderata nel suo settore. "
        else:
            section += "in un mercato di nicchia. "
        
        if social_platforms >= 3:
            section += "L'azienda dimostra una buona maturità nella presenza social media."
        elif social_platforms >= 1:
            section += "La presenza social è presente ma può essere significativamente ampliata."
        else:
            section += "Esiste un importante potenziale di sviluppo nella presenza sui social media."
        
        section += "\n\n"
        
        # Raccomandazioni finali
        section += "### Raccomandazioni Finali\n\n"
        section += "Per massimizzare le opportunità di crescita:\n\n"
        section += "1. **Investire nella presenza digitale** attraverso SEO e content marketing\n"
        section += "2. **Sviluppare una strategia social integrata** per aumentare la visibilità\n"
        section += "3. **Monitorare attivamente i competitor** per identificare opportunità\n"
        section += "4. **Implementare metriche di performance** per misurare i progressi\n"
        section += "5. **Considerare partnership** per accelerare la crescita\n\n"
        
        section += f"Con un approccio strategico e un'implementazione coerente, {company_name} può raggiungere una posizione di leadership nel proprio settore di riferimento.\n\n"
        
        section += "---\n"
        section += f"*Report generato automaticamente da Marketing Analyzer Pro il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}*\n"
        section += "*Analisi basata su dati pubblici disponibili al momento della generazione*\n"
        
        return section

class AdvancedMarketingAnalyzer:
    """Analyzer principale che coordina tutte le analisi"""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.serper_agent = None
        self.semrush_agent = None
        self.openai_analyzer = None
        self.report_generator = None
    
    def setup_api_config(self, openai_key: str, semrush_key: str, serper_key: str):
        """Setup delle API keys"""
        self.api_config.openai_api_key = openai_key
        self.api_config.semrush_api_key = semrush_key
        self.api_config.serper_api_key = serper_key
        
        # Inizializza gli agenti disponibili
        if serper_key:
            self.serper_agent = SimpleSerperAgent(serper_key)
        
        if semrush_key:
            self.semrush_agent = SimpleSEMRushAgent(semrush_key)
        
        if openai_key:
            self.openai_analyzer = OpenAIAnalyzer(openai_key)
        
        self.report_generator = ReportGenerator(self.openai_analyzer)
    
    def run_comprehensive_analysis(self, company_input: str) -> Dict[str, Any]:
        """Esegue l'analisi completa"""
        
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
        
        # Progress tracking
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 1. RICERCA APPROFONDITA AZIENDA
                status_text.text("🔍 Ricerca approfondita informazioni azienda...")
                progress_bar.progress(10)
                
                if self.serper_agent:
                    company_research = self.serper_agent.deep_company_research(company_name, domain)
                    results["company_research"] = company_research
                    results["analysis_status"]["company_research"] = "✅ Completata"
                    st.success("✅ Ricerca azienda completata")
                else:
                    results["analysis_status"]["company_research"] = "❌ Serper non disponibile"
                
                progress_bar.progress(25)
                
                # 2. ANALISI SEO
                status_text.text("📊 Analisi SEO con SEMRush...")
                
                if self.semrush_agent and domain:
                    seo_analysis = self.semrush_agent.comprehensive_seo_analysis(domain)
                    results["seo_analysis"] = seo_analysis
                    results["analysis_status"]["seo_analysis"] = "✅ Completata"
                    st.success("✅ Analisi SEO completata")
                else:
                    results["analysis_status"]["seo_analysis"] = "⚠️ SEMRush non disponibile"
                    if not domain:
                        st.warning("⚠️ Dominio non identificato per analisi SEO")
                    else:
                        st.warning("⚠️ SEMRush API non configurata")
                
                progress_bar.progress(50)
                
                # 3. RICERCA E ANALISI COMPETITOR
                status_text.text("🎯 Ricerca e analisi competitor...")
                
                if self.serper_agent:
                    competitors = self.serper_agent.research_competitors(company_name)
                    
                    # Analisi dettagliata dei competitor
                    detailed_competitors = []
                    for i, competitor in enumerate(competitors[:3]):
                        status_text.text(f"🔍 Analizzando competitor {i+1}/3: {competitor.get('name', 'N/A')}")
                        
                        detailed_analysis = self.serper_agent.analyze_competitor_details(competitor)
                        detailed_competitors.append(detailed_analysis)
                        
                        progress_bar.progress(50 + (i + 1) * 8)
                    
                    results["competitors_analysis"] = detailed_competitors
                    results["analysis_status"]["competitors_analysis"] = f"✅ Analizzati {len(detailed_competitors)} competitor"
                    st.success(f"✅ Analisi competitor completata ({len(detailed_competitors)} competitor)")
                else:
                    results["analysis_status"]["competitors_analysis"] = "❌ Serper non disponibile"
                
                progress_bar.progress(75)
                
                # 4. ANALISI SOCIAL MEDIA
                status_text.text("📱 Analisi social media...")
                
                if self.serper_agent:
                    social_analysis = self.serper_agent.comprehensive_social_analysis(company_name)
                    results["social_analysis"] = social_analysis
                    
                    platforms_found = len(social_analysis.get("platforms_found", {}))
                    results["analysis_status"]["social_analysis"] = f"✅ Trovate {platforms_found} piattaforme"
                    st.success(f"✅ Analisi social completata ({platforms_found} piattaforme)")
                else:
                    results["analysis_status"]["social_analysis"] = "❌ Social analyzer non disponibile"
                
                progress_bar.progress(90)
                
                # 5. GENERAZIONE REPORT
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

def main():
    """Funzione principale dell'applicazione"""
    
    # Header
    st.title("📊 Marketing Analyzer Pro")
    st.markdown("### 🚀 Analisi marketing completa in stile professionale")
    st.markdown("*Genera report dettagliati con analisi AI avanzate*")
    st.markdown("---")
    
    # Inizializza analyzer
    if 'advanced_analyzer' not in st.session_state:
        st.session_state.advanced_analyzer = AdvancedMarketingAnalyzer()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurazione API")
        
        # API Keys
        openai_key = st.text_input(
            "🤖 OpenAI API Key",
            type="password",
            value=st.session_state.get('openai_key', ''),
            help="Per analisi AI avanzate, SWOT, raccomandazioni"
        )
        
        semrush_key = st.text_input(
            "📊 SEMRush API Key",
            type="password",
            value=st.session_state.get('semrush_key', ''),
            help="Per analisi SEO dettagliate"
        )
        
        serper_key = st.text_input(
            "🔍 Serper.dev API Key",
            type="password",
            value=st.session_state.get('serper_key', ''),
            help="OBBLIGATORIA per ricerca online"
        )
        
        # Salva in session state
        st.session_state.openai_key = openai_key
        st.session_state.semrush_key = semrush_key
        st.session_state.serper_key = serper_key
        
        # Setup analyzer
        st.session_state.advanced_analyzer.setup_api_config(openai_key, semrush_key, serper_key)
        
        # Status API
        st.markdown("---")
        st.subheader("🔌 Status API")
        
        if openai_key.startswith('sk-'):
            st.success("🤖 OpenAI: Configurata")
        else:
            st.error("🤖 OpenAI: Non configurata")
        
        if len(semrush_key) > 10:
            st.success("📊 SEMRush: Configurata")
        else:
            st.error("📊 SEMRush: Non configurata")
        
        if len(serper_key) > 10:
            st.success("🔍 Serper: Configurata")
        else:
            st.error("🔍 Serper: Non configurata")
        
        # Info
        st.markdown("---")
        st.info("""
        **Report include:**
        - Profilo aziendale completo
        - Analisi finanziaria
        - Prodotti e servizi
        - Presenza digitale e SEO
        - Social media dettagliato
        - Analisi competitor
        - SWOT analysis
        - Raccomandazioni strategiche
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Analisi Azienda Completa")
        
        # Form di input
        with st.form("analysis_form"):
            company_input = st.text_input(
                "Nome azienda, URL sito web, o Partita IVA",
                placeholder="Es: Venezianico, https://venezianico.com, IT04427770278",
                help="Il sistema riconoscerà automaticamente il tipo di input"
            )
            
            analyze_button = st.form_submit_button(
                "🚀 Avvia Analisi Completa", 
                type="primary"
            )
        
        # Risultati analisi
        if analyze_button:
            if not company_input:
                st.error("⚠️ Inserisci un'azienda da analizzare")
            elif not serper_key:
                st.error("⚠️ Serper.dev API key obbligatoria per l'analisi")
            else:
                st.info("⏱️ L'analisi completa richiede 2-4 minuti. Attendi...")
                
                with st.spinner("Analisi in corso..."):
                    results = st.session_state.advanced_analyzer.run_comprehensive_analysis(company_input)
                    st.session_state.comprehensive_results = results
                
                if "error" not in results:
                    st.success("🎉 Analisi completa terminata!")
                    
                    # Status analisi
                    with st.expander("📊 Status Analisi", expanded=True):
                        status_data = results.get("analysis_status", {})
                        for analysis, status in status_data.items():
                            st.markdown(f"**{analysis.replace('_', ' ').title()}:** {status}")
                    
                    # Report completo
                    if "comprehensive_report" in results:
                        st.markdown("---")
                        display_comprehensive_report(results)
                    
                else:
                    st.error(f"❌ Errore: {results['error']}")
    
    with col2:
        st.subheader("📋 Guida")
        
        st.markdown("""
        **Tipi di input:**
        
        🏢 **Nome azienda**
        - Es: "Apple Inc"
        - Es: "Venezianico"
        
        🌐 **URL sito web**
        - Es: "https://apple.com"
        - Es: "venezianico.com"
        
        📄 **Partita IVA italiana**
        - Es: "IT04427770278"
        - Es: "04427770278"
        """)
        
        st.markdown("---")
        
        # Esempi di test
        st.subheader("🧪 Esempi Test")
        
        examples = [
            ("🏢 Venezianico", "Venezianico"),
            ("🌐 Apple", "https://apple.com"),
            ("📄 P.IVA Test", "IT00359200447"),
            ("🚗 Ferrari", "Ferrari")
        ]
        
        for label, value in examples:
            if st.button(label, key=f"example_{value}"):
                st.info(f"Esempio: {value}")

def display_comprehensive_report(results: Dict[str, Any]):
    """Mostra il report completo"""
    
    comprehensive_report = results.get("comprehensive_report", "")
    
    if not comprehensive_report:
        st.warning("⚠️ Report non disponibile")
        return
    
    # Tab per organizzare
    tab1, tab2, tab3 = st.tabs(["📄 Report Completo", "📊 Dati JSON", "💾 Download"])
    
    with tab1:
        st.subheader("📄 Report Marketing Completo")
        st.markdown(comprehensive_report)
    
    with tab2:
        st.subheader("📊 Dati Strutturati")
        
        sections = [
            ("company_info", "🏢 Info Azienda"),
            ("company_research", "🔍 Ricerca"),
            ("seo_analysis", "📊 SEO"),
            ("competitors_analysis", "🎯 Competitor"),
            ("social_analysis", "📱 Social"),
            ("analysis_status", "✅ Status")
        ]
        
        for key, title in sections:
            if key in results:
                with st.expander(title):
                    st.json(results[key])
    
    with tab3:
        st.subheader("💾 Download Report")
        
        company_name = results.get("company_info", {}).get("company_name", "azienda")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # Download Markdown
        st.download_button(
            label="📥 Scarica Report Markdown",
            data=comprehensive_report,
            file_name=f"report_{company_name.lower().replace(' ', '_')}_{timestamp}.md",
            mime="text/markdown"
        )
        
        # Download JSON
        json_data = json.dumps(results, ensure_ascii=False, indent=2)
        st.download_button(
            label="📊 Scarica Dati JSON",
            data=json_data,
            file_name=f"dati_{company_name.lower().replace(' ', '_')}_{timestamp}.json",
            mime="application/json"
        )

def show_analysis_summary(results: Dict[str, Any]):
    """Mostra riassunto analisi"""
    
    st.subheader("📊 Riassunto Analisi")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Competitor
    competitors_count = len(results.get("competitors_analysis", []))
    with col1:
        st.metric("🎯 Competitor", competitors_count)
    
    # Social platforms
    social_platforms = len(results.get("social_analysis", {}).get("platforms_found", {}))
    with col2:
        st.metric("📱 Social", social_platforms)
    
    # SEO keywords
    seo_data = results.get("seo_analysis", {})
    keywords = seo_data.get("overview", {}).get("organic_keywords", 0) if seo_data else 0
    with col3:
        st.metric("📊 Keywords", f"{keywords:,}")
    
    # Authority
    authority = seo_data.get("backlinks", {}).get("authority_score", 0) if seo_data else 0
    with col4:
        st.metric("⭐ Authority", authority)

if __name__ == "__main__":
    # Esegui applicazione
    main()
    
    # Mostra riassunto se disponibile
    if 'comprehensive_results' in st.session_state:
        results = st.session_state.comprehensive_results
        if "error" not in results:
            st.markdown("---")
            show_analysis_summary(results)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <small>📊 Marketing Analyzer Pro | Powered by AI | Versione 2.0</small>
    </div>
    """, unsafe_allow_html=True)
