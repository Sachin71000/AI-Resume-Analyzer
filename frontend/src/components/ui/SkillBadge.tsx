import { motion } from 'framer-motion';
import { Sparkles, BookOpen, CheckCircle, XCircle } from 'lucide-react';
import { Magnet } from '../reactbits/Magnet';

interface SkillBadgeProps {
  name: string;
  source: string;
  status: 'found' | 'missing' | 'critical';
}

export const SkillBadge = ({ name, source, status }: SkillBadgeProps) => {
  const getStatusStyles = () => {
    switch (status) {
      case 'found':
        return 'bg-success/10 text-success border-success/20';
      case 'missing':
        return 'bg-danger/10 text-danger border-danger/20';
      case 'critical':
        return 'bg-warning/10 text-warning border-warning/20';
    }
  };

  const getSourceIcon = () => {
    if (source.toLowerCase() === 'inferred') return <Sparkles className="w-3 h-3" />;
    if (source.toLowerCase() === 'coursework' || source.toLowerCase() === 'project') return <BookOpen className="w-3 h-3" />;
    return <CheckCircle className="w-3 h-3" />;
  };

  return (
    <Magnet padding={20}>
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`inline-flex flex-col border rounded-xl px-3 py-2 text-sm font-medium ${getStatusStyles()}`}
      >
        <div className="flex items-center gap-1.5">
          {status === 'missing' || status === 'critical' ? <XCircle className="w-4 h-4 opacity-70" /> : null}
          {name}
        </div>
        {status === 'found' && source !== 'explicit' && (
          <div className="flex items-center gap-1 text-[10px] uppercase tracking-wider mt-1 opacity-80 border-t border-current/10 pt-1">
            {getSourceIcon()}
            {source}
          </div>
        )}
      </motion.div>
    </Magnet>
  );
};
