# 🚀 Advanced Features - Code Examples

## Funzionalità Avanzate per AI Readiness Assessment v2.0

---

## 1. 📧 Email Report Sharing

### Implementazione completa sistema di invio email

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st

def send_email_report(
    recipient_email: str, 
    pdf_bytes: bytes, 
    results: Dict,
    sender_config: Dict
) -> bool:
    """
    Send assessment report via email.
    
    Args:
        recipient_email: Recipient's email address
        pdf_bytes: PDF report as bytes
        results: Assessment results dictionary
        sender_config: Email configuration (SMTP settings)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_config['email']
        msg['To'] = recipient_email
        msg['Subject'] = f"AI Readiness Assessment Report - Score: {int(results['total_score'])}/100"
        
        # Email body
        body = f"""
        Dear Colleague,
        
        Your AI Readiness Assessment has been completed successfully!
        
        Overall Score: {int(results['total_score'])}/100
        Level: {results['level']}
        
        Please find your detailed report attached.
        
        Key Highlights:
        """
        
        for dim_id, dim_info in results['dimensions'].items():
            body += f"\n- {dim_info['name']}: {int(dim_info['score'])}/100"
        
        body += """
        
        Best regards,
        AI Readiness Assessment Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
        pdf_attachment.add_header(
            'Content-Disposition', 
            'attachment', 
            filename='ai_readiness_report.pdf'
        )
        msg.attach(pdf_attachment)
        
        # Send email
        with smtplib.SMTP(sender_config['smtp_server'], sender_config['smtp_port']) as server:
            server.starttls()
            server.login(sender_config['email'], sender_config['password'])
            server.send_message(msg)
        
        return True
    
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# Usage in Streamlit app
def show_email_sharing_ui(results: Dict, pdf_bytes: bytes, t: Dict):
    """Display email sharing UI."""
    st.markdown("### 📧 Share via Email")
    
    with st.form("email_form"):
        recipient = st.text_input("Recipient Email", placeholder="colleague@company.com")
        
        # Optional: Email configuration (or use st.secrets)
        with st.expander("SMTP Settings (Optional)"):
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587)
            sender_email = st.text_input("Your Email")
            sender_password = st.text_input("Password", type="password")
        
        submit = st.form_submit_button("Send Email")
        
        if submit:
            if not recipient:
                st.error("Please enter recipient email")
            else:
                sender_config = {
                    'smtp_server': smtp_server,
                    'smtp_port': smtp_port,
                    'email': sender_email,
                    'password': sender_password
                }
                
                with st.spinner("Sending email..."):
                    success = send_email_report(recipient, pdf_bytes, results, sender_config)
                    
                    if success:
                        st.success(f"✅ Report sent to {recipient}!")
                    else:
                        st.error("Failed to send email. Check your SMTP settings.")
```

---

## 2. 🔄 Auto-Save con LocalStorage

### Salvataggio automatico persistente usando JavaScript

```python
import streamlit.components.v1 as components

def auto_save_to_localstorage(data: Dict, key: str = "ai_assessment_draft"):
    """
    Auto-save data to browser's localStorage.
    
    Args:
        data: Dictionary to save
        key: Storage key
    """
    data_json = json.dumps(data)
    
    # JavaScript code to save to localStorage
    js_code = f"""
    <script>
        localStorage.setItem('{key}', '{data_json}');
        console.log('Data auto-saved to localStorage');
    </script>
    """
    
    components.html(js_code, height=0)

def load_from_localstorage(key: str = "ai_assessment_draft") -> Optional[Dict]:
    """
    Load data from browser's localStorage.
    
    Args:
        key: Storage key
    
    Returns:
        Loaded data or None
    """
    js_code = f"""
    <script>
        const data = localStorage.getItem('{key}');
        if (data) {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                data: data
            }}, '*');
        }}
    </script>
    """
    
    result = components.html(js_code, height=0)
    
    if result:
        try:
            return json.loads(result)
        except:
            return None
    
    return None

# Usage in assessment page
def show_assessment_with_autosave(questions_data, t, lang, sector):
    """Assessment page with auto-save functionality."""
    
    # Load draft on page load
    if 'draft_loaded' not in st.session_state:
        draft = load_from_localstorage()
        if draft:
            st.session_state.answers = draft
            st.info("📂 Draft loaded from browser storage")
        st.session_state.draft_loaded = True
    
    # ... existing assessment code ...
    
    # Auto-save on answer change
    if st.session_state.get('answers'):
        auto_save_to_localstorage(st.session_state.answers)
        
        # Show last save indicator
        if 'last_autosave' not in st.session_state:
            st.session_state.last_autosave = datetime.now()
        
        time_since_save = (datetime.now() - st.session_state.last_autosave).seconds
        
        if time_since_save < 5:
            st.success("💾 Saved", icon="✅")
```

---

## 3. 📊 Advanced Analytics Dashboard

### Dashboard con metriche avanzate e visualizzazioni

```python
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

def show_advanced_analytics(t: Dict):
    """Display advanced analytics dashboard."""
    st.title("📊 Advanced Analytics")
    
    # Load all historical data
    if not st.session_state.get('assessment_history'):
        st.info("Complete at least one assessment to see analytics")
        return
    
    history = st.session_state.assessment_history
    
    # Convert to DataFrame
    analytics_data = []
    for assessment in history:
        timestamp = datetime.fromisoformat(assessment['timestamp'])
        results = assessment['results']
        
        record = {
            'timestamp': timestamp,
            'total_score': results['total_score'],
            'level': results['level'],
            'sector': assessment.get('sector', 'Unknown')
        }
        
        # Add dimension scores
        for dim_id, dim_info in results['dimensions'].items():
            record[f'dim_{dim_id}'] = dim_info['score']
        
        analytics_data.append(record)
    
    df = pd.DataFrame(analytics_data)
    
    # --- KPI Metrics ---
    st.markdown("### 📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        latest_score = df['total_score'].iloc[-1]
        st.metric("Latest Score", f"{int(latest_score)}/100")
    
    with col2:
        avg_score = df['total_score'].mean()
        st.metric("Average Score", f"{int(avg_score)}/100")
    
    with col3:
        if len(df) > 1:
            improvement = df['total_score'].iloc[-1] - df['total_score'].iloc[0]
            st.metric("Total Improvement", f"{improvement:+.1f}", delta=f"{improvement:+.1f}")
        else:
            st.metric("Total Improvement", "N/A")
    
    with col4:
        assessments_count = len(df)
        st.metric("Assessments Completed", assessments_count)
    
    st.markdown("---")
    
    # --- Score Trend ---
    st.markdown("### 📉 Score Trend Over Time")
    
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['total_score'],
        mode='lines+markers',
        name='Total Score',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10)
    ))
    
    # Add trend line
    if len(df) > 2:
        z = np.polyfit(range(len(df)), df['total_score'], 1)
        p = np.poly1d(z)
        
        fig_trend.add_trace(go.Scatter(
            x=df['timestamp'],
            y=p(range(len(df))),
            mode='lines',
            name='Trend',
            line=dict(color='#ffc107', width=2, dash='dash')
        ))
    
    fig_trend.update_layout(
        xaxis_title="Date",
        yaxis_title="Score",
        yaxis_range=[0, 100],
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # --- Dimension Heatmap ---
    st.markdown("### 🔥 Dimension Performance Heatmap")
    
    # Prepare heatmap data
    dimension_cols = [col for col in df.columns if col.startswith('dim_')]
    heatmap_data = df[dimension_cols].T
    
    # Rename rows
    dimension_names = {
        'dim_strategy': 'Strategy',
        'dim_data': 'Data',
        'dim_processes': 'Processes',
        'dim_team': 'Team & Culture',
        'dim_infrastructure': 'Infrastructure',
        'dim_ethics': 'Ethics & Governance'
    }
    heatmap_data.index = [dimension_names.get(idx, idx) for idx in heatmap_data.index]
    
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="Assessment #", y="Dimension", color="Score"),
        x=[f"#{i+1}" for i in range(len(df))],
        color_continuous_scale='RdYlGn',
        aspect='auto'
    )
    
    fig_heatmap.update_layout(
        xaxis_title="Assessment Number",
        yaxis_title="Dimension"
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # --- Sector Comparison ---
    st.markdown("### 🏢 Performance by Sector")
    
    if len(df['sector'].unique()) > 1:
        sector_avg = df.groupby('sector')['total_score'].agg(['mean', 'count']).reset_index()
        sector_avg.columns = ['Sector', 'Avg Score', 'Assessments']
        
        fig_sector = px.bar(
            sector_avg,
            x='Sector',
            y='Avg Score',
            text='Assessments',
            color='Avg Score',
            color_continuous_scale='Blues'
        )
        
        fig_sector.update_traces(texttemplate='%{text} assessments', textposition='outside')
        fig_sector.update_layout(yaxis_range=[0, 100])
        
        st.plotly_chart(fig_sector, use_container_width=True)
    else:
        st.info("Complete assessments in different sectors to see comparison")
    
    # --- Dimension Radar Comparison (First vs Last) ---
    if len(df) > 1:
        st.markdown("### 🎯 Progress Radar: First vs Latest")
        
        first_assessment = df.iloc[0]
        last_assessment = df.iloc[-1]
        
        categories = list(dimension_names.values())
        
        first_scores = [first_assessment[col] for col in dimension_cols]
        last_scores = [last_assessment[col] for col in dimension_cols]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=first_scores + [first_scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=f"First ({first_assessment['timestamp'].strftime('%Y-%m-%d')})",
            line_color='#ffc107'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=last_scores + [last_scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=f"Latest ({last_assessment['timestamp'].strftime('%Y-%m-%d')})",
            line_color='#667eea'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # --- Export Analytics ---
    st.markdown("### 💾 Export Analytics Data")
    
    col_csv, col_excel = st.columns(2)
    
    with col_csv:
        csv = df.to_csv(index=False)
        st.download_button(
            "📊 Download CSV",
            data=csv,
            file_name="analytics_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_excel:
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Analytics', index=False)
        
        st.download_button(
            "📈 Download Excel",
            data=excel_buffer.getvalue(),
            file_name="analytics_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
```

---

## 4. 🤖 AI-Powered Recommendations

### Sistema di raccomandazioni intelligenti basato su pattern

```python
from typing import List, Tuple

def generate_ai_recommendations(results: Dict, history: List[Dict]) -> List[Dict]:
    """
    Generate AI-powered recommendations based on current results and history.
    
    Args:
        results: Current assessment results
        history: Assessment history
    
    Returns:
        List of smart recommendations
    """
    recommendations = []
    
    # 1. Identify weakest dimensions
    dimensions_sorted = sorted(
        results['dimensions'].items(),
        key=lambda x: x[1]['score']
    )
    
    weakest_dim = dimensions_sorted[0]
    second_weakest = dimensions_sorted[1] if len(dimensions_sorted) > 1 else None
    
    # 2. Analyze trend if history available
    trend_analysis = {}
    if len(history) > 1:
        for dim_id in results['dimensions'].keys():
            scores = [
                h['results']['dimensions'][dim_id]['score'] 
                for h in history 
                if dim_id in h['results']['dimensions']
            ]
            
            if len(scores) > 1:
                trend = scores[-1] - scores[0]
                trend_analysis[dim_id] = {
                    'trend': trend,
                    'velocity': trend / len(scores)
                }
    
    # 3. Generate priority recommendations
    
    # Critical improvement needed
    if weakest_dim[1]['score'] < 40:
        recommendations.append({
            'priority': 'HIGH',
            'icon': '🚨',
            'title': f"Critical: Strengthen {weakest_dim[1]['name']}",
            'description': f"Score of {int(weakest_dim[1]['score'])} is significantly below benchmark. "
                          f"This dimension requires immediate attention.",
            'actions': [
                "Conduct detailed gap analysis",
                "Allocate dedicated resources",
                "Set quarterly improvement targets"
            ],
            'estimated_impact': '+15-20 points',
            'timeframe': '3-6 months'
        })
    
    # Quick wins
    for dim_id, dim_info in results['dimensions'].items():
        score = dim_info['score']
        
        # Dimensions close to next level
        if 35 < score < 45 or 65 < score < 75:
            recommendations.append({
                'priority': 'MEDIUM',
                'icon': '🎯',
                'title': f"Quick Win: Push {dim_info['name']} to next level",
                'description': f"With {int(score)} score, you're close to the next maturity level. "
                              f"Focus effort here for visible progress.",
                'actions': [
                    "Identify 2-3 quick improvement initiatives",
                    "Leverage existing strengths",
                    "Demonstrate early success"
                ],
                'estimated_impact': '+5-10 points',
                'timeframe': '1-3 months'
            })
            break  # Only one quick win to focus
    
    # Leverage strengths
    strongest_dim = dimensions_sorted[-1]
    if strongest_dim[1]['score'] > 70:
        recommendations.append({
            'priority': 'LOW',
            'icon': '🚀',
            'title': f"Leverage {strongest_dim[1]['name']} Excellence",
            'description': f"Your strength in {strongest_dim[1]['name']} ({int(strongest_dim[1]['score'])} score) "
                          f"can be used to drive improvements in other areas.",
            'actions': [
                "Share best practices across teams",
                "Use as proof of concept for skeptics",
                "Build on this momentum"
            ],
            'estimated_impact': 'Indirect +5-15 points',
            'timeframe': 'Ongoing'
        })
    
    # Trend-based recommendations
    if trend_analysis:
        declining_dims = [
            dim_id for dim_id, trend in trend_analysis.items() 
            if trend['trend'] < -5
        ]
        
        if declining_dims:
            dim_name = results['dimensions'][declining_dims[0]]['name']
            recommendations.append({
                'priority': 'HIGH',
                'icon': '⚠️',
                'title': f"Reverse Decline in {dim_name}",
                'description': f"Negative trend detected. Investigate root causes and take corrective action.",
                'actions': [
                    "Conduct stakeholder interviews",
                    "Review recent changes or challenges",
                    "Implement recovery plan"
                ],
                'estimated_impact': 'Stop decline, +10 points',
                'timeframe': '2-4 months'
            })
    
    return recommendations

def show_ai_recommendations_ui(results: Dict, history: List[Dict], t: Dict):
    """Display AI-powered recommendations."""
    st.markdown("### 🤖 AI-Powered Strategic Recommendations")
    
    recommendations = generate_ai_recommendations(results, history)
    
    # Priority filtering
    priority_filter = st.multiselect(
        "Filter by Priority",
        options=['HIGH', 'MEDIUM', 'LOW'],
        default=['HIGH', 'MEDIUM', 'LOW']
    )
    
    filtered_recs = [r for r in recommendations if r['priority'] in priority_filter]
    
    for rec in filtered_recs:
        # Color-code by priority
        border_color = {
            'HIGH': '#dc3545',
            'MEDIUM': '#ffc107',
            'LOW': '#28a745'
        }[rec['priority']]
        
        with st.container():
            st.markdown(
                f"""
                <div style='
                    padding: 20px; 
                    border-left: 5px solid {border_color}; 
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                    border-radius: 10px;
                    margin-bottom: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                '>
                    <h4 style='margin: 0 0 10px 0; color: {border_color};'>
                        {rec['icon']} {rec['title']} 
                        <span style='float: right; font-size: 0.8em; background: {border_color}; color: white; padding: 3px 10px; border-radius: 5px;'>
                            {rec['priority']}
                        </span>
                    </h4>
                    <p style='margin: 10px 0; color: #555;'>{rec['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Expandable action items
            with st.expander("📋 Action Plan"):
                st.markdown("**Recommended Actions:**")
                for action in rec['actions']:
                    st.markdown(f"- {action}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Estimated Impact", rec['estimated_impact'])
                with col2:
                    st.metric("Timeframe", rec['timeframe'])
```

---

## 5. 🔔 Progress Notifications

### Sistema di notifiche per tracciare progressi

```python
def check_milestones(current_score: float, history: List[Dict]) -> List[str]:
    """
    Check if user has reached any milestones.
    
    Args:
        current_score: Current total score
        history: Assessment history
    
    Returns:
        List of milestone messages
    """
    milestones = []
    
    # First assessment
    if len(history) == 1:
        milestones.append("🎉 Congratulations on completing your first assessment!")
    
    # Score milestones
    if current_score >= 50 and (not history or all(h['results']['total_score'] < 50 for h in history[:-1])):
        milestones.append("🎯 Milestone: You've reached 50+ score!")
    
    if current_score >= 70 and (not history or all(h['results']['total_score'] < 70 for h in history[:-1])):
        milestones.append("🚀 Milestone: Entered 'High Readiness' zone (70+)!")
    
    # Improvement milestones
    if len(history) > 1:
        improvement = current_score - history[-2]['results']['total_score']
        
        if improvement >= 10:
            milestones.append(f"📈 Wow! +{improvement:.1f} point improvement since last assessment!")
        elif improvement >= 5:
            milestones.append(f"👏 Great progress! +{improvement:.1f} points improvement!")
    
    # Consistency milestone
    if len(history) >= 3:
        milestones.append("💪 Consistency: 3+ assessments completed. Keep tracking your progress!")
    
    if len(history) >= 5:
        milestones.append("🏆 Dedication: 5+ assessments! You're serious about AI readiness!")
    
    return milestones

def show_milestone_notifications(current_score: float, history: List[Dict]):
    """Display milestone notifications."""
    milestones = check_milestones(current_score, history)
    
    if milestones:
        st.markdown("### 🎊 Achievements Unlocked!")
        
        for milestone in milestones:
            st.success(milestone)
            st.balloons()  # Celebration!
```

---

## 6. 📱 Mobile-Responsive Design

### CSS enhancements for mobile devices

```python
MOBILE_CSS = """
<style>
    /* Mobile-specific styles */
    @media only screen and (max-width: 768px) {
        /* Adjust font sizes */
        .score-text {
            font-size: 60px !important;
        }
        
        .level-text {
            font-size: 24px !important;
        }
        
        /* Stack columns on mobile */
        .dimension-card {
            height: auto;
            min-height: 180px;
        }
        
        /* Improve touch targets */
        .stButton > button {
            min-height: 48px;
            font-size: 16px;
        }
        
        /* Responsive padding */
        .score-box {
            padding: 25px;
        }
        
        .recommendation-card {
            padding: 15px;
        }
    }
    
    /* Tablet styles */
    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        .score-text {
            font-size: 70px !important;
        }
    }
</style>
"""

def apply_responsive_design():
    """Apply mobile-responsive CSS."""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
```

---

## 7. 🔗 API Integration Template

### Template for future API integrations

```python
import requests
from typing import Optional

class AssessmentAPI:
    """API client for external integrations."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def submit_assessment(self, results: Dict, metadata: Dict) -> Optional[str]:
        """
        Submit assessment results to external system.
        
        Args:
            results: Assessment results
            metadata: Additional metadata
        
        Returns:
            Submission ID if successful
        """
        try:
            payload = {
                'results': results,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/assessments",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            return response.json().get('submission_id')
        
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return None
    
    def get_benchmark_data(self, sector: str) -> Optional[Dict]:
        """Fetch live benchmark data from API."""
        try:
            response = requests.get(
                f"{self.base_url}/benchmarks/{sector}",
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            st.warning(f"Could not fetch live benchmarks: {e}")
            return None

# Usage example
def integrate_api():
    """Integrate with external API."""
    if 'api_client' not in st.session_state:
        # Initialize from secrets
        api_key = st.secrets.get('api_key', '')
        base_url = st.secrets.get('api_base_url', '')
        
        if api_key and base_url:
            st.session_state.api_client = AssessmentAPI(base_url, api_key)
    
    # Use API
    if hasattr(st.session_state, 'api_client'):
        # Submit results
        submission_id = st.session_state.api_client.submit_assessment(
            results=results,
            metadata={'sector': sector, 'lang': lang}
        )
        
        if submission_id:
            st.success(f"✅ Results submitted! ID: {submission_id}")
```

---

Questi esempi di codice avanzati possono essere integrati nel tuo tool per espanderne significativamente le funzionalità! 🚀
