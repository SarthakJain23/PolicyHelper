"use client";

import {
  llmConfigApi,
  ReindexPayload,
  SaveLLMConfigPayload,
  TestAndDiscoverPayload,
} from "@/lib/api/llm-config";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

export function useLLMConfig() {
  const queryClient = useQueryClient();
  const [reindexTaskId, setReindexTaskId] = useState<string | null>(null);

  const configsQuery = useQuery({
    queryKey: ["llm-configs"],
    queryFn: llmConfigApi.listConfigs,
    staleTime: 60 * 1000,
  });

  const availableModelsQuery = useQuery({
    queryKey: ["llm-models"],
    queryFn: llmConfigApi.getAvailableChatModels,
    staleTime: 5 * 60 * 1000,
  });

  const testAndDiscoverMutation = useMutation({
    mutationFn: (payload: TestAndDiscoverPayload) =>
      llmConfigApi.testAndDiscover(payload),
    onError: (err: any) => {
      toast.error(
        err.response?.data?.detail || "Failed to validate credentials",
      );
    },
  });

  const saveConfigMutation = useMutation({
    mutationFn: (payload: SaveLLMConfigPayload) =>
      llmConfigApi.saveConfig(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["llm-configs"] });
      queryClient.invalidateQueries({ queryKey: ["llm-models"] });
      toast.success("LLM Provider configuration saved successfully!");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to save configuration");
    },
  });

  const reindexMutation = useMutation({
    mutationFn: (payload: ReindexPayload) =>
      llmConfigApi.triggerReindex(payload),
    onSuccess: (data) => {
      setReindexTaskId(data.task_id);
      toast.info("Re-indexing started in the background");
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to start re-indexing");
    },
  });

  const reindexStatusQuery = useQuery({
    queryKey: ["reindex-status", reindexTaskId],
    queryFn: () =>
      reindexTaskId
        ? llmConfigApi.getReindexStatus(reindexTaskId)
        : Promise.resolve(null),
    enabled: !!reindexTaskId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === "IN_PROGRESS") return 1500;
      return false;
    },
  });

  return {
    configs: configsQuery.data || [],
    isLoadingConfigs: configsQuery.isLoading,
    availableModels: availableModelsQuery.data,
    isLoadingModels: availableModelsQuery.isLoading,
    testAndDiscover: testAndDiscoverMutation.mutateAsync,
    isTesting: testAndDiscoverMutation.isPending,
    saveConfig: saveConfigMutation.mutateAsync,
    isSaving: saveConfigMutation.isPending,
    triggerReindex: reindexMutation.mutateAsync,
    isReindexing: reindexMutation.isPending,
    reindexStatus: reindexStatusQuery.data,
    setReindexTaskId,
  };
}
