import { motion } from 'framer-motion';
import { CountUp } from '../reactbits/CountUp';

interface ScoreGaugeProps {
  score: number;
  label?: string;
  size?: number;
  strokeWidth?: number;
}

export const ScoreGauge = ({ score, label, size = 200, strokeWidth = 14 }: ScoreGaugeProps) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Color config based on score
  let gradientStart = '#10b981';
  let gradientEnd = '#34d399';
  let glowColor = 'rgba(16,185,129,0.5)';
  
  if (score < 50) {
    gradientStart = '#ef4444';
    gradientEnd = '#f87171';
    glowColor = 'rgba(239,68,68,0.4)';
  } else if (score < 75) {
    gradientStart = '#f59e0b';
    gradientEnd = '#fcd34d';
    glowColor = 'rgba(245,158,11,0.4)';
  }

  const gradientId = `gauge-gradient-${Math.round(score)}`;

  return (
    <div className="relative flex flex-col items-center justify-center">
      <div
        style={{ width: size, height: size }}
        className="relative flex items-center justify-center"
      >
        <svg
          className="absolute -rotate-90 w-full h-full"
          viewBox={`0 0 ${size} ${size}`}
        >
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={gradientStart} />
              <stop offset="100%" stopColor={gradientEnd} />
            </linearGradient>
            <filter id="gauge-glow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Track circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={strokeWidth}
          />

          {/* Glow duplicate (slightly wider, blurred) */}
          <motion.circle
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.8, ease: 'easeOut' }}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke={glowColor}
            strokeWidth={strokeWidth + 6}
            strokeDasharray={circumference}
            strokeLinecap="round"
            style={{ filter: 'blur(6px)' }}
          />

          {/* Main progress arc */}
          <motion.circle
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.8, ease: 'easeOut' }}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke={`url(#${gradientId})`}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeLinecap="round"
          />
        </svg>

        {/* Inner content */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <motion.span
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="text-5xl font-black tracking-tight"
            style={{ color: gradientStart, textShadow: `0 0 20px ${glowColor}` }}
          >
            <CountUp to={score} duration={1.8} />
            <span className="text-2xl font-bold">%</span>
          </motion.span>
          <span className="text-xs text-slate-500 font-medium uppercase tracking-wider mt-1">
            Match
          </span>
        </div>
      </div>

      {label && (
        <span className="mt-5 text-sm font-semibold text-slate-300 tracking-wide text-center">
          {label}
        </span>
      )}
    </div>
  );
};
