"use client";

import {
  chatApi,
  CreateSessionPayload,
  UpdateSessionPayload,
} from "@/lib/api/chat";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useChatSessions(includeArchived = false) {
  const queryClient = useQueryClient();

  const sessionsQuery = useQuery({
    queryKey: ["chat", "sessions", { includeArchived }],
    queryFn: () => chatApi.listSessions(includeArchived),
  });

  const createSessionMutation = useMutation({
    mutationFn: (payload: CreateSessionPayload = {}) =>
      chatApi.createSession(payload),
    onSuccess: (newSession) => {
      queryClient.invalidateQueries({ queryKey: ["chat", "sessions"] });
      return newSession;
    },
    onError: (err: any) => {
      toast.error(
        err.response?.data?.detail || "Failed to create conversation",
      );
    },
  });

  const updateSessionMutation = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: UpdateSessionPayload;
    }) => chatApi.updateSession(id, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["chat", "sessions"] });
      queryClient.invalidateQueries({
        queryKey: ["chat", "session", updated.id],
      });
    },
    onError: (err: any) => {
      toast.error(
        err.response?.data?.detail || "Failed to update conversation",
      );
    },
  });

  const deleteSessionMutation = useMutation({
    mutationFn: (id: string) => chatApi.deleteSession(id),
    onSuccess: () => {
      toast.success("Conversation deleted");
      queryClient.invalidateQueries({ queryKey: ["chat", "sessions"] });
    },
    onError: (err: any) => {
      toast.error(
        err.response?.data?.detail || "Failed to delete conversation",
      );
    },
  });

  return {
    sessions: sessionsQuery.data || [],
    isLoading: sessionsQuery.isLoading,
    createSession: createSessionMutation.mutateAsync,
    isCreating: createSessionMutation.isPending,
    updateSession: updateSessionMutation.mutateAsync,
    isUpdating: updateSessionMutation.isPending,
    deleteSession: deleteSessionMutation.mutateAsync,
    isDeleting: deleteSessionMutation.isPending,
  };
}

export function useChatSession(sessionId: string | null) {
  return useQuery({
    queryKey: ["chat", "session", sessionId],
    queryFn: () => (sessionId ? chatApi.getSession(sessionId) : null),
    enabled: !!sessionId,
  });
}

