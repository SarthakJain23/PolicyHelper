"use client";

import { useQuery } from "@tanstack/react-query";
import { logsApi, LogFilterParams } from "@/lib/api/logs";

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
