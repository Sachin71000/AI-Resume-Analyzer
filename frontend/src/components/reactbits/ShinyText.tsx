import type { ReactNode } from 'react';

interface ShinyTextProps {
  children: ReactNode;
  className?: string;
}

export const ShinyText = ({ children, className = '' }: ShinyTextProps) => {
  return (
    <span
      className={`inline-block text-transparent bg-clip-text animate-shimmer bg-[linear-gradient(110deg,#e2e8f0,45%,#ffffff,55%,#e2e8f0)] bg-[length:250%_100%] ${className}`}
    >
      {children}
    </span>
  );
};
