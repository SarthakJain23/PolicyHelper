"use client";

import DepartmentDialog from "@/components/departments/department-dialog";
import DepartmentTable from "@/components/departments/department-table";
import DashboardShell from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useDepartments } from "@/hooks/useDepartments";
import { Department } from "@/lib/api/types";
import { Building2, Plus } from "lucide-react";
import { useState } from "react";

export default function DepartmentsPage() {
  const { isSuperAdmin, isHrAdmin } = useAuth();
  const {
    departments,
    isLoading,
    createDepartment,
    isCreating,
    updateDepartment,
    isUpdating,
    deleteDepartment,
  } = useDepartments(true);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedDept, setSelectedDept] = useState<Department | null>(null);

  const handleOpenCreate = () => {
    setSelectedDept(null);
    setDialogOpen(true);
  };

  const handleOpenEdit = (dept: Department) => {
    setSelectedDept(dept);
    setDialogOpen(true);
  };

  const handleSubmit = async (data: {
    name: string;
    code: string;
    description?: string;
  }) => {
    if (selectedDept) {
      await updateDepartment({
        id: selectedDept.id,
        payload: {
          name: data.name,
          code: data.code,
          description: data.description,
        },
      });
    } else {
      await createDepartment({
        name: data.name,
        code: data.code,
        description: data.description,
        is_active: true,
      });
    }
  };

  return (
    <DashboardShell>
      <div className="flex-1 space-y-4 p-4 sm:p-6 max-w-7xl mx-auto w-full">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-neutral-200 dark:border-neutral-800">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50 flex items-center space-x-2">
              <Building2 className="h-5 w-5" />
              <span>Departments</span>
            </h1>
            <p className="text-xs text-neutral-500 mt-0.5">
              Manage company divisions for policy document scoping and role
              assignments.
            </p>
          </div>

          {(isSuperAdmin || isHrAdmin) && (
            <Button
              size="sm"
              onClick={handleOpenCreate}
              className="h-8 text-xs font-medium"
            >
              <Plus className="mr-1.5 h-3.5 w-3.5" />
              <span>Add Department</span>
            </Button>
          )}
        </div>

        {/* Table Content */}
        {isLoading ? (
          <div className="p-8 text-center text-xs text-neutral-500">
            Loading departments...
          </div>
        ) : (
          <DepartmentTable
            departments={departments}
            onEdit={handleOpenEdit}
            onDeactivate={(id) => deleteDepartment(id)}
            isSuperAdmin={isSuperAdmin}
          />
        )}

        {/* Create / Edit Dialog */}
        <DepartmentDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          department={selectedDept}
          onSubmit={handleSubmit}
          isSubmitting={isCreating || isUpdating}
        />
      </div>
    </DashboardShell>
  );
}
