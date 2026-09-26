"use client";

import DashboardShell from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import PasswordRevealDialog from "@/components/users/password-reveal-dialog";
import UserDialog from "@/components/users/user-dialog";
import UserTable from "@/components/users/user-table";
import { useAuth } from "@/hooks/useAuth";
import { useDepartments } from "@/hooks/useDepartments";
import { useUsers } from "@/hooks/useUsers";
import { User } from "@/lib/api/types";
import { Plus, Users as UsersIcon } from "lucide-react";
import { useState } from "react";

export default function UsersPage() {
  const { isSuperAdmin, isHrAdmin } = useAuth();
  const {
    users,
    isLoadingUsers,
    roles,
    createUser,
    isCreating,
    updateUser,
    isUpdating,
    resetPassword,
  } = useUsers();
  const { departments } = useDepartments();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const [passwordRevealOpen, setPasswordRevealOpen] = useState(false);
  const [revealedCreds, setRevealedCreds] = useState<{
    email: string;
    temporaryPassword: string;
  }>({
    email: "",
    temporaryPassword: "",
  });

  const handleOpenCreate = () => {
    setSelectedUser(null);
    setDialogOpen(true);
  };

  const handleOpenEdit = (user: User) => {
    setSelectedUser(user);
    setDialogOpen(true);
  };

  const handleResetPassword = async (user: User) => {
    const res = await resetPassword(user.id);
    if (res?.temporary_password) {
      setRevealedCreds({
        email: user.email,
        temporaryPassword: res.temporary_password,
      });
      setPasswordRevealOpen(true);
    }
  };

  const handleSubmit = async (data: {
    email?: string;
    full_name: string;
    role_names: string[];
    department_id?: string | null;
  }) => {
    if (selectedUser) {
      await updateUser({
        id: selectedUser.id,
        payload: {
          full_name: data.full_name,
          role_names: data.role_names,
          department_id: data.department_id,
        },
      });
    } else {
      if (!data.email) return;
      const res = await createUser({
        email: data.email,
        full_name: data.full_name,
        role_names: data.role_names,
        department_id: data.department_id,
      });
      if (res?.temporary_password) {
        setRevealedCreds({
          email: data.email,
          temporaryPassword: res.temporary_password,
        });
        setPasswordRevealOpen(true);
      }
    }
  };

  return (
    <DashboardShell>
      <div className="flex-1 space-y-4 p-4 sm:p-6 max-w-7xl mx-auto w-full">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-neutral-200 dark:border-neutral-800">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50 flex items-center space-x-2">
              <UsersIcon className="h-5 w-5" />
              <span>Users & Access Control</span>
            </h1>
            <p className="text-xs text-neutral-500 mt-0.5">
              Manage employee accounts, role-based access rules, and
              credentials.
            </p>
          </div>

          {(isSuperAdmin || isHrAdmin) && (
            <Button
              size="sm"
              onClick={handleOpenCreate}
              className="h-8 text-xs font-medium"
            >
              <Plus className="mr-1.5 h-3.5 w-3.5" />
              <span>Add Employee</span>
            </Button>
          )}
        </div>

        {/* User Table */}
        {isLoadingUsers ? (
          <div className="p-8 text-center text-xs text-neutral-500">
            Loading user accounts...
          </div>
        ) : (
          <UserTable
            users={users}
            onEdit={handleOpenEdit}
            onResetPassword={handleResetPassword}
          />
        )}

        {/* User Dialog */}
        <UserDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          user={selectedUser}
          roles={roles}
          departments={departments}
          onSubmit={handleSubmit}
          isSubmitting={isCreating || isUpdating}
        />

        {/* Password Reveal Dialog */}
        <PasswordRevealDialog
          open={passwordRevealOpen}
          onOpenChange={setPasswordRevealOpen}
          email={revealedCreds.email}
          temporaryPassword={revealedCreds.temporaryPassword}
        />
      </div>
    </DashboardShell>
  );
}
