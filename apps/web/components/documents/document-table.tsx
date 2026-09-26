"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { documentsApi } from "@/lib/api/documents";
import { DocumentItem } from "@/lib/api/types";
import { formatBytes, formatDate } from "@/lib/utils";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Download,
  FileText,
  Loader2,
  MoreHorizontal,
  RotateCw,
  Trash2,
} from "lucide-react";

interface DocumentTableProps {
  documents: DocumentItem[];
  onDelete: (id: string) => void;
  onRetry?: (id: string) => void;
  isRetrying?: boolean;
  retryingId?: string;
  isHrAdmin: boolean;
}

export default function DocumentTable({
  documents,
  onDelete,
  onRetry,
  isRetrying,
  retryingId,
  isHrAdmin,
}: DocumentTableProps) {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed rounded-lg border-neutral-200 dark:border-neutral-800">
        <FileText className="h-10 w-10 text-neutral-400 mb-3" />
        <h3 className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
          No policy documents uploaded
        </h3>
        <p className="text-xs text-neutral-500 mt-1 max-w-sm">
          Upload PDF, Word, or Markdown files to build the company AI knowledge
          base.
        </p>
      </div>
    );
  }

  const renderStatus = (doc: DocumentItem) => {
    switch (doc.status) {
      case "INDEXED":
        return (
          <Badge variant="success" className="space-x-1">
            <CheckCircle2 className="h-3 w-3" />
            <span>Indexed</span>
          </Badge>
        );
      case "PROCESSING":
        return (
          <Badge variant="warning" className="space-x-1 animate-pulse">
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>Processing</span>
          </Badge>
        );
      case "PENDING":
        return (
          <Badge variant="secondary" className="space-x-1">
            <Clock className="h-3 w-3" />
            <span>Pending</span>
          </Badge>
        );
      case "FAILED":
        return (
          <div className="flex flex-col gap-1 items-start">
            <div className="flex items-center gap-1.5 flex-wrap">
              <Badge
                variant="destructive"
                className="space-x-1 cursor-help"
                title={doc.error_message || "Ingestion failed"}
              >
                <AlertCircle className="h-3 w-3" />
                <span>Failed</span>
              </Badge>
              {isHrAdmin && onRetry && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRetry(doc.id)}
                  disabled={isRetrying && retryingId === doc.id}
                  className="h-5 px-1.5 text-[10px] font-medium border-red-200 text-red-700 hover:bg-red-50 dark:border-red-800 dark:text-red-300 dark:hover:bg-red-950/40"
                  title="Retry Ingestion"
                >
                  {isRetrying && retryingId === doc.id ? (
                    <Loader2 className="h-2.5 w-2.5 animate-spin mr-1" />
                  ) : (
                    <RotateCw className="h-2.5 w-2.5 mr-1" />
                  )}
                  <span>Retry</span>
                </Button>
              )}
            </div>
            {doc.error_message && (
              <p
                className="text-[10px] text-red-500 max-w-56 truncate"
                title={doc.error_message}
              >
                {doc.error_message}
              </p>
            )}
          </div>
        );
    }
  };

  return (
    <div className="rounded-lg border border-neutral-200 bg-white overflow-hidden dark:border-neutral-800 dark:bg-neutral-950 shadow-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-neutral-50 border-b border-neutral-200 font-medium text-neutral-500 dark:bg-neutral-900 dark:border-neutral-800 dark:text-neutral-400">
            <tr>
              <th className="px-4 py-3">Document Title</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Size & Chunks</th>
              <th className="px-4 py-3">Uploaded</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800 text-neutral-800 dark:text-neutral-200">
            {documents.map((doc) => (
              <tr
                key={doc.id}
                className="hover:bg-neutral-50/70 transition-colors dark:hover:bg-neutral-900/50"
              >
                <td className="px-4 py-3">
                  <div className="flex items-center space-x-2.5">
                    <FileText className="h-4 w-4 text-neutral-500 shrink-0" />
                    <div>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">
                        {doc.title}
                      </p>
                      <p className="text-neutral-400 text-[11px] truncate max-w-xs">
                        {doc.file_name}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <Badge variant="outline" className="text-[10px]">
                    {doc.category}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-neutral-600 dark:text-neutral-400">
                  {doc.department ? doc.department.name : "Company-Wide"}
                </td>
                <td className="px-4 py-3">{renderStatus(doc)}</td>
                <td className="px-4 py-3 text-neutral-500">
                  <span>{formatBytes(doc.file_size)}</span>
                  {doc.status === "INDEXED" && (
                    <span className="text-neutral-400 ml-1.5">
                      ({doc.chunk_count} chunks)
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-neutral-500">
                  {formatDate(doc.created_at)}
                </td>
                <td className="px-4 py-3 text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <MoreHorizontal className="h-3.5 w-3.5" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-40">
                      <DropdownMenuItem asChild>
                        <a
                          href={documentsApi.getDownloadUrl(doc.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center text-xs"
                        >
                          <Download className="mr-2 h-3.5 w-3.5" />
                          <span>Download / View</span>
                        </a>
                      </DropdownMenuItem>
                      {isHrAdmin && onRetry && doc.status === "FAILED" && (
                        <DropdownMenuItem
                          onClick={() => onRetry(doc.id)}
                          disabled={isRetrying && retryingId === doc.id}
                          className="text-xs text-amber-600 focus:text-amber-600"
                        >
                          <RotateCw className="mr-2 h-3.5 w-3.5" />
                          <span>Retry Ingestion</span>
                        </DropdownMenuItem>
                      )}
                      {isHrAdmin && (
                        <DropdownMenuItem
                          onClick={() => onDelete(doc.id)}
                          className="text-xs text-red-600 focus:text-red-600"
                        >
                          <Trash2 className="mr-2 h-3.5 w-3.5" />
                          <span>Delete Document</span>
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
