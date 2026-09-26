"use client";

import {
  organizationApi,
  UpdateOrganizationPayload,
} from "@/lib/api/organization";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useOrganization() {
  const queryClient = useQueryClient();

  const organizationQuery = useQuery({
    queryKey: ["organization"],
    queryFn: organizationApi.getOrganization,
    staleTime: 5 * 60 * 1000,
  });

  const updateOrganizationMutation = useMutation({
    mutationFn: (payload: UpdateOrganizationPayload) =>
      organizationApi.updateOrganization(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["organization"], data);
      toast.success("Organization updated successfully");
    },
    onError: (err: any) => {
      toast.error(
        err.response?.data?.detail || "Failed to update organization",
      );
    },
  });

  return {
    organization: organizationQuery.data,
    isLoading: organizationQuery.isLoading,
    isError: organizationQuery.isError,
    updateOrganization: updateOrganizationMutation.mutateAsync,
    isUpdating: updateOrganizationMutation.isPending,
  };
}
