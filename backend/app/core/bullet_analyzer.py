import re
import os
import json
from typing import Dict, List, Any

class BulletAnalyzer:
    def __init__(self, action_verbs: Dict[str, List[str]] = None):
        if action_verbs is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
            with open(os.path.join(data_dir, 'action_verbs.json'), 'r') as f:
                self.action_verbs = json.load(f)
        else:
            self.action_verbs = action_verbs
            
        self.all_verbs = set(self.action_verbs.get('strong', [])) | \
                         set(self.action_verbs.get('moderate', [])) | \
                         set(self.action_verbs.get('weak', []))

    def extract_bullets(self, text: str) -> List[str]:
        bullets = []
        for line in text.split('\n'):
            line = line.strip()
            if re.match(r'^[\u2022\-\*]\s+', line):
                bullets.append(re.sub(r'^[\u2022\-\*]\s+', '', line).strip())
            elif line.startswith('●') or line.startswith('▪'):
                bullets.append(re.sub(r'^[●▪]\s*', '', line).strip())
        return [b for b in bullets if len(b) > 20] # Only substantive bullets

    def analyze_bullet(self, bullet: str) -> Dict[str, Any]:
        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]+\b', bullet)]
        
        # Check for Action Verb
        has_action_verb = False
        if words and (words[0] in self.all_verbs or words[0].rstrip('ed') in self.all_verbs or words[0].rstrip('s') in self.all_verbs):
            has_action_verb = True

        # Check for Metric (Numbers, percentages, multipliers)
        has_metric = bool(re.search(r'\b\d+(\.\d+)?%?|\b(billion|million|thousand|hundred)\b', bullet, re.IGNORECASE))
        
        # Check for Outcome (Resulted in, led to, etc)
        outcome_patterns = r'\b(resulted in|led to|increased|decreased|improved|reduced|achieved|delivered|optimized|saved|generated)\b'
        has_outcome = bool(re.search(outcome_patterns, bullet, re.IGNORECASE))
        
        score = sum([has_action_verb, has_metric, has_outcome])
        
        feedback = []
        if not has_action_verb:
            feedback.append("Missing action verb.")
        if not has_metric:
            feedback.append("Missing metrics.")
        if not has_outcome:
            feedback.append("Missing outcome.")

        return {
            'text': bullet,
            'score': score,
            'has_action_verb': has_action_verb,
            'has_metric': has_metric,
            'has_outcome': has_outcome,
            'feedback': feedback
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        bullets = self.extract_bullets(text)
        if not bullets:
            return {'average_score': 0, 'weak_bullets': [], 'total_bullets': 0}
        
        analyzed = [self.analyze_bullet(b) for b in bullets]
        weak_bullets = [b for b in analyzed if b['score'] <= 1]
        
        avg_score = sum(b['score'] for b in analyzed) / len(analyzed)
        
        return {
            'average_score': avg_score,
            'weak_bullets': weak_bullets,
            'total_bullets': len(bullets)
        }
