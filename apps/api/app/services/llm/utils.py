from typing import Any


def extract_text_content(content: Any) -> str:
    """
    Extracts clean text string from diverse LLM response/chunk content formats:
    - plain string
    - list of content blocks/dicts (e.g. Google Gemini, Anthropic [{'type': 'text', 'text': '...'}])
    - objects with .text attributes
    - dictionaries with 'text' or 'content' keys
    """
    if not content:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if "text" in item and isinstance(item["text"], str):
                    parts.append(item["text"])
                elif "content" in item and isinstance(item["content"], str):
                    parts.append(item["content"])
            elif hasattr(item, "text") and isinstance(item.text, str):
                parts.append(item.text)
        return "".join(parts)
    if isinstance(content, dict):
        if "text" in content and isinstance(content["text"], str):
            return content["text"]
        if "content" in content and isinstance(content["content"], str):
            return content["content"]
    return ""
