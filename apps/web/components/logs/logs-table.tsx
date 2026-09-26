"use client";

import { Badge } from "@/components/ui/badge";
import { AuditLogItem } from "@/lib/api/types";
import { formatDateTime } from "@/lib/utils";
import { Activity, Clock } from "lucide-react";

interface LogsTableProps {
  logs: AuditLogItem[];
  isAdmin: boolean;
}

export default function LogsTable({ logs, isAdmin }: LogsTableProps) {
  if (logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed rounded-lg border-neutral-200 dark:border-neutral-800">
        <Activity className="h-10 w-10 text-neutral-400 mb-3" />
        <h3 className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
          No activity logs found
        </h3>
        <p className="text-xs text-neutral-500 mt-1 max-w-sm">
          User actions, logins, document uploads, and security events will be
          recorded and displayed here.
        </p>
      </div>
    );
  }

  const getActionBadge = (action: string) => {
    switch (action) {
      case "LOGIN":
        return <Badge variant="secondary">Login</Badge>;
      case "CHANGE_PASSWORD":
        return <Badge variant="warning">Password Changed</Badge>;
      case "UPLOAD_DOCUMENT":
        return <Badge variant="success">Document Upload</Badge>;
      case "DELETE_DOCUMENT":
        return <Badge variant="destructive">Document Deleted</Badge>;
      case "CREATE_USER":
        return <Badge variant="default">User Created</Badge>;
      case "UPDATE_USER":
        return <Badge variant="secondary">User Updated</Badge>;
      case "ADMIN_RESET_PASSWORD":
        return <Badge variant="warning">Password Reset</Badge>;
      case "CREATE_DEPARTMENT":
      case "UPDATE_DEPARTMENT":
      case "DEACTIVATE_DEPARTMENT":
        return <Badge variant="outline">{action.replace("_", " ")}</Badge>;
      default:
        return <Badge variant="outline">{action}</Badge>;
    }
  };

  return (
    <div className="rounded-lg border border-neutral-200 bg-white overflow-hidden dark:border-neutral-800 dark:bg-neutral-950 shadow-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-neutral-50 border-b border-neutral-200 font-medium text-neutral-500 dark:bg-neutral-900 dark:border-neutral-800 dark:text-neutral-400">
            <tr>
              <th className="px-4 py-3">Timestamp</th>
              {isAdmin && <th className="px-4 py-3">User</th>}
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Activity Details</th>
              <th className="px-4 py-3">IP Address</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800 text-neutral-800 dark:text-neutral-200">
            {logs.map((log) => (
              <tr
                key={log.id}
                className="hover:bg-neutral-50/70 transition-colors dark:hover:bg-neutral-900/50"
              >
                <td className="px-4 py-3 font-mono text-neutral-500 text-[11px] whitespace-nowrap">
                  <div className="flex items-center space-x-1.5">
                    <Clock className="h-3 w-3 text-neutral-400" />
                    <span>{formatDateTime(log.created_at)}</span>
                  </div>
                </td>

                {isAdmin && (
                  <td className="px-4 py-3 whitespace-nowrap">
                    {log.user_email ? (
                      <div className="flex items-center space-x-2">
                        <div className="flex h-5 w-5 items-center justify-center rounded-full bg-neutral-100 text-[10px] font-semibold text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
                          {log.user_name
                            ? log.user_name.charAt(0).toUpperCase()
                            : "U"}
                        </div>
                        <div>
                          <p className="font-medium text-neutral-900 dark:text-neutral-100">
                            {log.user_name || "User"}
                          </p>
                          <p className="text-[10px] text-neutral-400">
                            {log.user_email}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <span className="text-neutral-400">
                        System / Anonymous
                      </span>
                    )}
                  </td>
                )}

                <td className="px-4 py-3 whitespace-nowrap">
                  {getActionBadge(log.action)}
                </td>

                <td className="px-4 py-3 text-neutral-600 dark:text-neutral-300 font-mono text-[11px] max-w-xs truncate">
                  {log.details && Object.keys(log.details).length > 0 ? (
                    <span>
                      {Object.entries(log.details)
                        .map(
                          ([k, v]) =>
                            `${k}: ${typeof v === "object" ? JSON.stringify(v) : v}`,
                        )
                        .join(", ")}
                    </span>
                  ) : (
                    <span className="text-neutral-400">—</span>
                  )}
                </td>

                <td className="px-4 py-3 font-mono text-neutral-400 text-[11px] whitespace-nowrap">
                  {log.ip_address || "Internal"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
