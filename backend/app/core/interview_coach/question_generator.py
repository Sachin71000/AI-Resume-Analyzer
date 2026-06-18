"""
QuestionGenerator — Fully redesigned to fix:
  - B1: Static fallback loop (same hardcoded question repeated)
  - B5: Exact-only skill key matching (misses "Python 3", "scikit-learn" etc.)
  - B9: No deduplication within session
  - New: Topic rotation via TopicRotator
  - New: Context-aware Gemini prompts with cross-session memory injection
  - New: Diverse static fallback pool (never same Q twice)
"""
import os
import json
import random
import logging
import difflib
from pydantic import BaseModel, Field
from ...services.gemini_service import GeminiService
from .deduplication import DeduplicationEngine
from .topic_rotator import TopicRotator, TOPIC_INSTRUCTIONS

logger = logging.getLogger(__name__)

# ── Pydantic response schemas ────────────────────────────────────────────────

class AISkillQuestion(BaseModel):
    question: str = Field(description="A clear, specific interview question targeting this exact skill and difficulty level.")
    ideal_answer: str = Field(description="A highly accurate, detailed model answer with concrete examples a strong candidate would give.")
    keywords: list[str] = Field(description="5-8 key technical terms or concepts that must appear in a good answer.")
    category: str = Field(description="Specific sub-category of the skill (e.g. 'Memory Management', 'System Design').")
    topic_tag: str = Field(description="One-word tag for this question's theme (e.g. 'concurrency', 'scaling', 'debugging').")

class GeneralQuestions(BaseModel):
    questions: list[AISkillQuestion]

# ── Diverse static fallback pool (never repeats within 1 session) ────────────
DIVERSE_FALLBACK_POOL = [
    {
        "question": "Explain the SOLID principles and give a real-world example of the Single Responsibility Principle.",
        "ideal_answer": "SOLID is an acronym for five OOP design principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. SRP states that a class should have one reason to change. Example: a UserManager class that handles both user authentication AND sending emails violates SRP. Fix: split into AuthService and EmailService.",
        "keywords": ["SOLID", "SRP", "OOP", "class", "responsibility", "cohesion", "separation"],
        "category": "Design Principles",
        "type": "skill",
    },
    {
        "question": "What is the difference between synchronous and asynchronous programming? Describe an async pattern in your primary language.",
        "ideal_answer": "Synchronous code executes line-by-line, blocking execution until each operation completes. Async programming allows long-running operations (I/O, network) to run without blocking the main thread, improving throughput. In Python: asyncio with async/await. In JavaScript: Promises, async/await, event loop. Async is ideal for I/O-bound tasks; CPU-bound tasks should use multiprocessing.",
        "keywords": ["async", "await", "blocking", "I/O", "event loop", "concurrency", "throughput"],
        "category": "Concurrency",
        "type": "skill",
    },
    {
        "question": "Describe how you would design a caching layer for a high-traffic REST API.",
        "ideal_answer": "Use Redis or Memcached as a distributed cache. Implement cache-aside (lazy loading) pattern: check cache first, fetch from DB on miss and store result. Set appropriate TTLs based on data staleness requirements. Cache at multiple levels: CDN for static assets, application layer for API responses, DB query cache. Handle cache invalidation on write with pub/sub or write-through. Monitor hit rate with metrics.",
        "keywords": ["Redis", "cache-aside", "TTL", "invalidation", "CDN", "write-through", "hit rate"],
        "category": "System Design",
        "type": "skill",
    },
    {
        "question": "How do you approach debugging a production issue with high latency and no obvious error logs?",
        "ideal_answer": "Systematic approach: 1) Check dashboards for anomaly timing (deployments, traffic spikes). 2) Use distributed tracing (Jaeger/Zipkin) to find slow spans. 3) Profile DB queries with EXPLAIN ANALYZE. 4) Check GC pauses or memory pressure. 5) Look for thread pool exhaustion or connection pool saturation. 6) Compare metrics before/after the issue started. Start broad, narrow down with evidence.",
        "keywords": ["tracing", "latency", "profiling", "EXPLAIN", "metrics", "GC", "connection pool"],
        "category": "Debugging",
        "type": "skill",
    },
    {
        "question": "What is eventual consistency and when would you choose it over strong consistency in a distributed system?",
        "ideal_answer": "Eventual consistency means all replicas will converge to the same state eventually, but not necessarily immediately. Suitable for use cases where availability > consistency: social media feeds, shopping cart recommendations, DNS. Strong consistency is required when data correctness is critical: financial transactions, inventory management. CAP theorem trade-off: you can't have both high availability and strong consistency during a partition.",
        "keywords": ["eventual consistency", "strong consistency", "CAP theorem", "partition", "replica", "availability"],
        "category": "Distributed Systems",
        "type": "skill",
    },
    {
        "question": "Explain the concept of database normalization. What are 1NF, 2NF, and 3NF?",
        "ideal_answer": "Normalization eliminates data redundancy and ensures data integrity. 1NF: atomic values, no repeating groups. 2NF: 1NF + no partial dependency (non-key attributes depend on full primary key). 3NF: 2NF + no transitive dependency (non-key attributes depend only on PK, not other non-key attributes). Denormalization is sometimes used for read performance at the cost of redundancy.",
        "keywords": ["normalization", "1NF", "2NF", "3NF", "redundancy", "dependency", "atomic"],
        "category": "Database Design",
        "type": "skill",
    },
    {
        "question": "Describe the CI/CD pipeline you would set up for a Python REST API project.",
        "ideal_answer": "CI: trigger on every PR — run linting (flake8/ruff), type checking (mypy), unit tests (pytest), security scan (bandit), coverage check. CD: on merge to main — build Docker image, push to registry, deploy to staging, run smoke tests, promote to production with rolling/blue-green strategy. Use GitHub Actions or GitLab CI. Rollback strategy: maintain previous image tag for instant revert.",
        "keywords": ["CI/CD", "pytest", "Docker", "staging", "rolling deployment", "blue-green", "GitHub Actions"],
        "category": "DevOps",
        "type": "skill",
    },
    {
        "question": "How do you ensure security in a REST API? Name and explain at least 5 practices.",
        "ideal_answer": "1) Input validation & sanitization (prevent SQLi, XSS). 2) Authentication with JWT or OAuth2. 3) HTTPS/TLS for all traffic. 4) Rate limiting to prevent DDoS/brute force. 5) Least privilege access (RBAC). 6) Secrets management (env vars, Vault, no hardcoding). 7) Dependency scanning (Snyk, Safety). 8) CORS whitelist. 9) Logging and audit trails. 10) OWASP Top 10 checklist.",
        "keywords": ["JWT", "OAuth2", "HTTPS", "rate limiting", "RBAC", "OWASP", "sanitization", "CORS"],
        "category": "Security",
        "type": "skill",
    },
    {
        "question": "What are the differences between process, thread, and coroutine? When would you use each?",
        "ideal_answer": "Process: independent OS-managed unit with its own memory space. Use for CPU-bound parallelism. Thread: lightweight unit sharing process memory; use for I/O-bound parallelism with shared state. Coroutine: cooperative, user-space, single-threaded; use for I/O-bound concurrency with high connection counts (e.g., async web servers, 10k+ concurrent connections). Python coroutines via asyncio. Go uses goroutines. Rust uses async/await with tokio.",
        "keywords": ["process", "thread", "coroutine", "CPU-bound", "I/O-bound", "asyncio", "parallelism"],
        "category": "Concurrency",
        "type": "skill",
    },
    {
        "question": "Explain the Observer design pattern and give a use case where it applies.",
        "ideal_answer": "Observer pattern: a Subject object maintains a list of Observers and notifies them automatically of any state changes. Decouples event producers from consumers. Use cases: UI event handling (button listeners), pub/sub messaging systems, real-time notifications, model-view synchronization in MVC. In Python: can implement with __setattr__ hooks or libraries like RxPY. Django signals use this pattern.",
        "keywords": ["Observer", "Subject", "notify", "event", "pub/sub", "MVC", "decoupled"],
        "category": "Design Patterns",
        "type": "skill",
    },
]

# ── Alias map for fuzzy skill matching ──────────────────────────────────────
SKILL_ALIASES = {
    "python3": "python",
    "python 3": "python",
    "python3.x": "python",
    "scikit-learn": "machine learning",
    "sklearn": "machine learning",
    "tensorflow": "machine learning",
    "pytorch": "machine learning",
    "keras": "machine learning",
    "xgboost": "machine learning",
    "nodejs": "javascript",
    "node.js": "javascript",
    "node js": "javascript",
    "typescript": "javascript",
    "ts": "javascript",
    "postgres": "sql",
    "postgresql": "sql",
    "mysql": "sql",
    "sqlite": "sql",
    "reactjs": "react",
    "react.js": "react",
    "react js": "react",
    "vuejs": "javascript",
    "vue.js": "javascript",
    "angular": "javascript",
    "spring boot": "java",
    "springboot": "java",
    "asp.net": "c#",
    "dotnet": "c#",
    ".net": "c#",
    "aws lambda": "aws",
    "amazon web services": "aws",
    "gcp": "google cloud",
    "azure": "microsoft azure",
    "k8s": "kubernetes",
    "docker-compose": "docker",
    "mongodb": "nosql",
    "mongo": "nosql",
    "cassandra": "nosql",
    "dynamodb": "nosql",
    "elasticsearch": "nosql",
}


def _normalize_skill_key(skill: str) -> str:
    """
    Normalize a raw skill name to a canonical bank key.
    Order of precedence:
      1. Direct alias lookup
      2. Direct bank key match (lowercase)
      3. Fuzzy substring match
    """
    raw = skill.lower().strip()
    # 1. Alias map
    if raw in SKILL_ALIASES:
        return SKILL_ALIASES[raw]
    return raw


def _find_bank_key(skill_normalized: str, bank_skills: dict) -> str | None:
    """
    Find the best matching key in the question bank.
    Returns None if no reasonable match found.
    """
    # 1. Exact match
    if skill_normalized in bank_skills:
        return skill_normalized

    # 2. Substring match (e.g., "deep learning" contains "machine learning"'s key)
    for key in bank_skills:
        if key in skill_normalized or skill_normalized in key:
            return key

    # 3. Fuzzy match via difflib (cutoff=0.75 to avoid false positives)
    matches = difflib.get_close_matches(skill_normalized, list(bank_skills.keys()), n=1, cutoff=0.75)
    if matches:
        logger.debug(f"[QGen] Fuzzy matched '{skill_normalized}' → '{matches[0]}'")
        return matches[0]

    return None


class QuestionGenerator:
    def __init__(
        self,
        question_bank_path: str = None,
        gemini_service: GeminiService = None,
    ):
        if not question_bank_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            question_bank_path = os.path.join(base_dir, "data", "question_bank.json")

        self.question_bank_path = question_bank_path
        self.gemini_service = gemini_service
        self.question_bank = self._load_question_bank()
        self._fallback_pool_idx = 0  # rotating index for diverse fallbacks

    # ── Public API ────────────────────────────────────────────────────────────

    def generate_interview_questions(
        self,
        skills_found: list,
        resume_text: str,
        target_role: str,
        difficulty: str = "medium",
        total_count: int = 10,
        include_types: list = None,
        analysis_id: str = None,
    ) -> list[dict]:
        """
        Orchestrate question generation using topic rotation + deduplication.

        Changes from old version:
          - Uses TopicRotator for structured variety
          - Uses DeduplicationEngine to filter out previously-asked questions
          - Gemini prompts include asked-question history
          - Diverse static fallback pool (never repeats the same string)
        """
        if not include_types:
            include_types = ["skill", "project", "behavioral", "role"]

        difficulty = difficulty.lower()
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"

        # Init engines
        rotator = TopicRotator(total_questions=total_count)
        dedup = DeduplicationEngine(analysis_id=analysis_id or "anon")
        if analysis_id:
            dedup.load_history()

        skills_pool = self._extract_skill_names(skills_found)
        random.shuffle(skills_pool)
        skill_cursor = 0  # cycle through skills for variety

        asked_context = dedup.get_asked_texts(limit=15)  # for Gemini context injection
        questions: list[dict] = []

        for _ in range(total_count):
            topic, q_type = rotator.next_topic()

            # Skip disabled question types
            if q_type not in include_types:
                q_type = "skill"
                topic = "skill_core"

            candidate: dict | None = None

            if q_type == "behavioral":
                candidate = self._select_behavioral_question(dedup)
            elif q_type == "project":
                if resume_text and self.gemini_service:
                    candidate = self._generate_project_question(
                        resume_text, target_role, difficulty, asked_context, dedup
                    )
            elif q_type == "role":
                candidate = self._select_or_generate_role_question(
                    target_role, difficulty, topic, asked_context, dedup
                )

            # Default to skill question for 'skill' type or if specific type failed
            if not candidate:
                skill = skills_pool[skill_cursor % len(skills_pool)] if skills_pool else None
                skill_cursor += 1
                candidate = self._select_or_generate_skill_question(
                    skill, difficulty, topic, asked_context, dedup
                )

            if candidate:
                # Dedup check (final safety net)
                if dedup.is_duplicate(candidate["question"]):
                    # Try one alternative from fallback pool
                    candidate = self._get_rotating_fallback(dedup)

                # Mark as asked (in-memory + DB)
                dedup.mark_asked(candidate["question"], topic=topic, persist=bool(analysis_id))
                asked_context.append(candidate["question"])  # update local context

                candidate["topic"] = topic
                candidate["difficulty"] = difficulty
                candidate["index"] = len(questions) + 1
                questions.append(candidate)

        # Store rotator state in first question for session_manager to persist
        if questions:
            questions[0]["_rotator_state"] = rotator.to_state_dict()

        return questions

    # ── Internal generators ───────────────────────────────────────────────────

    def _select_behavioral_question(self, dedup: DeduplicationEngine) -> dict | None:
        """Select a non-repeated behavioral question from bank."""
        bank = self.question_bank.get("behavioral", [])
        random.shuffle(bank)
        for q in bank:
            if not dedup.is_duplicate(q["question"]):
                return {
                    "question": q["question"],
                    "ideal_answer": q["ideal_answer"],
                    "keywords": q.get("keywords", []),
                    "category": q.get("category", "Behavioral"),
                    "type": "behavioral",
                }
        # All behavioral questions exhausted — generate with Gemini
        if self.gemini_service:
            return self._generate_behavioral_via_gemini(dedup)
        return None

    def _generate_behavioral_via_gemini(self, dedup: DeduplicationEngine) -> dict | None:
        """Generate a unique behavioral question via Gemini when bank is exhausted."""
        asked = dedup.get_asked_texts(limit=10)
        prompt = f"""
You are an expert behavioral interviewer.
Generate a UNIQUE STAR-format behavioral interview question.

ALREADY ASKED (DO NOT REPEAT OR REPHRASE):
{chr(10).join(f'- {q}' for q in asked) if asked else 'None yet'}

Requirements:
- Use STAR framework prompt (Situation, Task, Action, Result)
- Focus on: teamwork, leadership, conflict resolution, problem ownership, or innovation
- Must be different from all questions above
"""
        try:
            res = self.gemini_service._call_gemini_with_retry(prompt, AISkillQuestion)
            if res:
                return {
                    "question": res.question,
                    "ideal_answer": res.ideal_answer,
                    "keywords": res.keywords,
                    "category": res.category,
                    "type": "behavioral",
                }
        except Exception as e:
            logger.error(f"[QGen] Gemini behavioral generation failed: {e}")
        return None

    def _select_or_generate_skill_question(
        self,
        skill: str | None,
        difficulty: str,
        topic: str,
        asked_context: list[str],
        dedup: DeduplicationEngine,
    ) -> dict | None:
        """
        Fixed B5: Use fuzzy matching + alias map before falling back to Gemini.
        Fixed B1: Never loops same static string — uses rotating diverse fallback pool.
        """
        if skill:
            normalized = _normalize_skill_key(skill)
            bank_skills = self.question_bank.get("skills", {})
            matched_key = _find_bank_key(normalized, bank_skills)

            if matched_key:
                diff_dict = bank_skills[matched_key]
                options = (
                    diff_dict.get(difficulty)
                    or diff_dict.get("medium")
                    or diff_dict.get("easy")
                    or diff_dict.get("hard")
                    or []
                )
                random.shuffle(options)
                for q in options:
                    if not dedup.is_duplicate(q["question"]):
                        return {
                            "question": q["question"],
                            "ideal_answer": q["ideal_answer"],
                            "keywords": q.get("keywords", []),
                            "category": q.get("category", "Technical"),
                            "type": "skill",
                            "skill": skill,
                        }

        # Gemini generation with context injection
        if self.gemini_service:
            result = self._generate_skill_via_gemini(skill, difficulty, topic, asked_context)
            if result:
                return result

        # Diverse rotating fallback — B1 FIX: never same string twice
        return self._get_rotating_fallback(dedup)

    def _generate_skill_via_gemini(
        self,
        skill: str | None,
        difficulty: str,
        topic: str,
        asked_context: list[str],
    ) -> dict | None:
        """Context-aware Gemini question generation with asked-question memory."""
        topic_instruction = TOPIC_INSTRUCTIONS.get(topic, "Ask a relevant technical question.")
        asked_summary = (
            "\n".join(f"- {q}" for q in asked_context[-10:])
            if asked_context
            else "None yet"
        )

        skill_context = f"for the skill: '{skill}'" if skill else "for a senior software engineer"
        prompt = f"""
You are a senior technical interviewer conducting a {difficulty}-level technical interview.

TASK: Generate exactly 1 high-quality technical interview question {skill_context}.

QUESTION FOCUS: {topic_instruction}
DIFFICULTY: {difficulty}

ALREADY ASKED IN THIS SESSION — DO NOT REPEAT OR REPHRASE ANY OF THESE:
{asked_summary}

OUTPUT REQUIREMENTS:
- The question must be specific, not generic
- Ideal answer must be detailed with real technical depth
- Include 5-8 technical keywords expected in a strong answer
- Assign a meaningful category (e.g., 'Memory Management', 'Concurrency', 'API Design')
- Include a topic_tag (one word: e.g., 'caching', 'scaling', 'testing')
"""
        try:
            res = self.gemini_service._call_gemini_with_retry(prompt, AISkillQuestion)
            if res:
                return {
                    "question": res.question,
                    "ideal_answer": res.ideal_answer,
                    "keywords": res.keywords,
                    "category": res.category,
                    "type": "skill",
                    "skill": skill or "Software Engineering",
                }
        except Exception as e:
            logger.error(f"[QGen] Gemini skill question generation failed: {e}")
        return None

    def _generate_project_question(
        self,
        resume_text: str,
        role: str,
        difficulty: str,
        asked_context: list[str],
        dedup: DeduplicationEngine,
    ) -> dict | None:
        """Generate a project deep-dive question using resume context."""
        asked_summary = "\n".join(f"- {q}" for q in asked_context[-8:]) or "None"
        prompt = f"""
You are a senior technical interviewer.
Analyze this resume excerpt and identify the most technically complex project listed.
Generate 1 deep-dive interview question about that specific project.

RESUME EXCERPT:
{resume_text[:2500]}

ROLE: {role}
DIFFICULTY: {difficulty}

ALREADY ASKED (avoid these topics/phrasings):
{asked_summary}

Requirements:
- Reference the specific project by name
- Focus on: architecture decisions, technology tradeoffs, scalability challenges, or lessons learned
- The question should require the candidate to explain WHY they made specific decisions
"""
        try:
            res = self.gemini_service._call_gemini_with_retry(prompt, AISkillQuestion)
            if res and not dedup.is_duplicate(res.question):
                return {
                    "question": res.question,
                    "ideal_answer": res.ideal_answer,
                    "keywords": res.keywords,
                    "category": f"Project: {res.category}",
                    "type": "project",
                }
        except Exception as e:
            logger.error(f"[QGen] Gemini project question failed: {e}")
        return None

    def _select_or_generate_role_question(
        self,
        role: str,
        difficulty: str,
        topic: str,
        asked_context: list[str],
        dedup: DeduplicationEngine,
    ) -> dict | None:
        """Select role-based question from bank or generate via Gemini."""
        bank_roles = self.question_bank.get("role_based", {})
        role_key = role.lower()

        matched_key = None
        for key in bank_roles:
            if key in role_key or role_key in key:
                matched_key = key
                break

        if matched_key and bank_roles[matched_key]:
            options = list(bank_roles[matched_key])
            random.shuffle(options)
            for q in options:
                if not dedup.is_duplicate(q["question"]):
                    return {
                        "question": q["question"],
                        "ideal_answer": q["ideal_answer"],
                        "keywords": q.get("keywords", []),
                        "category": q.get("category", "System Design"),
                        "type": "role",
                        "role": matched_key,
                    }

        if self.gemini_service:
            asked_summary = "\n".join(f"- {q}" for q in asked_context[-8:]) or "None"
            topic_inst = TOPIC_INSTRUCTIONS.get(topic, "Ask a role-specific situational question.")
            prompt = f"""
You are a senior {role} interviewer.
Generate a {difficulty}-level situational/system-design question for a {role} candidate.

FOCUS: {topic_inst}

ALREADY ASKED (avoid these):
{asked_summary}

Requirements:
- Must be specific to the {role} role and its real-world responsibilities
- Should test judgment, architecture sense, or leadership (depending on topic)
"""
            try:
                res = self.gemini_service._call_gemini_with_retry(prompt, AISkillQuestion)
                if res and not dedup.is_duplicate(res.question):
                    return {
                        "question": res.question,
                        "ideal_answer": res.ideal_answer,
                        "keywords": res.keywords,
                        "category": res.category,
                        "type": "role",
                        "role": role,
                    }
            except Exception as e:
                logger.error(f"[QGen] Role question generation failed: {e}")

        return None

    def _get_rotating_fallback(self, dedup: DeduplicationEngine) -> dict:
        """
        B1 FIX: Return a rotating question from the DIVERSE_FALLBACK_POOL.
        Each call returns a different question, cycling through the pool.
        Only resets when all fallbacks have been used in this session.
        """
        pool = list(DIVERSE_FALLBACK_POOL)
        random.shuffle(pool)
        for q in pool:
            if not dedup.is_duplicate(q["question"]):
                logger.info(f"[QGen] Using diverse fallback: {q['question'][:50]}...")
                return dict(q)

        # All fallbacks used — generate a completely new one from Gemini or create variant
        logger.warning("[QGen] All diverse fallbacks exhausted. Generating emergency question.")
        if self.gemini_service:
            asked = dedup.get_asked_texts(limit=20)
            try:
                prompt = f"""
Generate a unique, advanced software engineering interview question that hasn't been asked yet.
Already asked (avoid these completely):
{chr(10).join(f'- {q}' for q in asked[:15])}
Make it about: design patterns, system architecture, or software quality.
"""
                res = self.gemini_service._call_gemini_with_retry(prompt, AISkillQuestion)
                if res:
                    return {
                        "question": res.question,
                        "ideal_answer": res.ideal_answer,
                        "keywords": res.keywords,
                        "category": res.category,
                        "type": "skill",
                        "skill": "Software Engineering",
                    }
            except Exception:
                pass

        # Absolute last resort — different static Q with random variation
        # (This should essentially never happen with 10-question sessions)
        variants = [
            "How do you approach technical debt reduction in a legacy codebase without disrupting production?",
            "Describe your process for writing effective code reviews. What do you look for?",
            "How would you design a feature flag system for gradual rollouts?",
        ]
        q_text = random.choice(variants)
        return {
            "question": q_text,
            "ideal_answer": "A strong answer demonstrates systematic thinking, team collaboration awareness, risk management, and practical engineering judgment.",
            "keywords": ["systematic", "collaboration", "risk", "incremental", "testing"],
            "category": "Engineering Excellence",
            "type": "skill",
            "skill": "Software Engineering",
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _load_question_bank(self) -> dict:
        """Load question bank JSON with safe fallback."""
        try:
            if os.path.exists(self.question_bank_path):
                with open(self.question_bank_path, "r") as f:
                    return json.load(f)
            logger.warning(f"[QGen] Bank not found at {self.question_bank_path}. Using empty bank.")
        except Exception as e:
            logger.error(f"[QGen] Error loading question_bank.json: {e}")
        return {"skills": {}, "behavioral": [], "role_based": {}}

    def _extract_skill_names(self, skills_found: list) -> list[str]:
        """Normalize and extract skill names from diverse input formats."""
        names = []
        for s in skills_found:
            if isinstance(s, dict):
                name = s.get("name") or s.get("skill") or ""
            else:
                name = str(s)
            name = name.strip()
            if name:
                names.append(name)
        return names if names else ["Software Engineering"]
