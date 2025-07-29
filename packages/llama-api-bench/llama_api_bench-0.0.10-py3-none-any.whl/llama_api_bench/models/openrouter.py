# Models and their unsupported test cases
from ..core.interface import ModelConfig

OPENROUTER_MODEL_CONFIGS: list[ModelConfig] = [
    ModelConfig(model="meta-llama/llama-4-scout:free", unsupported_test_cases=[]),
    ModelConfig(model="meta-llama/llama-4-maverick:free", unsupported_test_cases=[]),
    ModelConfig(
        model="meta-llama/llama-3.3-70b-instruct:free",
        unsupported_test_cases=["vision"],
    ),
    ModelConfig(
        model="meta-llama/llama-3.3-8b-instruct:free",
        unsupported_test_cases=["vision"],
    ),
]
