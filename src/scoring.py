def calculate_dimension_score(answers, dimension_data):
    """
    Calculates the weighted score for a single dimension (0-100).
    answers: list of selected scores [1, 5, ...] corresponding to questions.
    dimension_data: dict containing questions and their weights.
    """
    total_weight = 0
    weighted_sum = 0
    
    questions = dimension_data.get('questions', [])
    
    # If answers list is shorter than questions (e.g. FMCG not answered), we slice
    # But usually answers should match index. 
    # Safety check:
    limit = min(len(answers), len(questions))
    
    for i in range(limit):
        q = questions[i]
        w = q.get('weight', 1.0)
        
        # Dynamic max score detection for proper normalization (supports 1-5, 0-100, etc.)
        max_q_score = max([opt.get('score', 5) for opt in q.get('options', [])]) if q.get('options') else 5
        
        weighted_sum += answers[i] * w
        total_weight += w * max_q_score 
        
    if total_weight == 0:
        return 0
        
    # Standard normalization
    normalized_score = (weighted_sum / total_weight) * 100
    
    # --- GOVERNANCE SPECIFIC LOGIC (AI Act) ---
    # Apply penalty for high-risk sectors if Governance score is calculated
    dim_id = dimension_data.get('id', '')
    if dim_id == 'governance':
        # Multiplier: Higher means HARDER to get good score (Regulated sectors)
        multipliers = {
            "Finance": 1.2,       # High Risk
            "Manufacturing": 1.1, # Medium Risk (Safety components)
            "FMCG": 1.0, 
            "Retail": 1.0,
            "General": 1.0
        }
        # We need sector passed down, but for now let's assume standard if not available
        # To fix this properly, I will update assessment.py to pass sector, 
        # but calculate_dimension_score signature needs to change.
        # Alternatively, we can apply this in assessment.py wrapper.
        pass # Moving logic to assessment.py wrapper to avoid breaking signature widely
        
    return round(normalized_score, 1)

def calculate_governance_score_specific(answers, dimension_data, sector="General"):
    """
    Specific scoring for Governance with AI Act sector penalties.
    """
    raw_score = calculate_dimension_score(answers, dimension_data)
    
    multipliers = {
        "Finance": 1.15,      # Strict
        "Manufacturing": 1.1, # Safety checks
        "FMCG": 1.0,
        "Retail": 1.0,
        "General": 1.0
    }
    impact = multipliers.get(sector, 1.0)
    
    # Reduce score based on regulatory impact (Harder to reach 100%)
    final_score = raw_score / impact
    return min(100, max(0, final_score))

def get_readiness_level(total_score, lang="it"):
    """
    Returns the maturity level based on standard models.
    Levels: Ad-hoc (0-25), Opportunistic (26-50), Systematic (51-75), Transformational (76-100)
    """
    # Defensive check: if lang is None or weird, default to 'it'
    safe_lang = lang.lower() if lang else "it"
    
    if safe_lang == "en":
        if total_score < 25:
            return "Ad-hoc", "Focus on basics: Data collection and pilot experiments."
        elif total_score < 50:
            return "Opportunistic", "Structure your processes and define a clear strategy."
        elif total_score < 75:
            return "Systematic", "Scale up! You have good foundations, aim for integration."
        else:
            return "Transformational", "AI is native. Focus on innovation and governance."
    else:
        # Default to ITALIAN for 'it', 'IT', or any other unhandled code
        if total_score < 25:
            return "Iniziale / Ad-hoc", "Focus sulle basi: Digitalizzazione dati ed esperimenti pilota."
        elif total_score < 50:
            return "Opportunistico", "Struttura i processi e definisci una strategia chiara."
        elif total_score < 75:
            return "Sistematico", "Scala! Hai buone basi, punta all'integrazione dei sistemi."
        else:
            return "Trasformativo", "L'IA è nativa. Focus su innovazione e governance etica."

def get_detailed_recommendations(results, lang="it"):
    """
    Generates specific suggestions for EACH dimension based on its score.
    """
    suggestions = []
    
    # Text Mapping
    text_map = {
        "it": {
            "data": ["Dati", 
                     "Governance Minima", "Manca una 'source of truth'. Avvia un censimento dei dati.",
                     "Qualità del Dato", "I dati ci sono ma non sono puliti. Implementa controlli di qualità automatici."],
            "process": ["Processi", 
                        "Mappatura", "Processi non documentati non sono automatizzabili. Inizia a mapparli (BPMN).",
                        "Automazione", "Identifica 3 colli di bottiglia e avvia un pilota di RPA."],
            "team": ["Team & Cultura", 
                     "Formazione", "Il team non è pronto. Avvia corsi di alfabetizzazione sui dati (Data Literacy).",
                     "Leadership", "Manca la spinta dall'alto. Organizza un workshop strategico per l'Exec Team."],
            "strategy": ["Strategia", 
                         "Business Case", "L'IA è vista come costo. Definisci il ROI atteso per ogni progetto.",
                         "Roadmap", "Manca una visione a lungo termine. Crea una roadmap a 12-24 mesi."],
            "infrastructure": ["Infrastruttura",
                               "Cloud", "Sistemi legacy bloccano l'innovazione. Valuta migrazione al Cloud.",
                               "Integrazione", "I sistemi non parlano tra loro. Crea API layer."],
            "ethics": ["Etica & Governance",
                       "Compliance", "Rischi normativi (AI Act). Consulta un legale.",
                       "Framework", "Definisci linee guida etiche per l'uso dell'IA."]
        },
        "en": {
            "data": ["Data", "Governance", "Start data census.", "Quality", "Implement auto-quality checks."],
            "process": ["Processes", "Mapping", "Map your workflows.", "Automation", "Start RPA pilot."],
            "team": ["Team", "Training", "Start Data Literacy program.", "Leadership", "Exec workshop needed."],
            "strategy": ["Strategy", "Business Case", "Define ROI.", "Roadmap", "Create 12-month roadmap."],
            "infrastructure": ["Infrastructure", "Cloud", "Legacy systems blocking. Move to Cloud.", "Integration", "Create API layer."],
            "ethics": ["Ethics", "Compliance", "Check EU AI Act.", "Framework", "Define ethical guidelines."]
        }
    }
    
    t = text_map.get(lang, text_map['en'])
    
    # Iterate over all dimensions in results
    for dim_id, data in results['dimensions'].items():
        score = data['score']
        # Generic fallback key if dim_id not in map (e.g. fmcg)
        txt = t.get(dim_id)
        if not txt: continue 
        
        # logic: Low (<40), Med (<75 only if not low), High(>=75)
        # We append only ONE recommendation per dimension to avoid clutter? 
        # Or both if very low? Let's give priority to the most urgent one.
        if score < 40:
            suggestions.append({"dimension": txt[0], "action": txt[1], "detail": txt[2]})
        elif score < 75:
             suggestions.append({"dimension": txt[0], "action": txt[3], "detail": txt[4]})
        # If High, maybe no suggestion needed or "Maintain"
        
    return suggestions

def calculate_total_score(dimension_results):
    """
    Calculates the weighted total score with normalization.
    dimension_results: list of tuples (score, weight)
    """
    weighted_sum = sum(score * weight for score, weight in dimension_results)
    total_weight = sum(weight for score, weight in dimension_results)
    
    if total_weight == 0: return 0
    
    return weighted_sum / total_weight
