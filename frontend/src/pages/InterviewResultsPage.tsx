import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, CheckCircle2, AlertTriangle, ChevronDown, 
  ArrowLeft, Bookmark, Sparkles, BookOpen, 
  Smile, User, BarChart2, Star, ThumbsUp, AlertCircle
} from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { getInterviewResults } from '../services/api';
import type { InterviewResultsResponse, EvaluatedQuestion } from '../types';
import { ScoreGauge } from '../components/ui/ScoreGauge';

export default function InterviewResultsPage() {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  // Loading and results state
  const [results, setResults] = useState<InterviewResultsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(0); // expand first by default

  useEffect(() => {
    // If state contains results directly, load immediately
    if (location.state?.results) {
      setResults(location.state.results);
      setLoading(false);
    } else if (sessionId) {
      loadSessionResults(sessionId);
    }
  }, [sessionId, location.state]);

  const loadSessionResults = async (id: string) => {
    setLoading(true);
    try {
      const data = await getInterviewResults(id);
      setResults(data);
    } catch (err: any) {
      console.error("Failed to load results:", err);
      setError("Failed to retrieve interview evaluations. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleExpand = (idx: number) => {
    setExpandedQuestion(prev => (prev === idx ? null : idx));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand mb-4" />
        <p className="text-slate-400 text-sm">Synchronizing scorecards and reports...</p>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="max-w-md mx-auto text-center py-20 space-y-4">
        <AlertTriangle className="w-12 h-12 text-warning mx-auto" />
        <h2 className="text-xl font-bold text-white">Results Unavailable</h2>
        <p className="text-slate-400 text-sm">{error || "Could not retrieve mock interview data."}</p>
        <button 
          onClick={() => navigate('/')} 
          className="px-6 py-2 bg-brand hover:bg-brandLight text-white rounded-xl text-sm font-semibold transition-colors"
        >
          Return to Analyzer
        </button>
      </div>
    );
  }

  // Prep Radar Chart data
  const radarData = Object.entries(results.topic_scores).map(([name, score]) => ({
    subject: name,
    A: score,
    fullMark: 10
  }));

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-6xl mx-auto w-full space-y-8"
    >
      
      {/* Header Panel */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 bg-surface/50 p-6 md:p-8 rounded-3xl border border-white/5 backdrop-blur-xl">
        <div>
          <span className="text-xs font-semibold text-brandLight uppercase tracking-wider bg-brand/10 border border-brand/20 px-3 py-1 rounded-full">
            Interview Evaluation Completed
          </span>
          <h1 className="text-3xl font-bold text-white mt-3 mb-2 flex items-center gap-3">
            Mock Interview Report
          </h1>
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Shield className="w-4 h-4 text-slate-500" />
            Session Reference: {sessionId?.slice(0, 8)}...
          </div>
        </div>

        <div className="flex gap-3">
          <button 
            onClick={() => navigate(-1)} 
            className="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 transition-colors font-medium text-sm flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Start New Simulation
          </button>
        </div>
      </div>

      {/* Overview Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Score Card */}
        <motion.div variants={itemVariants} className="lg:col-span-4 bg-surface/50 border border-white/5 rounded-3xl p-8 flex flex-col items-center justify-center backdrop-blur-xl">
          <ScoreGauge score={results.overall_percentage} label="Final Panel Score" size={200} strokeWidth={16} />
          
          <div className="text-center mt-6">
            <span className={`text-sm font-bold uppercase tracking-wider px-3 py-1 rounded-full ${
              results.overall_percentage >= 75 
                ? 'bg-success/10 text-success' 
                : results.overall_percentage >= 50 
                ? 'bg-warning/10 text-warning' 
                : 'bg-danger/10 text-danger'
            }`}>
              {results.overall_percentage >= 75 ? 'Good Performance' : results.overall_percentage >= 50 ? 'Average performance' : 'Requires Preparation'}
            </span>
          </div>
        </motion.div>

        {/* Topic Breakdown Radar */}
        <motion.div variants={itemVariants} className="lg:col-span-4 bg-surface/50 border border-white/5 rounded-3xl p-6 flex flex-col justify-between backdrop-blur-xl h-[340px]">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <BarChart2 className="w-4 h-4" />
              Topic Performance
            </span>
          </div>
          
          <div className="flex-1 w-full flex items-center justify-center">
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.05)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: '#475569', fontSize: 9 }} />
                  <Radar name="Candidate Score" dataKey="A" stroke="#6366f1" fill="#6366f1" fillOpacity={0.15} />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <span className="text-sm text-slate-500">No topic data available</span>
            )}
          </div>
        </motion.div>

        {/* Communication Metrics */}
        <motion.div variants={itemVariants} className="lg:col-span-4 bg-surface/50 border border-white/5 rounded-3xl p-6 flex flex-col justify-between backdrop-blur-xl h-[340px]">
          <div>
            <span className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 mb-6">
              <Smile className="w-4 h-4" />
              Communication Heuristics
            </span>

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Fluency Quality Score</span>
                <span className="text-sm font-bold text-white">
                  {results.communication_summary.avg_communication_score}/10
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Average Word Count</span>
                <span className="text-sm font-bold text-white">
                  {results.communication_summary.avg_word_count} words
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Total Filler Words</span>
                <span className="text-sm font-bold text-white">
                  {results.communication_summary.total_filler_words} hits
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Filler Rate</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                  results.communication_summary.filler_rate_per_hundred > 3 
                    ? 'bg-warning/10 text-warning' 
                    : 'bg-success/10 text-success'
                }`}>
                  {results.communication_summary.filler_rate_per_hundred}% of speech
                </span>
              </div>
            </div>
          </div>

          <div className="text-xs text-slate-500 pt-4 border-t border-white/5">
            Assesses verbal pacing, articulation depth, and use of conversational crutch words.
          </div>
        </motion.div>

      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Key Strengths */}
        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8 backdrop-blur-xl">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-6 text-white">
            <ThumbsUp className="w-6 h-6 text-success" />
            Demonstrated Strengths
          </h2>
          
          <div className="space-y-3">
            {results.strengths.length > 0 ? (
              results.strengths.map((str, i) => (
                <div key={i} className="flex gap-3 bg-success/5 p-4 rounded-xl border border-success/10">
                  <CheckCircle2 className="w-5 h-5 text-success shrink-0" />
                  <div>
                    <div className="text-sm font-bold text-white">{str}</div>
                    <div className="text-xs text-slate-400 mt-0.5">Demonstrated high factual and technical articulation.</div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-sm">Complete more highly-scored questions to register strengths.</p>
            )}
          </div>
        </motion.div>

        {/* Development Opportunities */}
        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8 backdrop-blur-xl">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-6 text-white">
            <AlertCircle className="w-6 h-6 text-warning" />
            Improvement Gaps
          </h2>
          
          <div className="space-y-3">
            {results.weaknesses.length > 0 ? (
              results.weaknesses.map((weak, i) => (
                <div key={i} className="flex gap-3 bg-warning/5 p-4 rounded-xl border border-warning/10">
                  <AlertTriangle className="w-5 h-5 text-warning shrink-0" />
                  <div>
                    <div className="text-sm font-bold text-white">{weak}</div>
                    <div className="text-xs text-slate-400 mt-0.5">Missed key reference concepts or had low structural completeness.</div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-success text-sm font-medium">Outstanding! No major knowledge gaps identified.</p>
            )}
          </div>
        </motion.div>

      </div>

      {/* Study & Improvement Roadmap */}
      {results.roadmap && results.roadmap.length > 0 && (
        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8 backdrop-blur-xl">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-6 text-white">
            <Sparkles className="w-6 h-6 text-brand" />
            Personalized Study Roadmap
          </h2>

          <div className="space-y-6">
            {results.roadmap.map((item, idx) => (
              <div key={idx} className="bg-black/20 rounded-2xl border border-white/5 p-5 flex flex-col md:flex-row gap-6">
                
                {/* Topic Indicator */}
                <div className="md:w-1/4 shrink-0 flex flex-col justify-between">
                  <div>
                    <div className="text-sm font-bold text-white">{item.skill}</div>
                    <div className="text-xs text-slate-500 mt-1 capitalize">
                      Assessment: <span className="text-warning font-semibold">{item.current_level}</span>
                    </div>
                  </div>
                  <div className="mt-4 md:mt-0 flex items-center gap-1.5 text-xs text-slate-400 bg-white/5 px-2.5 py-1 rounded w-fit border border-white/5">
                    <BookOpen className="w-3.5 h-3.5" /> Study Focus
                  </div>
                </div>

                {/* Recommendations and Resources */}
                <div className="flex-1 space-y-4">
                  <div>
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Practice & Study Recommendations</div>
                    <ul className="list-disc pl-4 space-y-1.5">
                      {item.recommendations.map((rec, rIdx) => (
                        <li key={rIdx} className="text-sm text-slate-300 leading-relaxed">{rec}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="pt-2 border-t border-white/5">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Recommended Platforms & Guides</div>
                    <div className="flex flex-wrap gap-2">
                      {item.resources.map((res, sIdx) => (
                        <span key={sIdx} className="text-xs font-medium text-brandLight bg-brand/10 border border-brand/20 px-2.5 py-1 rounded">
                          {res}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Collapsible Question-by-Question Grading */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
          <Bookmark className="w-6 h-6 text-slate-400" />
          Question-by-Question Breakdown
        </h2>

        {results.questions.map((q: EvaluatedQuestion, idx: number) => {
          const isOpen = expandedQuestion === idx;
          return (
            <div key={idx} className="bg-surface/40 border border-white/5 rounded-3xl overflow-hidden backdrop-blur-xl transition-all">
              
              {/* Question summary toggler */}
              <button
                onClick={() => handleToggleExpand(idx)}
                className="w-full flex items-center justify-between p-6 hover:bg-white/5 transition-colors text-left"
              >
                <div className="flex items-center gap-4 flex-1 pr-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    q.score >= 7.5 
                      ? 'bg-success/15 text-success' 
                      : q.score >= 5.0 
                      ? 'bg-warning/15 text-warning' 
                      : 'bg-danger/15 text-danger'
                  }`}>
                    {q.question_index}
                  </div>

                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-white truncate">{q.question_text}</h3>
                    <div className="flex items-center gap-2.5 mt-1">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider bg-white/5 px-2 py-0.5 rounded">
                        {q.category}
                      </span>
                      <span className="text-[10px] text-slate-500 font-bold uppercase">
                        Score: {q.score.toFixed(1)}/10
                      </span>
                    </div>
                  </div>
                </div>

                <motion.div animate={{ rotate: isOpen ? 180 : 0 }} className="shrink-0 text-slate-400">
                  <ChevronDown className="w-5 h-5" />
                </motion.div>
              </button>

              {/* Collapsed Grading Details */}
              <AnimatePresence>
                {isOpen && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="border-t border-white/5 px-6 pb-6"
                  >
                    
                    {/* Detailed Multi-Score breakdown */}
                    <div className="grid grid-cols-3 gap-3 my-6">
                      <div className="bg-black/20 p-3.5 rounded-xl border border-white/5 text-center">
                        <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide mb-1">
                          Cosine (25%)
                        </div>
                        <div className="text-lg font-bold text-white">{q.tfidf_score.toFixed(1)}</div>
                      </div>
                      <div className="bg-black/20 p-3.5 rounded-xl border border-white/5 text-center">
                        <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide mb-1">
                          Keywords (25%)
                        </div>
                        <div className="text-lg font-bold text-white">{q.keyword_score.toFixed(1)}</div>
                      </div>
                      <div className="bg-black/20 p-3.5 rounded-xl border border-white/5 text-center">
                        <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide mb-1">
                          AI Semantic (50%)
                        </div>
                        <div className="text-lg font-bold text-white">{q.gemini_score.toFixed(1)}</div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      
                      {/* User's Answer */}
                      <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 mb-1.5">
                          <User className="w-3.5 h-3.5" /> Candidate Response
                        </span>
                        <p className="text-sm text-slate-300 leading-relaxed italic bg-black/10 p-4 rounded-xl border border-white/5">
                          "{q.user_answer || 'Unanswered.'}"
                        </p>
                      </div>

                      {/* Strengths & Weaknesses */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-success/5 p-4 rounded-xl border border-success/10 space-y-2">
                          <span className="text-[10px] font-bold text-success uppercase tracking-wider flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> What you got right
                          </span>
                          <ul className="list-disc pl-4 space-y-1 text-xs text-slate-300 leading-relaxed">
                            {q.feedback.strengths.map((str, sIdx) => <li key={sIdx}>{str}</li>)}
                            {q.feedback.strengths.length === 0 && <li>Included relevant technical vocabulary.</li>}
                          </ul>
                        </div>

                        <div className="bg-warning/5 p-4 rounded-xl border border-warning/10 space-y-2">
                          <span className="text-[10px] font-bold text-warning uppercase tracking-wider flex items-center gap-1">
                            <AlertTriangle className="w-3.5 h-3.5" /> Missed details
                          </span>
                          <ul className="list-disc pl-4 space-y-1 text-xs text-slate-300 leading-relaxed">
                            {q.feedback.weaknesses.map((weak, wIdx) => <li key={wIdx}>{weak}</li>)}
                            {q.feedback.weaknesses.length === 0 && <li>Answer was complete and structured.</li>}
                          </ul>
                        </div>
                      </div>

                      {/* Actionable Rewrite/Improvement Tip */}
                      <div className="bg-brand/5 p-4 rounded-xl border border-brand/15 flex gap-3">
                        <Star className="w-5 h-5 text-brand shrink-0 pt-0.5" />
                        <div>
                          <span className="text-[10px] font-bold text-brandLight uppercase tracking-wider">
                            Actionable Improvement Tip
                          </span>
                          <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                            {q.feedback.improvement_tip}
                          </p>
                        </div>
                      </div>

                      {/* Collapsible Ideal Answer Summary */}
                      <CollapsibleIdealAnswer text={q.ideal_answer} />

                    </div>

                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </motion.div>

    </motion.div>
  );
}

// Collapsible helper for Ideal answers
function CollapsibleIdealAnswer({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="border border-white/5 rounded-xl overflow-hidden mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-3.5 bg-black/15 hover:bg-black/25 text-left text-xs font-semibold text-slate-400 transition-colors"
      >
        <span className="flex items-center gap-1.5">
          <BookOpen className="w-4 h-4 text-slate-500" /> Reference Ideal Answer Summary
        </span>
        <motion.div animate={{ rotate: expanded ? 180 : 0 }} className="text-slate-500">
          <ChevronDown className="w-4 h-4" />
        </motion.div>
      </button>
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 bg-black/35 text-xs text-slate-300 leading-relaxed border-t border-white/5"
          >
            {text}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
