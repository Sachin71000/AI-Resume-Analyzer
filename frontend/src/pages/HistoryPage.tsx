import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHistory, deleteAnalysis, deleteAnalyses } from '../services/api';
import type { HistoryItem } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, ChevronDown, Trash2, ArrowRightLeft, FileText,
  ChevronLeft, ChevronRight, Clock, Trash, CheckCircle2, TrendingUp
} from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.07 } },
};
const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] as const } },
};

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('date');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const navigate = useNavigate();

  useEffect(() => { fetchHistory(); }, [page, sort, search]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await getHistory(page, 10, sort, search);
      setItems(data.items);
      setTotalPages(data.pages);
    } catch (error) {
      console.error('Failed to fetch history', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selected);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      if (newSelected.size < 5) newSelected.add(id);
      else alert('You can only compare up to 5 analyses at once.');
    }
    setSelected(newSelected);
  };

  const handleCompare = () => {
    if (selected.size === 2) {
      navigate(`/compare?ids=${Array.from(selected).join(',')}`);
    } else {
      alert('Please select exactly 2 analyses to compare.');
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this analysis?')) {
      await deleteAnalysis(id);
      fetchHistory();
      if (selected.has(id)) toggleSelect(id);
    }
  };

  const handleBulkDelete = async () => {
    if (confirm(`Delete ${selected.size} selected analyses?`)) {
      await deleteAnalyses(Array.from(selected));
      setSelected(new Set());
      fetchHistory();
    }
  };

  const getScoreStyle = (score: number) => {
    if (score >= 70) return { color: '#10b981', glow: 'rgba(16,185,129,0.3)', bg: '#10b981' };
    if (score >= 45) return { color: '#f59e0b', glow: 'rgba(245,158,11,0.3)', bg: '#f59e0b' };
    return { color: '#ef4444', glow: 'rgba(239,68,68,0.3)', bg: '#ef4444' };
  };

  return (
    <div className="max-w-5xl mx-auto w-full space-y-6">

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-end justify-between gap-4"
      >
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-brand mb-3">
            <TrendingUp className="w-3 h-3" /> Track Progress
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-white mb-2 tracking-tight flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2))', border: '1px solid rgba(99,102,241,0.2)' }}
            >
              <Clock className="w-5 h-5 text-brand" />
            </div>
            Analysis History
          </h1>
          <p className="text-slate-500">Review past analyses and track score improvements over time.</p>
        </div>
      </motion.div>

      {/* Filters bar */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center p-4 rounded-2xl"
        style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(12px)' }}
      >
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search resumes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl py-2.5 pl-9 pr-4 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none transition-all duration-200"
            style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.07)' }}
            onFocus={(e) => { e.target.style.border = '1px solid rgba(99,102,241,0.4)'; e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.1)'; }}
            onBlur={(e) => { e.target.style.border = '1px solid rgba(255,255,255,0.07)'; e.target.style.boxShadow = 'none'; }}
          />
        </div>

        {/* Sort */}
        <div className="relative">
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="appearance-none rounded-xl py-2.5 pl-4 pr-9 text-sm text-slate-200 focus:outline-none cursor-pointer transition-all duration-200"
            style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.07)' }}
          >
            <option value="date">Sort by Date</option>
            <option value="score">Sort by Score</option>
          </select>
          <ChevronDown className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
        </div>

        {/* Action buttons (when selected) */}
        <AnimatePresence>
          {selected.size > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex gap-2"
            >
              <button
                onClick={handleCompare}
                disabled={selected.size !== 2}
                className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl flex items-center justify-center gap-2 text-sm font-semibold transition-all duration-200 cursor-pointer"
                style={
                  selected.size === 2
                    ? { background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: '#fff', boxShadow: '0 0 15px rgba(99,102,241,0.3)' }
                    : { background: 'rgba(255,255,255,0.04)', color: 'rgba(148,163,184,0.5)', cursor: 'not-allowed' }
                }
              >
                <ArrowRightLeft className="w-4 h-4" /> Compare ({selected.size}/2)
              </button>
              <button
                onClick={handleBulkDelete}
                className="px-4 py-2.5 rounded-xl flex items-center gap-2 text-sm font-semibold text-red-400 transition-all duration-200 cursor-pointer"
                style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)' }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(239,68,68,0.15)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(239,68,68,0.08)')}
              >
                <Trash2 className="w-4 h-4" /> Delete ({selected.size})
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Content */}
      {loading ? (
        <div className="py-20 flex justify-center">
          <div
            className="w-10 h-10 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: 'rgba(99,102,241,0.3)', borderTopColor: '#6366f1' }}
          />
        </div>
      ) : items.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="rounded-3xl py-20 flex flex-col items-center text-center"
          style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(255,255,255,0.06)' }}
        >
          <div
            className="w-20 h-20 rounded-2xl flex items-center justify-center mb-6"
            style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.15)' }}
          >
            <FileText className="w-10 h-10 text-brand opacity-60" />
          </div>
          <p className="text-slate-400 text-lg mb-2 font-semibold">No analyses found</p>
          <p className="text-slate-600 text-sm mb-8">
            {search ? 'Try a different search term' : 'Upload your first resume to get started'}
          </p>
          {search ? (
            <button
              className="px-6 py-2.5 rounded-xl font-semibold text-slate-300 transition-all cursor-pointer"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)' }}
              onClick={() => setSearch('')}
            >
              Clear Search
            </button>
          ) : (
            <button
              className="px-6 py-2.5 rounded-xl font-semibold text-white transition-all cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 0 20px rgba(99,102,241,0.3)' }}
              onClick={() => navigate('/')}
            >
              Analyze a Resume
            </button>
          )}
        </motion.div>
      ) : (
        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-3">
          {items.map((item) => {
            const scoreStyle = getScoreStyle(item.overall_score);
            const isSelected = selected.has(item.id);

            return (
              <motion.div key={item.id} variants={itemVariants}>
                <div
                  className="group flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-2xl transition-all duration-200 cursor-pointer"
                  style={{
                    background: isSelected
                      ? 'linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.08) 100%)'
                      : 'rgba(15,23,42,0.7)',
                    border: isSelected
                      ? '1px solid rgba(99,102,241,0.25)'
                      : '1px solid rgba(255,255,255,0.06)',
                    boxShadow: isSelected ? '0 0 20px rgba(99,102,241,0.1)' : 'none',
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) e.currentTarget.style.border = '1px solid rgba(255,255,255,0.1)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) e.currentTarget.style.border = '1px solid rgba(255,255,255,0.06)';
                  }}
                >
                  <div className="flex items-center gap-4 flex-1">
                    {/* Checkbox */}
                    <div
                      onClick={() => toggleSelect(item.id)}
                      className="w-5 h-5 rounded-md flex items-center justify-center shrink-0 transition-all duration-200 cursor-pointer"
                      style={{
                        background: isSelected ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'transparent',
                        border: isSelected ? 'none' : '1px solid rgba(255,255,255,0.2)',
                        boxShadow: isSelected ? '0 0 10px rgba(99,102,241,0.4)' : 'none',
                      }}
                    >
                      {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                    </div>

                    {/* Info */}
                    <div
                      className="flex-1 cursor-pointer"
                      onClick={() => navigate(`/analysis/${item.id}`)}
                    >
                      <h3 className="text-sm font-bold text-slate-200 group-hover:text-white transition-colors flex items-center gap-2">
                        <FileText className="w-4 h-4 text-slate-500 shrink-0" />
                        {item.resume_filename}
                      </h3>
                      <p className="text-xs text-slate-600 mt-0.5">
                        {new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        {' at '}
                        {new Date(item.created_at).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                        {item.label && (
                          <span
                            className="ml-2 px-2 py-0.5 rounded text-[10px] font-medium"
                            style={{ background: 'rgba(255,255,255,0.07)' }}
                          >
                            {item.label}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>

                  {/* Score + actions */}
                  <div className="flex items-center justify-between sm:justify-end gap-5 sm:w-[280px]">
                    <div className="w-[120px]">
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-slate-500 font-medium">Score</span>
                        <span className="font-black" style={{ color: scoreStyle.color }}>
                          {item.overall_score.toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-1.5 w-full rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                        <motion.div
                          initial={{ width: '0%' }}
                          animate={{ width: `${item.overall_score}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className="h-full rounded-full"
                          style={{
                            background: scoreStyle.bg,
                            boxShadow: `0 0 8px ${scoreStyle.glow}`,
                          }}
                        />
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        className="px-4 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200 cursor-pointer text-slate-300"
                        style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
                        onClick={() => navigate(`/analysis/${item.id}`)}
                        onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.1)')}
                        onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.05)')}
                      >
                        View
                      </button>
                      <button
                        className="p-1.5 rounded-lg transition-all duration-200 cursor-pointer text-slate-600 hover:text-red-400"
                        style={{ background: 'transparent' }}
                        onClick={() => handleDelete(item.id)}
                        onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(239,68,68,0.08)')}
                        onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                      >
                        <Trash className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-4">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="p-2.5 rounded-xl transition-all duration-200 cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed text-slate-400"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div
            className="px-5 py-2 rounded-xl text-sm font-semibold text-slate-300"
            style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(255,255,255,0.08)' }}
          >
            Page {page} of {totalPages}
          </div>
          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="p-2.5 rounded-xl transition-all duration-200 cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed text-slate-400"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
