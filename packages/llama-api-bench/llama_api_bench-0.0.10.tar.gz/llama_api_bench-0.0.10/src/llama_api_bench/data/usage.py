from .types import CriteriaTestCase

USAGE_DATA: dict[str, CriteriaTestCase] = {
    "usage_word_count": CriteriaTestCase(
        id="usage_word_count",
        request_data={"messages": [{"role": "user", "content": "How many words are in this sentence?"}]},
        criteria="usage",
        criteria_params={
            "num_prompt_tokens": 18,
        },
    ),
}
