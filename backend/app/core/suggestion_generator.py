from typing import Dict, List

class SuggestionGenerator:
    @staticmethod
    def generate(skills_data: Dict, quality_data: Dict, sections_data: Dict, bullet_data: Dict = None, exp_data: Dict = None) -> List[Dict]:
        """
        Generate rule-based suggestions from analysis results.
        Returns list of: { category, priority, suggestion }
        """
        suggestions: List[Dict] = []

        # 1. Missing skills suggestions
        missing = skills_data.get('missing', [])
        for skill in missing[:5]:  # Top 5 missing skills
            importance = skill.get('importance', 'important')
            priority = 'high' if importance == 'critical' else 'medium'
            suggestions.append({
                'category': 'skills',
                'priority': priority,
                'suggestion': f"Add \"{skill['name']}\" to your resume — it's listed as {importance} in the job description.",
            })

        # 2. Quality-based suggestions
        issues = quality_data.get('issues', [])
        for issue in issues:
            priority = 'high' if issue['type'] == 'warning' else 'medium'
            suggestions.append({
                'category': 'quality',
                'priority': priority,
                'suggestion': issue['message'],
            })

        # 3. Section-based suggestions
        missing_required = sections_data.get('missing_required', [])
        for section in missing_required:
            suggestions.append({
                'category': 'structure',
                'priority': 'high',
                'suggestion': f"Add a \"{section.title()}\" section — most ATS systems and recruiters expect this.",
            })

        missing_recommended = sections_data.get('missing_recommended', [])
        for section in missing_recommended:
            suggestions.append({
                'category': 'structure',
                'priority': 'low',
                'suggestion': f"Consider adding a \"{section.title()}\" section to strengthen your resume.",
            })

        # 4. Skill match percentage feedback
        match_pct = skills_data.get('match_percentage', 0)
        if match_pct < 40:
            suggestions.insert(0, {
                'category': 'overall',
                'priority': 'high',
                'suggestion': f"Your skill match is only {match_pct}%. Tailor your resume significantly to match this job description.",
            })
        elif match_pct < 60:
            suggestions.insert(0, {
                'category': 'overall',
                'priority': 'medium',
                'suggestion': f"Your skill match is {match_pct}%. Adding a few key skills could push you over the threshold.",
            })

        # 5. Bullet Analysis Suggestions
        if bullet_data and bullet_data.get('weak_bullets'):
            for b in bullet_data['weak_bullets'][:3]:  # Top 3 weak bullets
                suggestions.append({
                    'category': 'impact',
                    'priority': 'medium',
                    'suggestion': f"Improve bullet: \"{b['text'][:50]}...\" — {' '.join(b['feedback'])}"
                })

        # 6. Experience Grading Suggestions
        if exp_data and not exp_data.get('meets_requirement', True):
            delta = exp_data.get('delta', 0)
            suggestions.append({
                'category': 'experience',
                'priority': 'high',
                'suggestion': f"The job asks for {exp_data['required_yoe']} years of experience, but we only detected {exp_data['detected_yoe']} years. Highlight relevant projects or transferable skills."
            })

        # Sort: high > medium > low
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 1))

        return suggestions
