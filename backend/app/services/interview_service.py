"""
InterviewService — Fixed:
  - B4: Replaced deprecated Model.query.get() with db.session.get()
  - B11: Target role now inferred from JD analysis or analysis data, not hardcoded
  - B6: GeminiService created only once per call via lazy singleton pattern
  - Input validation added for answer submission
"""
import logging
from datetime import datetime, timezone
from flask import current_app
from ..models.analysis import Analysis
from ..models.interview import InterviewSession, InterviewAnswer
from ..extensions import db
from ..services.gemini_service import GeminiService
from ..core.interview_coach.question_generator import QuestionGenerator
from ..core.interview_coach.evaluator import Evaluator
from ..core.interview_coach.feedback import FeedbackGenerator
from ..core.interview_coach.session_manager import SessionManager

logger = logging.getLogger(__name__)

# ── App-context service cache (B6 FIX) ─────────────────────────────────────
# Cache service instances per Flask app context to avoid re-initializing on
# every request. Uses a dict keyed by api_key to support key rotation.
_service_cache: dict = {}


class InterviewService:
    @staticmethod
    def _get_services():
        """
        B6 FIX: Returns cached service instances within the current request context.
        Gemini client is created once per unique API key, not per request.
        """
        api_key = current_app.config.get("GEMINI_API_KEY") or ""
        cache_key = f"interview_services_{api_key[:8]}"  # safe prefix for cache key

        # Use Flask's app context extensions dict as a per-request cache
        if not hasattr(current_app, "_interview_service_cache"):
            current_app._interview_service_cache = {}

        if cache_key not in current_app._interview_service_cache:
            gemini_service = GeminiService(api_key=api_key if api_key else None)
            q_generator = QuestionGenerator(gemini_service=gemini_service)
            evaluator = Evaluator(gemini_service=gemini_service)
            feedback_gen = FeedbackGenerator(gemini_service=gemini_service)
            session_mgr = SessionManager(question_generator=q_generator)

            current_app._interview_service_cache[cache_key] = {
                "session_mgr": session_mgr,
                "evaluator": evaluator,
                "feedback_gen": feedback_gen,
            }

        cache = current_app._interview_service_cache[cache_key]
        return cache["session_mgr"], cache["evaluator"], cache["feedback_gen"]

    @staticmethod
    def start_interview_session(
        analysis_id: str,
        difficulty: str = "medium",
        question_count: int = 10,
        include_types: list = None,
        target_role: str = None,
    ) -> dict:
        """
        Starts a mock interview session:
        1. Loads the analysis record.
        2. Infers target role from JD data if not provided (B11 FIX).
        3. Invokes session manager to create a new session.
        """
        # B4 FIX: use db.session.get() instead of deprecated Model.query.get()
        analysis = db.session.get(Analysis, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis record with ID '{analysis_id}' not found.")

        skills_found = analysis.skills_json.get("found", [])

        # B11 FIX: Smarter role inference instead of always "Software Engineer"
        if not target_role:
            target_role = InterviewService._infer_target_role(analysis)

        session_mgr, _, _ = InterviewService._get_services()

        session = session_mgr.create_session(
            analysis_id=analysis_id,
            target_role=target_role,
            skills_found=skills_found,
            resume_text=analysis.resume_text,
            difficulty=difficulty,
            question_count=int(question_count),
            include_types=include_types,
        )

        first_q = session_mgr.get_current_question(session.id)

        return {
            "session_id": session.id,
            "total_questions": session.total_questions,
            "first_question": first_q,
            "target_role": target_role,
            "difficulty": difficulty,
        }

    @staticmethod
    def _infer_target_role(analysis) -> str:
        """
        B11 FIX: Infer target role from analysis data.
        Priority order:
          1. JD requirements parsed by Gemini (analysis.jd_requirements_json)
          2. Dominant skills heuristic
          3. Default "Software Engineer"
        """
        # Check if JD analysis has a role title
        try:
            jd_data = getattr(analysis, "jd_requirements_json", None)
            if jd_data and isinstance(jd_data, dict):
                title = jd_data.get("title")
                if title and len(title) > 2:
                    return title
        except Exception:
            pass

        # Heuristic: infer from dominant skills
        try:
            skills = analysis.skills_json.get("found", [])
            skill_names = [
                (s.get("name") if isinstance(s, dict) else str(s)).lower()
                for s in skills
            ]
            if any(s in skill_names for s in ["tensorflow", "pytorch", "scikit-learn", "keras"]):
                return "Machine Learning Engineer"
            if any(s in skill_names for s in ["react", "vue", "angular", "typescript", "css"]):
                return "Frontend Engineer"
            if any(s in skill_names for s in ["aws", "docker", "kubernetes", "terraform", "ansible"]):
                return "DevOps / Cloud Engineer"
            if any(s in skill_names for s in ["sql", "postgresql", "spark", "pandas", "tableau"]):
                return "Data Engineer"
            if "android" in skill_names or "ios" in skill_names or "swift" in skill_names:
                return "Mobile Engineer"
        except Exception:
            pass

        return "Software Engineer"

    @staticmethod
    def submit_question_answer(
        session_id: str,
        user_answer: str,
        time_taken_seconds: int = None,
    ) -> dict:
        """Submits answer for current question and returns the next question."""
        if not session_id:
            raise ValueError("session_id is required")

        # Input validation
        user_answer = (user_answer or "").strip()
        if len(user_answer) > 5000:
            user_answer = user_answer[:5000]

        session_mgr, _, _ = InterviewService._get_services()

        submit_res = session_mgr.submit_answer(
            session_id=session_id,
            user_answer=user_answer,
            time_taken_seconds=time_taken_seconds,
        )

        if not submit_res:
            raise ValueError(f"Failed to record answer for session '{session_id}'")

        next_q = None
        if not submit_res["is_last"]:
            next_q = session_mgr.get_current_question(session_id)

        return {
            "received": True,
            "next_question": next_q,
            "progress": submit_res["progress"],
            "is_last": submit_res["is_last"],
        }

    @staticmethod
    def evaluate_completed_session(session_id: str) -> dict:
        """
        Orchestrates batch answer evaluation and feedback generation:
        1. Loads the session and all answers.
        2. Evaluates each answer in batch.
        3. Generates overall synthesis report.
        4. Saves results in database.
        5. Updates session status to 'completed'.
        """
        # B4 FIX
        session = db.session.get(InterviewSession, session_id)
        if not session:
            raise ValueError(f"Session with ID '{session_id}' not found.")

        if session.status == "completed" and session.results_json:
            results = session.results_json.copy()
            results["session_id"] = session.id
            return results

        answers = (
            InterviewAnswer.query
            .filter_by(session_id=session_id)
            .order_by(InterviewAnswer.question_index)
            .all()
        )
        if not answers:
            raise ValueError(f"No answers found for session '{session_id}' to evaluate.")

        session_mgr, evaluator, feedback_gen = InterviewService._get_services()

        # Batch evaluate each answer
        evaluated_list = []
        q_list = session.questions_json

        for ans in answers:
            idx = ans.question_index - 1
            curr_q = q_list[idx] if idx < len(q_list) else {}

            ideal = ans.ideal_answer or curr_q.get("ideal_answer", "")
            kws = curr_q.get("keywords", [])

            logger.info(f"Evaluating Q{ans.question_index}: {ans.question_text[:40]}...")
            eval_res = evaluator.evaluate_answer(
                question_text=ans.question_text,
                user_answer=ans.user_answer,
                ideal_answer=ideal,
                keywords=kws,
            )

            ans.score = eval_res["score"]
            ans.tfidf_score = eval_res["tfidf_score"]
            ans.keyword_score = eval_res["keyword_score"]
            ans.gemini_score = eval_res["gemini_score"]
            ans.feedback_json = {
                "verdict": eval_res["verdict"],
                "strengths": eval_res["strengths"],
                "weaknesses": eval_res["weaknesses"],
                "improvement_tip": eval_res["improvement_tip"],
                "keywords_found": eval_res["keywords_found"],
            }

            ans_dict = ans.to_dict()
            ans_dict["feedback"] = ans.feedback_json
            ans_dict["metrics"] = eval_res["metrics"]
            evaluated_list.append(ans_dict)

        # Generate overall session report
        report = feedback_gen.generate_session_report(
            evaluated_answers=evaluated_list,
            target_role=session.target_role or "Software Engineer",
        )

        # Update session record
        session.overall_score = report["overall_score"]
        session.results_json = report
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)

        db.session.commit()

        report_copy = report.copy()
        report_copy["session_id"] = session.id
        report_copy["questions"] = evaluated_list
        return report_copy

    @staticmethod
    def get_session_results(session_id: str) -> dict:
        """Retrieves results of a completed session."""
        # B4 FIX
        session = db.session.get(InterviewSession, session_id)
        if not session:
            raise ValueError(f"Session with ID '{session_id}' not found.")

        if session.status != "completed":
            return {
                "session_id": session.id,
                "status": session.status,
                "overall_score": None,
                "results": None,
            }

        answers = (
            InterviewAnswer.query
            .filter_by(session_id=session_id)
            .order_by(InterviewAnswer.question_index)
            .all()
        )
        answers_dict = [a.to_dict() for a in answers]

        report = session.results_json.copy() if session.results_json else {}
        report["session_id"] = session.id
        report["questions"] = answers_dict
        report["status"] = session.status
        return report

    @staticmethod
    def get_interview_history(analysis_id: str = None) -> list:
        """Lists historical mock interviews, optionally filtered by analysis_id."""
        query = InterviewSession.query
        if analysis_id:
            query = query.filter_by(analysis_id=analysis_id)
        sessions = query.order_by(InterviewSession.started_at.desc()).all()
        return [s.to_summary() for s in sessions]

    @staticmethod
    def delete_interview_session(session_id: str) -> bool:
        """Deletes a session and its answers."""
        # B4 FIX
        session = db.session.get(InterviewSession, session_id)
        if not session:
            return False
        db.session.delete(session)
        db.session.commit()
        return True
