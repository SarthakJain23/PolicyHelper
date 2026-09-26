"use client";

import { Badge } from "@/components/ui/badge";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/hooks/useAuth";
import { useLLMConfig } from "@/hooks/useLLMConfig";
import { useOrganization } from "@/hooks/useOrganization";
import { TestAndDiscoverResponse } from "@/lib/api/types";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  Cpu,
  Key,
  Layers,
  Loader2,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function SettingsPage() {
  const { isSuperAdmin, isHrAdmin } = useAuth();
  const {
    organization,
    updateOrganization,
    isUpdating: isUpdatingOrg,
  } = useOrganization();
  const {
    configs,
    isLoadingConfigs,
    testAndDiscover,
    isTesting,
    saveConfig,
    isSaving,
    triggerReindex,
    isReindexing,
    reindexStatus,
  } = useLLMConfig();

  // Organization state
  const [orgName, setOrgName] = useState("");
  const [orgSlug, setOrgSlug] = useState("");

  useEffect(() => {
    if (organization) {
      setOrgName(organization.name);
      setOrgSlug(organization.slug);
    }
  }, [organization]);

  // Provider state
  const [selectedProvider, setSelectedProvider] = useState<
    "openai" | "anthropic" | "gemini"
  >("openai");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [discoveryResult, setDiscoveryResult] =
    useState<TestAndDiscoverResponse | null>(null);
  const [selectedEmbeddingModel, setSelectedEmbeddingModel] = useState(
    "text-embedding-3-small",
  );
  const [selectedDimensions, setSelectedDimensions] = useState(1536);

  // Auto-sync active config for provider
  useEffect(() => {
    const existing = configs.find(
      (c) => c.provider.toLowerCase() === selectedProvider,
    );
    if (existing) {
      setSelectedEmbeddingModel(existing.default_embedding_model);
      setSelectedDimensions(existing.embedding_dimensions);
      setBaseUrl(existing.base_url || "");
    } else {
      if (selectedProvider === "openai") {
        setSelectedEmbeddingModel("text-embedding-3-small");
        setSelectedDimensions(1536);
      } else if (selectedProvider === "gemini") {
        setSelectedEmbeddingModel("models/text-embedding-004");
        setSelectedDimensions(768);
      } else {
        setSelectedEmbeddingModel("text-embedding-3-small");
        setSelectedDimensions(1536);
      }
    }
    setDiscoveryResult(null);
  }, [selectedProvider, configs]);

  if (!isSuperAdmin && !isHrAdmin) {
    return (
      <div className="flex h-96 flex-col items-center justify-center p-6 text-center">
        <AlertTriangle className="h-10 w-10 text-amber-500 mb-3" />
        <h2 className="text-lg font-medium">Access Restricted</h2>
        <p className="text-sm text-neutral-500 max-w-sm mt-1">
          Only Administrators can configure Organization details and LLM
          Strategy Providers.
        </p>
      </div>
    );
  }

  const handleSaveOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orgName.trim()) return;
    await updateOrganization({ name: orgName.trim(), slug: orgSlug.trim() });
  };

  const handleTestAndDiscover = async () => {
    if (!apiKey.trim()) {
      toast.error("Please enter an API key to test");
      return;
    }
    try {
      const res = await testAndDiscover({
        provider: selectedProvider,
        api_key: apiKey.trim(),
        base_url: baseUrl.trim() || null,
      });
      setDiscoveryResult(res);
      if (res.default_embedding_model) {
        setSelectedEmbeddingModel(res.default_embedding_model);
      }
      toast.success(
        `Successfully connected! Discovered ${res.chat_models.length} chat models.`,
      );
    } catch (e) {
      // Error handled by hook
    }
  };

  const handleSaveProviderConfig = async () => {
    if (!apiKey.trim()) {
      toast.error("Please enter an API key");
      return;
    }
    await saveConfig({
      provider: selectedProvider,
      api_key: apiKey.trim(),
      base_url: baseUrl.trim() || null,
      default_embedding_model: selectedEmbeddingModel,
      embedding_dimensions: selectedDimensions,
      is_active: true,
    });
    setApiKey("");
    setDiscoveryResult(null);
  };

  const handleTriggerReindex = async () => {
    if (
      confirm(
        `Are you sure you want to re-index all documents with ${selectedEmbeddingModel}? This will re-generate embeddings in the background.`,
      )
    ) {
      await triggerReindex({
        new_embedding_model: selectedEmbeddingModel,
        dimensions: selectedDimensions,
      });
    }
  };

  return (
    <div className="container max-w-5xl py-8 space-y-8 px-4 sm:px-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
          Organization & LLM Settings
        </h1>
        <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
          Manage company branding, configure dynamic LLM strategies, and manage
          vector embedding models.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Organization Information */}
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Building2 className="h-5 w-5 text-neutral-700 dark:text-neutral-300" />
              <CardTitle className="text-base">Organization Profile</CardTitle>
            </div>
            <CardDescription>
              Set company identity displayed across PolicyHelper.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSaveOrg} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="orgName">Organization Name</Label>
                <Input
                  id="orgName"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  placeholder="e.g. Acme Corporation"
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="orgSlug">Organization Slug</Label>
                <Input
                  id="orgSlug"
                  value={orgSlug}
                  onChange={(e) => setOrgSlug(e.target.value)}
                  placeholder="e.g. acme-corp"
                  required
                />
              </div>
              <Button type="submit" disabled={isUpdatingOrg} className="w-full">
                {isUpdatingOrg ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : null}
                Save Organization
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Active Providers Summary */}
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Cpu className="h-5 w-5 text-neutral-700 dark:text-neutral-300" />
              <CardTitle className="text-base">Active LLM Providers</CardTitle>
            </div>
            <CardDescription>
              Stored credentials with AES-256 encryption at rest.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {isLoadingConfigs ? (
              <div className="py-4 text-center text-sm text-neutral-500">
                Loading configurations...
              </div>
            ) : configs.length === 0 ? (
              <div className="py-4 text-center text-sm text-neutral-500">
                No LLM providers configured yet. Set up a provider below.
              </div>
            ) : (
              configs.map((c) => (
                <div
                  key={c.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/50"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-semibold capitalize">
                        {c.provider}
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {c.key_fingerprint}
                      </Badge>
                      {c.is_active && (
                        <Badge className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 text-[10px]">
                          Active
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-neutral-500">
                      Embedding:{" "}
                      <span className="font-mono">
                        {c.default_embedding_model}
                      </span>{" "}
                      ({c.embedding_dimensions}d)
                    </p>
                  </div>
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* Provider Configuration & Key Management */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Key className="h-5 w-5 text-neutral-700 dark:text-neutral-300" />
            <CardTitle className="text-base">
              Configure LLM Provider & Dynamic Models
            </CardTitle>
          </div>
          <CardDescription>
            Input your vendor API key to dynamically fetch and enable models for
            employee chat.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Tabs
            value={selectedProvider}
            onValueChange={(val) => setSelectedProvider(val as any)}
            className="w-full"
          >
            <TabsList className="grid grid-cols-3 w-full max-w-md">
              <TabsTrigger value="openai">OpenAI</TabsTrigger>
              <TabsTrigger value="anthropic">Anthropic</TabsTrigger>
              <TabsTrigger value="gemini">Google Gemini</TabsTrigger>
            </TabsList>

            <div className="mt-6 space-y-4 max-w-xl">
              <div className="space-y-1.5">
                <Label htmlFor="apiKey">
                  {selectedProvider === "openai"
                    ? "OpenAI API Key"
                    : selectedProvider === "anthropic"
                      ? "Anthropic API Key"
                      : "Google Gemini API Key"}
                </Label>
                <div className="flex space-x-2">
                  <Input
                    id="apiKey"
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Paste your API key here..."
                  />
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleTestAndDiscover}
                    disabled={isTesting || !apiKey.trim()}
                  >
                    {isTesting ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-1.5" />
                    ) : (
                      <Sparkles className="h-4 w-4 mr-1.5 text-amber-500" />
                    )}
                    Test & Discover
                  </Button>
                </div>
                <p className="text-xs text-neutral-500">
                  Key is encrypted with Fernet (AES-256) at rest and never
                  transmitted unmasked.
                </p>
              </div>

              {/* Base URL (Optional for Proxies / Azure) */}
              <div className="space-y-1.5">
                <Label htmlFor="baseUrl">Custom Base URL (Optional)</Label>
                <Input
                  id="baseUrl"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder={
                    selectedProvider === "openai"
                      ? "https://api.openai.com/v1"
                      : "Leave empty for official API"
                  }
                />
              </div>

              {/* Discovered Models Display */}
              {discoveryResult && (
                <div className="p-4 rounded-lg border border-emerald-200 dark:border-emerald-900 bg-emerald-50/50 dark:bg-emerald-950/20 space-y-3">
                  <div className="flex items-center space-x-2 text-emerald-800 dark:text-emerald-300 font-medium text-xs">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    <span>Live Vendor Verification Succeeded</span>
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs font-semibold">
                      Discovered Chat Models (
                      {discoveryResult.chat_models.length}):
                    </Label>
                    <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-1.5 bg-white/70 dark:bg-neutral-900/70 rounded border border-neutral-200 dark:border-neutral-800">
                      {discoveryResult.chat_models.map((m) => (
                        <Badge
                          key={m.id}
                          variant="secondary"
                          className="text-[11px]"
                        >
                          {m.name}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {discoveryResult.embedding_models.length > 0 && (
                    <div className="space-y-1.5">
                      <Label className="text-xs font-semibold">
                        Active Embedding Model:
                      </Label>
                      <Select
                        value={selectedEmbeddingModel}
                        onValueChange={(val) => {
                          setSelectedEmbeddingModel(val);
                          const matched = discoveryResult.embedding_models.find(
                            (e) => e.id === val,
                          );
                          if (matched)
                            setSelectedDimensions(matched.dimensions);
                        }}
                      >
                        <SelectTrigger className="w-full bg-white dark:bg-neutral-900">
                          <SelectValue placeholder="Select embedding model" />
                        </SelectTrigger>
                        <SelectContent>
                          {discoveryResult.embedding_models.map((em) => (
                            <SelectItem key={em.id} value={em.id}>
                              {em.name} ({em.dimensions} dimensions)
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>
              )}

              {/* Save Configuration Button */}
              <div className="pt-2">
                <Button
                  onClick={handleSaveProviderConfig}
                  disabled={isSaving || !apiKey.trim()}
                  className="w-full"
                >
                  {isSaving ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : null}
                  Save & Activate Provider
                </Button>
              </div>
            </div>
          </Tabs>
        </CardContent>
      </Card>

      {/* Embedding Model Migration & Re-Indexing */}
      <Card className="border-amber-200/60 dark:border-amber-900/40">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Layers className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            <CardTitle className="text-base">
              Embedding Model & Re-Indexing
            </CardTitle>
          </div>
          <CardDescription>
            When changing vector embedding models, re-index existing policy
            documents in the background.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 rounded-lg bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900 space-y-2">
            <p className="text-xs text-amber-800 dark:text-amber-300">
              <strong>Vector Space Protocol:</strong> Changing embedding models
              produces vectors in a new coordinate space. Running a re-index
              iterates through all document chunks and updates the{" "}
              <code className="font-mono">pgvector</code> database with zero
              downtime.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-2">
            <div className="space-y-1">
              <span className="text-sm font-medium">
                Active Embedding Model
              </span>
              <p className="text-xs text-neutral-500">
                <span className="font-mono">{selectedEmbeddingModel}</span> (
                {selectedDimensions} dims)
              </p>
            </div>
            <Button
              variant="outline"
              onClick={handleTriggerReindex}
              disabled={isReindexing || reindexStatus?.status === "IN_PROGRESS"}
            >
              {reindexStatus?.status === "IN_PROGRESS" ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Re-Index All Documents
            </Button>
          </div>

          {/* Re-indexing progress tracker */}
          {reindexStatus && (
            <div className="mt-4 p-4 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold">Reindexing Status:</span>
                <Badge
                  variant={
                    reindexStatus.status === "COMPLETED"
                      ? "default"
                      : reindexStatus.status === "FAILED"
                        ? "destructive"
                        : "secondary"
                  }
                >
                  {reindexStatus.status}
                </Badge>
              </div>

              {reindexStatus.status === "IN_PROGRESS" && (
                <div className="space-y-1">
                  <div className="w-full bg-neutral-200 dark:bg-neutral-800 rounded-full h-2">
                    <div
                      className="bg-neutral-900 dark:bg-neutral-100 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${reindexStatus.progress_percentage}%` }}
                    />
                  </div>
                  <p className="text-[11px] text-neutral-500 text-right">
                    {reindexStatus.completed_chunks} /{" "}
                    {reindexStatus.total_chunks} chunks (
                    {reindexStatus.progress_percentage}%)
                  </p>
                </div>
              )}

              {reindexStatus.status === "COMPLETED" && (
                <p className="text-xs text-emerald-600 dark:text-emerald-400">
                  Successfully re-indexed {reindexStatus.total_chunks} chunks
                  with {reindexStatus.new_embedding_model}.
                </p>
              )}

              {reindexStatus.status === "FAILED" && (
                <p className="text-xs text-rose-600 dark:text-rose-400">
                  Error: {reindexStatus.error}
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
