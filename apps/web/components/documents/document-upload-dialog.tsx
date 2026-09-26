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
import { Department } from "@/lib/api/types";
import { formatBytes } from "@/lib/utils";
import { FileText, Loader2, Upload, X } from "lucide-react";
import React, { useRef, useState } from "react";

interface DocumentUploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  departments: Department[];
  onUpload: (data: {
    file: File;
    title: string;
    category: string;
    department_id?: string | null;
    allowed_roles: string[];
  }) => Promise<void>;
  isUploading: boolean;
}

export default function DocumentUploadDialog({
  open,
  onOpenChange,
  departments,
  onUpload,
  isUploading,
}: DocumentUploadDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("HR");
  const [departmentId, setDepartmentId] = useState("none");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!title) {
        // Remove extension for default title
        const cleanName = selected.name.replace(/\.[^/.]+$/, "");
        setTitle(cleanName);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title.trim()) return;

    await onUpload({
      file,
      title: title.trim(),
      category: category.toUpperCase(),
      department_id: departmentId === "none" ? null : departmentId,
      allowed_roles: ["EMPLOYEE", "MANAGER", "HR_ADMIN", "SUPER_ADMIN"],
    });

    setFile(null);
    setTitle("");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-base">
            Upload Policy Document
          </DialogTitle>
          <DialogDescription className="text-xs">
            Upload PDF, Word (.docx), or Markdown (.md) documents to be indexed
            for semantic search.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          {/* File Dropzone Area */}
          <div className="space-y-1.5">
            <Label className="text-xs">Select Document File</Label>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.doc,.md,.txt"
              onChange={handleFileChange}
              className="hidden"
            />
            {file ? (
              <div className="flex items-center justify-between rounded-lg border border-neutral-200 bg-neutral-50 p-3 dark:border-neutral-800 dark:bg-neutral-900">
                <div className="flex items-center space-x-2.5 overflow-hidden">
                  <FileText className="h-5 w-5 text-neutral-500 shrink-0" />
                  <div className="truncate text-xs">
                    <p className="font-medium text-neutral-900 dark:text-neutral-100 truncate">
                      {file.name}
                    </p>
                    <p className="text-neutral-500 text-[11px]">
                      {formatBytes(file.size)}
                    </p>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 text-neutral-400 hover:text-neutral-900"
                  onClick={() => setFile(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg border-neutral-200 hover:border-neutral-300 dark:border-neutral-800 cursor-pointer transition-colors"
              >
                <Upload className="h-7 w-7 text-neutral-400 mb-2" />
                <p className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
                  Click to choose a policy file
                </p>
                <p className="text-[11px] text-neutral-400 mt-0.5">
                  PDF, DOCX, MD, TXT (Max 50MB)
                </p>
              </div>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="doc-title" className="text-xs">
              Document Display Title
            </Label>
            <Input
              id="doc-title"
              placeholder="e.g. Parental Leave Policy 2026"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="h-9 text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="doc-category" className="text-xs">
                Category
              </Label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger id="doc-category" className="h-9 text-sm">
                  <SelectValue placeholder="Select Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="HR">HR & Benefits</SelectItem>
                  <SelectItem value="IT_SECURITY">IT & Security</SelectItem>
                  <SelectItem value="TRAVEL">Travel & Expenses</SelectItem>
                  <SelectItem value="LEGAL">Legal & Compliance</SelectItem>
                  <SelectItem value="GENERAL">General Overview</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="doc-dept" className="text-xs">
                Department Visibility
              </Label>
              <Select value={departmentId} onValueChange={setDepartmentId}>
                <SelectTrigger id="doc-dept" className="h-9 text-sm">
                  <SelectValue placeholder="Select Department" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">
                    All Employees (Company-Wide)
                  </SelectItem>
                  {departments
                    .filter((d) => d.is_active)
                    .map((dept) => (
                      <SelectItem key={dept.id} value={dept.id}>
                        {dept.name}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
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
              disabled={isUploading || !file || !title.trim()}
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                  Uploading...
                </>
              ) : (
                "Upload & Index"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
