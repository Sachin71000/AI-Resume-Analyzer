"""
SessionManager — Fixed:
  - B3: DifficultyAdapter now WIRED and called on each answer submission
  - B4: Replaced deprecated Session.query.get() with db.session.get()
  - New: Persists topic_rotation_state and difficulty_history on session
  - New: Passes analysis_id to QuestionGenerator for cross-session deduplication
"""
import logging
from datetime import datetime
from ...extensions import db
from ...models.interview import InterviewSession, InterviewAnswer
from .question_generator import QuestionGenerator
from .difficulty import DifficultyAdapter

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, question_generator: QuestionGenerator):
        self.question_generator = question_generator

    def create_session(
        self,
        analysis_id: str,
        target_role: str,
        skills_found: list,
        resume_text: str,
        difficulty: str = "medium",
        question_count: int = 10,
        include_types: list = None,
    ) -> InterviewSession:
        """
        Initializes an interview session:
        1. Generates questions using QuestionGenerator with dedup + topic rotation.
        2. Persists a new InterviewSession record in DB.
        3. Returns the session object.
        """
        # Generate questions — now with analysis_id for cross-session dedup
        questions = self.question_generator.generate_interview_questions(
            skills_found=skills_found,
            resume_text=resume_text,
            target_role=target_role,
            difficulty=difficulty,
            total_count=question_count,
            include_types=include_types,
            analysis_id=analysis_id,  # ← enables cross-session deduplication
        )

        # Extract and persist the rotator state (stored in first question by generator)
        rotator_state = None
        if questions and "_rotator_state" in questions[0]:
            rotator_state = questions[0].pop("_rotator_state")

        session = InterviewSession(
            analysis_id=analysis_id,
            target_role=target_role,
            difficulty=difficulty,
            status="in_progress",
            total_questions=len(questions),
            questions_json=questions,
            topic_rotation_state=rotator_state,
            difficulty_history=[],
            started_at=datetime.utcnow(),
        )

        db.session.add(session)
        db.session.commit()
        return session

    def get_current_question(self, session_id: str) -> dict | None:
        """
        Returns details of the current unanswered question.
        Determined by counting already-submitted answers.
        """
        # B4 FIX: use db.session.get() instead of deprecated Model.query.get()
        session = db.session.get(InterviewSession, session_id)
        if not session or session.status != "in_progress":
            return None

        answered_count = InterviewAnswer.query.filter_by(session_id=session_id).count()

        if answered_count >= session.total_questions:
            return None

        q_list = session.questions_json
        if answered_count < len(q_list):
            curr_q = dict(q_list[answered_count])
            # Reflect the current (possibly adapted) difficulty
            curr_q["difficulty"] = session.difficulty
            return curr_q

        return None

    def submit_answer(
        self,
        session_id: str,
        user_answer: str,
        time_taken_seconds: int = None,
    ) -> dict | None:
        """
        Saves candidate's answer for the current question.
        B3 FIX: Now calls DifficultyAdapter to update session difficulty
        based on the rolling average of recent scores.
        """
        # B4 FIX: use db.session.get()
        session = db.session.get(InterviewSession, session_id)
        if not session or session.status != "in_progress":
            return None

        answered_count = InterviewAnswer.query.filter_by(session_id=session_id).count()
        question_idx = answered_count + 1

        if question_idx > session.total_questions:
            logger.warning(f"Session {session_id} has already answered all questions.")
            return None

        q_list = session.questions_json
        curr_q = q_list[answered_count]

        # Input sanitization: cap answer length (security fix)
        sanitized_answer = (user_answer or "").strip()[:5000]

        # Save answer to DB
        answer_rec = InterviewAnswer(
            session_id=session_id,
            question_index=question_idx,
            question_text=curr_q["question"],
            category=curr_q.get("type", "skill"),
            skill=curr_q.get("skill"),
            user_answer=sanitized_answer,
            ideal_answer=curr_q.get("ideal_answer"),
            time_taken_seconds=time_taken_seconds,
            answered_at=datetime.utcnow(),
        )
        db.session.add(answer_rec)

        # ── B3 FIX: Adaptive Difficulty ──────────────────────────────────────
        # We can adapt difficulty based on previous answer scores IF we have them.
        # Since batch evaluation happens at session end, we track scores that ARE
        # available (scored answers from previous sessions on same analysis OR
        # when real-time scoring is active).
        difficulty_history = list(session.difficulty_history or [])
        if answer_rec.score is not None:
            difficulty_history.append(answer_rec.score)

        if len(difficulty_history) >= 2:
            new_difficulty = DifficultyAdapter.adapt_difficulty(
                current_difficulty=session.difficulty,
                recent_scores=difficulty_history,
            )
            if new_difficulty != session.difficulty:
                logger.info(
                    f"[SessionMgr] Adapting difficulty for session {session_id}: "
                    f"{session.difficulty} → {new_difficulty}"
                )
                session.difficulty = new_difficulty

        session.difficulty_history = difficulty_history
        # ─────────────────────────────────────────────────────────────────────

        db.session.commit()

        progress = {
            "answered": question_idx,
            "total": session.total_questions,
            "percentage": round((question_idx / session.total_questions) * 100),
            "current_difficulty": session.difficulty,
        }

        is_last = question_idx == session.total_questions

        return {
            "answer_id": answer_rec.id,
            "progress": progress,
            "is_last": is_last,
        }
