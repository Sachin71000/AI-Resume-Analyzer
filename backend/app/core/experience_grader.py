import re
from typing import Dict, Any, List

class ExperienceGrader:
    def _extract_years(self, text: str) -> List[float]:
        years = []
        
        # Match patterns like "5+ years", "3-5 years", "10 years"
        patterns = [
            r'(\d+)\s*(?:\+|-(\d+))?\s*years?',
            r'(\d+)\s*yrs?'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    val1 = float(match.group(1))
                    if len(match.groups()) > 1 and match.group(2):
                        val2 = float(match.group(2))
                        years.append((val1 + val2) / 2.0)
                    else:
                        years.append(val1)
                except ValueError:
                    continue
        return years

    def analyze(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        jd_years = self._extract_years(jd_text)
        required_yoe = max(jd_years) if jd_years else 0.0

        res_years = self._extract_years(resume_text)
        # Often resumes list "years of experience" in summary. 
        # Alternatively, if they don't explicitly say it, this might return 0.
        # A more robust solution uses dates, but regex is a good V1.
        detected_yoe = max(res_years) if res_years else 0.0

        # If JD requires 0 years, they meet it.
        # If we couldn't detect resume years but JD requires it, assume false unless we have 0 requirement
        meets_req = detected_yoe >= required_yoe if required_yoe > 0 else True
        
        delta = detected_yoe - required_yoe if required_yoe > 0 else 0.0

        return {
            'required_yoe': required_yoe,
            'detected_yoe': detected_yoe,
            'meets_requirement': meets_req,
            'delta': delta
        }
