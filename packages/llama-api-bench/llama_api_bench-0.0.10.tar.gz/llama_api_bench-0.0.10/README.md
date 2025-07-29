# llama_api_bench

[![PyPI - Version](https://img.shields.io/pypi/v/llama-api-bench.svg)](https://pypi.org/project/llama-api-bench)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/llama-api-bench.svg)](https://pypi.org/project/llama-api-bench)

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```bash
pip install llama-api-bench
```

**Install from source**
```bash
pip install -e .

# dev
pip install -e ".[dev]"
```

## Usage

**Run All**
```bash
llama-api-bench run-all
```

**Run Subset**

- Run on a specific criteria for all models and providers
```bash
llama-api-bench run-criteria --criteria tool_call
```

- Run on a specific test case data for all models and providers
```bash
llama-api-bench run-test-case --test-case tool_call_get_weather
```

- Run all test cases on a specific provider
```bash
llama-api-bench run-provider --provider openrouter
```

- Run on a specific test case x model x provider
```bash
# streaming
llama-api-bench run --test-case basic_dont_call_tool --model Cerebras-Llama-4-Scout-17B-16E-Instruct --provider llamaapi --stream

# non-streaming
llama-api-bench run --test-case basic_dont_call_tool --model Cerebras-Llama-4-Scout-17B-16E-Instruct --provider llamaapi --no-stream
```

- Run on specific provider x model
```bash
llama-api-bench run-provider --provider openai --models gpt-4o

llama-api-bench run-provider --provider llamaapi --models Llama-4-Maverick-17B-128E-Instruct-FP8
```

![cli](./assets/cli.png)

## Customization

#### Add a New Test Case / Criteria
1. Add a new test case in [llama_api_bench/data/](./src/llama_api_bench/data/).
2. If the new test case requires a new Test Criteria to run evaluation, add it to [llama_api_bench/core/criterias](./src/llama_api_bench/core/criterias/).

#### Add New Provider
1. Add supported models in [llama_api_bench/models/](./src/llama_api_bench/models/). See an example in [llamaapi.py](./src/llama_api_bench/models/llamaapi.py).
2. Add ProviderConfig in [llama_api_bench/core/providers.py](./src/llama_api_bench/core/providers.py).
3. If the provider requires has a new request format, add it to [get_request_json](./src/llama_api_bench/core/criterias/common.py).
4. If the provider requires a new response format parsing, add its evaluation criteria in [llama_api_bench/core/criterias](./src/llama_api_bench/core/criterias/).

## License

`llama-api-bench` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
