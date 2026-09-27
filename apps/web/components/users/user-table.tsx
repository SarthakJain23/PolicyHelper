"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User } from "@/lib/api/types";
import { formatDate } from "@/lib/utils";
import {
  KeyRound,
  MoreHorizontal,
  Pencil,
  Users as UsersIcon,
} from "lucide-react";

interface UserTableProps {
  users: User[];
  onEdit: (user: User) => void;
  onResetPassword: (user: User) => void;
}

const getRoleBadgeStyle = (roleName: string) => {
  switch (roleName.toUpperCase()) {
    case "SUPER_ADMIN":
      return "border-purple-200 bg-purple-50 text-purple-700 dark:border-purple-900/60 dark:bg-purple-950/50 dark:text-purple-300";
    case "HR_ADMIN":
      return "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900/60 dark:bg-blue-950/50 dark:text-blue-300";
    case "MANAGER":
      return "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900/60 dark:bg-amber-950/50 dark:text-amber-300";
    case "EMPLOYEE":
      return "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/60 dark:bg-emerald-950/50 dark:text-emerald-300";
    default:
      return "border-neutral-200 bg-neutral-50 text-neutral-700 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-300";
  }
};

export default function UserTable({
  users,
  onEdit,
  onResetPassword,
}: UserTableProps) {
  if (users.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed rounded-lg border-neutral-200 dark:border-neutral-800">
        <UsersIcon className="h-10 w-10 text-neutral-400 mb-3" />
        <h3 className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
          No users found
        </h3>
        <p className="text-xs text-neutral-500 mt-1 max-w-sm">
          Add employees to the platform to grant access to company policy chat
          and search.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-neutral-200 bg-white overflow-hidden dark:border-neutral-800 dark:bg-neutral-950 shadow-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-neutral-50 border-b border-neutral-200 font-medium text-neutral-500 dark:bg-neutral-900 dark:border-neutral-800 dark:text-neutral-400">
            <tr>
              <th className="px-4 py-3">Employee</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Roles</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800 text-neutral-800 dark:text-neutral-200">
            {users.map((u) => (
              <tr
                key={u.id}
                className="hover:bg-neutral-50/70 transition-colors dark:hover:bg-neutral-900/50"
              >
                <td className="px-4 py-3">
                  <div className="flex items-center space-x-2.5">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-neutral-100 font-semibold text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
                      {u.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">
                        {u.full_name}
                      </p>
                      <p className="text-neutral-500 text-[11px]">{u.email}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  {u.department ? (
                    <span className="font-medium text-neutral-800 dark:text-neutral-200">
                      {u.department.name}
                    </span>
                  ) : (
                    <span className="text-neutral-400">General / All</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {u.roles.map((r) => (
                      <Badge
                        key={r.id}
                        variant="outline"
                        className={`text-[10px] py-0 font-medium ${getRoleBadgeStyle(r.name)}`}
                      >
                        {r.name}
                      </Badge>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center space-x-1.5">
                    <Badge variant={u.is_active ? "success" : "secondary"}>
                      {u.is_active ? "Active" : "Inactive"}
                    </Badge>
                    {u.must_change_password && (
                      <Badge variant="warning" className="text-[10px]">
                        Pending Reset
                      </Badge>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 text-neutral-500">
                  {formatDate(u.created_at)}
                </td>
                <td className="px-4 py-3 text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <MoreHorizontal className="h-3.5 w-3.5" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-44">
                      <DropdownMenuItem
                        onClick={() => onEdit(u)}
                        className="text-xs"
                      >
                        <Pencil className="mr-2 h-3.5 w-3.5" />
                        <span>Edit Account</span>
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => onResetPassword(u)}
                        className="text-xs"
                      >
                        <KeyRound className="mr-2 h-3.5 w-3.5" />
                        <span>Regenerate Password</span>
                      </DropdownMenuItem>
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
