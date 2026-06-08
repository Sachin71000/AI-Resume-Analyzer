import logging
from collections import defaultdict
from pydantic import BaseModel, Field
from ...services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class AISkillRoadmap(BaseModel):
    skill: str = Field(description="The name of the weak skill or topic.")
    current_level: str = Field(description="The assessed level (e.g. 'needs work', 'average').")
    recommendations: list[str] = Field(description="2-3 specific topics, concepts, or exercises to practice.")
    resources: list[str] = Field(description="1-2 recommended resources (books, platforms, tutorials).")

class AIInterviewRoadmap(BaseModel):
    roadmaps: list[AISkillRoadmap] = Field(description="A study roadmap for each weak skill identified during the interview.")

class FeedbackGenerator:
    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service

    def generate_session_report(
        self,
        evaluated_answers: list[dict],
        target_role: str
    ) -> dict:
        """
        Synthesizes the complete report for an interview session:
        - Overall score and percentage
        - Category-wise grouping and averaging
        - Strengths and Weaknesses lists
        - Personal Study Roadmap
        - Communication speed/quality summaries
        """
        if not evaluated_answers:
            return {
                "overall_score": 0.0,
                "overall_percentage": 0.0,
                "topic_scores": {},
                "strengths": [],
                "weaknesses": [],
                "moderate": [],
                "communication_summary": {
                    "avg_word_count": 0,
                    "total_filler_words": 0,
                    "avg_communication_score": 0.0
                },
                "roadmap": []
            }

        # Calculate scores and metrics
        total_score = 0.0
        total_comm_score = 0.0
        total_words = 0
        total_fillers = 0
        
        topic_scores = defaultdict(list)
        strengths = []
        weaknesses = []
        moderate = []

        for ans in evaluated_answers:
            score = ans.get("score", 0.0)
            total_score += score
            
            # Topic scores grouping
            # Use skill or category as key
            category_key = ans.get("skill") or ans.get("category") or "General"
            topic_scores[category_key].append(score)

            # Heuristics communication averages
            metrics = ans.get("metrics", {})
            total_comm_score += metrics.get("communication_quality_score", 0.0)
            total_words += metrics.get("word_count", 0)
            total_fillers += metrics.get("filler_word_count", 0)

        num_questions = len(evaluated_answers)
        overall_score = round(total_score / num_questions, 2)
        overall_pct = round(overall_score * 10.0, 1)

        # Average out topic scores
        topic_averages = {}
        for topic, scores in topic_scores.items():
            avg = round(sum(scores) / len(scores), 2)
            topic_averages[topic] = avg
            
            # Classify
            if avg >= 7.5:
                strengths.append(topic)
            elif avg < 5.0:
                weaknesses.append(topic)
            else:
                moderate.append(topic)

        # Build communication overview
        avg_word_count = round(total_words / num_questions)
        avg_comm_score = round(total_comm_score / num_questions, 2)

        communication_summary = {
            "avg_word_count": avg_word_count,
            "total_filler_words": total_fillers,
            "avg_communication_score": avg_comm_score,
            "filler_rate_per_hundred": round((total_fillers / max(1, total_words)) * 100, 1)
        }

        # Generate Personalized Study Roadmap (Dynamic via Gemini if available)
        roadmap = self._generate_roadmap(weaknesses, moderate, target_role)

        return {
            "overall_score": overall_score,
            "overall_percentage": overall_pct,
            "topic_scores": topic_averages,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "moderate": moderate,
            "communication_summary": communication_summary,
            "roadmap": roadmap
        }

    def _generate_roadmap(self, weaknesses: list[str], moderate: list[str], role: str) -> list[dict]:
        """Generates dynamic study recommendations for weak/moderate topics."""
        roadmap_items = []
        
        # If Gemini is available and we have weaknesses, generate highly personalized roadmap
        if self.gemini_service and (weaknesses or moderate):
            prompt = f"""
            You are a master career coach and technical trainer.
            A candidate seeking the role of '{role}' took a mock interview and demonstrated:
            - WEAK TOPICS: {', '.join(weaknesses) if weaknesses else 'None'}
            - MODERATE TOPICS: {', '.join(moderate) if moderate else 'None'}
            
            Create a highly practical study and improvement roadmap.
            For each topic, provide targeted recommendations and specific learning resources (courses, books, tutorials).
            """
            try:
                res = self.gemini_service._call_gemini_with_retry(prompt, AIInterviewRoadmap)
                if res and hasattr(res, 'roadmaps'):
                    return [r.model_dump() for r in res.roadmaps]
            except Exception as e:
                logger.error(f"Error generating dynamic roadmap: {e}")

        # Rule-based fallback if Gemini fails or is skipped
        all_issues = []
        for w in weaknesses:
            all_issues.append((w, "needs work"))
        for m in moderate:
            all_issues.append((m, "average"))

        for topic, lvl in all_issues:
            topic_lower = topic.lower()
            recs = ["Review core concepts and theoretical foundations."]
            res = ["GeeksforGeeks", "Official Documentation"]
            
            if "python" in topic_lower:
                recs = [
                    "Practice decorator patterns, closures, and custom generators.",
                    "Study Python memory management and garbage collection.",
                    "Solve intermediate exercises on HackerRank or LeetCode."
                ]
                res = ["Real Python (realpython.com)", "LeetCode Python track"]
            elif "sql" in topic_lower:
                recs = [
                    "Practice aggregate window functions (ROW_NUMBER, DENSE_RANK, SUM OVER).",
                    "Understand difference between CTEs, Subqueries, and Temp tables.",
                    "Solve hard SQL questions involving joins and aggregations."
                ]
                res = ["Mode Analytics SQL Tutorial", "Hackerrank SQL challenges"]
            elif "machine learning" in topic_lower or "ml" in topic_lower:
                recs = [
                    "Deep-dive into the mathematical derivation of gradient descent and SVMs.",
                    "Study ensemble methods and hyperparameter optimization techniques.",
                    "Practice explaining the bias-variance tradeoff with concrete mathematical formulations."
                ]
                res = ["StatQuest by Josh Starmer (YouTube)", "Hands-On Machine Learning (Book by Aurélien Géron)"]
            elif "react" in topic_lower:
                recs = [
                    "Study the virtual DOM reconciliation process and key matching details.",
                    "Implement complex custom hooks that manage side-effects or state sharing.",
                    "Understand React's concurrent rendering features and state-batching updates."
                ]
                res = ["React official documentation (react.dev)", "Kent C. Dodds epicreact.dev"]
            
            roadmap_items.append({
                "skill": topic,
                "current_level": lvl,
                "recommendations": recs,
                "resources": res
            })

        return roadmap_items
