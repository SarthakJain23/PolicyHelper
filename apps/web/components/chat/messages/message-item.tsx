"use client";

import CitationBadge from "@/components/chat/citations/citation-badge";
import { ChatMessage, MessageCitation } from "@/lib/api/types";
import { cn } from "@/lib/utils";
import { BookOpen, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import StreamingCursor from "./streaming-cursor";

interface MessageItemProps {
  message: ChatMessage;
  isStreaming?: boolean;
  onCitationClick: (citation: MessageCitation) => void;
}

export default function MessageItem({
  message,
  isStreaming,
  onCitationClick,
}: MessageItemProps) {
  const isUser = message.sender === "USER";

  return (
    <div
      className={cn(
        "flex w-full space-x-3 py-4 text-xs sm:text-sm leading-relaxed",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && (
        <div className="flex h-7 w-7 shrink-0 select-none items-center justify-center rounded-md bg-neutral-900 text-white shadow-xs dark:bg-neutral-100 dark:text-neutral-900">
          <BookOpen className="h-3.5 w-3.5" />
        </div>
      )}

      <div
        className={cn(
          "max-w-2xl space-y-2 rounded-xl px-4 py-3",
          isUser
            ? "bg-neutral-900 text-neutral-50 shadow-xs dark:bg-neutral-100 dark:text-neutral-900"
            : "bg-white border border-neutral-200/80 text-neutral-800 shadow-2xs dark:border-neutral-800 dark:bg-neutral-950 dark:text-neutral-200",
        )}
      >
        <div className="prose prose-xs sm:prose-sm dark:prose-invert max-w-none break-words">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
          {isStreaming && <StreamingCursor />}
        </div>

        {/* Citations Footer */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-3 pt-2.5 border-t border-neutral-100 dark:border-neutral-800 space-y-1.5">
            <p className="text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">
              Referenced Policies:
            </p>
            <div className="flex flex-wrap gap-1.5">
              {message.citations.map((citation, idx) => (
                <CitationBadge
                  key={citation.id || idx}
                  citation={citation}
                  index={idx + 1}
                  onClick={onCitationClick}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex h-7 w-7 shrink-0 select-none items-center justify-center rounded-full bg-neutral-200 text-neutral-700 shadow-xs dark:bg-neutral-800 dark:text-neutral-300">
          <User className="h-3.5 w-3.5" />
        </div>
      )}
    </div>
  );
}
