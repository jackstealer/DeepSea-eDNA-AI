import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { FileUpload } from './components/FileUpload';
import { ProcessingPipeline } from './components/ProcessingPipeline';
import { ResultsVisualization } from './components/ResultsVisualization';
import HeroSection from './components/HeroSection';
import SciFiBackground from './components/SciFiBackground';
import { Footer } from './components/Footer';
import { Toast, ToastType } from './components/Toast';
import { Documentation } from './components/Documentation';
import { Play, RefreshCw, Zap, Cpu, Database, Brain } from 'lucide-react';
import { motion } from 'framer-motion';

function App() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [showHero, setShowHero] = useState(true);
  const [showDocs, setShowDocs] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: ToastType; visible: boolean }>({
    message: '',
    type: 'info',
    visible: false
  });

  // Listen for documentation open event from Footer
  useEffect(() => {
    const handleOpenDocumentation = () => {
      setShowDocs(true);
    };

    window.addEventListener('openDocumentation', handleOpenDocumentation);

    return () => {
      window.removeEventListener('openDocumentation', handleOpenDocumentation);
    };
  }, []);

  const showToast = (message: string, type: ToastType) => {
    setToast({ message, type, visible: true });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, visible: false }));
  };

  const handleFilesSelected = (files: File[]) => {
    setSelectedFiles(files);
    setResults(null);
    if (files.length > 0) {
      showToast(`${files.length} file(s) selected successfully`, 'success');
    }
  };

  const startProcessing = () => {
    if (selectedFiles.length === 0) {
      showToast('Please select at least one file to analyze', 'warning');
      return;
    }
    setIsProcessing(true);
    setResults(null);
    showToast('Analysis started. This may take a few minutes...', 'info');
  };

  const handleProcessingComplete = (processingResults: any) => {
    setResults(processingResults);
    setIsProcessing(false);
    showToast('Analysis completed successfully!', 'success');
  };

  const resetAnalysis = () => {
    setSelectedFiles([]);
    setResults(null);
    setIsProcessing(false);
    showToast('Analysis reset', 'info');
  };

  const handleStartAnalysis = () => {
    setShowHero(false);
  };

  const handleBackToHome = () => {
    setShowHero(true);
    setSelectedFiles([]);
    setResults(null);
    setIsProcessing(false);
  };

  const acceptedFormats = ['.fasta', '.fastq', '.fa', '.fq', '.fas'];

  if (showHero) {
    return (
      <>
        <Toast 
          message={toast.message} 
          type={toast.type} 
          isVisible={toast.visible} 
          onClose={hideToast} 
        />
        <Documentation isOpen={showDocs} onClose={() => setShowDocs(false)} />
        <div className="min-h-screen relative flex flex-col">
          <SciFiBackground />
          <div className="relative flex-1" style={{ zIndex: 100 }}>
            <Header />
            <HeroSection onStartAnalysis={handleStartAnalysis} />
          </div>
          <div className="relative" style={{ zIndex: 100 }}>
            <Footer />
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Toast 
        message={toast.message} 
        type={toast.type} 
        isVisible={toast.visible} 
        onClose={hideToast} 
      />
      <Documentation isOpen={showDocs} onClose={() => setShowDocs(false)} />
      <div className="min-h-screen relative flex flex-col">
        <SciFiBackground />
        <div className="relative flex-1" style={{ zIndex: 100 }}>
          <Header showBackButton={true} onBackClick={handleBackToHome} />
          
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Introduction Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 mb-8 border border-yellow-500/30"
        >
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-yellow-500/10 rounded-lg">
              <Brain className="h-6 w-6 text-yellow-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-white mb-2">
                AI-Driven Deep-Sea eDNA Analysis Pipeline
              </h2>
              <p className="text-gray-300 mb-4">
                Our advanced pipeline addresses critical challenges in marine biodiversity research by minimizing 
                reliance on incomplete reference databases and dramatically reducing computational time through 
                optimized deep learning workflows.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="glass-card p-3 border border-blue-500/30 hover:border-blue-500/50 transition-all">
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="h-5 w-5 text-blue-400" />
                    <h3 className="font-semibold text-blue-300">Deep Learning Classification</h3>
                  </div>
                  <p className="text-sm text-gray-400">Neural networks for direct sequence analysis</p>
                </div>
                <div className="glass-card p-3 border border-purple-500/30 hover:border-purple-500/50 transition-all">
                  <div className="flex items-center gap-2 mb-2">
                    <Database className="h-5 w-5 text-purple-400" />
                    <h3 className="font-semibold text-purple-300">Novel Taxa Discovery</h3>
                  </div>
                  <p className="text-sm text-gray-400">Unsupervised learning identifies new species</p>
                </div>
                <div className="glass-card p-3 border border-green-500/30 hover:border-green-500/50 transition-all">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="h-5 w-5 text-green-400" />
                    <h3 className="font-semibold text-green-300">Real-time Analysis</h3>
                  </div>
                  <p className="text-sm text-gray-400">Optimized workflows for rapid results</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - File Upload & Controls */}
          <div className="lg:col-span-1 space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass-card p-6"
            >
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <Zap className="h-6 w-6 text-yellow-400" />
                Upload eDNA Data
              </h2>
              <FileUpload
                onFilesSelected={handleFilesSelected}
                acceptedFormats={acceptedFormats}
              />
              
              <div className="mt-6 space-y-3">
                <button
                  onClick={startProcessing}
                  disabled={selectedFiles.length === 0 || isProcessing}
                  className={`w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-semibold transition-all duration-300 ${
                    selectedFiles.length === 0 || isProcessing
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-yellow-500 to-orange-500 text-gray-900 hover:shadow-2xl hover:shadow-yellow-500/50 transform hover:scale-105'
                  }`}
                >
                  {isProcessing ? (
                    <>
                      <RefreshCw className="h-5 w-5 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5" />
                      <span>Start AI Analysis</span>
                    </>
                  )}
                </button>

                {(results || isProcessing) && (
                  <button
                    onClick={resetAnalysis}
                    disabled={isProcessing}
                    className="w-full px-4 py-2 glass-card border border-purple-500/30 text-gray-300 rounded-lg hover:border-purple-500/50 disabled:opacity-50 transition-all"
                  >
                    Reset Analysis
                  </button>
                )}
              </div>
            </motion.div>

            {/* Analysis Parameters */}
            {selectedFiles.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="glass-card p-6"
              >
                <h3 className="text-lg font-semibold text-white mb-4">Analysis Parameters</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Files Selected:</span>
                    <span className="font-medium text-yellow-400">{selectedFiles.length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Total Size:</span>
                    <span className="font-medium text-yellow-400">
                      {(selectedFiles.reduce((sum, file) => sum + file.size, 0) / (1024 * 1024)).toFixed(2)} MB
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">AI Model:</span>
                    <span className="font-medium text-purple-400">DeepTaxa-v2.1</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Clustering:</span>
                    <span className="font-medium text-purple-400">UMAP + DBSCAN</span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Right Column - Processing & Results */}
          <div className="lg:col-span-2">
            {!isProcessing && !results ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-12 text-center"
              >
                <div className="max-w-md mx-auto">
                  <div className="mb-6">
                    <div className="flex justify-center space-x-2 mb-4">
                      <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                      <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-4">
                    Ready for Deep-Sea Discovery
                  </h3>
                  <p className="text-gray-400 mb-6">
                    Upload your eDNA sequence files to begin AI-powered taxonomic classification 
                    and biodiversity analysis. Our pipeline will identify both known and novel taxa 
                    while providing abundance estimates and ecological insights.
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="glass-card p-3 border border-blue-500/30">
                      <p className="font-semibold text-blue-300">Fast Processing</p>
                      <p className="text-gray-400 text-xs">~2-5 min per sample</p>
                    </div>
                    <div className="glass-card p-3 border border-green-500/30">
                      <p className="font-semibold text-green-300">High Accuracy</p>
                      <p className="text-gray-400 text-xs">99%+ classification rate</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ) : (
              <div className="space-y-6">
                <ProcessingPipeline
                  isRunning={isProcessing}
                  onComplete={handleProcessingComplete}
                  files={selectedFiles}
                />

                {results && (
                  <ResultsVisualization results={results} />
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-12 glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Technical Specifications</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-yellow-400 mb-1">Deep Learning Engine</h4>
              <p className="text-gray-400 text-xs">Transformer-based sequence embeddings with attention mechanisms</p>
            </div>
            <div>
              <h4 className="font-medium text-purple-400 mb-1">Clustering Algorithm</h4>
              <p className="text-gray-400 text-xs">UMAP dimensionality reduction with DBSCAN clustering</p>
            </div>
            <div>
              <h4 className="font-medium text-blue-400 mb-1">Classification Model</h4>
              <p className="text-gray-400 text-xs">Ensemble neural networks trained on marine eDNA datasets</p>
            </div>
            <div>
              <h4 className="font-medium text-green-400 mb-1">Database Independence</h4>
              <p className="text-gray-400 text-xs">Minimal reliance on reference databases through learned representations</p>
            </div>
          </div>
        </motion.div>
      </main>
      <div className="relative" style={{ zIndex: 100 }}>
        <Footer />
      </div>
      </div>
    </div>
    </>
  );
}

export default App;
