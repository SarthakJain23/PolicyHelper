"use client";

import { LogFilterParams, logsApi } from "@/lib/api/logs";
import { useQuery } from "@tanstack/react-query";

export function useLogs(params?: LogFilterParams) {
  const query = useQuery({
    queryKey: ["logs", params],
    queryFn: () => logsApi.list(params),
  });

  return {
    logs: query.data || [],
    isLoading: query.isLoading,
    refetch: query.refetch,
    isRefetching: query.isRefetching,
  };
}
