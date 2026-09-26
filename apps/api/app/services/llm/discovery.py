import hashlib
import logging
from datetime import datetime, timezone
from typing import Any
import httpx

logger = logging.getLogger(__name__)

FALLBACK_MODELS = {
    "openai": {
        "chat": [
            {"id": "gpt-4o", "name": "GPT-4o (Omni - Flagship)", "category": "flagship"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Fast & Cost Effective)", "category": "fast"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "category": "flagship"},
            {"id": "o1-mini", "name": "o1 Mini (Reasoning)", "category": "reasoning"},
            {"id": "o1-preview", "name": "o1 Preview (Reasoning)", "category": "reasoning"},
        ],
        "embedding": [
            {"id": "text-embedding-3-small", "name": "Text Embedding 3 Small (1536 dims)", "dimensions": 1536},
            {"id": "text-embedding-3-large", "name": "Text Embedding 3 Large (3072 dims)", "dimensions": 3072},
            {"id": "text-embedding-ada-002", "name": "Text Embedding Ada 002 (1536 dims)", "dimensions": 1536},
        ],
    },
    "anthropic": {
        "chat": [
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet (Flagship)", "category": "flagship"},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku (Fast)", "category": "fast"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus (High Capability)", "category": "flagship"},
        ],
        "embedding": [
            # Anthropic relies on OpenAI or standard embedding models
            {"id": "text-embedding-3-small", "name": "Text Embedding 3 Small (OpenAI Compatible)", "dimensions": 1536},
        ],
    },
    "gemini": {
        "chat": [
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro (Flagship)", "category": "flagship"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash (Fast)", "category": "fast"},
            {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash (Next-Gen)", "category": "fast"},
        ],
        "embedding": [
            {"id": "models/text-embedding-004", "name": "Google Text Embedding 004 (768 dims)", "dimensions": 768},
            {"id": "models/embedding-001", "name": "Google Embedding 001 (768 dims)", "dimensions": 768},
        ],
    },
}


class ModelDiscoveryService:
    """
    Singleton Service to introspect available models dynamically from LLM vendor APIs
    with thread-safe in-memory TTL caching.
    """

    _instance: "ModelDiscoveryService | None" = None
    CACHE_TTL_SECONDS = 3600  # 1 hour

    def __new__(cls) -> "ModelDiscoveryService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ModelDiscoveryService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _cache_key(self, provider: str, api_key: str) -> str:
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]
        return f"{provider.lower()}:{key_hash}"

    async def get_models(
        self, provider: str, api_key: str, base_url: str | None = None
    ) -> dict[str, Any]:
        """Fetch models dynamically from vendor API with caching."""
        provider_clean = provider.lower()
        if provider_clean == "google":
            provider_clean = "gemini"

        cache_key = self._cache_key(provider_clean, api_key)
        now = datetime.now(timezone.utc)

        if cache_key in self._cache:
            ts, data = self._cache[cache_key]
            if (now - ts).total_seconds() < self.CACHE_TTL_SECONDS:
                return data

        # Query live vendor API
        discovered = await self._discover_from_vendor(provider_clean, api_key, base_url)
        self._cache[cache_key] = (now, discovered)
        return discovered

    @classmethod
    async def fetch_and_cache_models(
        cls, provider: str, api_key: str, base_url: str | None = None
    ) -> dict[str, Any]:
        """Convenience method delegating to Singleton instance."""
        return await cls.get_instance().get_models(provider, api_key, base_url)

    def clear_cache(self, provider: str | None = None) -> None:
        """Clear cache for a specific provider or all entries."""
        if provider:
            prefix = f"{provider.lower()}:"
            keys_to_remove = [k for k in self._cache if k.startswith(prefix)]
            for k in keys_to_remove:
                self._cache.pop(k, None)
        else:
            self._cache.clear()

    @classmethod
    def invalidate_cache(cls, provider: str | None = None) -> None:
        """Convenience method delegating to Singleton instance."""
        cls.get_instance().clear_cache(provider)

    @classmethod
    async def _discover_from_vendor(
        cls, provider: str, api_key: str, base_url: str | None = None
    ) -> dict[str, Any]:
        if provider == "openai":
            return await cls._discover_openai(api_key, base_url)
        elif provider == "anthropic":
            return await cls._discover_anthropic(api_key, base_url)
        elif provider == "gemini":
            return await cls._discover_gemini(api_key, base_url)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @classmethod
    async def _discover_openai(cls, api_key: str, base_url: str | None = None) -> dict[str, Any]:
        url = (base_url.rstrip("/") + "/models") if base_url else "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code != 200:
                    logger.warning(f"OpenAI models API returned {res.status_code}: {res.text}")
                    return FALLBACK_MODELS["openai"]

                data = res.json()
                raw_models = data.get("data", [])
                
                chat_models = []
                embedding_models = []

                for m in raw_models:
                    model_id = m.get("id", "")
                    # Filter chat/reasoning models
                    if any(model_id.startswith(p) for p in ["gpt-4", "gpt-3.5", "o1", "o3", "chatgpt"]):
                        if "audio" not in model_id and "realtime" not in model_id and "transcription" not in model_id:
                            cat = "reasoning" if (model_id.startswith("o1") or model_id.startswith("o3")) else (
                                "fast" if ("mini" in model_id or "turbo" in model_id) else "flagship"
                            )
                            chat_models.append({
                                "id": model_id,
                                "name": model_id,
                                "category": cat,
                            })
                    # Filter embedding models
                    elif "embedding" in model_id:
                        dims = 3072 if "large" in model_id else 1536
                        embedding_models.append({
                            "id": model_id,
                            "name": f"{model_id} ({dims} dims)",
                            "dimensions": dims,
                        })

                # Sort by relevance
                chat_models.sort(key=lambda x: (0 if "gpt-4o" in x["id"] else 1, x["id"]))

                if not chat_models:
                    chat_models = FALLBACK_MODELS["openai"]["chat"]
                if not embedding_models:
                    embedding_models = FALLBACK_MODELS["openai"]["embedding"]

                return {
                    "valid": True,
                    "chat_models": chat_models,
                    "embedding_models": embedding_models,
                }
        except Exception as e:
            logger.warning(f"Error fetching OpenAI models: {e}. Falling back to default list.")
            return {
                "valid": True,
                "chat_models": FALLBACK_MODELS["openai"]["chat"],
                "embedding_models": FALLBACK_MODELS["openai"]["embedding"],
            }

    @classmethod
    async def _discover_anthropic(cls, api_key: str, base_url: str | None = None) -> dict[str, Any]:
        url = (base_url.rstrip("/") + "/models") if base_url else "https://api.anthropic.com/v1/models"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    raw_models = data.get("data", [])
                    chat_models = []
                    for m in raw_models:
                        model_id = m.get("id", "")
                        display_name = m.get("display_name", model_id)
                        cat = "fast" if "haiku" in model_id.lower() else "flagship"
                        chat_models.append({
                            "id": model_id,
                            "name": display_name,
                            "category": cat,
                        })
                    if not chat_models:
                        chat_models = FALLBACK_MODELS["anthropic"]["chat"]
                else:
                    chat_models = FALLBACK_MODELS["anthropic"]["chat"]

                return {
                    "valid": True,
                    "chat_models": chat_models,
                    "embedding_models": FALLBACK_MODELS["anthropic"]["embedding"],
                }
        except Exception as e:
            logger.warning(f"Error fetching Anthropic models: {e}. Falling back to default list.")
            return {
                "valid": True,
                "chat_models": FALLBACK_MODELS["anthropic"]["chat"],
                "embedding_models": FALLBACK_MODELS["anthropic"]["embedding"],
            }

    @classmethod
    async def _discover_gemini(cls, api_key: str, base_url: str | None = None) -> dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                if res.status_code != 200:
                    logger.warning(f"Gemini models API returned {res.status_code}: {res.text}")
                    return {
                        "valid": True,
                        "chat_models": FALLBACK_MODELS["gemini"]["chat"],
                        "embedding_models": FALLBACK_MODELS["gemini"]["embedding"],
                    }

                data = res.json()
                raw_models = data.get("models", [])
                chat_models = []
                embedding_models = []

                for m in raw_models:
                    model_name = m.get("name", "")  # e.g. "models/gemini-1.5-pro"
                    display_name = m.get("displayName", model_name)
                    methods = m.get("supportedGenerationMethods", [])

                    clean_id = model_name.replace("models/", "")

                    if "generateContent" in methods and "gemini" in model_name:
                        cat = "fast" if "flash" in model_name else "flagship"
                        chat_models.append({
                            "id": clean_id,
                            "name": f"{display_name} ({clean_id})",
                            "category": cat,
                        })
                    elif "embedContent" in methods or "batchEmbedContents" in methods:
                        embedding_models.append({
                            "id": model_name,
                            "name": f"{display_name} ({model_name})",
                            "dimensions": 768,
                        })

                if not chat_models:
                    chat_models = FALLBACK_MODELS["gemini"]["chat"]
                if not embedding_models:
                    embedding_models = FALLBACK_MODELS["gemini"]["embedding"]

                return {
                    "valid": True,
                    "chat_models": chat_models,
                    "embedding_models": embedding_models,
                }
        except Exception as e:
            logger.warning(f"Error fetching Gemini models: {e}. Falling back to default list.")
            return {
                "valid": True,
                "chat_models": FALLBACK_MODELS["gemini"]["chat"],
                "embedding_models": FALLBACK_MODELS["gemini"]["embedding"],
            }
