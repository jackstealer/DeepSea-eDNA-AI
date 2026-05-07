import React, { useState } from 'react';
import { BarChart3, TrendingUp, Eye, Download, Layers, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

interface TaxonomicData {
  name: string;
  abundance: number;
  confidence: number;
  isNovel: boolean;
}

interface DepthProfile {
  depth: number;
  diversity: number;
  abundance: number;
}

interface ResultsData {
  totalSequences: number;
  identifiedTaxa: number;
  novelTaxa: number;
  shannonDiversity: string;
  simpsonDiversity: string;
  taxonomicData: TaxonomicData[];
  depthProfile: DepthProfile[];
}

interface ResultsVisualizationProps {
  results: ResultsData;
}

export const ResultsVisualization: React.FC<ResultsVisualizationProps> = ({ results }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const maxAbundance = Math.max(...results.taxonomicData.map(d => d.abundance));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card overflow-hidden"
    >
      <div className="border-b border-purple-500/30">
        <nav className="flex space-x-2 px-6 overflow-x-auto" aria-label="Tabs">
          {[
            { id: 'overview', name: 'Overview', icon: BarChart3 },
            { id: 'taxonomy', name: 'Taxonomy', icon: Layers },
            { id: 'novel', name: 'Novel Taxa', icon: Eye },
            { id: 'depth', name: 'Depth Profile', icon: TrendingUp }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-4 px-4 border-b-2 font-medium text-sm whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'border-yellow-500 text-yellow-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-purple-500/50'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Total Sequences', value: results.totalSequences.toLocaleString(), color: 'blue', icon: Sparkles },
                { label: 'Identified Taxa', value: results.identifiedTaxa, color: 'green', icon: Layers },
                { label: 'Novel Taxa', value: results.novelTaxa, color: 'purple', icon: Eye },
                { label: 'Shannon Diversity', value: results.shannonDiversity, color: 'orange', icon: TrendingUp }
              ].map((stat, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className={`glass-card p-4 border-${stat.color}-500/30 hover:border-${stat.color}-500/50 transition-all`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-gray-400">{stat.label}</h3>
                    <stat.icon className={`h-5 w-5 text-${stat.color}-400`} />
                  </div>
                  <p className={`text-3xl font-bold text-${stat.color}-400`}>{stat.value}</p>
                </motion.div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="glass-card p-4">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-yellow-400" />
                  Taxonomic Abundance
                </h3>
                <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
                  {results.taxonomicData.map((taxon, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-white">{taxon.name}</span>
                          {taxon.isNovel && (
                            <span className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">
                              Novel
                            </span>
                          )}
                        </div>
                        <span className="text-sm text-gray-400">{taxon.abundance}</span>
                      </div>
                      <div className="relative w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                        <motion.div 
                          className="absolute inset-y-0 left-0 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${(taxon.abundance / maxAbundance) * 100}%` }}
                          transition={{ duration: 0.5, delay: index * 0.05 }}
                        />
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              <div className="glass-card p-4">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-400" />
                  Diversity Metrics
                </h3>
                <div className="space-y-6">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-300">Shannon Diversity</span>
                      <span className="text-lg font-bold text-green-400">{results.shannonDiversity}</span>
                    </div>
                    <div className="relative w-full h-3 bg-gray-800 rounded-full overflow-hidden">
                      <motion.div 
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${(parseFloat(results.shannonDiversity) / 4) * 100}%` }}
                        transition={{ duration: 1 }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-300">Simpson Diversity</span>
                      <span className="text-lg font-bold text-blue-400">{results.simpsonDiversity}</span>
                    </div>
                    <div className="relative w-full h-3 bg-gray-800 rounded-full overflow-hidden">
                      <motion.div 
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${parseFloat(results.simpsonDiversity) * 100}%` }}
                        transition={{ duration: 1, delay: 0.2 }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'taxonomy' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-white">Taxonomic Classification Results</h3>
              <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-gray-900 font-semibold rounded-lg hover:shadow-lg hover:shadow-yellow-500/50 transition-all">
                <Download className="h-4 w-4" />
                <span>Export Data</span>
              </button>
            </div>
            <div className="glass-card overflow-hidden">
              <table className="min-w-full">
                <thead className="bg-white/5 border-b border-purple-500/30">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-300 uppercase">Taxon</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-300 uppercase">Abundance</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-300 uppercase">Confidence</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-300 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-purple-500/20">
                  {results.taxonomicData.map((taxon, index) => (
                    <motion.tr
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                      className="hover:bg-white/5 transition-colors"
                    >
                      <td className="px-4 py-3 text-sm font-medium text-white">{taxon.name}</td>
                      <td className="px-4 py-3 text-sm text-gray-300">{taxon.abundance.toLocaleString()}</td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center space-x-2">
                          <div className="w-16 h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                taxon.confidence > 0.8 ? 'bg-green-500' :
                                taxon.confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${taxon.confidence * 100}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-400">{(taxon.confidence * 100).toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {taxon.isNovel ? (
                          <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">
                            Novel
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs bg-green-500/20 text-green-300 rounded border border-green-500/30">
                            Known
                          </span>
                        )}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'novel' && (
          <div className="space-y-6">
            <div className="text-center py-8 glass-card">
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Eye className="mx-auto h-12 w-12 text-purple-400 mb-4" />
              </motion.div>
              <h3 className="text-xl font-semibold text-white mb-2">Novel Taxa Discovery</h3>
              <p className="text-gray-400">
                {results.novelTaxa} potentially new species discovered through unsupervised learning
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.taxonomicData.filter(t => t.isNovel).map((taxon, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="glass-card p-4 border-2 border-purple-500/30 hover:border-purple-500/50 transition-all"
                >
                  <h4 className="font-semibold text-purple-300 mb-2">Novel Taxon {index + 1}</h4>
                  <p className="text-sm text-gray-400 mb-3">Closest match: {taxon.name}</p>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Abundance:</span>
                      <span className="font-medium text-white">{taxon.abundance}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Similarity:</span>
                      <span className="font-medium text-white">{(taxon.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                  <button className="mt-3 w-full px-3 py-2 bg-purple-500/20 text-purple-300 font-medium rounded-lg hover:bg-purple-500/30 border border-purple-500/30 transition-all">
                    View Details
                  </button>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'depth' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-400" />
              Depth Distribution Analysis
            </h3>
            <div className="glass-card p-4">
              <div className="space-y-4">
                {results.depthProfile.map((profile, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-4"
                  >
                    <div className="w-16 text-sm font-semibold text-yellow-400">
                      {profile.depth}m
                    </div>
                    <div className="flex-1 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Diversity Index</span>
                        <span className="text-white font-medium">{profile.diversity.toFixed(2)}</span>
                      </div>
                      <div className="relative w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                        <motion.div 
                          className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${(profile.diversity / 4) * 100}%` }}
                          transition={{ duration: 0.5, delay: index * 0.1 }}
                        />
                      </div>
                    </div>
                    <div className="flex-1 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Abundance</span>
                        <span className="text-white font-medium">{profile.abundance.toLocaleString()}</span>
                      </div>
                      <div className="relative w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                        <motion.div 
                          className="absolute inset-y-0 left-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${(profile.abundance / 11000) * 100}%` }}
                          transition={{ duration: 0.5, delay: index * 0.1 }}
                        />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};
