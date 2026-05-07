// Application Configuration
// This file centralizes all configurable values for easy customization

export const APP_CONFIG = {
  // Application Info
  app: {
    name: 'DeepSea eDNA AI',
    subtitle: 'Advanced Biodiversity Analysis Pipeline',
    version: '2.1.0',
    description: 'AI-Driven Deep-Sea eDNA Analysis Pipeline',
  },

  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:3000',
    timeout: 300000, // 5 minutes for long-running analysis
    endpoints: {
      upload: '/api/upload',
      analyze: '/api/analyze',
      results: '/api/results',
      export: '/api/export',
    },
  },

  // File Upload Configuration
  upload: {
    acceptedFormats: ['.fasta', '.fastq', '.fa', '.fq', '.fas', '.fna'],
    maxFileSize: 500 * 1024 * 1024, // 500MB
    maxFiles: 10,
    allowedMimeTypes: [
      'text/plain',
      'application/octet-stream',
      'text/x-fasta',
    ],
  },

  // Analysis Configuration
  analysis: {
    defaultModel: 'DeepTaxa-v2.1',
    availableModels: [
      { id: 'deeptaxa-v2.1', name: 'DeepTaxa v2.1', description: 'Latest model with improved accuracy' },
      { id: 'deeptaxa-v2.0', name: 'DeepTaxa v2.0', description: 'Stable production model' },
      { id: 'custom', name: 'Custom Model', description: 'Upload your own trained model' },
    ],
    clusteringAlgorithms: [
      { id: 'umap-dbscan', name: 'UMAP + DBSCAN', description: 'Default clustering method' },
      { id: 'tsne-hdbscan', name: 't-SNE + HDBSCAN', description: 'Alternative clustering' },
      { id: 'pca-kmeans', name: 'PCA + K-means', description: 'Fast clustering for large datasets' },
    ],
    defaultClustering: 'UMAP + DBSCAN',
  },

  // Pipeline Steps Configuration
  pipeline: {
    steps: [
      {
        id: 'preprocessing',
        name: 'Data Preprocessing',
        description: 'Quality filtering, adapter removal, and sequence cleaning',
        estimatedTime: 30, // seconds
      },
      {
        id: 'embedding',
        name: 'Deep Learning Embedding',
        description: 'Neural network feature extraction from raw sequences',
        estimatedTime: 120,
      },
      {
        id: 'clustering',
        name: 'Unsupervised Clustering',
        description: 'Identifying sequence clusters and potential novel taxa',
        estimatedTime: 60,
      },
      {
        id: 'classification',
        name: 'AI Classification',
        description: 'Deep learning taxonomy prediction and confidence scoring',
        estimatedTime: 90,
      },
      {
        id: 'abundance',
        name: 'Abundance Estimation',
        description: 'Statistical abundance calculation and normalization',
        estimatedTime: 45,
      },
      {
        id: 'annotation',
        name: 'Functional Annotation',
        description: 'Ecological role prediction and pathway analysis',
        estimatedTime: 60,
      },
    ],
  },

  // Performance Metrics
  metrics: {
    processingTimePerSample: { min: 2, max: 5 }, // minutes
    classificationRate: 0.95, // 95%
    confidenceThreshold: 0.7,
  },

  // Export Configuration
  export: {
    formats: ['csv', 'json', 'xlsx', 'tsv'],
    defaultFormat: 'csv',
  },

  // UI Configuration
  ui: {
    resultsRefreshInterval: 5000, // 5 seconds
    maxRecentAnalyses: 10,
    theme: {
      primaryColor: 'blue',
      secondaryColor: 'teal',
    },
  },

  // Feature Flags
  features: {
    enableRealTimeProcessing: true,
    enableExport: true,
    enableModelSelection: true,
    enableAdvancedSettings: true,
    enableDemoMode: false, // Disabled by default - use real backend
  },
};

export default APP_CONFIG;
