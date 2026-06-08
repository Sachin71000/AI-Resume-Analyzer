import os
from datetime import datetime
from fpdf import FPDF
from ..models.analysis import Analysis

class PDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(99, 102, 241) # Brand color
        self.cell(0, 10, 'Smart Resume Analyzer', border=0, align='L', ln=1)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', border=0, align='R', ln=1)
        self.line(10, 25, 200, 25)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()} - Smart Resume Analyzer', 0, 0, 'C')

class ExportService:
    @staticmethod
    def safe_str(text: str) -> str:
        if not text:
            return ""
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    @staticmethod
    def generate_pdf(analysis: Analysis) -> str:
        pdf = PDFReport()
        pdf.add_page()
        safe_str = ExportService.safe_str
        
        # Title & filename
        pdf.set_font('helvetica', 'B', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, 'Analysis Report', ln=1)
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0, 8, safe_str(f'Resume: {analysis.resume_filename}'), ln=1)
        
        if analysis.label:
            pdf.set_font('helvetica', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 8, safe_str(f'Label: {analysis.label}'), ln=1)
        
        pdf.ln(5)

        # Overall Score
        pdf.set_font('helvetica', 'B', 24)
        if analysis.overall_score >= 70:
            pdf.set_text_color(16, 185, 129)
        elif analysis.overall_score >= 45:
            pdf.set_text_color(245, 158, 11)
        else:
            pdf.set_text_color(239, 68, 68)
        
        pdf.cell(0, 15, safe_str(f'Overall Match Score: {round(analysis.overall_score, 1)}%'), ln=1)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        # Sub-scores
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Score Breakdown', ln=1)
        pdf.set_font('helvetica', '', 10)
        
        scores = analysis.scores_json
        items = [
            ("Semantic Similarity", scores.get('tfidf_similarity', 0)),
            ("Skill Match", scores.get('skill_match', 0)),
            ("Section Coverage", scores.get('section_coverage', 0)),
            ("Keyword Density", scores.get('keyword_density', 0)),
            ("Resume Quality", scores.get('quality', 0)),
            ("ATS Compatibility", scores.get('ats_compatibility', 0))
        ]
        
        for name, value in items:
            pdf.cell(60, 8, safe_str(name), border=1)
            pdf.cell(30, 8, safe_str(f'{round(value, 1)}%'), border=1, align='R', ln=1)
        
        pdf.ln(10)

        # Skills
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Skills Analysis', ln=1)
        pdf.set_font('helvetica', '', 10)
        
        found = [s['name'] for s in analysis.skills_json.get('found', [])]
        missing = [s['name'] for s in analysis.skills_json.get('missing', [])]
        
        pdf.set_text_color(16, 185, 129) # green
        pdf.multi_cell(0, 6, safe_str(f"[+] Found Skills: {', '.join(found) if found else 'None'}"))
        pdf.ln(2)
        pdf.set_text_color(239, 68, 68) # red
        pdf.multi_cell(0, 6, safe_str(f"[-] Missing Skills: {', '.join(missing) if missing else 'None'}"))
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)

        # ATS Issues
        ats_issues = analysis.ats_json.get('issues', [])
        if ats_issues:
            pdf.set_font('helvetica', 'B', 14)
            pdf.cell(0, 10, 'ATS Issues', ln=1)
            pdf.set_font('helvetica', '', 10)
            
            for issue in ats_issues:
                pdf.set_font('helvetica', 'B', 10)
                pdf.cell(20, 6, safe_str(f"[{issue.get('severity', 'info').upper()}]"), align='L')
                pdf.cell(0, 6, safe_str(issue.get('message', '')), ln=1)
                pdf.set_font('helvetica', '', 10)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 6, safe_str(issue.get('fix_suggestion', '')))
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)
        
        pdf.ln(5)

        # Suggestions
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Actionable Suggestions', ln=1)
        pdf.set_font('helvetica', '', 10)
        
        suggestions = analysis.suggestions_json
        all_suggs = suggestions.get('ai_generated', []) + suggestions.get('rule_based', [])
        
        for sugg in all_suggs:
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(0, 6, safe_str(f"- {sugg.get('category', '').title()} (Priority: {sugg.get('priority', '')})"), ln=1)
            pdf.set_font('helvetica', '', 10)
            pdf.multi_cell(0, 6, safe_str(sugg.get('suggestion', '')))
            
            if sugg.get('example'):
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 6, safe_str(f"Example: {sugg.get('example')}"))
                pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

        # Save file to temp location
        import tempfile
        fd, file_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        pdf.output(file_path)
        
        return file_path
