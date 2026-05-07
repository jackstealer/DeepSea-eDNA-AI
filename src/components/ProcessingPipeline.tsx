import React, { useState, useEffect } from 'react';
import { Play, CheckCircle, Clock, AlertCircle, Activity, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import APP_CONFIG from '../config/app.config';
import apiService from '../services/api.service';

interface PipelineStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  progress: number;
  duration?: number;
}

interface ProcessingPipelineProps {
  isRunning: boolean;
  onComplete: (results: any) => void;
  files: File[];
  model?: string;
  clustering?: string;
}

export const ProcessingPipeline: React.FC<ProcessingPipelineProps> = ({ 
  isRunning, 
  onComplete,
  files,
  model,
  clustering
}) => {
  const [steps, setSteps] = useState<PipelineStep[]>(
    APP_CONFIG.pipeline.steps.map(step => ({
      ...step,
      status: 'pending' as const,
      progress: 0
    }))
  );

  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [totalProgress, setTotalProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isRunning) return;

    const processAnalysis = async () => {
      try {
        setError(null);

        // Use real API service with trained model
        const response = await apiService.startAnalysis({
          files,
          model: model || APP_CONFIG.analysis.defaultModel,
          clustering: clustering || APP_CONFIG.analysis.defaultClustering,
        });

        // Poll for status updates from backend
        const pollInterval = setInterval(async () => {
          try {
            const status = await apiService.getAnalysisStatus(response.jobId);
            
            if (status.progress !== undefined) {
              setTotalProgress(status.progress);
              
              if (status.currentStep) {
                const stepIndex = steps.findIndex(s => s.id === status.currentStep);
                if (stepIndex >= 0) {
                  setCurrentStepIndex(stepIndex);
                  setSteps(prev => prev.map((step, index) => {
                    if (index < stepIndex) {
                      return { ...step, status: 'completed', progress: 100 };
                    } else if (index === stepIndex) {
                      return { ...step, status: 'running', progress: status.progress || 0 };
                    }
                    return step;
                  }));
                }
              }
            }

            if (status.status === 'completed' && status.results) {
              clearInterval(pollInterval);
              onComplete(status.results);
            } else if (status.status === 'failed') {
              clearInterval(pollInterval);
              setError(status.error || 'Analysis failed');
              setSteps(prev => prev.map(step => 
                step.status === 'running' ? { ...step, status: 'error' } : step
              ));
            }
          } catch (err) {
            clearInterval(pollInterval);
            setError('Failed to get analysis status');
            console.error(err);
          }
        }, 2000); // Poll every 2 seconds
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Analysis failed');
        setSteps(prev => prev.map(step => 
          step.status === 'running' ? { ...step, status: 'error' } : step
        ));
      }
    };

    processAnalysis();
  }, [isRunning, files, model, clustering]);

  const getStatusIcon = (status: PipelineStep['status']) => {
    switch (status) {
      case 'running':
        return <Activity className="h-5 w-5 text-yellow-400 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-400" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  if (!isRunning) {
    return (
      <div className="glass-card p-12 text-center">
        <motion.div
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Play className="mx-auto h-16 w-16 text-purple-400 mb-4" />
        </motion.div>
        <h3 className="text-xl font-semibold text-white mb-2">Ready to Process</h3>
        <p className="text-gray-400">Upload files and click start to begin analysis</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6"
    >
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Zap className="h-6 w-6 text-yellow-400" />
            AI Processing Pipeline
          </h3>
          <span className="text-2xl font-bold text-yellow-400">{totalProgress.toFixed(0)}%</span>
        </div>
        
        <div className="relative w-full h-3 bg-gray-800 rounded-full overflow-hidden border border-purple-500/30">
          <motion.div 
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-yellow-500 via-orange-500 to-purple-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${totalProgress}%` }}
            transition={{ duration: 0.5 }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
        </div>
      </div>

      <div className="space-y-3">
        {steps.map((step, index) => (
          <motion.div 
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`relative overflow-hidden rounded-lg p-4 transition-all duration-300 ${
              index === currentStepIndex && isRunning
                ? 'bg-yellow-500/10 border-2 border-yellow-500/50 glow-border'
                : step.status === 'completed'
                ? 'bg-green-500/10 border border-green-500/30'
                : 'bg-white/5 border border-purple-500/20'
            }`}
          >
            {step.status === 'running' && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-yellow-500/10 to-transparent animate-pulse" />
            )}
            
            <div className="relative flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3 flex-1">
                {getStatusIcon(step.status)}
                <div>
                  <h4 className="font-semibold text-white">{step.name}</h4>
                  <p className="text-sm text-gray-400">{step.description}</p>
                </div>
              </div>
              <div className="text-lg font-bold text-yellow-400">
                {step.progress}%
              </div>
            </div>
            
            {step.status === 'running' && (
              <div className="relative w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                <motion.div 
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${step.progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg"
        >
          <p className="text-red-400 text-sm">{error}</p>
        </motion.div>
      )}
    </motion.div>
  );
};
