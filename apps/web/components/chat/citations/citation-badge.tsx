"use client";

import { MessageCitation } from "@/lib/api/types";
import { FileText } from "lucide-react";

interface CitationBadgeProps {
  citation: MessageCitation;
  index: number;
  onClick: (citation: MessageCitation) => void;
}

export default function CitationBadge({
  citation,
  index,
  onClick,
}: CitationBadgeProps) {
  return (
    <button
      type="button"
      onClick={() => onClick(citation)}
      className="inline-flex items-center space-x-1.5 rounded-full border border-neutral-200 bg-neutral-100/80 px-2.5 py-1 text-[11px] font-medium text-neutral-800 transition-colors hover:bg-neutral-200 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-200 dark:hover:bg-neutral-700 cursor-pointer shadow-2xs"
    >
      <FileText className="h-3 w-3 text-neutral-500" />
      <span className="truncate max-w-[140px]">{citation.document_title}</span>
      {citation.page_number && (
        <span className="text-neutral-500 font-mono">
          p.{citation.page_number}
        </span>
      )}
    </button>
  );
}
