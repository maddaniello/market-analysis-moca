# agents/__init__.py
"""
Marketing Analyzer - Agents Package

Questo package contiene tutti gli agenti AI per l'analisi marketing:
- SEMRushAgent: Analisi SEO e competitor tramite SEMRush
- SerperAgent: Ricerca online tramite Serper.dev
- SocialAgent: Analisi social media
- CompanyAgent: Raccolta dati aziendali ufficiali
- ReportAgent: Generazione report finale
"""

from .base_agent import BaseAgent
from .semrush_agent import SEMRushAgent
from .serper_agent import SerperAgent
from .social_agent import SocialAgent
from .company_agent import CompanyAgent
from .report_agent import ReportAgent

__all__ = [
    'BaseAgent',
    'SEMRushAgent', 
    'SerperAgent',
    'SocialAgent',
    'CompanyAgent',
    'ReportAgent'
]

__version__ = '1.0.0'

# utils/__init__.py
"""
Marketing Analyzer - Utils Package

Utilities per validazione, processamento dati e web scraping.
"""

from .validators import InputValidator
from .data_processor import DataProcessor

__all__ = [
    'InputValidator',
    'DataProcessor'
]