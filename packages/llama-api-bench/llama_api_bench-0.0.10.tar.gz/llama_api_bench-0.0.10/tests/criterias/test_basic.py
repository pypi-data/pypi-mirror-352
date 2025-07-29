from llama_api_bench.core.criterias.criterias import get_criteria


def test_check_basic_chat_completion():
    tc = get_criteria("basic_chat_completion")
    assert tc is not None
