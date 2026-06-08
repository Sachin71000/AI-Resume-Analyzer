import re
import json
import os
from typing import Dict, List

class QualityAnalyzer:
    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        with open(os.path.join(data_dir, 'action_verbs.json'), 'r') as f:
            self.action_verbs = json.load(f)
        
        # Flatten all verbs for quick lookup
        self.all_verbs = set()
        self.strong_verbs = set(self.action_verbs.get('strong', []))
        self.moderate_verbs = set(self.action_verbs.get('moderate', []))
        self.weak_verbs = set(self.action_verbs.get('weak', []))
        self.all_verbs = self.strong_verbs | self.moderate_verbs | self.weak_verbs

    def analyze(self, resume_text: str, sections: Dict[str, str]) -> Dict:
        """
        Analyze resume quality: length, action verbs, metrics, contact info, etc.
        Returns a quality report dict.
        """
        issues: List[Dict] = []
        word_count = len(resume_text.split())

        # 1. Length check
        length_status = 'good'
        if word_count < 200:
            length_status = 'too_short'
            issues.append({'type': 'warning', 'message': 'Resume is very short. Aim for at least 400 words.'})
        elif word_count < 400:
            length_status = 'short'
            issues.append({'type': 'info', 'message': 'Resume could be more detailed. Aim for 400-800 words for a 1-page resume.'})
        elif word_count > 1200:
            length_status = 'long'
            issues.append({'type': 'info', 'message': 'Resume is quite long. Consider trimming to the most relevant content.'})

        # 2. Action verb analysis
        lines = resume_text.split('\n')
        bullet_lines = [l.strip() for l in lines if l.strip().startswith(('-', '•', '●', '▪', '*'))]
        # Also consider lines that start with a capital letter after removing bullets
        action_verb_count = 0
        strong_count = 0
        weak_count = 0
        
        for line in lines:
            clean_line = re.sub(r'^[\s\-•●▪*]+', '', line).strip()
            if not clean_line:
                continue
            first_word = clean_line.split()[0].lower().rstrip('ed').rstrip('ing') if clean_line.split() else ''
            first_word_full = clean_line.split()[0].lower() if clean_line.split() else ''
            
            if first_word_full in self.all_verbs or first_word in self.all_verbs:
                action_verb_count += 1
                if first_word_full in self.strong_verbs:
                    strong_count += 1
                elif first_word_full in self.weak_verbs:
                    weak_count += 1

        action_verb_pct = round(action_verb_count / max(len(lines), 1) * 100, 1)

        if action_verb_pct < 10:
            issues.append({'type': 'warning', 'message': 'Use more action verbs to start your bullet points (e.g., "Developed", "Led", "Optimized").'})
        if weak_count > strong_count and weak_count > 2:
            issues.append({'type': 'info', 'message': 'Replace weak verbs (helped, used, worked) with stronger alternatives (engineered, spearheaded, architected).'})

        # 3. Quantification / metrics detection
        metrics_patterns = [
            r'\d+\s*%',           # percentages
            r'\$[\d,]+',          # dollar amounts
            r'\d+x\b',           # multipliers
            r'\d+\s*(?:users|customers|clients|projects|teams|people|employees)',  # counts
            r'(?:increased|decreased|improved|reduced|grew|saved).*\d+',  # action + number
        ]
        metrics_count = 0
        for pattern in metrics_patterns:
            metrics_count += len(re.findall(pattern, resume_text, re.IGNORECASE))
        
        has_metrics = metrics_count > 0
        if not has_metrics:
            issues.append({'type': 'warning', 'message': 'Add quantifiable metrics to your achievements (e.g., "Improved performance by 40%", "Managed a team of 8").'})
        elif metrics_count < 3:
            issues.append({'type': 'info', 'message': f'Found {metrics_count} quantified achievement(s). Try to add metrics to more bullet points.'})

        # 4. Contact info check
        has_email = bool(re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', resume_text))
        has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text))
        has_linkedin = bool(re.search(r'linkedin', resume_text, re.IGNORECASE))
        has_github = bool(re.search(r'github', resume_text, re.IGNORECASE))

        contact_items = sum([has_email, has_phone, has_linkedin, has_github])
        if not has_email:
            issues.append({'type': 'warning', 'message': 'No email address detected. Always include your email.'})
        if not has_phone:
            issues.append({'type': 'info', 'message': 'Consider adding a phone number.'})
        if not has_linkedin:
            issues.append({'type': 'info', 'message': 'Consider adding your LinkedIn profile URL.'})

        # 5. Section completeness 
        section_names = set(sections.keys())
        if 'education' not in section_names:
            issues.append({'type': 'warning', 'message': 'No Education section detected. Most roles require this.'})
        if 'experience' not in section_names:
            issues.append({'type': 'warning', 'message': 'No Experience section detected. This is critical for most roles.'})
        if 'skills' not in section_names:
            issues.append({'type': 'info', 'message': 'Consider adding a dedicated Skills section for ATS compatibility.'})
        if 'certifications' not in section_names:
            issues.append({'type': 'info', 'message': 'Consider adding a Certifications section if you have relevant certifications.'})

        # 6. Compute overall quality score
        quality_score = 100
        for issue in issues:
            if issue['type'] == 'warning':
                quality_score -= 10
            elif issue['type'] == 'info':
                quality_score -= 3
        quality_score = max(quality_score, 0)

        return {
            'score': quality_score,
            'word_count': word_count,
            'length_status': length_status,
            'action_verb_percentage': action_verb_pct,
            'strong_verb_count': strong_count,
            'weak_verb_count': weak_count,
            'has_metrics': has_metrics,
            'metrics_count': metrics_count,
            'contact_info': {
                'email': has_email,
                'phone': has_phone,
                'linkedin': has_linkedin,
                'github': has_github
            },
            'issues': issues
        }
