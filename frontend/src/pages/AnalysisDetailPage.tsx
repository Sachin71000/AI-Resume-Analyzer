import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAnalysis } from '../services/api';
import type { AnalysisResponse } from '../types';
import ResultsPage from './ResultsPage';
import { AlertCircle, ArrowLeft } from 'lucide-react';

export default function AnalysisDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      getAnalysis(id)
        .then(res => setData(res))
        .catch(err => setError(err.response?.data?.error || err.message))
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) return (
    <div className="py-20 flex flex-col items-center justify-center space-y-4">
      <div className="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin" />
      <p className="text-slate-400 font-medium">Loading analysis...</p>
    </div>
  );

  if (error) return (
    <div className="max-w-2xl mx-auto py-20 text-center space-y-6">
      <div className="bg-danger/10 text-danger p-4 rounded-xl border border-danger/20 font-medium flex items-center justify-center gap-2">
        <AlertCircle className="w-5 h-5" /> {error}
      </div>
      <button 
        className="px-6 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 transition-colors font-medium text-sm inline-flex items-center gap-2"
        onClick={() => navigate('/history')}
      >
        <ArrowLeft className="w-4 h-4" /> Back to History
      </button>
    </div>
  );

  if (!data) return null;

  return <ResultsPage injectedData={data} />;
}

