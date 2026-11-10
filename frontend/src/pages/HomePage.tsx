import { Link } from 'react-router-dom'
import { TrendingUp, FileText, Batch, Key, Brain, BarChart3, Database, ArrowRight } from 'lucide-react'
import { useHealthCheck, useModelInfo, useDatasetInfo } from '../hooks'

const featureCards = [
  {
    icon: FileText,
    title: 'Single Prediction',
    description: 'Analyze sentiment of individual user comments',
    to: '/predict',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    icon: Batch,
    title: 'Batch Processing',
    description: 'Analyze multiple comments at once',
    to: '/batch',
    color: 'bg-purple-100 text-purple-600',
  },
  {
    icon: Key,
    title: 'Keyword Analysis',
    description: 'Identify sentiment-driving keywords',
    to: '/keywords',
    color: 'bg-green-100 text-green-600',
  },
  {
    icon: Brain,
    title: 'Model Training',
    description: 'Train custom models on your data',
    to: '/train',
    color: 'bg-orange-100 text-orange-600',
  },
  {
    icon: BarChart3,
    title: 'Model Evaluation',
    description: 'Evaluate model performance',
    to: '/evaluate',
    color: 'bg-red-100 text-red-600',
  },
  {
    icon: Database,
    title: 'Dataset Info',
    description: 'Explore your dataset',
    to: '/dataset',
    color: 'bg-indigo-100 text-indigo-600',
  },
]

export default function HomePage() {
  const { health, isLoading: healthLoading } = useHealthCheck()
  const { modelInfo, isLoading: modelLoading } = useModelInfo()
  const { datasetInfo, isLoading: datasetLoading } = useDatasetInfo()

  const isLoading = healthLoading || modelLoading || datasetLoading

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-8 text-white">
        <div className="max-w-4xl">
          <h1 className="text-4xl font-bold mb-4">Sentiment Analysis Dashboard</h1>
          <p className="text-xl text-primary-100 mb-8">
            Analyze user comments using PySpark ML models. Classify text as positive or negative sentiment.
          </p>
          
          {/* Quick Stats */}
          {!isLoading && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4">
                <p className="text-sm text-primary-200 mb-1">API Status</p>
                <p className="text-2xl font-bold">
                  {health?.status === 'healthy' ? '✓ Healthy' : '✗ Unhealthy'}
                </p>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4">
                <p className="text-sm text-primary-200 mb-1">Model</p>
                <p className="text-2xl font-bold">
                  {modelInfo?.trained ? '✓ Trained' : '✗ Not Trained'}
                </p>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4">
                <p className="text-sm text-primary-200 mb-1">Dataset</p>
                <p className="text-2xl font-bold">
                  {datasetInfo?.total_samples || 0} Samples
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-800">Features</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featureCards.map(({ icon: Icon, title, description, to, color }) => (
            <Link
              key={to}
              to={to}
              className="card group hover:shadow-lg transition-shadow duration-200"
            >
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color} flex-shrink-0`}>
                  <Icon size={24} />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                    {title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-3">{description}</p>
                  <div className="text-primary-600 font-medium flex items-center gap-1">
                    Learn more <ArrowRight size={16} />
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Quick Start */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Quick Start</h2>
        <p className="text-gray-600 mb-6">
          Get started with sentiment analysis in just a few steps:
        </p>
        
        <div className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-primary-600 font-medium">1</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Enter Text</h3>
              <p className="text-gray-600 text-sm">Go to Single Prediction and enter user comment</p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-primary-600 font-medium">2</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Get Prediction</h3>
              <p className="text-gray-600 text-sm">View sentiment classification with confidence scores</p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-primary-600 font-medium">3</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Analyze Keywords</h3>
              <p className="text-gray-600 text-sm">Identify which keywords drive sentiment</p>
            </div>
          </div>
        </div>

        <div className="mt-6 flex gap-4">
          <Link to="/predict" className="btn btn-primary">
            Try Single Prediction
          </Link>
          <Link to="/batch" className="btn btn-secondary">
            Try Batch Prediction
          </Link>
        </div>
      </div>
    </div>
  )
}
