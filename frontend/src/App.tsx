import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import AnalysisDetailPage from './pages/AnalysisDetailPage';
import ComparePage from './pages/ComparePage';
import InterviewSetupPage from './pages/InterviewSetupPage';
import InterviewPage from './pages/InterviewPage';
import InterviewResultsPage from './pages/InterviewResultsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="results" element={<ResultsPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="analysis/:id" element={<AnalysisDetailPage />} />
          <Route path="compare" element={<ComparePage />} />
          <Route path="interview/setup" element={<InterviewSetupPage />} />
          <Route path="interview/:id" element={<InterviewPage />} />
          <Route path="interview/:id/results" element={<InterviewResultsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
