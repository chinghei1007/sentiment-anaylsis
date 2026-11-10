import { useQuery } from '@tanstack/react-query'
import { sentimentApi, DatasetInfo } from '../services/api'

export function useDatasetInfo() {
  const query = useQuery({
    queryKey: ['dataset-info'],
    queryFn: sentimentApi.getDatasetInfo,
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  return {
    datasetInfo: query.data,
    isLoading: query.isLoading,
    error: query.error,
  }
}

export function useHealthCheck() {
  const query = useQuery({
    queryKey: ['health-check'],
    queryFn: sentimentApi.health,
    retry: 3,
    refetchInterval: 60000, // Refetch every minute
  })

  return {
    health: query.data,
    isLoading: query.isLoading,
    error: query.error,
  }
}
