from fpdf import FPDF
import datetime

class PDFReport(FPDF):
    def header(self):
        # Tool branding
        self.set_font('Arial', 'B', 9)
        self.set_text_color(102, 126, 234)
        self.cell(0, 6, 'AI Readiness Assessment Pro  |  Developed by Sabrina Rizzi', 0, 0, 'L')
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, 'sabrina-rizzi.github.io', 0, 1, 'R')
        # Main title
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'AI Readiness Assessment Report', 0, 1, 'C')
        self.set_draw_color(102, 126, 234)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-18)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font('Arial', 'I', 7)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, f'Page {self.page_no()} | Generated: {datetime.date.today()} | AI Readiness Assessment Pro by Sabrina Rizzi', 0, 1, 'C')
        self.set_font('Arial', 'I', 6)
        self.cell(0, 4, 'DISCLAIMER: This report is for illustrative and educational purposes only and does not constitute certified professional advice.', 0, 0, 'C')


def generate_pdf(results, sector, lang="it"):
    pdf = PDFReport()
    pdf.add_page()
    
    # Title Info
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True, align='R')
    pdf.cell(200, 10, txt=f"Sector: {sector}", ln=True, align='L')
    
    pdf.ln(10)
    
    # Total Score
    pdf.set_font("Arial", "B", 24)
    color = (220, 53, 69) if results['total_score'] < 40 else (239, 183, 0) if results['total_score'] < 70 else (40, 167, 69)
    pdf.set_text_color(*color)
    pdf.cell(0, 15, txt=f"Total Score: {int(results['total_score'])}/100", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=f"Level: {results['level']}", ln=True, align='C')
    
    pdf.ln(10)
    
    # Recommendations
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, txt="Strategic Recommendation:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=results['recommendation'])
    
    pdf.ln(10)
    
    # Breakdown
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, txt="Dimension Breakdown:", ln=True)
    pdf.set_font("Arial", size=11)
    
    for dim_id, data in results['dimensions'].items():
        pdf.cell(100, 10, txt=f"{data['name']}:", border=0)
        pdf.cell(50, 10, txt=f"{int(data['score'])}/100", border=0, ln=True)
        
    pdf.ln(10)
    
    # Specific Actions
    if results.get('detailed_recommendations'):
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, txt="Action Plan:", ln=True)
        pdf.set_font("Arial", size=10)
        for rec in results['detailed_recommendations']:
            pdf.set_text_color(0, 123, 255)
            pdf.cell(0, 8, txt=f"- {rec['action']}: {rec['detail']}", ln=True)

    # --- EU AI ACT WARNING ---
    # Check if Governance exists and is low
    gov_data = results['dimensions'].get('governance') or results['dimensions'].get('ethics') # Fallback
    if gov_data and gov_data['score'] < 50:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(220, 53, 69) # Red
        pdf.cell(0, 10, txt="WARNING: EU AI ACT COMPLIANCE WARNING", ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        warning_text = (
            "Your Governance score is critical. According to the EU AI Act, "
            "insufficient human oversight and risk management may lead to significant "
            "penalties (up to 7% of global turnover). Immediate action required."
        )
        pdf.multi_cell(0, 6, txt=warning_text)
    # Output
    # Return bytes explicitly
    try:
        return pdf.output(dest='S').encode('latin-1')
    except AttributeError:
        # Fallback if it's already bytes or bytearray that needs casting
        data = pdf.output(dest='S')
        if isinstance(data, bytearray):
            return bytes(data)
        return data
