"use client";

import { authApi } from "@/lib/api/auth";
import { LoginResponse, User } from "@/lib/api/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const userQuery = useQuery<User | null>({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      try {
        return await authApi.getMe();
      } catch {
        return null;
      }
    },
    staleTime: 1000 * 60 * 5,
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: async ({
      email,
      password,
    }: {
      email: string;
      password: string;
    }) => {
      return await authApi.login(email, password);
    },
    onSuccess: (data: LoginResponse) => {
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });

      if (data.must_change_password) {
        toast.info(
          "First login detected. Please change your password to continue.",
        );
        router.push("/change-password");
      } else {
        toast.success(`Welcome back, ${data.full_name}!`);
        router.push("/chat");
      }
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || "Invalid email or password";
      toast.error(msg);
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: async ({
      current_password,
      new_password,
    }: {
      current_password: string;
      new_password: string;
    }) => {
      return await authApi.changePassword(current_password, new_password);
    },
    onSuccess: () => {
      toast.success("Password changed successfully!");
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      router.push("/chat");
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || "Failed to update password";
      toast.error(msg);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      try {
        await authApi.logout();
      } catch {
        // Ignore errors during logout
      }
    },
    onSettled: () => {
      queryClient.clear();
      router.push("/login");
    },
  });

  const currentUser = userQuery.data;
  const isSuperAdmin =
    currentUser?.roles.some((r) => r.name === "SUPER_ADMIN") || false;
  const isHrAdmin =
    isSuperAdmin ||
    currentUser?.roles.some((r) => r.name === "HR_ADMIN") ||
    false;
  const isManager =
    isHrAdmin || currentUser?.roles.some((r) => r.name === "MANAGER") || false;

  return {
    user: currentUser,
    isLoading: userQuery.isLoading,
    isSuperAdmin,
    isHrAdmin,
    isManager,
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    changePassword: changePasswordMutation.mutateAsync,
    isChangingPassword: changePasswordMutation.isPending,
    logout: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,
  };
}
