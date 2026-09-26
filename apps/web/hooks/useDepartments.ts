"use client";

import {
  CreateDepartmentPayload,
  departmentsApi,
  UpdateDepartmentPayload,
} from "@/lib/api/departments";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useDepartments(includeInactive = false) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["departments", { includeInactive }],
    queryFn: () => departmentsApi.list(includeInactive),
  });

  const createMutation = useMutation({
    mutationFn: (payload: CreateDepartmentPayload) =>
      departmentsApi.create(payload),
    onSuccess: (newDept) => {
      toast.success(`Department "${newDept.name}" created!`);
      queryClient.invalidateQueries({ queryKey: ["departments"] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create department");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: UpdateDepartmentPayload;
    }) => departmentsApi.update(id, payload),
    onSuccess: (updated) => {
      toast.success(`Department "${updated.name}" updated!`);
      queryClient.invalidateQueries({ queryKey: ["departments"] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update department");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => departmentsApi.delete(id),
    onSuccess: () => {
      toast.success("Department deactivated");
      queryClient.invalidateQueries({ queryKey: ["departments"] });
    },
    onError: (err: any) => {
      toast.error(
        err.response?.data?.detail || "Failed to deactivate department",
      );
    },
  });

  return {
    departments: query.data || [],
    isLoading: query.isLoading,
    createDepartment: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateDepartment: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteDepartment: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}
