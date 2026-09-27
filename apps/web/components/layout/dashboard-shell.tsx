"use client";

import Navbar from "@/components/layout/navbar";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";
import { usePathname, useRouter } from "next/navigation";
import React, { useEffect } from "react";

export default function DashboardShell({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (
        !user &&
        !pathname.startsWith("/login") &&
        !pathname.startsWith("/change-password")
      ) {
        router.push("/login");
      } else if (
        user?.must_change_password &&
        !pathname.startsWith("/change-password")
      ) {
        router.push("/change-password");
      }
    }
  }, [user, isLoading, pathname, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen w-full flex-col bg-neutral-50 dark:bg-neutral-900">
        <header className="h-14 border-b border-neutral-200 bg-white px-6 flex items-center justify-between" />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-4">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-64 w-full" />
        </main>
      </div>
    );
  }

  if (
    !user &&
    !pathname.startsWith("/login") &&
    !pathname.startsWith("/change-password")
  ) {
    return null;
  }

  return (
    <div className="flex h-screen flex-col bg-neutral-50/50 text-neutral-900 dark:bg-neutral-950 dark:text-neutral-50 overflow-hidden">
      <Navbar />
      <main
        className={cn(
          "flex-1 flex flex-col min-h-0 overflow-y-auto",
          className,
        )}
      >
        {children}
      </main>
    </div>
  );
}
