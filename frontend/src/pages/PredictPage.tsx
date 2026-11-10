import { useState, FormEvent } from 'react'
import { Send, History, Trash2, Loader2 } from 'lucide-react'
import { useSentimentPrediction, useSentimentHistory } from '../hooks'

export default function PredictPage() {
  const [text, setText] = useState('')
  const { predict, isLoading, error, data } = useSentimentPrediction()
  const { history, addToHistory, clearHistory } = useSentimentHistory()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!text.trim()) return

    try {
      const prediction = await predict(text)
      addToHistory(prediction)
    } catch (err) {
      console.error('Prediction error:', err)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-sentiment-positive/10 text-sentiment-positive border-sentiment-positive'
      case 'negative':
        return 'bg-red-100 text-red-700 border-red-300'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300'
    }
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return '😊'
      case 'negative':
        return '😠'
      default:
        return '😐'
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Single Prediction</h1>
          <p className="text-gray-600 mt-1">
            Analyze sentiment of individual user comments
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Enter Text</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label" htmlFor="text">
                User Comment or Text
              </label>
              <textarea
                id="text"
                rows={8}
                className="input resize-none"
                placeholder="Enter user comment or text to analyze...\n\nExample:\n- I love this product! It's amazing.\n- This is the worst experience ever."
                value={text}
                onChange={(e) => setText(e.target.value)}
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary w-full flex items-center justify-center gap-2"
              disabled={isLoading || !text.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send size={20} />
                  Analyze Sentiment
                </>
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error.message}</p>
            </div>
          )}

          {/* Quick Examples */}
          <div className="mt-6">
            <h3 className="text-lg font-medium text-gray-700 mb-4">Quick Examples</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                "This product is absolutely amazing!",
                "I hate this, it's terrible quality.",
                "It's okay, nothing special.",
                "Best purchase I've ever made!",
                "Worst customer service experience.",
                "Works as expected, satisfied.",
              ].map((example) => (
                <button
                  key={example}
                  onClick={() => setText(example)}
                  className="text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors truncate"
                >
                  "{example}"
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Results</h2>

          {data && !isLoading ? (
            <div className="space-y-6">
              {/* Overall Sentiment */}
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-4xl ${getSentimentColor(data.sentiment)}`}>
                    {getSentimentIcon(data.sentiment)}
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold capitalize">{data.sentiment}</h3>
                    <p className="text-gray-500 text-sm">Sentiment</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Confidence</p>
                    <p className="text-3xl font-bold text-gray-900">
                      {(data.confidence ? data.confidence * 100 : 0).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Label</p>
                    <p className="text-3xl font-bold text-gray-900">{data.label}</p>
                  </div>
                </div>

                {data.prob_positive !== undefined && (
                  <div className="mt-4 bg-white rounded-lg p-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Probabilities</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-green-600 font-medium">Positive</span>
                        <div className="flex items-center gap-2">
                          <div className="w-48 h-2 bg-green-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-green-500 rounded-full"
                              style={{ width: `${(data.prob_positive || 0) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">
                            {(data.prob_positive ? data.prob_positive * 100 : 0).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-red-600 font-medium">Negative</span>
                        <div className="flex items-center gap-2">
                          <div className="w-48 h-2 bg-red-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-red-500 rounded-full"
                              style={{ width: `${(data.prob_negative || 0) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">
                            {(data.prob_negative ? data.prob_negative * 100 : 0).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input Text */}
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Input Text</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{data.text}</p>
              </div>
            </div>
          ) : (
            !isLoading && (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Send size={48} className="text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  Enter text to analyze
                </h3>
                <p className="text-gray-500">
                  Type or paste user comment above and click "Analyze Sentiment"
                </p>
              </div>
            )
          )}

          {isLoading && (
            <div className="text-center py-12">
              <Loader2 className="animate-spin mx-auto mb-4" size={48} />
              <p className="text-gray-600">Analyzing sentiment...</p>
            </div>
          )}
        </div>
      </div>

      {/* History */}
      {history.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-800">Recent History</h2>
            <button
              onClick={clearHistory}
              className="flex items-center gap-2 text-sm text-red-600 hover:text-red-700 transition-colors"
            >
              <Trash2 size={16} />
              Clear History
            </button>
          </div>

          <div className="space-y-4">
            {history.slice(0, 5).map((item, index) => (
              <div
                key={index}
                className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl border border-gray-200"
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${getSentimentColor(item.sentiment)}`}>
                  {getSentimentIcon(item.sentiment)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-gray-700 truncate">{item.text}</p>
                  <div className="flex items-center gap-4 mt-2">
                    <span className={`sentiment-badge ${item.sentiment === 'positive' ? 'sentiment-positive' : 'sentiment-negative'}`}>
                      {item.sentiment}
                    </span>
                    <span className="text-sm text-gray-500">
                      Confidence: {(item.confidence ? item.confidence * 100 : 0).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
