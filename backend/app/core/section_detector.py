import re
from typing import Dict, List, Optional

# Common section heading patterns
SECTION_PATTERNS = {
    'contact': [
        r'contact\s*info', r'personal\s*info', r'personal\s*details'
    ],
    'summary': [
        r'summary', r'objective', r'professional\s*summary',
        r'career\s*summary', r'profile', r'about\s*me', r'overview'
    ],
    'education': [
        r'education', r'academic', r'qualification', r'degree',
        r'university', r'college', r'school', r'coursework'
    ],
    'experience': [
        r'experience', r'employment', r'work\s*history', r'professional\s*experience',
        r'work\s*experience', r'career\s*history', r'my\s*journey',
        r'professional\s*background', r'employment\s*history'
    ],
    'skills': [
        r'skills', r'technical\s*skills', r'competencies', r'proficiencies',
        r'core\s*competencies', r'areas\s*of\s*expertise', r'technologies',
        r'tools\s*(?:and|&)\s*technologies'
    ],
    'projects': [
        r'projects', r'portfolio', r'personal\s*projects',
        r'academic\s*projects', r'key\s*projects', r'notable\s*projects'
    ],
    'certifications': [
        r'certification', r'certifications', r'licenses',
        r'professional\s*certifications', r'credentials'
    ],
    'awards': [
        r'awards', r'achievements', r'honors', r'recognition',
        r'accomplishments'
    ],
    'publications': [
        r'publications', r'papers', r'research', r'articles'
    ],
    'references': [
        r'references', r'referees'
    ]
}

class SectionDetector:
    @staticmethod
    def detect_sections(text: str) -> Dict[str, str]:
        """
        Detect resume sections by matching common heading patterns.
        Returns dict: { section_name: section_text }
        """
        lines = text.split('\n')
        sections: List[Dict] = []  # [{name, start_line, pattern_matched}]

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            # Heuristic: section headings are typically short lines (< 60 chars)
            # and often uppercase or title-case
            if len(stripped) > 80:
                continue

            line_lower = stripped.lower()

            for section_name, patterns in SECTION_PATTERNS.items():
                for pattern in patterns:
                    # Match if the line IS the heading or starts with it
                    if re.match(r'^' + pattern + r'[\s:]*$', line_lower) or \
                       re.match(r'^' + pattern + r'\s', line_lower):
                        sections.append({
                            'name': section_name,
                            'start_line': i,
                            'heading': stripped
                        })
                        break
                else:
                    continue
                break

        # Extract text between section headings
        result: Dict[str, str] = {}
        for idx, section in enumerate(sections):
            start = section['start_line'] + 1
            if idx + 1 < len(sections):
                end = sections[idx + 1]['start_line']
            else:
                end = len(lines)
            
            section_text = '\n'.join(lines[start:end]).strip()
            result[section['name']] = section_text

        return result

    @staticmethod
    def get_section_coverage(detected_sections: Dict[str, str]) -> Dict:
        """
        Check which critical sections are present / missing.
        """
        required = ['education', 'experience', 'skills']
        recommended = ['summary', 'projects', 'certifications']
        
        detected_names = set(detected_sections.keys())
        present_required = [s for s in required if s in detected_names]
        missing_required = [s for s in required if s not in detected_names]
        present_recommended = [s for s in recommended if s in detected_names]
        missing_recommended = [s for s in recommended if s not in detected_names]

        total_check = len(required) + len(recommended)
        present_count = len(present_required) + len(present_recommended)
        coverage_score = round(present_count / total_check * 100, 1) if total_check > 0 else 0

        return {
            'detected': list(detected_names),
            'missing_required': missing_required,
            'missing_recommended': missing_recommended,
            'coverage_score': coverage_score
        }
