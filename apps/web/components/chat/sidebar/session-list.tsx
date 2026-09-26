"use client";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatSession } from "@/lib/api/types";
import { MessageSquarePlus, Plus } from "lucide-react";
import SessionItem from "./session-item";

interface SessionListProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onCreateSession: () => void;
  onUpdateSession: (
    id: string,
    payload: { title?: string; is_pinned?: boolean; is_archived?: boolean },
  ) => void;
  onDeleteSession: (id: string) => void;
  isCreating: boolean;
}

export default function SessionList({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onUpdateSession,
  onDeleteSession,
  isCreating,
}: SessionListProps) {
  const pinnedSessions = sessions.filter((s) => s.is_pinned);
  const regularSessions = sessions.filter((s) => !s.is_pinned);

  return (
    <div className="flex h-full flex-col bg-neutral-50/70 dark:bg-neutral-900/60 border-r border-neutral-200 dark:border-neutral-800 w-64 lg:w-72 shrink-0">
      {/* Sidebar Header with New Chat Button */}
      <div className="p-3 border-b border-neutral-200 dark:border-neutral-800">
        <Button
          onClick={onCreateSession}
          disabled={isCreating}
          className="w-full h-9 justify-start space-x-2 text-xs font-medium shadow-xs"
        >
          <Plus className="h-4 w-4 shrink-0" />
          <span>New Conversation</span>
        </Button>
      </div>

      {/* Sessions Scroll Area */}
      <ScrollArea className="flex-1 p-2">
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-6 text-center text-xs text-neutral-400">
            <MessageSquarePlus className="h-6 w-6 mb-2 opacity-50" />
            <span>No conversations yet</span>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Pinned Section */}
            {pinnedSessions.length > 0 && (
              <div className="space-y-1">
                <p className="px-2.5 text-[10px] font-semibold tracking-wider text-neutral-400 uppercase">
                  Pinned
                </p>
                {pinnedSessions.map((session) => (
                  <SessionItem
                    key={session.id}
                    session={session}
                    isActive={session.id === activeSessionId}
                    onSelect={onSelectSession}
                    onUpdate={onUpdateSession}
                    onDelete={onDeleteSession}
                  />
                ))}
              </div>
            )}

            {/* Recent Conversations */}
            {regularSessions.length > 0 && (
              <div className="space-y-1">
                <p className="px-2.5 text-[10px] font-semibold tracking-wider text-neutral-400 uppercase">
                  Recent
                </p>
                {regularSessions.map((session) => (
                  <SessionItem
                    key={session.id}
                    session={session}
                    isActive={session.id === activeSessionId}
                    onSelect={onSelectSession}
                    onUpdate={onUpdateSession}
                    onDelete={onDeleteSession}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
