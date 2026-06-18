import type { ReactNode } from 'react';

interface ShinyTextProps {
  children: ReactNode;
  className?: string;
  variant?: 'white' | 'brand' | 'violet';
}

export const ShinyText = ({ children, className = '', variant = 'brand' }: ShinyTextProps) => {
  const gradients = {
    white: 'linear-gradient(110deg, #94a3b8, 45%, #ffffff, 55%, #94a3b8)',
    brand: 'linear-gradient(110deg, #6366f1, 40%, #c084fc, 55%, #818cf8, 70%, #6366f1)',
    violet: 'linear-gradient(110deg, #8b5cf6, 40%, #e879f9, 55%, #a78bfa, 70%, #8b5cf6)',
  };

  return (
    <span
      className={`inline-block text-transparent bg-clip-text ${className}`}
      style={{
        backgroundImage: gradients[variant],
        backgroundSize: '250% 100%',
        animation: 'shimmer 3s linear infinite',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}
    >
      {children}
    </span>
  );
};
