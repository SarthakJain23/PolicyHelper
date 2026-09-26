"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { documentsApi } from "@/lib/api/documents";
import { MessageCitation } from "@/lib/api/types";
import { ExternalLink, FileText } from "lucide-react";

interface CitationDrawerProps {
  citation: MessageCitation | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function CitationDrawer({
  citation,
  open,
  onOpenChange,
}: CitationDrawerProps) {
  if (!citation) return null;

  const downloadUrl = documentsApi.getDownloadUrl(citation.document_id);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <div className="flex items-center space-x-2 text-neutral-900 dark:text-neutral-50">
            <FileText className="h-5 w-5 text-neutral-600 dark:text-neutral-400" />
            <DialogTitle className="text-base truncate max-w-sm">
              {citation.document_title}
            </DialogTitle>
          </div>
          <DialogDescription className="text-xs">
            Source excerpt extracted from company policy documents.
            {citation.page_number &&
              ` (Referenced Page: ${citation.page_number})`}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-2">
          <div className="rounded-lg border border-neutral-200 bg-neutral-50/70 p-3.5 text-xs leading-relaxed text-neutral-800 font-sans whitespace-pre-wrap dark:border-neutral-800 dark:bg-neutral-900/60 dark:text-neutral-200 max-h-72 overflow-y-auto">
            {citation.snippet}
          </div>

          <div className="flex items-center justify-between pt-2">
            <span className="text-[11px] text-neutral-400">
              Relevance Score:{" "}
              {citation.relevance_score
                ? Math.round(citation.relevance_score * 100) + "%"
                : "High"}
            </span>

            <Button size="sm" variant="outline" asChild className="h-8 text-xs">
              <a
                href={downloadUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center space-x-1.5"
              >
                <span>Open Full Document</span>
                <ExternalLink className="h-3.5 w-3.5 ml-1" />
              </a>
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
