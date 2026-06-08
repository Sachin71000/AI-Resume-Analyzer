import { useEffect, useState, useRef } from 'react';

interface CountUpProps {
  to: number;
  duration?: number;
  delay?: number;
  className?: string;
  decimals?: number;
}

export const CountUp = ({ to, duration = 1.5, delay = 0, className = '', decimals = 0 }: CountUpProps) => {
  const [count, setCount] = useState(0);
  const countRef = useRef(0);
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    let timeout: ReturnType<typeof setTimeout>;
    let animationFrame: number;

    timeout = setTimeout(() => {
      let startTime: number;

      const animate = (timestamp: number) => {
        if (!startTime) startTime = timestamp;
        const progress = timestamp - startTime;
        const percentage = Math.min(progress / (duration * 1000), 1);
        
        // Easing function (easeOutExpo)
        const easeProgress = percentage === 1 ? 1 : 1 - Math.pow(2, -10 * percentage);
        
        const currentCount = easeProgress * to;
        countRef.current = currentCount;
        setCount(currentCount);

        if (percentage < 1) {
          animationFrame = requestAnimationFrame(animate);
        } else {
          setCount(to);
        }
      };

      animationFrame = requestAnimationFrame(animate);
    }, delay * 1000);

    return () => {
      clearTimeout(timeout);
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [to, duration, delay, isVisible]);

  return (
    <span ref={ref} className={className}>
      {count.toFixed(decimals)}
    </span>
  );
};
