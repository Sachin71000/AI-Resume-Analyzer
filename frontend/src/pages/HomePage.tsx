import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { analyzeResume } from '../services/api';
import { SplitText } from '../components/reactbits/SplitText';
import { JDPreview } from '../components/ui/JDPreview';
import {
  Upload, FileText, File, Loader2, Sparkles, AlertCircle,
  ArrowUpRight, CheckCircle2, BrainCircuit, X, Target, Brain, BarChart2, TrendingUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const FEATURES = [
  { icon: <Target className="w-3 h-3" />, label: 'ATS Score' },
  { icon: <Brain className="w-3 h-3" />, label: 'AI Insights' },
  { icon: <BarChart2 className="w-3 h-3" />, label: 'Skill Gap Analysis' },
  { icon: <TrendingUp className="w-3 h-3" />, label: 'Improvement Plan' },
];

export default function HomePage() {
  const location = useLocation();
  const [file, setFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();

  const parentId = location.state?.parent_id;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      const ext = droppedFile.name.split('.').pop()?.toLowerCase();
      if (ext === 'pdf' || ext === 'doc' || ext === 'docx') {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Please upload a PDF or DOCX file.');
      }
    }
  };

  const handleAnalyze = async () => {
    if (!file || !jdText.trim()) {
      setError('Please provide both a resume file and a job description.');
      return;
    }

    setLoading(true);
    setError(null);
    setLoadingStep(0);

    const t1 = setTimeout(() => setLoadingStep(1), 800);
    const t2 = setTimeout(() => setLoadingStep(2), 2000);
    const t3 = setTimeout(() => setLoadingStep(3), 3500);
    const clear = () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };

    try {
      if (parentId) {
        const api = await import('../services/api');
        const res = await api.improveResume(file, jdText, parentId);
        clear();
        navigate(`/analysis/${res.analysis_id}`, { state: { results: res } });
        return;
      }
      const results = await analyzeResume(file, jdText);
      clear();
      navigate('/results', { state: { results } });
    } catch (err: any) {
      clear();
      setError(err.response?.data?.error || 'An error occurred during analysis. Is the backend running?');
      setLoading(false);
    }
  };

  // ── Loading state ─────────────────────────────────────────────────────────
  if (loading) {
    const steps = [
      'Parsing document structure...',
      'Extracting skills & context...',
      'Computing match scores...',
      'Generating AI insights...',
    ];
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh]">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="relative w-full max-w-sm p-8 rounded-3xl overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.95) 100%)',
            border: '1px solid rgba(99,102,241,0.2)',
            boxShadow: '0 0 60px rgba(99,102,241,0.2), 0 24px 64px rgba(0,0,0,0.5)',
          }}
        >
          {/* Progress bar */}
          <div className="absolute top-0 left-0 w-full h-0.5 bg-white/5">
            <motion.div
              className="h-full"
              initial={{ width: '0%' }}
              animate={{ width: `${((loadingStep + 1) / steps.length) * 100}%` }}
              transition={{ duration: 0.6 }}
              style={{ background: 'linear-gradient(90deg, #6366f1, #8b5cf6)' }}
            />
          </div>

          {/* Animated icon */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              <div
                className="w-20 h-20 rounded-2xl flex items-center justify-center"
                style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 0 40px rgba(99,102,241,0.4)' }}
              >
                <BrainCircuit className="w-10 h-10 text-white animate-pulse" />
              </div>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
                className="absolute -inset-2 rounded-3xl"
                style={{ border: '2px dashed rgba(99,102,241,0.4)' }}
              />
            </div>
          </div>

          <h3 className="text-xl font-bold text-white text-center mb-2">Analyzing Profile</h3>
          <p className="text-sm text-slate-500 text-center mb-8">Our AI is reviewing your resume...</p>

          <div className="space-y-3">
            {steps.map((step, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 transition-all duration-500 ${
                  idx < loadingStep
                    ? 'bg-success/20 text-success'
                    : idx === loadingStep
                    ? 'bg-brand/20 text-brand'
                    : 'bg-white/5 border border-white/10'
                }`}>
                  {idx < loadingStep
                    ? <CheckCircle2 className="w-3.5 h-3.5" />
                    : idx === loadingStep
                    ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    : null
                  }
                </div>
                <span className={`text-sm font-medium transition-colors duration-300 ${
                  idx <= loadingStep ? 'text-white' : 'text-slate-600'
                }`}>
                  {step}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    );
  }

  // ── Main form ─────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col items-center max-w-4xl mx-auto w-full">

      {/* Hero section */}
      <div className="text-center mb-12 mt-6 space-y-6">
        {/* Eyebrow badge */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-center"
        >
          {parentId ? (
            <span
              className="inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-full"
              style={{
                background: 'linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.15) 100%)',
                border: '1px solid rgba(99,102,241,0.25)',
                color: '#818cf8',
              }}
            >
              <ArrowUpRight className="w-4 h-4" />
              Improvement Mode — track your score changes
              <button
                onClick={() => navigate('/', { replace: true })}
                className="ml-1 p-0.5 rounded hover:bg-white/10 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          ) : (
            <span
              className="inline-flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-full uppercase tracking-widest"
              style={{
                background: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(139,92,246,0.12) 100%)',
                border: '1px solid rgba(99,102,241,0.2)',
                color: '#818cf8',
              }}
            >
              <Sparkles className="w-3 h-3" />
              AI-Powered Career Intelligence
            </span>
          )}
        </motion.div>

        {/* Title */}
        <SplitText
          text="Analyze Your Resume"
          className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.05]"
          delay={0.04}
        />

        {/* Subtitle */}
        {!parentId && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="text-lg text-slate-400 max-w-xl mx-auto leading-relaxed"
          >
            Get a comprehensive match analysis, ATS score, skill gap report, and actionable AI feedback in seconds.
          </motion.p>
        )}

        {/* Feature pills */}
        {!parentId && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="flex flex-wrap items-center justify-center gap-2"
          >
            {FEATURES.map((f, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full text-slate-400"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
              >
                {f.icon} {f.label}
              </span>
            ))}
          </motion.div>
        )}
      </div>

      {/* Main card */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full"
        style={{
          background: 'linear-gradient(135deg, rgba(15,23,42,0.8) 0%, rgba(30,41,59,0.8) 100%)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '24px',
          boxShadow: '0 24px 64px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06)',
          backdropFilter: 'blur(24px)',
        }}
      >
        <div className="p-6 md:p-8 space-y-8">

          {/* Error */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-start gap-3 p-4 rounded-xl"
                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)' }}
              >
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <p className="text-sm font-medium text-red-400">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Step 1 — Upload */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span
                className="w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center text-white"
                style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
              >
                1
              </span>
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
                <File className="w-4 h-4 text-brandLight" />
                Upload Resume
              </div>
            </div>

            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input')?.click()}
              className="relative cursor-pointer group rounded-2xl min-h-[160px] flex flex-col items-center justify-center p-8 transition-all duration-300"
              style={{
                border: `2px dashed ${dragActive ? '#6366f1' : file ? 'rgba(16,185,129,0.5)' : 'rgba(255,255,255,0.1)'}`,
                background: dragActive
                  ? 'rgba(99,102,241,0.06)'
                  : file
                  ? 'rgba(16,185,129,0.04)'
                  : 'rgba(255,255,255,0.02)',
                boxShadow: dragActive ? '0 0 0 4px rgba(99,102,241,0.15)' : 'none',
              }}
            >
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx"
                id="file-input"
                className="hidden"
              />

              {file ? (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="flex flex-col items-center text-center"
                >
                  <div
                    className="w-14 h-14 rounded-full flex items-center justify-center mb-4"
                    style={{ background: 'rgba(16,185,129,0.15)', boxShadow: '0 0 20px rgba(16,185,129,0.2)' }}
                  >
                    <CheckCircle2 className="w-7 h-7 text-emerald-400" />
                  </div>
                  <p className="font-bold text-white text-lg">{file.name}</p>
                  <p className="text-sm text-slate-400 mt-1">
                    {(file.size / 1024 / 1024).toFixed(2)} MB &bull; Click to replace
                  </p>
                </motion.div>
              ) : (
                <div className="flex flex-col items-center text-center">
                  <div
                    className="w-14 h-14 rounded-full flex items-center justify-center mb-4 transition-all duration-300"
                    style={{
                      background: dragActive ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.05)',
                      boxShadow: dragActive ? '0 0 20px rgba(99,102,241,0.4)' : 'none',
                    }}
                  >
                    <Upload className={`w-6 h-6 transition-colors ${dragActive ? 'text-white' : 'text-slate-400 group-hover:text-brand'}`} />
                  </div>
                  <p className="font-semibold text-slate-200 text-base mb-1">
                    {dragActive ? 'Drop it here!' : 'Drag & drop your resume'}
                  </p>
                  <p className="text-sm text-slate-500">PDF, DOC, DOCX &bull; up to 16 MB</p>
                </div>
              )}
            </div>
          </div>

          {/* Step 2 — JD */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span
                className="w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center text-white"
                style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
              >
                2
              </span>
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
                <FileText className="w-4 h-4 text-brandLight" />
                Paste Job Description
              </div>
            </div>

            <div className="relative group">
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the target job description here..."
                className="w-full h-44 rounded-2xl p-4 text-slate-200 text-sm placeholder:text-slate-600 focus:outline-none resize-none transition-all duration-300"
                style={{
                  background: 'rgba(0,0,0,0.3)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.2)',
                }}
                onFocus={(e) => {
                  e.target.style.border = '1px solid rgba(99,102,241,0.4)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.1), inset 0 2px 8px rgba(0,0,0,0.2)';
                }}
                onBlur={(e) => {
                  e.target.style.border = '1px solid rgba(255,255,255,0.08)';
                  e.target.style.boxShadow = 'inset 0 2px 8px rgba(0,0,0,0.2)';
                }}
              />
              {jdText && (
                <div className="absolute right-3 bottom-3">
                  <span
                    className="text-xs font-medium px-2.5 py-1 rounded-lg text-slate-500"
                    style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.06)' }}
                  >
                    {jdText.split(/\s+/).filter((w) => w.length > 0).length} words
                  </span>
                </div>
              )}
            </div>
            {jdText.trim() && <JDPreview text={jdText} />}
          </div>

          {/* Analyze button */}
          <motion.button
            whileHover={file && jdText.trim() ? { scale: 1.01, y: -1 } : {}}
            whileTap={file && jdText.trim() ? { scale: 0.99 } : {}}
            onClick={handleAnalyze}
            disabled={!file || !jdText.trim()}
            className="w-full py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-2.5 transition-all duration-300"
            style={
              file && jdText.trim()
                ? {
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    boxShadow: '0 0 30px rgba(99,102,241,0.35), 0 8px 24px rgba(0,0,0,0.4)',
                    color: '#ffffff',
                    cursor: 'pointer',
                  }
                : {
                    background: 'rgba(255,255,255,0.04)',
                    border: '1px solid rgba(255,255,255,0.06)',
                    color: 'rgba(148,163,184,0.5)',
                    cursor: 'not-allowed',
                  }
            }
          >
            <Sparkles className="w-5 h-5" />
            {file && jdText.trim() ? 'Analyze Resume Fit' : 'Complete Both Steps'}
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
