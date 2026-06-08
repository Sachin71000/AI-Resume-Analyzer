import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { analyzeResume } from '../services/api';
import { SplitText } from '../components/reactbits/SplitText';
import { ShinyText } from '../components/reactbits/ShinyText';
import { JDPreview } from '../components/ui/JDPreview';
import { Upload, FileText, File, Loader2, Sparkles, AlertCircle, ArrowUpRight, CheckCircle2, BrainCircuit } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
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

    const stepTimer1 = setTimeout(() => setLoadingStep(1), 800);
    const stepTimer2 = setTimeout(() => setLoadingStep(2), 2000);
    const stepTimer3 = setTimeout(() => setLoadingStep(3), 3500);

    try {
      let results;
      if (parentId) {
        import('../services/api').then(api => api.improveResume(file, jdText, parentId)).then(res => {
          clearTimeout(stepTimer1);
          clearTimeout(stepTimer2);
          clearTimeout(stepTimer3);
          navigate(`/analysis/${res.analysis_id}`, { state: { results: res } });
        }).catch(err => {
          throw err;
        });
        return;
      } else {
        results = await analyzeResume(file, jdText);
      }
      
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      navigate('/results', { state: { results } });
    } catch (err: any) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      setError(err.response?.data?.error || 'An error occurred during analysis. Is the backend running?');
      setLoading(false);
    }
  };

  if (loading) {
    const steps = [
      'Parsing document structure...',
      'Extracting skills & context...',
      'Computing match scores...',
      'Generating AI insights...',
    ];
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[60vh]">
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-surface/50 backdrop-blur-xl border border-white/10 rounded-3xl p-10 w-full max-w-md shadow-2xl shadow-brand/10 relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-full h-1 bg-white/5">
            <motion.div 
              className="h-full bg-gradient-to-r from-brand to-brandLight"
              initial={{ width: '0%' }}
              animate={{ width: `${((loadingStep + 1) / steps.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          
          <div className="flex justify-center mb-8">
            <div className="relative">
              <div className="w-16 h-16 rounded-2xl bg-brand/10 flex items-center justify-center">
                <BrainCircuit className="w-8 h-8 text-brand animate-pulse" />
              </div>
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 3, ease: "linear" }}
                className="absolute -inset-2 border-2 border-dashed border-brand/30 rounded-3xl"
              />
            </div>
          </div>
          
          <h3 className="text-xl font-semibold text-center mb-6">Analyzing Profile</h3>
          
          <div className="space-y-4">
            {steps.map((step, idx) => (
              <div key={idx} className="flex items-center gap-3">
                {idx < loadingStep ? (
                  <div className="w-6 h-6 rounded-full bg-success/20 text-success flex items-center justify-center">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                ) : idx === loadingStep ? (
                  <div className="w-6 h-6 rounded-full bg-brand/20 text-brand flex items-center justify-center">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                ) : (
                  <div className="w-6 h-6 rounded-full bg-white/5 border border-white/10" />
                )}
                <span className={`text-sm font-medium ${idx <= loadingStep ? 'text-white' : 'text-slate-500'}`}>
                  {step}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center max-w-4xl mx-auto w-full">
      <div className="text-center mb-12 space-y-4 mt-8">
        <SplitText 
          text="AI-Powered Resume Analysis" 
          className="text-4xl md:text-6xl font-extrabold tracking-tight"
          delay={0.04}
        />
        <motion.p 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-lg text-slate-400 max-w-2xl mx-auto"
        >
          {parentId ? (
            <span className="flex items-center justify-center gap-2 text-brandLight bg-brand/10 py-2 px-4 rounded-full inline-flex">
              <ArrowUpRight className="w-4 h-4" />
              Improvement Mode: Upload updated resume to track score changes
              <button 
                onClick={() => navigate('/', { replace: true })}
                className="ml-2 text-xs bg-white/10 hover:bg-white/20 px-2 py-1 rounded"
              >
                Cancel
              </button>
            </span>
          ) : (
            "Upload your resume and paste the job description to get a deep-dive match analysis and actionable feedback."
          )}
        </motion.p>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="w-full bg-surface/40 backdrop-blur-md border border-white/10 p-1 rounded-3xl shadow-xl"
      >
        <div className="bg-surface/80 rounded-[22px] p-6 md:p-8 space-y-8">
          
          <AnimatePresence>
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-danger/10 border border-danger/20 text-danger-400 p-4 rounded-xl flex items-start gap-3"
              >
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <p className="text-sm font-medium">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-300 ml-1">
              <File className="w-4 h-4 text-brandLight" />
              Step 1: Upload Resume
            </div>
            
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input')?.click()}
              className={`relative overflow-hidden group cursor-pointer border-2 border-dashed rounded-2xl p-8 transition-all duration-300 flex flex-col items-center justify-center min-h-[160px] ${
                dragActive 
                  ? 'border-brand bg-brand/5 scale-[1.02]' 
                  : file ? 'border-success/50 bg-success/5' : 'border-white/10 hover:border-brand/50 hover:bg-white/5'
              }`}
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
                  <div className="w-12 h-12 rounded-full bg-success/20 text-success flex items-center justify-center mb-3">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <p className="font-semibold text-white text-lg">{file.name}</p>
                  <p className="text-sm text-slate-400 mt-1">
                    {(file.size / 1024 / 1024).toFixed(2)} MB • Click to replace
                  </p>
                </motion.div>
              ) : (
                <div className="flex flex-col items-center text-center">
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center mb-4 transition-colors ${dragActive ? 'bg-brand text-white' : 'bg-white/5 text-slate-400 group-hover:text-brand'}`}>
                    <Upload className="w-6 h-6" />
                  </div>
                  <p className="font-medium text-slate-200 text-lg mb-1">
                    Drag & drop your resume here
                  </p>
                  <p className="text-sm text-slate-400">
                    Supports PDF, DOC, DOCX up to 16MB
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-300 ml-1">
              <FileText className="w-4 h-4 text-brandLight" />
              Step 2: Target Job Description
            </div>
            
            <div className="relative group">
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the target job description here..."
                className="w-full h-40 bg-black/20 border border-white/10 rounded-2xl p-4 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand/50 resize-none transition-all"
              />
              <div className="absolute right-3 bottom-3 flex gap-2">
                <span className="text-xs text-slate-500 font-medium bg-white/5 px-2 py-1 rounded">
                  {jdText.split(/\s+/).filter(w => w.length > 0).length} words
                </span>
              </div>
            </div>
            {jdText.trim() && <JDPreview text={jdText} />}
          </div>

          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleAnalyze}
            disabled={!file || !jdText.trim()}
            className={`w-full py-4 rounded-xl flex items-center justify-center gap-2 font-semibold text-lg transition-all ${
              !file || !jdText.trim()
                ? 'bg-white/5 text-slate-500 cursor-not-allowed'
                : 'bg-brand text-white shadow-lg shadow-brand/25 hover:bg-brandLight'
            }`}
          >
            {file && jdText.trim() ? (
              <>
                <Sparkles className="w-5 h-5" />
                <ShinyText className="text-white">Analyze Fit</ShinyText>
              </>
            ) : (
              'Analyze Fit'
            )}
          </motion.button>

        </div>
      </motion.div>
    </div>
  );
}
