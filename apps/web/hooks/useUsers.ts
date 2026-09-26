"use client";

import {
  CreateUserPayload,
  UpdateUserPayload,
  usersApi,
} from "@/lib/api/users";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useUsers(departmentId?: string, roleName?: string) {
  const queryClient = useQueryClient();

  const usersQuery = useQuery({
    queryKey: ["users", { departmentId, roleName }],
    queryFn: () =>
      usersApi.list({ department_id: departmentId, role_name: roleName }),
  });

  const rolesQuery = useQuery({
    queryKey: ["roles"],
    queryFn: () => usersApi.listRoles(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: CreateUserPayload) => usersApi.create(payload),
    onSuccess: (data) => {
      toast.success(`User "${data.user.email}" created successfully!`);
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to create user");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateUserPayload }) =>
      usersApi.update(id, payload),
    onSuccess: () => {
      toast.success("User updated successfully");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to update user");
    },
  });

  const resetPasswordMutation = useMutation({
    mutationFn: (id: string) => usersApi.resetPassword(id),
    onSuccess: () => {
      toast.success("Temporary password regenerated");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to reset password");
    },
  });

  return {
    users: usersQuery.data || [],
    isLoadingUsers: usersQuery.isLoading,
    roles: rolesQuery.data || [],
    isLoadingRoles: rolesQuery.isLoading,
    createUser: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateUser: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    resetPassword: resetPasswordMutation.mutateAsync,
    isResettingPassword: resetPasswordMutation.isPending,
  };
}
