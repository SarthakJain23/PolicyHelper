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
import { useChatSession, useChatSessions } from "@/hooks/useChatSessions";
import { useChatStream } from "@/hooks/useChatStream";
import { useLLMConfig } from "@/hooks/useLLMConfig";
import { MessageCitation } from "@/lib/api/types";
import { PanelLeftClose, PanelLeftOpen, Sparkles } from "lucide-react";
import { useState } from "react";

export default function ChatPage() {
  const { sessions, createSession, isCreating, updateSession, deleteSession } =
    useChatSessions();
  const { availableModels, isLoadingModels } = useLLMConfig();

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedModel, setSelectedModel] = useState<string>("");

  const activeModel =
    selectedModel ||
    availableModels?.default_model ||
    availableModels?.chat_models[0]?.id ||
    "gpt-4o";

  // Citation Drawer State
  const [selectedCitation, setSelectedCitation] =
    useState<MessageCitation | null>(null);
  const [citationDrawerOpen, setCitationDrawerOpen] = useState(false);

  // Load session messages via TanStack Query hook
  const sessionDetailQuery = useChatSession(activeSessionId);

  const { sendMessage, isStreaming, streamingContent, streamingCitations } =
    useChatStream(activeSessionId);

  const handleCreateNewSession = () => {
    setActiveSessionId(null);
  };

  const handleDeleteSession = async (id: string) => {
    await deleteSession(id);
    if (activeSessionId === id) {
      const remaining = sessions.filter((s) => s.id !== id);
      setActiveSessionId(remaining[0]?.id || null);
    }
  };

  const handleSendMessage = async (text: string) => {
    const options = {
      model: activeModel || undefined,
      provider: availableModels?.provider,
    };

    let targetId = activeSessionId;
    if (!targetId) {
      try {
        const newSession = await createSession({
          title: text.length > 40 ? `${text.slice(0, 37)}...` : text,
        });
        if (newSession && newSession.id) {
          targetId = newSession.id;
          setActiveSessionId(newSession.id);
        } else {
          return;
        }
      } catch (e) {
        console.error("Failed to create session on first message", e);
        return;
      }
    }
    await sendMessage(text, options, targetId);
  };

  const handleCitationClick = (citation: MessageCitation) => {
    setSelectedCitation(citation);
    setCitationDrawerOpen(true);
  };

  const currentMessages = activeSessionId
    ? sessionDetailQuery.data?.messages || []
    : [];

  return (
    <DashboardShell className="overflow-hidden">
      <div className="flex flex-1 overflow-hidden h-full">
        {/* Collapsible Session History Sidebar */}
        {sidebarOpen && (
          <SessionList
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={(id) => setActiveSessionId(id)}
            onCreateSession={handleCreateNewSession}
            onUpdateSession={(id, payload) => updateSession({ id, payload })}
            onDeleteSession={handleDeleteSession}
            isCreating={isCreating}
          />
        )}

        {/* Main Chat Interface */}
        <div className="flex flex-1 flex-col h-full min-h-0 overflow-hidden bg-white dark:bg-neutral-950">
          {/* Top Bar with Sidebar Toggle & Dynamic Model Selector */}
          <div className="flex h-11 shrink-0 items-center justify-between px-4 border-b border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/40">
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
                {activeSessionId
                  ? sessionDetailQuery.data?.title || "Conversation"
                  : "New Conversation"}
              </span>
            </div>

            {/* Dynamic Model Dropdown */}
            <div className="flex items-center space-x-2">
              <Sparkles className="h-3.5 w-3.5 text-amber-500 hidden sm:inline-block" />
              {availableModels && availableModels.chat_models.length > 0 ? (
                <Select
                  value={activeModel}
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
          <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
            <MessageList
              messages={currentMessages}
              isStreaming={isStreaming}
              streamingContent={streamingContent}
              streamingCitations={streamingCitations}
              onCitationClick={handleCitationClick}
              onSuggestedClick={handleSendMessage}
            />
          </div>

          {/* Chat Prompt Input */}
          <div className="shrink-0">
            <ChatInput onSend={handleSendMessage} disabled={isStreaming} />
          </div>
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
