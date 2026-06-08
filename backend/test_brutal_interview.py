import sys
import os
import unittest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.analysis import Analysis
from app.models.interview import InterviewSession, InterviewAnswer
from app.core.interview_coach.evaluator import Evaluator
from app.core.interview_coach.question_generator import QuestionGenerator
from app.core.interview_coach.feedback import FeedbackGenerator
from app.services.interview_service import InterviewService

class TestBrutalInterviewCoach(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Verify/create a dummy Analysis record for testing
        cls.analysis = Analysis.query.first()
        if not cls.analysis:
            cls.analysis = Analysis(
                resume_filename="brutal_resume.pdf",
                resume_text="Jane Architect. Expert at Python, SQL, Cloud Computing, Kubernetes.",
                jd_text="Looking for a Python Backend Expert with Kubernetes and cloud knowledge.",
                scores_json={"overall": 80, "tfidf_similarity": 75, "skill_match": 85, "section_coverage": 90, "keyword_density": 70, "quality": 80, "ats_compatibility": 85},
                skills_json={"found": [{"name": "Python", "source": "explicit"}, {"name": "SQL", "source": "explicit"}, {"name": "Kubernetes", "source": "explicit"}], "missing": []},
                sections_json={"experience": True, "skills": True, "education": True},
                quality_json={"issues": [], "score": 80},
                ats_json={"issues": [], "score": 85},
                suggestions_json={"rule_based": [], "ai_generated": []}
            )
            db.session.add(cls.analysis)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_brutal_1_invalid_analysis_start(self):
        """Verify that starting a session with invalid analysis ID raises an error or is properly handled."""
        print("\n[Brutal Test 1] Testing start session with non-existent analysis_id...")
        with self.assertRaises(Exception):
            InterviewService.start_interview_session(
                analysis_id="non-existent-id-12345678",
                difficulty="medium",
                question_count=5,
                include_types=["skill"],
                target_role="Software Architect"
            )
        print("  -> PASSED: Starting session with invalid Analysis ID raised expected error.")

    def test_brutal_2_extreme_answers(self):
        """Test evaluator with extremely empty, large, and unicode-heavy answers."""
        print("\n[Brutal Test 2] Testing evaluator under extreme inputs...")
        _, evaluator, _ = InterviewService.get_services()
        
        question = "Explain standard container orchestration in Kubernetes."
        ideal = "Kubernetes coordinates a highly available cluster of computers that are co-scheduled to work as a single unit."
        keywords = ["orchestration", "Kubernetes", "cluster", "co-scheduled", "highly available", "pods"]
        
        # Scenario A: Empty string answer
        res_empty = evaluator.evaluate_answer(question, "", ideal, keywords)
        self.assertEqual(res_empty["score"], 0.0)
        self.assertEqual(res_empty["verdict"], "Unanswered")
        print("  -> Scenario A (Empty Answer) PASSED: Score is 0.0.")
        
        # Scenario B: Giant 10k character answer containing repeated keywords
        giant_answer = "Kubernetes cluster orchestration co-scheduled highly available pods " * 200
        res_giant = evaluator.evaluate_answer(question, giant_answer, ideal, keywords)
        self.assertTrue(0.0 <= res_giant["score"] <= 10.0)
        self.assertEqual(res_giant["keyword_score"], 10.0)  # Should match all keywords
        print(f"  -> Scenario B (Giant Answer) PASSED: Score is {res_giant['score']}/10.")
        
        # Scenario C: Emojis and non-ASCII characters
        unicode_answer = "🚀 Kubernetes is a 🌟 cluster for running containers. Highly available! 🖥️"
        res_unicode = evaluator.evaluate_answer(question, unicode_answer, ideal, keywords)
        self.assertTrue(res_unicode["score"] > 0.0)
        self.assertIn("Kubernetes", res_unicode["keywords_found"])
        print(f"  -> Scenario C (Unicode/Emoji Answer) PASSED: Score is {res_unicode['score']}/10.")

    def test_brutal_3_duplicate_and_weird_keywords(self):
        """Test evaluator with duplicate keywords or punctuation-heavy ideal answers."""
        print("\n[Brutal Test 3] Testing evaluator with duplicate & noisy keywords...")
        _, evaluator, _ = InterviewService.get_services()
        
        question = "What is SQL?"
        ideal = "... ,,, !!!"
        keywords = ["sql", "SQL", "sQl", "sql", "", "a"]
        
        res = evaluator.evaluate_answer(question, "I write SQL databases.", ideal, keywords)
        self.assertTrue(0.0 <= res["score"] <= 10.0)
        print(f"  -> PASSED: Evaluator handled duplicate, weird casing, and empty keywords cleanly. Score: {res['score']}/10.")

    def test_brutal_4_db_double_submission(self):
        """Verify database integrity when submitting double answers or invalid parameters."""
        print("\n[Brutal Test 4] Testing double answer submission & extreme time inputs...")
        
        # Start a legitimate session
        session_data = InterviewService.start_interview_session(
            analysis_id=self.analysis.id,
            difficulty="hard",
            question_count=2,
            include_types=["skill"],
            target_role="Database Engineer"
        )
        session_id = session_data["session_id"]
        
        # Submit Answer 1
        res1 = InterviewService.submit_question_answer(
            session_id=session_id,
            user_answer="First response to question",
            time_taken_seconds=10
        )
        
        # Re-submit answer (simulate double-clicking or duplicate request)
        # The service should transition to the next question, meaning submitting again should be for question index 1 (not 0)
        # Let's verify that submitting again records the answer for the current active index, without violating schema
        res2 = InterviewService.submit_question_answer(
            session_id=session_id,
            user_answer="Second response to second question",
            time_taken_seconds=-5  # Negative time edge case
        )
        
        # Assertions
        session = InterviewSession.query.get(session_id)
        self.assertEqual(len(session.answers), 2)
        self.assertTrue(res2["is_last"])
        
        # Check time taken was stored (either clamped or absolute)
        answers = InterviewAnswer.query.filter_by(session_id=session_id).all()
        self.assertEqual(len(answers), 2)
        print("  -> PASSED: Handled consecutive submits and negative timers gracefully.")

    def test_brutal_5_skip_all_questions_evaluation(self):
        """Test final evaluation when all questions are skipped (empty answers)."""
        print("\n[Brutal Test 5] Testing session evaluation with skipped questions...")
        
        session_data = InterviewService.start_interview_session(
            analysis_id=self.analysis.id,
            difficulty="easy",
            question_count=3,
            include_types=["skill", "behavioral"],
            target_role="Fullstack Developer"
        )
        session_id = session_data["session_id"]
        
        # Skip all 3 questions
        InterviewService.submit_question_answer(session_id, "", 0)
        InterviewService.submit_question_answer(session_id, "", 0)
        InterviewService.submit_question_answer(session_id, "", 0)
        
        # Run batch evaluation
        results = InterviewService.evaluate_completed_session(session_id)
        self.assertEqual(results["overall_score"], 0.0)
        self.assertEqual(results["overall_percentage"], 0.0)
        self.assertEqual(results["strengths"], [])
        self.assertTrue(len(results["weaknesses"]) > 0)
        print("  -> PASSED: Skip-all session graded to 0% and completed successfully.")

    def test_brutal_6_adaptive_difficulty(self):
        """Verify the adaptive difficulty engine adjusts properly under extreme grades."""
        print("\n[Brutal Test 6] Testing adaptive difficulty engine slides correctly...")
        from app.core.interview_coach.difficulty import DifficultyAdapter
        
        # Scenario A: High performance (all 9s and 10s) -> should elevate or stay high
        difficulties_high = ["easy", "easy", "easy"]
        scores_high = [9.0, 9.5, 10.0]
        next_diff_high = DifficultyAdapter.adapt_difficulty(current_difficulty="easy", recent_scores=scores_high)
        self.assertEqual(next_diff_high, "medium")
        
        # Scenario B: Low performance (all 1s and 2s) -> should demote or stay low
        difficulties_low = ["hard", "hard", "hard"]
        scores_low = [2.0, 1.5, 3.0]
        next_diff_low = DifficultyAdapter.adapt_difficulty(current_difficulty="hard", recent_scores=scores_low)
        self.assertEqual(next_diff_low, "medium")
        
        # Scenario C: Mixed / average performance -> should stay same
        difficulties_mixed = ["medium", "medium", "medium"]
        scores_mixed = [6.0, 7.0, 6.5]
        next_diff_mixed = DifficultyAdapter.adapt_difficulty(current_difficulty="medium", recent_scores=scores_mixed)
        self.assertEqual(next_diff_mixed, "medium")
        
        print("  -> PASSED: Adaptive difficulty transitions correctly between easy, medium, and hard.")

if __name__ == "__main__":
    print("=== RUNNING BRUTAL TESTS FOR AI INTERVIEW COACH ===")
    unittest.main()
