import os
from crewai import LLM
from src.shared.config import settings

def get_llm() -> LLM:
    """
    CrewAI + LiteLLM Azure OpenAI configuration.
    This MUST use api_base (not base_url).
    """

    api_base = os.getenv("AZURE_API_BASE")
    api_version = os.getenv("AZURE_API_VERSION", "2024-12-01-preview")

    if not api_base:
        raise ValueError("AZURE_OPENAI_ENDPOINT is missing in .env")

    return LLM(
        # ✅ Azure deployment name (NOT gpt-4o)
        model=f"azure/{settings.openai_model_name}",

        # ✅ Azure OpenAI key
        api_key=settings.openai_api_key,

        # ✅ CRITICAL: LiteLLM expects api_base for Azure
        api_base=api_base,

        # ✅ Required for Azure
        api_version=api_version,

        # ✅ Explicitly tell LiteLLM this is Azure
        api_type="azure",
    )