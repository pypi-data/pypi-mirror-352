from ..core.interface import ModelConfig

LLAMA_API_MODEL_CONFIGS: list[ModelConfig] = [
    ModelConfig(model="Llama-4-Scout-17B-16E-Instruct-FP8", unsupported_test_cases=[]),
    ModelConfig(model="Llama-4-Maverick-17B-128E-Instruct-FP8", unsupported_test_cases=[]),
    ModelConfig(model="Llama-3.3-70B-Instruct", unsupported_test_cases=["vision"]),
    ModelConfig(model="Llama-3.3-8B-Instruct", unsupported_test_cases=["vision"]),
    ModelConfig(model="Cerebras-Llama-4-Scout-17B-16E-Instruct", unsupported_test_cases=["vision"]),
    ModelConfig(model="Groq-Llama-4-Maverick-17B-128E-Instruct", unsupported_test_cases=["vision"]),
    ModelConfig(model="Cerebras-Llama-4-Maverick-17B-128E-Instruct", unsupported_test_cases=["vision"]),
]
