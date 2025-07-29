from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table
from tqdm import tqdm

from llama_api_bench.core.criterias.criterias import get_criteria
from llama_api_bench.core.interface import ModelConfig, ProviderConfig
from llama_api_bench.core.providers import get_all_provider_configs, get_llamaapi_provider_configs
from llama_api_bench.data.data import ALL_TEST_CASES
from llama_api_bench.data.export import save_to_csv, to_dataframe
from llama_api_bench.data.types import CriteriaTestCase, CriteriaTestResult


def run_one(args: tuple[CriteriaTestCase, ProviderConfig, str, bool]) -> CriteriaTestResult:
    tc, provider_config, model, stream = args
    criteria_func = get_criteria(tc.criteria)
    return criteria_func(test_case=tc, model=model, stream=stream, provider_config=provider_config)


def get_results(
    test_cases: dict[str, CriteriaTestCase],
    provider_configs: list[ProviderConfig],
    parallel: bool = True,
) -> list[CriteriaTestResult]:
    results = []

    # Flatten all combinations to a list
    combinations = [
        (tc, provider_config, m.model, stream)
        for tc in test_cases.values()
        for provider_config in provider_configs
        for m in provider_config.available_models
        for stream in [True, False]
        if tc.criteria not in m.unsupported_test_cases
    ]

    if parallel:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(run_one, combo) for combo in combinations]
            for f in tqdm(as_completed(futures), total=len(futures), desc="Running test cases (parallel)"):
                results.append(f.result())
    else:
        for tc, provider_config, model, stream in tqdm(combinations, desc="Running test cases"):
            criteria_func = get_criteria(tc.criteria)
            r = criteria_func(test_case=tc, model=model, stream=stream, provider_config=provider_config)
            results.append(r)

    return results


def print_result(results: list[CriteriaTestResult], title: str):
    df = to_dataframe(results)
    df["status"] = df["result"].apply(lambda x: "✅" if x["pass"] else "❌")
    df["result"] = df.apply(lambda row: {"pass": True} if row["result"]["pass"] else row["result"], axis=1)
    df = df[["id", "model", "stream", "provider", "status", "result"]]
    _rich_display_dataframe(df, title=title)


def _rich_display_dataframe(df, title="Dataframe"):
    """Display a Pandas DataFrame as a rich table."""
    console = Console()
    table = Table(title=title, show_lines=True)

    for col in df.columns:
        table.add_column(str(col))

    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row.values])

    console.print(table)


def aggregate_metrics(results: list[CriteriaTestResult], print_result: bool = False) -> pd.DataFrame:
    """
    Return aggregated metrics from results in a for visualization.
    """
    group_by = ["model", "criteria"]
    # group_by = ["model", "criteria", "provider", "stream"]

    df = to_dataframe(results)
    df["pass"] = df["result"].apply(lambda x: x["pass"])
    df = (
        df.groupby(group_by)
        .agg(num_pass=("pass", "sum"), num_total=("pass", "count"), pass_rate=("pass", "mean"))
        .reset_index()
    )
    df["status"] = df["pass_rate"].apply(lambda x: "✅" if x == 1.0 else "❌")
    df["pass_rate"] = df.apply(lambda row: f"{row['num_pass']}/{row['num_total']} ({row['pass_rate']:.1%})", axis=1)
    df = df[["model", "criteria", "pass_rate", "status"]]

    if print_result:
        _rich_display_dataframe(df, title="Aggregated Results")

    return df


def run_all_test_cases(verbose: bool = True):
    """
    Run all test cases and print the results.
    """
    results = get_results(
        ALL_TEST_CASES,
        get_llamaapi_provider_configs(),
    )

    save_to_csv(results, "results_all.csv")
    aggregate_metrics(results, print_result=verbose)


def run_test_case(test_case: str):
    """
    Run a specific test case and print the results.
    """
    tc = ALL_TEST_CASES[test_case]
    results = get_results({test_case: tc}, get_llamaapi_provider_configs())
    save_to_csv(results, f"results_test_case_{test_case}.csv")
    print_result(results, f"Test Case: {test_case}")


def run_criteria(criteria: str):
    """
    Run a specific criteria and print the results.
    """
    filtered_test_cases = {k: v for k, v in ALL_TEST_CASES.items() if v.criteria == criteria}
    results = get_results(filtered_test_cases, get_llamaapi_provider_configs())
    save_to_csv(results, f"results_criteria_{criteria}.csv")
    print_result(results, f"Criteria: {criteria}")


def run_provider(provider: str, models_override: list[ModelConfig] | None = None):
    """
    Run a specific provider and print the results.
    """
    filtered_providers = [p for p in get_all_provider_configs() if p.provider.value == provider]
    if models_override:
        for p in filtered_providers:
            p.available_models = list(models_override)

    results = get_results(ALL_TEST_CASES, filtered_providers)
    save_to_csv(results, f"results_provider_{provider}.csv")
    aggregate_metrics(results, print_result=True)


def run_one_test_case(test_case: str, provider: str, model: str, stream: bool):
    """
    Run a specific test case and print the results.
    """
    tc = ALL_TEST_CASES[test_case]
    filtered_providers = [p for p in get_all_provider_configs() if p.provider.value == provider]
    provider_config = filtered_providers[0]

    args = (tc, provider_config, model, stream)

    result = run_one(args)
    pprint(result)
