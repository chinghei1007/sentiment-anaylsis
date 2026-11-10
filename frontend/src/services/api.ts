import axios, { AxiosInstance, AxiosError } from 'axios'

// API base URL - can be configured via environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle errors globally
    if (error.response) {
      const { status, data } = error.response
      
      // Log error
      console.error(`API Error ${status}:`, data)
      
      // Reject with error details
      return Promise.reject({
        ...error,
        message: data?.detail || data?.error || 'Request failed',
        status,
      })
    }
    
    return Promise.reject(error)
  }
)

// Type definitions for API responses
export interface SentimentPrediction {
  text: string
  sentiment: 'positive' | 'negative'
  label: number
  confidence?: number
  prob_positive?: number
  prob_negative?: number
}

export interface BatchSentimentResponse {
  predictions: SentimentPrediction[]
  total: number
  processed_at: string
}

export interface TrainingResponse {
  model_type: string
  training_samples: number
  validation_samples: number
  label_distribution: Record<string, number>
  accuracy: number
  confusion_matrix: Record<number, Record<number, number>>
  sample_predictions: Array<Record<string, any>>
  timestamp: string
  model_saved: boolean
  model_path?: string
}

export interface EvaluationResponse {
  accuracy: number
  f1_score: number
  precision: number
  recall: number
  confusion_matrix: Record<number, Record<number, number>>
  total_samples: number
  positive_samples: number
  negative_samples: number
  evaluated_at: string
}

export interface ModelInfo {
  model_type: string
  trained: boolean
  training_date?: string
  accuracy?: number
  f1_score?: number
  path?: string
}

export interface DatasetInfo {
  name: string
  total_samples: number
  positive_samples: number
  negative_samples: number
  neutral_samples: number
  sources: string[]
  columns: string[]
}

export interface HealthResponse {
  status: string
  version: string
  timestamp: string
  spark_available: boolean
  model_loaded: boolean
}

// API Service Functions
export const sentimentApi = {
  // Health check
  health: (): Promise<HealthResponse> => 
    api.get('/health'),

  // Sentiment prediction
  predict: (text: string): Promise<SentimentPrediction> =>
    api.post('/predict', { text }),

  // Batch prediction
  batchPredict: (texts: string[]): Promise<BatchSentimentResponse> =>
    api.post('/predict/batch', { texts }),

  // Model training
  train: (params: {
    model_type?: string
    validation_split?: number
    random_seed?: number
  } = {}): Promise<TrainingResponse> =>
    api.post('/train', params),

  // Model evaluation
  evaluate: (): Promise<EvaluationResponse> =>
    api.post('/evaluate'),

  // Model info
  getModelInfo: (): Promise<ModelInfo> =>
    api.get('/model'),

  // Dataset info
  getDatasetInfo: (): Promise<DatasetInfo> =>
    api.get('/dataset'),

  // Training history
  getTrainingHistory: (): Promise<any[]> =>
    api.get('/history'),
}

// Keyword analysis API
export const keywordApi = {
  // Analyze keywords in text
  analyze: (text: string): Promise<any> =>
    api.post('/keywords/analyze', { text }),

  // Batch analyze keywords
  batchAnalyze: (texts: string[]): Promise<any[]> =>
    api.post('/keywords/batch', { texts }),

  // Get keyword sentiment trends
  getTrends: (): Promise<any> =>
    api.get('/keywords/trends'),

  // Get top keywords by sentiment
  getTopKeywords: (sentiment: 'positive' | 'negative', limit: number = 10): Promise<any> =>
    api.get(`/keywords/top/${sentiment}?limit=${limit}`),

  // Get keyword frequency
  getFrequency: (limit: number = 20): Promise<any> =>
    api.get(`/keywords/frequency?limit=${limit}`),
}

export default api
