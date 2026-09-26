"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Department, Role, User } from "@/lib/api/types";
import { Loader2 } from "lucide-react";
import React, { useEffect, useState } from "react";

interface UserDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user?: User | null;
  roles: Role[];
  departments: Department[];
  onSubmit: (data: {
    email?: string;
    full_name: string;
    role_names: string[];
    department_id?: string | null;
  }) => Promise<void>;
  isSubmitting: boolean;
}

export default function UserDialog({
  open,
  onOpenChange,
  user,
  roles,
  departments,
  onSubmit,
  isSubmitting,
}: UserDialogProps) {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [selectedRole, setSelectedRole] = useState("EMPLOYEE");
  const [departmentId, setDepartmentId] = useState<string>("none");

  useEffect(() => {
    if (user) {
      setEmail(user.email);
      setFullName(user.full_name);
      setSelectedRole(user.roles[0]?.name || "EMPLOYEE");
      setDepartmentId(user.department?.id || "none");
    } else {
      setEmail("");
      setFullName("");
      setSelectedRole("EMPLOYEE");
      setDepartmentId("none");
    }
  }, [user, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || (!user && !email.trim())) return;

    await onSubmit({
      email: user ? undefined : email.trim().toLowerCase(),
      full_name: fullName.trim(),
      role_names: [selectedRole],
      department_id: departmentId === "none" ? null : departmentId,
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-base">
            {user ? "Edit Employee Account" : "Add Employee"}
          </DialogTitle>
          <DialogDescription className="text-xs">
            {user
              ? "Update employee profile details, assigned roles, and department."
              : "A secure random temporary password will be generated automatically."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          {!user && (
            <div className="space-y-1.5">
              <Label htmlFor="user-email" className="text-xs">
                Email Address
              </Label>
              <Input
                id="user-email"
                type="email"
                placeholder="employee@company.internal"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-9 text-sm"
              />
            </div>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="user-fullname" className="text-xs">
              Full Name
            </Label>
            <Input
              id="user-fullname"
              placeholder="e.g. Jane Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="h-9 text-sm"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="user-dept" className="text-xs">
              Department
            </Label>
            <Select value={departmentId} onValueChange={setDepartmentId}>
              <SelectTrigger id="user-dept" className="h-9 text-sm">
                <SelectValue placeholder="Select Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">General / No Department</SelectItem>
                {departments
                  .filter((d) => d.is_active)
                  .map((dept) => (
                    <SelectItem key={dept.id} value={dept.id}>
                      {dept.name} ({dept.code})
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="user-role" className="text-xs">
              System Role
            </Label>
            <Select value={selectedRole} onValueChange={setSelectedRole}>
              <SelectTrigger id="user-role" className="h-9 text-sm">
                <SelectValue placeholder="Select Role" />
              </SelectTrigger>
              <SelectContent>
                {roles.map((role) => (
                  <SelectItem key={role.id} value={role.name}>
                    {role.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              size="sm"
              disabled={
                isSubmitting || !fullName.trim() || (!user && !email.trim())
              }
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                  Saving...
                </>
              ) : user ? (
                "Update User"
              ) : (
                "Create User & Generate Password"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
