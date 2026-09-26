"use client";

import { API_BASE_URL } from "@/lib/api/client";
import { ChatMessage, MessageCitation } from "@/lib/api/types";
import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import { toast } from "sonner";

export interface StreamState {
  isStreaming: boolean;
  streamingContent: string;
  streamingCitations: MessageCitation[];
}

export function useChatStream(sessionId: string | null) {
  const queryClient = useQueryClient();
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingCitations, setStreamingCitations] = useState<
    MessageCitation[]
  >([]);

  const sendMessage = useCallback(
    async (
      content: string,
      options?: { model?: string; provider?: string },
      targetSessionId?: string,
    ) => {
      const effectiveSessionId = targetSessionId || sessionId;
      if (!effectiveSessionId || !content.trim() || isStreaming) return;

      setIsStreaming(true);
      setStreamingContent("");
      setStreamingCitations([]);

      // Optimistically append user message in local react query cache
      const tempUserMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        session_id: effectiveSessionId,
        sender: "USER",
        content: content.trim(),
        prompt_tokens: 0,
        completion_tokens: 0,
        metadata: {},
        created_at: new Date().toISOString(),
        citations: [],
      };

      queryClient.setQueryData(
        ["chat", "session", effectiveSessionId],
        (oldData: any) => {
          if (!oldData) {
            return {
              id: effectiveSessionId,
              title: "New Conversation",
              messages: [tempUserMessage],
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              message_count: 1,
              is_title_auto_generated: false,
              is_pinned: false,
              is_archived: false,
            };
          }
          return {
            ...oldData,
            messages: [...(oldData.messages || []), tempUserMessage],
          };
        },
      );

      try {
        const response = await fetch(
          `${API_BASE_URL}/chat/sessions/${effectiveSessionId}/stream`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include", // Sends HttpOnly auth cookies with the request automatically
            body: JSON.stringify({
              content: content.trim(),
              model: options?.model,
              provider: options?.provider,
            }),
          },
        );

        if (!response.ok) {
          throw new Error(
            `Server returned ${response.status}: ${response.statusText}`,
          );
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder("utf-8");

        if (!reader) throw new Error("Response body is not readable");

        let buffer = "";
        let accumulatedTokens = "";
        const accumulatedCitations: MessageCitation[] = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            const cleanLine = line.trim();
            if (!cleanLine.startsWith("data: ")) continue;

            const jsonStr = cleanLine.replace("data: ", "").trim();
            try {
              const eventPayload = JSON.parse(jsonStr);
              const { event, data } = eventPayload;

              if (event === "citation") {
                accumulatedCitations.push(data);
                setStreamingCitations([...accumulatedCitations]);
              } else if (event === "token") {
                accumulatedTokens += data.content;
                setStreamingContent(accumulatedTokens);
              } else if (event === "session_updated") {
                // Invalidate session listing to update the sidebar title
                queryClient.invalidateQueries({
                  queryKey: ["chat", "sessions"],
                });
              } else if (event === "done") {
                // Done event
              } else if (event === "error") {
                toast.error(data.message || "Error during response streaming");
              }
            } catch (e) {
              console.error("Failed to parse SSE payload:", jsonStr, e);
            }
          }
        }
      } catch (err: any) {
        console.error("Stream error:", err);
        toast.error(err.message || "Failed to stream assistant response");
      } finally {
        setIsStreaming(false);
        setStreamingContent("");
        setStreamingCitations([]);
        // Re-sync authoritative message list from DB
        queryClient.invalidateQueries({
          queryKey: ["chat", "session", effectiveSessionId],
        });
        queryClient.invalidateQueries({ queryKey: ["chat", "sessions"] });
      }
    },
    [sessionId, isStreaming, queryClient],
  );

  return {
    sendMessage,
    isStreaming,
    streamingContent,
    streamingCitations,
  };
}
