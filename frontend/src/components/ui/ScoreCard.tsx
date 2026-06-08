import type { ReactNode } from 'react';
import { SpotlightCard } from '../reactbits/SpotlightCard';
import { CountUp } from '../reactbits/CountUp';

interface ScoreCardProps {
  label: string;
  value: number;
  maxScore?: number;
  icon?: ReactNode;
  delay?: number;
}

export const ScoreCard = ({ label, value, maxScore = 100, icon, delay = 0 }: ScoreCardProps) => {
  const percentage = (value / maxScore) * 100;
  
  let colorClass = 'text-success';
  let bgClass = 'bg-success';
  if (percentage < 50) {
    colorClass = 'text-danger';
    bgClass = 'bg-danger';
  } else if (percentage < 75) {
    colorClass = 'text-warning';
    bgClass = 'bg-warning';
  }

  return (
    <SpotlightCard className="p-5 flex flex-col gap-3 group">
      <div className="flex items-center justify-between text-slate-400">
        <div className="flex items-center gap-2 font-medium">
          {icon && <span className="opacity-70 group-hover:opacity-100 transition-opacity">{icon}</span>}
          {label}
        </div>
      </div>
      <div className="flex items-end gap-1">
        <span className={`text-3xl font-bold ${colorClass}`}>
          <CountUp to={value} duration={1.5} delay={delay} decimals={maxScore === 100 ? 0 : 1} />
        </span>
        <span className="text-sm text-slate-500 font-medium mb-1">/ {maxScore}</span>
      </div>
      <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden mt-1">
        <div 
          className={`h-full ${bgClass} transition-all duration-1000 ease-out`} 
          style={{ width: `${percentage}%`, transitionDelay: `${delay}s` }}
        />
      </div>
    </SpotlightCard>
  );
};
