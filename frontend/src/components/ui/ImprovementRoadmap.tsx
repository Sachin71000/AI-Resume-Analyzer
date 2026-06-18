import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { ChevronDown, Sparkles, CheckCircle2, ArrowRight, Target, Zap } from 'lucide-react';
import type { SuggestionItem } from '../../types';

interface RoadmapProps {
  suggestions: SuggestionItem[];
}

export const ImprovementRoadmap = ({ suggestions }: RoadmapProps) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const immediate = suggestions.filter((s) => s.priority === 'high');
  const shortTerm  = suggestions.filter((s) => s.priority === 'medium');
  const longTerm   = suggestions.filter((s) => s.priority === 'low');

  const timelineSteps = [
    {
      id: 'immediate',
      title: 'Immediate Fixes',
      subtitle: 'High impact, do these now',
      color: '#ef4444',
      glow: 'rgba(239,68,68,0.2)',
      bg: 'rgba(239,68,68,0.08)',
      border: 'rgba(239,68,68,0.2)',
      items: immediate,
      icon: <Zap className="w-4 h-4" />,
    },
    {
      id: 'short',
      title: 'Short-term Polish',
      subtitle: 'Medium priority improvements',
      color: '#f59e0b',
      glow: 'rgba(245,158,11,0.2)',
      bg: 'rgba(245,158,11,0.08)',
      border: 'rgba(245,158,11,0.2)',
      items: shortTerm,
      icon: <Target className="w-4 h-4" />,
    },
    {
      id: 'long',
      title: 'Long-term Goals',
      subtitle: 'Optional enhancements',
      color: '#10b981',
      glow: 'rgba(16,185,129,0.2)',
      bg: 'rgba(16,185,129,0.08)',
      border: 'rgba(16,185,129,0.2)',
      items: longTerm,
      icon: <CheckCircle2 className="w-4 h-4" />,
    },
  ].filter((step) => step.items.length > 0);

  if (timelineSteps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
          style={{ background: 'rgba(16,185,129,0.1)' }}
        >
          <CheckCircle2 className="w-8 h-8 text-emerald-400" />
        </div>
        <p className="text-emerald-400 font-semibold text-lg">Your resume looks perfect!</p>
        <p className="text-slate-500 text-sm mt-1">No major suggestions at this time.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {timelineSteps.map((step, idx) => (
        <motion.div
          key={step.id}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1, duration: 0.4 }}
          className="rounded-2xl overflow-hidden"
          style={{
            background: step.bg,
            border: `1px solid ${step.border}`,
          }}
        >
          {/* Step header */}
          <div className="flex items-start gap-4 p-5">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
              style={{ background: `${step.color}20`, color: step.color, border: `1px solid ${step.border}`, boxShadow: `0 0 12px ${step.glow}` }}
            >
              {step.icon}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-base" style={{ color: step.color }}>{step.title}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">{step.subtitle}</p>
                </div>
                <span
                  className="text-xs font-bold px-2.5 py-1 rounded-full"
                  style={{ background: `${step.color}15`, color: step.color, border: `1px solid ${step.border}` }}
                >
                  {step.items.length} item{step.items.length !== 1 ? 's' : ''}
                </span>
              </div>

              {/* Items */}
              <div className="mt-4 space-y-2">
                {step.items.map((item, i) => {
                  const isAI = item.source === 'ai';
                  const itemId = `${step.id}-${i}`;
                  const isExpanded = expandedId === itemId;

                  return (
                    <div
                      key={i}
                      className={`p-3 rounded-xl transition-all duration-200 ${isAI && item.example ? 'cursor-pointer' : ''}`}
                      style={{
                        background: 'rgba(0,0,0,0.2)',
                        border: '1px solid rgba(255,255,255,0.05)',
                      }}
                      onClick={() => isAI && item.example && setExpandedId(isExpanded ? null : itemId)}
                      onMouseEnter={(e) => {
                        if (isAI && item.example) e.currentTarget.style.background = 'rgba(0,0,0,0.3)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(0,0,0,0.2)';
                      }}
                    >
                      <div className="flex gap-3">
                        <div className="mt-0.5 shrink-0">
                          {isAI
                            ? <Sparkles className="w-4 h-4" style={{ color: '#c084fc' }} />
                            : <ArrowRight className="w-4 h-4 text-slate-600" />
                          }
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-slate-200 leading-relaxed">{item.suggestion}</p>

                          <AnimatePresence>
                            {isAI && item.example && isExpanded && (
                              <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mt-3 pt-3"
                                style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}
                              >
                                <p className="text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-wider">Example Rewrite</p>
                                <p
                                  className="text-sm text-brandLight italic p-3 rounded-lg leading-relaxed"
                                  style={{ background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.12)' }}
                                >
                                  "{item.example}"
                                </p>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>

                        {isAI && item.example && (
                          <div className="shrink-0 text-slate-600 mt-0.5">
                            <motion.div animate={{ rotate: isExpanded ? 180 : 0 }} transition={{ duration: 0.25 }}>
                              <ChevronDown className="w-4 h-4" />
                            </motion.div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};
