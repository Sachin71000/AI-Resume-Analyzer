import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, MicOff, FastForward, Clock, 
  Terminal, User, ChevronRight, Award
} from 'lucide-react';
import { submitAnswer, completeInterview } from '../services/api';
import type { InterviewQuestion } from '../types';

export default function InterviewPage() {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  // Route state fallbacks
  const totalQuestions = location.state?.totalQuestions || 10;
  const targetRole = location.state?.targetRole || 'Software Engineer';
  // Core state
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [answerText, setAnswerText] = useState<string>('');
  const [questionIndex, setQuestionIndex] = useState<number>(1);
  const [timeRemaining, setTimeRemaining] = useState<number>(180); // 3 minutes standard per Q
  const [isLastQuestion, setIsLastQuestion] = useState<boolean>(false);
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);
  const [evalProgressText, setEvalProgressText] = useState<string>('Uploading transcript...');
  const [loadingSubmit, setLoadingSubmit] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Timer Ref
  const timerRef = useRef<any>(null);

  // Voice Recognition States & Refs
  const [isListening, setIsListening] = useState<boolean>(false);
  const recognitionRef = useRef<any>(null);

  // Load first question on load
  useEffect(() => {
    if (location.state?.session?.first_question) {
      setCurrentQuestion(location.state.session.first_question);
      setQuestionIndex(1);
    } else {
      // If we directly navigated, reload session question
      fetchQuestionDirectly();
    }
  }, [sessionId, location.state]);

  // Handle countdown timer
  useEffect(() => {
    if (!currentQuestion || isEvaluating || loadingSubmit) return;

    setTimeRemaining(180); // reset timer to 3 mins for new question
    
    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          // Timer expired! Auto submit current answer
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [currentQuestion]);

  // Web Speech API Voice Recognition setup
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = 'en-US';

      rec.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + ' ';
          }
        }
        if (finalTranscript) {
          setAnswerText(prev => (prev.trim() + ' ' + finalTranscript.trim()).trim());
        }
      };

      rec.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
    }
  }, []);

  const fetchQuestionDirectly = async () => {
    // If state wasn't passed, we can complete and evaluate since session was likely active or lost
    // For safety, let's suggest navigating back to setup if session details aren't found
    setError("Could not restore session state. Please navigate from resume results.");
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Voice speech-to-text recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error("Failed to start voice listener:", err);
      }
    }
  };

  const handleAutoSubmit = () => {
    handleSubmit(true);
  };

  const handleSubmit = async (isTimeExpired = false) => {
    if (isTimeExpired) {
      // Intended for auto-submit behavior on timer end
      console.log("Submitting automatically due to timer expiration.");
    }
    if (!sessionId || !currentQuestion) return;

    // Stop listening if active
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }

    setLoadingSubmit(true);
    setError(null);

    const timeTaken = 180 - timeRemaining;

    try {
      const res = await submitAnswer(
        sessionId,
        answerText,
        timeTaken
      );

      setAnswerText(''); // clear text area

      if (res.is_last || !res.next_question) {
        // Trigger batch evaluation
        triggerBatchEvaluation();
      } else {
        // Load next question
        setCurrentQuestion(res.next_question);
        setQuestionIndex(res.progress.answered + 1);
        setIsLastQuestion(res.progress.answered + 1 === totalQuestions);
      }
    } catch (err: any) {
      console.error("Failed to submit answer:", err);
      setError(err.response?.data?.error || "Failed to record your answer. Please try again.");
    } finally {
      setLoadingSubmit(false);
    }
  };

  const handleSkip = () => {
    setAnswerText("Gave no answer.");
    // Wait a brief tick for state to register or just submit immediately
    setTimeout(() => {
      handleSubmit();
    }, 100);
  };

  const triggerBatchEvaluation = async () => {
    if (!sessionId) return;
    
    setIsEvaluating(true);
    if (timerRef.current) clearInterval(timerRef.current);

    // Progress updates to feel highly advanced and alive!
    const stages = [
      'Compiling interview transcripts...',
      'Performing TF-IDF cosine similarity analysis...',
      'Running keyword density and coverage counts...',
      'Synthesizing deep semantic assessments using Gemini...',
      'Scoring communication fluency and filler counts...',
      'Generating personalized engineering roadmap...',
      'Finalizing scores...'
    ];

    let stageIdx = 0;
    const progressTimer = setInterval(() => {
      if (stageIdx < stages.length - 1) {
        stageIdx++;
        setEvalProgressText(stages[stageIdx]);
      }
    }, 1800);

    try {
      const res = await completeInterview(sessionId);
      clearInterval(progressTimer);
      // Navigate to results
      navigate(`/interview/${sessionId}/results`, { state: { results: res } });
    } catch (err: any) {
      console.error("Batch evaluation failed:", err);
      clearInterval(progressTimer);
      setIsEvaluating(false);
      setError(err.response?.data?.error || "Grading calculations failed. Please try again.");
    }
  };

  // Helper formatting for timer
  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${mins}:${remainingSecs < 10 ? '0' : ''}${remainingSecs}`;
  };

  const getProgressPercentage = () => {
    return (questionIndex / totalQuestions) * 100;
  };

  if (isEvaluating) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-2xl z-50 flex items-center justify-center flex-col px-6">
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-surface/50 border border-white/10 rounded-3xl p-8 max-w-md w-full text-center flex flex-col items-center shadow-2xl relative"
        >
          <div className="absolute top-0 w-32 h-1 bg-brand rounded-full animate-pulse" />
          
          <div className="w-16 h-16 rounded-full bg-brand/10 border border-brand/20 flex items-center justify-center text-brand mb-6 animate-spin">
            <Clock className="w-8 h-8" />
          </div>

          <h2 className="text-xl font-bold text-white mb-2">Assembling Panel Evaluation</h2>
          <p className="text-slate-400 text-sm mb-6 leading-relaxed">
            Please wait while the AI Interview Coach grades your responses across all dimensions.
          </p>

          <div className="w-full bg-black/30 rounded-full h-2 mb-4 overflow-hidden border border-white/5">
            <motion.div 
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{ duration: 12 }}
              className="bg-gradient-to-r from-brand to-brandLight h-full"
            />
          </div>

          <span className="text-xs text-brandLight font-medium uppercase tracking-wider animate-pulse">
            {evalProgressText}
          </span>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto w-full flex flex-col space-y-6">
      
      {/* Top Indicators: Index + Timer */}
      <div className="flex justify-between items-center bg-surface/40 backdrop-blur-md p-4 rounded-2xl border border-white/5">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            {targetRole} Interview
          </span>
          <span className="h-4 w-px bg-white/10" />
          <span className="text-sm font-bold text-white">
            Question {questionIndex} of {totalQuestions}
          </span>
        </div>

        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm font-bold transition-colors ${
          timeRemaining < 30 
            ? 'bg-danger/10 border-danger/20 text-danger animate-pulse' 
            : 'bg-black/20 border-white/5 text-slate-300'
        }`}>
          <Clock className="w-4 h-4" />
          {formatTime(timeRemaining)}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden border border-white/5">
        <motion.div 
          animate={{ width: `${getProgressPercentage()}%` }}
          className="bg-brand h-full"
        />
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm">
          {error}
        </div>
      )}

      {/* Question Card */}
      <AnimatePresence mode="wait">
        {currentQuestion && (
          <motion.div
            key={currentQuestion.index}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.3 }}
            className="bg-surface/50 border border-white/5 rounded-3xl p-6 md:p-8 backdrop-blur-xl relative overflow-hidden shadow-xl"
          >
            <div className="absolute top-0 right-0 w-48 h-48 bg-brand/5 rounded-full blur-3xl pointer-events-none" />

            <div className="flex flex-wrap items-center gap-2.5 mb-4">
              <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-brandLight bg-brand/10 border border-brand/20 px-3 py-1 rounded-full">
                <Terminal className="w-3.5 h-3.5" />
                {currentQuestion.category}
              </span>
              <span className="text-xs font-bold uppercase tracking-wider bg-white/5 text-slate-400 border border-white/5 px-3 py-1 rounded-full">
                {currentQuestion.difficulty}
              </span>
            </div>

            <h2 className="text-lg md:text-xl font-bold text-white leading-relaxed">
              {currentQuestion.question}
            </h2>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Answer Inputs */}
      <div className="bg-surface/50 border border-white/5 rounded-3xl p-6 backdrop-blur-xl flex flex-col space-y-4">
        
        <div className="flex justify-between items-center">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <User className="w-3.5 h-3.5" />
            Your Explanation
          </label>
          
          <span className="text-xs font-semibold text-slate-500">
            {answerText.split(/\s+/).filter(Boolean).length} words
          </span>
        </div>

        <div className="relative">
          <textarea
            value={answerText}
            onChange={(e) => setAnswerText(e.target.value)}
            disabled={loadingSubmit}
            placeholder="Structure your thoughts clearly. Use technical terms and outline trade-offs where applicable..."
            className="w-full bg-black/25 border border-white/10 rounded-2xl p-4 min-h-[220px] text-slate-200 focus:outline-none focus:border-brand/40 transition-colors leading-relaxed text-sm placeholder:text-slate-600 focus:ring-1 focus:ring-brand/20"
          />

          {/* Voice Mic Overlay */}
          <div className="absolute right-3 bottom-3 flex items-center gap-2">
            {isListening && (
              <span className="text-xs text-brandLight font-medium animate-pulse hidden md:inline">
                Listening to voice input...
              </span>
            )}
            
            <button
              type="button"
              onClick={toggleListening}
              disabled={loadingSubmit}
              className={`w-10 h-10 rounded-full flex items-center justify-center border transition-all ${
                isListening 
                  ? 'bg-brand text-white border-brandLight shadow-lg shadow-brand/20 animate-pulse' 
                  : 'bg-black/30 border-white/10 text-slate-400 hover:bg-black/55 hover:text-white'
              }`}
              title="Click to speak (speech-to-text)"
            >
              {isListening ? <MicOff className="w-4.5 h-4.5" /> : <Mic className="w-4.5 h-4.5" />}
            </button>
          </div>
        </div>

        {/* Buttons Panel */}
        <div className="flex justify-between items-center pt-2">
          <button
            type="button"
            onClick={handleSkip}
            disabled={loadingSubmit}
            className="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors font-medium text-sm flex items-center gap-2"
          >
            <FastForward className="w-4 h-4" /> Skip Question
          </button>

          <button
            type="button"
            onClick={() => handleSubmit(false)}
            disabled={loadingSubmit}
            className="px-6 py-2.5 rounded-xl bg-brand hover:bg-brandLight text-white font-bold transition-all text-sm flex items-center gap-2 shadow-lg shadow-brand/10"
          >
            {loadingSubmit ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            ) : (
              <>
                {isLastQuestion ? (
                  <>
                    <Award className="w-4 h-4" /> Complete Mock Interview
                  </>
                ) : (
                  <>
                    Next Question <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </>
            )}
          </button>
        </div>

      </div>

    </div>
  );
}
