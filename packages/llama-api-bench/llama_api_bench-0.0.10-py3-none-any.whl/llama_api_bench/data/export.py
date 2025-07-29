import json
from typing import List

import pandas as pd

from .types import CriteriaTestResult


def to_dataframe(results: List[CriteriaTestResult]) -> pd.DataFrame:
    """
    Convert a list of CriteriaTestResult objects to a pandas DataFrame.

    Args:
        results: List of CriteriaTestResult objects

    Returns:
        pd.DataFrame: DataFrame containing all results
    """
    # Convert each result to a dictionary
    data = [result.model_dump() for result in results]
    # Create DataFrame
    df = pd.DataFrame(data)
    return df


def save_to_jsonl(results: List[CriteriaTestResult], file_path: str) -> None:
    """
    Save a list of CriteriaTestResult objects to a JSONL file.

    Args:
        results: List of CriteriaTestResult objects
        file_path: Path to save the JSONL file
    """
    df = to_dataframe(results)
    df.to_json(file_path, orient="records", lines=True)


def save_to_csv(results: List[CriteriaTestResult], file_path: str) -> None:
    """
    Save a list of CriteriaTestResult objects to a CSV file.

    Args:
        results: List of CriteriaTestResult objects
        file_path: Path to save the CSV file
    """
    df = to_dataframe(results)
    df["request_json"] = df["request_json"].apply(lambda x: json.dumps(x))
    df["response_json"] = df["response_json"].apply(lambda x: json.dumps(x))
    df.to_csv(file_path, index=False)
