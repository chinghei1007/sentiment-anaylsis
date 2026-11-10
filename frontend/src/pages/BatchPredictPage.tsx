import { useState, FormEvent, ChangeEvent } from 'react'
import { Upload, FileText, Trash2, Loader2, Download } from 'lucide-react'
import { useBatchSentimentPrediction } from '../hooks'

export default function BatchPredictPage() {
  const [texts, setTexts] = useState<string[]>([''])
  const [file, setFile] = useState<File | null>(null)
  const { predictBatch, isLoading, error, data } = useBatchSentimentPrediction()

  const handleTextChange = (index: number, value: string) => {
    const newTexts = [...texts]
    newTexts[index] = value
    setTexts(newTexts)
  }

  const handleAddText = () => {
    setTexts([...texts, ''])
  }

  const handleRemoveText = (index: number) => {
    const newTexts = texts.filter((_, i) => i !== index)
    setTexts(newTexts.length > 0 ? newTexts : [''])
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleFileUpload = () => {
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      if (content) {
        const lines = content.split('\n').filter(line => line.trim())
        setTexts(lines.length > 0 ? lines : [''])
      }
    }
    reader.readAsText(file)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    
    const validTexts = texts.filter(t => t.trim())
    if (validTexts.length === 0) return

    try {
      await predictBatch(validTexts)
    } catch (err) {
      console.error('Batch prediction error:', err)
    }
  }

  const handleDownloadResults = () => {
    if (!data) return

    const csvContent = [
      ['Text', 'Sentiment', 'Label', 'Confidence', 'Prob Positive', 'Prob Negative'],
      ...data.predictions.map(p => [
        `"${p.text.replace(/"/g, '""')}"`,
        p.sentiment,
        p.label,
        p.confidence || '',
        p.prob_positive || '',
        p.prob_negative || ''
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `sentiment_results_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
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

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Batch Prediction</h1>
          <p className="text-gray-600 mt-1">
            Analyze sentiment for multiple user comments at once
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Input</h2>

          {/* File Upload */}
          <div className="mb-6 p-6 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300 hover:border-primary-300 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-700">Upload Text File</h3>
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept=".txt,.csv"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <Upload size={24} className="text-primary-600" />
              </label>
            </div>
            <p className="text-sm text-gray-500 mb-4">
              Upload a .txt or .csv file with one comment per line
            </p>
            {file && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{file.name}</span>
                <button
                  onClick={handleFileUpload}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  Load File
                </button>
              </div>
            )}
          </div>

          {/* Text Inputs */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-lg font-medium text-gray-700 mb-4">Enter Comments</h3>
            
            <div className="space-y-4">
              {texts.map((text, index) => (
                <div key={index} className="flex items-center gap-4">
                  <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-medium flex-shrink-0">
                    {index + 1}
                  </span>
                  <textarea
                    rows={3}
                    className="input flex-1"
                    placeholder={`Enter comment ${index + 1}...`}
                    value={text}
                    onChange={(e) => handleTextChange(index, e.target.value)}
                    disabled={isLoading}
                  />
                  {texts.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveText(index)}
                      className="w-10 h-10 bg-red-100 hover:bg-red-200 rounded-lg flex items-center justify-center text-red-600 transition-colors flex-shrink-0"
                    >
                      <Trash2 size={20} />
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="flex gap-4">
              <button
                type="button"
                onClick={handleAddText}
                className="btn btn-secondary flex-1"
              >
                Add Another Comment
              </button>
              <button
                type="submit"
                className="btn btn-primary flex-1 flex items-center justify-center gap-2"
                disabled={isLoading || texts.filter(t => t.trim()).length === 0}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin" size={20} />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <FileText size={20} />
                    Analyze All
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error.message}</p>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-800">Results</h2>
            {data && (
              <button
                onClick={handleDownloadResults}
                className="btn btn-secondary flex items-center gap-2 text-sm"
              >
                <Download size={16} />
                Download CSV
              </button>
            )}
          </div>

          {data && !isLoading ? (
            <div className="space-y-4">
              {/* Summary */}
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Total Analyzed</p>
                    <p className="text-3xl font-bold text-gray-900">{data.total}</p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Positive</p>
                    <p className="text-3xl font-bold text-sentiment-positive">
                      {data.predictions.filter(p => p.sentiment === 'positive').length}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Negative</p>
                    <p className="text-3xl font-bold text-red-600">
                      {data.predictions.filter(p => p.sentiment === 'negative').length}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Avg Confidence</p>
                    <p className="text-3xl font-bold text-gray-900">
                      {(
                        data.predictions.reduce((sum, p) => sum + (p.confidence || 0), 0) / data.predictions.length * 100
                      ).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Results List */}
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {data.predictions.map((prediction, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl border border-gray-200"
                  >
                    <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-medium flex-shrink-0">
                      {index + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-gray-700 truncate mb-2">{prediction.text}</p>
                      <div className="flex items-center gap-4">
                        <span className={`sentiment-badge ${prediction.sentiment === 'positive' ? 'sentiment-positive' : 'sentiment-negative'}`}>
                          {prediction.sentiment}
                        </span>
                        <span className="text-sm text-gray-500">
                          Confidence: {(prediction.confidence ? prediction.confidence * 100 : 0).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            !isLoading && (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileText size={48} className="text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  Enter comments to analyze
                </h3>
                <p className="text-gray-500">
                  Add comments above or upload a file and click "Analyze All"
                </p>
              </div>
            )
          )}

          {isLoading && (
            <div className="text-center py-12">
              <Loader2 className="animate-spin mx-auto mb-4" size={48} />
              <p className="text-gray-600">Analyzing {texts.filter(t => t.trim()).length} comments...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
