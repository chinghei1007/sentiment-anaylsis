import { useState } from 'react'
import { BarChart3, Loader2, RefreshCw, CheckCircle, XCircle } from 'lucide-react'
import { useModelEvaluation, useModelInfo } from '../hooks'
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Cell } from 'recharts'

export default function EvaluationPage() {
  const { evaluate, isLoading, error, data } = useModelEvaluation()
  const { modelInfo } = useModelInfo()

  const handleEvaluate = async () => {
    try {
      await evaluate()
    } catch (err) {
      console.error('Evaluation error:', err)
    }
  }

  // Confusion matrix data for chart
  const getConfusionMatrixData = () => {
    if (!data) return []
    
    const matrix = data.confusion_matrix
    return [
      { name: 'True Pos', value: matrix[1]?.[1] || 0, label: 'TP' },
      { name: 'False Neg', value: matrix[1]?.[0] || 0, label: 'FN' },
      { name: 'False Pos', value: matrix[0]?.[1] || 0, label: 'FP' },
      { name: 'True Neg', value: matrix[0]?.[0] || 0, label: 'TN' },
    ]
  }

  const confusionData = getConfusionMatrixData()

  // Metrics for chart
  const metricsData = [
    { name: 'Accuracy', value: data?.accuracy ? data.accuracy * 100 : 0, color: '#10b981' },
    { name: 'F1 Score', value: data?.f1_score ? data.f1_score * 100 : 0, color: '#3b82f6' },
    { name: 'Precision', value: data?.precision ? data.precision * 100 : 0, color: '#8b5cf6' },
    { name: 'Recall', value: data?.recall ? data.recall * 100 : 0, color: '#f59e0b' },
  ]

  const COLORS = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b']

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Model Evaluation</h1>
          <p className="text-gray-600 mt-1">
            Evaluate your model's performance on test data
          </p>
        </div>
        <button
          onClick={handleEvaluate}
          className="btn btn-primary flex items-center gap-2"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              Evaluating...
            </>
          ) : (
            <>
              <BarChart3 size={20} />
              Evaluate Model
            </>
          )}
        </button>
      </div>

      {/* Current Model Status */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Current Model</h2>
        
        {modelInfo ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500 mb-1">Model Type</p>
              <p className="font-medium text-gray-800">{modelInfo.model_type}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500 mb-1">Status</p>
              <p className={`font-medium ${modelInfo.trained ? 'text-green-600' : 'text-red-600'}`}>
                {modelInfo.trained ? 'Trained' : 'Not Trained'}
              </p>
            </div>
            {modelInfo.accuracy && (
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-500 mb-1">Training Accuracy</p>
                <p className="font-medium text-green-600">
                  {(modelInfo.accuracy * 100).toFixed(2)}%
                </p>
              </div>
            )}
            {modelInfo.f1_score && (
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-500 mb-1">F1 Score</p>
                <p className="font-medium text-blue-600">
                  {(modelInfo.f1_score * 100).toFixed(2)}%
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No model loaded</p>
            <p className="text-sm text-gray-400">Train a model first to evaluate</p>
          </div>
        )}
      </div>

      {error && (
        <div className="card bg-red-50 border border-red-200">
          <div className="flex items-center gap-2">
            <XCircle size={24} className="text-red-600" />
            <p className="text-red-700">{error.message}</p>
          </div>
        </div>
      )}

      {/* Evaluation Results */}
      {data && (
        <div className="space-y-8">
          {/* Summary Metrics */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Performance Metrics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-4">Scores</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="stat-card">
                    <p className="text-sm text-gray-500 mb-1">Accuracy</p>
                    <p className="text-3xl font-bold text-green-600">
                      {(data.accuracy * 100).toFixed(2)}%
                    </p>
                  </div>
                  <div className="stat-card">
                    <p className="text-sm text-gray-500 mb-1">F1 Score</p>
                    <p className="text-3xl font-bold text-blue-600">
                      {(data.f1_score * 100).toFixed(2)}%
                    </p>
                  </div>
                  <div className="stat-card">
                    <p className="text-sm text-gray-500 mb-1">Precision</p>
                    <p className="text-3xl font-bold text-purple-600">
                      {(data.precision * 100).toFixed(2)}%
                    </p>
                  </div>
                  <div className="stat-card">
                    <p className="text-sm text-gray-500 mb-1">Recall</p>
                    <p className="text-3xl font-bold text-orange-600">
                      {(data.recall * 100).toFixed(2)}%
                    </p>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-4">Dataset</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="stat-card">
                    <p className="text-sm text-gray-500 mb-1">Total Samples</p>
                    <p className="text-3xl font-bold text-gray-900">{data.total_samples}</p>
                  </div>
                  <div className="stat-card">
                    <p className="text-sm text-gray-500 mb-1">Positive</p>
                    <p className="text-3xl font-bold text-green-600">{data.positive_samples}</p>
                  </div>
                  <div className="stat-card">
                    <p className="text-sm text-gray-500 mb-1">Negative</p>
                    <p className="text-3xl font-bold text-red-600">{data.negative_samples}</p>
                  </div>
                  <div className="stat-card">
                    <p className="text-sm text-gray-500 mb-1">Evaluated At</p>
                    <p className="text-sm font-medium text-gray-700">
                      {new Date(data.evaluated_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Metrics Chart */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Metrics Overview</h2>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metricsData} layout="vertical">
                  <XAxis type="category" dataKey="name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8">
                    {metricsData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Confusion Matrix */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Confusion Matrix</h2>
            
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-4">Matrix</h3>
                <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-500 mb-1">Predicted Positive</p>
                      <p className="text-3xl font-bold text-green-600">
                        {data.confusion_matrix[1]?.[1] || 0}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-500 mb-1">Predicted Negative</p>
                      <p className="text-3xl font-bold text-green-600">
                        {data.confusion_matrix[1]?.[0] || 0}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-500 mb-1">Predicted Positive</p>
                      <p className="text-3xl font-bold text-red-600">
                        {data.confusion_matrix[0]?.[1] || 0}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-500 mb-1">Predicted Negative</p>
                      <p className="text-3xl font-bold text-red-600">
                        {data.confusion_matrix[0]?.[0] || 0}
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>Actual Positive</span>
                      <span>Actual Negative</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-4">Chart</h3>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={confusionData} layout="vertical">
                      <XAxis type="category" dataKey="name" hide />
                      <YAxis type="category" dataKey="label" />
                      <Tooltip />
                      <Bar dataKey="value" fill="#8884d8">
                        {confusionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!data && !isLoading && !error && (
        <div className="card text-center py-12">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <BarChart3 size={48} className="text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Evaluate Your Model
          </h3>
          <p className="text-gray-500 mb-6">
            Click "Evaluate Model" to test your trained model on the test dataset
          </p>
          <button
            onClick={handleEvaluate}
            className="btn btn-primary flex items-center gap-2 mx-auto"
          >
            <BarChart3 size={20} />
            Evaluate Model
          </button>
        </div>
      )}
    </div>
  )
}
