"use client";

import CitationDrawer from "@/components/chat/citations/citation-drawer";
import ChatInput from "@/components/chat/messages/chat-input";
import MessageList from "@/components/chat/messages/message-list";
import SessionList from "@/components/chat/sidebar/session-list";
import DashboardShell from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useChatSessions } from "@/hooks/useChatSessions";
import { useChatStream } from "@/hooks/useChatStream";
import { useLLMConfig } from "@/hooks/useLLMConfig";
import { chatApi } from "@/lib/api/chat";
import { MessageCitation } from "@/lib/api/types";
import { useQuery } from "@tanstack/react-query";
import { PanelLeftClose, PanelLeftOpen, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

export default function ChatPage() {
  const { sessions, createSession, isCreating, updateSession, deleteSession } =
    useChatSessions();
  const { availableModels, isLoadingModels } = useLLMConfig();

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedModel, setSelectedModel] = useState<string>("");

  // Sync selected model from dynamic models endpoint
  useEffect(() => {
    if (availableModels && !selectedModel) {
      setSelectedModel(
        availableModels.default_model ||
          availableModels.chat_models[0]?.id ||
          "gpt-4o",
      );
    }
  }, [availableModels, selectedModel]);

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
    const options = {
      model: selectedModel || undefined,
      provider: availableModels?.provider,
    };

    if (!activeSessionId) {
      const newSession = await createSession({ title: text.slice(0, 30) });
      if (newSession) {
        setActiveSessionId(newSession.id);
        // Short delay to let state settle
        setTimeout(() => sendMessage(text, options), 100);
      }
    } else {
      await sendMessage(text, options);
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
          {/* Top Bar with Sidebar Toggle & Dynamic Model Selector */}
          <div className="flex h-11 items-center justify-between px-4 border-b border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/40">
            <div className="flex items-center space-x-3">
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

              <span className="text-xs font-medium text-neutral-600 dark:text-neutral-300 truncate max-w-xs">
                {sessionDetailQuery.data?.title || "New Conversation"}
              </span>
            </div>

            {/* Dynamic Model Dropdown */}
            <div className="flex items-center space-x-2">
              <Sparkles className="h-3.5 w-3.5 text-amber-500 hidden sm:inline-block" />
              {availableModels && availableModels.chat_models.length > 0 ? (
                <Select
                  value={selectedModel}
                  onValueChange={(val) => setSelectedModel(val)}
                >
                  <SelectTrigger className="h-7 text-xs px-2.5 py-0 bg-white dark:bg-neutral-900 border-neutral-200 dark:border-neutral-800 rounded-md min-w-36">
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent align="end">
                    {availableModels.chat_models.map((model) => (
                      <SelectItem
                        key={model.id}
                        value={model.id}
                        className="text-xs"
                      >
                        <div className="flex items-center justify-between space-x-2 w-full">
                          <span>{model.name}</span>
                          <span className="text-[10px] text-neutral-400 capitalize">
                            {model.category}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Badge variant="outline" className="text-[11px] font-normal">
                  {isLoadingModels ? "Loading models..." : "Default LLM"}
                </Badge>
              )}
            </div>
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
