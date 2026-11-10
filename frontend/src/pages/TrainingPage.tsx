import { useState, FormEvent } from 'react'
import { Brain, Loader2, CheckCircle, XCircle, History, Play } from 'lucide-react'
import { useModelTraining, useTrainingHistory, useModelInfo } from '../hooks'

export default function TrainingPage() {
  const [modelType, setModelType] = useState('logistic')
  const [validationSplit, setValidationSplit] = useState(0.2)
  const [randomSeed, setRandomSeed] = useState(42)
  
  const { train, isLoading, error, data } = useModelTraining()
  const { history } = useTrainingHistory()
  const { modelInfo, refetch: refetchModelInfo } = useModelInfo()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    
    try {
      await train({
        model_type: modelType,
        validation_split: validationSplit,
        random_seed: randomSeed,
      })
      
      // Refetch model info after training
      setTimeout(() => refetchModelInfo(), 2000)
    } catch (err) {
      console.error('Training error:', err)
    }
  }

  const modelTypes = [
    { value: 'logistic', label: 'Logistic Regression', description: 'Good for text classification, fast and interpretable' },
    { value: 'naive_bayes', label: 'Naive Bayes', description: 'Simple and fast, works well with text data' },
    { value: 'random_forest', label: 'Random Forest', description: 'Ensemble method, handles non-linear relationships' },
    { value: 'gbt', label: 'Gradient Boosted Trees', description: 'Powerful ensemble method, high accuracy' },
  ]

  const getStatusColor = (trained: boolean) => {
    return trained ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Train Model</h1>
          <p className="text-gray-600 mt-1">
            Train a new sentiment analysis model on your dataset
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Training Form */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Training Configuration</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Model Type */}
            <div>
              <label className="label" htmlFor="modelType">
                Model Type
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {modelTypes.map(({ value, label, description }) => (
                  <label
                    key={value}
                    className={`flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                      modelType === value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 bg-gray-50 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      id={value}
                      name="modelType"
                      value={value}
                      checked={modelType === value}
                      onChange={(e) => setModelType(e.target.value)}
                      className="mt-1 hidden"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800">{label}</h3>
                      <p className="text-sm text-gray-500 mt-1">{description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Validation Split */}
            <div>
              <label className="label" htmlFor="validationSplit">
                Validation Split
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  id="validationSplit"
                  min={0.1}
                  max={0.5}
                  step={0.1}
                  value={validationSplit}
                  onChange={(e) => setValidationSplit(parseFloat(e.target.value))}
                  className="flex-1"
                />
                <span className="w-20 text-center font-medium text-gray-700">
                  {validationSplit * 100}%
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Fraction of data to use for validation (0.1-0.5)
              </p>
            </div>

            {/* Random Seed */}
            <div>
              <label className="label" htmlFor="randomSeed">
                Random Seed
              </label>
              <input
                type="number"
                id="randomSeed"
                value={randomSeed}
                onChange={(e) => setRandomSeed(parseInt(e.target.value) || 42)}
                className="input"
                placeholder="42"
              />
              <p className="text-sm text-gray-500 mt-2">
                Random seed for reproducibility
              </p>
            </div>

            {/* Training Button */}
            <button
              type="submit"
              className="btn btn-primary w-full flex items-center justify-center gap-2"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Training Model...
                </>
              ) : (
                <>
                  <Brain size={20} />
                  Start Training
                </>
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error.message}</p>
            </div>
          )}

          {data && (
            <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-xl">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle size={24} className="text-green-600" />
                <h3 className="text-lg font-semibold text-green-800">Training Complete!</h3>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500 mb-1">Model Type</p>
                  <p className="font-medium text-gray-800">{data.model_type}</p>
                </div>
                <div>
                  <p className="text-gray-500 mb-1">Accuracy</p>
                  <p className="font-medium text-green-600">
                    {(data.accuracy * 100).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 mb-1">Training Samples</p>
                  <p className="font-medium text-gray-800">{data.training_samples}</p>
                </div>
                <div>
                  <p className="text-gray-500 mb-1">Validation Samples</p>
                  <p className="font-medium text-gray-800">{data.validation_samples}</p>
                </div>
              </div>
              
              <p className="text-sm text-green-600 mt-4">
                Model saved and ready for predictions
              </p>
            </div>
          )}
        </div>

        {/* Current Model Status */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-800">Current Model</h2>
            <span className={`sentiment-badge ${getStatusColor(modelInfo?.trained || false)}`}>
              {modelInfo?.trained ? 'Trained' : 'Not Trained'}
            </span>
          </div>

          {modelInfo ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
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
                {modelInfo.training_date && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Trained</p>
                    <p className="font-medium text-gray-800">{new Date(modelInfo.training_date).toLocaleString()}</p>
                  </div>
                )}
                {modelInfo.accuracy && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Accuracy</p>
                    <p className="font-medium text-green-600">
                      {(modelInfo.accuracy * 100).toFixed(2)}%
                    </p>
                  </div>
                )}
              </div>

              {modelInfo.path && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500 mb-1">Model Path</p>
                  <p className="font-mono text-sm text-gray-700 truncate">{modelInfo.path}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No model loaded</p>
              <p className="text-sm text-gray-400">Train a model to get started</p>
            </div>
          )}
        </div>
      </div>

      {/* Training History */}
      {history.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-800">Training History</h2>
            <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
              {history.length} sessions
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-600">Date</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-600">Model</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-600">Accuracy</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-600">Samples</th>
                </tr>
              </thead>
              <tbody>
                {history.slice().reverse().map((session, index) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-700">
                      {new Date(session.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-gray-700">
                      {session.model_type}
                    </td>
                    <td className="py-3 px-4 text-green-600 font-medium">
                      {(session.results.accuracy * 100).toFixed(2)}%
                    </td>
                    <td className="py-3 px-4 text-gray-700">
                      {session.results.training_samples}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
