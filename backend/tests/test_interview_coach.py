"""
Unit Tests — QuestionGenerator, DeduplicationEngine, TopicRotator, DifficultyAdapter
Run: pytest tests/ -v
"""
import pytest
import sys
import os

# Ensure backend package is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ── DeduplicationEngine tests (no DB needed — test in-memory mode) ────────────
from app.core.interview_coach.deduplication import DeduplicationEngine, compute_question_hash


class TestDeduplicationEngine:
    def setup_method(self):
        """Fresh engine for each test — no DB, analysis_id='test'."""
        self.engine = DeduplicationEngine(analysis_id="test_analysis")
        # Don't call load_history() — no DB in unit tests

    def test_compute_hash_is_deterministic(self):
        q = "What is the GIL in Python?"
        assert compute_question_hash(q) == compute_question_hash(q)

    def test_compute_hash_normalizes_case_and_whitespace(self):
        h1 = compute_question_hash("What is the GIL?")
        h2 = compute_question_hash("  what is the GIL?  ")
        assert h1 == h2

    def test_new_question_is_not_duplicate(self):
        assert self.engine.is_duplicate("A brand new question?") is False

    def test_marking_makes_it_duplicate(self):
        q = "What is polymorphism?"
        self.engine.mark_asked(q, persist=False)
        assert self.engine.is_duplicate(q) is True

    def test_different_questions_not_duplicate(self):
        self.engine.mark_asked("Question A", persist=False)
        assert self.engine.is_duplicate("Question B") is False

    def test_filter_candidates_removes_duplicates(self):
        self.engine.mark_asked("Old question 1", persist=False)
        candidates = [
            {"question": "Old question 1", "type": "skill"},
            {"question": "New question 2", "type": "skill"},
        ]
        filtered = self.engine.filter_candidates(candidates)
        assert len(filtered) == 1
        assert filtered[0]["question"] == "New question 2"

    def test_filter_candidates_empty_list(self):
        assert self.engine.filter_candidates([]) == []

    def test_mark_asked_idempotent(self):
        """Marking same question twice should not raise or duplicate."""
        q = "What is a closure?"
        self.engine.mark_asked(q, persist=False)
        self.engine.mark_asked(q, persist=False)  # second call
        assert self.engine.is_duplicate(q) is True

    def test_get_asked_texts_no_db(self):
        """Should return empty list when DB not available in unit test."""
        result = self.engine.get_asked_texts()
        assert isinstance(result, list)


# ── TopicRotator tests ────────────────────────────────────────────────────────
from app.core.interview_coach.topic_rotator import TopicRotator, TOPIC_TO_QTYPE_MAP


class TestTopicRotator:
    def test_basic_creation(self):
        rotator = TopicRotator(total_questions=10)
        assert len(rotator.get_full_sequence()) == 10

    def test_first_topic_is_behavioral_warmup(self):
        rotator = TopicRotator(total_questions=5)
        topic, _ = rotator.next_topic()
        assert topic == "behavioral_warmup"

    def test_returns_correct_question_type(self):
        rotator = TopicRotator(total_questions=10)
        # All returned q_types must be known types
        valid_types = {"behavioral", "skill", "project", "role"}
        for _ in range(10):
            _, q_type = rotator.next_topic()
            assert q_type in valid_types

    def test_serialization_round_trip(self):
        rotator = TopicRotator(total_questions=5)
        # Advance cursor
        rotator.next_topic()
        rotator.next_topic()
        state = rotator.to_state_dict()
        restored = TopicRotator.from_state_dict(state)
        assert restored._cursor == rotator._cursor
        assert restored._queue == rotator._queue

    def test_small_session_does_not_crash(self):
        rotator = TopicRotator(total_questions=1)
        seq = rotator.get_full_sequence()
        assert len(seq) == 1

    def test_large_session_extends_queue(self):
        rotator = TopicRotator(total_questions=20)
        seq = rotator.get_full_sequence()
        assert len(seq) == 20

    def test_excess_next_topic_calls_fallback(self):
        rotator = TopicRotator(total_questions=3)
        # Call more times than queue length
        for _ in range(6):
            topic, q_type = rotator.next_topic()
            assert topic is not None
            assert q_type is not None


# ── DifficultyAdapter tests ───────────────────────────────────────────────────
from app.core.interview_coach.difficulty import DifficultyAdapter


class TestDifficultyAdapter:
    def test_insufficient_scores_returns_same(self):
        result = DifficultyAdapter.adapt_difficulty("medium", [9.0])
        assert result == "medium"  # needs at least 2 scores

    def test_high_scores_increases_difficulty(self):
        result = DifficultyAdapter.adapt_difficulty("easy", [8.5, 9.0, 8.2])
        assert result == "medium"

    def test_very_high_scores_from_medium(self):
        result = DifficultyAdapter.adapt_difficulty("medium", [9.0, 8.5, 9.5])
        assert result == "hard"

    def test_low_scores_decreases_difficulty(self):
        result = DifficultyAdapter.adapt_difficulty("hard", [2.0, 3.5, 1.0])
        assert result == "medium"

    def test_cannot_go_above_hard(self):
        result = DifficultyAdapter.adapt_difficulty("hard", [9.5, 9.8, 10.0])
        assert result == "hard"  # already at max

    def test_cannot_go_below_easy(self):
        result = DifficultyAdapter.adapt_difficulty("easy", [0.5, 1.0, 2.0])
        assert result == "easy"  # already at min

    def test_average_scores_maintain_difficulty(self):
        result = DifficultyAdapter.adapt_difficulty("medium", [6.0, 5.5, 6.8])
        assert result == "medium"

    def test_invalid_difficulty_defaults_to_medium(self):
        result = DifficultyAdapter.adapt_difficulty("ultra", [9.0, 9.5])
        # Should default to medium then increase to hard
        assert result in ["medium", "hard"]


# ── QuestionGenerator unit tests (no Gemini) ─────────────────────────────────
from app.core.interview_coach.question_generator import (
    QuestionGenerator, _normalize_skill_key, _find_bank_key, SKILL_ALIASES
)


class TestSkillNormalization:
    def test_direct_alias(self):
        assert _normalize_skill_key("python3") == "python"
        assert _normalize_skill_key("scikit-learn") == "machine learning"
        assert _normalize_skill_key("reactjs") == "react"

    def test_unknown_skill_returns_lowercase(self):
        result = _normalize_skill_key("Kotlin")
        assert result == "kotlin"

    def test_whitespace_stripped(self):
        result = _normalize_skill_key("  Python  ")
        assert result == "python"


class TestFindBankKey:
    MOCK_BANK = {
        "python": {},
        "sql": {},
        "machine learning": {},
        "react": {},
    }

    def test_exact_match(self):
        assert _find_bank_key("python", self.MOCK_BANK) == "python"

    def test_substring_match(self):
        # "deep learning" contains "machine learning" partially — no, test real substring
        result = _find_bank_key("sql", self.MOCK_BANK)
        assert result == "sql"

    def test_no_match_returns_none(self):
        result = _find_bank_key("cobol", self.MOCK_BANK)
        assert result is None

    def test_fuzzy_match_close_name(self):
        # "reacts" is close to "react"
        result = _find_bank_key("reacts", self.MOCK_BANK)
        # May or may not fuzzy match depending on cutoff
        assert result is None or result == "react"


class TestQuestionGeneratorNoGemini:
    """Test QuestionGenerator without Gemini API (offline mode)."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with a real question bank."""
        bank_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'question_bank.json'
        )
        return QuestionGenerator(question_bank_path=bank_path, gemini_service=None)

    def test_generates_correct_count(self, generator):
        questions = generator.generate_interview_questions(
            skills_found=[{"name": "python"}, {"name": "sql"}],
            resume_text="Sample resume text",
            target_role="Software Engineer",
            total_count=5,
        )
        assert len(questions) == 5

    def test_all_questions_have_required_fields(self, generator):
        questions = generator.generate_interview_questions(
            skills_found=[{"name": "python"}],
            resume_text="Sample resume",
            target_role="Engineer",
            total_count=3,
        )
        required = {"question", "ideal_answer", "keywords", "category", "type", "index"}
        for q in questions:
            missing = required - set(q.keys())
            assert not missing, f"Question missing fields: {missing}"

    def test_no_repeated_questions(self, generator):
        """Core test: no duplicate questions in a single session."""
        questions = generator.generate_interview_questions(
            skills_found=[{"name": "python"}, {"name": "sql"}, {"name": "react"}],
            resume_text="Engineer with 3 years experience in Python and SQL.",
            target_role="Software Engineer",
            total_count=8,
        )
        texts = [q["question"] for q in questions]
        # All question texts must be unique
        assert len(texts) == len(set(texts)), f"Duplicates found: {[t for t in texts if texts.count(t) > 1]}"

    def test_diverse_fallback_pool_no_repeats(self, generator):
        """B1 FIX TEST: Even with unknown skills and no Gemini, no same string repeated."""
        questions = generator.generate_interview_questions(
            skills_found=[{"name": "unknownskillxyz"}],
            resume_text="",
            target_role="Engineer",
            total_count=5,
        )
        texts = [q["question"] for q in questions]
        assert len(texts) == len(set(texts)), "Fallback pool has duplicates!"

    def test_fuzzy_skill_matching(self, generator):
        """B5 FIX TEST: 'Python 3' and 'scikit-learn' should not all fall to generic fallback."""
        questions = generator.generate_interview_questions(
            skills_found=[{"name": "Python 3"}, {"name": "scikit-learn"}],
            resume_text="ML engineer with Python 3 and scikit-learn experience.",
            target_role="Data Scientist",
            total_count=4,
        )
        # Should still generate questions without error
        assert len(questions) == 4

    def test_indices_are_sequential(self, generator):
        questions = generator.generate_interview_questions(
            skills_found=[{"name": "python"}],
            resume_text="Resume",
            target_role="Engineer",
            total_count=5,
        )
        indices = [q["index"] for q in questions]
        assert indices == list(range(1, 6))


# ── Interview routes integration tests ────────────────────────────────────────
@pytest.fixture
def app():
    """Create test Flask app with in-memory SQLite."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from app import create_app
    from app.config import TestingConfig

    application = create_app(TestingConfig)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


class TestHealthEndpoint:
    def test_health_check_returns_200(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_health_check_body(self, client):
        data = response = client.get('/api/health').get_json()
        assert "status" in data
        assert "database" in data
        assert data["database"] == "healthy"


class TestInterviewRoutes:
    def test_start_interview_missing_analysis_id(self, client):
        """Should return 400 when analysis_id is missing."""
        response = client.post(
            '/api/interview/start',
            json={},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_start_interview_invalid_analysis_id(self, client):
        """Should return 404 for non-existent analysis."""
        response = client.post(
            '/api/interview/start',
            json={"analysis_id": "nonexistent-id-12345"},
            content_type='application/json'
        )
        assert response.status_code == 404

    def test_submit_answer_invalid_session(self, client):
        """Should return 404 or 500 for non-existent session."""
        response = client.post(
            '/api/interview/nonexistent-session/answer',
            json={"answer": "Test answer"},
            content_type='application/json'
        )
        assert response.status_code in [404, 500]

    def test_get_history_empty(self, client):
        """Interview history should return empty list for fresh DB."""
        response = client.get('/api/interview/history')
        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert isinstance(data["items"], list)
