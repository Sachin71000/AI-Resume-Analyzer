import os
import json
import random
import logging
from pydantic import BaseModel, Field
from ...services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class AISkillQuestion(BaseModel):
    question: str = Field(description="A clear technical interview question for the specific skill and difficulty.")
    ideal_answer: str = Field(description="A highly accurate, detailed ideal answer that candidates should aim for.")
    keywords: list[str] = Field(description="5-8 key technical terms, libraries, or concepts that must be present in a good answer.")
    category: str = Field(description="Specific sub-category or domain of the skill.")

class AIProjectQuestions(BaseModel):
    questions: list[dict] = Field(
        description="A list of 2-3 questions about the projects, assessing architectural decisions, trade-offs, and technologies."
    )

class QuestionGenerator:
    def __init__(self, question_bank_path: str = None, gemini_service: GeminiService = None):
        if not question_bank_path:
            # Resolve relative to backend/data
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            question_bank_path = os.path.join(base_dir, 'data', 'question_bank.json')
        
        self.question_bank_path = question_bank_path
        self.gemini_service = gemini_service
        self.question_bank = self._load_question_bank()

    def _load_question_bank(self) -> dict:
        """Loads question bank from JSON file with safe fallback."""
        try:
            if os.path.exists(self.question_bank_path):
                with open(self.question_bank_path, 'r') as f:
                    return json.load(f)
            logger.warning(f"Question bank path not found: {self.question_bank_path}. Using empty bank.")
            return {"skills": {}, "behavioral": [], "role_based": {}}
        except Exception as e:
            logger.error(f"Error loading question_bank.json: {e}")
            return {"skills": {}, "behavioral": [], "role_based": {}}

    def generate_interview_questions(
        self,
        skills_found: list,
        resume_text: str,
        target_role: str,
        difficulty: str = "medium",
        total_count: int = 10,
        include_types: list = None
    ) -> list[dict]:
        """
        Orchestrates selection and generation of questions:
        - Technical/Skill questions: From bank or Gemini
        - Project-based questions: Extracted and generated using Gemini
        - Role-based questions: Inferred role situational questions
        - Behavioral questions: STAR-based
        """
        if not include_types:
            include_types = ["skill", "project", "behavioral", "role"]

        difficulty = difficulty.lower()
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"

        questions = []
        
        # 1. Behavioral Question (Warmup)
        if "behavioral" in include_types:
            behavioral_q = self._select_behavioral_question()
            if behavioral_q:
                questions.append(behavioral_q)

        # 2. Project-Based Questions (Dynamic via Gemini)
        if "project" in include_types and self.gemini_service and resume_text:
            project_qs = self._generate_project_questions(resume_text, target_role, difficulty)
            questions.extend(project_qs)

        # 3. Role-Based Question
        if "role" in include_types:
            role_q = self._select_role_question(target_role, difficulty)
            if role_q:
                questions.append(role_q)

        # 4. Core Technical/Skill Questions
        if "skill" in include_types and skills_found:
            # We want to fill the remaining slots with skill questions
            needed = total_count - len(questions)
            if needed > 0:
                skill_qs = self._select_skill_questions(skills_found, difficulty, needed)
                questions.extend(skill_qs)

        # Shuffle middle questions to feel like a real flow, but keep behavioral first/last if appropriate
        # For simple sequencing:
        # Sort or structure the order: Warmup -> Skills -> Projects -> Role -> Behavioral closing
        # Let's clean the list, assign indices, and return.
        
        final_questions = []
        for i, q in enumerate(questions[:total_count]):
            q_copy = q.copy()
            q_copy["index"] = i + 1
            q_copy["difficulty"] = difficulty
            final_questions.append(q_copy)

        return final_questions

    def _select_behavioral_question(self) -> dict | None:
        """Select a behavioral question from bank."""
        bank_behavioral = self.question_bank.get("behavioral", [])
        if bank_behavioral:
            q = random.choice(bank_behavioral)
            return {
                "question": q["question"],
                "ideal_answer": q["ideal_answer"],
                "keywords": q.get("keywords", []),
                "category": "Behavioral",
                "type": "behavioral"
            }
        return None

    def _select_role_question(self, role: str, difficulty: str) -> dict | None:
        """Select role-specific situational question or generate one."""
        role_key = role.lower()
        # Find matching key in role_based bank
        bank_roles = self.question_bank.get("role_based", {})
        matched_key = None
        for key in bank_roles.keys():
            if key in role_key or role_key in key:
                matched_key = key
                break

        if matched_key and bank_roles[matched_key]:
            # Try to match difficulty if possible, otherwise grab random
            options = bank_roles[matched_key]
            q = random.choice(options)
            return {
                "question": q["question"],
                "ideal_answer": q["ideal_answer"],
                "keywords": q.get("keywords", []),
                "category": q.get("category", "System Design"),
                "type": "role",
                "role": matched_key
            }
        
        # Fallback to Gemini if available to generate a situational role-based question
        if self.gemini_service:
            prompt = f"""
            Generate a high-quality situational interview question for a candidate applying for the role of {role}.
            The question difficulty should be {difficulty}.
            Provide a clear question, a detailed ideal answer, a list of 5 expected keywords, and a category.
            """
            try:
                res = self.gemini_service._call_gemini_with_retry(prompt, AISkillQuestion)
                if res:
                    return {
                        "question": res.question,
                        "ideal_answer": res.ideal_answer,
                        "keywords": res.keywords,
                        "category": res.category,
                        "type": "role",
                        "role": role
                    }
            except Exception as e:
                logger.error(f"Error generating dynamic role question: {e}")

        # Static fallback if everything else fails
        return {
            "question": f"As a {role}, describe how you approach designing a scalable system or workflow under a tight deadline.",
            "ideal_answer": "A structured explanation following the lifecycle: requirements gathering, component decomposition, trade-off analysis, testing, and progressive deployment.",
            "keywords": ["requirements", "decomposition", "trade-off", "scalability", "deadline"],
            "category": "System Design",
            "type": "role",
            "role": role
        }

    def _select_skill_questions(self, skills: list, difficulty: str, count: int) -> list[dict]:
        """Select or generate technical questions based on list of skills."""
        selected_questions = []
        skills_pool = [s.get('name') if isinstance(s, dict) else str(s) for s in skills]
        
        # Shuffle pool to ensure random coverage
        random.shuffle(skills_pool)
        
        # Loop through skills and pull from bank, or generate if needed
        for skill in skills_pool:
            if len(selected_questions) >= count:
                break
                
            skill_key = skill.lower()
            bank_skills = self.question_bank.get("skills", {})
            
            matched_key = None
            for key in bank_skills.keys():
                if key == skill_key:
                    matched_key = key
                    break

            if matched_key:
                diff_dict = bank_skills[matched_key]
                options = diff_dict.get(difficulty, [])
                if not options:
                    # try medium fallback if requested difficulty empty
                    options = diff_dict.get("medium", []) or diff_dict.get("easy", []) or diff_dict.get("hard", [])
                
                if options:
                    q = random.choice(options)
                    selected_questions.append({
                        "question": q["question"],
                        "ideal_answer": q["ideal_answer"],
                        "keywords": q.get("keywords", []),
                        "category": q.get("category", "Technical"),
                        "type": "skill",
                        "skill": skill
                    })
                    continue

            # Fallback to dynamic Gemini generation if skill not in bank
            if self.gemini_service:
                logger.info(f"Generating dynamic question for skill '{skill}' with difficulty '{difficulty}'")
                prompt = f"""
                You are a senior technical interviewer.
                Generate a high-quality interview question for the skill: '{skill}'.
                Difficulty level: '{difficulty}'.
                
                Provide a clear question, a detailed ideal answer, a list of 5-8 expected keywords, and a subcategory.
                """
                try:
                    res = self.gemini_service._call_gemini_with_retry(prompt, AISkillQuestion)
                    if res:
                        selected_questions.append({
                            "question": res.question,
                            "ideal_answer": res.ideal_answer,
                            "keywords": res.keywords,
                            "category": res.category,
                            "type": "skill",
                            "skill": skill
                        })
                except Exception as e:
                    logger.error(f"Error generating dynamic skill question: {e}")

        # If we still need more questions, fill up with general software engineering or logic questions
        if len(selected_questions) < count and self.gemini_service:
            # Let's generate general programming questions based on the skills list
            needed = count - len(selected_questions)
            prompt = f"""
            Generate {needed} technical interview questions for a candidate with skills: {', '.join(skills_pool)}.
            Difficulty: {difficulty}.
            Provide them as a JSON list.
            """
            class GeneralQuestions(BaseModel):
                questions: list[AISkillQuestion]
                
            try:
                res = self.gemini_service._call_gemini_with_retry(prompt, GeneralQuestions)
                if res and hasattr(res, 'questions'):
                    for q in res.questions:
                        selected_questions.append({
                            "question": q.question,
                            "ideal_answer": q.ideal_answer,
                            "keywords": q.keywords,
                            "category": q.category,
                            "type": "skill",
                            "skill": skills_pool[0] if skills_pool else "General CS"
                        })
            except Exception as e:
                logger.error(f"Error generating general questions: {e}")

        # Static fallback if everything else fails
        while len(selected_questions) < count:
            selected_questions.append({
                "question": f"Explain what principles you follow to write clean, maintainable, and well-documented code in a team project.",
                "ideal_answer": "Principles include SOLID principles, DRY (Don't Repeat Yourself), writing descriptive naming conventions, adding clear docstrings/comments, using version control systematically, and writing unit tests.",
                "keywords": ["SOLID", "DRY", "naming", "comments", "git", "tests"],
                "category": "Best Practices",
                "type": "skill",
                "skill": "Software Engineering"
            })

        return selected_questions[:count]

    def _generate_project_questions(self, resume_text: str, role: str, difficulty: str) -> list[dict]:
        """Uses Gemini to extract a project from the resume and generate relevant deep-dive questions."""
        if not self.gemini_service:
            return []

        prompt = f"""
        Analyze this resume text and identify the main technical projects listed.
        Select the most complex or relevant project for a {role} role.
        Generate 1 deep-dive interview question about this project, targeting architectural choices, technological trade-offs, or implementation challenges.
        Difficulty level: {difficulty}.
        
        Provide the output in a structured format containing:
        - The question (referencing the specific project name)
        - The ideal answer structure (what a candidate should address, e.g. details of tech stack, architectural layers, hurdles faced)
        - 5 key terms/technologies expected in the answer
        - The project name as the category
        """
        
        try:
            res = self.gemini_service._call_gemini_with_retry(prompt, AISkillQuestion)
            if res:
                return [{
                    "question": res.question,
                    "ideal_answer": res.ideal_answer,
                    "keywords": res.keywords,
                    "category": f"Project: {res.category}",
                    "type": "project"
                }]
        except Exception as e:
            logger.error(f"Error generating dynamic project question: {e}")

        return []
