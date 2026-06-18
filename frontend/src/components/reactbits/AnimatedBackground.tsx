import { motion } from 'framer-motion';

export const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10" style={{ backgroundColor: '#020617' }}>
      {/* Primary aurora blobs */}
      <div className="absolute inset-0 opacity-[0.20]">
        <motion.div
          animate={{
            scale: [1, 1.3, 1.1, 1],
            x: [0, 120, 60, 0],
            y: [0, 60, -30, 0],
          }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[-15%] left-[-10%] w-[55%] h-[55%] rounded-full will-change-transform"
          style={{
            background: 'radial-gradient(ellipse, #6366f1 0%, #4f46e5 40%, transparent 70%)',
            filter: 'blur(80px)',
            backfaceVisibility: 'hidden',
            transform: 'translateZ(0)',
          }}
        />
        <motion.div
          animate={{
            scale: [1, 1.4, 1.2, 1],
            x: [0, -130, -60, 0],
            y: [0, 80, 40, 0],
          }}
          transition={{ duration: 28, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-[-15%] right-[-10%] w-[65%] h-[65%] rounded-full will-change-transform"
          style={{
            background: 'radial-gradient(ellipse, #8b5cf6 0%, #7c3aed 40%, transparent 70%)',
            filter: 'blur(100px)',
            backfaceVisibility: 'hidden',
            transform: 'translateZ(0)',
          }}
        />
        <motion.div
          animate={{
            scale: [1, 1.2, 0.9, 1],
            x: [0, 60, -40, 0],
            y: [0, -80, -30, 0],
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[35%] left-[45%] w-[45%] h-[45%] rounded-full will-change-transform"
          style={{
            background: 'radial-gradient(ellipse, #a78bfa 0%, #6366f1 40%, transparent 70%)',
            filter: 'blur(90px)',
            backfaceVisibility: 'hidden',
            transform: 'translateZ(0)',
          }}
        />
        {/* Accent teal spot */}
        <motion.div
          animate={{
            scale: [1, 1.5, 1.2, 1],
            x: [0, -80, 40, 0],
            y: [0, 60, -60, 0],
          }}
          transition={{ duration: 32, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[60%] left-[5%] w-[35%] h-[35%] rounded-full will-change-transform"
          style={{
            background: 'radial-gradient(ellipse, #06b6d4 0%, #0891b2 40%, transparent 70%)',
            filter: 'blur(80px)',
            opacity: 0.6,
            backfaceVisibility: 'hidden',
            transform: 'translateZ(0)',
          }}
        />
      </div>

      {/* Dot grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.06]"
        style={{
          backgroundImage: `radial-gradient(rgba(148, 163, 184, 0.8) 1px, transparent 1px)`,
          backgroundSize: '28px 28px',
        }}
      />

      {/* Radial vignette to keep edges dark */}
      <div
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse 80% 80% at 50% 50%, transparent 40%, rgba(2, 6, 23, 0.7) 100%)',
        }}
      />
    </div>
  );
};
