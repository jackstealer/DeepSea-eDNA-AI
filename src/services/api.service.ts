// API Service for backend communication
import APP_CONFIG from '../config/app.config';

export interface AnalysisRequest {
  files: File[];
  model?: string;
  clustering?: string;
  parameters?: Record<string, any>;
}

export interface AnalysisResponse {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress?: number;
  currentStep?: string;
  results?: any;
  error?: string;
}

export interface AnalysisResults {
  totalSequences: number;
  identifiedTaxa: number;
  novelTaxa: number;
  shannonDiversity: number;
  simpsonDiversity: number;
  taxonomicData: TaxonomicData[];
  depthProfile?: DepthProfile[];
  metadata: {
    processingTime: number;
    model: string;
    clustering: string;
    timestamp: string;
  };
}

export interface TaxonomicData {
  name: string;
  abundance: number;
  confidence: number;
  isNovel: boolean;
  taxonomicRank?: string;
  lineage?: string[];
}

export interface DepthProfile {
  depth: number;
  diversity: number;
  abundance: number;
}

class ApiService {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = APP_CONFIG.api.baseUrl;
    this.timeout = APP_CONFIG.api.timeout;
  }

  /**
   * Upload files and start analysis
   */
  async startAnalysis(request: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      // Step 1: Upload files
      const formData = new FormData();
      request.files.forEach((file) => {
        formData.append('files', file);
      });

      const uploadResponse = await fetch(`${this.baseUrl}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        const error = await uploadResponse.json();
        throw new Error(error.detail || `Upload failed: ${uploadResponse.status}`);
      }

      const uploadData = await uploadResponse.json();
      const filePaths = uploadData.file_paths;

      // Step 2: Start analysis with uploaded file paths
      const analysisPayload = {
        file_paths: filePaths,
        model: request.model || APP_CONFIG.analysis.defaultModel,
        clustering: request.clustering || APP_CONFIG.analysis.defaultClustering,
        parameters: request.parameters || {},
      };

      const analysisResponse = await fetch(`${this.baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisPayload),
        signal: AbortSignal.timeout(this.timeout),
      });

      if (!analysisResponse.ok) {
        const error = await analysisResponse.json();
        throw new Error(error.detail || `Analysis failed: ${analysisResponse.status}`);
      }

      return await analysisResponse.json();
    } catch (error) {
      console.error('Analysis start failed:', error);
      throw error;
    }
  }

  /**
   * Poll for analysis status and results
   */
  async getAnalysisStatus(jobId: string): Promise<AnalysisResponse> {
    try {
      const response = await fetch(
        `${this.baseUrl}${APP_CONFIG.api.endpoints.results}/${jobId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Status check failed:', error);
      throw error;
    }
  }

  /**
   * Export results in specified format
   */
  async exportResults(
    jobId: string,
    format: string = APP_CONFIG.export.defaultFormat
  ): Promise<Blob> {
    try {
      const response = await fetch(
        `${this.baseUrl}${APP_CONFIG.api.endpoints.export}/${jobId}?format=${format}`,
        {
          method: 'GET',
        }
      );

      if (!response.ok) {
        throw new Error(`Export failed: ${response.status} ${response.statusText}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('Export failed:', error);
      throw error;
    }
  }

  /**
   * Download exported file
   */
  downloadFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  /**
   * Validate file before upload
   */
  validateFile(file: File): { valid: boolean; error?: string } {
    // Check file size
    if (file.size > APP_CONFIG.upload.maxFileSize) {
      return {
        valid: false,
        error: `File size exceeds maximum allowed size of ${APP_CONFIG.upload.maxFileSize / (1024 * 1024)}MB`,
      };
    }

    // Check file extension
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!APP_CONFIG.upload.acceptedFormats.includes(extension)) {
      return {
        valid: false,
        error: `File format not supported. Accepted formats: ${APP_CONFIG.upload.acceptedFormats.join(', ')}`,
      };
    }

    return { valid: true };
  }
}

export const apiService = new ApiService();
export default apiService;
