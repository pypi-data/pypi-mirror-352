# Models and their unsupported test cases
from ..core.interface import ModelConfig

OPENAI_MODEL_CONFIGS: list[ModelConfig] = [
    ModelConfig(model="gpt-4o", unsupported_test_cases=["vision", "usage", "long_context"]),
]
