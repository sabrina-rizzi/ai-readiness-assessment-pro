# 🚀 Guida all'Implementazione - AI Readiness Assessment v2.0

## 📋 Indice

1. [Migrazione dalla v1.0 alla v2.0](#migrazione)
2. [Best Practices](#best-practices)
3. [Ottimizzazioni Performance](#performance)
4. [Troubleshooting](#troubleshooting)
5. [Customizzazione](#customizzazione)

---

## 🔄 Migrazione dalla v1.0 alla v2.0

### Passo 1: Backup dei Dati Esistenti

```bash
# Backup del progetto corrente
cp -r ai-readiness-assessment ai-readiness-assessment-backup

# Backup dei dati utente (se presenti)
mkdir backup_data
cp data/*.json backup_data/
```

### Passo 2: Installazione Nuove Dipendenze

```bash
# Aggiorna pip
pip install --upgrade pip

# Installa nuovi pacchetti
pip install -r requirements.txt

# Verifica installazione
pip list | grep streamlit
pip list | grep plotly
pip list | grep openpyxl
```

### Passo 3: Migrazione File di Configurazione

**Vecchio formato (v1.0):**
```python
# Hardcoded values
SECTORS = ["General", "Manufacturing", "Finance"]
```

**Nuovo formato (v2.0):**
```python
# config.py
from dataclasses import dataclass

@dataclass
class AppConfig:
    SUPPORTED_SECTORS = ["General", "Manufacturing", "Finance", "FMCG", "Retail"]
```

### Passo 4: Aggiornamento Session State

**Aggiungi nuovi stati:**
```python
# Nel main()
if 'assessment_history' not in st.session_state:
    st.session_state.assessment_history = []
if 'last_autosave' not in st.session_state:
    st.session_state.last_autosave = None
```

### Passo 5: Testing

```bash
# Test locale
streamlit run app_improved.py

# Verifica funzionalità:
# ✓ Caricamento home page
# ✓ Assessment completo
# ✓ Export PDF/Excel/JSON
# ✓ Salvataggio in cronologia
# ✓ Confronto assessment
```

---

## 💡 Best Practices

### 1. Gestione Session State

**❌ Cattiva Pratica:**
```python
# Accesso diretto senza controllo
score = st.session_state.score  # Può causare KeyError
```

**✅ Buona Pratica:**
```python
# Usa get() con fallback
score = st.session_state.get('score', 0)

# O controlla esistenza
if 'score' in st.session_state:
    score = st.session_state.score
```

### 2. Form Submission

**❌ Cattiva Pratica:**
```python
# Submit multipli senza controllo
if st.button("Submit"):
    # Logic here
if st.button("Save"):
    # Logic here
```

**✅ Buona Pratica:**
```python
# Usa form context
with st.form("assessment_form"):
    # ... form fields ...
    
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.form_submit_button("Submit")
    with col2:
        saved = st.form_submit_button("Save Draft")
```

### 3. File Export

**❌ Cattiva Pratica:**
```python
# Blocca UI durante export
pdf_bytes = generate_huge_pdf()
st.download_button("Download", pdf_bytes)
```

**✅ Buona Pratica:**
```python
# Usa spinner e gestisci errori
with st.spinner("Generating PDF..."):
    try:
        pdf_bytes = generate_pdf(results, sector)
        st.download_button("Download", pdf_bytes)
    except Exception as e:
        st.error(f"Export failed: {e}")
```

### 4. Data Validation

**✅ Implementa validazione robusta:**
```python
def validate_answers(answers: Dict) -> bool:
    """Validate assessment answers."""
    if not answers:
        return False
    
    required_dimensions = ['strategy', 'data', 'processes', 'team', 'infrastructure', 'ethics']
    
    for dim in required_dimensions:
        if dim not in answers:
            return False
        if not isinstance(answers[dim], list):
            return False
        if None in answers[dim]:
            return False
    
    return True
```

### 5. Error Handling

**✅ Cattura errori specifici:**
```python
try:
    results = run_assessment_v2(answers, lang)
except ValueError as e:
    st.error(f"Invalid data: {e}")
except FileNotFoundError as e:
    st.error(f"Required file missing: {e}")
except Exception as e:
    st.error(f"Unexpected error: {e}")
    # Log error for debugging
    import logging
    logging.exception("Assessment calculation failed")
```

---

## ⚡ Ottimizzazioni Performance

### 1. Caching Strategico

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_benchmarks():
    """Load and cache benchmarks."""
    with open('data/benchmarks.json', 'r') as f:
        return json.load(f)

@st.cache_data(ttl=3600)
def load_questions():
    """Load and cache questions."""
    with open('data/questions.json', 'r') as f:
        return json.load(f)
```

### 2. Lazy Loading

```python
# Carica solo quando necessario
def show_results(results, t, sector, lang):
    """Show results with lazy loading."""
    
    # Carica libreria PDF solo se necessario
    if st.button("Download PDF"):
        from src.report_generator import generate_pdf
        pdf_bytes = generate_pdf(results, sector, lang)
        st.download_button("Save", pdf_bytes)
```

### 3. Ottimizzazione Visualizzazioni

```python
# Riduci complessità radar chart
def create_radar_chart(data, max_points=100):
    """Create optimized radar chart."""
    
    # Limita punti per performance
    if len(data) > max_points:
        data = data[:max_points]
    
    fig = go.Figure(data=...)
    
    # Disabilita animazioni per chart grandi
    fig.update_layout(
        transition={'duration': 0} if len(data) > 50 else {'duration': 300}
    )
    
    return fig
```

### 4. Session State Cleanup

```python
def cleanup_old_assessments():
    """Remove old assessments to prevent memory issues."""
    max_history = 10
    
    if 'assessment_history' in st.session_state:
        if len(st.session_state.assessment_history) > max_history:
            st.session_state.assessment_history = \
                st.session_state.assessment_history[-max_history:]
```

---

## 🔧 Troubleshooting

### Problema 1: "Module not found"

**Sintomo:**
```
ImportError: No module named 'openpyxl'
```

**Soluzione:**
```bash
pip install openpyxl
# O reinstalla tutti i requirements
pip install -r requirements.txt
```

### Problema 2: "Session state key error"

**Sintomo:**
```
KeyError: 'answers'
```

**Soluzione:**
```python
# Sempre usa .get() o controlla esistenza
answers = st.session_state.get('answers', {})

# O inizializza all'inizio
if 'answers' not in st.session_state:
    st.session_state.answers = {}
```

### Problema 3: "PDF generation fails"

**Sintomo:**
```
UnicodeEncodeError: 'latin-1' codec can't encode character
```

**Soluzione:**
```python
# In report_generator.py, usa font Unicode
from fpdf import FPDF

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Aggiungi font Unicode
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
```

### Problema 4: "Chart not displaying"

**Sintomo:**
Chart Plotly non si visualizza

**Soluzione:**
```python
# Verifica configurazione Plotly
import plotly.graph_objects as go

fig = go.Figure(...)

# Usa config esplicita
st.plotly_chart(
    fig, 
    use_container_width=True,
    config={'displayModeBar': False}
)
```

### Problema 5: "Form resets on interaction"

**Sintomo:**
Form si resetta quando si interagisce con widget

**Soluzione:**
```python
# Usa chiavi uniche con UID
uid = st.session_state.get('data_uid', 0)

choice = st.radio(
    "Option",
    options=["A", "B"],
    key=f"question_{dim_id}_{idx}_{uid}"  # Chiave univoca
)
```

---

## 🎨 Customizzazione

### 1. Temi e Colori

**Modifica i colori principali:**

```python
# In config.py
THEME_COLORS = {
    "primary": "#YOUR_COLOR",    # Cambia colore primario
    "secondary": "#YOUR_COLOR",  # Cambia colore secondario
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545"
}
```

**Applica nel CSS:**

```python
st.markdown(f"""
<style>
    .score-text {{
        background: linear-gradient(135deg, {THEME_COLORS['primary']} 0%, {THEME_COLORS['secondary']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
</style>
""", unsafe_allow_html=True)
```

### 2. Aggiungere Nuove Dimensioni

**1. Aggiorna questions.json:**

```json
{
  "dimensions": [
    ...existing dimensions...,
    {
      "id": "innovation",
      "name": "Innovazione",
      "name_en": "Innovation",
      "description": "Capacità di innovare...",
      "description_en": "Innovation capability...",
      "questions": [
        {
          "text": "Quanto investite in R&D?",
          "text_en": "How much do you invest in R&D?",
          "options": [
            {"text": "< 1% fatturato", "text_en": "< 1% revenue", "score": 0},
            {"text": "1-3% fatturato", "text_en": "1-3% revenue", "score": 50},
            {"text": "> 3% fatturato", "text_en": "> 3% revenue", "score": 100}
          ]
        }
      ]
    }
  ]
}
```

**2. Aggiorna config.py:**

```python
DIMENSION_WEIGHTS = {
    ...existing weights...,
    "innovation": 1.0
}
```

**3. Aggiorna benchmarks.json:**

```json
{
  "General": {
    ...existing scores...,
    "innovation": 50
  },
  "Technology": {
    ...existing scores...,
    "innovation": 75
  }
}
```

### 3. Personalizzare Raccomandazioni

**Aggiungi template custom in config.py:**

```python
RECOMMENDATION_TEMPLATES = {
    "innovation": {
        "low": {
            "action_it": "Creare Innovation Lab",
            "action_en": "Create Innovation Lab",
            "detail_it": "Dedicare risorse a sperimentazione e prototyping rapido.",
            "detail_en": "Dedicate resources to experimentation and rapid prototyping."
        },
        "medium": {
            "action_it": "Accelerare Time-to-Market",
            "action_en": "Accelerate Time-to-Market",
            "detail_it": "Implementare metodologie agile e DevOps.",
            "detail_en": "Implement agile methodologies and DevOps."
        }
    }
}
```

### 4. Aggiungere Nuovi Export Format

**Esempio: CSV Export**

```python
def export_to_csv(results: Dict, sector: str) -> str:
    """Export results to CSV format."""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Dimension', 'Score', 'Weight'])
    
    # Data
    for dim_id, dim_info in results['dimensions'].items():
        writer.writerow([
            dim_info['name'],
            dim_info['score'],
            dim_info.get('weight', 1.0)
        ])
    
    return output.getvalue()

# In show_results()
if st.button("Export CSV"):
    csv_data = export_to_csv(results, sector)
    st.download_button(
        "Download CSV",
        data=csv_data,
        file_name="assessment.csv",
        mime="text/csv"
    )
```

### 5. Integrare Analytics

**Traccia metriche utente:**

```python
import time

def track_assessment_metrics():
    """Track assessment completion metrics."""
    if 'assessment_start_time' not in st.session_state:
        st.session_state.assessment_start_time = time.time()
    
    if st.session_state.get('show_results'):
        completion_time = time.time() - st.session_state.assessment_start_time
        
        # Salva metriche
        metrics = {
            'completion_time': completion_time,
            'timestamp': datetime.now().isoformat(),
            'sector': st.session_state.get('sector', 'Unknown')
        }
        
        # Append to metrics file
        with open('data/metrics.json', 'a') as f:
            f.write(json.dumps(metrics) + '\n')
```

---

## 📊 Dashboard Metriche (Bonus)

**Crea pagina analytics:**

```python
def show_analytics(t: Dict):
    """Display analytics dashboard."""
    st.title("📊 Analytics Dashboard")
    
    if not os.path.exists('data/metrics.json'):
        st.info("No analytics data yet.")
        return
    
    # Load metrics
    metrics = []
    with open('data/metrics.json', 'r') as f:
        for line in f:
            metrics.append(json.loads(line))
    
    df = pd.DataFrame(metrics)
    
    # Visualizations
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Assessments", len(df))
    
    with col2:
        avg_time = df['completion_time'].mean() / 60
        st.metric("Avg. Completion Time", f"{avg_time:.1f} min")
    
    with col3:
        most_common = df['sector'].value_counts().index[0]
        st.metric("Most Common Sector", most_common)
    
    # Sector distribution
    fig = px.pie(df, names='sector', title='Assessments by Sector')
    st.plotly_chart(fig, use_container_width=True)
    
    # Completion time trend
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_avg = df.groupby('date')['completion_time'].mean() / 60
    
    fig = px.line(
        x=daily_avg.index,
        y=daily_avg.values,
        labels={'x': 'Date', 'y': 'Avg. Time (min)'},
        title='Average Completion Time Trend'
    )
    st.plotly_chart(fig, use_container_width=True)
```

---

## 🚀 Deploy su Cloud

### Streamlit Cloud

```bash
# 1. Push to GitHub
git add .
git commit -m "AI Readiness Assessment v2.0"
git push origin main

# 2. Deploy su Streamlit Cloud
# - Vai su share.streamlit.io
# - Connetti repository GitHub
# - Seleziona app_improved.py
# - Deploy!
```

### Docker

**Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app_improved.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build & Run:**

```bash
docker build -t ai-readiness .
docker run -p 8501:8501 ai-readiness
```

---

## 📞 Supporto

Per domande o problemi:
- GitHub Issues: [repository-url]
- Email: sabrina.rizzi@example.com
- LinkedIn: [sabrina-rizzi14]

---

**Ultima versione**: v2.0  
**Data aggiornamento**: Febbraio 2024
