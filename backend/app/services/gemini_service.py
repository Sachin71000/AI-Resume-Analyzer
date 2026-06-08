import logging
import json
import time
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Pydantic schema for AI Suggestions
class AISuggestion(BaseModel):
    category: str = Field(description="Must be one of: skills, content, formatting, ats, structure")
    priority: str = Field(description="Must be one of: high, medium, low")
    suggestion: str = Field(description="The actionable advice to improve the resume")
    example: str = Field(description="A concrete example of how to implement the suggestion (e.g., a rewritten bullet point)")

class AISuggestionsResponse(BaseModel):
    suggestions: list[AISuggestion]

# Pydantic schema for JD Parsing
class JDRequirements(BaseModel):
    title: str = Field(description="The job title")
    experience_level: str = Field(description="Must be one of: junior, mid, senior, lead")
    years_required: int | None = Field(description="Minimum years of experience required, or null if not specified")
    required_skills: list[str] = Field(description="List of required hard skills")
    preferred_skills: list[str] = Field(description="List of preferred or 'nice to have' hard skills")
    education_requirements: list[str] = Field(description="Required education degrees or certifications")
    key_responsibilities: list[str] = Field(description="Main job responsibilities")

class GeminiService:
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = model

    def parse_jd_requirements(self, jd_text: str) -> JDRequirements | None:
        """Parse job description into structured requirements using Gemini."""
        if not self.client:
            logger.warning("Gemini API key is not set. Skipping JD parsing.")
            return None
        
        prompt = f"""
        Parse this job description into structured data. Extract the required skills, preferred skills, 
        experience level, years required, education requirements, and key responsibilities.
        
        JOB DESCRIPTION:
        {jd_text}
        """
        
        return self._call_gemini_with_retry(prompt, JDRequirements)

    def generate_ai_suggestions(self, resume_text: str, jd_text: str, scores: dict, missing_skills: list) -> list[dict]:
        """Generate personalized AI suggestions based on analysis results."""
        if not self.client:
            logger.warning("Gemini API key is not set. Skipping AI suggestions.")
            return []

        prompt = f"""
        You are an expert resume reviewer and career coach.
        
        Given the following:
        - RESUME TEXT: {resume_text}
        - JOB DESCRIPTION: {jd_text}
        - MATCH SCORES: {json.dumps(scores)}
        - MISSING SKILLS: {json.dumps([s['name'] for s in missing_skills])}
        
        Provide up to 6 actionable, specific suggestions to improve this resume for this specific job.
        For each suggestion:
        1. Identify the problem clearly.
        2. Explain WHY it matters for this specific role.
        3. Give a concrete EXAMPLE of how to fix it (e.g., a rewritten bullet point, added section).
        
        Focus on:
        - Missing critical skills and how to demonstrate them.
        - Weak bullet points that need quantification.
        - Section improvements specific to this role.
        - ATS optimization tips.
        """
        
        response_model = self._call_gemini_with_retry(prompt, AISuggestionsResponse)
        
        if response_model and hasattr(response_model, 'suggestions'):
            suggestions = [s.model_dump() for s in response_model.suggestions]
            for s in suggestions:
                s['source'] = 'ai'
            return suggestions
        return []

    def extract_skills_from_text(self, text: str) -> list[dict]:
        """Deep skill extraction for free-text sections that might evade taxonomy matching."""
        if not self.client:
            return []
            
        prompt = f"""
        Extract all professional hard skills, tools, and technical concepts mentioned or strongly implied in this text.
        For each skill, also extract the proficiency level (beginner, intermediate, expert) based on context (e.g. years of experience, depth of usage).
        Return ONLY a JSON array of objects containing the skill names in canonical form (e.g., lowercase) and their proficiency.
        
        TEXT:
        {text}
        """
        
        class SkillProficiency(BaseModel):
            name: str
            proficiency: str = Field(description="One of: beginner, intermediate, expert")
            
        class SkillsList(BaseModel):
            skills: list[SkillProficiency]
            
        try:
            response = self._call_gemini_with_retry(prompt, SkillsList)
            if response and hasattr(response, 'skills'):
                return [s.model_dump() for s in response.skills]
            return []
        except Exception:
            return []

    def _call_gemini_with_retry(self, prompt: str, schema: type[BaseModel], max_retries: int = 3):
        """Helper to call Gemini API with exponential backoff and schema validation."""
        if not self.client:
            logger.warning("Gemini Client is not initialized. Skipping API call.")
            return None
            
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                    ),
                )
                return response.parsed
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 1s, 2s
                else:
                    logger.error("Max retries reached for Gemini API.")
                    return None
