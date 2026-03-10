"""
Configuration file for AI Readiness Assessment Tool
Enhanced version with better organization and extensibility
"""

from typing import Dict, List
from dataclasses import dataclass

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

@dataclass
class AppConfig:
    """Main application configuration."""
    APP_NAME: str = "AI Readiness Assessment Pro"
    VERSION: str = "2.0"
    PAGE_ICON: str = "🤖"
    LAYOUT: str = "wide"
    
    # File paths
    DATA_DIR: str = "data"
    EXAMPLES_DIR: str = "examples"
    BENCHMARKS_FILE: str = "data/benchmarks.json"
    QUESTIONS_FILE: str = "data/questions.json"
    AUDIT_FILE: str = "data/data_audit.json"
    
    # Session limits
    MAX_HISTORY: int = 10
    MAX_COMPARISON: int = 3
    
    # Auto-save settings
    AUTOSAVE_ENABLED: bool = True
    AUTOSAVE_INTERVAL: int = 60  # seconds

# ============================================================================
# SCORING CONFIGURATION
# ============================================================================

DIMENSION_WEIGHTS = {
    "strategy": 1.2,      # Higher weight - strategic vision is critical
    "data": 1.1,          # Data quality is foundational
    "processes": 1.0,     # Standard weight
    "team": 1.0,          # Standard weight
    "infrastructure": 0.9, # Slightly lower - can be acquired
    "ethics": 1.1         # Important for compliance
}

SCORE_LEVELS = {
    "low": {
        "threshold": (0, 40),
        "label_it": "Consapevolezza Iniziale",
        "label_en": "Initial Awareness",
        "color": "#dc3545",
        "icon": "⚠️"
    },
    "medium": {
        "threshold": (40, 70),
        "label_it": "Maturità in Sviluppo",
        "label_en": "Developing Maturity",
        "color": "#ffc107",
        "icon": "📈"
    },
    "high": {
        "threshold": (70, 100),
        "label_it": "Leadership Digitale",
        "label_en": "Digital Leadership",
        "color": "#28a745",
        "icon": "🚀"
    }
}

# ============================================================================
# SECTOR BENCHMARKS (Fallback)
# ============================================================================

DEFAULT_BENCHMARKS = {
    "General": {
        "strategy": 50,
        "data": 50,
        "processes": 50,
        "team": 50,
        "infrastructure": 50,
        "ethics": 50
    },
    "Manufacturing": {
        "strategy": 55,
        "data": 60,
        "processes": 65,
        "team": 50,
        "infrastructure": 55,
        "ethics": 50
    },
    "Finance": {
        "strategy": 70,
        "data": 75,
        "processes": 65,
        "team": 60,
        "infrastructure": 70,
        "ethics": 80
    },
    "FMCG": {
        "strategy": 60,
        "data": 65,
        "processes": 60,
        "team": 55,
        "infrastructure": 60,
        "ethics": 65
    },
    "Retail": {
        "strategy": 55,
        "data": 60,
        "processes": 60,
        "team": 50,
        "infrastructure": 55,
        "ethics": 60
    },
    "Healthcare": {
        "strategy": 60,
        "data": 70,
        "processes": 55,
        "team": 55,
        "infrastructure": 60,
        "ethics": 85
    },
    "Technology": {
        "strategy": 75,
        "data": 80,
        "processes": 70,
        "team": 70,
        "infrastructure": 80,
        "ethics": 70
    }
}

# ============================================================================
# UI THEME CONFIGURATION
# ============================================================================

THEME_COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

GRADIENT_STYLES = {
    "primary": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "success": "linear-gradient(135deg, #56ab2f 0%, #a8e063 100%)",
    "warning": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    "info": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
}

# ============================================================================
# EXPORT SETTINGS
# ============================================================================

EXPORT_FORMATS = {
    "pdf": {
        "extension": ".pdf",
        "mime": "application/pdf",
        "icon": "📄"
    },
    "excel": {
        "extension": ".xlsx",
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "icon": "📊"
    },
    "json": {
        "extension": ".json",
        "mime": "application/json",
        "icon": "💾"
    },
    "csv": {
        "extension": ".csv",
        "mime": "text/csv",
        "icon": "📋"
    }
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

VALIDATION_RULES = {
    "min_questions_per_dimension": 3,
    "max_questions_per_dimension": 10,
    "min_options_per_question": 2,
    "max_options_per_question": 5,
    "score_range": (0, 100)
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    "history": True,
    "comparison": True,
    "what_if_simulator": True,
    "benchmarking": True,
    "multi_export": True,
    "auto_save": True,
    "case_studies": True,
    "data_audit": True,
    "recommendations": True
}

# ============================================================================
# RECOMMENDATION TEMPLATES
# ============================================================================

RECOMMENDATION_TEMPLATES = {
    "strategy": {
        "low": {
            "action_it": "Definire una strategia AI chiara",
            "action_en": "Define a clear AI strategy",
            "detail_it": "Creare un business case formale con ROI attesi e roadmap di implementazione.",
            "detail_en": "Create a formal business case with expected ROI and implementation roadmap."
        },
        "medium": {
            "action_it": "Rafforzare il commitment organizzativo",
            "action_en": "Strengthen organizational commitment",
            "detail_it": "Coinvolgere il top management e allocare budget dedicato per iniziative AI.",
            "detail_en": "Engage top management and allocate dedicated budget for AI initiatives."
        }
    },
    "data": {
        "low": {
            "action_it": "Avviare un programma di Data Governance",
            "action_en": "Start a Data Governance program",
            "detail_it": "Catalogare i dati disponibili, migliorare la qualità e creare policy di accesso.",
            "detail_en": "Catalog available data, improve quality, and create access policies."
        },
        "medium": {
            "action_it": "Implementare una Data Platform centralizzata",
            "action_en": "Implement a centralized Data Platform",
            "detail_it": "Investire in infrastruttura per raccolta, storage e processing dati in tempo reale.",
            "detail_en": "Invest in infrastructure for real-time data collection, storage, and processing."
        }
    },
    "processes": {
        "low": {
            "action_it": "Mappare i processi candidati all'automazione",
            "action_en": "Map processes suitable for automation",
            "detail_it": "Identificare processi ripetitivi ad alto volume e basso valore aggiunto.",
            "detail_en": "Identify repetitive, high-volume, low-value processes."
        },
        "medium": {
            "action_it": "Avviare progetti pilota di automazione",
            "action_en": "Launch automation pilot projects",
            "detail_it": "Testare RPA o AI su processi selezionati per dimostrare quick wins.",
            "detail_en": "Test RPA or AI on selected processes to demonstrate quick wins."
        }
    },
    "team": {
        "low": {
            "action_it": "Lanciare programmi di upskilling AI",
            "action_en": "Launch AI upskilling programs",
            "detail_it": "Formare il personale esistente su fondamentali di AI, data literacy e tool.",
            "detail_en": "Train existing staff on AI fundamentals, data literacy, and tools."
        },
        "medium": {
            "action_it": "Assumere o formare AI specialists",
            "action_en": "Hire or train AI specialists",
            "detail_it": "Creare un team dedicato con competenze in ML, data science e AI engineering.",
            "detail_en": "Create a dedicated team with ML, data science, and AI engineering skills."
        }
    },
    "infrastructure": {
        "low": {
            "action_it": "Valutare migration al Cloud",
            "action_en": "Evaluate Cloud migration",
            "detail_it": "Sfruttare scalabilità e servizi AI managed per ridurre complessità infrastrutturale.",
            "detail_en": "Leverage scalability and managed AI services to reduce infrastructure complexity."
        },
        "medium": {
            "action_it": "Implementare architettura AI-ready",
            "action_en": "Implement AI-ready architecture",
            "detail_it": "Adottare MLOps, API-first design e container orchestration.",
            "detail_en": "Adopt MLOps, API-first design, and container orchestration."
        }
    },
    "ethics": {
        "low": {
            "action_it": "Definire policy etiche per l'AI",
            "action_en": "Define AI ethics policies",
            "detail_it": "Creare linee guida su fairness, trasparenza, privacy e accountability.",
            "detail_en": "Create guidelines on fairness, transparency, privacy, and accountability."
        },
        "medium": {
            "action_it": "Implementare AI Risk Management",
            "action_en": "Implement AI Risk Management",
            "detail_it": "Stabilire processi di audit, testing per bias e compliance AI Act.",
            "detail_en": "Establish audit processes, bias testing, and AI Act compliance."
        }
    }
}

# ============================================================================
# ANALYTICS & METRICS
# ============================================================================

METRICS_CONFIG = {
    "track_completion_time": True,
    "track_revision_count": True,
    "track_dimension_changes": True,
    "track_export_formats": True
}

# ============================================================================
# LOCALIZATION SETTINGS
# ============================================================================

SUPPORTED_LANGUAGES = ["it", "en"]
DEFAULT_LANGUAGE = "en"

# ============================================================================
# API ENDPOINTS (Future Integration)
# ============================================================================

API_CONFIG = {
    "enabled": False,
    "base_url": "https://api.example.com",
    "version": "v1",
    "timeout": 30,
    "retry_attempts": 3
}
