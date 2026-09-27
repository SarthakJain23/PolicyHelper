"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage, MessageCitation } from "@/lib/api/types";
import { useEffect, useRef } from "react";
import EmptyChatState from "./empty-chat-state";
import MessageItem from "./message-item";

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;
  streamingCitations: MessageCitation[];
  onCitationClick: (citation: MessageCitation) => void;
  onSuggestedClick: (query: string) => void;
}

export default function MessageList({
  messages,
  isStreaming,
  streamingContent,
  streamingCitations,
  onCitationClick,
  onSuggestedClick,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isStreaming) {
    return <EmptyChatState onSuggestedClick={onSuggestedClick} />;
  }

  return (
    <ScrollArea className="flex-1 min-h-0 h-full w-full">
      <div className="max-w-3xl mx-auto px-4 sm:px-8 py-4 space-y-2">
        {messages.map((msg) => (
          <MessageItem
            key={msg.id}
            message={msg}
            onCitationClick={onCitationClick}
          />
        ))}

        {/* Live Streaming Assistant Message */}
        {isStreaming && streamingContent && (
          <MessageItem
            message={{
              id: "streaming-active",
              session_id: "active",
              sender: "ASSISTANT",
              content: streamingContent,
              prompt_tokens: 0,
              completion_tokens: 0,
              metadata: {},
              created_at: new Date().toISOString(),
              citations: streamingCitations,
            }}
            isStreaming={true}
            onCitationClick={onCitationClick}
          />
        )}

        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
