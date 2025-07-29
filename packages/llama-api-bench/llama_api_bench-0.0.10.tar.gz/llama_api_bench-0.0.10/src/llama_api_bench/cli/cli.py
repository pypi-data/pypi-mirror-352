from typing import Annotated, Optional

import typer

from llama_api_bench.data.data import ALL_TEST_CASES

app = typer.Typer(
    name="llama-api-bench",
    help="A CLI for interacting with llama-api-bench.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def run_all(verbose: Annotated[bool, typer.Option(help="Print a more verbose output.")] = True):
    """
    Run all test cases for all models and providers
    """
    if verbose:
        typer.echo("Running all test cases...")

    from llama_api_bench.core.run import run_all_test_cases

    run_all_test_cases(verbose=verbose)


@app.command()
def run_test_case(
    test_case: Annotated[str, typer.Option(help="The name of the test case to run.")],
):
    """
    Run a specific test case for all models and providers
    """
    from llama_api_bench.core.run import run_test_case

    if test_case is not None and test_case not in ALL_TEST_CASES:
        raise typer.BadParameter(
            f"Invalid test case: {test_case}. Please choose from: {', '.join(ALL_TEST_CASES.keys())}"
        )

    run_test_case(test_case=test_case)


@app.command()
def run_criteria(
    criteria: Annotated[str, typer.Option(help="The name of the criteria to run.")],
):
    """
    Run a specific criteria for all models and providers
    """
    from llama_api_bench.core.run import run_criteria

    all_criterias = set([x.criteria for x in ALL_TEST_CASES.values()])

    if criteria not in all_criterias:
        raise typer.BadParameter(f"Invalid criteria: {criteria}. Please choose from: {', '.join(all_criterias)}")

    run_criteria(criteria=criteria)


@app.command()
def run_provider(
    provider: Annotated[str, typer.Option(help="The name of the provider to run.")],
    models: Annotated[Optional[list[str]], typer.Option(help="The name of the model to run.")] = None,
):
    """
    Run a specific provider for all models for that provider
    """
    from llama_api_bench.core.providers import get_all_provider_configs
    from llama_api_bench.core.run import run_provider

    all_providers = set([p.provider.value for p in get_all_provider_configs()])

    if provider not in all_providers:
        raise typer.BadParameter(f"Invalid provider: {provider}. Please choose from: {', '.join(all_providers)}")

    models_override = []
    if models is not None:
        provider_config = [p for p in get_all_provider_configs() if p.provider.value == provider][0]
        models_override = [m for m in provider_config.available_models if m.model in models]
        if len(models_override) == 0:
            raise typer.BadParameter(f"Invalid model: {models} for provider: {provider}")

    run_provider(provider=provider, models_override=models_override)


@app.command()
def run(
    test_case: Annotated[str, typer.Option(help="The name of the test case to run.")],
    provider: Annotated[str, typer.Option(help="The name of the provider to run.")],
    model: Annotated[str, typer.Option(help="The name of the model to run.")],
    stream: Annotated[bool, typer.Option(help="Whether to run the test case in streaming mode.")],
):
    """
    Run a specific test case for a specific provider and model
    """
    from llama_api_bench.core.run import run_one_test_case

    run_one_test_case(test_case=test_case, provider=provider, model=model, stream=stream)


if __name__ == "__main__":
    app()
