import os

from llama_api_client import LlamaAPIClient
from openai import OpenAI

from ..models.llamaapi import LLAMA_API_MODEL_CONFIGS
from ..models.openai import OPENAI_MODEL_CONFIGS
from ..models.openrouter import OPENROUTER_MODEL_CONFIGS
from .interface import ProviderConfig, ProviderEnum

ProviderClient = LlamaAPIClient | OpenAI


def get_all_provider_configs() -> list[ProviderConfig]:
    return [
        ProviderConfig(
            provider=ProviderEnum.LLAMAAPI_OPENAI_COMPAT,
            provider_params={"base_url": "https://api.llama.com/compat/v1/", "api_key": os.getenv("LLAMA_API_KEY")},
            available_models=LLAMA_API_MODEL_CONFIGS,
            extra_params={"stream_options": {"include_usage": True}},
        ),
        ProviderConfig(
            provider=ProviderEnum.LLAMAAPI,
            provider_params={"api_key": os.getenv("LLAMA_API_KEY")},
            available_models=LLAMA_API_MODEL_CONFIGS,
        ),
        ProviderConfig(
            provider=ProviderEnum.OPENROUTER,
            provider_params={
                "base_url": "https://openrouter.ai/api/v1/",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                # hit rate limit too fast, increase the max retries
                "max_retries": 50,
            },
            available_models=OPENROUTER_MODEL_CONFIGS,
            extra_params={"extra_body": {"provider": {"order": ["Meta"], "allow_fallbacks": False}}},
        ),
        ProviderConfig(
            provider=ProviderEnum.OPENAI,
            provider_params={
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            available_models=OPENAI_MODEL_CONFIGS,
        ),
    ]


def get_llamaapi_provider_configs() -> list[ProviderConfig]:
    return [
        p
        for p in get_all_provider_configs()
        if p.provider in {ProviderEnum.LLAMAAPI, ProviderEnum.LLAMAAPI_OPENAI_COMPAT}
    ]


def get_provider_client(provider_config: ProviderConfig) -> ProviderClient:
    """Get the provider client."""
    if provider_config.provider == ProviderEnum.LLAMAAPI:
        return LlamaAPIClient(
            **provider_config.provider_params,
        )
    elif provider_config.provider in {
        ProviderEnum.OPENAI,
        ProviderEnum.LLAMAAPI_OPENAI_COMPAT,
        ProviderEnum.OPENROUTER,
    }:
        return OpenAI(
            **provider_config.provider_params,
        )
    else:
        raise ValueError(f"Provider {provider_config.provider} not supported")
