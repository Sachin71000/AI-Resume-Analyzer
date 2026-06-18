import { motion } from 'framer-motion';
import { Sparkles, BookOpen, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface SkillBadgeProps {
  name: string;
  source: string;
  status: 'found' | 'missing' | 'critical';
}

export const SkillBadge = ({ name, source, status }: SkillBadgeProps) => {
  const config = {
    found: {
      bg: 'rgba(16,185,129,0.1)',
      border: 'rgba(16,185,129,0.2)',
      color: '#34d399',
      hoverBg: 'rgba(16,185,129,0.18)',
      icon: null,
    },
    missing: {
      bg: 'rgba(239,68,68,0.08)',
      border: 'rgba(239,68,68,0.2)',
      color: '#f87171',
      hoverBg: 'rgba(239,68,68,0.15)',
      icon: <XCircle className="w-3 h-3" />,
    },
    critical: {
      bg: 'rgba(245,158,11,0.08)',
      border: 'rgba(245,158,11,0.2)',
      color: '#fbbf24',
      hoverBg: 'rgba(245,158,11,0.15)',
      icon: <AlertTriangle className="w-3 h-3" />,
    },
  }[status];

  const getSourceIcon = () => {
    if (source.toLowerCase() === 'inferred') return <Sparkles className="w-2.5 h-2.5" />;
    if (source.toLowerCase() === 'coursework' || source.toLowerCase() === 'project') return <BookOpen className="w-2.5 h-2.5" />;
    return <CheckCircle className="w-2.5 h-2.5" />;
  };

  return (
    <motion.div
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.97 }}
      className="inline-flex flex-col rounded-xl px-3 py-2 text-xs font-semibold transition-all duration-200 cursor-default"
      style={{
        background: config.bg,
        border: `1px solid ${config.border}`,
        color: config.color,
      }}
      onMouseEnter={(e) => (e.currentTarget.style.background = config.hoverBg)}
      onMouseLeave={(e) => (e.currentTarget.style.background = config.bg)}
    >
      <div className="flex items-center gap-1.5">
        {config.icon}
        <span>{name}</span>
      </div>
      {status === 'found' && source !== 'explicit' && (
        <div
          className="flex items-center gap-1 mt-1 pt-1 uppercase tracking-wider text-[9px] opacity-70"
          style={{ borderTop: `1px solid ${config.border}` }}
        >
          {getSourceIcon()}
          {source}
        </div>
      )}
    </motion.div>
  );
};
