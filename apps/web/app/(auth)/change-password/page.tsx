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
import ThemeToggle from "@/components/ui/theme-toggle";
import { useAuth } from "@/hooks/useAuth";
import { ArrowLeft, BookOpen, KeyRound, Loader2 } from "lucide-react";
import Link from "next/link";
import React, { useState } from "react";
import { toast } from "sonner";

export default function ChangePasswordPage() {
  const { user, changePassword, isChangingPassword } = useAuth();
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
    <div className="flex min-h-screen flex-col bg-neutral-50 dark:bg-neutral-950">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 w-full border-b border-neutral-200 bg-white/95 backdrop-blur-xs dark:border-neutral-800 dark:bg-neutral-950/95">
        <div className="flex h-14 items-center justify-between px-4 sm:px-6">
          <Link
            href="/chat"
            className="flex items-center space-x-2.5 font-semibold text-neutral-900 dark:text-neutral-50"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 shadow-xs">
              <BookOpen className="h-4 w-4" />
            </div>
            <span className="text-base tracking-tight font-medium">
              PolicyHelper
            </span>
          </Link>

          <div className="flex items-center space-x-2 sm:space-x-2.5">
            {!user?.must_change_password && (
              <Button
                variant="outline"
                size="sm"
                asChild
                className="h-8 px-2.5 text-xs font-medium gap-1.5 border-neutral-200 dark:border-neutral-800 hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                <Link href="/chat">
                  <ArrowLeft className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">Back to Main Page</span>
                  <span className="sm:hidden">Back</span>
                </Link>
              </Button>
            )}
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 flex-col items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-md space-y-6">
          <div className="flex flex-col items-center text-center space-y-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
              <KeyRound className="h-6 w-6" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
              {user?.must_change_password
                ? "Set Permanent Password"
                : "Change Password"}
            </h1>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 max-w-sm">
              {user?.must_change_password
                ? "For security reasons, you must change your temporary password before accessing the policy portal."
                : "Update your account password to keep your account secure."}
            </p>
          </div>

          <Card className="border-neutral-200/80 shadow-xs">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg">
                {user?.must_change_password
                  ? "Update Password"
                  : "Change Your Password"}
              </CardTitle>
              <CardDescription className="text-xs">
                {user?.must_change_password
                  ? "Enter your current temporary password followed by your chosen permanent password."
                  : "Enter your current password and your new password below."}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="currentPassword" className="text-xs">
                    Current {user?.must_change_password ? "/ Temporary " : ""}
                    Password
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

                <div className="flex flex-col sm:flex-row gap-2 pt-1">
                  <Button
                    type="submit"
                    disabled={
                      isChangingPassword ||
                      !currentPassword ||
                      !newPassword ||
                      !confirmPassword
                    }
                    className="flex-1 h-9 text-xs font-medium"
                  >
                    {isChangingPassword ? (
                      <>
                        <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                        Updating password...
                      </>
                    ) : user?.must_change_password ? (
                      "Set Password & Proceed"
                    ) : (
                      "Update Password"
                    )}
                  </Button>
                  {!user?.must_change_password && (
                    <Button
                      type="button"
                      variant="outline"
                      asChild
                      className="h-9 text-xs font-medium"
                    >
                      <Link href="/chat">Cancel</Link>
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
