"use client";

import CitationDrawer from "@/components/chat/citations/citation-drawer";
import ChatInput from "@/components/chat/messages/chat-input";
import MessageList from "@/components/chat/messages/message-list";
import SessionList from "@/components/chat/sidebar/session-list";
import DashboardShell from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { useChatSessions } from "@/hooks/useChatSessions";
import { useChatStream } from "@/hooks/useChatStream";
import { chatApi } from "@/lib/api/chat";
import { MessageCitation } from "@/lib/api/types";
import { useQuery } from "@tanstack/react-query";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { useEffect, useState } from "react";

export default function ChatPage() {
  const { sessions, createSession, isCreating, updateSession, deleteSession } =
    useChatSessions();

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Citation Drawer State
  const [selectedCitation, setSelectedCitation] =
    useState<MessageCitation | null>(null);
  const [citationDrawerOpen, setCitationDrawerOpen] = useState(false);

  // Auto-select first session if none selected
  useEffect(() => {
    if (!activeSessionId && sessions.length > 0) {
      setActiveSessionId(sessions[0].id);
    }
  }, [sessions, activeSessionId]);

  // Load session messages
  const sessionDetailQuery = useQuery({
    queryKey: ["chat", "session", activeSessionId],
    queryFn: () =>
      activeSessionId ? chatApi.getSession(activeSessionId) : null,
    enabled: !!activeSessionId,
  });

  const { sendMessage, isStreaming, streamingContent, streamingCitations } =
    useChatStream(activeSessionId);

  const handleCreateNewSession = async () => {
    const newSession = await createSession({ title: "New Conversation" });
    if (newSession) {
      setActiveSessionId(newSession.id);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!activeSessionId) {
      const newSession = await createSession({ title: text.slice(0, 30) });
      if (newSession) {
        setActiveSessionId(newSession.id);
        // Short delay to let state settle
        setTimeout(() => sendMessage(text), 100);
      }
    } else {
      await sendMessage(text);
    }
  };

  const handleCitationClick = (citation: MessageCitation) => {
    setSelectedCitation(citation);
    setCitationDrawerOpen(true);
  };

  const currentMessages = sessionDetailQuery.data?.messages || [];

  return (
    <DashboardShell>
      <div className="flex flex-1 overflow-hidden h-[calc(100vh-3.5rem)]">
        {/* Collapsible Session History Sidebar */}
        {sidebarOpen && (
          <SessionList
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={(id) => setActiveSessionId(id)}
            onCreateSession={handleCreateNewSession}
            onUpdateSession={(id, payload) => updateSession({ id, payload })}
            onDeleteSession={(id) => deleteSession(id)}
            isCreating={isCreating}
          />
        )}

        {/* Main Chat Interface */}
        <div className="flex flex-1 flex-col overflow-hidden bg-white dark:bg-neutral-950">
          {/* Top Bar with Sidebar Toggle */}
          <div className="flex h-10 items-center justify-between px-4 border-b border-neutral-100 dark:border-neutral-800">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-neutral-500"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
            >
              {sidebarOpen ? (
                <PanelLeftClose className="h-4 w-4" />
              ) : (
                <PanelLeftOpen className="h-4 w-4" />
              )}
            </Button>

            <span className="text-xs font-medium text-neutral-500 truncate max-w-sm">
              {sessionDetailQuery.data?.title || "Conversation"}
            </span>

            <div className="w-7" />
          </div>

          {/* Message History & Live Stream */}
          <MessageList
            messages={currentMessages}
            isStreaming={isStreaming}
            streamingContent={streamingContent}
            streamingCitations={streamingCitations}
            onCitationClick={handleCitationClick}
            onSuggestedClick={handleSendMessage}
          />

          {/* Chat Prompt Input */}
          <ChatInput onSend={handleSendMessage} disabled={isStreaming} />
        </div>

        {/* Citation Detail Modal / Drawer */}
        <CitationDrawer
          citation={selectedCitation}
          open={citationDrawerOpen}
          onOpenChange={setCitationDrawerOpen}
        />
      </div>
    </DashboardShell>
  );
}
