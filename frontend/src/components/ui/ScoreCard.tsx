import type { ReactNode } from 'react';
import { SpotlightCard } from '../reactbits/SpotlightCard';
import { CountUp } from '../reactbits/CountUp';
import { motion } from 'framer-motion';

interface ScoreCardProps {
  label: string;
  value: number;
  maxScore?: number;
  icon?: ReactNode;
  delay?: number;
}

export const ScoreCard = ({ label, value, maxScore = 100, icon, delay = 0 }: ScoreCardProps) => {
  const percentage = (value / maxScore) * 100;

  let colorStyle = { color: '#10b981', barColor: '#10b981', barGlow: 'rgba(16,185,129,0.3)', spotlight: 'rgba(16,185,129,0.08)' };
  if (percentage < 50) {
    colorStyle = { color: '#ef4444', barColor: '#ef4444', barGlow: 'rgba(239,68,68,0.3)', spotlight: 'rgba(239,68,68,0.08)' };
  } else if (percentage < 75) {
    colorStyle = { color: '#f59e0b', barColor: '#f59e0b', barGlow: 'rgba(245,158,11,0.3)', spotlight: 'rgba(245,158,11,0.08)' };
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
    >
      <SpotlightCard
        className="p-5 flex flex-col gap-3 group cursor-default h-full"
        spotlightColor={colorStyle.spotlight}
      >
        {/* Header */}
        <div className="flex items-center gap-2 text-slate-400">
          {icon && (
            <span
              className="opacity-60 group-hover:opacity-100 transition-opacity duration-200"
              style={{ color: colorStyle.color }}
            >
              {icon}
            </span>
          )}
          <span className="text-xs font-semibold uppercase tracking-wider">{label}</span>
        </div>

        {/* Score value */}
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-black" style={{ color: colorStyle.color }}>
            <CountUp to={value} duration={1.5} delay={delay} decimals={maxScore === 100 ? 0 : 1} />
          </span>
          <span className="text-sm text-slate-500 font-medium">/ {maxScore}</span>
        </div>

        {/* Progress bar */}
        <div className="h-1.5 w-full rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 1.2, delay: delay + 0.1, ease: 'easeOut' }}
            className="h-full rounded-full"
            style={{
              background: `linear-gradient(90deg, ${colorStyle.barColor}, ${colorStyle.barColor}cc)`,
              boxShadow: `0 0 8px ${colorStyle.barGlow}`,
            }}
          />
        </div>
      </SpotlightCard>
    </motion.div>
  );
};
