export interface SkillItem {
  name: string;
  category: string;
  type: 'hard' | 'soft';
  importance?: 'critical' | 'important' | 'nice-to-have';
  source?: 'explicit' | 'inferred' | 'coursework' | 'project' | 'experience' | 'certification';
}

export interface AnalysisScores {
  overall: number;
  tfidf_similarity: number;
  skill_match: number;
  section_coverage: number;
  keyword_density: number;
  quality: number;
  ats_compatibility: number;
}

export interface AnalysisSkills {
  found: SkillItem[];
  missing: SkillItem[];
  match_percentage: number;
}

export interface SectionsData {
  detected: string[];
  missing_required: string[];
  missing_recommended: string[];
  coverage_score: number;
}

export interface QualityIssue {
  type: 'warning' | 'info';
  message: string;
}

export interface QualityData {
  score: number;
  word_count: number;
  length_status: string;
  action_verb_percentage: number;
  strong_verb_count: number;
  weak_verb_count: number;
  has_metrics: boolean;
  metrics_count: number;
  contact_info: {
    email: boolean;
    phone: boolean;
    linkedin: boolean;
    github: boolean;
  };
  issues: QualityIssue[];
}

export interface SuggestionItem {
  category: string;
  priority: 'high' | 'medium' | 'low';
  suggestion: string;
  source?: 'ai' | 'rule';
  example?: string;
}

export interface SuggestionsData {
  rule_based: SuggestionItem[];
  ai_generated?: SuggestionItem[];
}

export interface ATSIssue {
  severity: 'high' | 'medium' | 'low';
  category: string;
  message: string;
  fix_suggestion: string;
}

export interface ATSData {
  score: number;
  issues: ATSIssue[];
}

export interface AnalysisResponse {
  analysis_id: string;
  timestamp: string;
  resume_filename: string;
  scores: AnalysisScores;
  skills: AnalysisSkills;
  sections: SectionsData;
  quality: QualityData;
  ats: ATSData;
  suggestions: SuggestionsData;
  error?: string;
  parent_analysis_id?: string | null;
  label?: string | null;
  delta?: ScoreDelta;
}

export interface HistoryItem {
  id: string;
  resume_filename: string;
  overall_score: number;
  scores: AnalysisScores;
  created_at: string;
  parent_analysis_id: string | null;
  label: string | null;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  pages: number;
}

export interface ScoreDelta {
  overall: number;
  skill_match: number;
  ats_compatibility: number;
  quality: number;
  skills_gained?: string[];
  skills_lost?: string[];
  improved: boolean;
}

export interface CompareResponse {
  analyses: AnalysisResponse[];
  comparison: {
    score_deltas: ScoreDelta;
    skills_gained: string[];
    skills_lost: string[];
    improved: boolean;
  };
}

export interface InterviewQuestion {
  index: number;
  question: string;
  category: string;
  skill?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  time_limit_seconds?: number;
}

export interface InterviewProgress {
  answered: number;
  total: number;
  percentage: number;
}

export interface StartInterviewResponse {
  session_id: string;
  total_questions: number;
  first_question: InterviewQuestion | null;
}

export interface SubmitAnswerResponse {
  received: boolean;
  next_question: InterviewQuestion | null;
  progress: InterviewProgress;
  is_last: boolean;
}

export interface AnswerFeedback {
  verdict: string;
  strengths: string[];
  weaknesses: string[];
  improvement_tip: string;
  keywords_found: string[];
}

export interface EvaluatedQuestion {
  id: string;
  session_id: string;
  question_index: number;
  question_text: string;
  category: string;
  skill: string | null;
  user_answer: string;
  ideal_answer: string;
  score: number;
  tfidf_score: number;
  keyword_score: number;
  gemini_score: number;
  feedback: AnswerFeedback;
  time_taken_seconds: number | null;
  answered_at: string;
}

export interface CommunicationSummary {
  avg_word_count: number;
  total_filler_words: number;
  avg_communication_score: number;
  filler_rate_per_hundred: number;
}

export interface RoadmapItem {
  skill: string;
  current_level: string;
  recommendations: string[];
  resources: string[];
}

export interface InterviewResultsResponse {
  session_id: string;
  overall_score: number;
  overall_percentage: number;
  topic_scores: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  moderate: string[];
  communication_summary: CommunicationSummary;
  roadmap: RoadmapItem[];
  questions: EvaluatedQuestion[];
  status?: string;
}

export interface InterviewHistoryItem {
  id: string;
  analysis_id: string;
  target_role: string;
  difficulty: string;
  status: string;
  total_questions: number;
  overall_score: number | null;
  started_at: string;
  completed_at: string | null;
}

export interface InterviewHistoryResponse {
  items: InterviewHistoryItem[];
  total: number;
}
