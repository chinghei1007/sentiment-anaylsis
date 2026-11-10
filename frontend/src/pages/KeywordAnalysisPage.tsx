import { useState, FormEvent } from 'react'
import { Search, TrendingUp, TrendingDown, Loader2, Sparkles } from 'lucide-react'
import { keywordApi } from '../services/api'
import { useQuery } from '@tanstack/react-query'

interface KeywordAnalysisResult {
  text: string
  overall_sentiment: string
  overall_score: number
  confidence: number
  keywords: Array<{
    keyword: string
    score: number
    sentiment: string
  }>
  positive_keywords: Array<{
    keyword: string
    score: number
    sentiment: string
  }>
  negative_keywords: Array<{
    keyword: string
    score: number
    sentiment: string
  }>
  total_keywords: number
}

export default function KeywordAnalysisPage() {
  const [text, setText] = useState('')
  const [analysisResult, setAnalysisResult] = useState<KeywordAnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch keyword trends
  const { data: trends, isLoading: trendsLoading } = useQuery({
    queryKey: ['keyword-trends'],
    queryFn: () => keywordApi.getTrends(),
    retry: 2,
  })

  // Fetch top keywords
  const { data: topKeywords, isLoading: topKeywordsLoading } = useQuery({
    queryKey: ['top-keywords'],
    queryFn: async () => {
      const [positive, negative] = await Promise.all([
        keywordApi.getTopKeywords('positive', 10),
        keywordApi.getTopKeywords('negative', 10),
      ])
      return { positive, negative }
    },
    retry: 2,
  })

  // Fetch keyword frequency
  const { data: frequency, isLoading: frequencyLoading } = useQuery({
    queryKey: ['keyword-frequency'],
    queryFn: () => keywordApi.getFrequency(20),
    retry: 2,
  })

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!text.trim()) return

    setIsAnalyzing(true)
    setError(null)

    try {
      const result = await keywordApi.analyze(text)
      setAnalysisResult(result)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze keywords')
    } finally {
      setIsAnalyzing(false)
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

  const getScoreColor = (score: number) => {
    if (score > 0.5) return 'text-sentiment-positive'
    if (score < -0.5) return 'text-red-600'
    if (score > 0) return 'text-green-500'
    if (score < 0) return 'text-orange-500'
    return 'text-gray-500'
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Keyword Analysis</h1>
          <p className="text-gray-600 mt-1">
            Analyze sentiment at the keyword level to identify what drives sentiment
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Analysis Form */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Analyze Text</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label" htmlFor="text">
                Enter Text
              </label>
              <textarea
                id="text"
                rows={8}
                className="input resize-none"
                placeholder="Enter text to analyze keywords...\n\nExample:\nThe product quality is excellent and the customer service is amazing, but the price is too high."
                value={text}
                onChange={(e) => setText(e.target.value)}
                disabled={isAnalyzing}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary w-full flex items-center justify-center gap-2"
              disabled={isAnalyzing || !text.trim()}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Analyzing Keywords...
                </>
              ) : (
                <>
                  <Search size={20} />
                  Analyze Keywords
                </>
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {/* Quick Examples */}
          <div className="mt-6">
            <h3 className="text-lg font-medium text-gray-700 mb-4">Quick Examples</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                "The product is amazing and works perfectly!",
                "Terrible quality and poor customer service.",
                "Good value for money, but could be better.",
                "Excellent features, fast delivery, highly recommended.",
                "Waste of money, broken on arrival, no refund.",
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

        {/* Analysis Results */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Results</h2>

          {analysisResult && !isAnalyzing ? (
            <div className="space-y-6">
              {/* Overall Sentiment */}
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Overall Sentiment</h3>
                
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-4xl ${getSentimentColor(analysisResult.overall_sentiment)}`}>
                    {analysisResult.overall_sentiment === 'positive' ? '😊' : 
                     analysisResult.overall_sentiment === 'negative' ? '😠' : '😐'}
                  </div>
                  <div>
                    <h4 className="text-2xl font-bold capitalize">{analysisResult.overall_sentiment}</h4>
                    <p className="text-gray-500 text-sm">Overall Sentiment</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Score</p>
                    <p className={`text-3xl font-bold ${getScoreColor(analysisResult.overall_score)}`}>
                      {analysisResult.overall_score.toFixed(2)}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Confidence</p>
                    <p className="text-3xl font-bold text-gray-900">
                      {(analysisResult.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Keywords Breakdown */}
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Keywords Breakdown</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles size={18} className="text-sentiment-positive" />
                      <h4 className="font-semibold text-gray-800">Positive Keywords</h4>
                    </div>
                    <p className="text-sm text-gray-500 mb-3">
                      {analysisResult.positive_keywords.length} keywords
                    </p>
                    <div className="space-y-2">
                      {analysisResult.positive_keywords.slice(0, 5).map((kw, i) => (
                        <div key={i} className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">{kw.keyword}</span>
                          <span className={`text-xs font-medium ${getScoreColor(kw.score)}`}>
                            {kw.score.toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles size={18} className="text-red-500" />
                      <h4 className="font-semibold text-gray-800">Negative Keywords</h4>
                    </div>
                    <p className="text-sm text-gray-500 mb-3">
                      {analysisResult.negative_keywords.length} keywords
                    </p>
                    <div className="space-y-2">
                      {analysisResult.negative_keywords.slice(0, 5).map((kw, i) => (
                        <div key={i} className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">{kw.keyword}</span>
                          <span className={`text-xs font-medium ${getScoreColor(kw.score)}`}>
                            {kw.score.toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* All Keywords */}
              {analysisResult.keywords.length > 0 && (
                <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">All Keywords</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-2 px-4 font-semibold text-gray-600">Keyword</th>
                          <th className="text-left py-2 px-4 font-semibold text-gray-600">Sentiment</th>
                          <th className="text-right py-2 px-4 font-semibold text-gray-600">Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analysisResult.keywords.map((kw, i) => (
                          <tr key={i} className="border-b border-gray-100">
                            <td className="py-2 px-4 text-gray-700">{kw.keyword}</td>
                            <td className="py-2 px-4">
                              <span className={`sentiment-badge ${kw.sentiment === 'positive' ? 'sentiment-positive' : 'sentiment-negative'}`}>
                                {kw.sentiment}
                              </span>
                            </td>
                            <td className={`py-2 px-4 text-right font-medium ${getScoreColor(kw.score)}`}>
                              {kw.score.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ) : (
            !isAnalyzing && (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Search size={48} className="text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  Enter text to analyze
                </h3>
                <p className="text-gray-500">
                  Type or paste text above and click "Analyze Keywords"
                </p>
              </div>
            )
          )}

          {isAnalyzing && (
            <div className="text-center py-12">
              <Loader2 className="animate-spin mx-auto mb-4" size={48} />
              <p className="text-gray-600">Analyzing keywords...</p>
            </div>
          )}
        </div>
      </div>

      {/* Keyword Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Positive Keywords */}
        <div className="card">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp size={24} className="text-sentiment-positive" />
            <h2 className="text-xl font-semibold text-gray-800">Top Positive Keywords</h2>
          </div>
          
          {topKeywordsLoading ? (
            <div className="text-center py-8">
              <Loader2 className="animate-spin mx-auto" size={24} />
            </div>
          ) : topKeywords?.positive?.keywords ? (
            <div className="space-y-3">
              {topKeywords.positive.keywords.map((kw: any, index: number) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-8 h-8 bg-sentiment-positive/10 rounded-lg flex items-center justify-center text-sentiment-positive font-medium">
                      {index + 1}
                    </span>
                    <span className="font-medium text-gray-800">{kw[0]}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-green-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-500 rounded-full"
                        style={{ width: `${Math.min(kw[1] * 10, 100)}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-600">{kw[1]}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No data available</p>
          )}
        </div>

        {/* Top Negative Keywords */}
        <div className="card">
          <div className="flex items-center gap-2 mb-6">
            <TrendingDown size={24} className="text-red-500" />
            <h2 className="text-xl font-semibold text-gray-800">Top Negative Keywords</h2>
          </div>
          
          {topKeywordsLoading ? (
            <div className="text-center py-8">
              <Loader2 className="animate-spin mx-auto" size={24} />
            </div>
          ) : topKeywords?.negative?.keywords ? (
            <div className="space-y-3">
              {topKeywords.negative.keywords.map((kw: any, index: number) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center text-red-600 font-medium">
                      {index + 1}
                    </span>
                    <span className="font-medium text-gray-800">{kw[0]}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-red-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-red-500 rounded-full"
                        style={{ width: `${Math.min(Math.abs(kw[1]) * 10, 100)}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-600">{Math.abs(kw[1])}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No data available</p>
          )}
        </div>
      </div>

      {/* Keyword Frequency */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Most Frequent Keywords</h2>
        
        {frequencyLoading ? (
          <div className="text-center py-8">
            <Loader2 className="animate-spin mx-auto" size={24} />
          </div>
        ) : frequency?.keywords ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {frequency.keywords.map((kw: any, index: number) => (
              <div
                key={index}
                className="bg-gray-50 rounded-xl p-4 border border-gray-200"
              >
                <p className="font-medium text-gray-800 truncate">{kw.keyword}</p>
                <p className="text-sm text-gray-500 mt-1">{kw.frequency} occurrences</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No data available</p>
        )}
      </div>
    </div>
  )
}
