import json
import os
import re
from typing import List, Dict, Set, Optional

class SkillExtractor:
    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        
        with open(os.path.join(data_dir, 'skills_taxonomy.json'), 'r') as f:
            self.taxonomy = json.load(f)
        
        with open(os.path.join(data_dir, 'synonyms.json'), 'r') as f:
            self.synonyms = json.load(f)
        
        # Load contextual inference map
        contexts_path = os.path.join(data_dir, 'skill_contexts.json')
        if os.path.exists(contexts_path):
            with open(contexts_path, 'r') as f:
                raw_contexts = json.load(f)
                # Filter out comment keys
                self.skill_contexts = {k: v for k, v in raw_contexts.items() if not k.startswith('_')}
        else:
            self.skill_contexts = {}

        # Build a flat lookup: skill_lowercase -> category
        self.skill_to_category: Dict[str, str] = {}
        for category, skills in self.taxonomy.items():
            for skill in skills:
                self.skill_to_category[skill.lower()] = category

        # Determine which skills are multi-word for n-gram matching
        self.multi_word_skills = [s for s in self.skill_to_category if ' ' in s or '.' in s or '-' in s or '/' in s]
        self.single_word_skills = [s for s in self.skill_to_category if ' ' not in s and '.' not in s and '-' not in s and '/' not in s]

        # Build multi-word synonyms (sorted longest-first for greedy matching)
        self.multi_word_synonyms = {k: v for k, v in self.synonyms.items() 
                                     if (' ' in k or '-' in k or '/' in k) and not k.startswith('_')}
        self.single_word_synonyms = {k: v for k, v in self.synonyms.items() 
                                      if ' ' not in k and '-' not in k and '/' not in k and not k.startswith('_')}
        
        # Sort multi-word synonyms by length (longest first) for greedy replacement
        self.sorted_multi_synonyms = sorted(self.multi_word_synonyms.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Sort contextual phrases by length (longest first)
        self.sorted_contexts = sorted(self.skill_contexts.items(), key=lambda x: len(x[0]), reverse=True)

    def _resolve_synonyms(self, text: str) -> str:
        """
        Replace abbreviations / synonyms with canonical names.
        Multi-word synonyms are processed first (longest match), then single-word.
        """
        text_lower = text.lower()
        
        # 1. Multi-word synonym replacement (longest-match-first)
        for synonym, canonical in self.sorted_multi_synonyms:
            # Use word boundary-aware replacement
            pattern = r'(?<![a-z])' + re.escape(synonym) + r'(?![a-z])'
            text_lower = re.sub(pattern, canonical, text_lower)
        
        # 2. Single-word synonym replacement
        words = text_lower.split()
        resolved = []
        for w in words:
            resolved.append(self.single_word_synonyms.get(w, w))
        
        text_resolved = ' '.join(resolved)
        return self._split_compounds(text_resolved)

    def _split_compounds(self, text: str) -> str:
        """
        Splits compound patterns like "python/django" or "c/c++" into "python django"
        to ensure individual tokens are properly extracted.
        """
        # Replace '/' with space if it's between word characters or + (like c++)
        # This handles unknown combinations that aren't in synonyms.json
        return re.sub(r'(?<=[a-z0-9+#])/(?=[a-z0-9+#])', ' ', text)

    def _classify_skill_type(self, category: str) -> str:
        """Return 'hard' or 'soft' based on category."""
        if category == 'soft_skills':
            return 'soft'
        return 'hard'

    def _make_skill_entry(self, canonical: str, category: str, source: str = 'explicit') -> Dict:
        """Create a standardized skill entry dict."""
        return {
            'name': canonical.title() if len(canonical) > 3 else canonical.upper(),
            'category': category,
            'type': self._classify_skill_type(category),
            'source': source
        }

    def extract_skills(self, text: str, source: str = 'explicit') -> List[Dict]:
        """
        Extract skills from text using taxonomy matching + n-gram matching.
        Returns list of dicts: [{ name, category, type, source }]
        """
        text_lower = text.lower()
        text_resolved = self._resolve_synonyms(text_lower)
        found: Dict[str, Dict] = {}  # canonical_name -> {name, category, type, source}

        # 1. Multi-word skill matching (n-grams) — check first to catch "machine learning" etc.
        for skill in self.multi_word_skills:
            # Use word boundary regex for accuracy
            pattern = r'(?:^|[\s,;(])' + re.escape(skill) + r'(?:[\s,;).]|$)'
            if re.search(pattern, text_lower) or re.search(pattern, text_resolved):
                canonical = self.synonyms.get(skill, skill)
                if canonical.startswith('_'):
                    continue
                cat = self.skill_to_category.get(skill, 'tools')
                found[canonical] = self._make_skill_entry(canonical, cat, source)

        # 2. Single-word skill matching
        words_in_text = set(re.findall(r'[a-z0-9#+./]+', text_lower))
        words_in_resolved = set(re.findall(r'[a-z0-9#+./]+', text_resolved))
        all_words = words_in_text | words_in_resolved

        for skill in self.single_word_skills:
            if skill in all_words:
                canonical = self.synonyms.get(skill, skill)
                if isinstance(canonical, str) and canonical.startswith('_'):
                    continue
                cat = self.skill_to_category.get(skill, 'tools')
                found[canonical] = self._make_skill_entry(canonical, cat, source)

        return list(found.values())

    def extract_contextual_skills(self, text: str) -> List[Dict]:
        """
        Infer skills from project descriptions and contextual phrases.
        E.g., "phishing website detection" → infers cybersecurity, phishing, etc.
        Returns list of dicts with source='inferred'.
        """
        text_lower = text.lower()
        found: Dict[str, Dict] = {}

        for phrase, implied_skills in self.sorted_contexts:
            if phrase in text_lower:
                for skill_name in implied_skills:
                    skill_lower = skill_name.lower()
                    cat = self.skill_to_category.get(skill_lower, 'security')
                    if skill_lower not in found:
                        found[skill_lower] = self._make_skill_entry(skill_lower, cat, 'inferred')

        return list(found.values())

    def extract_section_skills(self, sections: Dict[str, str]) -> List[Dict]:
        """
        Extract skills from specific resume sections with appropriate source labels.
        - 'skills' section → source='explicit'
        - 'projects' section → source='project' (both keyword + contextual)
        - 'education' section → source='coursework' (keyword + contextual for coursework)
        - 'experience' section → source='experience' (keyword + contextual)
        - 'certifications' section → source='certification'
        """
        all_found: Dict[str, Dict] = {}

        section_source_map = {
            'skills': 'explicit',
            'projects': 'project',
            'education': 'coursework',
            'experience': 'experience',
            'certifications': 'certification',
        }

        for section_name, section_text in sections.items():
            if not section_text or not section_text.strip():
                continue
            
            source_label = section_source_map.get(section_name, 'explicit')
            
            # Direct keyword extraction from this section
            section_skills = self.extract_skills(section_text, source=source_label)
            for skill in section_skills:
                key = skill['name'].lower()
                # Keep the most specific source (explicit > project > coursework > inferred)
                if key not in all_found:
                    all_found[key] = skill

            # Contextual inference from this section (especially projects & education)
            if section_name in ('projects', 'education', 'experience'):
                contextual = self.extract_contextual_skills(section_text)
                for skill in contextual:
                    key = skill['name'].lower()
                    skill['source'] = source_label  # Override with section source
                    if key not in all_found:
                        all_found[key] = skill

        return list(all_found.values())

    def merge_ai_skills(self, existing_skills: List[Dict], ai_skills: List[Dict]) -> List[Dict]:
        """
        Merges AI-extracted skills into the existing taxonomy-matched skills list.
        AI skills that don't exist are added with source='ai' and a default category.
        """
        existing_map = {s['name'].lower(): s for s in existing_skills}
        
        for ai_skill in ai_skills:
            ai_name = ai_skill.get('name', '').lower()
            if not ai_name:
                continue
                
            canonical = self.synonyms.get(ai_name, ai_name)
            if isinstance(canonical, str) and canonical.startswith('_'):
                continue
            
            if canonical in existing_map:
                existing_map[canonical]['proficiency'] = ai_skill.get('proficiency', 'intermediate')
            else:
                cat = self.skill_to_category.get(canonical, 'tools')
                new_skill = self._make_skill_entry(canonical, cat, source='ai')
                new_skill['proficiency'] = ai_skill.get('proficiency', 'intermediate')
                existing_map[canonical] = new_skill
                
        return list(existing_map.values())

    def compare_skills(self, resume_text: str, jd_text: str, sections: Optional[Dict[str, str]] = None, ai_resume_skills: Optional[List[Dict]] = None) -> Dict:
        """
        Compare skills found in resume vs JD.
        Uses three extraction methods and merges results:
        1. Direct keyword matching on full resume text
        2. Contextual inference on full resume text
        3. Section-aware extraction (if sections provided)
        
        Returns: { found: [...], missing: [...], match_percentage: float, resume_only: [...] }
        """
        # ─── Extract resume skills from multiple sources ───
        all_resume_skills: Dict[str, Dict] = {}

        # Method 1: Direct keyword match on full text
        direct_skills = self.extract_skills(resume_text, source='explicit')
        for skill in direct_skills:
            all_resume_skills[skill['name'].lower()] = skill

        # Method 2: Contextual inference on full text
        contextual_skills = self.extract_contextual_skills(resume_text)
        for skill in contextual_skills:
            key = skill['name'].lower()
            if key not in all_resume_skills:
                all_resume_skills[key] = skill

        # Method 3: Section-aware extraction
        if sections:
            section_skills = self.extract_section_skills(sections)
            for skill in section_skills:
                key = skill['name'].lower()
                if key not in all_resume_skills:
                    all_resume_skills[key] = skill
                elif all_resume_skills[key]['source'] == 'inferred' and skill['source'] != 'inferred':
                    # Upgrade from inferred to a more specific source
                    all_resume_skills[key] = skill

        resume_skills = list(all_resume_skills.values())
        if ai_resume_skills:
            resume_skills = self.merge_ai_skills(resume_skills, ai_resume_skills)

        # ─── Extract JD skills ───
        jd_skills = self.extract_skills(jd_text)
        # Also apply contextual inference to JD
        jd_contextual = self.extract_contextual_skills(jd_text)
        jd_all: Dict[str, Dict] = {}
        for s in jd_skills:
            jd_all[s['name'].lower()] = s
        for s in jd_contextual:
            key = s['name'].lower()
            if key not in jd_all:
                jd_all[key] = s
        jd_skills = list(jd_all.values())

        # ─── Compare ───
        resume_skill_names: Set[str] = {s['name'].lower() for s in resume_skills}
        jd_skill_names: Set[str] = {s['name'].lower() for s in jd_skills}

        found_names = resume_skill_names & jd_skill_names
        missing_names = jd_skill_names - resume_skill_names

        # Build found list with category info and source
        found_list = [s for s in resume_skills if s['name'].lower() in found_names]
        
        # Build missing list — count occurrences in JD to determine importance
        jd_lower = jd_text.lower()
        missing_list = []
        seen_missing = set()
        for s in jd_skills:
            name_lower = s['name'].lower()
            if name_lower in missing_names and name_lower not in seen_missing:
                seen_missing.add(name_lower)
                count = jd_lower.count(name_lower)
                if count >= 3:
                    importance = 'critical'
                elif count >= 1:
                    importance = 'important'
                else:
                    importance = 'nice-to-have'
                missing_list.append({**s, 'importance': importance})

        # Sort missing: critical first, then important, then nice-to-have
        importance_order = {'critical': 0, 'important': 1, 'nice-to-have': 2}
        missing_list.sort(key=lambda x: importance_order.get(x.get('importance', 'nice-to-have'), 2))

        match_pct = 0.0
        if len(jd_skill_names) > 0:
            match_pct = round(len(found_names) / len(jd_skill_names) * 100, 1)

        return {
            'found': found_list,
            'missing': missing_list,
            'match_percentage': match_pct,
            'resume_only': [s for s in resume_skills if s['name'].lower() not in jd_skill_names]
        }
