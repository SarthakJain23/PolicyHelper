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
import { BookOpen, Loader2, ShieldCheck } from "lucide-react";
import React, { useState } from "react";

export default function LoginPage() {
  const { login, isLoggingIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    await login({ email, password });
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 bg-neutral-50 dark:bg-neutral-950">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-neutral-900 text-white shadow-md">
            <BookOpen className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
            PolicyHelper
          </h1>
          <p className="text-xs text-neutral-500 dark:text-neutral-400 max-w-sm">
            Company policy search and AI assistant for internal teams
          </p>
        </div>

        {/* Login Card */}
        <Card className="border-neutral-200/80 shadow-xs">
          <CardHeader className="space-y-1 pb-4">
            <CardTitle className="text-lg">Sign in to your account</CardTitle>
            <CardDescription className="text-xs">
              Enter your corporate email and password to access company policies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="email" className="text-xs">
                  Email address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoFocus
                  className="h-9 text-sm"
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password" className="text-xs">
                    Password
                  </Label>
                </div>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="h-9 text-sm"
                />
              </div>

              <Button
                type="submit"
                disabled={isLoggingIn || !email || !password}
                className="w-full h-9 text-xs font-medium"
              >
                {isLoggingIn ? (
                  <>
                    <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Security Notice */}
        <div className="flex items-center justify-center space-x-1.5 text-[11px] text-neutral-400">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>Internal secure company network access only</span>
        </div>
      </div>
    </div>
  );
}
