import { motion } from 'framer-motion';
import { CountUp } from '../reactbits/CountUp';

interface ScoreGaugeProps {
  score: number;
  label?: string;
  size?: number;
  strokeWidth?: number;
}

export const ScoreGauge = ({ score, label, size = 160, strokeWidth = 12 }: ScoreGaugeProps) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  let colorClass = 'text-success';
  if (score < 50) colorClass = 'text-danger';
  else if (score < 75) colorClass = 'text-warning';

  return (
    <div className="relative flex flex-col items-center justify-center">
      <div style={{ width: size, height: size }} className="relative flex items-center justify-center">
        {/* Background Circle */}
        <svg className="absolute -rotate-90 w-full h-full" viewBox={`0 0 ${size} ${size}`}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-white/10"
          />
          {/* Foreground Circle */}
          <motion.circle
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeLinecap="round"
            className={`${colorClass}`}
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className={`text-4xl font-black ${colorClass}`}>
            <CountUp to={score} duration={1.5} />
            <span className="text-xl">%</span>
          </span>
        </div>
      </div>
      {label && <span className="mt-4 text-slate-300 font-medium tracking-wide">{label}</span>}
    </div>
  );
};
