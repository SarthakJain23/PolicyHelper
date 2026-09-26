"use client";

import DocumentTable from "@/components/documents/document-table";
import DocumentUploadDialog from "@/components/documents/document-upload-dialog";
import DashboardShell from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useDepartments } from "@/hooks/useDepartments";
import { useDocuments } from "@/hooks/useDocuments";
import { FileText, Plus, RefreshCw } from "lucide-react";
import { useState } from "react";

export default function DocumentsPage() {
  const { isSuperAdmin, isHrAdmin } = useAuth();
  const {
    documents,
    isLoading,
    refetch,
    uploadDocument,
    isUploading,
    deleteDocument,
    retryDocument,
    isRetrying,
    retryingId,
  } = useDocuments();
  const { departments } = useDepartments();

  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  const handleUpload = async (data: {
    file: File;
    title: string;
    category: string;
    department_id?: string | null;
    allowed_roles: string[];
  }) => {
    await uploadDocument({
      file: data.file,
      title: data.title,
      category: data.category,
      department_id: data.department_id,
      allowed_roles: data.allowed_roles,
    });
  };

  return (
    <DashboardShell>
      <div className="flex-1 space-y-4 p-4 sm:p-6 max-w-7xl mx-auto w-full">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-neutral-200 dark:border-neutral-800">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50 flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>Policy Knowledge Base</span>
            </h1>
            <p className="text-xs text-neutral-500 mt-0.5">
              Upload, inspect, and manage company handbook files and policies.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              className="h-8 text-xs font-medium"
            >
              <RefreshCw className="mr-1.5 h-3 w-3" />
              <span>Refresh</span>
            </Button>
            {(isSuperAdmin || isHrAdmin) && (
              <Button
                size="sm"
                onClick={() => setUploadDialogOpen(true)}
                className="h-8 text-xs font-medium"
              >
                <Plus className="mr-1.5 h-3.5 w-3.5" />
                <span>Upload Policy</span>
              </Button>
            )}
          </div>
        </div>

        {/* Documents Table */}
        {isLoading ? (
          <div className="p-8 text-center text-xs text-neutral-500">
            Loading policy documents...
          </div>
        ) : (
          <DocumentTable
            documents={documents}
            onDelete={(id) => deleteDocument(id)}
            onRetry={(id) => retryDocument(id)}
            isRetrying={isRetrying}
            retryingId={retryingId}
            isHrAdmin={isSuperAdmin || isHrAdmin}
          />
        )}

        {/* Upload Dialog */}
        <DocumentUploadDialog
          open={uploadDialogOpen}
          onOpenChange={setUploadDialogOpen}
          departments={departments}
          onUpload={handleUpload}
          isUploading={isUploading}
        />
      </div>
    </DashboardShell>
  );
}
