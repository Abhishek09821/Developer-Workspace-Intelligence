import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { HealthResponse } from '@/types/api'

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await api.get<HealthResponse>('/health')
      return res.data
    },
    refetchInterval: 30_000,
    retry: false,
  })
}
