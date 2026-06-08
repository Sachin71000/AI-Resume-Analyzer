import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Briefcase, Zap, Target } from 'lucide-react';

interface JDPreviewProps {
  text: string;
}

export const JDPreview = ({ text }: JDPreviewProps) => {
  const [analysis, setAnalysis] = useState<{
    title: string | null;
    level: string | null;
    skills: string[];
  }>({ title: null, level: null, skills: [] });

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (!text.trim()) {
        setAnalysis({ title: null, level: null, skills: [] });
        return;
      }
      
      const lowerText = text.toLowerCase();
      
      let level = null;
      if (lowerText.match(/\b(senior|staff|principal|lead|director)\b/)) level = 'Senior';
      else if (lowerText.match(/\b(mid|intermediate)\b/)) level = 'Mid-Level';
      else if (lowerText.match(/\b(junior|entry|intern)\b/)) level = 'Entry-Level';
      
      const commonSkills = ['python', 'javascript', 'typescript', 'react', 'node', 'aws', 'docker', 'kubernetes', 'sql', 'java', 'c++', 'go', 'azure', 'gcp', 'ci/cd', 'agile', 'machine learning', 'data science'];
      const foundSkills = commonSkills.filter(skill => lowerText.includes(skill));
      
      const lines = text.split('\n').filter(l => l.trim().length > 0);
      let title = lines[0]?.length < 50 ? lines[0] : null;

      setAnalysis({ title, level, skills: foundSkills.slice(0, 5) });
    }, 500);
    
    return () => clearTimeout(timeout);
  }, [text]);

  if (!text.trim()) return null;

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        className="mt-3 bg-brand/5 border border-brand/20 rounded-xl p-4 overflow-hidden"
      >
        <div className="flex items-center gap-2 mb-3">
          <Zap className="w-4 h-4 text-brand" />
          <span className="text-sm font-semibold text-brandLight">Live Preview Scan</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
              <Briefcase className="w-3 h-3" /> Role Detected
            </div>
            <div className="text-sm font-medium text-slate-200">
              {analysis.title || 'Unknown Title'} {analysis.level ? `• ${analysis.level}` : ''}
            </div>
          </div>
          
          <div>
            <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
              <Target className="w-3 h-3" /> Key Skills Seen
            </div>
            <div className="flex flex-wrap gap-1.5">
              {analysis.skills.length > 0 ? (
                analysis.skills.map(s => (
                  <span key={s} className="px-2 py-0.5 bg-black/20 text-slate-300 text-xs rounded border border-white/5 capitalize">
                    {s}
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-500">Keep typing...</span>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
