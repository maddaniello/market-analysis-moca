import json
import pandas as pd
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

class DataProcessor:
    """Classe per processare e normalizzare i dati raccolti"""
    
    @staticmethod
    def normalize_company_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizza i dati dell'azienda"""
        normalized = {
            "company_name": "",
            "website": "",
            "vat_number": "",
            "fiscal_code": "",
            "legal_form": "",
            "headquarters": "",
            "sector": "",
            "employees": 0,
            "revenue": "",
            "founding_date": "",
            "contact_info": {}
        }
        
        # Normalizza nome azienda
        if "company_name" in raw_data:
            normalized["company_name"] = DataProcessor._clean_company_name(
                raw_data["company_name"]
            )
        
        # Normalizza sito web
        if "website" in raw_data:
            normalized["website"] = DataProcessor._normalize_url(
                raw_data["website"]
            )
        
        # Normalizza partita IVA
        if "vat_number" in raw_data:
            normalized["vat_number"] = DataProcessor._normalize_vat_number(
                raw_data["vat_number"]
            )
        
        # Normalizza numero dipendenti
        if "employees" in raw_data:
            normalized["employees"] = DataProcessor._extract_number(
                raw_data["employees"]
            )
        
        # Copia altri campi se presenti
        for field in ["fiscal_code", "legal_form", "headquarters", "sector", 
                     "revenue", "founding_date", "contact_info"]:
            if field in raw_data:
                normalized[field] = raw_data[field]
        
        return normalized
    
    @staticmethod
    def normalize_seo_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizza i dati SEO"""
        normalized = {
            "organic_keywords": 0,
            "organic_traffic": 0,
            "backlinks": 0,
            "authority_score": 0,
            "top_keywords": [],
            "competitor_domains": [],
            "paid_keywords": 0
        }
        
        # Estrae dati organici
        if "organic_traffic" in raw_data:
            organic = raw_data["organic_traffic"]
            normalized["organic_traffic"] = DataProcessor._extract_number(
                organic.get("organic_traffic", 0)
            )
        
        # Estrae dati keyword
        if "keywords" in raw_data:
            keywords = raw_data["keywords"]
            normalized["organic_keywords"] = keywords.get("total_keywords", 0)
            normalized["top_keywords"] = keywords.get("keyword_list", [])[:10]
        
        # Estrae dati backlink
        if "backlinks" in raw_data:
            backlinks = raw_data["backlinks"]
            normalized["backlinks"] = backlinks.get("total_backlinks", 0)
            normalized["authority_score"] = backlinks.get("authority_score", 0)
        
        # Estrae competitor
        if "competitors" in raw_data:
            competitors = raw_data["competitors"]
            if isinstance(competitors, list):
                normalized["competitor_domains"] = [
                    comp.get("domain", "") for comp in competitors[:10]
                ]
        
        return normalized
    
    @staticmethod
    def normalize_social_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizza i dati social"""
        normalized = {
            "total_followers": 0,
            "active_platforms": 0,
            "platform_details": {},
            "engagement_score": 0,
            "social_urls": {}
        }
        
        if "social_analytics" in raw_data:
            analytics = raw_data["social_analytics"]
            total_followers = 0
            active_platforms = 0
            
            for platform, data in analytics.items():
                if isinstance(data, dict) and not data.get("error"):
                    active_platforms += 1
                    
                    # Normalizza follower count
                    followers = data.get("followers", 0) or data.get("subscribers", 0)
                    followers = DataProcessor._extract_number(followers)
                    total_followers += followers
                    
                    # Salva dettagli piattaforma
                    normalized["platform_details"][platform] = {
                        "followers": followers,
                        "url": data.get("url", ""),
                        "engagement": data.get("engagement_rate", 0)
                    }
                    
                    # Salva URL
                    if data.get("url"):
                        normalized["social_urls"][platform] = data["url"]
            
            normalized["total_followers"] = total_followers
            normalized["active_platforms"] = active_platforms
            
            # Calcola engagement score
            if active_platforms > 0:
                normalized["engagement_score"] = DataProcessor._calculate_engagement_score(
                    normalized["platform_details"]
                )
        
        return normalized
    
    @staticmethod
    def create_competitor_matrix(competitors_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Crea una matrice dei competitor per analisi comparativa"""
        
        if not competitors_data:
            return pd.DataFrame()
        
        # Prepara dati per DataFrame
        matrix_data = []
        
        for comp in competitors_data:
            row = {
                "Nome": comp.get("name", ""),
                "Dominio": comp.get("domain", ""),
                "Settore": comp.get("sector", ""),
                "Dipendenti": DataProcessor._extract_number(comp.get("employees", 0)),
                "Keywords_SEO": comp.get("se_keywords", 0),
                "Traffico_Organico": comp.get("organic_traffic", 0),
                "Social_Followers": DataProcessor._extract_number(comp.get("social_followers", 0)),
                "Authority_Score": comp.get("authority_score", 0)
            }
            matrix_data.append(row)
        
        df = pd.DataFrame(matrix_data)
        
        # Ordina per authority score decrescente
        if "Authority_Score" in df.columns and not df["Authority_Score"].empty:
            df = df.sort_values("Authority_Score", ascending=False)
        
        return df
    
    @staticmethod
    def calculate_market_position_score(company_data: Dict[str, Any], 
                                      competitors_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcola il punteggio di posizione di mercato"""
        
        scores = {
            "seo_position": 0,
            "social_position": 0,
            "size_position": 0,
            "overall_position": 0,
            "percentile": 0
        }
        
        if not competitors_data:
            return scores
        
        # Estrae metriche azienda
        company_keywords = company_data.get("organic_keywords", 0)
        company_followers = company_data.get("total_followers", 0)  
        company_employees = company_data.get("employees", 0)
        
        # Estrae metriche competitor
        comp_keywords = [DataProcessor._extract_number(c.get("se_keywords", 0)) for c in competitors_data]
        comp_followers = [DataProcessor._extract_number(c.get("social_followers", 0)) for c in competitors_data]
        comp_employees = [DataProcessor._extract_number(c.get("employees", 0)) for c in competitors_data]
        
        # Calcola posizioni relative
        scores["seo_position"] = DataProcessor._calculate_percentile(
            company_keywords, comp_keywords
        )
        
        scores["social_position"] = DataProcessor._calculate_percentile(
            company_followers, comp_followers
        )
        
        scores["size_position"] = DataProcessor._calculate_percentile(
            company_employees, comp_employees
        )
        
        # Posizione complessiva (media pesata)
        scores["overall_position"] = (
            scores["seo_position"] * 0.4 +
            scores["social_position"] * 0.3 +
            scores["size_position"] * 0.3
        )
        
        scores["percentile"] = scores["overall_position"]
        
        return scores
    
    @staticmethod
    def generate_insights_summary(all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un riassunto degli insights principali"""
        
        summary = {
            "strengths": [],
            "weaknesses": [], 
            "opportunities": [],
            "threats": [],
            "key_metrics": {},
            "recommendations": []
        }
        
        # Analizza punti di forza
        seo_data = all_data.get("normalized_seo", {})
        if seo_data.get("organic_keywords", 0) > 500:
            summary["strengths"].append("Forte presenza SEO organica")
        
        if seo_data.get("authority_score", 0) > 50:
            summary["strengths"].append("Buona autorità del dominio")
        
        social_data = all_data.get("normalized_social", {})
        if social_data.get("active_platforms", 0) >= 4:
            summary["strengths"].append("Presenza social diversificata")
        
        # Analizza debolezze
        if seo_data.get("organic_keywords", 0) < 100:
            summary["weaknesses"].append("Presenza SEO limitata")
        
        if social_data.get("total_followers", 0) < 1000:
            summary["weaknesses"].append("Base follower limitata")
        
        # Identifica opportunità
        if seo_data.get("organic_keywords", 0) > 0:
            summary["opportunities"].append("Espansione strategia contenuti SEO")
        
        if social_data.get("active_platforms", 0) < 5:
            summary["opportunities"].append("Espansione su nuove piattaforme social")
        
        # Metriche chiave
        summary["key_metrics"] = {
            "seo_keywords": seo_data.get("organic_keywords", 0),
            "authority_score": seo_data.get("authority_score", 0),
            "social_platforms": social_data.get("active_platforms", 0),
            "total_followers": social_data.get("total_followers", 0)
        }
        
        return summary
    
    # Metodi helper privati
    
    @staticmethod
    def _clean_company_name(name: str) -> str:
        """Pulisce il nome dell'azienda"""
        if not name:
            return ""
        
        # Rimuove caratteri speciali e normalizza
        cleaned = re.sub(r'[^\w\s\.\-&]', '', str(name))
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip().title()
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalizza un URL"""
        if not url:
            return ""
        
        url = str(url).strip().lower()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @staticmethod
    def _normalize_vat_number(vat: str) -> str:
        """Normalizza partita IVA italiana"""
        if not vat:
            return ""
        
        # Rimuove tutto eccetto numeri
        digits_only = re.sub(r'[^\d]', '', str(vat))
        
        # Aggiunge IT se manca
        if len(digits_only) == 11:
            return f"IT{digits_only}"
        
        return vat
    
    @staticmethod
    def _extract_number(value) -> int:
        """Estrae un numero da vari formati"""
        if isinstance(value, (int, float)):
            return int(value)
        
        if not value:
            return 0
        
        # Converte stringhe con K, M, B
        value_str = str(value).upper()
        
        # Rimuove caratteri non numerici eccetto K, M, B, .
        clean_value = re.sub(r'[^\d\.\,KMB]', '', value_str)
        
        if not clean_value:
            return 0
        
        try:
            if clean_value.endswith('K'):
                return int(float(clean_value[:-1]) * 1000)
            elif clean_value.endswith('M'):
                return int(float(clean_value[:-1]) * 1000000)
            elif clean_value.endswith('B'):
                return int(float(clean_value[:-1]) * 1000000000)
            else:
                # Rimuove virgole e converte
                clean_value = clean_value.replace(',', '')
                return int(float(clean_value))
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def _calculate_engagement_score(platform_details: Dict[str, Any]) -> float:
        """Calcola un punteggio di engagement"""
        if not platform_details:
            return 0.0
        
        total_score = 0.0
        platform_count = len(platform_details)
        
        for platform, data in platform_details.items():
            followers = data.get("followers", 0)
            
            # Score basato su numero follower
            if followers > 10000:
                score = 5.0
            elif followers > 5000:
                score = 4.0
            elif followers > 1000:
                score = 3.0
            elif followers > 100:
                score = 2.0
            else:
                score = 1.0
            
            total_score += score
        
        return total_score / platform_count if platform_count > 0 else 0.0
    
    @staticmethod
    def _calculate_percentile(value: float, comparison_values: List[float]) -> float:
        """Calcola il percentile di un valore rispetto a una lista"""
        if not comparison_values:
            return 50.0  # Default al 50° percentile
        
        # Filtra valori validi
        valid_values = [v for v in comparison_values if isinstance(v, (int, float)) and v >= 0]
        
        if not valid_values:
            return 50.0
        
        # Aggiunge il valore dell'azienda
        all_values = valid_values + [value]
        all_values.sort()
        
        # Trova la posizione
        position = all_values.index(value)
        percentile = (position / (len(all_values) - 1)) * 100
        
        return min(100.0, max(0.0, percentile))
    
    @staticmethod
    def export_to_json(data: Dict[str, Any], filename: str) -> bool:
        """Esporta dati in formato JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Errore esportazione JSON: {e}")
            return False
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> bool:
        """Esporta dati in formato CSV"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Errore esportazione CSV: {e}")
            return False