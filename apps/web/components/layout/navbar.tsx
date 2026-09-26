"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import ThemeToggle from "@/components/ui/theme-toggle";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";
import {
  Activity,
  BookOpen,
  Building2,
  FileText,
  KeyRound,
  LogOut,
  MessageSquare,
  Users,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();
  const { user, isSuperAdmin, isHrAdmin, logout } = useAuth();

  const navItems = [
    { label: "Policy Chat", href: "/chat", icon: MessageSquare },
    {
      label: "Policy Documents",
      href: "/documents",
      icon: FileText,
      requireRole: "HR",
    },
    {
      label: "Departments",
      href: "/departments",
      icon: Building2,
      requireRole: "HR",
    },
    { label: "Users & Access", href: "/users", icon: Users, requireRole: "HR" },
    { label: "Activity Logs", href: "/logs", icon: Activity },
  ];

  const visibleItems = navItems.filter((item) => {
    if (!item.requireRole) return true;
    return isHrAdmin || isSuperAdmin;
  });

  return (
    <header className="sticky top-0 z-40 w-full border-b border-neutral-200 bg-white/95 backdrop-blur-xs dark:border-neutral-800 dark:bg-neutral-950/95">
      <div className="flex h-14 items-center justify-between px-4 sm:px-6">
        {/* Brand */}
        <div className="flex items-center space-x-6">
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

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {visibleItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-2 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                    isActive
                      ? "bg-neutral-100 text-neutral-900 dark:bg-neutral-800 dark:text-neutral-50"
                      : "text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-900 dark:hover:text-neutral-50",
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Action Controls & User Account Menu */}
        <div className="flex items-center space-x-2.5">
          <ThemeToggle />

          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="h-8 px-2 flex items-center space-x-2 text-xs"
                >
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-neutral-200 text-[10px] font-semibold text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
                    {user.full_name.charAt(0).toUpperCase()}
                  </div>
                  <span className="hidden sm:inline-block font-medium text-neutral-800 dark:text-neutral-200">
                    {user.full_name}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-2 py-1.5 text-xs">
                  <p className="font-semibold text-neutral-900 dark:text-neutral-100">
                    {user.full_name}
                  </p>
                  <p className="text-neutral-500 truncate">{user.email}</p>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {user.roles.map((r) => (
                      <span
                        key={r.id}
                        className="rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] font-medium text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300"
                      >
                        {r.name}
                      </span>
                    ))}
                  </div>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/logs" className="flex items-center text-xs">
                    <Activity className="mr-2 h-3.5 w-3.5" />
                    <span>Activity History</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link
                    href="/change-password"
                    className="flex items-center text-xs"
                  >
                    <KeyRound className="mr-2 h-3.5 w-3.5" />
                    <span>Change Password</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => logout()}
                  className="text-xs text-red-600 focus:text-red-600"
                >
                  <LogOut className="mr-2 h-3.5 w-3.5" />
                  <span>Sign Out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button size="sm" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
