import logging

logger = logging.getLogger(__name__)

class DifficultyAdapter:
    @staticmethod
    def adapt_difficulty(current_difficulty: str, recent_scores: list[float]) -> str:
        """
        Adaptive difficulty logic:
        Given current difficulty ('easy', 'medium', 'hard') and a list of floats representing recent scores (0-10):
        - If the average of the last 2-3 answers is >= 8.0: increase difficulty
        - If the average of the last 2-3 answers is <= 4.5: decrease difficulty
        - Otherwise, maintain difficulty
        """
        difficulty_levels = ["easy", "medium", "hard"]
        
        # Guard: Need at least 2 questions answered to make a decision
        if not recent_scores or len(recent_scores) < 2:
            return current_difficulty

        # Take at most the last 3 questions for local context
        window = recent_scores[-3:]
        avg_score = sum(window) / len(window)
        
        current_lower = current_difficulty.lower()
        if current_lower not in difficulty_levels:
            current_lower = "medium"

        current_idx = difficulty_levels.index(current_lower)

        if avg_score >= 8.0:
            if current_idx < len(difficulty_levels) - 1:
                new_difficulty = difficulty_levels[current_idx + 1]
                logger.info(f"Performance high (avg: {avg_score:.2f}). Adapting difficulty: {current_lower} -> {new_difficulty}")
                return new_difficulty
        elif avg_score <= 4.5:
            if current_idx > 0:
                new_difficulty = difficulty_levels[current_idx - 1]
                logger.info(f"Performance low (avg: {avg_score:.2f}). Adapting difficulty: {current_lower} -> {new_difficulty}")
                return new_difficulty

        return current_lower
