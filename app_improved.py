import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import importlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import base64
from io import BytesIO

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dynamic imports with error handling
try:
    from src import scoring, assessment, report_generator
    importlib.reload(scoring)
    importlib.reload(assessment)
    importlib.reload(report_generator)
except ImportError as e:
    st.error(f"⚠️ Module import error: {e}")
    st.stop()

from src.assessment import run_assessment_v2, load_questions

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Readiness Assessment Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ENHANCED CSS WITH ANIMATIONS
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Score Box Enhanced */
    .score-box {
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 25px;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        animation: fadeIn 0.6s ease-out;
    }
    
    .score-text {
        font-size: 80px !important; 
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .level-text {
        font-size: 32px !important;
        font-weight: 700;
        margin-top: 10px;
        color: #333;
    }
    
    /* Custom Primary Button Color (Yellow Warning) */
    div[data-testid="stSidebar"] button[kind="primary"], div[data-testid="stExpander"] button[kind="primary"] {
        background-color: #ffb703 !important;
        color: #000000 !important;
        border-color: #ffb703 !important;
    }
    div[data-testid="stSidebar"] button[kind="primary"]:hover, div[data-testid="stExpander"] button[kind="primary"]:hover {
        background-color: #fb8500 !important;
        border-color: #fb8500 !important;
    }
    
    /* Dimension Cards Enhanced */
    .dimension-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e0e0e0;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 220px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        position: relative;
        overflow: hidden;
    }
    
    .dimension-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .dimension-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .dimension-card:hover::before {
        transform: scaleX(1);
    }
    
    .dim-icon {
        font-size: 36px;
        margin-bottom: 12px;
        transition: transform 0.3s ease;
    }
    
    .dimension-card:hover .dim-icon {
        transform: scale(1.2);
    }
    
    .dim-title {
        font-weight: 700;
        font-size: 18px;
        color: #333;
        margin-bottom: 8px;
    }
    
    .dim-desc {
        font-size: 16px;
        color: #666;
        line-height: 1.5;
    }
    
    /* Recommendation Card Enhanced */
    .recommendation-card {
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #667eea;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #f0f7ff 0%, #e8f4f8 100%);
        color: #333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        animation: fadeIn 0.4s ease-out;
    }
    
    .recommendation-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .rec-title {
        font-weight: 700;
        color: #667eea;
        font-size: 20px;
        margin-bottom: 10px;
    }
    
    .rec-action {
        font-weight: 600;
        color: #444;
        margin-bottom: 8px;
        font-size: 16px;
    }
    
    /* Progress Bar Enhanced */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Alert Boxes */
    .success-box {
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        margin: 20px 0;
        animation: fadeIn 0.5s ease-out;
    }
    
    .info-box {
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 5px solid #17a2b8;
        margin: 20px 0;
        color: #1a3a3a;
    }
    
    .warning-box {
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
        margin: 20px 0;
    }
    
    /* Button Enhancements */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Sidebar Styling */
    .sidebar-title-custom {
        font-size: 30px !important;
        font-weight: 800 !important;
        margin-top: -20px;
        margin-bottom: 5px;
        line-height: 1.2;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Loading Spinner */
    .loading-spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: 800;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Comparison Table */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    
    .comparison-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }
    
    .comparison-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .comparison-table tr:hover {
        background-color: #f8f9fa;
    }
    
    /* Sidebar uniform section title style */
    .sidebar-section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e0e0e0;
        margin: 4px 0 6px 0;
        letter-spacing: 0.3px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Sidebar Selectbox Cursor - CSS approach, may be overridden */
    div[data-testid="stSidebar"] [data-baseweb="select"],
    div[data-testid="stSidebar"] [data-baseweb="select"] *,
    div[data-testid="stSidebar"] [data-baseweb="select"] > div,
    div[data-testid="stSidebar"] [data-baseweb="select"] svg {
        cursor: pointer !important;
    }

    /* Also target Streamlit's own selectbox wrapper in sidebar */
    div[data-testid="stSidebar"] .stSelectbox div {
        cursor: pointer !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TRANSLATIONS (Enhanced)
# ============================================================================

TRANS = {
    "it": {
        "title": "AI Readiness Assessment Pro", 
        "nav": "Menu",
        "home": "Home",
        "assess": "Assessment",
        "audit": "Data Audit",
        "about": "Informazioni",
        "history": "Cronologia",
        "compare": "Confronta",
        "lang": "💬 Lingua", 
        "examples": "Casi Studio",
        "compare": "Confronta",
        "lang": "💬 Lingua", 
        "examples": "Casi Studio",
        "new": "✨ Nuovo Assessment",
        "export_opt": "📥 Opzioni di Esportazione",
        "compare_not_enough": "Sono necessari almeno 2 assessment salvati. Completa altri assessment!",
        "compare_select": "Seleziona Assessment da Confrontare (max 3)",
        "compare_table": "Comparazione Dettagliata",
        "c_date": "Data", "c_score": "Punteggio Totale", "c_level": "Livello",
        "prog_anal": "Analisi dei Progressi",
        "first_score": "Primo Punteggio", "last_score": "Ultimo Punteggio", "improvement": "Miglioramento",
        "download_comp": "📥 Scarica Dati Confronto",

        "hero_title": "Navigare la Trasformazione: AI Readiness Framework",
        "hero_subtitle": "Uno strumento analitico avanzato per misurare la maturità digitale delle organizzazioni e tracciare la rotta verso l'adozione consapevole dell'Intelligenza Artificiale.",
        "met_dim": "Dimensioni Analizzate",
        "met_bench": "Benchmark Settoriali",
        "met_time": "Tempo Stimato",
        "why_title": "Il Modello: 6 Pilastri della Readiness",
        "why_desc": "L'adozione dell'IA non è solo tecnologia. Questo framework analizza l'organizzazione a 360 gradi:",
        "d1_t": "Strategia", "d1_d": "Visione aziendale, Business Case e investimenti a lungo termine.",
        "d2_t": "Dati", "d2_d": "Qualità, accessibilità, governance e volume dei dati disponibili.",
        "d3_t": "Processi", "d3_d": "Maturità dei workflow e potenziale di automazione.",
        "d4_t": "Team & Cultura", "d4_d": "Competenze interne (upskilling) e apertura al cambiamento.",
        "d5_t": "Infrastruttura", "d5_d": "Stack tecnologico, Cloud readiness e capacità di integrazione.",
        "d6_t": "Etica & Governance", "d6_d": "Compliance (AI Act), privacy e gestione dei rischi.",
        "method_title": "🔎 Metodologia di Scoring",
        "method": "Metodologia",
        "method_text": "Sistema di scoring ponderato basato su 6 dimensioni chiave.",
        "method_p1": "**Normalizzazione**: Ogni risposta ha un peso specifico. Il punteggio finale (0-100) è calcolato algoritmicamente pesando l'importanza di ogni dimensione.",
        "method_p2": "**Benchmarking**: I tuoi risultati vengono confrontati in tempo reale con standard di settore (es. Manufacturing, Finance, Retail) per evidenziare gap competitivi.",
        "cta_title": "Pronto a iniziare?",
        "start_btn": "🚀 Avvia Assessment",
        "audit_btn": "🔎 Data Audit (Preliminare)",
        "cases_title": "📂 Casi Studio Reali",
        "cases_desc": "Esplora come aziende di diversi settori si posizionano. Clicca per caricare un report completo.",
        "case_1": "🏦 Settore Finance (Alto)",
        "case_2": "🏭 Settore Manifatturiero (Medio)",
        "case_3": "🏪 Settore Retail (Basso)",
        
        "score_title": "Punteggio AI Readiness",
        "sector": "Settore",
        "download": "📄 Scarica Report PDF",
        "download_excel": "📊 Esporta Excel",
        "download_json": "💾 Esporta JSON",
        "share": "🔗 Condividi",
        "save": "💾 Salva Assessment",
        "examples": "📂 Casi Studio",
        "new": "— Nessun Caso Studio —",
        "export_opt": "📥 Opzioni di Esportazione",
        "benchmark": "Benchmark",
        "perf_dim": "Performance per Dimensione",
        "assess_intro": "**Istruzioni**: Rispondi a tutte le domande. Le risposte sono obbligatorie per garantire l'accuratezza del modello.",
        "what_if_title": "🔮 What-If Simulator",
        "what_if_sub": "Pianificazione Strategica",
        "what_if_desc": "Simula l'impatto degli investimenti sul tuo punteggio totale.",
        "sim_total": "Punteggio Simulato",
        "error_answ": "⚠️ Rispondi a tutte le domande per procedere.",
        "reset_btn": "🔄 Reset & Riavvia",
        "autosave": "💾 Salvataggio automatico attivo",
        "sync_title": "Sincronizza con la Cache del Browser",
        "sync_info": "La cronologia degli assessment è mantenuta in memoria di sessione. Usa questa funzione per ripristinare i dati dalla memoria locale del browser.",
        "sync_btn": "Ripristina dalla Memoria del Browser",
        "sync_warning": "Nota: questa funzione usa il LocalStorage del browser. I dati sono specifici del dispositivo.",
        "sync_paste": "Contenuto Cache (Incolla qui se la sincronizzazione automatica fallisce)",
        "sync_ok": "✅ Dati ripristinati dalla cache del browser!",
        "sync_cache": "Nessun dato trovato nella cache del browser.",
        
        "rec_title": "💡 Roadmap Strategica",
        "empty_rec": "Ottimo lavoro! Nessuna raccomandazione critica.",
        "all_done": "🎉 Assessment Completato!",
        "audit_title": "Data Audit Checklist",
        "audit_desc": "Check rapido sulla salute dei dati.",
        "audit_score": "Indice Maturità Dati",
        "audit_low": "⚠️ Silos Informativi",
        "audit_low_desc": "La tua organizzazione presenta dati **frammentati e non condivisi** tra i reparti. Questo significa che ogni team lavora con le proprie fonti, rendendo difficile qualsiasi analisi integrata e bloccando l'adozione dell'IA. È necessario affrontare subito una strategia di integrazione dei dati.",
        "audit_med": "📈 Digitalizzazione Reattiva",
        "audit_med_desc": "La tua organizzazione ha intrapreso un percorso di digitalizzazione, ma in modo **non sistematico**: si reagisce alle esigenze, senza una strategia proattiva. Hai basi solide su cui costruire, ma serve un piano strutturato per passare al livello successivo.",
        "audit_high": "🚀 Data Governance Proattiva",
        "audit_high_desc": "Complimenti! La tua organizzazione ha una gestione dei dati **matura e strutturata**, con processi definiti e responsabilità chiare. Sei in una posizione ottimale per avviare o scalare progetti di Intelligenza Artificiale.",
        "audit_cta_low": "💡 Questo risultato suggerisce che esiste un **ampio margine di crescita** nella tua infrastruttura dati. Completa l'AI Readiness Assessment completo per ricevere una roadmap strategica personalizzata.",
        "audit_cta_med": "💡 Il tuo assessment parziale evidenzia aree di miglioramento specifiche. Procedi con l'**AI Readiness Assessment** completo per una valutazione approfondita e un piano d'azione su misura.",
        "audit_cta_high": "💡 La maturità dei tuoi dati è un asset strategico. Esplora il tuo **potenziale AI complessivo** con l'Assessment completo per identificare le dimensioni dove puoi creare ancora più valore.",
        "go_to_assess": "Vai all'Assessment →",
        "about_text": "Sviluppato da Sabrina Rizzi.",
        "contact": "Contatti",
        "history_title": "📊 Cronologia Assessment",
        "history_empty": "Nessun assessment salvato. Completa il tuo primo assessment!",
        "compare_title": "📊 Confronto Assessment",
        "compare_desc": "Confronta fino a 3 assessment per tracciare i progressi",
        "loading": "Caricamento in corso...",
        "error_generic": "Si è verificato un errore. Riprova.",
        "success_save": "✅ Assessment salvato con successo!",
        "confirm_reset": "Sei sicuro di voler resettare? Tutti i dati non salvati andranno persi.",
        "waterfall_title": "📊 Contributo Dimensioni al Punteggio",
        "critical_dims": "🔍 Focus: Dimensioni Chiave",
        "perf_dim": "Punteggio per Dimensione",
        "benchmark": "Benchmark di Settore",
        "what_if_title": "📉 What-If Simulator",
        "what_if_sub": "Pianificazione Strategica",
        "what_if_desc": "Simula l'impatto degli investimenti sul tuo punteggio totale.",
        "choose_options": "Scegli un'opzione",
        "ux_challenge_title": "Design Challenge: UX in contesti a bassa flessibilità grafica",
        "ux_challenge_text": "Per questo progetto ho scelto Streamlit per la sua efficienza tecnica, accettando la sfida di ottimizzare la User Experience entro i limiti strutturali del framework. Mi sono concentrata sulla Gerarchia dell'Informazione e sulla Riduzione del Carico Cognitivo, dividendo l'assessment in moduli logici e utilizzando il Data Storytelling visivo (Radar Charts) per rendere i risultati immediatamente azionabili dal management.",
        "about_note": "🎓 **Nota sul Progetto**: Questo tool è realizzato a scopo **formativo e di portfolio personale**, come dimostrazione pratica di competenze in progettazione software, UX, analisi dei dati e compliance normativa. I risultati dell'assessment sono indicativi e pensati per stimolare riflessione strategica.",
        "about_vision_title": "🚀 Visione del Progetto",
        "about_vision_text": "L'**AI Readiness Assessment Tool** è progettato per aiutare le organizzazioni a mappare il proprio percorso di trasformazione digitale. Non si limita a misurare la capacità tecnica, ma valuta l'ecosistema aziendale nel suo complesso, garantendo che l'adozione dell'IA sia **etica, sicura e strategica**.",
        "about_methodology_title": "🏗️ Metodologia e Scoring",
        "about_6pillars_title": "#### Framework a 6 Pilastri",
        "about_6pillars_desc": "Il tool analizza sei dimensioni critiche, ognuna con un peso specifico basato sull'impatto strategico:\n1. **Strategia**: Allineamento agli obiettivi di business.\n2. **Dati**: Qualità e architettura informativa.\n3. **Processi**: Potenziale di automazione dei workflow.\n4. **Team & Cultura**: Competenze e gestione del cambiamento.\n5. **Infrastruttura**: Prontezza tecnologica e scalabilità.\n6. **Governance & Etica**: Conformità normativa (AI Act).",
        "about_ai_act_title": "**⚖️ Focus: EU AI Act Compliance**",
        "about_ai_act_desc": "A differenza degli assessment generici, questo tool integra i requisiti del nuovo **Regolamento Europeo sull'IA**. Lo score di Governance penalizza le lacune nella supervisione umana (Human-in-the-loop) e premia la corretta classificazione del rischio dei sistemi IA.",
        "about_maturity_title": "#### Modello di Maturità Digitale",
        "about_maturity_desc": "Le aziende vengono classificate in 4 stadi:",
        "about_features_title": "✨ Core Features",
        "about_feat1": "**Analisi Multilingua**\nSupporto completo IT/EN per contesti internazionali.",
        "about_feat2": "**What-If Simulator**\nSimulazione degli impatti degli investimenti in tempo reale.",
        "about_feat3": "**Benchmarking**\nConfronto immediato con i dati medi di settore (PMI, Finance, Retail).",
        "about_architecture_title": "⚙️ Architettura della Compliance",
        "about_architecture_text": "Il tool è stato costruito seguendo standard rigorosi per garantire la massima sicurezza e trasparenza:\n\n**Transparency (Trasparenza)**: La logica di scoring non è una 'black box'. Ogni dimensione segue una pesatura documentata e i criteri di calcolo sono basati su framework di maturità digitale standard (es. OECD/NIST).\n\n**Privacy-by-Design**: L'applicazione è progettata per non trattenere dati. L'elaborazione avviene esclusivamente in-session (RAM temporanea del browser). Una volta chiusa la scheda, nessun dato aziendale o risposta rimane sui nostri server.\n\n**Ethics-by-Design**: Il questionario include controlli specifici per identificare bias algoritmici e garantire che l'IA sia sviluppata come strumento di supporto all'uomo (Human-in-the-loop).",
        "about_contact_title": "🤝 Contatti",
        "about_contact_info": "**Sabrina Rizzi** *In formazione presso ITS Digital Academy Mario Volpato*<br>[🌐 Sito Web Professionale](https://sabrina-rizzi.github.io/)<br>[🔗 Profilo LinkedIn](http://www.linkedin.com/in/sabrina-rizzi14)",
        "about_version_title": "📝 Versione",
        "about_version_info": "v2.1 PRO - Ultima Modifica: Marzo 2026\n- UX Restyling: Pulsanti primari e flussi di conferma\n- Navigation: Auto-scroll al top e transizioni pulite\n- AI Act Scoring Logic\n- Dynamic Radar Charting\n- PDF/Excel Reports",
        "sidebar_badge_title": "🛡️ AI Act Compliant Framework",
        "sidebar_badge_desc": "Ethics-by-Design • Transparency • Privacy-by-Design<br><i>Regolamento UE 2024/1689</i>"
    },
    "en": {
        "title": "AI Readiness Assessment Pro",
        "nav": "Menu",
        "home": "Home",
        "assess": "Assessment",
        "audit": "Data Audit",
        "about": "About",
        "history": "History",
        "compare": "Compare",
        "lang": "💬 Language",
        "examples": "📂 Examples",
        "new": "— No Example —",
        "export_opt": "📥 Export Options",
        "compare_not_enough": "You need at least 2 saved assessments to compare. Complete more assessments first!",
        "compare_select": "Select Assessments to Compare (max 3)",
        "compare_table": "Detailed Comparison",
        "c_date": "Date", "c_score": "Total Score", "c_level": "Level",
        "prog_anal": "Progress Analysis",
        "first_score": "First Score", "last_score": "Latest Score", "improvement": "Improvement",
        "download_comp": "📥 Download Comparison Data",

        "hero_title": "Navigating Transformation: AI Readiness Framework",
        "hero_subtitle": "An advanced analytic tool to measure digital maturity and chart the course towards conscious AI adoption.",
        "met_dim": "Dimensions Analyzed",
        "met_bench": "Sector Benchmarks",
        "met_time": "Est. Time",
        "why_title": "The Model: 6 Pillars of Readiness",
        "why_desc": "AI adoption is not just tech. Our framework analyzes the organization 360 degrees:",
        "d1_t": "Strategy", "d1_d": "Business vision, ROI definition, and long-term investment.",
        "d2_t": "Data", "d2_d": "Quality, accessibility, governance, and volume.",
        "d3_t": "Processes", "d3_d": "Workflow maturity and automation potential.",
        "d4_t": "Team & Culture", "d4_d": "Internal skills (upskilling) and change management.",
        "d5_t": "Infrastructure", "d5_d": "Tech stack, Cloud readiness, and integration.",
        "d6_t": "Ethics & Governance", "d6_d": "Compliance (AI Act), privacy, and risk management.",
        "method_title": "🔎 Scoring Methodology",
        "method": "Methodology",
        "method_text": "Weighted scoring system based on 6 key dimensions.",
        "method_p1": "**Normalization**: Each question has a weight. The final score (0-100) is calculated algorithmically.",
        "method_p2": "**Benchmarking**: Your results are compared in real-time with industry standards to highlight competitive gaps.",
        "cta_title": "Ready to start?",
        "start_btn": "🚀 Start Assessment",
        "audit_btn": "🔎 Data Audit (Preliminary)",
        "cases_title": "📂 Real-World Case Studies",
        "cases_desc": "Explore how different companies perform. Click to load a full report.",
        "case_1": "🏦 Finance Sector (High)",
        "case_2": "🏭 Manufacturing Sector (Medium)",
        "case_3": "🏪 Retail Sector (Low)",
        
        "score_title": "AI Readiness Score",
        "sector": "Sector",
        "download": "📄 Download PDF Report",
        "download_excel": "📊 Export Excel",
        "download_json": "💾 Export JSON",
        "share": "🔗 Share",
        "save": "💾 Save Assessment",
        "assess_intro": "**Instructions**: Answer all questions honestly.",
        "sim_total": "Simulated Score",
        "error_answ": "⚠️ Please answer all questions.",
        "reset_btn": "🔄 Reset & Restart",
        "autosave": "💾 Auto-save active",
        "sync_title": "Sync with Browser Cache",
        "sync_info": "Assessment history is kept in session memory. Use this to restore data from your browser's local storage.",
        "sync_btn": "Restore from Browser Memory",
        "sync_warning": "Note: This feature uses browser LocalStorage. Data is device-specific.",
        "sync_paste": "Cache Content (Paste here if auto-sync fails)",
        "sync_ok": "✅ Data restored from browser cache!",
        "sync_cache": "No data found in browser cache.",
        
        "rec_title": "💡 Strategic Roadmap",
        "empty_rec": "Great job! No critical recommendations.",
        "all_done": "🎉 Assessment Completed!",
        "audit_title": "Data Audit Checklist",
        "audit_desc": "Quick data health check.",
        "audit_score": "Data Maturity Index",
        "audit_low": "⚠️ Data Silos", 
        "audit_low_desc": "Your organisation shows **fragmented, non-integrated data** across departments. Each team works in isolation, making any AI initiative difficult to implement. An immediate data integration strategy is required.",
        "audit_med": "📈 Reactive Digitalization", 
        "audit_med_desc": "Your organisation has started digitalization, but **reactively rather than strategically**. You have solid foundations to build on, but a structured plan is needed to reach the next maturity level.",
        "audit_high": "🚀 Proactive Data Governance",
        "audit_high_desc": "Excellent! Your organisation demonstrates **mature, structured data management** with defined processes and clear ownership. You are in an optimal position to launch or scale AI projects.",
        "audit_cta_low": "💡 This result highlights significant growth potential in your data infrastructure. Complete the full AI Readiness Assessment to receive a personalised strategic roadmap.",
        "audit_cta_med": "💡 Your audit highlights specific improvement areas. Proceed with the full AI Readiness Assessment for an in-depth evaluation and a tailored action plan.",
        "audit_cta_high": "💡 Your data maturity is a strategic asset. Explore your full AI potential with the complete Assessment to identify where you can create even more value.",
        "go_to_assess": "Go to Assessment →",
        "about_text": "Developed by Sabrina Rizzi.",
        "contact": "Contact",
        "history_title": "📊 Assessment History",
        "history_empty": "No saved assessments. Complete your first assessment!",
        "compare_title": "📊 Compare Assessments",
        "compare_desc": "Compare up to 3 assessments to track progress",
        "loading": "Loading...",
        "error_generic": "An error occurred. Please try again.",
        "success_save": "✅ Assessment saved successfully!",
        "confirm_reset": "Are you sure you want to reset? All unsaved data will be lost.",
        "waterfall_title": "📊 Score Contribution by Dimension",
        "critical_dims": "🔍 Focus: Key Dimensions",
        "disclaimer": "LEGAL DISCLAIMER: This tool is provided for illustrative and educational purposes only. The results and reports generated represent an indicative self-assessment and do not constitute certified legal, technical, or professional advice. The author assumes no liability for any strategic decisions or investments made based on the data provided by this tool.",
        "choose_options": "Choose Options",
        "ux_challenge_title": "Design Challenge: UX in low graphic flexibility contexts",
        "ux_challenge_text": "For this project I chose Streamlit for its technical efficiency, accepting the challenge of optimizing the User Experience within the structural limits of the framework. I focused on Information Hierarchy and Cognitive Load Reduction, dividing the assessment into logical modules and using visual Data Storytelling (Radar Charts) to make results immediately actionable for management.",
        "perf_dim": "Performance by Dimension",
        "benchmark": "Sector Benchmark",
        "what_if_title": "📉 What-If Simulator",
        "what_if_sub": "Strategic Planning",
        "what_if_desc": "Simulate the impact of investments on your total score.",
        "about_note": "🎓 **Project Note**: This tool is made for **educational and personal portfolio purposes**, as a practical demonstration of skills in software design, UX, data analysis, and regulatory compliance. The assessment results are indicative and intended to stimulate strategic reflection.",
        "about_vision_title": "🚀 Project Vision",
        "about_vision_text": "The **AI Readiness Assessment Tool** is designed to help organizations map their digital transformation journey. It doesn't just measure technical capability, but evaluates the business ecosystem as a whole, ensuring AI adoption is **ethical, secure, and strategic**.",
        "about_methodology_title": "🏗️ Methodology and Scoring",
        "about_6pillars_title": "#### 6 Pillar Framework",
        "about_6pillars_desc": "The tool analyzes six critical dimensions, each with a specific weight based on strategic impact:\n1. **Strategy**: Alignment with business objectives.\n2. **Data**: Quality and information architecture.\n3. **Processes**: Workflow automation potential.\n4. **Team & Culture**: Skills and change management.\n5. **Infrastructure**: Technological readiness and scalability.\n6. **Governance & Ethics**: Regulatory compliance (AI Act).",
        "about_ai_act_title": "**⚖️ Focus: EU AI Act Compliance**",
        "about_ai_act_desc": "Unlike generic assessments, this tool integrates the requirements of the new **European AI Regulation**. The Governance score penalizes gaps in human oversight (Human-in-the-loop) and rewards the correct risk classification of AI systems.",
        "about_maturity_title": "#### Digital Maturity Model",
        "about_maturity_desc": "Companies are classified into 4 stages:",
        "about_features_title": "✨ Core Features",
        "about_feat1": "**Multilingual Analysis**\nFull IT/EN support for international contexts.",
        "about_feat2": "**What-If Simulator**\nReal-time simulation of investment impacts.",
        "about_feat3": "**Benchmarking**\nImmediate comparison with sector averages (SMEs, Finance, Retail).",
        "about_architecture_title": "⚙️ Compliance Architecture",
        "about_architecture_text": "The tool was built following rigorous standards to ensure maximum security and transparency:\n\n**Transparency**: The scoring logic is not a 'black box'. Each dimension follows a documented weighting, and the calculation criteria are based on standard digital maturity frameworks (e.g., OECD/NIST).\n\n**Privacy-by-Design**: The application is designed to not retain data. Processing occurs exclusively in-session (temporary browser RAM). Once the tab is closed, no corporate data or answers remain on our servers.\n\n**Ethics-by-Design**: The questionnaire includes specific controls to identify algorithmic bias and ensure that AI is developed as a human support tool (Human-in-the-loop).",
        "about_contact_title": "🤝 Contact",
        "about_contact_info": "**Sabrina Rizzi** *In training at ITS Digital Academy Mario Volpato*<br>[🌐 Professional Website](https://sabrina-rizzi.github.io/)<br>[🔗 LinkedIn Profile](http://www.linkedin.com/in/sabrina-rizzi14)",
        "about_version_title": "📝 Version",
        "about_version_info": "v2.1 PRO - Last Update: March 2026\n- UX Restyling: Primary buttons & Confirmation flows\n- Navigation: Auto-scroll to top & clean transitions\n- AI Act Scoring Logic\n- Dynamic Radar Charting\n- PDF/Excel Reports",
        "sidebar_badge_title": "🛡️ AI Act Compliant Framework",
        "sidebar_badge_desc": "Ethics-by-Design • Transparency • Privacy-by-Design<br><i>EU Regulation 2024/1689</i>"
    }
}

# Add translations for maturity levels
MATURITY_TRANS = {
    "Ad-hoc": {"it": "Ad-hoc (Iniziale)", "en": "Ad-hoc"},
    "Opportunistic": {"it": "Opportunistico (Ripetibile)", "en": "Opportunistic"},
    "Systematic": {"it": "Sistematico (Definito)", "en": "Systematic"},
    "Transformational": {"it": "Trasformativo (Ottimizzato)", "en": "Transformational"}
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_benchmarks() -> Dict:
    """Load sector benchmarks from JSON file."""
    try:
        with open('data/benchmarks.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning("⚠️ Benchmark file not found. Using defaults.")
        return {
            "General": {"strategy": 50, "data": 50, "processes": 50, 
                       "team": 50, "infrastructure": 50, "ethics": 50},
            "Manufacturing": {"strategy": 55, "data": 60, "processes": 65, 
                             "team": 50, "infrastructure": 55, "ethics": 50},
            "Finance": {"strategy": 70, "data": 75, "processes": 65, 
                       "team": 60, "infrastructure": 70, "ethics": 80},
            "FMCG": {"strategy": 60, "data": 65, "processes": 60, 
                    "team": 55, "infrastructure": 60, "ethics": 65},
            "Retail": {"strategy": 55, "data": 60, "processes": 60, 
                      "team": 50, "infrastructure": 55, "ethics": 60}
        }
    except Exception as e:
        st.error(f"Error loading benchmarks: {e}")
        return {}

def save_assessment_to_history(results: Dict, sector: str, lang: str) -> None:
    """Save assessment to history with timestamp."""
    if 'assessment_history' not in st.session_state:
        st.session_state.assessment_history = []
    
    assessment_record = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'sector': sector,
        'lang': lang,
        'answers': st.session_state.get('answers', {})
    }
    
    st.session_state.assessment_history.append(assessment_record)
    
    # Keep only last 10 assessments
    if len(st.session_state.assessment_history) > 10:
        st.session_state.assessment_history = st.session_state.assessment_history[-10:]
    
    # Persistent Sync
    save_to_localstorage()

def export_to_excel(results: Dict, sector: str) -> BytesIO:
    """Export assessment results to Excel format."""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Metric': ['Total Score', 'Level', 'Sector', 'Date', 'Tool', 'Author', 'Disclaimer'],
            'Value': [
                results['total_score'],
                results['level'],
                sector,
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                'AI Readiness Assessment Pro',
                'Sabrina Rizzi (sabrina-rizzi.github.io)',
                'Educational and portfolio use only. Not certified professional advice.'
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Dimensions sheet
        dim_data = []
        for dim_id, dim_info in results['dimensions'].items():
            dim_data.append({
                'Dimension': dim_info['name'],
                'Score': dim_info['score'],
                'Weight': dim_info.get('weight', 1.0)
            })
        pd.DataFrame(dim_data).to_excel(writer, sheet_name='Dimensions', index=False)
        
        # Recommendations sheet
        if 'detailed_recommendations' in results:
            rec_data = []
            for rec in results['detailed_recommendations']:
                rec_data.append({
                    'Dimension': rec['dimension'],
                    'Action': rec['action'],
                    'Detail': rec['detail']
                })
            pd.DataFrame(rec_data).to_excel(writer, sheet_name='Recommendations', index=False)
    
    output.seek(0)
    return output

def export_to_json(results: Dict, sector: str, answers: Dict) -> str:
    """Export complete assessment to JSON format."""
    export_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'sector': sector,
            'version': '2.0',
            'tool_info': {
                'name': 'AI Readiness Assessment Pro',
                'author': 'Sabrina Rizzi',
                'website': 'https://sabrina-rizzi.github.io/',
                'disclaimer': 'This tool is for educational and portfolio purposes only. Not certified professional advice.'
            }
        },
        'results': results,
        'answers': answers
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def create_comparison_chart(assessments: List[Dict], t: Dict) -> go.Figure:
    """Create comparison chart for multiple assessments."""
    fig = go.Figure()
    
    colors = ['#667eea', '#f093fb', '#4facfe']
    
    for idx, assessment in enumerate(assessments):
        results = assessment['results']
        timestamp = datetime.fromisoformat(assessment['timestamp']).strftime('%Y-%m-%d %H:%M')
        
        categories = [dim['name'] for dim in results['dimensions'].values()]
        values = [dim['score'] for dim in results['dimensions'].values()]
        
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            name=f"Assessment {idx + 1} ({timestamp})",
            line_color=colors[idx % len(colors)]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="#e0e0e0",
                tickfont=dict(size=12)
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(l=40, r=40, t=20, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def auto_save_answers() -> None:
    """Auto-save current answers to session state."""
    if 'answers' in st.session_state and st.session_state.answers:
        st.session_state.last_autosave = datetime.now()
        save_to_localstorage()

def save_to_localstorage():
    """Save history and current answers to browser LocalStorage using JS."""
    import streamlit.components.v1 as components
    
    # Prepare data
    history = st.session_state.get('assessment_history', [])
    answers = st.session_state.get('answers', {})
    
    # We encode to base64 to avoid quote issues in JS
    history_json = json.dumps(history)
    answers_json = json.dumps(answers)
    
    js_code = f"""
    <script>
        localStorage.setItem('ai_readiness_history', `{history_json}`);
        localStorage.setItem('ai_readiness_answers', `{answers_json}`);
    </script>
    """
    components.html(js_code, height=0)

def load_from_localstorage():
    """Load data from LocalStorage using a JS-to-Python bridge."""
    import streamlit.components.v1 as components
    
    st.markdown(f"### 🔄 Sincronizza con la Cache del Browser")
    st.info("La cronologia degli assessment è mantenuta in memoria di sessione. Usa questa funzione per ripristinare i dati dalla memoria locale del browser.")
    
    if st.button("Ripristina dalla Memoria del Browser"):
        st.warning("Nota: questa funzione usa il LocalStorage del browser. I dati sono specifici del dispositivo.")
        components.html("""
            <script>
                const history = localStorage.getItem('ai_readiness_history');
                const answers = localStorage.getItem('ai_readiness_answers');
                if (history || answers) {
                    const data = JSON.stringify({history: JSON.parse(history), answers: JSON.parse(answers)});
                    window.parent.postMessage({
                        type: 'streamlit:set_widget_value',
                        data: {id: 'ls_data_receiver', value: data}
                    }, '*');
                } else {
                    alert('Nessun dato trovato nella cache del browser.');
                }
            </script>
        """, height=0)
    
    ls_data = st.text_area("Contenuto Cache (Incolla qui se la sincronizzazione automatica fallisce)", key="ls_data_receiver", help="Uso interno per la sincronizzazione")
    
    if ls_data:
        try:
            imported = json.loads(ls_data)
            if 'history' in imported:
                st.session_state.assessment_history = imported['history']
            if 'answers' in imported:
                st.session_state.answers = imported['answers']
            st.success("✅ Dati ripristinati dalla cache del browser!")
            st.rerun()
        except:
            pass

def create_waterfall_chart(results: Dict, t: Dict) -> go.Figure:
    """Create a waterfall chart showing contribution of each dimension to total score."""
    dims = results['dimensions']
    
    # Calculate weighted contributions
    labels = []
    values = []
    
    for d_id, d_info in dims.items():
        # Contribution = (score * weight) / total_weight
        # But for total score 0-100, we show score * weight
        # Actually total_score = sum(score * weight) / sum(weight)
        # So we can show the weighted score contribution
        cw = d_info.get('weight', 1.0)
        contribution = (d_info['score'] * cw) / sum(d['weight'] for d in dims.values())
        
        name = d_info['name']
        labels.append(name)
        values.append(contribution)
    
    # Add 'Total' to the end
    labels.append("Total Score")
    values.append(results['total_score'])
    
    fig = go.Figure(go.Waterfall(
        name = "Score Breakdown",
        orientation = "v",
        measure = ["relative"] * (len(labels) - 1) + ["total"],
        x = labels,
        textposition = "outside",
        text = [f"+{v:.1f}" for v in values[:-1]] + [f"{values[-1]:.0f}"],
        y = values[:-1] + [0], # Plotly waterfall handles total automatically if measure="total"
        connector = {"line":{"color":"#667eea", "width": 2, "dash": "dot"}},
        increasing = {"marker":{"color":"#43a047"}},
        decreasing = {"marker":{"color":"#e53935"}},
        totals = {"marker":{"color":"#1e3a8a"}}
    ))

    fig.update_layout(
        title = t.get('waterfall_title', "Score Contribution by Dimension"),
        showlegend = False,
        plot_bgcolor = "white",
        margin = dict(l=20, r=20, t=100, b=20), # Increased top margin to prevent cutting
        font=dict(family="Inter, sans-serif", size=13, color="#111"), # Darker font
        uniformtext=dict(mode='hide', minsize=11),
        height=500 # Increased base height of the chart to prevent squashing
    )
    
    # Improve text contrast specifically for the labels
    fig.update_traces(
        textfont=dict(color="black", size=12),
        textposition="outside"
    )
    
    return fig

def create_gauge_chart(score: float, label: str, color_hex: str = "#667eea") -> go.Figure:
    """Create a minimalist gauge chart."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{label}</b>", 'font': {'size': 16, 'color': '#FFF'}}, # Changed to white as requested
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#BBB"},
            'bar': {'color': color_hex},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e0e0e0",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(229, 57, 53, 0.1)'},
                {'range': [40, 70], 'color': 'rgba(251, 192, 45, 0.1)'},
                {'range': [70, 100], 'color': 'rgba(67, 160, 71, 0.1)'}
            ],
        }
    ))
    
    fig.update_layout(
        height=150,
        margin=dict(l=25, r=25, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def load_example_data_and_redirect(example_name: str, menu_options: Dict, t: Dict) -> None:
    """Load example data from JSON file and redirect to assessment."""
    file_map = {
        t.get('case_1', 'Caso Studio Alto'): "examples/intesa_sanpaolo.json",
        t.get('case_2', 'Caso Studio Medio'): "examples/italian_sme.json",
        t.get('case_3', 'Caso Studio Basso'): "examples/low_readiness.json",
        # Legacy keys for backwards compat
        "Intesa Sanpaolo (High)": "examples/intesa_sanpaolo.json",
        "Italian SME (Medium)": "examples/italian_sme.json",
        "Tradizione Casa (Low)": "examples/low_readiness.json",
    }
    
    file_path = file_map.get(example_name)
    
    if not file_path:
        file_path = "examples/italian_sme.json"
    
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                st.session_state.answers = data.get('answers', {})
                st.session_state.data_uid = st.session_state.get('data_uid', 0) + 1
                st.session_state.last_loaded_example = example_name
                st.session_state.menu = "Assessment"
                st.session_state.show_results = True
                
                try:
                    assess_label = next(k for k, v in menu_options.items() if v == "Assessment")
                    st.session_state.nav_radio = assess_label
                except:
                    pass
                
                st.rerun()
        except Exception as e:
            st.error(f"Errore nel caricamento del caso studio: {e}")
    else:
        st.warning(f"File cas studio non trovato: {file_path}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    # Initialize session state
    if 'menu' not in st.session_state:
        st.session_state.menu = "Home"
    if 'data_uid' not in st.session_state:
        st.session_state.data_uid = 0
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'assessment_history' not in st.session_state:
        st.session_state.assessment_history = []
    
    # JS snippet to sync LocalStorage -> Session State on first load
    # This uses a "hidden" mechanism to communicate back to Streamlit
    import streamlit.components.v1 as components
    
    # We use a state variable to ensure we only sync once per session
    if 'ls_synced' not in st.session_state:
        st.session_state.ls_synced = False

    if not st.session_state.ls_synced:
        # Script to send data back to Streamlit
        # We'll use a simple button 'Sync with Browser Memory' in the UI instead of auto-sync
        # because auto-sync back to Python is tricky without heavy components.
        pass
    
    # Sidebar
    st.sidebar.markdown(
        f"<p class='sidebar-title-custom'>🤖 {TRANS['en']['title']}</p>", 
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("""
    <div style='font-size: 0.9em; color: #666; margin-top: -10px; margin-bottom: 20px;'>
    | Sabrina Rizzi
    </div>
    <div class='sidebar-link'>
    <a href="https://sabrina-rizzi.github.io/" target="_blank">🌐 Website</a> | 
    <a href="http://www.linkedin.com/in/sabrina-rizzi14" target="_blank">🔗 LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Language selector - Reordered as requested
    lang_code = st.sidebar.radio(
        "💬 Language", 
        ["IT", "EN"], 
        horizontal=True, 
        key="lang_toggle"
    )
    lang = lang_code.lower()
    t = TRANS[lang]
    
    if 'last_loaded_example' not in st.session_state:
        st.session_state.last_loaded_example = t['new']
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Inject JS to force cursor:pointer on sidebar selectboxes and Compare multiselect (reliable fix)
    import streamlit.components.v1 as _comp_cursor
    _comp_cursor.html("""
    <script>
    (function(){
        function applyPointer(){
            var els = window.parent.document.querySelectorAll(
                'section[data-testid="stSidebar"] [data-baseweb="select"],' +
                'section[data-testid="stSidebar"] [data-baseweb="select"] *,' +
                'section[data-testid="stSidebar"] [data-baseweb="select"] > div,' +
                '[data-testid="stSelectbox"] [data-baseweb="select"],' +
                '[data-testid="stSelectbox"] [data-baseweb="select"] *,' +
                '[data-testid="stMultiSelect"] [data-baseweb="select"],' +
                '[data-testid="stMultiSelect"] [data-baseweb="select"] *'
            );
            els.forEach(function(e){ e.style.cssText += ';cursor:pointer!important'; });
        }
        applyPointer();
        var obs = new MutationObserver(applyPointer);
        obs.observe(window.parent.document.body, {childList:true, subtree:true});
    })();
    </script>
    """, height=0)

    st.sidebar.markdown("---")
    
    # Navigation menu
    menu_options = {
        t['home']: "Home",
        t['audit']: "Data Audit",
        t['assess']: "Assessment",
        t['history']: "History",
        t['compare']: "Compare",
        t['about']: "About"
    }
    
    def handle_menu():
        st.session_state.menu = menu_options[st.session_state.nav_radio]
        if st.session_state.menu != "Assessment":
            st.session_state.show_results = False
    
    current_labels = list(menu_options.keys())
    try:
        current_label = next(k for k, v in menu_options.items() if v == st.session_state.menu)
    except StopIteration:
        current_label = t['home']
        st.session_state.menu = "Home"
    
    st.session_state.nav_radio = current_label
    st.sidebar.markdown(f"**<span style='font-size: 1.1rem; color: #e0e0e0;'>🧭 {t['nav']}</span>**", unsafe_allow_html=True)
    st.sidebar.radio(
        f"🧭 {t['nav']}", 
        current_labels, 
        key="nav_radio", 
        on_change=handle_menu,
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Sector selector (moved under Menu)
    sector_tooltip = (
        "🏜️ **A cosa serve il Settore?**\n\n"
        "Il settore selezionato viene usato come **benchmark di confronto** nel grafico radar dei risultati. "
        "Ti permette di confrontare il tuo punteggio con la media del tuo settore di riferimento.\n\n"
        "**Consiglio**: scegli il settore più vicino all'attività principale della tua organizzazione. "
        "Se sei un'azienda manifatturiera che usa molto data science, scegli *Manufacturing*."
    ) if lang == 'it' else (
        "🏜️ **What is the Sector for?**\n\n"
        "The selected sector is used as a **benchmark** in the radar chart of your results. "
        "It allows you to compare your score against your sector's average.\n\n"
        "**Tip**: choose the sector closest to your organisation's main activity."
    )
    st.sidebar.markdown(f"**<span style='font-size: 1.1rem; color: #e0e0e0;'>🏢 {t['sector']}</span>**", unsafe_allow_html=True)
    sector_options = ["General", "Manufacturing", "Finance", "FMCG", "Retail"]
    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        sector_options, 
        key="sector_select",
        help=sector_tooltip,
        label_visibility="collapsed"
    )
    
    # Examples selector
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**<span style='font-size: 1.1rem; color: #e0e0e0;'>{t['examples']}</span>**", unsafe_allow_html=True)
    example_options = [
        t['new'], 
        t.get('case_1', 'Caso Studio Alto'),
        t.get('case_2', 'Caso Studio Medio'),
        t.get('case_3', 'Caso Studio Basso'),
    ]
    selected_example = st.sidebar.selectbox(
        "Select Example", 
        example_options, 
        key=f"ex_box_{lang}",
        label_visibility="collapsed"
    )
    
    if selected_example != t['new']:
        # Case Study selected
        if st.session_state.get('last_loaded_example') != selected_example:
            # Check if there's already a case study loaded OR meaningful manual answers
            if st.session_state.get('last_loaded_example') != t['new'] or st.session_state.get('show_results'):
                with st.sidebar.expander(f"⚠️ {t['examples']}", expanded=True):
                    msg = "Vuoi cambiare Caso Studio?" if lang == 'it' else "Change Case Study?"
                    if st.session_state.get('last_loaded_example') == t['new']:
                        msg = "Caricare Caso Studio? L'assessment attuale verrà sovrascritto." if lang == 'it' else "Load Case Study? Current assessment will be overwritten."
                    
                    st.warning(msg)
                    if st.button("Conferma" if lang == 'it' else "Confirm", type="primary", key="confirm_change_case", width="stretch"):
                        st.session_state.last_loaded_example = selected_example
                        load_example_data_and_redirect(selected_example, menu_options, t)
            else:
                # Direct load if in clean "New Assessment" mode without results
                st.session_state.last_loaded_example = selected_example
                load_example_data_and_redirect(selected_example, menu_options, t)
    else:
        # '— Nessun Caso Studio —' selected
        if st.session_state.get('last_loaded_example') != t['new']:
            with st.sidebar.expander(f"⚠️ Rimuovi Caso Studio", expanded=True):
                st.warning(t.get('confirm_reset', 'Vuoi tornare al tuo assessment? I dati del caso studio verranno rimossi.'))
                confirm = st.button("Conferma" if lang == 'it' else "Confirm", type="primary", key="confirm_new_assessment", width="stretch")
                
                if confirm:
                    st.session_state.answers = {}
                    st.session_state.show_results = False
                    st.session_state._balloons_shown = False
                    st.session_state.last_loaded_example = t['new']
                    
                    # Redirect to Assessment menu
                    st.session_state.menu = "Assessment"
                    try:
                        assess_label = next(k for k, v in menu_options.items() if v == "Assessment")
                        st.session_state.nav_radio = assess_label
                    except:
                        pass
                        
                    # Clear sliders and radio buttons
                    keys_to_delete = [k for k in st.session_state.keys() if k.startswith('sim_') or k.startswith('q_')]
                    for k in keys_to_delete:
                        del st.session_state[k]
                    st.session_state._scroll_to_top = True
                    st.rerun()
    
    st.sidebar.markdown("---")
    
    # Reset button --- two-step confirmation to avoid accidental resets
    # Step 1: show button → set pending flag. Step 2: show expander → clear on confirm.
    if st.sidebar.button(t.get('reset_btn', '🔄 Reset'), type="primary"):
        st.session_state['_reset_pending'] = True

    if st.session_state.get('_reset_pending', False):
        with st.sidebar.expander(f"⚠️ {t.get('reset_btn', 'Reset')}", expanded=True):
            st.warning(t.get('confirm_reset', 'Conferma reset'))
            if st.button("Conferma" if lang == 'it' else "Confirm", type="primary", key="confirm_reset_check", width="stretch"):
                saved_lang = st.session_state.get('lang_toggle', 'IT')
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state['lang_toggle'] = saved_lang
                
                # Setup correct starting state (Home)
                st.session_state.menu = "Home"
                st.session_state.last_loaded_example = t['new']
                st.session_state._scroll_to_top = True
                
                st.rerun()
    
    # Auto-save indicator
    if 'last_autosave' in st.session_state:
        last_save = st.session_state.last_autosave.strftime('%H:%M:%S')
        st.sidebar.markdown(f"<div style='font-size: 0.8em; color: #28a745;'>{t['autosave']}<br>Last: {last_save}</div>", unsafe_allow_html=True)
    
    # Load questions
    questions_data = load_questions()
    
    # Route to appropriate page
    menu = st.session_state.menu
    
    if menu == "Home":
        show_home(t, lang, menu_options)
    elif menu == "Assessment":
        show_assessment(questions_data, t, lang, selected_sector)
    elif menu == "Data Audit":
        show_data_audit(t, lang, menu_options)
    elif menu == "History":
        show_history(t, lang)
    elif menu == "Compare":
        show_compare(t, lang)
    elif menu == "About":
        show_about(t)

    # Sidebar Badge
    st.sidebar.markdown("---")
    
    badge_title = t.get('sidebar_badge_title', "🛡️ AI Act Compliant Framework")
    badge_desc = t.get('sidebar_badge_desc', "Ethics-by-Design • Transparency • Privacy-by-Design<br><i>Regolamento UE 2024/1689</i>")
    
    st.sidebar.markdown(f"""
    <div style='border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; background-color: #f9f9f9;'>
        <p style='margin: 0; font-weight: 700; font-size: 0.85em; color: #333;'>{badge_title}</p>
        <p style='margin: 0; font-size: 0.75em; color: #666;'>
            {badge_desc}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    
    # Legal Modal Triggers - Custom Footer with Buttons
    f_col1, f_col2, f_col3, f_col4 = st.columns([1, 0.4, 0.4, 1])
    with f_col1:
        st.markdown(f"<div style='text-align: left; font-size: 0.8em; color: #777;'>© 2026 Sabrina Rizzi</div>", unsafe_allow_html=True)
    with f_col2:
        if st.button("Privacy & Cookies", key="btn_privacy", help="Privacy Policy"):
            show_privacy_dialog(lang)
    with f_col3:
        if st.button("Disclaimer", key="btn_disclaimer", help="Legal Disclaimer"):
            show_disclaimer_dialog(lang)
    with f_col4:
        st.markdown(f"<div style='text-align: right; font-size: 0.8em; color: #777;'>Licensed under MIT</div>", unsafe_allow_html=True)

    # Secondary Disclaimer (Smaller)
    st.markdown("""
        <div style='text-align: center; color: #888; padding-top: 20px; font-size: 0.8em;'>
            <p style='margin: 0;'>AI Readiness Assessment Pro &copy; %s</p>
        </div>
    """ % datetime.now().year, unsafe_allow_html=True)
    
    # Scroll to top mechanism
    if st.session_state.get('_scroll_to_top', False):
        import streamlit.components.v1 as components
        components.html("""
        <script>
            // Try multiple strategies since Streamlit's DOM changes based on layout
            window.parent.scrollTo({top: 0, behavior: 'smooth'});
            var mainContainer = window.parent.document.querySelector('.main');
            if (mainContainer) mainContainer.scrollTo({top: 0, behavior: 'smooth'});
            var appView = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
            if (appView) appView.scrollTo({top: 0, behavior: 'smooth'});
        </script>
        """, height=0)
        st.session_state._scroll_to_top = False

# ============================================================================
# LEGAL DIALOGS
# ============================================================================

@st.dialog("Privacy & Cookies")
def show_privacy_dialog(lang):
    if lang == 'it':
        st.markdown("""
        ### Politica sulla Privacy e sui Cookie
        
        **Nessuna Raccolta Dati Personali**
        Questo strumento è progettato secondo il principio della *Privacy-by-Design*. Non raccogliamo, memorizziamo né trasmettiamo i tuoi dati personali o le risposte dell'assessment a server esterni.
        
        **Elaborazione Locale**
        Tutte le informazioni inserite vengono elaborate esclusivamente nella memoria temporanea (RAM) del tuo browser. Una volta chiusa la scheda, i dati della sessione vengono eliminati.
        
        **Cookie e LocalStorage**
        - Non utilizziamo cookie di profilazione o di terze parti.
        - Utilizziamo esclusivamente il `LocalStorage` del tuo browser per permetterti di salvare la tua cronologia assessment localmente sul tuo dispositivo.
        - Puoi eliminare questi dati in qualsiasi momento cliccando sul tasto "Reset" nella sidebar o svuotando la cache del browser.
        
        **Sicurezza**
        Sebbene i dati non lascino il tuo dispositivo, ti consigliamo di non inserire segreti industriali o dati sensibili specifici.
        """)
    else:
        st.markdown("""
        ### Privacy & Cookie Policy
        
        **No Personal Data Collection**
        This tool is designed following the *Privacy-by-Design* principle. We do not collect, store, or transmit your personal data or assessment answers to external servers.
        
        **Local Processing**
        All information entered is processed exclusively in your browser's temporary memory (RAM). Once the tab is closed, the session data is deleted.
        
        **Cookies & LocalStorage**
        - We do not use profiling or third-party cookies.
        - we exclusively use your browser's `LocalStorage` to allow you to save your assessment history locally on your device.
        - You can delete this data at any time by clicking the "Reset" button in the sidebar or by clearing your browser cache.
        
        **Security**
        Although data does not leave your device, we recommend not entering specific industrial secrets or sensitive data.
        """)

@st.dialog("Disclaimer")
def show_disclaimer_dialog(lang):
    if lang == 'it':
        st.markdown("""
        ### Avviso Legale (Disclaimer)
        
        **Scopo Formativo**
        Questo strumento è fornito esclusivamente a scopo illustrativo, formativo e come dimostrazione di portfolio. I risultati e i report generati rappresentano un'autovalutazione indicativa.
        
        **Nessuna Consulenza Professionale**
        L'utilizzo di questo tool non costituisce e non sostituisce una consulenza legale (EU AI Act), tecnica o professionale certificata. Per implementazioni aziendali reali, si consiglia di consultare esperti qualificati.
        
        **Limitazione di Responsabilità**
        L'autore (Sabrina Rizzi) non si assume alcuna responsabilità per eventuali decisioni strategiche, investimenti o azioni intraprese sulla base dei punteggi o dei consigli forniti da questo software.
        
        **Accuratezza**
        Sebbene basata su standard internazionali (NIST, OECD), la pesatura dello scoring è frutto di una modellazione propria e potrebbe non riflettere appieno la complessità di ogni specifica realtà aziendale.
        """)
    else:
        st.markdown("""
        ### Legal Disclaimer
        
        **Educational Purpose**
        This tool is provided solely for illustrative, educational purposes and as a portfolio demonstration. The results and reports generated represent an indicative self-assessment.
        
        **No Professional Advice**
        Using this tool does not constitute or replace certified legal (EU AI Act), technical, or professional advice. For real business implementations, consulting qualified experts is recommended.
        
        **Limitation of Liability**
        The author (Sabrina Rizzi) assumes no liability for any strategic decisions, investments, or actions taken based on the scores or advice provided by this software.
        
        **Accuracy**
        Although based on international standards (NIST, OECD), the scoring weights are the result of internal modeling and may not fully reflect the complexity of every specific business reality.
        """)

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================

def show_home(t: Dict, lang: str, menu_options: Dict) -> None:
    """Display home page."""
    # Hero section
    st.title("🚀 " + t['hero_title'])
    st.markdown(f"### {t['hero_subtitle']}")
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    
    dim_suffix = "Pilastri" if lang == 'it' else "Pillars"
    bench_suffix = "Settori" if lang == 'it' else "Sectors"
    
    m1.metric("📊 " + t['met_dim'], f"6 {dim_suffix}")
    m2.metric("🏢 " + t['met_bench'], f"5 {bench_suffix}")
    m3.metric("⏱️ " + t['met_time'], "5-7 min")
    
    st.markdown("---")
    
    # Dimensions grid
    st.subheader(t['why_title'])
    st.markdown(t['why_desc'])
    
    # Row 1
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='dimension-card'>"
            f"<div class='dim-icon'>🎯</div>"
            f"<div class='dim-title'>{t['d1_t']}</div>"
            f"<div class='dim-desc'>{t['d1_d']}</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div class='dimension-card'>"
            f"<div class='dim-icon'>💾</div>"
            f"<div class='dim-title'>{t['d2_t']}</div>"
            f"<div class='dim-desc'>{t['d2_d']}</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"<div class='dimension-card'>"
            f"<div class='dim-icon'>⚙️</div>"
            f"<div class='dim-title'>{t['d3_t']}</div>"
            f"<div class='dim-desc'>{t['d3_d']}</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(
            f"<div class='dimension-card'>"
            f"<div class='dim-icon'>👥</div>"
            f"<div class='dim-title'>{t['d4_t']}</div>"
            f"<div class='dim-desc'>{t['d4_d']}</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
    with c5:
        st.markdown(
            f"<div class='dimension-card'>"
            f"<div class='dim-icon'>☁️</div>"
            f"<div class='dim-title'>{t['d5_t']}</div>"
            f"<div class='dim-desc'>{t['d5_d']}</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
    with c6:
        st.markdown(
            f"<div class='dimension-card'>"
            f"<div class='dim-icon'>⚖️</div>"
            f"<div class='dim-title'>{t['d6_t']}</div>"
            f"<div class='dim-desc'>{t['d6_d']}</div>"
            f"</div>", 
            unsafe_allow_html=True
        )
    
    # Ethics-by-Design Box
    st.markdown("""
    <div style='text-align: center; margin-top: 15px; padding: 15px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #e0e0e0;'>
        <p style='margin: 0; font-size: 14px; color: #555;'>
            🛡️ <b>Sviluppato con un approccio Ethics-by-Design</b>, integrando i parametri del Regolamento UE 2024/1689 (AI Act).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Methodology and actions
    col_met, col_act = st.columns([1.5, 1])
    
    with col_met:
        st.subheader(t['method_title'])
        st.info(t['method_p1'])
        st.info(t['method_p2'])
    
    with col_act:
        st.markdown(f"### {t['cta_title']}")
        
        def go_assess():
            st.session_state.menu = "Assessment"
            try:
                assess_label = next(k for k, v in menu_options.items() if v == "Assessment")
                st.session_state.nav_radio = assess_label
            except:
                pass
        
        def go_audit():
            st.session_state.menu = "Data Audit"
            try:
                audit_label = next(k for k, v in menu_options.items() if v == "Data Audit")
                st.session_state.nav_radio = audit_label
            except:
                pass
        
        st.button(t['start_btn'], on_click=go_assess, type="primary", width="stretch")
        st.markdown("")
        
        # Custom style for Audit button to be ochre/yellow
        st.markdown("""
        <style>
        div.stButton > button[kind="secondary"] {
            background-color: #fbc02d;
            color: #212529;
            border: 1px solid #fbc02d;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: #f9a825;
            border-color: #f9a825;
            color: #212529;
        }
        </style>
        """, unsafe_allow_html=True)
        st.button(t['audit_btn'], on_click=go_audit, type="secondary", width="stretch")
    
    st.markdown("---")
    
    # Case studies
    st.subheader(t['cases_title'])
    st.markdown(t['cases_desc'])
    
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        if st.button(t['case_1'], width="stretch"):
            load_example_data_and_redirect("Intesa Sanpaolo (High)", menu_options, t)
    with cc2:
        if st.button(t['case_2'], width="stretch"):
            load_example_data_and_redirect("Bauli / FMCG (Retail)", menu_options, t)
    with cc3:
        if st.button(t['case_3'], width="stretch"):
            load_example_data_and_redirect("Italian SME (Medium)", menu_options, t)

def show_assessment(questions_data: Dict, t: Dict, lang: str, sector: str) -> None:
    """Display assessment page with questions."""
    st.title(f"{t['assess']} - {sector}")
    st.markdown(t['assess_intro'])
    
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    
    # Filter dimensions based on sector
    active_dims = [
        d for d in questions_data['dimensions'] 
        if not (d['id'] == 'fmcg' and sector != 'FMCG')
    ]
    
    # Calculate progress
    total_questions = sum(len(d['questions']) for d in active_dims)
    answered_real = 0
    
    for dim in active_dims:
        if dim['id'] in st.session_state.answers:
            valid_ans = [a for a in st.session_state.answers[dim['id']] if a is not None]
            answered_real += len(valid_ans)
    
    progress = min(answered_real / total_questions, 1.0) if total_questions > 0 else 0
    st.progress(progress, text=f"Progress: {int(progress*100)}%")
    
    # Assessment form
    with st.form(f"assessment_form_{lang}"):
        temp_answers = {}
        all_answered = True
        
        for dim in active_dims:
            dim_name = dim['name'] if lang == 'it' else dim.get('name_en', dim['name'])
            dim_desc = dim['description'] if lang == 'it' else dim.get('description_en', dim['description'])
            
            st.header(f"📍 {dim_name}")
            with st.expander(f"ℹ️ {dim_name}: Info"):
                st.write(dim_desc)
            
            dim_answers = []
            for i, q in enumerate(dim['questions']):
                default_idx = None
                if dim['id'] in st.session_state.answers:
                    if i < len(st.session_state.answers[dim['id']]):
                        saved_score = st.session_state.answers[dim['id']][i]
                        opt_scores = [o['score'] for o in q['options']]
                        if saved_score in opt_scores:
                            default_idx = opt_scores.index(saved_score)
                
                q_text = q['text'] if lang == 'it' else q.get('text_en', q['text'])
                st.markdown(f"#### {q_text}")
                
                ops_labels = []
                ops_scores = []
                for opt in q['options']:
                    ops_labels.append(opt['text'] if lang == 'it' else opt.get('text_en', opt['text']))
                    ops_scores.append(opt['score'])
                
                uid = st.session_state.get('data_uid', 0)
                choice = st.radio(
                    f"Select option {i} {dim['id']}", 
                    options=ops_labels,
                    index=default_idx, 
                    key=f"{dim['id']}_{i}_{lang}_{uid}_{sector}", 
                    label_visibility="collapsed"
                )
                
                if choice is None:
                    all_answered = False
                    dim_answers.append(None)
                else:
                    score = ops_scores[ops_labels.index(choice)]
                    dim_answers.append(score)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            temp_answers[dim['id']] = dim_answers
            st.markdown("---")
        
        # Submit button
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button(f"🏁 {t['assess']}", type="primary", width="stretch")
        with col2:
            save_draft = st.form_submit_button(t['save'], type="secondary", width="stretch")
        
        if submitted:
            if not all_answered:
                st.error(t['error_answ'])
            else:
                st.session_state.answers = temp_answers
                st.session_state.show_results = True
                auto_save_answers()
                st.rerun()
        
        if save_draft:
            st.session_state.answers = temp_answers
            auto_save_answers()
            st.success(t['success_save'])
    
    # Show results if available
    if st.session_state.get('show_results', False):
        try:
            from src import assessment
            results = assessment.run_assessment_v2(st.session_state.answers, lang=lang)
            show_results(results, t, sector, lang)
        except Exception as e:
            st.error(f"Error calculating results: {e}")

def show_results(results: Dict, t: Dict, sector: str, lang: str) -> None:
    """Display assessment results with enhanced visualizations."""
    # Show balloons only once per result session, not on every rerun
    if not st.session_state.get('_balloons_shown', False):
        st.balloons()
        st.session_state['_balloons_shown'] = True
    st.markdown(f"<div class='success-box'><h2 style='color: #155724;'>{t['all_done']}</h2></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader(t.get('score_title', "Score"))
        score = int(results['total_score'])
        
        # Dynamic score colour (solid, works on both light and dark themes)
        if score < 40:
            score_color = "#e53935"
            score_bg = "rgba(229, 57, 53, 0.12)"
        elif score < 70:
            score_color = "#ffa000"
            score_bg = "rgba(255, 160, 0, 0.12)"
        else:
            score_color = "#43a047"
            score_bg = "rgba(67, 160, 71, 0.12)"
            
        st.markdown(
            f"<div class='score-box' style='background: {score_bg}; border: 2px solid {score_color};'>"
            f"<p class='score-text' style='color: {score_color}; -webkit-text-fill-color: {score_color};'>{score}/100</p>"
            f"<p class='level-text' style='color: {score_color};'>{results['level']}</p>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        st.info(results['recommendation'])
        
        # Download buttons
        st.markdown(f"### {t.get('export_opt', 'Export Options')}")
        
        col_pdf, col_excel, col_json = st.columns(3)
        
        with col_pdf:
            if st.button(t['download'], width="stretch"):
                try:
                    from src.report_generator import generate_pdf
                    pdf_bytes = generate_pdf(results, sector, lang=lang)
                    st.download_button(
                        "📥 Download PDF", 
                        data=pdf_bytes, 
                        file_name=f"ai_readiness_{datetime.now().strftime('%Y%m%d')}.pdf", 
                        mime="application/pdf",
                        width="stretch"
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}")
        
        with col_excel:
            if st.button(t['download_excel'], width="stretch"):
                try:
                    excel_bytes = export_to_excel(results, sector)
                    st.download_button(
                        "📥 Download Excel", 
                        data=excel_bytes, 
                        file_name=f"ai_readiness_{datetime.now().strftime('%Y%m%d')}.xlsx", 
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch"
                    )
                except Exception as e:
                    st.error(f"Excel error: {e}")
        
        with col_json:
            if st.button(t['download_json'], width="stretch"):
                json_str = export_to_json(results, sector, st.session_state.get('answers', {}))
                st.download_button(
                    "📥 Download JSON", 
                    data=json_str, 
                    file_name=f"ai_readiness_{datetime.now().strftime('%Y%m%d')}.json", 
                    mime="application/json",
                    width="stretch"
                )
        
        # Save to history button
        save_tooltip = (
            "💾 Salva l'assessment nella cronologia della sessione per poterlo visualizzare nella sezione 'Cronologia' e confrontarlo con assessment futuri nella sezione 'Confronta'."
            if lang == 'it' else
            "💾 Save the assessment to session history to view it under 'History' and compare it with future assessments under 'Compare'."
        )
        if st.button(t['save'], type="primary", width="stretch", help=save_tooltip):
            save_assessment_to_history(results, sector, lang)
            st.success(t['success_save'])
        
        st.caption("ℹ️ Salvataggio nella cronologia locale della sessione (i dati si resettano alla chiusura del browser)." if lang == 'it' else "ℹ️ Saved to local session history (data resets on browser close).")
    
    with col2:
        st.subheader(t['perf_dim'])
        
        categories = [dim['name'] for dim in results['dimensions'].values()]
        values = [dim['score'] for dim in results['dimensions'].values()]
        
        benchmarks = load_benchmarks()
        sector_bench = benchmarks.get(sector, benchmarks.get('General', {}))
        bench_values = [sector_bench.get(dim_id, 0) for dim_id in results['dimensions'].keys()]
        
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        bench_closed = bench_values + [bench_values[0]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values_closed, 
            theta=categories_closed, 
            fill='toself', 
            name='Your Score',
            line_color='#667eea',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=bench_closed, 
            theta=categories_closed, 
            fill='toself', 
            name=f"{t['benchmark']} ({sector})",
            line_color='#ffc107',
            fillcolor='rgba(255, 193, 7, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, 
                    range=[0, 100], 
                    gridcolor="#e0e0e0",
                    tickfont=dict(size=12)
                )
            ),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            margin=dict(l=40, r=40, t=20, b=50),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig, width="stretch")
    
    st.markdown("---")
    
    # NEW: Waterfall Chart & Gauges
    col_wat, col_gau = st.columns([1.5, 1])
    
    with col_wat:
        # Bar chart of dimension contributions
        dim_names = [d['name'] for d in results['dimensions'].values()]
        dim_scores = [d['score'] for d in results['dimensions'].values()]
        colors = ['#e53935' if s < 40 else '#ffa000' if s < 70 else '#43a047' for s in dim_scores]
        bar_fig = go.Figure(go.Bar(
            x=dim_names,
            y=dim_scores,
            marker_color=colors,
            text=[f"{int(s)}" for s in dim_scores],
            textposition='outside'
        ))
        bar_fig.update_layout(
            title=dict(text=t.get('perf_dim', 'Punteggio per Dimensione'), font=dict(size=16)),
            yaxis=dict(range=[0, 120], title='Score'),
            xaxis=dict(tickangle=-35),
            margin=dict(l=40, r=40, t=60, b=120),
            height=480,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(bar_fig, width="stretch")
        
    with col_gau:
        st.subheader(t.get('critical_dims', '🔎 Focus: Dimensioni Chiave'))
        sorted_dims = sorted(results['dimensions'].items(), key=lambda x: x[1]['score'])
        for d_id, d_data in sorted_dims[:3]:
            s = d_data['score']
            c = '#e53935' if s < 40 else '#ffa000' if s < 70 else '#43a047'
            gauge = go.Figure(go.Indicator(
                mode='gauge+number',
                value=s,
                title={'text': d_data['name'], 'font': {'size': 12}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': c},
                    'steps': [
                        {'range': [0, 40], 'color': 'rgba(229,57,53,0.15)'},
                        {'range': [40, 70], 'color': 'rgba(255,160,0,0.15)'},
                        {'range': [70, 100], 'color': 'rgba(67,160,71,0.15)'}
                    ]
                }
            ))
            gauge.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(gauge, width="stretch")

    st.markdown("---")
    
    # What-If Simulator
    with st.expander(t['what_if_title'], expanded=True):
        st.subheader(t['what_if_sub'])
        st.markdown(t['what_if_desc'])
        
        current_dims = results['dimensions']
        weighted_sim_sum = 0
        total_sim_weight = 0
        
        cols = st.columns(3)
        for i, (d_id, d_val) in enumerate(current_dims.items()):
            with cols[i % 3]:
                val = int(d_val['score'])
                # Use a unique key for sliders based on the current results so it resets when data changes
                uid_hash = hash(str(results['total_score']))
                new_val = st.slider(
                    f"{d_val['name']}", 
                    0, 100, val, 
                    key=f"sim_{d_id}_{uid_hash}"
                )
                
                w = d_val.get('weight', 1.0)
                weighted_sim_sum += new_val * w
                total_sim_weight += w
        
        if total_sim_weight > 0:
            sim_total = weighted_sim_sum / total_sim_weight
            sim_total = min(100, max(0, sim_total))
            delta = int(sim_total - score)
            
            st.markdown("---")
            col_sim1, col_sim2 = st.columns(2)
            with col_sim1:
                st.metric(t['sim_total'], f"{int(sim_total)}/100", delta=f"{delta:+d}")
            with col_sim2:
                impact_pct = (delta / score * 100) if score > 0 else 0
                st.metric("Impact", f"{impact_pct:+.1f}%")
    
    st.markdown("---")
    
    # Strategic Roadmap
    st.subheader(t['rec_title'])
    detailed_recs = results.get('detailed_recommendations', [])
    
    if detailed_recs:
        rec_cols = st.columns(2)
        for idx, rec in enumerate(detailed_recs):
            with rec_cols[idx % 2]:
                st.markdown(
                    f"<div class='recommendation-card'>"
                    f"<div class='rec-title'>📍 {rec['dimension']}</div>"
                    f"<div class='rec-action'>👉 {rec['action']}</div>"
                    f"<div style='font-size: 14px; margin-top: 8px;'>{rec['detail']}</div>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
    else:
        st.markdown(f"<div class='info-box'>{t['empty_rec']}</div>", unsafe_allow_html=True)

def show_data_audit(t: Dict, lang: str, menu_options: Dict) -> None:
    """Display data audit checklist page."""
    st.title(t['audit_title'])
    st.markdown(t['audit_desc'])
    
    try:
        with open('data/data_audit.json', 'r', encoding='utf-8') as f:
            audit_data = json.load(f)
        
        checked_count = 0
        total_questions = 0
        
        for section in audit_data['sections']:
            title = section['title'] if lang == 'it' else section.get('title_en', section['title'])
            st.subheader(title)
            
            questions = section['questions']
            for q in questions:
                total_questions += 1
                q_text = q['text'] if isinstance(q, dict) else q
                if isinstance(q, dict):
                    q_text = q['text'] if lang == 'it' else q.get('text_en', q['text'])
                
                if st.checkbox(q_text, key=f"audit_{total_questions}_{lang}"):
                    checked_count += 1
            
            st.markdown("---")
        
        if st.button(t['audit_btn'], key=f"audit_calc_btn_{lang}", type="primary"):
            score = int((checked_count / total_questions) * 100) if total_questions > 0 else 0
            
            st.markdown(f"### 📊 {t['audit_score']}: {score}%")
            
            if score < 35:
                feedback = t['audit_low']
                color = "#dc3545"
            elif score < 75:
                feedback = t['audit_med']
                color = "#ffc107"
            else:
                feedback = t['audit_high']
                color = "#28a745"
            
            cta_desc_key = f"audit_cta_{'low' if score < 35 else 'med' if score < 75 else 'high'}"
            feedback_desc_key = f"audit_{'low' if score < 35 else 'med' if score < 75 else 'high'}_desc"
            
            st.markdown(
                f"<div style='padding: 20px; border-radius: 12px; "
                f"background-color: {color}20; border-left: 5px solid {color};'>"
                f"<h3 style='color: {color}; margin: 0 0 12px 0;'>{feedback}</h3>"
                f"<p style='margin: 0; line-height: 1.6;'>{t.get(feedback_desc_key, '')}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(t.get(cta_desc_key, ''))
            
            if score >= 35:
                def go_to_assessment():
                    st.session_state.menu = "Assessment"
                    st.session_state.show_results = False
                    try:
                        assess_label = next(k for k, v in menu_options.items() if v == "Assessment")
                        st.session_state.nav_radio = assess_label
                    except:
                        pass
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.button(
                    t['go_to_assess'], 
                    key=f"redir_{lang}", 
                    on_click=go_to_assessment, 
                    type="primary",
                    width="stretch"
                )
    
    except FileNotFoundError:
        st.error("Data audit file not found. Please create 'data/data_audit.json'")
    except Exception as e:
        st.error(f"Error: {e}")

def show_history(t: Dict, lang: str) -> None:
    """Display assessment history page."""
    st.title(t['history_title'])
    
    # Sync button
    load_from_localstorage()
    st.markdown("---")
    
    if not st.session_state.get('assessment_history', []):
        st.markdown(f"<div class='info-box'>{t['history_empty']}</div>", unsafe_allow_html=True)
        return
    
    # Display assessment history
    for idx, assessment in enumerate(reversed(st.session_state.assessment_history)):
        timestamp = datetime.fromisoformat(assessment['timestamp'])
        results = assessment['results']
        sector = assessment.get('sector', 'General')
        
        with st.expander(
            f"📊 Assessment #{len(st.session_state.assessment_history) - idx} - "
            f"{timestamp.strftime('%Y-%m-%d %H:%M')} - Score: {int(results['total_score'])}/100",
            expanded=(idx == 0)
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(t.get('c_score', 'Punteggio Totale'), f"{int(results['total_score'])}/100")
            with col2:
                st.metric(t.get('c_level', 'Livello'), results['level'])
            with col3:
                st.metric(t.get('sector', 'Settore'), sector)
            
            st.markdown(f"#### {t.get('perf_dim', 'Punteggio Dimensioni')}")
            dim_data = []
            for dim_id, dim_info in results['dimensions'].items():
                dim_data.append({
                    'Dimension': dim_info['name'],
                    'Score': f"{int(dim_info['score'])}/100"
                })
            
            df = pd.DataFrame(dim_data)
            st.dataframe(df, width="stretch", hide_index=True)
            
            # Action buttons
            col_load, col_delete = st.columns(2)
            
            with col_load:
                if st.button(
                    "📂 Load This Assessment", 
                    key=f"load_{idx}", 
                    width="stretch"
                ):
                    st.session_state.answers = assessment.get('answers', {})
                    st.session_state.menu = "Assessment"
                    st.session_state.show_results = True
                    st.rerun()
            
            with col_delete:
                if st.button(
                    "🗑️ Delete", 
                    key=f"delete_{idx}", 
                    type="secondary",
                    width="stretch"
                ):
                    actual_idx = len(st.session_state.assessment_history) - 1 - idx
                    st.session_state.assessment_history.pop(actual_idx)
                    st.rerun()

def show_compare(t: Dict, lang: str) -> None:
    """Display comparison page for multiple assessments."""
    st.title(t['compare_title'])
    st.markdown(t['compare_desc'])
    
    if len(st.session_state.get('assessment_history', [])) < 2:
        st.warning(t.get('compare_not_enough', 'You need at least 2 saved assessments to compare. Complete more assessments first!'))
        return
        
    # Comparison multiselect
    st.markdown(f"### 🔄 {t['compare_select']}")
    
    # Format labels clearly
    assessment_labels = []
    for i, a in enumerate(st.session_state.assessment_history):
        date_str = datetime.fromisoformat(a['timestamp']).strftime('%Y-%m-%d %H:%M')
        score = int(a['results']['total_score'])
        assessment_labels.append(f"#{i+1} - {date_str} - {score}/100")
        
    selected_options = st.multiselect(
        t.get('choose_options', 'Choose Options'),
        options=range(len(assessment_labels)),
        format_func=lambda x: assessment_labels[x],
        max_selections=3,
        label_visibility="collapsed",
        placeholder=t.get('choose_options', 'Scegli un\'opzione')
    )
    
    if len(selected_options) >= 2:
        selected_assessments = [
            st.session_state.assessment_history[i] for i in selected_options
        ]
        
        # Custom CSS specifically for Audit button is scoped to Home or where it's used. 
        # Note: In Streamlit, styling apply globally when injected. 
        # If we only want this specific button yellow, we rely on the fact that audit button is "secondary" 
        # in the context where we inject the style (Home page). 
        # But to avoid affecting other secondary buttons elsewhere, revert styles if needed or accept global change for secondary.
        # User requested: "Data Audit button... ochre/yellow... to distinguish it". 
        # Using secondary type + injected CSS in Home page is a reasonable approach.
        
        # Comparison radar chart
        st.markdown(f"### 📊 {t.get('compare_title', 'Comparison Chart')}")
        fig = create_comparison_chart(selected_assessments, t)
        st.plotly_chart(fig, width="stretch")
        
        # Comparison table
        st.markdown(f"### 📋 {t['compare_table']}")
        
        comparison_data = []
        for idx, assessment in enumerate(selected_assessments):
            results = assessment['results']
            timestamp = datetime.fromisoformat(assessment['timestamp'])
            
            row = {
                'Assessment': f"#{selected_options[idx] + 1}",
                t['c_date']: timestamp.strftime('%Y-%m-%d'),
                t['c_score']: int(results['total_score']),
                t['c_level']: results['level']
            }
            
            for dim_id, dim_info in results['dimensions'].items():
                row[dim_info['name']] = int(dim_info['score'])
            
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, width="stretch", hide_index=True)
        
        # Add branding info to the exported dataframe
        export_df = df.copy()
        export_df['Generated By'] = 'AI Readiness Assessment Pro - sabrina-rizzi.github.io'
        
        # Download Comparison Data
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=t['download_comp'],
            data=csv,
            file_name=f"comparison_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key='download-csv'
        )
        
        # Progress analysis
        if len(selected_assessments) >= 2:
            st.markdown(f"### 📈 {t['prog_anal']}")
            
            first_score = int(selected_assessments[0]['results']['total_score'])
            last_score = int(selected_assessments[-1]['results']['total_score'])
            improvement = last_score - first_score
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(t['first_score'], f"{first_score}/100")
            with col2:
                st.metric(t['last_score'], f"{last_score}/100", delta=f"{improvement:+d}")
            with col3:
                improvement_pct = (improvement / first_score * 100) if first_score > 0 else 0
                st.metric(t['improvement'], f"{improvement_pct:+.1f}%")

def show_about(t):
    st.title(f"ℹ️ {t.get('about', 'Informazioni')}")
    
    # Portfolio / Educational Notice
    st.info(t['about_note'])
    
    st.markdown(f"### {t['about_vision_title']}")
    st.markdown(t['about_vision_text'])

    # --- Sezione Metodologia ---
    st.markdown("---")
    st.subheader(t['about_methodology_title'])
    
    col_met1, col_met2 = st.columns(2)
    with col_met1:
        st.markdown(t['about_6pillars_title'])
        st.markdown(t['about_6pillars_desc'])
    
    with col_met2:
        st.info(f"{t['about_ai_act_title']}\n{t['about_ai_act_desc']}")

    # --- Diagramma della Maturità (Placeholder visivo) ---
    st.markdown(t['about_maturity_title'])
    st.write(t['about_maturity_desc'])
    
    st.markdown(f"""
    - **{MATURITY_TRANS['Ad-hoc']['it' if t['choose_options'] == "Scegli un'opzione" else 'en']}**: {("Processi non strutturati, iniziative isolate." if t['choose_options'] == "Scegli un'opzione" else "Unstructured processes, isolated initiatives.")}
    - **{MATURITY_TRANS['Opportunistic']['it' if t['choose_options'] == "Scegli un'opzione" else 'en']}**: {("Primi esperimenti, ma manca una visione d'insieme." if t['choose_options'] == "Scegli un'opzione" else "Early experiments, but lacks an overall vision.")}
    - **{MATURITY_TRANS['Systematic']['it' if t['choose_options'] == "Scegli un'opzione" else 'en']}**: {("Processi definiti, governance dei dati attiva." if t['choose_options'] == "Scegli un'opzione" else "Defined processes, active data governance.")}
    - **{MATURITY_TRANS['Transformational']['it' if t['choose_options'] == "Scegli un'opzione" else 'en']}**: {("AI integrata ovunque, innovazione continua." if t['choose_options'] == "Scegli un'opzione" else "AI integrated everywhere, continuous innovation.")}
    """)

    # --- Features Highlights ---
    st.markdown("---")
    st.subheader(t['about_features_title'])
    
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(t['about_feat1'])
    with f2:
        st.markdown(t['about_feat2'])
    with f3:
        st.markdown(t['about_feat3'])

    # --- Compliance Architecture ---
    st.markdown("---")
    st.subheader(t['about_architecture_title'])
    st.markdown(t['about_architecture_text'])
    
    # --- UX Paragraph ---
    st.markdown("---")
    st.subheader(t['ux_challenge_title'])
    st.markdown(t['ux_challenge_text'])

    # --- Contatti e Credits ---
    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader(t['about_contact_title'])
        st.markdown(t['about_contact_info'], unsafe_allow_html=True)
    
    with c2:
        st.subheader(t['about_version_title'])
        st.code(t['about_version_info'])

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
