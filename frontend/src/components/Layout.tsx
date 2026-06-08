import { Link, Outlet, useLocation } from 'react-router-dom';
import { FileSearch, History, BrainCircuit } from 'lucide-react';
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

  return (
    <div className="min-h-screen bg-transparent text-slate-200 font-sans flex flex-col relative z-0">
      <AnimatedBackground />
      
      <header 
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled ? 'bg-black/40 backdrop-blur-2xl border-b border-white/10 shadow-xl shadow-black/40' : 'bg-transparent border-b border-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand group-hover:bg-brand group-hover:text-white group-hover:border-brand transition-all duration-300 shadow-lg shadow-brand/10">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <span className="font-bold text-xl tracking-tight text-white group-hover:text-brandLight transition-colors">Smart Resume</span>
          </Link>
          
          <nav className="flex items-center gap-1 bg-black/20 backdrop-blur-xl p-1.5 rounded-full border border-white/10 shadow-inner shadow-white/5">
            <Link 
              to="/" 
              className={`flex items-center gap-2 px-4 md:px-5 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                location.pathname === '/' || location.pathname.startsWith('/results') 
                  ? 'bg-brand text-white shadow-lg shadow-brand/25 border border-brandLight/20' 
                  : 'text-slate-400 hover:text-white hover:bg-white/10 border border-transparent'
              }`}
            >
              <FileSearch className="w-4 h-4" />
              <span className="hidden md:inline">Analyze</span>
            </Link>
            <Link 
              to="/history" 
              className={`flex items-center gap-2 px-4 md:px-5 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                location.pathname.startsWith('/history') || location.pathname.startsWith('/analysis') || location.pathname.startsWith('/compare') 
                  ? 'bg-brand text-white shadow-lg shadow-brand/25 border border-brandLight/20' 
                  : 'text-slate-400 hover:text-white hover:bg-white/10 border border-transparent'
              }`}
            >
              <History className="w-4 h-4" />
              <span className="hidden md:inline">History</span>
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 pt-28 pb-12 flex flex-col relative z-10">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="flex-1 flex flex-col max-w-7xl w-full mx-auto px-6"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
