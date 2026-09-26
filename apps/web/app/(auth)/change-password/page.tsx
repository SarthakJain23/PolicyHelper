"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { KeyRound, Loader2 } from "lucide-react";
import React, { useState } from "react";
import { toast } from "sonner";

export default function ChangePasswordPage() {
  const { changePassword, isChangingPassword } = useAuth();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPassword || !newPassword) return;

    if (newPassword.length < 8) {
      toast.error("New password must be at least 8 characters long");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }

    await changePassword({
      current_password: currentPassword,
      new_password: newPassword,
    });
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-neutral-50 dark:bg-neutral-950">
      <div className="w-full max-w-md space-y-6">
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
            <KeyRound className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
            Set Permanent Password
          </h1>
          <p className="text-xs text-neutral-500 dark:text-neutral-400 max-w-sm">
            For security reasons, you must change your temporary password before
            accessing the policy portal.
          </p>
        </div>

        <Card className="border-neutral-200/80 shadow-xs">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">Update Password</CardTitle>
            <CardDescription className="text-xs">
              Enter your current temporary password followed by your chosen
              permanent password.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="currentPassword" className="text-xs">
                  Current / Temporary Password
                </Label>
                <Input
                  id="currentPassword"
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  autoFocus
                  className="h-9 text-sm"
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="newPassword" className="text-xs">
                  New Password (min. 8 characters)
                </Label>
                <Input
                  id="newPassword"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  className="h-9 text-sm"
                />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="confirmPassword" className="text-xs">
                  Confirm New Password
                </Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="h-9 text-sm"
                />
              </div>

              <Button
                type="submit"
                disabled={
                  isChangingPassword ||
                  !currentPassword ||
                  !newPassword ||
                  !confirmPassword
                }
                className="w-full h-9 text-xs font-medium"
              >
                {isChangingPassword ? (
                  <>
                    <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                    Updating password...
                  </>
                ) : (
                  "Set Password & Proceed"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
