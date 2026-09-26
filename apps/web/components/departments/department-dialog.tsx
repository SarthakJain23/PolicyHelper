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
import { Department } from "@/lib/api/types";
import { Loader2 } from "lucide-react";
import React, { useEffect, useState } from "react";

interface DepartmentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  department?: Department | null;
  onSubmit: (data: {
    name: string;
    code: string;
    description?: string;
  }) => Promise<void>;
  isSubmitting: boolean;
}

export default function DepartmentDialog({
  open,
  onOpenChange,
  department,
  onSubmit,
  isSubmitting,
}: DepartmentDialogProps) {
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (department) {
      setName(department.name);
      setCode(department.code);
      setDescription(department.description || "");
    } else {
      setName("");
      setCode("");
      setDescription("");
    }
  }, [department, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !code.trim()) return;
    await onSubmit({
      name: name.trim(),
      code: code.trim().toUpperCase(),
      description: description.trim() || undefined,
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-base">
            {department ? "Edit Department" : "Create Department"}
          </DialogTitle>
          <DialogDescription className="text-xs">
            Organizational units used to scope policy documents and employee
            access.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="dept-name" className="text-xs">
              Department Name
            </Label>
            <Input
              id="dept-name"
              placeholder="e.g. Human Resources, Engineering"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="h-9 text-sm"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="dept-code" className="text-xs">
              Department Code
            </Label>
            <Input
              id="dept-code"
              placeholder="e.g. HR, ENG, SALES"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              required
              disabled={!!department} // Lock code on edit
              className="h-9 text-sm font-mono uppercase"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="dept-desc" className="text-xs">
              Description (Optional)
            </Label>
            <Input
              id="dept-desc"
              placeholder="Brief description of department scope"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="h-9 text-sm"
            />
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
              disabled={isSubmitting || !name.trim() || !code.trim()}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                  Saving...
                </>
              ) : department ? (
                "Update Department"
              ) : (
                "Create Department"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
