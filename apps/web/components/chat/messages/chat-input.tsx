"use client";

import { Button } from "@/components/ui/button";
import { ArrowUp, Loader2 } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [content, setContent] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [content]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || disabled) return;
    onSend(content.trim());
    setContent("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto p-4">
      <form
        onSubmit={handleSubmit}
        className="relative flex items-end rounded-2xl border border-neutral-200/90 bg-white shadow-sm p-1.5 focus-within:border-neutral-400 focus-within:ring-1 focus-within:ring-neutral-400 dark:border-neutral-800 dark:bg-neutral-950"
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question regarding company policies..."
          disabled={disabled}
          className="flex-1 resize-none bg-transparent px-3 py-2 text-xs sm:text-sm focus:outline-none placeholder:text-neutral-400 text-neutral-800 dark:text-neutral-200 max-h-40 overflow-y-auto"
        />

        <Button
          type="submit"
          size="icon"
          disabled={disabled || !content.trim()}
          className="h-8 w-8 rounded-xl shrink-0 bg-neutral-900 text-white hover:bg-neutral-800 dark:bg-neutral-100 dark:text-neutral-900 shadow-xs"
        >
          {disabled ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <ArrowUp className="h-4 w-4" />
          )}
        </Button>
      </form>
    </div>
  );
}
