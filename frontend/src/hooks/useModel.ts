import { useMutation, useQuery } from '@tanstack/react-query'
import { sentimentApi, TrainingResponse, EvaluationResponse, ModelInfo } from '../services/api'

export function useModelTraining() {
  const mutation = useMutation({
    mutationFn: sentimentApi.train,
    mutationKey: ['model-training'],
  })

  return {
    train: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error,
    data: mutation.data as TrainingResponse | undefined,
  }
}

export function useModelEvaluation() {
  const mutation = useMutation({
    mutationFn: sentimentApi.evaluate,
    mutationKey: ['model-evaluation'],
  })

  return {
    evaluate: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error,
    data: mutation.data as EvaluationResponse | undefined,
  }
}

export function useModelInfo() {
  const query = useQuery({
    queryKey: ['model-info'],
    queryFn: sentimentApi.getModelInfo,
    retry: 3,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  return {
    modelInfo: query.data,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  }
}

export function useTrainingHistory() {
  const query = useQuery({
    queryKey: ['training-history'],
    queryFn: sentimentApi.getTrainingHistory,
    retry: 2,
  })

  return {
    history: query.data || [],
    isLoading: query.isLoading,
    error: query.error,
  }
}
