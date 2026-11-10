import { useState, useEffect } from 'react'
import { Database, FileText, Loader2, Upload, Eye, Trash2 } from 'lucide-react'
import { useDatasetInfo, useHealthCheck } from '../hooks'

export default function DatasetPage() {
  const { datasetInfo, isLoading, error } = useDatasetInfo()
  const { health } = useHealthCheck()
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setUploadedFiles(Array.from(e.target.files))
    }
  }

  const handleRemoveFile = (index: number) => {
    setUploadedFiles(uploadedFiles.filter((_, i) => i !== index))
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-sentiment-positive/10 text-sentiment-positive'
      case 'negative':
        return 'bg-red-100 text-red-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  // Sample data for demonstration
  const sampleData = [
    {
      id: 1,
      text: "Absolutely love this product! It exceeded all my expectations and the quality is outstanding.",
      sentiment: 'positive',
      source: 'Product Review',
      date: '2026-01-15'
    },
    {
      id: 2,
      text: "The service was okay, nothing special. Delivery was on time but the packaging could have been better.",
      sentiment: 'neutral',
      source: 'Customer Feedback',
      date: '2026-01-16'
    },
    {
      id: 3,
      text: "Terrible experience! The product arrived damaged and customer support was unhelpful.",
      sentiment: 'negative',
      source: 'Product Review',
      date: '2026-01-17'
    },
    {
      id: 4,
      text: "This is the best purchase I've made this year! The features are amazing and it works exactly as advertised.",
      sentiment: 'positive',
      source: 'Social Media',
      date: '2026-01-18'
    },
    {
      id: 5,
      text: "Received the package today. It looks decent but haven't tried it yet.",
      sentiment: 'neutral',
      source: 'Social Media',
      date: '2026-01-19'
    },
  ]

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dataset</h1>
          <p className="text-gray-600 mt-1">
            Explore and manage your sentiment analysis dataset
          </p>
        </div>
      </div>

      {/* Upload Section */}
      <div className="card">
        <div className="flex items-center gap-2 mb-6">
          <Upload size={24} className="text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-800">Upload Dataset</h2>
        </div>

        <div className="p-6 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300 hover:border-primary-300 transition-colors">
          <div className="text-center mb-4">
            <Upload size={48} className="text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">
              Drag & drop files here, or click to browse
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Supports: CSV, JSON, TSV
            </p>
          </div>
          
          <label className="cursor-pointer">
            <input
              type="file"
              accept=".csv,.json,.tsv,.txt"
              onChange={handleFileUpload}
              className="hidden"
              multiple
            />
            <button className="btn btn-secondary">
              <Upload size={18} />
              Select Files
            </button>
          </label>
        </div>

        {uploadedFiles.length > 0 && (
          <div className="mt-4 space-y-3">
            <h3 className="text-lg font-medium text-gray-700">Selected Files</h3>
            <div className="space-y-2">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-center gap-3">
                    <FileText size={20} className="text-gray-500" />
                    <div>
                      <p className="font-medium text-gray-800">{file.name}</p>
                      <p className="text-sm text-gray-500">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleRemoveFile(index)}
                    className="text-red-500 hover:text-red-600 transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </div>
            <button className="btn btn-primary mt-4">
              <Upload size={18} />
              Upload & Process
            </button>
          </div>
        )}
      </div>

      {/* Dataset Info */}
      <div className="card">
        <div className="flex items-center gap-2 mb-6">
          <Database size={24} className="text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-800">Dataset Information</h2>
        </div>

        {isLoading ? (
          <div className="text-center py-8">
            <Loader2 className="animate-spin mx-auto" size={24} />
            <p className="text-gray-600 mt-2">Loading dataset info...</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <XCircle size={48} className="text-red-600 mx-auto mb-2" />
            <p className="text-red-700">{error.message}</p>
          </div>
        ) : datasetInfo ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="stat-card">
              <p className="text-sm text-gray-500 mb-1">Total Samples</p>
              <p className="text-3xl font-bold text-gray-900">{datasetInfo.total_samples}</p>
            </div>
            <div className="stat-card">
              <p className="text-sm text-gray-500 mb-1">Positive</p>
              <p className="text-3xl font-bold text-sentiment-positive">
                {datasetInfo.positive_samples}
              </p>
            </div>
            <div className="stat-card">
              <p className="text-sm text-gray-500 mb-1">Negative</p>
              <p className="text-3xl font-bold text-red-600">
                {datasetInfo.negative_samples}
              </p>
            </div>
            <div className="stat-card">
              <p className="text-sm text-gray-500 mb-1">Neutral</p>
              <p className="text-3xl font-bold text-gray-600">
                {datasetInfo.neutral_samples}
              </p>
            </div>
            <div className="stat-card md:col-span-2">
              <p className="text-sm text-gray-500 mb-1">Name</p>
              <p className="font-medium text-gray-800">{datasetInfo.name}</p>
            </div>
            <div className="stat-card md:col-span-2">
              <p className="text-sm text-gray-500 mb-1">Sources</p>
              <div className="flex flex-wrap gap-2">
                {datasetInfo.sources.map((source, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
                  >
                    {source}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <Database size={48} className="text-gray-400 mx-auto mb-2" />
            <p className="text-gray-500">No dataset loaded</p>
          </div>
        )}
      </div>

      {/* API Health */}
      <div className="card">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
            <span className="text-primary-600 font-bold">API</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-800">API Health</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="stat-card">
            <p className="text-sm text-gray-500 mb-1">Status</p>
            <p className={`text-3xl font-bold ${
              health?.status === 'healthy' ? 'text-green-600' : 'text-red-600'
            }`}>
              {health?.status === 'healthy' ? '✓ Healthy' : '✗ Unhealthy'}
            </p>
          </div>
          <div className="stat-card">
            <p className="text-sm text-gray-500 mb-1">Version</p>
            <p className="text-3xl font-bold text-gray-900">{health?.version || 'Unknown'}</p>
          </div>
          <div className="stat-card">
            <p className="text-sm text-gray-500 mb-1">Spark Available</p>
            <p className={`text-3xl font-bold ${
              health?.spark_available ? 'text-green-600' : 'text-red-600'
            }`}>
              {health?.spark_available ? '✓ Yes' : '✗ No'}
            </p>
          </div>
          <div className="stat-card">
            <p className="text-sm text-gray-500 mb-1">Model Loaded</p>
            <p className={`text-3xl font-bold ${
              health?.model_loaded ? 'text-green-600' : 'text-red-600'
            }`}>
              {health?.model_loaded ? '✓ Yes' : '✗ No'}
            </p>
          </div>
        </div>
      </div>

      {/* Sample Data Preview */}
      <div className="card">
        <div className="flex items-center gap-2 mb-6">
          <Eye size={24} className="text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-800">Sample Data Preview</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-600">ID</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-600">Text</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-600">Sentiment</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-600">Source</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-600">Date</th>
              </tr>
            </thead>
            <tbody>
              {sampleData.map((row) => (
                <tr key={row.id} className="border-b border-gray-100">
                  <td className="py-3 px-4 text-gray-700">{row.id}</td>
                  <td className="py-3 px-4 text-gray-700 max-w-xs truncate">
                    {row.text}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`sentiment-badge ${getSentimentColor(row.sentiment)}`}>
                      {row.sentiment}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-700">{row.source}</td>
                  <td className="py-3 px-4 text-gray-700 text-sm">{row.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-sm text-gray-500 mt-4">
          Showing sample data. Actual dataset may contain more records.
        </p>
      </div>
    </div>
  )
}
