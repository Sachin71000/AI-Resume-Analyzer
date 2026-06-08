<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Gemini_AI-2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini" />
  <img src="https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind" />
</p>

# 🎯 AAT — AI-Powered Resume Analyzer & Interview Coach

**AAT** (AI Analysis Tool) is a full-stack intelligent resume analysis platform that combines traditional NLP techniques with Google's Gemini AI to deliver deep resume scoring, ATS compatibility checks, skill gap analysis, improvement tracking, and a fully interactive AI-powered mock interview coaching system.

> Built as an end-to-end ML + NLP + Full Stack project demonstrating real-world applicability of text analysis pipelines, TF-IDF vectorization, cosine similarity scoring, structured AI generation with Pydantic schemas, and modern React interfaces.

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#1-backend-setup)
  - [Frontend Setup](#2-frontend-setup)
  - [Environment Variables](#3-environment-variables)
  - [Running the Application](#4-running-the-application)
- [Usage Guide](#-usage-guide)
- [API Reference](#-api-reference)
- [NLP & ML Pipeline](#-nlp--ml-pipeline)
- [Interview Coach System](#-interview-coach-system)
- [Database Schema](#-database-schema)
- [Testing](#-testing)
- [Screenshots](#-screenshots)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 📄 Resume Analysis Engine
- **Multi-format parsing** — Supports PDF (`.pdf`) and Word (`.doc`, `.docx`) resume uploads
- **TF-IDF cosine similarity** — Computes semantic similarity between resume text and job description using scikit-learn's TF-IDF vectorizer
- **Hybrid scoring system** — 5-factor weighted scoring:
  - TF-IDF Similarity (25%)
  - Semantic Match (20%)
  - Skill Overlap (30%)
  - Section Coverage (15%)
  - Keyword Density (10%)
- **Intelligent skill extraction** — Taxonomy-based matching with 500+ skills across categories (programming languages, frameworks, databases, cloud, DevOps, soft skills, etc.)
- **Section detection** — Identifies resume sections (Experience, Education, Skills, Projects, Summary, etc.) and flags missing required sections
- **Quality analysis** — Word count, action verb usage, quantification metrics, contact information completeness, bullet point structure
- **ATS compatibility scoring** — 10-factor ATS audit covering keyword match, standard headings, contact info, formatting, spelling, readability, and more

### 🤖 AI-Powered Features (Gemini 2.0 Flash)
- **AI suggestions** — Personalized, actionable resume improvement suggestions with concrete examples
- **JD parsing** — Structured extraction of required skills, preferred skills, experience level, and responsibilities from job descriptions
- **Deep skill extraction** — AI-based skill discovery from free-text sections that evade taxonomy matching

### 🎤 AI Interview Coach
- **Personalized mock interviews** — Generates interview questions based on extracted resume skills, projects, and target role
- **4 question types** — Technical/skill-based, project deep-dives, role-specific situational, and behavioral (STAR method)
- **3 difficulty levels** — Easy, medium, hard with configurable question counts (5/10/15/20)
- **Real-time voice input** — Speech-to-text via Web Speech API for hands-free answering
- **3-layer answer evaluation**:
  - TF-IDF cosine similarity vs. ideal answer (25%)
  - Keyword coverage analysis (25%)
  - Gemini AI semantic assessment — correctness, completeness, clarity, depth (50%)
- **Communication metrics** — Word count, filler word detection, fluency scoring
- **Detailed feedback** — Per-question strengths, weaknesses, and actionable improvement tips
- **Study roadmap** — Personalized learning recommendations for weak topics with curated resources
- **Per-question timer** — 3-minute countdown per question with auto-submit

### 📊 Additional Features
- **Analysis history** — Full history of all resume analyses with search, sort, and pagination
- **Resume comparison** — Side-by-side comparison of two analyses with score deltas, skills gained/lost
- **Improvement tracking** — Re-analyze an improved resume version linked to the original, showing score progression
- **PDF export** — Download analysis results as a formatted PDF report
- **Analysis labeling** — Custom labels for organizing analyses
- **Batch delete** — Multi-select and delete analyses

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 19)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ HomePage  │  │ Results  │  │ History  │  │  Interview Coach  │  │
│  │ (Upload)  │  │  Page    │  │  Page    │  │  Setup/Live/Eval  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       │              │             │                  │             │
│       └──────────────┴─────────────┴──────────────────┘             │
│                              │  Axios HTTP                         │
│                      Vite Dev Proxy (/api)                         │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────┐
│                     BACKEND (Flask 3.0)                            │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐    │
│  │              REST API Blueprints (/api/*)                  │    │
│  │  /analyze  /history  /compare  /export  /interview/*       │    │
│  └───────────────────────────┼────────────────────────────────┘    │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐    │
│  │                    Service Layer                            │    │
│  │   AnalysisService  │  InterviewService  │  ExportService    │    │
│  └───────────────────────────┼────────────────────────────────┘    │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐    │
│  │                NLP / ML Core Modules                       │    │
│  │  Parser │ SkillExtractor │ MatchingEngine │ ATSScorer      │    │
│  │  SectionDetector │ QualityAnalyzer │ BulletAnalyzer        │    │
│  │  SuggestionGenerator │ ExperienceGrader │ Preprocessor     │    │
│  │  ┌─────────────────────────────────────────────────┐       │    │
│  │  │            Interview Coach Core                 │       │    │
│  │  │  QuestionGenerator │ SessionManager │ Evaluator │       │    │
│  │  │  FeedbackGenerator │ DifficultyAdapter          │       │    │
│  │  └─────────────────────────────────────────────────┘       │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              │                                     │
│  ┌──────────────────┐  ┌────┴───────────────┐                     │
│  │   SQLite (ORM)   │  │  Gemini 2.0 Flash  │                     │
│  │   SQLAlchemy     │  │  (Structured Gen)   │                     │
│  └──────────────────┘  └────────────────────┘                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.12+** | Core language |
| **Flask 3.0** | Web framework / REST API |
| **Flask-SQLAlchemy 3.1** | ORM / Database abstraction |
| **SQLite** | Database (zero-config, file-based) |
| **scikit-learn 1.4** | TF-IDF vectorization, cosine similarity |
| **spaCy 3.7** | NLP tokenization and text preprocessing |
| **Google Gemini AI** (`google-genai`) | Structured AI generation with Pydantic schemas |
| **Pydantic 2.0** | Data validation and AI response schemas |
| **pdfplumber** | PDF text extraction |
| **python-docx** | Word document parsing |
| **textstat** | Readability scoring (Flesch-Kincaid) |
| **pyspellchecker** | Spelling error detection for ATS |
| **fpdf2** | PDF report generation |
| **pandas** | Data manipulation |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | UI framework |
| **TypeScript 6.0** | Type-safe JavaScript |
| **Vite 8.0** | Build tool and dev server |
| **TailwindCSS 3.4** | Utility-first CSS |
| **React Router 7** | Client-side routing |
| **Framer Motion** | Animations and transitions |
| **Recharts 3.8** | Data visualization (Radar charts, gauges) |
| **Lucide React** | Icon library |
| **Axios** | HTTP client |
| **canvas-confetti** | Celebration effects |

---

## 📁 Project Structure

```
AAT/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── config.py                # Configuration (env vars, DB URI, upload limits)
│   │   ├── extensions.py            # SQLAlchemy & CORS initialization
│   │   │
│   │   ├── core/                    # NLP / ML processing modules
│   │   │   ├── parser.py            # PDF & DOCX text extraction
│   │   │   ├── preprocessor.py      # Text cleaning, lemmatization, stopword removal
│   │   │   ├── skill_extractor.py   # Taxonomy-based + AI skill extraction
│   │   │   ├── section_detector.py  # Resume section identification
│   │   │   ├── matching_engine.py   # TF-IDF + hybrid scoring engine
│   │   │   ├── quality_analyzer.py  # Writing quality analysis
│   │   │   ├── ats_scorer.py        # ATS compatibility scoring (10 factors)
│   │   │   ├── bullet_analyzer.py   # Bullet point quality analysis
│   │   │   ├── experience_grader.py # Work experience grading
│   │   │   ├── suggestion_generator.py  # Rule-based improvement suggestions
│   │   │   │
│   │   │   └── interview_coach/     # AI Interview Coach module
│   │   │       ├── __init__.py
│   │   │       ├── question_generator.py  # Question generation (bank + Gemini)
│   │   │       ├── session_manager.py     # Interview session state management
│   │   │       ├── evaluator.py           # 3-layer answer evaluation engine
│   │   │       ├── feedback.py            # Session report & study roadmap generation
│   │   │       └── difficulty.py          # Dynamic difficulty adaptation
│   │   │
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py          # Analysis result model
│   │   │   └── interview.py         # InterviewSession + InterviewAnswer models
│   │   │
│   │   ├── routes/                  # Flask API blueprints
│   │   │   ├── analyze.py           # POST /api/analyze, /api/analyze/improve
│   │   │   ├── history.py           # GET /api/history, /api/analysis/<id>
│   │   │   ├── compare.py           # POST /api/compare
│   │   │   ├── export.py            # GET /api/export/<id>
│   │   │   └── interview.py         # Interview CRUD (start, answer, complete, results, history)
│   │   │
│   │   └── services/               # Business logic layer
│   │       ├── analysis_service.py  # Orchestrates the full analysis pipeline
│   │       ├── interview_service.py # Interview session orchestration
│   │       ├── gemini_service.py    # Google Gemini AI integration
│   │       └── export_service.py    # PDF report generation
│   │
│   ├── data/                        # Static data files
│   │   ├── skills_taxonomy.json     # 500+ skills organized by category
│   │   ├── skill_contexts.json      # Contextual skill relationships
│   │   ├── synonyms.json            # Skill synonym mappings
│   │   ├── action_verbs.json        # Strong/weak action verbs for quality analysis
│   │   └── question_bank.json       # Interview question bank by skill & difficulty
│   │
│   ├── instance/                    # SQLite database (auto-created)
│   ├── uploads/                     # Temporary resume upload directory
│   ├── .env                         # Environment variables (not committed)
│   ├── .env.example                 # Example environment template
│   ├── requirements.txt             # Python dependencies
│   ├── run.py                       # Application entry point
│   ├── test_interview.py            # Interview module unit tests
│   └── test_brutal_interview.py     # Stress tests (edge cases, unicode, payloads)
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                 # React entry point
│   │   ├── App.tsx                  # Root component with React Router
│   │   ├── App.css                  # Global application styles
│   │   ├── index.css                # Base CSS & Tailwind imports
│   │   │
│   │   ├── pages/                   # Page-level components
│   │   │   ├── HomePage.tsx         # Resume upload + JD input form
│   │   │   ├── ResultsPage.tsx      # Full analysis results dashboard
│   │   │   ├── HistoryPage.tsx      # Analysis history with search & sort
│   │   │   ├── AnalysisDetailPage.tsx   # Individual analysis detail view
│   │   │   ├── ComparePage.tsx      # Side-by-side analysis comparison
│   │   │   ├── InterviewSetupPage.tsx   # Interview configuration
│   │   │   ├── InterviewPage.tsx    # Live mock interview room
│   │   │   └── InterviewResultsPage.tsx # Interview evaluation report
│   │   │
│   │   ├── components/
│   │   │   ├── Layout.tsx           # App shell with navigation
│   │   │   ├── ui/                  # Reusable UI components
│   │   │   │   ├── ScoreGauge.tsx   # Animated circular score gauge
│   │   │   │   ├── ScoreCard.tsx    # Score card with progress bar
│   │   │   │   ├── ScoreRadarChart.tsx  # 6-axis radar chart
│   │   │   │   ├── SkillBadge.tsx   # Skill pill with source indicator
│   │   │   │   ├── JDPreview.tsx    # Job description preview card
│   │   │   │   ├── ImprovementRoadmap.tsx  # Improvement suggestions UI
│   │   │   │   └── Confetti.tsx     # Celebration confetti effect
│   │   │   └── reactbits/          # Third-party component adaptations
│   │   │
│   │   ├── services/
│   │   │   └── api.ts              # Axios API client (all endpoints)
│   │   │
│   │   └── types/
│   │       └── index.ts            # TypeScript interfaces for all API responses
│   │
│   ├── package.json
│   ├── vite.config.ts               # Vite config with API proxy
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── generate_report.py               # Standalone report generation script
├── generate_charts.py               # Chart generation for reports
├── .gitignore
└── README.md                        # ← You are here
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Google Gemini API Key** (optional but recommended) — [Get API Key](https://aistudio.google.com/apikey)

> **Note:** The application works without a Gemini API key, but AI-powered features (smart suggestions, project-based interview questions, semantic answer evaluation) will be disabled and fall back to rule-based logic.

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-username/AAT.git
cd AAT

# Create and activate a Python virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Download the spaCy English language model
python -m spacy download en_core_web_sm
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install Node.js dependencies
npm install
```

### 3. Environment Variables

Create a `.env` file inside the `backend/` directory:

```bash
cp backend/.env.example backend/.env
```

Then edit `backend/.env` with your configuration:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_APP` | Yes | Flask application entry point |
| `FLASK_ENV` | No | Set to `development` for debug mode |
| `SECRET_KEY` | Yes | Flask secret key for session security |
| `GEMINI_API_KEY` | No | Google Gemini API key for AI features |
| `DATABASE_URL` | No | Database URI (defaults to `sqlite:///../instance/app.db`) |

### 4. Running the Application

You need **two terminal windows** — one for the backend and one for the frontend.

**Terminal 1 — Backend (Flask API server):**

```bash
cd backend
python run.py
```

The API server will start at `http://localhost:5000`.

**Terminal 2 — Frontend (Vite dev server):**

```bash
cd frontend
npm run dev
```

The frontend dev server will start at `http://localhost:5173`. API requests are automatically proxied to the Flask backend.

**Open your browser** and navigate to: **http://localhost:5173**

---

## 📖 Usage Guide

### 1. Analyze a Resume

1. Navigate to the **Home** page
2. Upload your resume (PDF or DOCX, max 16MB)
3. Paste the target **Job Description** text
4. Click **"Analyze Resume"**
5. View your comprehensive results dashboard with scores, skill gaps, ATS issues, and AI-powered suggestions

### 2. Track Improvements

1. From the Results page, click **"Improve & Re-Analyze"**
2. Upload your revised resume with the same JD
3. See the **score delta** — what improved, skills gained/lost, and progress tracking

### 3. Compare Analyses

1. Go to the **History** page
2. Select two analyses using checkboxes
3. Click **"Compare Selected"**
4. View side-by-side score comparisons with visual deltas

### 4. Start a Mock Interview

1. From the Results page, click **"Start AI Interview Coach"**
2. Configure your interview: difficulty level, question count, question types, target role
3. Answer questions using text input or **voice dictation** (Chrome/Edge)
4. Receive a comprehensive evaluation with:
   - Per-question score breakdown (TF-IDF + Keywords + AI)
   - Topic performance radar chart
   - Strengths and weaknesses analysis
   - Personalized study roadmap

### 5. Export Results

- Click **"Download PDF"** on any Results page to get a formatted PDF report

---

## 🔌 API Reference

All endpoints are prefixed with `/api`.

### Resume Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Analyze a resume against a job description |
| `POST` | `/api/analyze/improve` | Re-analyze with improvement tracking |

**POST /api/analyze**
```
Content-Type: multipart/form-data

Fields:
  resume: File (PDF/DOCX)
  jd_text: string (Job description text)
```

### History & Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/history` | List all analyses (paginated, sortable, searchable) |
| `GET` | `/api/analysis/:id` | Get full analysis details |
| `DELETE` | `/api/analysis/:id` | Delete a single analysis |
| `DELETE` | `/api/analyses` | Batch delete analyses |
| `PATCH` | `/api/analysis/:id/label` | Update analysis label |

### Comparison & Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/compare` | Compare two analyses side-by-side |
| `GET` | `/api/export/:id` | Download analysis as PDF |

### Interview Coach

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/interview/start` | Start a new mock interview session |
| `POST` | `/api/interview/:id/answer` | Submit answer for current question |
| `POST` | `/api/interview/:id/complete` | Complete session & trigger batch evaluation |
| `GET` | `/api/interview/:id/results` | Fetch evaluation report |
| `GET` | `/api/interview/history` | List all interview sessions |
| `DELETE` | `/api/interview/:id` | Delete an interview session |

**POST /api/interview/start**
```json
{
  "analysis_id": "uuid",
  "difficulty": "easy | medium | hard",
  "question_count": 10,
  "question_types": ["skill", "project", "behavioral", "role"],
  "target_role": "Software Engineer"
}
```

**POST /api/interview/:id/answer**
```json
{
  "answer": "Your answer text here...",
  "time_taken_seconds": 120
}
```

---

## 🧠 NLP & ML Pipeline

The analysis pipeline processes a resume through 8 sequential stages:

```
Resume (PDF/DOCX)
    │
    ▼
┌─────────────────────────────────────┐
│  1. PARSING                         │
│     pdfplumber / python-docx        │
│     → Raw text extraction           │
├─────────────────────────────────────┤
│  2. PREPROCESSING                   │
│     spaCy tokenization              │
│     → Stopword removal              │
│     → Lemmatization                 │
│     → Text normalization            │
├─────────────────────────────────────┤
│  3. SECTION DETECTION               │
│     Regex + heading patterns        │
│     → Identifies: Experience,       │
│       Education, Skills, Projects,  │
│       Summary, Certifications, etc. │
├─────────────────────────────────────┤
│  4. SKILL EXTRACTION                │
│     Taxonomy matching (500+ skills) │
│     + Contextual extraction         │
│     + Gemini deep extraction        │
│     → Found vs Missing skills       │
├─────────────────────────────────────┤
│  5. QUALITY ANALYSIS                │
│     Action verbs, metrics,          │
│     contact info, bullet structure, │
│     word count, readability         │
├─────────────────────────────────────┤
│  6. ATS SCORING                     │
│     10-factor compatibility check   │
│     Spelling, formatting, headings, │
│     keyword density, readability    │
├─────────────────────────────────────┤
│  7. MATCHING ENGINE                 │
│     TF-IDF cosine similarity        │
│     + Hybrid 5-factor scoring       │
│     → Overall match score           │
├─────────────────────────────────────┤
│  8. SUGGESTIONS                     │
│     Rule-based + Gemini AI          │
│     → Actionable improvements       │
└─────────────────────────────────────┘
    │
    ▼
  Analysis Result (JSON) → SQLite DB
```

### Scoring Weights

| Factor | Weight | Method |
|--------|--------|--------|
| TF-IDF Similarity | 25% | scikit-learn TfidfVectorizer + cosine similarity |
| Semantic Match | 20% | Gemini AI semantic comparison |
| Skill Overlap | 30% | Taxonomy matching with skill categorization |
| Section Coverage | 15% | Required/recommended section detection |
| Keyword Density | 10% | Top JD keyword presence in resume |

---

## 🎤 Interview Coach System

The Interview Coach module follows a structured pipeline:

### Question Generation
Questions are sourced from multiple layers with intelligent fallback:

1. **Question Bank** — Static bank organized by skill → difficulty → questions
2. **Gemini AI Generation** — Dynamic questions tailored to specific skills, projects, and roles
3. **Resume Project Extraction** — Gemini analyzes the full resume text to create deep-dive project questions
4. **Static Fallback** — Generic software engineering questions when all else fails

### Answer Evaluation (3-Layer Scoring)

| Layer | Weight | Method |
|-------|--------|--------|
| TF-IDF Cosine | 25% | Compares user answer vs. ideal answer using TF-IDF vectors |
| Keyword Coverage | 25% | Checks presence of expected technical keywords |
| Gemini Semantic | 50% | AI evaluates correctness, completeness, clarity, and depth (0-10 each) |

### Session Flow

```
Setup → Generate Questions → Answer Q1 → Answer Q2 → ... → Answer QN
                                                                │
                                                                ▼
                                                    Batch Evaluation
                                                    ├── TF-IDF scoring
                                                    ├── Keyword analysis
                                                    ├── Gemini semantic eval
                                                    ├── Communication metrics
                                                    └── Study roadmap gen
                                                                │
                                                                ▼
                                                    Evaluation Report
```

---

## 🗄 Database Schema

The application uses SQLite with SQLAlchemy ORM. The database is auto-created at `backend/instance/app.db`.

```
┌──────────────────────────┐       ┌──────────────────────────┐
│        Analysis          │       │    InterviewSession      │
├──────────────────────────┤       ├──────────────────────────┤
│ id (PK, UUID)            │◄──────│ analysis_id (FK)         │
│ resume_filename          │       │ id (PK, UUID)            │
│ resume_text              │       │ target_role              │
│ jd_text                  │       │ difficulty               │
│ overall_score            │       │ status                   │
│ scores_json              │       │ total_questions          │
│ skills_json              │       │ questions_json           │
│ sections_json            │       │ overall_score            │
│ quality_json             │       │ results_json             │
│ ats_json                 │       │ started_at               │
│ suggestions_json         │       │ completed_at             │
│ parent_analysis_id (FK)  │       └──────────┬───────────────┘
│ label                    │                  │ 1:N
│ created_at               │                  │
└──────────────────────────┘       ┌──────────┴───────────────┐
                                   │    InterviewAnswer       │
                                   ├──────────────────────────┤
                                   │ id (PK, UUID)            │
                                   │ session_id (FK)          │
                                   │ question_index           │
                                   │ question_text            │
                                   │ category                 │
                                   │ skill                    │
                                   │ user_answer              │
                                   │ ideal_answer             │
                                   │ score                    │
                                   │ tfidf_score              │
                                   │ keyword_score            │
                                   │ gemini_score             │
                                   │ feedback_json            │
                                   │ time_taken_seconds       │
                                   │ answered_at              │
                                   └──────────────────────────┘
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run the interview module test suite
python -m pytest test_interview.py -v

# Run stress tests (edge cases, unicode, large payloads)
python -m pytest test_brutal_interview.py -v

# Run individual module tests
python test_modules.py
```

### Frontend Build Verification

```bash
cd frontend

# TypeScript type checking + production build
npm run build

# Lint check
npm run lint
```

---

## 📸 Screenshots

> _Screenshots can be added here showing the Home page, Results dashboard, Interview room, and Evaluation report._

---

## 🗺 Roadmap

- [ ] **Enhanced question personalization** — Deeper resume parsing for project-specific interview questions
- [ ] **Interview history page** — View and manage past mock interview sessions
- [ ] **Expanded question bank** — 200+ questions across 20+ technical skills
- [ ] **Skill alias matching** — Fuzzy matching for skill name variants (JS → JavaScript)
- [ ] **Offline project extraction** — Local NLP-based project detection without Gemini dependency
- [ ] **Gemini response caching** — Reduce API calls with intelligent caching
- [ ] **Voice-only interview mode** — Full speech-based interview with TTS question reading
- [ ] **Multi-language support** — Resume analysis in languages beyond English
- [ ] **Authentication & user accounts** — Persistent user profiles with interview history
- [ ] **Real-time difficulty adaptation** — Dynamic difficulty adjustment based on answer quality

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please ensure:
- Backend code follows PEP 8 style
- Frontend code passes TypeScript type checking (`tsc -b`)
- All existing tests continue to pass
- New features include appropriate tests

---

## 📄 License

This project is developed as an academic / portfolio project. Feel free to use, modify, and distribute.

---

<p align="center">
  Built with ❤️ using Python, React, and Gemini AI
</p>
