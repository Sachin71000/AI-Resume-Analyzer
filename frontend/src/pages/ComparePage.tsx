import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { compareAnalyses } from '../services/api';
import type { CompareResponse } from '../types';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowRightLeft, TrendingUp, TrendingDown, Minus, CheckCircle2, XCircle } from 'lucide-react';

export default function ComparePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const ids = params.get('ids')?.split(',') || [];

  useEffect(() => {
    if (ids.length !== 2) {
      setError('Please provide exactly 2 analysis IDs to compare.');
      setLoading(false);
      return;
    }

    compareAnalyses(ids)
      .then(res => setData(res))
      .catch(err => setError(err?.response?.data?.error || err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="py-20 flex flex-col items-center justify-center space-y-4">
      <div className="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin" />
      <p className="text-slate-400 font-medium">Comparing analyses...</p>
    </div>
  );
  
  if (error) return (
    <div className="max-w-2xl mx-auto py-20 text-center space-y-6">
      <div className="bg-danger/10 text-danger p-4 rounded-xl border border-danger/20 font-medium">
        {error}
      </div>
      <button className="px-6 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 transition-colors font-medium text-sm inline-flex items-center gap-2" onClick={() => navigate('/history')}>
        <ArrowLeft className="w-4 h-4" /> Back to History
      </button>
    </div>
  );
  
  if (!data) return null;

  const { analyses, comparison } = data;
  const [a1, a2] = analyses;
  const deltas = comparison.score_deltas;

  const renderDelta = (val: number, isScore = true) => {
    if (val > 0) return (
      <span className="inline-flex items-center gap-1 text-success font-bold bg-success/10 px-2.5 py-1 rounded-lg text-sm">
        <TrendingUp className="w-4 h-4" /> +{val}{isScore ? '%' : ''}
      </span>
    );
    if (val < 0) return (
      <span className="inline-flex items-center gap-1 text-danger font-bold bg-danger/10 px-2.5 py-1 rounded-lg text-sm">
        <TrendingDown className="w-4 h-4" /> {val}{isScore ? '%' : ''}
      </span>
    );
    return (
      <span className="inline-flex items-center gap-1 text-slate-500 font-bold bg-white/5 px-2.5 py-1 rounded-lg text-sm">
        <Minus className="w-4 h-4" /> 0{isScore ? '%' : ''}
      </span>
    );
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
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
      className="max-w-5xl mx-auto w-full space-y-8"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <button 
            onClick={() => navigate('/history')}
            className="mb-4 text-sm text-slate-400 hover:text-white transition-colors inline-flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Back to History
          </button>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <ArrowRightLeft className="w-8 h-8 text-brand" /> Resume Comparison
          </h1>
          <p className="text-slate-400 flex items-center gap-2">
            <span className="font-medium text-slate-300">{a1.resume_filename}</span>
            <span className="text-slate-600">vs</span>
            <span className="font-medium text-brandLight">{a2.resume_filename}</span>
          </p>
        </div>
      </div>

      <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-black/20 border-b border-white/5">
                <th className="p-5 text-sm font-semibold text-slate-300 uppercase tracking-wider">Metric</th>
                <th className="p-5 text-sm font-semibold text-slate-400 uppercase tracking-wider">
                  <div className="text-xs font-normal text-slate-500 mb-1">Old Version</div>
                  {new Date(a1.timestamp).toLocaleDateString()}
                </th>
                <th className="p-5 text-sm font-semibold text-brandLight uppercase tracking-wider bg-brand/5">
                  <div className="text-xs font-normal text-brand/50 mb-1">New Version</div>
                  {new Date(a2.timestamp).toLocaleDateString()}
                </th>
                <th className="p-5 text-sm font-semibold text-slate-300 uppercase tracking-wider">Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              <tr className="hover:bg-white/[0.02] transition-colors">
                <td className="p-5 font-bold text-white text-lg">Overall Score</td>
                <td className="p-5 text-slate-300 text-lg">{a1.scores.overall.toFixed(1)}%</td>
                <td className="p-5 text-brandLight text-lg bg-brand/[0.02] font-semibold">{a2.scores.overall.toFixed(1)}%</td>
                <td className="p-5">{renderDelta(deltas.overall)}</td>
              </tr>
              <tr className="hover:bg-white/[0.02] transition-colors">
                <td className="p-5 text-slate-200 font-medium">Skill Match</td>
                <td className="p-5 text-slate-400">{a1.scores.skill_match.toFixed(1)}%</td>
                <td className="p-5 text-slate-200 bg-brand/[0.02]">{a2.scores.skill_match.toFixed(1)}%</td>
                <td className="p-5">{renderDelta(deltas.skill_match)}</td>
              </tr>
              <tr className="hover:bg-white/[0.02] transition-colors">
                <td className="p-5 text-slate-200 font-medium">ATS Compatibility</td>
                <td className="p-5 text-slate-400">{a1.scores.ats_compatibility.toFixed(1)}%</td>
                <td className="p-5 text-slate-200 bg-brand/[0.02]">{a2.scores.ats_compatibility.toFixed(1)}%</td>
                <td className="p-5">{renderDelta(deltas.ats_compatibility)}</td>
              </tr>
              <tr className="hover:bg-white/[0.02] transition-colors">
                <td className="p-5 text-slate-200 font-medium">Quality</td>
                <td className="p-5 text-slate-400">{a1.scores.quality.toFixed(1)}</td>
                <td className="p-5 text-slate-200 bg-brand/[0.02]">{a2.scores.quality.toFixed(1)}</td>
                <td className="p-5">{renderDelta(deltas.quality)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold flex items-center gap-2 text-success">
              <CheckCircle2 className="w-6 h-6" /> Skills Gained
            </h3>
            <span className="bg-success/10 text-success px-3 py-1 rounded-full text-sm font-bold">+{comparison.skills_gained.length}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {comparison.skills_gained.length > 0 ? (
              comparison.skills_gained.map((s, i) => (
                <span key={i} className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium bg-success/10 text-success border border-success/20">
                  +{s}
                </span>
              ))
            ) : (
              <p className="text-slate-500 text-sm">No new skills detected.</p>
            )}
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold flex items-center gap-2 text-danger">
              <XCircle className="w-6 h-6" /> Skills Lost
            </h3>
            <span className="bg-danger/10 text-danger px-3 py-1 rounded-full text-sm font-bold">-{comparison.skills_lost.length}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {comparison.skills_lost.length > 0 ? (
              comparison.skills_lost.map((s, i) => (
                <span key={i} className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium bg-danger/10 text-danger border border-danger/20">
                  -{s}
                </span>
              ))
            ) : (
              <p className="text-success text-sm font-medium">No skills were lost!</p>
            )}
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
