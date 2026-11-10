import { useMutation, useQuery } from '@tanstack/react-query'
import { sentimentApi, SentimentPrediction, BatchSentimentResponse } from '../services/api'

export function useSentimentPrediction() {
  const mutation = useMutation({
    mutationFn: sentimentApi.predict,
    mutationKey: ['sentiment-prediction'],
  })

  return {
    predict: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  }
}

export function useBatchSentimentPrediction() {
  const mutation = useMutation({
    mutationFn: sentimentApi.batchPredict,
    mutationKey: ['batch-sentiment-prediction'],
  })

  return {
    predictBatch: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error,
    data: mutation.data as BatchSentimentResponse | undefined,
    reset: mutation.reset,
  }
}

export function useSentimentHistory() {
  const query = useQuery({
    queryKey: ['sentiment-history'],
    queryFn: () => {
      const history = localStorage.getItem('sentiment-history')
      return history ? JSON.parse(history) : []
    },
  })

  const addToHistory = (prediction: SentimentPrediction) => {
    const history = query.data || []
    const newHistory = [prediction, ...history].slice(0, 50) // Keep last 50
    localStorage.setItem('sentiment-history', JSON.stringify(newHistory))
    query.refetch()
  }

  const clearHistory = () => {
    localStorage.removeItem('sentiment-history')
    query.refetch()
  }

  return {
    history: query.data || [],
    isLoading: query.isLoading,
    addToHistory,
    clearHistory,
  }
}
