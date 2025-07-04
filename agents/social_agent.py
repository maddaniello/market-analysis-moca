from typing import Dict, Any, List
import requests
import json
import re
from bs4 import BeautifulSoup
from .base_agent import BaseAgent

class SocialAgent(BaseAgent):
    """Agente per l'analisi dei social media"""
    
    def __init__(self, api_config, app_config):
        super().__init__(api_config, app_config)
        self.social_platforms = {
            "facebook": "facebook.com",
            "instagram": "instagram.com",
            "linkedin": "linkedin.com",
            "twitter": "twitter.com", 
            "youtube": "youtube.com",
            "tiktok": "tiktok.com"
        }
        
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza la presenza social dell'azienda e dei competitor"""
        company_name = company_data.get("company_name", "")
        if not company_name:
            return {"error": "Nome azienda non fornito"}
        
        self.log_progress(f"Analizzando presenza social di {company_name}...")
        
        results = {}
        
        # 1. Trova profili social dell'azienda principale
        company_social = self._find_company_social_profiles(company_name)
        results["company_social"] = company_social
        
        # 2. Analizza ogni profilo social trovato
        social_analytics = {}
        for platform, profile_data in company_social.items():
            if profile_data.get("url"):
                analytics = self._analyze_social_profile(platform, profile_data["url"])
                social_analytics[platform] = analytics
        
        results["social_analytics"] = social_analytics
        
        # 3. Analizza competitor social (se disponibili)
        competitors = company_data.get("competitors", [])
        competitor_social = {}
        
        for competitor in competitors[:3]:  # Primi 3 competitor
            comp_name = competitor.get("name", "")
            if comp_name:
                comp_social = self._find_company_social_profiles(comp_name)
                competitor_social[comp_name] = comp_social
        
        results["competitor_social"] = competitor_social
        
        # 4. Confronto social con competitor
        social_comparison = self._compare_social_presence(
            results["social_analytics"], 
            competitor_social
        )
        results["social_comparison"] = social_comparison
        
        return results
    
    def _find_company_social_profiles(self, company_name: str) -> Dict[str, Any]:
        """Trova i profili social dell'azienda"""
        social_profiles = {}
        
        for platform, domain in self.social_platforms.items():
            self.log_progress(f"Cercando profilo {platform} per {company_name}")
            
            # Cerca tramite Google usando Serper se disponibile
            if hasattr(self, 'api_config') and self.api_config.serper_api_key:
                profile = self._search_social_with_serper(company_name, platform)
            else:
                profile = self._search_social_direct(company_name, platform)
            
            if profile:
                social_profiles[platform] = profile
        
        return social_profiles
    
    def _search_social_with_serper(self, company_name: str, platform: str) -> Dict[str, Any]:
        """Cerca profilo social usando Serper"""
        if not self.api_config.serper_api_key:
            return {}
        
        query = f"site:{self.social_platforms[platform]} {company_name}"
        
        headers = {
            "X-API-KEY": self.api_config.serper_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "gl": "it",
            "hl": "it",
            "num": 5
        }
        
        try:
            response = requests.post(
                "https://google.serper.dev/search", 
                headers=headers, 
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if "organic" in data and len(data["organic"]) > 0:
                first_result = data["organic"][0]
                return {
                    "url": first_result.get("link", ""),
                    "title": first_result.get("title", ""),
                    "description": first_result.get("snippet", ""),
                    "found_via": "serper"
                }
        except Exception as e:
            self.log_progress(f"Errore ricerca {platform}: {str(e)}", "error")
        
        return {}
    
    def _search_social_direct(self, company_name: str, platform: str) -> Dict[str, Any]:
        """Cerca profilo social direttamente (fallback)"""
        # Questa è una implementazione semplificata
        # In un ambiente reale, potresti usare le API specifiche delle piattaforme
        
        possible_urls = [
            f"https://www.{self.social_platforms[platform]}/{company_name.lower().replace(' ', '')}",
            f"https://www.{self.social_platforms[platform]}/{company_name.lower().replace(' ', '.')}",
            f"https://www.{self.social_platforms[platform]}/{company_name.lower().replace(' ', '_')}"
        ]
        
        for url in possible_urls:
            try:
                response = self.make_request(url, timeout=10)
                if response.status_code == 200:
                    return {
                        "url": url,
                        "title": f"{company_name} su {platform.title()}",
                        "description": f"Profilo {platform} di {company_name}",
                        "found_via": "direct"
                    }
            except:
                continue
        
        return {}
    
    def _analyze_social_profile(self, platform: str, url: str) -> Dict[str, Any]:
        """Analizza un profilo social specifico"""
        self.log_progress(f"Analizzando profilo {platform}: {url}")
        
        try:
            # Usa user agent diverso per ogni piattaforma
            headers = {
                "User-Agent": self.app_config.user_agents[0],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "it-IT,it;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Analizza in base alla piattaforma
            if platform == "facebook":
                return self._analyze_facebook_profile(soup, url)
            elif platform == "instagram":
                return self._analyze_instagram_profile(soup, url)
            elif platform == "linkedin":
                return self._analyze_linkedin_profile(soup, url)
            elif platform == "twitter":
                return self._analyze_twitter_profile(soup, url)
            elif platform == "youtube":
                return self._analyze_youtube_profile(soup, url)
            elif platform == "tiktok":
                return self._analyze_tiktok_profile(soup, url)
            else:
                return self._analyze_generic_profile(soup, url)
                
        except Exception as e:
            self.log_progress(f"Errore analisi {platform}: {str(e)}", "error")
            return {"error": str(e), "platform": platform, "url": url}
    
    def _analyze_facebook_profile(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analizza profilo Facebook"""
        data = {
            "platform": "facebook",
            "url": url,
            "followers": 0,
            "likes": 0,
            "posts_count": 0,
            "page_info": {},
            "recent_posts": []
        }
        
        # Cerca meta tag per informazioni
        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            if tag.get("property") == "og:title":
                data["page_info"]["title"] = tag.get("content", "")
            elif tag.get("property") == "og:description":
                data["page_info"]["description"] = tag.get("content", "")
        
        # Cerca informazioni sui follower nel testo
        page_text = soup.get_text()
        
        # Pattern per trovare numeri di follower/like
        follower_patterns = [
            r"(\d+(?:\.\d+)?[KMB]?)\s*(?:follower|seguaci)",
            r"(\d+(?:\.\d+)?[KMB]?)\s*(?:mi piace|like)",
            r"(\d+(?:,\d+)*)\s*(?:follower|seguaci|mi piace|like)"
        ]
        
        for pattern in follower_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                data["followers"] = self._parse_social_number(matches[0])
                break
        
        return data
    
    def _analyze_instagram_profile(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analizza profilo Instagram"""
        data = {
            "platform": "instagram",
            "url": url,
            "followers": 0,
            "following": 0,
            "posts": 0,
            "engagement_rate": 0,
            "profile_info": {}
        }
        
        # Cerca script JSON con dati del profilo
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                json_data = json.loads(script.string)
                if isinstance(json_data, dict) and "interactionStatistic" in json_data:
                    for stat in json_data["interactionStatistic"]:
                        if stat.get("interactionType") == "http://schema.org/FollowAction":
                            data["followers"] = stat.get("userInteractionCount", 0)
            except:
                continue
        
        # Cerca informazioni nel testo della pagina
        page_text = soup.get_text()
        
        # Pattern per Instagram
        patterns = {
            "followers": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:follower)",
            "following": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:seguiti|following)",
            "posts": r"(\d+(?:,\d+)*)\s*(?:post)"
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                data[key] = self._parse_social_number(matches[0])
        
        return data
    
    def _analyze_linkedin_profile(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analizza profilo LinkedIn"""
        data = {
            "platform": "linkedin",
            "url": url,
            "followers": 0,
            "employees": 0,
            "company_info": {},
            "industry": ""
        }
        
        # Cerca informazioni specifiche di LinkedIn
        page_text = soup.get_text()
        
        # Pattern per LinkedIn
        patterns = {
            "followers": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:follower|seguaci)",
            "employees": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:dipendenti|employees)"
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                data[key] = self._parse_social_number(matches[0])
        
        return data
    
    def _analyze_twitter_profile(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analizza profilo Twitter"""
        data = {
            "platform": "twitter",
            "url": url,
            "followers": 0,
            "following": 0,
            "tweets": 0,
            "profile_info": {}
        }
        
        # Twitter è più complesso da analizzare senza API
        # Implementazione base
        page_text = soup.get_text()
        
        patterns = {
            "followers": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:Follower)",
            "following": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:Following|Seguiti)",
            "tweets": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:Tweet)"
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                data[key] = self._parse_social_number(matches[0])
        
        return data
    
    def _analyze_youtube_profile(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analizza canale YouTube"""
        data = {
            "platform": "youtube",
            "url": url,
            "subscribers": 0,
            "views": 0,
            "videos": 0,
            "channel_info": {}
        }
        
        # Cerca meta tag specifici di YouTube
        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            if tag.get("property") == "og:title":
                data["channel_info"]["title"] = tag.get("content", "")
            elif tag.get("property") == "og:description":
                data["channel_info"]["description"] = tag.get("content", "")
        
        # Cerca informazioni sui subscriber
        page_text = soup.get_text()
        
        patterns = {
            "subscribers": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:iscritti|subscriber)",
            "views": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:visualizzazioni|views)",
            "videos": r"(\d+(?:,\d+)*)\s*(?:video)"
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                data[key] = self._parse_social_number(matches[0])
        
        return data
    
    def _analyze_tiktok_profile(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analizza profilo TikTok"""
        data = {
            "platform": "tiktok",
            "url": url,
            "followers": 0,
            "following": 0,
            "likes": 0,
            "videos": 0
        }
        
        # TikTok è molto dinamico, implementazione base
        page_text = soup.get_text()
        
        patterns = {
            "followers": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:Follower)",
            "following": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:Following)",
            "likes": r"(\d+(?:\.\d+)?[KMB]?)\s*(?:Like)"
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                data[key] = self._parse_social_number(matches[0])
        
        return data
    
    def _analyze_generic_profile(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analizza profilo generico"""
        return {
            "platform": "generic",
            "url": url,
            "title": soup.title.string if soup.title else "",
            "description": soup.find("meta", attrs={"name": "description"})
        }
    
    def _parse_social_number(self, number_str: str) -> int:
        """Converte stringhe con K/M/B in numeri"""
        if not number_str:
            return 0
        
        # Rimuove spazi e virgole
        number_str = number_str.replace(",", "").replace(" ", "").upper()
        
        # Converte K/M/B
        if number_str.endswith("K"):
            return int(float(number_str[:-1]) * 1000)
        elif number_str.endswith("M"):
            return int(float(number_str[:-1]) * 1000000)
        elif number_str.endswith("B"):
            return int(float(number_str[:-1]) * 1000000000)
        else:
            try:
                return int(float(number_str))
            except ValueError:
                return 0
    
    def _compare_social_presence(self, company_social: Dict, competitor_social: Dict) -> Dict[str, Any]:
        """Confronta la presenza social con i competitor"""
        comparison = {
            "total_platforms": len(company_social),
            "competitor_platforms": {},
            "platform_comparison": {},
            "recommendations": []
        }
        
        # Conta piattaforme per competitor
        for comp_name, comp_data in competitor_social.items():
            comparison["competitor_platforms"][comp_name] = len(comp_data)
        
        # Confronta ogni piattaforma
        for platform in self.social_platforms.keys():
            if platform in company_social:
                company_data = company_social[platform]
                competitor_data = []
                
                # Raccoglie dati competitor per questa piattaforma
                for comp_name, comp_social in competitor_social.items():
                    if platform in comp_social:
                        competitor_data.append(comp_social[platform])
                
                comparison["platform_comparison"][platform] = {
                    "company": company_data,
                    "competitors": competitor_data,
                    "competitive_position": self._calculate_competitive_position(
                        company_data, competitor_data
                    )
                }
        
        # Genera raccomandazioni
        comparison["recommendations"] = self._generate_social_recommendations(
            company_social, competitor_social
        )
        
        return comparison
    
    def _calculate_competitive_position(self, company_data: Dict, competitor_data: List[Dict]) -> str:
        """Calcola la posizione competitiva sui social"""
        if not competitor_data:
            return "Nessun competitor trovato"
        
        company_followers = company_data.get("followers", 0)
        competitor_followers = [comp.get("followers", 0) for comp in competitor_data]
        
        if not competitor_followers:
            return "Dati insufficienti"
        
        avg_competitor_followers = sum(competitor_followers) / len(competitor_followers)
        
        if company_followers > avg_competitor_followers * 1.5:
            return "Leader"
        elif company_followers > avg_competitor_followers:
            return "Sopra la media"
        elif company_followers > avg_competitor_followers * 0.5:
            return "Nella media"
        else:
            return "Sotto la media"
    
    def _generate_social_recommendations(self, company_social: Dict, competitor_social: Dict) -> List[str]:
        """Genera raccomandazioni per i social media"""
        recommendations = []
        
        # Piattaforme mancanti
        company_platforms = set(company_social.keys())
        competitor_platforms = set()
        
        for comp_data in competitor_social.values():
            competitor_platforms.update(comp_data.keys())
        
        missing_platforms = competitor_platforms - company_platforms
        
        if missing_platforms:
            recommendations.append(
                f"Considera di aprire profili su: {', '.join(missing_platforms)}"
            )
        
        # Analizza performance per piattaforma
        for platform, data in company_social.items():
            followers = data.get("followers", 0)
            if followers < 1000:
                recommendations.append(
                    f"Aumenta i follower su {platform} - attualmente sotto i 1000"
                )
        
        return recommendations