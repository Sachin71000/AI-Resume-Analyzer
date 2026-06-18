import axios from 'axios';
import type { AnalysisResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE,
});

export const analyzeResume = async (file: File, jdText: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('resume', file);
  formData.append('jd_text', jdText);

  const response = await apiClient.post<AnalysisResponse>('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const improveResume = async (file: File, jdText: string, parentId: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('resume', file);
  formData.append('jd_text', jdText);
  formData.append('parent_id', parentId);

  const response = await apiClient.post<AnalysisResponse>('/analyze/improve', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getHistory = async (page = 1, limit = 10, sort = 'date', search = '') => {
  const response = await apiClient.get('/history', {
    params: { page, limit, sort, search }
  });
  return response.data;
};

export const getAnalysis = async (id: string): Promise<AnalysisResponse> => {
  const response = await apiClient.get(`/analysis/${id}`);
  return response.data;
};

export const deleteAnalysis = async (id: string) => {
  const response = await apiClient.delete(`/analysis/${id}`);
  return response.data;
};

export const deleteAnalyses = async (ids: string[]) => {
  const response = await apiClient.delete('/analyses', {
    data: { ids }
  });
  return response.data;
};

export const updateLabel = async (id: string, label: string) => {
  const response = await apiClient.patch(`/analysis/${id}/label`, { label });
  return response.data;
};

export const compareAnalyses = async (ids: string[]) => {
  const response = await apiClient.post('/compare', { analysis_ids: ids });
  return response.data;
};

export const downloadPDF = (id: string) => {
  window.open(`${API_BASE}/export/${id}`, '_blank');
};

export const startInterview = async (
  analysisId: string,
  difficulty = 'medium',
  questionCount = 10,
  questionTypes = ['skill', 'project', 'behavioral', 'role'],
  targetRole?: string
): Promise<StartInterviewResponse> => {
  const response = await apiClient.post<StartInterviewResponse>('/interview/start', {
    analysis_id: analysisId,
    difficulty,
    question_count: questionCount,
    question_types: questionTypes,
    target_role: targetRole,
  });
  return response.data;
};

export const submitAnswer = async (
  sessionId: string,
  answer: string,
  timeTakenSeconds?: number
): Promise<SubmitAnswerResponse> => {
  const response = await apiClient.post<SubmitAnswerResponse>(`/interview/${sessionId}/answer`, {
    answer,
    time_taken_seconds: timeTakenSeconds,
  });
  return response.data;
};

export const completeInterview = async (sessionId: string): Promise<InterviewResultsResponse> => {
  const response = await apiClient.post<InterviewResultsResponse>(`/interview/${sessionId}/complete`);
  return response.data;
};

export const getInterviewResults = async (sessionId: string): Promise<InterviewResultsResponse> => {
  const response = await apiClient.get<InterviewResultsResponse>(`/interview/${sessionId}/results`);
  return response.data;
};

export const getInterviewHistory = async (analysisId?: string): Promise<InterviewHistoryResponse> => {
  const response = await apiClient.get<InterviewHistoryResponse>('/interview/history', {
    params: { analysis_id: analysisId },
  });
  return response.data;
};

export const deleteInterviewSession = async (sessionId: string) => {
  const response = await apiClient.delete(`/interview/${sessionId}`);
  return response.data;
};

// Import necessary types from index.ts
import type {
  StartInterviewResponse,
  SubmitAnswerResponse,
  InterviewResultsResponse,
  InterviewHistoryResponse
} from '../types';
