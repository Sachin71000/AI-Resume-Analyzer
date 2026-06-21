import sys
import os
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.analysis import Analysis
from app.models.interview import InterviewSession, InterviewAnswer
from app.core.interview_coach.question_generator import QuestionGenerator
from app.core.interview_coach.evaluator import Evaluator
from app.core.interview_coach.feedback import FeedbackGenerator
from app.services.interview_service import InterviewService

def run_tests():
    print("=== STARTING INTERVIEW COACH TESTING ===")
    app = create_app()
    with app.app_context():
        # 1. Verify DB is setup and tables exist
        print("\n[Test 1] Verifying database tables...")
        # Check if we can query or if it's empty
        session_count = InterviewSession.query.count()
        answer_count = InterviewAnswer.query.count()
        print(f"  Current InterviewSession count: {session_count}")
        print(f"  Current InterviewAnswer count: {answer_count}")

        # 2. Test Question Generator loading and generation
        print("\n[Test 2] Testing Question Generator...")
        # Since we might not have a Gemini API key loaded in test mode, we pass a dummy key or verify generator fallback
        # Let's inspect active services
        from app.core.interview_coach.session_manager import SessionManager
        q_gen = QuestionGenerator(gemini_service=None)
        session_mgr = SessionManager(question_generator=q_gen)
        evaluator = Evaluator(gemini_service=None)
        
        # Test loading question bank
        print(f"  Question bank size: {len(q_gen.question_bank.get('skills', {}))} skills loaded.")
        
        # Select questions by skills
        skills = ["Python", "SQL", "Machine Learning"]
        generated = q_gen.generate_interview_questions(
            skills_found=skills,
            resume_text="Worked on machine learning models using Python and SQL databases.",
            target_role="Data Scientist",
            difficulty="medium",
            total_count=5,
            include_types=["skill", "behavioral", "role"]
        )
        print(f"  Generated {len(generated)} questions:")
        for idx, q in enumerate(generated):
            print(f"    Q{idx+1}: [{q['type']}] ({q.get('skill', 'No Skill')}) - {q['question']}")

        # 3. Test Evaluator logic (TF-IDF & Keywords)
        print("\n[Test 3] Testing Evaluator Core Layers...")
        question_text = "What is the difference between a list and a tuple in Python?"
        ideal_answer = "Lists are mutable, meaning they can be modified after creation, while tuples are immutable, meaning they cannot be changed. Lists use square brackets and tuples use parentheses."
        expected_keywords = ["mutable", "immutable", "modified", "list", "tuple", "brackets", "parentheses"]
        
        # Perfect answer
        user_answer_perfect = "Lists are mutable and can be modified. Tuples are immutable and cannot be changed. Lists use brackets while tuples use parentheses."
        perfect_res = evaluator.evaluate_answer(question_text, user_answer_perfect, ideal_answer, expected_keywords)
        print("  Evaluating a near-perfect answer:")
        print(f"    Final Score: {perfect_res['score']}/10")
        print(f"    TF-IDF Score: {perfect_res['tfidf_score']}/10")
        print(f"    Keyword Score: {perfect_res['keyword_score']}/10")
        print(f"    Verdict: {perfect_res['verdict']}")
        print(f"    Keywords Found: {perfect_res['keywords_found']}")
        print(f"    Communication Quality: {perfect_res['metrics']['communication_quality_score']}/10")
        
        # Poor/Partial answer
        user_answer_poor = "Lists are for python and tuples too."
        poor_res = evaluator.evaluate_answer(question_text, user_answer_poor, ideal_answer, expected_keywords)
        print("\n  Evaluating a poor/partial answer:")
        print(f"    Final Score: {poor_res['score']}/10")
        print(f"    TF-IDF Score: {poor_res['tfidf_score']}/10")
        print(f"    Keyword Score: {poor_res['keyword_score']}/10")
        print(f"    Verdict: {poor_res['verdict']}")
        print(f"    Keywords Found: {poor_res['keywords_found']}")

        # Empty answer
        user_answer_empty = ""
        empty_res = evaluator.evaluate_answer(question_text, user_answer_empty, ideal_answer, expected_keywords)
        print("\n  Evaluating an empty answer:")
        print(f"    Final Score: {empty_res['score']}/10")
        print(f"    Verdict: {empty_res['verdict']}")

        # 4. Mock Full Session Pipeline in SQLite
        print("\n[Test 4] Simulating Database Session Flow...")
        # Create a mock Analysis record if none exists, or fetch existing
        analysis = Analysis.query.first()
        if not analysis:
            print("  No existing resume analysis found. Creating a temporary analysis...")
            analysis = Analysis(
                resume_filename="test_resume.pdf",
                resume_text="John Doe. Software Developer with Python and SQL experience.",
                jd_text="Software Developer with SQL and Python skills.",
                scores_json={"overall": 75, "tfidf_similarity": 70, "skill_match": 80, "section_coverage": 90, "keyword_density": 60, "quality": 80, "ats_compatibility": 85},
                skills_json={"found": [{"name": "Python", "source": "explicit"}, {"name": "SQL", "source": "explicit"}], "missing": []},
                sections_json={"experience": True, "skills": True, "education": True},
                quality_json={"issues": [], "score": 80},
                ats_json={"issues": [], "score": 85},
                suggestions_json={"rule_based": [], "ai_generated": []}
            )
            db.session.add(analysis)
            db.session.commit()
            print(f"  Created temporary Analysis ID: {analysis.id}")
        else:
            print(f"  Reusing existing Analysis ID: {analysis.id}")

        # Start interview session via Service
        session_data = InterviewService.start_interview_session(
            analysis_id=analysis.id,
            difficulty="medium",
            question_count=3,
            include_types=["skill", "behavioral"],
            target_role="Software Developer"
        )
        session_id = session_data["session_id"]
        print(f"  Started Interview Session! Session ID: {session_id}")
        print(f"  First Question: {session_data['first_question']['question']}")

        # Submit answer 1
        res1 = InterviewService.submit_question_answer(
            session_id=session_id,
            user_answer="A list is mutable and can be modified. A tuple is immutable and cannot be changed.",
            time_taken_seconds=30
        )
        print(f"  Submitted Answer 1. Next question: {res1['next_question']['question']}")

        # Submit answer 2
        res2 = InterviewService.submit_question_answer(
            session_id=session_id,
            user_answer="I work well with difficult teammates by listening to their opinions and collaborating.",
            time_taken_seconds=45
        )
        print(f"  Submitted Answer 2. Next question: {res2['next_question']['question']}")

        # Submit answer 3
        res3 = InterviewService.submit_question_answer(
            session_id=session_id,
            user_answer="I use Python libraries like pandas and NumPy for working with arrays.",
            time_taken_seconds=50
        )
        print(f"  Submitted Answer 3 (Is Last: {res3['is_last']})")

        # Complete and Batch Evaluate
        print("\n[Test 5] Running batch evaluation...")
        results = InterviewService.evaluate_completed_session(session_id)
        print(f"  Session Completed and Evaluated!")
        print(f"  Overall Score: {results['overall_score']}/10 ({results['overall_percentage']}%)")
        print(f"  Topic Breakdown: {results['topic_scores']}")
        print(f"  Strengths: {results['strengths']}")
        print(f"  Weaknesses: {results['weaknesses']}")
        print(f"  Roadmap: {results['roadmap']}")

        # Clean up temporary session to keep DB pristine if needed, or leave it for history testing
        print("\n[Test 6] Verifying history endpoint...")
        history = InterviewService.get_interview_history(analysis.id)
        print(f"  History items count: {len(history)}")
        if history:
            print(f"  Latest session score in history: {history[0]['overall_score']}/10")

    print("\n=== INTERVIEW COACH TESTING COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
