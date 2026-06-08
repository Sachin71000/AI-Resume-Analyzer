import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHistory, deleteAnalysis, deleteAnalyses } from '../services/api';
import type { HistoryItem } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronDown, Trash2, ArrowRightLeft, FileText, ChevronLeft, ChevronRight, Clock, Trash, CheckCircle2 } from 'lucide-react';

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('date');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, [page, sort, search]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await getHistory(page, 10, sort, search);
      setItems(data.items);
      setTotalPages(data.pages);
    } catch (error) {
      console.error("Failed to fetch history", error);
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
      else alert("You can only compare up to 5 analyses at once.");
    }
    setSelected(newSelected);
  };

  const handleCompare = () => {
    if (selected.size === 2) {
      navigate(`/compare?ids=${Array.from(selected).join(',')}`);
    } else {
      alert("Please select exactly 2 analyses to compare.");
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="max-w-5xl mx-auto w-full space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <Clock className="w-8 h-8 text-brand" /> Analysis History
          </h1>
          <p className="text-slate-400">Review past analyses and track score improvements over time.</p>
        </div>
      </div>

      <div className="bg-surface/50 border border-white/5 rounded-2xl p-4 flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="flex w-full sm:w-auto gap-4 flex-1">
          <div className="relative flex-1 sm:max-w-xs">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search resumes..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-black/20 border border-white/10 rounded-xl py-2 pl-9 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50 text-slate-200"
            />
          </div>
          <div className="relative">
            <select 
              value={sort} 
              onChange={(e) => setSort(e.target.value)}
              className="appearance-none bg-black/20 border border-white/10 rounded-xl py-2 pl-4 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50 text-slate-200 cursor-pointer"
            >
              <option value="date">Sort by Date</option>
              <option value="score">Sort by Score</option>
            </select>
            <ChevronDown className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          </div>
        </div>

        <AnimatePresence>
          {selected.size > 0 && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex items-center gap-3 w-full sm:w-auto"
            >
              <button 
                onClick={handleCompare} 
                disabled={selected.size !== 2}
                className={`flex-1 sm:flex-none px-4 py-2 rounded-xl flex items-center justify-center gap-2 text-sm font-medium transition-colors ${
                  selected.size === 2 ? 'bg-brand hover:bg-brandLight text-white' : 'bg-white/5 text-slate-500 cursor-not-allowed'
                }`}
              >
                <ArrowRightLeft className="w-4 h-4" /> Compare ({selected.size}/2)
              </button>
              <button 
                onClick={handleBulkDelete}
                className="px-4 py-2 rounded-xl bg-danger/10 hover:bg-danger/20 text-danger transition-colors flex items-center justify-center gap-2 text-sm font-medium"
              >
                <Trash2 className="w-4 h-4" /> Delete ({selected.size})
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {loading ? (
        <div className="py-20 flex justify-center">
          <div className="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin" />
        </div>
      ) : items.length === 0 ? (
        <div className="bg-surface/30 border border-white/5 rounded-3xl py-20 flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
            <FileText className="w-8 h-8 text-slate-500" />
          </div>
          <p className="text-slate-400 text-lg mb-6">No analyses found.</p>
          {search ? (
            <button className="px-6 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium" onClick={() => setSearch('')}>
              Clear Search
            </button>
          ) : (
            <button className="px-6 py-2.5 rounded-xl bg-brand hover:bg-brandLight text-white font-medium" onClick={() => navigate('/')}>
              Analyze a Resume
            </button>
          )}
        </div>
      ) : (
        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-3">
          {items.map(item => {
            const scoreColor = item.overall_score >= 70 ? 'bg-success' : item.overall_score >= 45 ? 'bg-warning' : 'bg-danger';
            
            return (
              <motion.div 
                key={item.id} 
                variants={itemVariants}
                className={`group flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-2xl border transition-all ${
                  selected.has(item.id) ? 'bg-brand/5 border-brand/30' : 'bg-surface/50 border-white/5 hover:border-white/10'
                }`}
              >
                <div className="flex items-center gap-4 flex-1">
                  <div 
                    onClick={() => toggleSelect(item.id)}
                    className={`w-5 h-5 rounded border flex items-center justify-center cursor-pointer transition-colors ${
                      selected.has(item.id) ? 'bg-brand border-brand text-white' : 'border-white/20 hover:border-brand/50'
                    }`}
                  >
                    {selected.has(item.id) && <CheckCircle2 className="w-3.5 h-3.5" />}
                  </div>
                  
                  <div className="flex-1 cursor-pointer" onClick={() => navigate(`/analysis/${item.id}`)}>
                    <h3 className="text-base font-semibold text-slate-200 group-hover:text-brandLight transition-colors flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-500" />
                      {item.resume_filename}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">
                      {new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })} at {new Date(item.created_at).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                      {item.label && <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-white/10 text-slate-300">{item.label}</span>}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between sm:justify-end gap-6 sm:w-[300px]">
                  <div className="w-[120px]">
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-slate-400">Score</span>
                      <span className="font-bold text-slate-200">{item.overall_score.toFixed(1)}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                      <div className={`h-full ${scoreColor} rounded-full`} style={{ width: `${item.overall_score}%` }} />
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button 
                      className="px-4 py-1.5 rounded-lg text-sm font-medium bg-white/5 hover:bg-white/10 text-slate-300 transition-colors"
                      onClick={() => navigate(`/analysis/${item.id}`)}
                    >
                      View
                    </button>
                    <button 
                      className="p-1.5 rounded-lg hover:bg-danger/10 text-slate-500 hover:text-danger transition-colors"
                      onClick={() => handleDelete(item.id)}
                    >
                      <Trash className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-6">
          <button 
            disabled={page === 1} 
            onClick={() => setPage(p => p - 1)}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="px-4 py-2 rounded-xl bg-surface/50 border border-white/5 text-sm font-medium">
            Page {page} of {totalPages}
          </div>
          <button 
            disabled={page === totalPages} 
            onClick={() => setPage(p => p + 1)}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
