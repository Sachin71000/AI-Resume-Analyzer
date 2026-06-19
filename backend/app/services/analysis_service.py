import os
import traceback
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from flask import current_app

from ..core.parser import ResumeParser
from ..core.preprocessor import TextPreprocessor
from ..core.matching_engine import MatchingEngine
from ..core.skill_extractor import SkillExtractor
from ..core.section_detector import SectionDetector
from ..core.quality_analyzer import QualityAnalyzer
from ..core.suggestion_generator import SuggestionGenerator
from ..core.ats_scorer import ATSScorer
from ..core.bullet_analyzer import BulletAnalyzer
from ..core.experience_grader import ExperienceGrader

from .gemini_service import GeminiService
from ..models.analysis import Analysis
from ..extensions import db

import numpy as np

def _sanitize_for_db(obj):
    """Recursively convert numpy types to native Python types for PostgreSQL."""
    if isinstance(obj, dict):
        return {k: _sanitize_for_db(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_db(v) for v in obj]
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

# Lazy-loaded singletons — initialized on first request to avoid OOM at gunicorn startup
# (Render free tier is 512MB; loading 6 NLP models at import time kills the worker)
_preprocessor = None
_skill_extractor = None
_quality_analyzer = None
_ats_scorer = None
_bullet_analyzer = None
_experience_grader = None

def _get_preprocessor():
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = TextPreprocessor()
    return _preprocessor

def _get_skill_extractor():
    global _skill_extractor
    if _skill_extractor is None:
        _skill_extractor = SkillExtractor()
    return _skill_extractor

def _get_quality_analyzer():
    global _quality_analyzer
    if _quality_analyzer is None:
        _quality_analyzer = QualityAnalyzer()
    return _quality_analyzer

def _get_ats_scorer():
    global _ats_scorer
    if _ats_scorer is None:
        _ats_scorer = ATSScorer()
    return _ats_scorer

def _get_bullet_analyzer():
    global _bullet_analyzer
    if _bullet_analyzer is None:
        _bullet_analyzer = BulletAnalyzer()
    return _bullet_analyzer

def _get_experience_grader():
    global _experience_grader
    if _experience_grader is None:
        _experience_grader = ExperienceGrader()
    return _experience_grader

class AnalysisService:
    @staticmethod
    def run_analysis(file_path: str, filename: str, jd_text: str, parent_id: str = None) -> dict:
        """
        Orchestrates the entire resume analysis pipeline.
        Extracts logic from the API route.
        """
        try:
            # Lazy-load NLP singletons on first request
            preprocessor = _get_preprocessor()
            skill_extractor = _get_skill_extractor()
            quality_analyzer = _get_quality_analyzer()
            ats_scorer = _get_ats_scorer()
            bullet_analyzer = _get_bullet_analyzer()
            experience_grader = _get_experience_grader()

            # 1. Parse Document
            parsed_data = ResumeParser.parse(file_path)
            resume_raw_text = parsed_data['text']

            # 2. Preprocess
            resume_processed = preprocessor.preprocess(resume_raw_text)
            jd_processed = preprocessor.preprocess(jd_text)

            # 3. Cache Check
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            content_hash = hashlib.md5((resume_raw_text + jd_text).encode('utf-8')).hexdigest()
            cache_file = os.path.join(cache_dir, f"{content_hash}.json")

            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cached_result = json.load(f)
                    
                    # Create new analysis record but reuse heavy computation
                    analysis = Analysis(
                        resume_filename=filename,
                        resume_text=resume_raw_text,
                        jd_text=jd_text,
                        overall_score=float(cached_result['scores']['overall']),
                        scores_json=cached_result['scores'],
                        skills_json=cached_result['skills'],
                        sections_json=cached_result['sections'],
                        quality_json=cached_result['quality'],
                        ats_json=cached_result['ats'],
                        suggestions_json=cached_result['suggestions'],
                        parent_analysis_id=parent_id
                    )
                    db.session.add(analysis)
                    db.session.commit()
                    
                    cached_result['analysis_id'] = analysis.id
                    cached_result['timestamp'] = analysis.created_at.isoformat()
                    cached_result['resume_filename'] = filename
                    return cached_result
                except Exception as e:
                    pass # Fallback to running full analysis if cache read fails

            # 4. Initialize Gemini
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                api_key = os.environ.get('GEMINI_API_KEY')
            
            gemini_service = GeminiService(api_key=api_key)

            # 5. Detect Sections (BEFORE skill extraction so sections are available)
            sections = SectionDetector.detect_sections(resume_raw_text)
            sections_coverage = SectionDetector.get_section_coverage(sections)

            # 6. Parse JD and Extract Skills using Gemini IN PARALLEL
            parsed_jd = None
            ai_resume_skills = []

            with ThreadPoolExecutor(max_workers=2) as executor:
                future_jd = executor.submit(gemini_service.parse_jd_requirements, jd_text)
                future_skills = executor.submit(gemini_service.extract_skills_from_text, resume_raw_text)
                
                try:
                    parsed_jd = future_jd.result(timeout=30)
                except Exception:
                    pass
                try:
                    ai_resume_skills = future_skills.result(timeout=30)
                except Exception:
                    pass

            # 7. Extract Skills (section-aware + contextual + keyword)
            jd_compare_text = jd_processed['raw_clean']
            
            # If Gemini parsed the JD, enrich with extracted required/preferred skills
            if parsed_jd and hasattr(parsed_jd, 'required_skills'):
                jd_compare_text += ' ' + ' '.join(parsed_jd.required_skills)
                if hasattr(parsed_jd, 'preferred_skills'):
                    jd_compare_text += ' ' + ' '.join(parsed_jd.preferred_skills)

            skills_data = skill_extractor.compare_skills(
                resume_text=resume_processed['raw_clean'],
                jd_text=jd_compare_text,
                sections=sections,
                ai_resume_skills=ai_resume_skills
            )

            # 7. Quality Analysis
            quality_data = quality_analyzer.analyze(resume_raw_text, sections)

            # 8. ATS Compatibility Score
            ats_data = ats_scorer.score(resume_raw_text, jd_text, sections, skills_data, quality_data)

            # 9. Hybrid Match Score
            semantic_score = preprocessor.compute_similarity(resume_processed['raw_clean'], jd_compare_text)
            
            match_result = MatchingEngine.compute_match(
                resume_text=resume_processed['processed'],
                jd_text=jd_processed['processed'],
                skill_match_pct=skills_data['match_percentage'],
                section_coverage_pct=sections_coverage['coverage_score'],
                semantic_score=semantic_score
            )

            # 10. Generate Suggestions (Rule-based)
            bullet_data = bullet_analyzer.analyze(resume_raw_text)
            exp_data = experience_grader.analyze(resume_raw_text, jd_text)
            
            rule_based_suggestions = SuggestionGenerator.generate(
                skills_data=skills_data,
                quality_data=quality_data,
                sections_data=sections_coverage,
                bullet_data=bullet_data,
                exp_data=exp_data
            )

            # 11. Generate Suggestions (AI via Gemini)
            scores_dict = {
                "overall": match_result.overall_score,
                "skill_match": match_result.skill_match_score,
                "ats_compatibility": ats_data['score']
            }
            ai_suggestions = gemini_service.generate_ai_suggestions(
                resume_text=resume_raw_text,
                jd_text=jd_text,
                scores=scores_dict,
                missing_skills=skills_data['missing']
            )

            # Deduplicate or merge (simplistic merge for now)
            suggestions_json = {
                "rule_based": rule_based_suggestions,
                "ai_generated": ai_suggestions
            }

            # Build response
            scores_json = {
                "overall": match_result.overall_score,
                "tfidf_similarity": match_result.tfidf_score,
                "semantic_similarity": match_result.semantic_score,
                "skill_match": match_result.skill_match_score,
                "section_coverage": match_result.section_coverage_score,
                "keyword_density": match_result.keyword_density_score,
                "quality": quality_data['score'],
                "ats_compatibility": ats_data['score']
            }

            skills_json = {
                "found": skills_data['found'],
                "missing": skills_data['missing'],
                "match_percentage": skills_data['match_percentage']
            }

            sections_json = {
                "detected": sections_coverage['detected'],
                "missing_required": sections_coverage['missing_required'],
                "missing_recommended": sections_coverage['missing_recommended'],
                "coverage_score": sections_coverage['coverage_score']
            }

            quality_json = {
                "score": quality_data['score'],
                "word_count": quality_data['word_count'],
                "length_status": quality_data['length_status'],
                "action_verb_percentage": quality_data['action_verb_percentage'],
                "strong_verb_count": quality_data['strong_verb_count'],
                "weak_verb_count": quality_data['weak_verb_count'],
                "has_metrics": quality_data['has_metrics'],
                "metrics_count": quality_data['metrics_count'],
                "contact_info": quality_data['contact_info'],
                "issues": quality_data['issues']
            }

            # Build response
            final_result = {
                "scores": scores_json,
                "skills": skills_json,
                "sections": sections_json,
                "quality": quality_json,
                "ats": ats_data,
                "suggestions": suggestions_json
            }
            
            # Save to cache
            try:
                with open(cache_file, 'w') as f:
                    json.dump(final_result, f)
            except Exception:
                pass

            # Save to DB — sanitize numpy types for PostgreSQL compatibility
            analysis = Analysis(
                resume_filename=filename,
                resume_text=resume_raw_text,
                jd_text=jd_text,
                overall_score=float(match_result.overall_score),
                scores_json=_sanitize_for_db(scores_json),
                skills_json=_sanitize_for_db(skills_json),
                sections_json=_sanitize_for_db(sections_json),
                quality_json=_sanitize_for_db(quality_json),
                ats_json=_sanitize_for_db(ats_data),
                suggestions_json=_sanitize_for_db(suggestions_json),
                parent_analysis_id=parent_id
            )
            db.session.add(analysis)
            db.session.commit()

            final_result["analysis_id"] = analysis.id
            final_result["timestamp"] = analysis.created_at.isoformat()
            final_result["resume_filename"] = filename
            
            return final_result

        except Exception as e:
            traceback.print_exc()
            raise e
