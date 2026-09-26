"use client";

import { documentsApi, UploadDocumentPayload } from "@/lib/api/documents";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useDocuments(category?: string, departmentId?: string) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["documents", { category, departmentId }],
    queryFn: () => documentsApi.list({ category, department_id: departmentId }),
    // Poll every 3 seconds if any document is PENDING or PROCESSING
    refetchInterval: (query) => {
      const hasProcessing = query.state.data?.some(
        (doc) => doc.status === "PENDING" || doc.status === "PROCESSING",
      );
      return hasProcessing ? 3000 : false;
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (payload: UploadDocumentPayload) =>
      documentsApi.upload(payload),
    onSuccess: (newDoc) => {
      toast.success(`"${newDoc.title}" uploaded! Indexing in background...`);
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Document upload failed");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess: () => {
      toast.success("Document and its vector chunks deleted");
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to delete document");
    },
  });

  return {
    documents: query.data || [],
    isLoading: query.isLoading,
    refetch: query.refetch,
    uploadDocument: uploadMutation.mutateAsync,
    isUploading: uploadMutation.isPending,
    deleteDocument: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}
