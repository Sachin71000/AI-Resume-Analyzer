import re
from typing import Dict, List
from dataclasses import dataclass
from spellchecker import SpellChecker
import textstat

@dataclass
class ATSIssue:
    severity: str
    category: str
    message: str
    fix_suggestion: str

class ATSScorer:
    def __init__(self):
        self.spell_checker = SpellChecker()

    def score(self, resume_text: str, jd_text: str, sections: Dict[str, str], skills_data: Dict, quality_data: Dict) -> Dict:
        """
        Calculate ATS compatibility score (0-100) based on 10 weighted factors.
        """
        issues = []
        total_score = 0
        
        # 1. Keyword Match (20 points maximum)
        match_pct = skills_data.get('match_percentage', 0)
        kw_score = min(20, (match_pct / 100.0) * 20)
        total_score += kw_score
        if match_pct < 60:
            issues.append(ATSIssue("high", "keywords", "Low keyword match with Job Description.", f"Ensure you include more skills from the JD. Current match: {match_pct}%"))

        # 2. Standard Headings (10 points maximum)
        std_headings = {'experience', 'skills', 'education', 'summary', 'projects'}
        detected_sections = set(sections.keys())
        found_std = detected_sections.intersection(std_headings)
        heading_score = min(10, len(found_std) * 3.33)
        total_score += heading_score
        
        non_standard = detected_sections - std_headings
        if non_standard:
            issues.append(ATSIssue("medium", "headings", f"Potentially non-standard headings detected: {', '.join(non_standard)}", "Use standard headings like 'Experience', 'Education', 'Skills' for better ATS parsing."))
        if 'experience' not in detected_sections:
            issues.append(ATSIssue("high", "headings", "Missing 'Experience' or 'Work History' heading.", "This is critical for ATS parsing. Add a standard Experience section."))

        # 3. Contact Info (10 points maximum)
        contact_info = quality_data.get('contact_info', {})
        contact_score = 0
        if contact_info.get('email'): contact_score += 4
        if contact_info.get('phone'): contact_score += 4
        if contact_info.get('linkedin'): contact_score += 2
        total_score += contact_score
        
        if not contact_info.get('email') and not contact_info.get('phone'):
            issues.append(ATSIssue("high", "contact", "Missing basic contact information.", "Ensure your email and phone number are clearly listed at the top."))

        # 4. Formatting checks (10 points max)
        fmt_score = 10
        tab_count = resume_text.count('\t')
        if tab_count > 20:
            fmt_score -= 5
            issues.append(ATSIssue("medium", "formatting", "Many tab characters detected.", "Heavy use of tabs or columns can confuse an ATS. Prefer a simple, single-column layout."))
        total_score += max(0, fmt_score)

        # 5. Skill Placement (5 points max)
        sp_score = 0
        if 'skills' in sections:
            sp_score = 5
        else:
             issues.append(ATSIssue("medium", "keywords", "No dedicated Skills section found.", "A dedicated Skills section helps the ATS easily categorize your proficiencies."))
        total_score += sp_score

        # 6. Keyword Density (10 points max)
        kd_score = 10
        missing = skills_data.get('missing', [])
        critical_missing = [s for s in missing if s.get('importance') == 'critical']
        if len(critical_missing) > 0:
             kd_score -= min(10, len(critical_missing) * 2)
             issues.append(ATSIssue("high", "density", f"Missing {len(critical_missing)} critical keywords.", "Ensure critical terms from the JD appear at least once in your resume text."))
        total_score += max(0, kd_score)

        # 7. File Parsing Quality (10 points max)
        fp_score = 10
        if '\ufffd' in resume_text:
            fp_score -= 5
            issues.append(ATSIssue("high", "formatting", "Garbled characters detected.", "The ATS may not be able to read your text. Avoid complex fonts or non-standard PDFs."))
        if len(resume_text.strip()) < 50:
            fp_score = 0
            issues.append(ATSIssue("high", "formatting", "Very little text extracted.", "The document might be an image-based PDF. Ensure it is text-searchable."))
        total_score += max(0, fp_score)
        
        # 8. Spelling (10 points max)
        words = re.findall(r'\b[a-zA-Z]+\b', resume_text)
        words_to_check = [w.lower() for w in words if len(w) > 3][:100]
        misspelled = self.spell_checker.unknown(words_to_check)
        error_count = len(misspelled)
        spell_score = max(0, 10 - (error_count // 2))
        if error_count > 5:
            issues.append(ATSIssue("medium", "spelling", f"Potential spelling errors detected ({error_count}+).", "Review your resume for typos. Ensure all technical terms are spelled correctly."))
        total_score += spell_score

        # 9. Readability (10 points max)
        try:
            readability = textstat.flesch_kincaid_grade(resume_text)
            read_score = 10
            if readability > 16:
                read_score -= 5
                issues.append(ATSIssue("medium", "readability", "Text is very complex.", "Simplify your sentence structure. Aim for a 10th-12th grade reading level."))
            elif readability < 6:
                read_score -= 5
                issues.append(ATSIssue("medium", "readability", "Text may be too simple.", "Use more professional phrasing and varied vocabulary."))
            total_score += max(0, read_score)
        except Exception:
            total_score += 10 

        # 10. Bullet Structure (5 points max)
        bullet_score = 5
        bullets = re.findall(r'^[•\-\*]\s+([a-zA-Z]+)', resume_text, re.MULTILINE)
        if not bullets and 'experience' in sections and len(sections['experience']) > 100:
            bullet_score -= 5
            issues.append(ATSIssue("medium", "formatting", "Few bullet points detected.", "Use bullet points in your experience section rather than long paragraphs for better ATS parsing."))
        total_score += max(0, bullet_score)

        return {
            "score": min(100, round(total_score, 1)),
            "issues": [vars(iss) for iss in issues]
        }
