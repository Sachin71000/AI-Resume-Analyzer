import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { ChevronDown, Sparkles, CheckCircle2, AlertTriangle, ArrowRight, Target } from 'lucide-react';
import type { SuggestionItem } from '../../types';

interface RoadmapProps {
  suggestions: SuggestionItem[];
}

export const ImprovementRoadmap = ({ suggestions }: RoadmapProps) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const immediate = suggestions.filter(s => s.priority === 'high');
  const shortTerm = suggestions.filter(s => s.priority === 'medium');
  const longTerm = suggestions.filter(s => s.priority === 'low');

  const timelineSteps = [
    { id: 'immediate', title: 'Immediate Fixes', color: 'text-danger border-danger', bg: 'bg-danger/10', items: immediate, icon: <AlertTriangle className="w-5 h-5" /> },
    { id: 'short', title: 'Short-term Polish', color: 'text-warning border-warning', bg: 'bg-warning/10', items: shortTerm, icon: <Target className="w-5 h-5" /> },
    { id: 'long', title: 'Long-term Goals', color: 'text-success border-success', bg: 'bg-success/10', items: longTerm, icon: <CheckCircle2 className="w-5 h-5" /> }
  ].filter(step => step.items.length > 0);

  if (timelineSteps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mb-4">
          <CheckCircle2 className="w-8 h-8 text-success" />
        </div>
        <p className="text-success font-medium text-lg">Your resume looks perfect — no major suggestions!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
      {timelineSteps.map((step, idx) => (
        <div key={step.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
          {/* Icon node */}
          <div className={`flex items-center justify-center w-10 h-10 rounded-full border-4 border-slate-900 ${step.bg} ${step.color.split(' ')[0]} shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-xl absolute left-0 md:left-1/2 -translate-x-1/2 z-10`}>
            {step.icon}
          </div>
          
          {/* Card */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] ml-16 md:ml-0 p-5 rounded-2xl bg-surface/50 border border-white/5 backdrop-blur-sm shadow-xl relative z-0`}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className={`font-bold text-lg ${step.color.split(' ')[0]}`}>{step.title}</h3>
              <span className="text-xs font-semibold bg-white/5 px-2 py-1 rounded text-slate-400">{step.items.length} items</span>
            </div>
            
            <div className="space-y-3">
              {step.items.map((item, i) => {
                const isAI = item.source === 'ai';
                const itemId = `${step.id}-${i}`;
                const isExpanded = expandedId === itemId;
                
                return (
                  <div key={i} className={`p-3 rounded-xl bg-black/20 border border-white/5 transition-colors ${isAI && item.example ? 'cursor-pointer hover:bg-white/5' : ''}`} onClick={() => isAI && item.example && setExpandedId(isExpanded ? null : itemId)}>
                    <div className="flex gap-3">
                      <div className="mt-0.5">
                        {isAI ? <Sparkles className="w-4 h-4 text-[#c084fc]" /> : <ArrowRight className="w-4 h-4 text-slate-500" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-slate-200 leading-relaxed">{item.suggestion}</p>
                        
                        <AnimatePresence>
                          {isAI && item.example && isExpanded && (
                            <motion.div 
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              exit={{ opacity: 0, height: 0 }}
                              className="mt-3 pt-3 border-t border-white/10"
                            >
                              <div className="text-[10px] font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Example Rewrite</div>
                              <p className="text-sm text-brandLight italic bg-brand/5 p-2 rounded-lg border border-brand/10">"{item.example}"</p>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                      
                      {isAI && item.example && (
                        <div className="shrink-0 text-slate-500">
                          <motion.div animate={{ rotate: isExpanded ? 180 : 0 }}>
                            <ChevronDown className="w-4 h-4" />
                          </motion.div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </div>
      ))}
    </div>
  );
};
