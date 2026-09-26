"use client";

import DashboardShell from "@/components/layout/dashboard-shell";
import LogsTable from "@/components/logs/logs-table";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/hooks/useAuth";
import { useLogs } from "@/hooks/useLogs";
import { useUsers } from "@/hooks/useUsers";
import { Activity, RefreshCw } from "lucide-react";
import { useState } from "react";

export default function LogsPage() {
  const { isSuperAdmin, isHrAdmin } = useAuth();
  const isAdmin = isSuperAdmin || isHrAdmin;

  const [selectedUserId, setSelectedUserId] = useState<string>("all");
  const [selectedAction, setSelectedAction] = useState<string>("all");

  const { users } = useUsers();

  const filterParams = {
    user_id: selectedUserId !== "all" ? selectedUserId : undefined,
    action: selectedAction !== "all" ? selectedAction : undefined,
  };

  const { logs, isLoading, refetch, isRefetching } = useLogs(filterParams);

  return (
    <DashboardShell>
      <div className="flex-1 space-y-4 p-4 sm:p-6 max-w-7xl mx-auto w-full">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-neutral-200 dark:border-neutral-800">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50 flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>
                {isAdmin
                  ? "User & System Activity Logs"
                  : "My Activity History"}
              </span>
            </h1>
            <p className="text-xs text-neutral-500 mt-0.5">
              {isAdmin
                ? "Inspect all user activity, authentication events, and policy management actions."
                : "View your personal account activity and login history."}
            </p>
          </div>

          <div className="flex items-center space-x-2">
            {/* User Filter for Admins */}
            {isAdmin && (
              <div className="w-44">
                <Select
                  value={selectedUserId}
                  onValueChange={setSelectedUserId}
                >
                  <SelectTrigger className="h-8 text-xs">
                    <SelectValue placeholder="All Users" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Users</SelectItem>
                    {users.map((u) => (
                      <SelectItem key={u.id} value={u.id}>
                        {u.full_name} ({u.email})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Action Filter */}
            <div className="w-36">
              <Select value={selectedAction} onValueChange={setSelectedAction}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue placeholder="All Actions" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Actions</SelectItem>
                  <SelectItem value="LOGIN">Logins</SelectItem>
                  <SelectItem value="CHANGE_PASSWORD">
                    Password Changes
                  </SelectItem>
                  <SelectItem value="UPLOAD_DOCUMENT">Doc Uploads</SelectItem>
                  <SelectItem value="DELETE_DOCUMENT">Doc Deletions</SelectItem>
                  <SelectItem value="CREATE_USER">User Creation</SelectItem>
                  <SelectItem value="UPDATE_USER">User Updates</SelectItem>
                  <SelectItem value="CREATE_DEPARTMENT">
                    Dept Creation
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              disabled={isRefetching}
              className="h-8 text-xs font-medium"
            >
              <RefreshCw
                className={`mr-1.5 h-3 w-3 ${isRefetching ? "animate-spin" : ""}`}
              />
              <span>Refresh</span>
            </Button>
          </div>
        </div>

        {/* Logs Table Content */}
        {isLoading ? (
          <div className="p-8 text-center text-xs text-neutral-500">
            Loading activity logs...
          </div>
        ) : (
          <LogsTable logs={logs} isAdmin={isAdmin} />
        )}
      </div>
    </DashboardShell>
  );
}
