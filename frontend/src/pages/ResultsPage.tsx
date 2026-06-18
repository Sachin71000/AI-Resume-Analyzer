import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { useState } from 'react';
import type { AnalysisResponse } from '../types';
import { ScoreGauge } from '../components/ui/ScoreGauge';
import { ScoreCard } from '../components/ui/ScoreCard';
import { SkillBadge } from '../components/ui/SkillBadge';
import { Confetti } from '../components/ui/Confetti';
import { ScoreRadarChart } from '../components/ui/ScoreRadarChart';
import { ImprovementRoadmap } from '../components/ui/ImprovementRoadmap';
import { SpotlightCard } from '../components/reactbits/SpotlightCard';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, LayoutTemplate, Type, FileSearch, Settings, Star,
  ChevronDown, ArrowUpRight, CheckCircle2, AlertTriangle,
  AlertCircle, Download, RefreshCw, XCircle, Sparkles, Brain
} from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } },
};

export default function ResultsPage({ injectedData }: { injectedData?: AnalysisResponse }) {
  const location = useLocation();
  const navigate = useNavigate();
  const results = injectedData || (location.state?.results as AnalysisResponse);

  if (!results) return <Navigate to="/" replace />;

  const { scores, skills, sections, quality, ats, suggestions, delta, analysis_id } = results;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-6xl mx-auto w-full space-y-6"
    >
      <Confetti trigger={scores.overall > 75} />

      {/* HEADER */}
      <motion.div
        variants={itemVariants}
        className="relative overflow-hidden rounded-3xl p-6 md:p-8"
        style={{
          background: 'linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(30,41,59,0.9) 100%)',
          border: '1px solid rgba(255,255,255,0.08)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        }}
      >
        {/* Background gradient accent */}
        <div
          className="absolute top-0 right-0 w-64 h-64 rounded-full pointer-events-none"
          style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%)', transform: 'translate(30%, -30%)' }}
        />

        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-brand mb-3">
              <Sparkles className="w-3 h-3" /> Analysis Complete
            </div>
            <h1 className="text-3xl md:text-4xl font-black text-white mb-2 tracking-tight">
              Analysis Results
            </h1>
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <FileText className="w-4 h-4" />
              <span>{results.resume_filename}</span>
            </div>

            {delta?.improved && (
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold text-emerald-400"
                style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)' }}
              >
                <ArrowUpRight className="w-4 h-4" />
                Score improved by +{delta.overall}% from previous version
              </motion.div>
            )}
          </div>

          <div className="flex gap-3 shrink-0">
            <button
              onClick={() => navigate('/')}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 text-slate-300 transition-all duration-200 cursor-pointer"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.1)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
            >
              <RefreshCw className="w-4 h-4" /> New Analysis
            </button>
            {analysis_id && (
              <button
                onClick={() => window.open(`/api/export/${analysis_id}`, '_blank')}
                className="px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 text-white transition-all duration-200 cursor-pointer"
                style={{
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  boxShadow: '0 0 20px rgba(99,102,241,0.3)',
                }}
              >
                <Download className="w-4 h-4" /> Export PDF
              </button>
            )}
          </div>
        </div>
      </motion.div>

      {/* TOP METRICS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* MAIN SCORE CARD */}
        <motion.div
          variants={itemVariants}
          className="lg:col-span-4 rounded-3xl p-8 flex flex-col items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.08) 100%)',
            border: '1px solid rgba(99,102,241,0.15)',
            boxShadow: '0 0 40px rgba(99,102,241,0.08), 0 8px 32px rgba(0,0,0,0.3)',
          }}
        >
          <ScoreGauge score={scores.overall} label="Overall Match Score" size={200} strokeWidth={14} />

          {analysis_id && (
            <div className="mt-8 w-full space-y-3">
              <button
                onClick={() => navigate('/', { state: { parent_id: analysis_id } })}
                className="w-full py-3 rounded-xl font-semibold flex items-center justify-center gap-2 text-sm text-emerald-400 transition-all duration-200 cursor-pointer"
                style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)' }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(16,185,129,0.15)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(16,185,129,0.08)')}
              >
                <ArrowUpRight className="w-4 h-4" /> Improve This Resume
              </button>
              <button
                onClick={() => navigate('/interview/setup', { state: { analysis_id } })}
                className="w-full py-3 rounded-xl font-semibold flex items-center justify-center gap-2 text-sm text-white transition-all duration-200 cursor-pointer"
                style={{
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  boxShadow: '0 0 20px rgba(99,102,241,0.3)',
                }}
              >
                <Brain className="w-4 h-4" /> Start AI Interview Coach
              </button>
            </div>
          )}
        </motion.div>

        {/* SUB SCORES */}
        <motion.div variants={itemVariants} className="lg:col-span-8 grid grid-cols-2 md:grid-cols-3 gap-4">
          <ScoreCard delay={0.1} value={scores.tfidf_similarity || 0} label="Semantic Similarity" icon={<FileSearch className="w-4 h-4" />} />
          <ScoreCard delay={0.2} value={scores.skill_match} label="Skill Match" icon={<Settings className="w-4 h-4" />} />
          <ScoreCard delay={0.3} value={scores.section_coverage} label="Section Coverage" icon={<LayoutTemplate className="w-4 h-4" />} />
          <ScoreCard delay={0.4} value={scores.keyword_density} label="Keyword Density" icon={<Type className="w-4 h-4" />} />
          <ScoreCard delay={0.5} value={scores.quality} label="Resume Quality" icon={<Star className="w-4 h-4" />} />
          <ScoreCard delay={0.6} value={scores.ats_compatibility} label="ATS Score" icon={<CheckCircle2 className="w-4 h-4" />} />
        </motion.div>
      </div>

      {/* SKILLS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants}>
          <SpotlightCard className="p-6 md:p-8 h-full" spotlightColor="rgba(16,185,129,0.06)">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold flex items-center gap-2 text-white">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Skills Found
              </h2>
              <span
                className="text-xs font-bold px-2.5 py-1 rounded-full text-emerald-400"
                style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)' }}
              >
                {skills.found.length}
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {skills.found.length > 0
                ? skills.found.map((s, i) => <SkillBadge key={i} name={s.name} source={s.source || 'explicit'} status="found" />)
                : <p className="text-slate-500 text-sm">No matching skills detected.</p>
              }
            </div>
          </SpotlightCard>
        </motion.div>

        <motion.div variants={itemVariants}>
          <SpotlightCard className="p-6 md:p-8 h-full" spotlightColor="rgba(239,68,68,0.06)">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold flex items-center gap-2 text-white">
                <XCircle className="w-5 h-5 text-red-400" /> Missing Skills
              </h2>
              <span
                className="text-xs font-bold px-2.5 py-1 rounded-full text-red-400"
                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)' }}
              >
                {skills.missing.length}
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {skills.missing.length > 0
                ? skills.missing.map((s, i) => (
                  <SkillBadge key={i} name={s.name} source="explicit" status={s.importance === 'critical' ? 'critical' : 'missing'} />
                ))
                : <p className="text-emerald-400 text-sm font-medium">Great! No critical missing skills detected.</p>
              }
            </div>
          </SpotlightCard>
        </motion.div>
      </div>

      {/* SUGGESTIONS */}
      <motion.div variants={itemVariants}>
        <SpotlightCard className="p-6 md:p-8" spotlightColor="rgba(99,102,241,0.06)">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-8 text-white">
            <Sparkles className="w-5 h-5 text-brand" /> Improvement Insights
          </h2>
          {(!suggestions.ai_generated || suggestions.ai_generated.length === 0) && suggestions.rule_based.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10">
              <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4" style={{ background: 'rgba(16,185,129,0.1)' }}>
                <CheckCircle2 className="w-8 h-8 text-emerald-400" />
              </div>
              <p className="text-emerald-400 font-semibold text-lg">Your resume looks great — no major suggestions!</p>
            </div>
          ) : (
            <ImprovementRoadmap suggestions={[...(suggestions.ai_generated || []), ...(suggestions.rule_based || [])]} />
          )}
        </SpotlightCard>
      </motion.div>

      {/* QUALITY & ATS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants}>
          <SpotlightCard className="p-6 md:p-8 h-full" spotlightColor="rgba(245,158,11,0.06)">
            <h2 className="text-lg font-bold mb-6 flex items-center gap-2 text-white">
              <Star className="w-5 h-5 text-amber-400" /> Quality Checks
            </h2>
            <div className="space-y-3">
              {quality.issues.map((issue, i) => (
                <div
                  key={i}
                  className="flex gap-3 p-4 rounded-xl"
                  style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.05)' }}
                >
                  {issue.type === 'warning'
                    ? <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    : <AlertCircle className="w-4 h-4 text-brand shrink-0 mt-0.5" />
                  }
                  <p className="text-sm text-slate-300">{issue.message}</p>
                </div>
              ))}
              {quality.issues.length === 0 && (
                <p className="text-emerald-400 text-sm font-medium">No quality issues found.</p>
              )}
            </div>
          </SpotlightCard>
        </motion.div>

        <motion.div variants={itemVariants}>
          <SpotlightCard className="p-6 md:p-8 h-full" spotlightColor="rgba(99,102,241,0.05)">
            <h2 className="text-lg font-bold mb-6 flex items-center gap-2 text-white">
              <LayoutTemplate className="w-5 h-5 text-slate-400" /> ATS Compatibility
            </h2>
            <div className="space-y-3">
              {ats.issues.map((issue, i) => (
                <div
                  key={i}
                  className="p-4 rounded-xl"
                  style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.05)' }}
                >
                  <div className="flex gap-3 mb-2">
                    {issue.severity === 'high'
                      ? <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                      : issue.severity === 'medium'
                      ? <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                      : <AlertCircle className="w-4 h-4 text-slate-500 shrink-0" />
                    }
                    <p className="text-sm text-slate-200 font-medium">{issue.message}</p>
                  </div>
                  <p className="text-sm text-slate-500 ml-7">{issue.fix_suggestion}</p>
                </div>
              ))}
              {ats.issues.length === 0 && (
                <p className="text-emerald-400 text-sm font-medium">No ATS issues found.</p>
              )}
            </div>
          </SpotlightCard>
        </motion.div>
      </div>

      {/* ADVANCED DETAILS */}
      <AdvancedDetailsPanel sections={sections} quality={quality} scores={scores} />
    </motion.div>
  );
}

function AdvancedDetailsPanel({
  sections,
  quality,
  scores,
}: {
  sections: AnalysisResponse['sections'];
  quality: AnalysisResponse['quality'];
  scores: AnalysisResponse['scores'];
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      layout
      className="rounded-3xl overflow-hidden"
      style={{
        background: 'rgba(15,23,42,0.6)',
        border: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-6 md:p-8 transition-all duration-200 cursor-pointer"
        style={{ background: 'transparent' }}
        onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.02)')}
        onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
      >
        <h2 className="text-lg font-bold flex items-center gap-2 text-white">
          <FileText className="w-5 h-5 text-slate-500" /> Advanced Details
        </h2>
        <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.3 }}>
          <ChevronDown className="w-5 h-5 text-slate-500" />
        </motion.div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="px-6 md:px-8 pb-8"
          >
            <div className="mb-8 pt-6 border-t border-white/[0.05]">
              <h3 className="text-base font-semibold text-white mb-2 text-center">Score Breakdown</h3>
              <ScoreRadarChart scores={scores} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-6 border-t border-white/[0.05]">
              <div>
                <h3 className="text-base font-semibold text-white mb-4">Resume Sections</h3>
                <div className="space-y-4">
                  {[
                    { label: 'Detected', items: sections.detected, cls: 'text-emerald-400', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)' },
                    { label: 'Missing (Required)', items: sections.missing_required, cls: 'text-red-400', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)' },
                    { label: 'Missing (Recommended)', items: sections.missing_recommended, cls: 'text-amber-400', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)' },
                  ].map(({ label, items, cls, bg, border }) => (
                    <div key={label}>
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</h4>
                      <div className="flex flex-wrap gap-2">
                        {items.length > 0
                          ? items.map((s, i) => (
                            <span key={i} className={`px-3 py-1 text-xs rounded-lg font-medium ${cls}`} style={{ background: bg, border: `1px solid ${border}` }}>{s}</span>
                          ))
                          : <span className="text-xs text-emerald-400 font-medium">None!</span>
                        }
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-base font-semibold text-white mb-4">Quality Metrics</h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Word Count', value: quality.word_count, sub: quality.length_status, subCls: quality.length_status === 'optimal' ? 'text-emerald-400' : 'text-amber-400' },
                    { label: 'Action Verbs', value: `${quality.action_verb_percentage.toFixed(0)}%`, sub: `${quality.strong_verb_count} strong / ${quality.weak_verb_count} weak`, subCls: 'text-slate-500' },
                    { label: 'Metrics & Numbers', value: quality.metrics_count, sub: quality.has_metrics ? 'Good quantification' : 'Needs numbers', subCls: quality.has_metrics ? 'text-emerald-400' : 'text-red-400' },
                  ].map(({ label, value, sub, subCls }) => (
                    <div key={label} className="p-4 rounded-xl" style={{ background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div className="text-xs text-slate-500 mb-1 font-medium">{label}</div>
                      <div className="text-2xl font-black text-white">{value}</div>
                      <div className={`text-xs mt-1 font-medium ${subCls}`}>{sub}</div>
                    </div>
                  ))}
                  <div className="p-4 rounded-xl" style={{ background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div className="text-xs text-slate-500 mb-2 font-medium">Contact Info</div>
                    <div className="flex flex-wrap gap-1.5">
                      {Object.entries(quality.contact_info).map(([key, value]) => (
                        <div
                          key={key}
                          className={`flex items-center gap-1 text-[10px] px-2 py-0.5 rounded font-medium ${value ? 'text-emerald-400' : 'text-red-400'}`}
                          style={{ background: value ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)' }}
                        >
                          {value ? <CheckCircle2 className="w-2.5 h-2.5" /> : <XCircle className="w-2.5 h-2.5" />}
                          <span className="capitalize">{key}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
