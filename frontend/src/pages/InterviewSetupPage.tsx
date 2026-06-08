import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, BrainCircuit, Shield, Terminal, MessageSquare, 
  HelpCircle, Settings, Play, Sparkles
} from 'lucide-react';
import { startInterview, getAnalysis } from '../services/api';
import type { AnalysisResponse } from '../types';

export default function InterviewSetupPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // States
  const [analysisId, setAnalysisId] = useState<string>('');
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [questionCount, setQuestionCount] = useState<number>(10);
  const [targetRole, setTargetRole] = useState<string>('Software Engineer');
  const [questionTypes, setQuestionTypes] = useState({
    skill: true,
    project: true,
    behavioral: true,
    role: true
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [fetchingAnalysis, setFetchingAnalysis] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Attempt to grab analysis_id from location state or search params
    const stateId = location.state?.analysis_id;
    const searchParams = new URLSearchParams(location.search);
    const queryId = searchParams.get('analysis_id');
    const id = stateId || queryId;

    if (id) {
      setAnalysisId(id);
      loadAnalysisDetails(id);
    } else {
      setError("Please select a resume analysis record to start an interview.");
    }
  }, [location]);

  const loadAnalysisDetails = async (id: string) => {
    setFetchingAnalysis(true);
    try {
      const data = await getAnalysis(id);
      setAnalysisData(data);
      // Pre-fill target role if available or inferred
      if (data.resume_filename) {
        // Fallback guess based on filename
        const filename = data.resume_filename.toLowerCase();
        if (filename.includes('data') || filename.includes('analyst')) {
          setTargetRole('Data Scientist');
        } else if (filename.includes('cyber') || filename.includes('security')) {
          setTargetRole('Cybersecurity Engineer');
        } else {
          setTargetRole('Software Engineer');
        }
      }
    } catch (err) {
      console.error("Error fetching analysis details:", err);
    } finally {
      setFetchingAnalysis(false);
    }
  };

  const handleToggleType = (type: keyof typeof questionTypes) => {
    setQuestionTypes(prev => {
      const updated = { ...prev, [type]: !prev[type] };
      // Ensure at least one type is checked
      const anyChecked = Object.values(updated).some(val => val === true);
      return anyChecked ? updated : prev;
    });
  };

  const handleStart = async () => {
    if (!analysisId) return;
    
    setLoading(true);
    setError(null);

    const activeTypes = Object.entries(questionTypes)
      .filter(([_, enabled]) => enabled)
      .map(([name]) => name);

    try {
      const res = await startInterview(
        analysisId,
        difficulty,
        questionCount,
        activeTypes,
        targetRole
      );
      
      // Navigate to the interview room
      navigate(`/interview/${res.session_id}`, {
        state: { 
          session: res,
          difficulty,
          targetRole,
          totalQuestions: questionCount
        }
      });
    } catch (err: any) {
      console.error("Failed to start interview session:", err);
      setError(err.response?.data?.error || "Failed to generate interview. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] as const }
    }
  };

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-3xl mx-auto w-full"
    >
      {/* Back Button */}
      <button 
        onClick={() => analysisId ? navigate(`/analysis/${analysisId}`) : navigate('/')}
        className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6 text-sm group"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        Back to Resume Analysis
      </button>

      <div className="bg-surface/50 border border-white/5 rounded-3xl p-8 backdrop-blur-xl relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand/5 rounded-full blur-3xl pointer-events-none" />
        
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-14 h-14 rounded-2xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
            <BrainCircuit className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              Setup AI Interview Coach
              <Sparkles className="w-5 h-5 text-brandLight animate-pulse" />
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Simulate a real-time technical & behavioral hiring panel custom-fit for your resume.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm">
            {error}
          </div>
        )}

        {/* Selected Resume Details Card */}
        {analysisData && (
          <div className="mb-8 p-5 bg-black/20 rounded-2xl border border-white/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Target Resume</div>
              <div className="text-sm font-semibold text-slate-200">{analysisData.resume_filename}</div>
              <div className="text-xs text-slate-400 mt-0.5">
                Skills extracted: {analysisData.skills.found.slice(0, 5).map(s => s.name).join(', ')}...
              </div>
            </div>
            <div className="shrink-0 flex items-center gap-2 bg-brand/10 text-brand px-3.5 py-1.5 rounded-full text-xs font-semibold border border-brand/20">
              <Shield className="w-3.5 h-3.5" />
              Resume Synchronized
            </div>
          </div>
        )}

        {fetchingAnalysis && (
          <div className="flex justify-center py-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand" />
          </div>
        )}

        {!fetchingAnalysis && (
          <div className="space-y-6">
            
            {/* Target Role */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wide">
                Target Job Role
              </label>
              <input 
                type="text" 
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. Frontend Engineer, Data Scientist, ML Engineer"
                className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-brand/50 transition-colors placeholder:text-slate-600"
              />
              <span className="text-xs text-slate-500 mt-1.5 block">
                We'll tailor situational & design questions specifically for this target title.
              </span>
            </div>

            {/* Difficulty Selector */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2.5 uppercase tracking-wide">
                Difficulty Level
              </label>
              <div className="grid grid-cols-3 gap-3">
                {(['easy', 'medium', 'hard'] as const).map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setDifficulty(level)}
                    className={`py-3.5 rounded-xl border font-semibold text-sm capitalize transition-all ${
                      difficulty === level 
                        ? 'bg-brand/10 border-brand text-brandLight shadow-lg shadow-brand/10' 
                        : 'bg-black/10 border-white/5 text-slate-400 hover:bg-black/35 hover:text-white'
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* Question Count Selector */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2.5 uppercase tracking-wide">
                Total Interview Questions
              </label>
              <div className="grid grid-cols-4 gap-3">
                {[5, 10, 15, 20].map((count) => (
                  <button
                    key={count}
                    type="button"
                    onClick={() => setQuestionCount(count)}
                    className={`py-3 rounded-xl border font-semibold text-sm transition-all ${
                      questionCount === count 
                        ? 'bg-brand/10 border-brand text-brandLight shadow-lg shadow-brand/10' 
                        : 'bg-black/10 border-white/5 text-slate-400 hover:bg-black/35 hover:text-white'
                    }`}
                  >
                    {count}
                  </button>
                ))}
              </div>
            </div>

            {/* Question Types Toggle */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wide">
                Interview Modules
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                <button
                  type="button"
                  onClick={() => handleToggleType('skill')}
                  className={`flex items-center gap-3 p-4 rounded-xl border text-left transition-all ${
                    questionTypes.skill 
                      ? 'bg-brand/10 border-brand/50 text-white' 
                      : 'bg-black/15 border-white/5 text-slate-400 hover:bg-black/30'
                  }`}
                >
                  <Terminal className={`w-5 h-5 shrink-0 ${questionTypes.skill ? 'text-brand' : 'text-slate-500'}`} />
                  <div>
                    <div className="text-sm font-semibold">Technical & Skills</div>
                    <div className="text-xs text-slate-500 mt-0.5">Core coding and system concepts found in your resume.</div>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => handleToggleType('project')}
                  className={`flex items-center gap-3 p-4 rounded-xl border text-left transition-all ${
                    questionTypes.project 
                      ? 'bg-brand/10 border-brand/50 text-white' 
                      : 'bg-black/15 border-white/5 text-slate-400 hover:bg-black/30'
                  }`}
                >
                  <Settings className={`w-5 h-5 shrink-0 ${questionTypes.project ? 'text-brand' : 'text-slate-500'}`} />
                  <div>
                    <div className="text-sm font-semibold">Project Deep-Dive</div>
                    <div className="text-xs text-slate-500 mt-0.5">Dynamic architectural evaluation of projects on your resume.</div>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => handleToggleType('behavioral')}
                  className={`flex items-center gap-3 p-4 rounded-xl border text-left transition-all ${
                    questionTypes.behavioral 
                      ? 'bg-brand/10 border-brand/50 text-white' 
                      : 'bg-black/15 border-white/5 text-slate-400 hover:bg-black/30'
                  }`}
                >
                  <MessageSquare className={`w-5 h-5 shrink-0 ${questionTypes.behavioral ? 'text-brand' : 'text-slate-500'}`} />
                  <div>
                    <div className="text-sm font-semibold">Behavioral & Soft Skills</div>
                    <div className="text-xs text-slate-500 mt-0.5">STAR-framework based workplace scenario questions.</div>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => handleToggleType('role')}
                  className={`flex items-center gap-3 p-4 rounded-xl border text-left transition-all ${
                    questionTypes.role 
                      ? 'bg-brand/10 border-brand/50 text-white' 
                      : 'bg-black/15 border-white/5 text-slate-400 hover:bg-black/30'
                  }`}
                >
                  <HelpCircle className={`w-5 h-5 shrink-0 ${questionTypes.role ? 'text-brand' : 'text-slate-500'}`} />
                  <div>
                    <div className="text-sm font-semibold">Situational Design</div>
                    <div className="text-xs text-slate-500 mt-0.5">Hypothetical architectural trade-offs specific to the target role.</div>
                  </div>
                </button>

              </div>
            </div>

            {/* Launch Button */}
            <div className="pt-4">
              <button
                type="button"
                disabled={loading}
                onClick={handleStart}
                className="w-full bg-brand hover:bg-brandLight text-white font-bold py-4 rounded-xl flex items-center justify-center gap-3 shadow-lg shadow-brand/20 hover:shadow-brand/35 transition-all text-base disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                    Assembling Panel & Generating Questions...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 fill-current" />
                    Enter Simulation Room
                  </>
                )}
              </button>
            </div>

          </div>
        )}

      </div>
    </motion.div>
  );
}
