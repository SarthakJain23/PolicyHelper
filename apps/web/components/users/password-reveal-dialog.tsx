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
import { Check, Copy, ShieldAlert } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface PasswordRevealDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  email: string;
  temporaryPassword: string;
}

export default function PasswordRevealDialog({
  open,
  onOpenChange,
  email,
  temporaryPassword,
}: PasswordRevealDialogProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(temporaryPassword);
    setCopied(true);
    toast.success("Temporary password copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md border-amber-200/80">
        <DialogHeader>
          <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400">
            <ShieldAlert className="h-5 w-5" />
            <DialogTitle className="text-base">
              Temporary Credentials Generated
            </DialogTitle>
          </div>
          <DialogDescription className="text-xs text-neutral-600 dark:text-neutral-400">
            Share these credentials with <strong>{email}</strong>. The user will
            be required to change this password on their initial login.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-3">
          <div className="space-y-1">
            <Label className="text-xs text-neutral-500">Email</Label>
            <Input
              readOnly
              value={email}
              className="h-8 text-xs bg-neutral-50 font-mono"
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs text-neutral-500">
              Temporary Password
            </Label>
            <div className="flex items-center space-x-2">
              <Input
                readOnly
                value={temporaryPassword}
                className="h-9 text-sm bg-neutral-50 font-mono font-bold text-neutral-900 dark:text-neutral-100"
              />
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleCopy}
                className="h-9 px-3 shrink-0"
              >
                {copied ? (
                  <Check className="h-4 w-4 text-emerald-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            size="sm"
            onClick={() => onOpenChange(false)}
            className="w-full text-xs"
          >
            Done & Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
