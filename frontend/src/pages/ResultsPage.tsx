import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { useState } from 'react';
import type { AnalysisResponse } from '../types';
import { ScoreGauge } from '../components/ui/ScoreGauge';
import { ScoreCard } from '../components/ui/ScoreCard';
import { SkillBadge } from '../components/ui/SkillBadge';
import { Confetti } from '../components/ui/Confetti';
import { ScoreRadarChart } from '../components/ui/ScoreRadarChart';
import { ImprovementRoadmap } from '../components/ui/ImprovementRoadmap';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, LayoutTemplate, Type, FileSearch, Settings, Star, 
  ChevronDown, ArrowUpRight, CheckCircle2, AlertTriangle, 
  AlertCircle, Download, RefreshCw, XCircle, Sparkles,
  Brain
} from 'lucide-react';



export default function ResultsPage({ injectedData }: { injectedData?: AnalysisResponse }) {
  const location = useLocation();
  const navigate = useNavigate();
  const results = injectedData || (location.state?.results as AnalysisResponse);

  if (!results) {
    return <Navigate to="/" replace />;
  }

  const { scores, skills, sections, quality, ats, suggestions, delta, analysis_id } = results;

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
      <Confetti trigger={scores.overall > 75} />
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 bg-surface/50 p-6 md:p-8 rounded-3xl border border-white/5">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            Analysis Results
          </h1>
          <div className="flex items-center gap-3 text-slate-400">
            <span className="flex items-center gap-1.5"><FileText className="w-4 h-4" /> {results.resume_filename}</span>
          </div>
          
          {delta && delta.improved && (
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="mt-4 inline-flex items-center gap-2 bg-success/10 text-success px-4 py-2 rounded-full text-sm font-bold"
            >
              <ArrowUpRight className="w-5 h-5" />
              Score increased by +{delta.overall}% from previous version
            </motion.div>
          )}
        </div>
        
        <div className="flex gap-3">
          <button onClick={() => navigate('/')} className="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 transition-colors font-medium text-sm flex items-center gap-2">
            <RefreshCw className="w-4 h-4" /> New Analysis
          </button>
          {analysis_id && (
            <button 
              onClick={() => window.open(`/api/export/${analysis_id}`, '_blank')}
              className="px-5 py-2.5 rounded-xl bg-brand hover:bg-brandLight text-white transition-colors font-medium text-sm flex items-center gap-2 shadow-lg shadow-brand/20"
            >
              <Download className="w-4 h-4" /> Download PDF
            </button>
          )}
        </div>
      </div>

      {/* TOP METRICS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* MAIN SCORE */}
        <motion.div variants={itemVariants} className="lg:col-span-4 bg-surface/50 border border-white/5 rounded-3xl p-8 flex flex-col items-center justify-center">
          <ScoreGauge score={scores.overall} label="Overall Match Score" size={200} strokeWidth={16} />
          {analysis_id && (
            <div className="mt-8 w-full space-y-3">
              <button 
                onClick={() => navigate('/', { state: { parent_id: analysis_id } })}
                className="w-full py-3 rounded-xl bg-success/10 hover:bg-success/20 text-success transition-colors font-semibold flex items-center justify-center gap-2 text-sm"
              >
                <ArrowUpRight className="w-5 h-5" /> Improve This Resume
              </button>
              
              <button 
                onClick={() => navigate('/interview/setup', { state: { analysis_id } })}
                className="w-full py-3 rounded-xl bg-brand hover:bg-brandLight text-white transition-colors font-semibold flex items-center justify-center gap-2 text-sm shadow-lg shadow-brand/10"
              >
                <Brain className="w-5 h-5" /> Start AI Interview Coach
              </button>
            </div>
          )}
        </motion.div>

        {/* SUB SCORES */}
        <motion.div variants={itemVariants} className="lg:col-span-8 grid grid-cols-2 md:grid-cols-3 gap-4">
          <ScoreCard delay={0.2} value={scores.tfidf_similarity || 0} label="Semantic Similarity" icon={<FileSearch className="w-4 h-4" />} />
          <ScoreCard delay={0.4} value={scores.skill_match} label="Skill Match" icon={<Settings className="w-4 h-4" />} />
          <ScoreCard delay={0.6} value={scores.section_coverage} label="Section Coverage" icon={<LayoutTemplate className="w-4 h-4" />} />
          <ScoreCard delay={0.8} value={scores.keyword_density} label="Keyword Density" icon={<Type className="w-4 h-4" />} />
          <ScoreCard delay={1.0} value={scores.quality} label="Resume Quality" icon={<Star className="w-4 h-4" />} />
          <ScoreCard delay={1.2} value={scores.ats_compatibility} label="ATS Score" icon={<CheckCircle2 className="w-4 h-4" />} />
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SKILLS DETECTED */}
        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-6 h-6 text-success" /> Skills Found
            </h2>
            <span className="bg-white/10 px-3 py-1 rounded-full text-sm font-medium">{skills.found.length}</span>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {skills.found.length > 0 ? (
              skills.found.map((s, i) => <SkillBadge key={i} name={s.name} source={s.source || 'explicit'} status="found" />)
            ) : (
              <p className="text-slate-400 text-sm">No matching skills detected. Try providing a more detailed resume.</p>
            )}
          </div>
        </motion.div>

        {/* MISSING SKILLS */}
        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <XCircle className="w-6 h-6 text-danger" /> Missing Skills
            </h2>
            <span className="bg-white/10 px-3 py-1 rounded-full text-sm font-medium">{skills.missing.length}</span>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {skills.missing.length > 0 ? (
              skills.missing.map((s, i) => (
                <SkillBadge 
                  key={i} 
                  name={s.name} 
                  source="explicit" 
                  status={s.importance === 'critical' ? 'critical' : 'missing'} 
                />
              ))
            ) : (
              <p className="text-success text-sm font-medium">Great! No critical missing skills detected.</p>
            )}
          </div>
        </motion.div>
      </div>

      {/* SUGGESTIONS & INSIGHTS */}
      <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8">
        <h2 className="text-xl font-semibold flex items-center gap-2 mb-8">
          <Sparkles className="w-6 h-6 text-brand" /> Improvement Insights
        </h2>

        {(!suggestions.ai_generated || suggestions.ai_generated.length === 0) && suggestions.rule_based.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10">
            <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mb-4">
              <CheckCircle2 className="w-8 h-8 text-success" />
            </div>
            <p className="text-success font-medium text-lg">Your resume looks great — no major suggestions!</p>
          </div>
        ) : (
          <ImprovementRoadmap suggestions={[...(suggestions.ai_generated || []), ...(suggestions.rule_based || [])]} />
        )}
      </motion.div>
      
      {/* QUALITY & ATS ISSUES */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Star className="w-6 h-6 text-warning" /> Quality Checks
          </h2>
          <div className="space-y-3">
            {quality.issues.map((issue, i) => (
              <div key={i} className="flex gap-3 bg-black/20 p-4 rounded-xl border border-white/5">
                {issue.type === 'warning' ? <AlertTriangle className="w-5 h-5 text-warning shrink-0" /> : <AlertCircle className="w-5 h-5 text-brandLight shrink-0" />}
                <p className="text-sm text-slate-300">{issue.message}</p>
              </div>
            ))}
            {quality.issues.length === 0 && (
              <p className="text-success text-sm font-medium">No quality issues found.</p>
            )}
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <LayoutTemplate className="w-6 h-6 text-slate-400" /> ATS Compatibility
          </h2>
          <div className="space-y-3">
            {ats.issues.map((issue, i) => (
              <div key={i} className="bg-black/20 p-4 rounded-xl border border-white/5">
                <div className="flex gap-3 mb-2">
                  {issue.severity === 'high' ? <AlertCircle className="w-5 h-5 text-danger shrink-0" /> : issue.severity === 'medium' ? <AlertTriangle className="w-5 h-5 text-warning shrink-0" /> : <AlertCircle className="w-5 h-5 text-slate-400 shrink-0" />}
                  <p className="text-sm text-slate-200 font-medium">{issue.message}</p>
                </div>
                <p className="text-sm text-slate-400 ml-8">{issue.fix_suggestion}</p>
              </div>
            ))}
            {ats.issues.length === 0 && (
              <p className="text-success text-sm font-medium">No ATS issues found.</p>
            )}
          </div>
        </motion.div>
      </div>

      {/* ADVANCED DETAILS (COLLAPSIBLE) */}
      <AdvancedDetailsPanel sections={sections} quality={quality} scores={scores} />

    </motion.div>
  );
}

function AdvancedDetailsPanel({ sections, quality, scores }: { sections: AnalysisResponse['sections'], quality: AnalysisResponse['quality'], scores: AnalysisResponse['scores'] }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div layout className="bg-surface/30 border border-white/5 rounded-3xl overflow-hidden mt-8">
      <button 
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-6 md:p-8 hover:bg-white/5 transition-colors"
      >
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <FileText className="w-6 h-6 text-slate-400" /> Advanced Details
        </h2>
        <motion.div animate={{ rotate: expanded ? 180 : 0 }}>
          <ChevronDown className="w-6 h-6 text-slate-400" />
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
            <div className="mb-8 pt-4 border-t border-white/5">
              <h3 className="text-lg font-medium text-white mb-2 text-center">Score Breakdown</h3>
              <ScoreRadarChart scores={scores} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-4 border-t border-white/5">
              
              {/* SECTIONS */}
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Resume Sections</h3>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm text-slate-400 mb-2">Detected</h4>
                    <div className="flex flex-wrap gap-2">
                      {sections.detected.length > 0 ? (
                        sections.detected.map((s, i) => <span key={i} className="px-3 py-1 bg-success/10 text-success text-sm rounded-lg border border-success/20">{s}</span>)
                      ) : <span className="text-sm text-slate-500">None detected</span>}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm text-slate-400 mb-2">Missing (Required)</h4>
                    <div className="flex flex-wrap gap-2">
                      {sections.missing_required.length > 0 ? (
                        sections.missing_required.map((s, i) => <span key={i} className="px-3 py-1 bg-danger/10 text-danger text-sm rounded-lg border border-danger/20">{s}</span>)
                      ) : <span className="text-sm text-success font-medium">None!</span>}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm text-slate-400 mb-2">Missing (Recommended)</h4>
                    <div className="flex flex-wrap gap-2">
                      {sections.missing_recommended.length > 0 ? (
                        sections.missing_recommended.map((s, i) => <span key={i} className="px-3 py-1 bg-warning/10 text-warning text-sm rounded-lg border border-warning/20">{s}</span>)
                      ) : <span className="text-sm text-success font-medium">None!</span>}
                    </div>
                  </div>
                </div>
              </div>

              {/* QUALITY METRICS */}
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Quality Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                    <div className="text-sm text-slate-400 mb-1">Word Count</div>
                    <div className="text-2xl font-bold text-white">{quality.word_count}</div>
                    <div className={`text-xs mt-1 ${quality.length_status === 'optimal' ? 'text-success' : 'text-warning'}`}>
                      {quality.length_status}
                    </div>
                  </div>
                  
                  <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                    <div className="text-sm text-slate-400 mb-1">Action Verbs</div>
                    <div className="text-2xl font-bold text-white">{quality.action_verb_percentage.toFixed(0)}%</div>
                    <div className="text-xs text-slate-500 mt-1">
                      {quality.strong_verb_count} strong / {quality.weak_verb_count} weak
                    </div>
                  </div>

                  <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                    <div className="text-sm text-slate-400 mb-1">Metrics & Numbers</div>
                    <div className="text-2xl font-bold text-white">{quality.metrics_count}</div>
                    <div className={`text-xs mt-1 ${quality.has_metrics ? 'text-success' : 'text-danger'}`}>
                      {quality.has_metrics ? 'Good quantification' : 'Needs numbers'}
                    </div>
                  </div>

                  <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                    <div className="text-sm text-slate-400 mb-2">Contact Info</div>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(quality.contact_info).map(([key, value]) => (
                        <div key={key} className={`flex items-center gap-1 text-xs px-2 py-1 rounded ${value ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
                          {value ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
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
