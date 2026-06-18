"""
DeduplicationEngine — prevents question repetition within and across sessions.

Strategy:
  1. Within session: track asked question hashes in memory (session.questions_json)
  2. Cross-session: persist question hashes in asked_question_log DB table
  3. Gemini prompts: include already-asked question texts to prevent AI regeneration
"""
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def compute_question_hash(question_text: str) -> str:
    """Compute a stable SHA256 fingerprint for a question string."""
    normalized = question_text.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


class DeduplicationEngine:
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        self._session_hashes: set[str] = set()

    def load_history(self):
        """
        Load previously-asked question hashes from DB for this analysis_id.
        Call once after DB session is available.
        """
        try:
            from ...models.interview import AskedQuestionLog
            from ...extensions import db
            records = AskedQuestionLog.query.filter_by(
                analysis_id=self.analysis_id
            ).all()
            for r in records:
                self._session_hashes.add(r.question_hash)
            logger.info(
                f"[Dedup] Loaded {len(records)} historical hashes for analysis {self.analysis_id}"
            )
        except Exception as e:
            logger.warning(f"[Dedup] Could not load history (new DB?): {e}")

    def is_duplicate(self, question_text: str) -> bool:
        """Return True if this question was already asked."""
        h = compute_question_hash(question_text)
        return h in self._session_hashes

    def mark_asked(self, question_text: str, topic: str = None, persist: bool = True):
        """
        Mark a question as asked.
        If persist=True, write to DB so cross-session dedup works.
        """
        h = compute_question_hash(question_text)
        if h in self._session_hashes:
            return  # already tracked

        self._session_hashes.add(h)

        if persist:
            try:
                from ...models.interview import AskedQuestionLog
                from ...extensions import db
                record = AskedQuestionLog(
                    analysis_id=self.analysis_id,
                    question_hash=h,
                    question_text=question_text[:500],
                    topic=topic or "general",
                )
                db.session.add(record)
                db.session.commit()
            except Exception as e:
                logger.error(f"[Dedup] Failed to persist question hash: {e}")

    def get_asked_texts(self, limit: int = 20) -> list[str]:
        """
        Return a list of recently-asked question texts for Gemini context injection.
        Limits to `limit` most recent to avoid overly long prompts.
        """
        try:
            from ...models.interview import AskedQuestionLog
            records = (
                AskedQuestionLog.query.filter_by(analysis_id=self.analysis_id)
                .order_by(AskedQuestionLog.asked_at.desc())
                .limit(limit)
                .all()
            )
            return [r.question_text for r in records if r.question_text]
        except Exception as e:
            logger.warning(f"[Dedup] Could not fetch asked texts: {e}")
            return []

    def filter_candidates(self, candidates: list[dict]) -> list[dict]:
        """
        Filter out any questions from a candidate list that are duplicates.
        Returns only non-duplicate questions.
        """
        unique = []
        for q in candidates:
            text = q.get("question", "")
            if text and not self.is_duplicate(text):
                unique.append(q)
            else:
                logger.info(f"[Dedup] Filtered duplicate: {text[:60]}...")
        return unique
