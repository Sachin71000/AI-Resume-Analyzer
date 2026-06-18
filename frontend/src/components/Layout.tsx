import { Link, Outlet, useLocation } from 'react-router-dom';
import { FileSearch, History, BrainCircuit, Sparkles } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { AnimatedBackground } from './reactbits/AnimatedBackground';

export default function Layout() {
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    {
      to: '/',
      label: 'Analyze',
      icon: <FileSearch className="w-4 h-4" />,
      active: location.pathname === '/' || location.pathname.startsWith('/results'),
    },
    {
      to: '/history',
      label: 'History',
      icon: <History className="w-4 h-4" />,
      active: location.pathname.startsWith('/history') || location.pathname.startsWith('/analysis') || location.pathname.startsWith('/compare'),
    },
  ];

  return (
    <div className="min-h-screen bg-transparent text-slate-200 font-sans flex flex-col relative z-0">
      <AnimatedBackground />

      {/* Floating navbar */}
      <header
        className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-5xl px-4 transition-all duration-500 ${
          scrolled ? 'top-3' : 'top-4'
        }`}
      >
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className={`flex items-center justify-between px-5 h-16 rounded-2xl transition-all duration-500 ${
            scrolled
              ? 'bg-black/60 backdrop-blur-2xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.06)]'
              : 'bg-black/30 backdrop-blur-xl border border-white/[0.06] shadow-[0_4px_24px_rgba(0,0,0,0.3)]'
          }`}
        >
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group shrink-0">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center text-white transition-all duration-300 group-hover:scale-110"
              style={{
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)',
              }}
            >
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-[15px] leading-tight text-white tracking-tight">
                Smart Resume
              </span>
              <span className="text-[10px] text-slate-500 leading-tight tracking-wider uppercase font-medium">
                AI Analyzer
              </span>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-1 bg-white/[0.04] p-1 rounded-xl border border-white/[0.08]">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`relative flex items-center gap-2 px-4 md:px-5 py-2 rounded-lg text-sm font-medium transition-all duration-300 cursor-pointer ${
                  link.active
                    ? 'text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.06]'
                }`}
              >
                {link.active && (
                  <motion.div
                    layoutId="nav-pill"
                    className="absolute inset-0 rounded-lg"
                    style={{
                      background: 'linear-gradient(135deg, rgba(99,102,241,0.3) 0%, rgba(139,92,246,0.3) 100%)',
                      border: '1px solid rgba(99,102,241,0.3)',
                      boxShadow: '0 0 12px rgba(99,102,241,0.2)',
                    }}
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
                <span className="relative z-10 flex items-center gap-2">
                  {link.icon}
                  <span className="hidden md:inline">{link.label}</span>
                </span>
              </Link>
            ))}
          </nav>

          {/* Status badge */}
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 bg-white/[0.03] border border-white/[0.06] px-3 py-1.5 rounded-lg">
            <Sparkles className="w-3 h-3 text-brand" />
            <span>AI Powered</span>
          </div>
        </motion.div>
      </header>

      <main className="flex-1 pt-28 pb-16 flex flex-col relative z-10">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 16, filter: 'blur(8px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -16, filter: 'blur(8px)' }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="flex-1 flex flex-col max-w-7xl w-full mx-auto px-4 md:px-6"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/[0.04] py-6 text-center text-xs text-slate-600">
        <p>Smart Resume Analyzer &bull; Powered by AI</p>
      </footer>
    </div>
  );
}
