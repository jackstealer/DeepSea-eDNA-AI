import React from 'react';
import { X, Book, Zap, Database, Brain, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface DocumentationProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Documentation: React.FC<DocumentationProps> = ({ isOpen, onClose }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[1000]"
          />
          
          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="fixed inset-4 md:inset-10 lg:inset-20 z-[1001] flex items-center justify-center"
          >
            <div className="glass-card border border-yellow-500/30 rounded-2xl w-full h-full max-w-6xl overflow-hidden flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-purple-500/30">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-yellow-500/10 rounded-lg">
                    <Book className="h-6 w-6 text-yellow-400" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">Documentation</h2>
                    <p className="text-sm text-gray-400">DeepSea eDNA AI Platform</p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 glass-card border border-red-500/30 rounded-lg hover:border-red-500/50 transition-all"
                >
                  <X className="h-6 w-6 text-red-400" />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Overview */}
                <section>
                  <h3 className="text-xl font-semibold text-yellow-400 mb-3 flex items-center gap-2">
                    <Zap className="h-5 w-5" />
                    Overview
                  </h3>
                  <p className="text-gray-300 leading-relaxed">
                    DeepSea eDNA AI is an advanced artificial intelligence platform for analyzing environmental DNA (eDNA) 
                    from marine ecosystems. Using state-of-the-art deep learning models, the platform identifies taxonomic 
                    classifications with 99.9% accuracy and discovers novel taxa through unsupervised learning.
                  </p>
                </section>

                {/* Features */}
                <section>
                  <h3 className="text-xl font-semibold text-purple-400 mb-3 flex items-center gap-2">
                    <Brain className="h-5 w-5" />
                    Key Features
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { title: 'Deep Learning Classification', desc: 'CNN + Attention architecture with 1.28M parameters' },
                      { title: 'Novel Taxa Discovery', desc: 'Autoencoder-based anomaly detection for new species' },
                      { title: 'Real-time Processing', desc: 'GPU-accelerated analysis in 2-5 minutes per sample' },
                      { title: 'High Accuracy', desc: '99.9% classification rate on marine sequences' },
                      { title: 'Multi-format Support', desc: 'FASTA, FASTQ, FA, FQ, FAS file formats' },
                      { title: 'Comprehensive Export', desc: 'JSON, CSV, Excel formats with full metadata' }
                    ].map((feature, i) => (
                      <div key={i} className="glass-card p-4 border border-blue-500/20">
                        <div className="flex items-start gap-2">
                          <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <h4 className="font-semibold text-white">{feature.title}</h4>
                            <p className="text-sm text-gray-400">{feature.desc}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* How to Use */}
                <section>
                  <h3 className="text-xl font-semibold text-green-400 mb-3 flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    How to Use
                  </h3>
                  <div className="space-y-4">
                    <div className="glass-card p-4 border border-yellow-500/20">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center flex-shrink-0">
                          <span className="text-yellow-400 font-bold">1</span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-white mb-1">Upload eDNA Files</h4>
                          <p className="text-sm text-gray-400">
                            Click "Start Analysis" and upload your eDNA sequence files in FASTA or FASTQ format. 
                            You can upload multiple files at once.
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="glass-card p-4 border border-purple-500/20">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                          <span className="text-purple-400 font-bold">2</span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-white mb-1">AI Processing</h4>
                          <p className="text-sm text-gray-400">
                            The AI pipeline processes your sequences through quality filtering, feature extraction, 
                            deep learning classification, and clustering analysis.
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="glass-card p-4 border border-blue-500/20">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                          <span className="text-blue-400 font-bold">3</span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-white mb-1">View Results</h4>
                          <p className="text-sm text-gray-400">
                            Explore taxonomic classifications, abundance data, diversity metrics, and novel taxa discoveries. 
                            Export results in your preferred format.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>

                {/* Technical Specifications */}
                <section>
                  <h3 className="text-xl font-semibold text-orange-400 mb-3">Technical Specifications</h3>
                  <div className="glass-card p-4 border border-orange-500/20">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <h4 className="font-semibold text-white mb-2">Model Architecture</h4>
                        <ul className="space-y-1 text-gray-400">
                          <li>• CNN + Attention mechanism</li>
                          <li>• 1.28M parameters</li>
                          <li>• PyTorch framework</li>
                          <li>• GPU-accelerated (CUDA)</li>
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold text-white mb-2">Training Data</h4>
                        <ul className="space-y-1 text-gray-400">
                          <li>• 4,000 NCBI sequences</li>
                          <li>• 8 taxonomic classes</li>
                          <li>• Marine organisms focus</li>
                          <li>• 99.875% training accuracy</li>
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold text-white mb-2">Clustering</h4>
                        <ul className="space-y-1 text-gray-400">
                          <li>• UMAP dimensionality reduction</li>
                          <li>• DBSCAN clustering</li>
                          <li>• Novel taxa detection</li>
                          <li>• Diversity metrics</li>
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold text-white mb-2">Performance</h4>
                        <ul className="space-y-1 text-gray-400">
                          <li>• 2-5 min per sample</li>
                          <li>• Real-time processing</li>
                          <li>• Batch support</li>
                          <li>• Multi-format export</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </section>

                {/* Support */}
                <section>
                  <h3 className="text-xl font-semibold text-pink-400 mb-3">Support & Contact</h3>
                  <div className="glass-card p-4 border border-pink-500/20">
                    <p className="text-gray-300 mb-3">
                      For technical support, feature requests, or bug reports, please contact our team:
                    </p>
                    <div className="space-y-2 text-sm">
                      <p className="text-gray-400">
                        <span className="text-white font-semibold">Email:</span>{' '}
                        <a 
                          href="mailto:jackstealer690@gmail.com" 
                          className="text-yellow-400 hover:text-yellow-300 transition-colors"
                        >
                          jackstealer690@gmail.com
                        </a>
                      </p>
                      <p className="text-gray-400">
                        <span className="text-white font-semibold">GitHub:</span>{' '}
                        <a 
                          href="https://github.com/jackstealer" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-yellow-400 hover:text-yellow-300 transition-colors"
                        >
                          github.com/jackstealer
                        </a>
                      </p>
                      <p className="text-gray-400">
                        <span className="text-white font-semibold">Version:</span> v2.1.0 (Neural Engine)
                      </p>
                    </div>
                  </div>
                </section>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
