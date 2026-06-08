import logging
from datetime import datetime
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

class InterviewService:
    @staticmethod
    def get_services():
        """Helper to initialize singletons or instances safely with active App Context."""
        api_key = current_app.config.get('GEMINI_API_KEY')
        gemini_service = GeminiService(api_key=api_key)
        
        q_generator = QuestionGenerator(gemini_service=gemini_service)
        evaluator = Evaluator(gemini_service=gemini_service)
        feedback_gen = FeedbackGenerator(gemini_service=gemini_service)
        session_mgr = SessionManager(question_generator=q_generator)

        return session_mgr, evaluator, feedback_gen

    @staticmethod
    def start_interview_session(
        analysis_id: str,
        difficulty: str = "medium",
        question_count: int = 10,
        include_types: list = None,
        target_role: str = None
    ) -> dict:
        """
        Starts a mock interview session:
        1. Loads the analysis record.
        2. Infers target role if not provided.
        3. Invokes session manager to create a new session.
        """
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            raise ValueError(f"Analysis record with ID '{analysis_id}' not found.")

        # Extract skills and role
        skills_found = analysis.skills_json.get("found", [])
        
        # If target role is not provided, use default or try parsing JD
        if not target_role:
            target_role = "Software Engineer"  # Simple default

        session_mgr, _, _ = InterviewService.get_services()
        
        session = session_mgr.create_session(
            analysis_id=analysis_id,
            target_role=target_role,
            skills_found=skills_found,
            resume_text=analysis.resume_text,
            difficulty=difficulty,
            question_count=question_count,
            include_types=include_types
        )

        first_q = session_mgr.get_current_question(session.id)

        return {
            "session_id": session.id,
            "total_questions": session.total_questions,
            "first_question": first_q
        }

    @staticmethod
    def submit_question_answer(
        session_id: str,
        user_answer: str,
        time_taken_seconds: int = None
    ) -> dict:
        """
        Submits answer for current question and returns the next question.
        """
        session_mgr, _, _ = InterviewService.get_services()
        
        submit_res = session_mgr.submit_answer(
            session_id=session_id,
            user_answer=user_answer,
            time_taken_seconds=time_taken_seconds
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
            "is_last": submit_res["is_last"]
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
        session = InterviewSession.query.get(session_id)
        if not session:
            raise ValueError(f"Session with ID '{session_id}' not found.")

        if session.status == "completed" and session.results_json:
            # Already completed, just return the cached results
            results = session.results_json.copy()
            results["session_id"] = session.id
            return results

        answers = InterviewAnswer.query.filter_by(session_id=session_id).order_by(InterviewAnswer.question_index).all()
        if not answers:
            raise ValueError(f"No answers found for session '{session_id}' to evaluate.")

        session_mgr, evaluator, feedback_gen = InterviewService.get_services()

        # Step 1: Batch evaluate each answer
        evaluated_list = []
        q_list = session.questions_json
        
        for ans in answers:
            # Match with expected question data (to fetch keywords, ideal answer, etc.)
            # Just in case details are missing in model, fallback to q_list
            idx = ans.question_index - 1
            curr_q = q_list[idx] if idx < len(q_list) else {}

            ideal = ans.ideal_answer or curr_q.get("ideal_answer", "")
            kws = curr_q.get("keywords", [])

            logger.info(f"Evaluating answer for Q{ans.question_index}: {ans.question_text[:30]}...")
            eval_res = evaluator.evaluate_answer(
                question_text=ans.question_text,
                user_answer=ans.user_answer,
                ideal_answer=ideal,
                keywords=kws
            )

            # Update answer model record
            ans.score = eval_res["score"]
            ans.tfidf_score = eval_res["tfidf_score"]
            ans.keyword_score = eval_res["keyword_score"]
            ans.gemini_score = eval_res["gemini_score"]
            ans.feedback_json = {
                "verdict": eval_res["verdict"],
                "strengths": eval_res["strengths"],
                "weaknesses": eval_res["weaknesses"],
                "improvement_tip": eval_res["improvement_tip"],
                "keywords_found": eval_res["keywords_found"]
            }
            
            # Combine dict for feedback compiler
            ans_dict = ans.to_dict()
            # Overwrite feedback and metrics directly
            ans_dict["feedback"] = ans.feedback_json
            ans_dict["metrics"] = eval_res["metrics"]
            evaluated_list.append(ans_dict)

        # Step 2: Compile overall session summary report
        report = feedback_gen.generate_session_report(
            evaluated_answers=evaluated_list,
            target_role=session.target_role or "Software Engineer"
        )

        # Step 3: Update session record
        session.overall_score = report["overall_score"]
        session.results_json = report
        session.status = "completed"
        session.completed_at = datetime.utcnow()

        db.session.commit()

        # Return details
        report_copy = report.copy()
        report_copy["session_id"] = session.id
        # Include lists of individual evaluated questions in response
        report_copy["questions"] = evaluated_list
        
        return report_copy

    @staticmethod
    def get_session_results(session_id: str) -> dict:
        """Retrieves results of a completed session."""
        session = InterviewSession.query.get(session_id)
        if not session:
            raise ValueError(f"Session with ID '{session_id}' not found.")

        if session.status != "completed":
            return {
                "session_id": session.id,
                "status": session.status,
                "overall_score": None,
                "results": None
            }

        answers = InterviewAnswer.query.filter_by(session_id=session_id).order_by(InterviewAnswer.question_index).all()
        answers_dict = [a.to_dict() for a in answers]

        report = session.results_json.copy() if session.results_json else {}
        report["session_id"] = session.id
        report["questions"] = answers_dict
        report["status"] = session.status
        
        return report

    @staticmethod
    def get_interview_history(analysis_id: str = None) -> list:
        """Lists historical mock interviews, optionally filtered by resume analysis id."""
        query = InterviewSession.query
        if analysis_id:
            query = query.filter_by(analysis_id=analysis_id)
            
        sessions = query.order_by(InterviewSession.started_at.desc()).all()
        return [s.to_summary() for s in sessions]

    @staticmethod
    def delete_interview_session(session_id: str) -> bool:
        """Deletes a session and its answers."""
        session = InterviewSession.query.get(session_id)
        if not session:
            return False
        
        db.session.delete(session)
        db.session.commit()
        return True
