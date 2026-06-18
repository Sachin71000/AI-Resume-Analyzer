"""
TopicRotator — ensures question variety by rotating through a structured topic queue.

Design:
- Each session gets a shuffled topic queue
- Questions are drawn from successive topics to prevent skill/topic clustering
- Behavioral questions are always placed at start (warmup) and optionally end (closing)
"""
import random
import logging

logger = logging.getLogger(__name__)

# Master topic taxonomy — ordered by natural interview flow
DEFAULT_TOPIC_SEQUENCE = [
    "behavioral_warmup",   # Always first: STAR-format icebreaker
    "skill_core",          # Core technical skill question
    "skill_applied",       # Real-world application of skill
    "system_design",       # Architecture / design thinking
    "project_deep_dive",   # Resume project exploration
    "debugging_scenario",  # Problem-solving under pressure
    "skill_core",          # Second skill question (rotated)
    "role_situational",    # Role-specific situational judgment
    "skill_applied",       # Third skill question
    "behavioral_closing",  # Closing: leadership/impact STAR question
]

TOPIC_TO_QTYPE_MAP = {
    "behavioral_warmup":   "behavioral",
    "behavioral_closing":  "behavioral",
    "skill_core":          "skill",
    "skill_applied":       "skill",
    "system_design":       "role",
    "project_deep_dive":   "project",
    "debugging_scenario":  "skill",
    "role_situational":    "role",
}

TOPIC_INSTRUCTIONS = {
    "skill_core": "Ask about fundamental concepts of the skill.",
    "skill_applied": "Ask about a real-world problem-solving scenario using the skill.",
    "system_design": "Ask about designing a scalable system or service component.",
    "project_deep_dive": "Ask about architectural decisions and tradeoffs in a specific project from the resume.",
    "debugging_scenario": "Present a debugging scenario or common pitfall in the skill area.",
    "role_situational": "Ask a situational/behavioral question specific to the role.",
    "behavioral_warmup": "Ask a warm-up STAR-format behavioral question about adaptability or learning.",
    "behavioral_closing": "Ask a closing STAR-format behavioral question about leadership, impact, or ownership.",
}


class TopicRotator:
    def __init__(self, total_questions: int = 10, custom_sequence: list[str] = None):
        self.total_questions = total_questions
        self._queue = self._build_queue(custom_sequence)
        self._cursor = 0

    def _build_queue(self, custom_sequence: list[str] = None) -> list[str]:
        """Build the topic queue scaled to total_questions."""
        if custom_sequence:
            base = custom_sequence
        else:
            base = DEFAULT_TOPIC_SEQUENCE

        # Scale or trim to match total_questions
        if self.total_questions <= len(base):
            # Trim: always keep behavioral_warmup first
            queue = [base[0]]  # warmup
            middle = base[1:-1]
            random.shuffle(middle)
            queue.extend(middle[:self.total_questions - 2])
            if self.total_questions > 1:
                queue.append("behavioral_closing")
            return queue[:self.total_questions]
        else:
            # Extend by repeating middle topics
            queue = [base[0]]  # warmup
            middle = base[1:-1]
            extended = (middle * ((self.total_questions // len(middle)) + 1))
            random.shuffle(extended)
            queue.extend(extended[:self.total_questions - 2])
            queue.append("behavioral_closing")
            return queue[:self.total_questions]

    def next_topic(self) -> tuple[str, str]:
        """
        Returns (topic_name, q_type) for the next question slot.
        Falls back to 'skill_core' if cursor exceeds queue.
        """
        if self._cursor < len(self._queue):
            topic = self._queue[self._cursor]
            self._cursor += 1
        else:
            topic = "skill_core"

        q_type = TOPIC_TO_QTYPE_MAP.get(topic, "skill")
        logger.debug(f"[TopicRotator] Slot {self._cursor}/{self.total_questions}: topic={topic}, type={q_type}")
        return topic, q_type

    def get_topic_instruction(self, topic: str) -> str:
        """Return a natural-language instruction for Gemini about this topic slot."""
        return TOPIC_INSTRUCTIONS.get(topic, "Ask a relevant technical question.")

    def get_full_sequence(self) -> list[str]:
        """Return the planned topic sequence for the session."""
        return list(self._queue)

    def to_state_dict(self) -> dict:
        """Serialize state for DB storage (resume across requests)."""
        return {
            "queue": self._queue,
            "cursor": self._cursor,
            "total": self.total_questions,
        }

    @classmethod
    def from_state_dict(cls, state: dict) -> "TopicRotator":
        """Restore from serialized DB state."""
        rotator = cls(total_questions=state.get("total", 10))
        rotator._queue = state.get("queue", rotator._queue)
        rotator._cursor = state.get("cursor", 0)
        return rotator
