"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Department } from "@/lib/api/types";
import { formatDate } from "@/lib/utils";
import { Building2, MoreHorizontal, Pencil, PowerOff } from "lucide-react";

interface DepartmentTableProps {
  departments: Department[];
  onEdit: (dept: Department) => void;
  onDeactivate: (id: string) => void;
  isSuperAdmin: boolean;
}

export default function DepartmentTable({
  departments,
  onEdit,
  onDeactivate,
  isSuperAdmin,
}: DepartmentTableProps) {
  if (departments.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed rounded-lg border-neutral-200 dark:border-neutral-800">
        <Building2 className="h-10 w-10 text-neutral-400 mb-3" />
        <h3 className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
          No departments found
        </h3>
        <p className="text-xs text-neutral-500 mt-1 max-w-sm">
          Create company departments to organize policy documents and assign
          access permissions.
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
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Department Name</th>
              <th className="px-4 py-3">Description</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800 text-neutral-800 dark:text-neutral-200">
            {departments.map((dept) => (
              <tr
                key={dept.id}
                className="hover:bg-neutral-50/70 transition-colors dark:hover:bg-neutral-900/50"
              >
                <td className="px-4 py-3 font-mono font-semibold text-neutral-900 dark:text-neutral-100">
                  {dept.code}
                </td>
                <td className="px-4 py-3 font-medium text-neutral-900 dark:text-neutral-100">
                  {dept.name}
                </td>
                <td className="px-4 py-3 text-neutral-500 max-w-xs truncate">
                  {dept.description || "—"}
                </td>
                <td className="px-4 py-3">
                  <Badge variant={dept.is_active ? "success" : "secondary"}>
                    {dept.is_active ? "Active" : "Inactive"}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-neutral-500">
                  {formatDate(dept.created_at)}
                </td>
                <td className="px-4 py-3 text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <MoreHorizontal className="h-3.5 w-3.5" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-40">
                      <DropdownMenuItem
                        onClick={() => onEdit(dept)}
                        className="text-xs"
                      >
                        <Pencil className="mr-2 h-3.5 w-3.5" />
                        <span>Edit Details</span>
                      </DropdownMenuItem>
                      {dept.is_active && dept.code !== "GENERAL" && (
                        <DropdownMenuItem
                          onClick={() => onDeactivate(dept.id)}
                          className="text-xs text-red-600 focus:text-red-600"
                        >
                          <PowerOff className="mr-2 h-3.5 w-3.5" />
                          <span>Deactivate</span>
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
