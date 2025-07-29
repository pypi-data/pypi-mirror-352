from .types import CriteriaTestCase

LONG_CONTEXT_DATA: dict[str, CriteriaTestCase] = {
    "long_context_summary_32000": CriteriaTestCase(
        id="long_context_summary_32000",
        request_data={
            "messages": [
                {
                    "role": "user",
                    "content": "Please summarize the following research paper abstract and identify its key findings:"
                    + "Abstract: "
                    + "This study investigates the impact of climate change on global agricultural productivity " * 2500
                    + "\n\nGive me the first 1000 characters of the abstract.",
                }
            ]
        },
        criteria="long_context",
        criteria_params={"expected_output": ["climate change", "repeat", "abstract"]},
    ),
}
