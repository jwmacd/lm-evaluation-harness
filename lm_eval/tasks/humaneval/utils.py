import evaluate as hf_evaluate

from lm_eval.models.code_extraction import extract_code


try:
    compute_ = hf_evaluate.load("code_eval")
    test_cases = ["assert add(2, 3)==5"]
    candidates = [["def add(a,b): return a*b"]]
    results = compute_.compute(references=test_cases, predictions=candidates, k=[1])
except Exception as e:
    raise e


def pass_at_k(references: list[str], predictions: list[list[str]], k: list[int] = None):
    global compute_
    assert k is not None
    if isinstance(k, int):
        k = [k]
    res = compute_.compute(
        references=references,
        predictions=predictions,
        k=k,
    )
    return res[0]


def build_predictions(resps: list[list[str]], docs: list[dict]) -> list[list[str]]:
    # Apply code extraction to clean responses before concatenating with prompt
    return [[doc["prompt"] + extract_code(r) for r in resp] for resp, doc in zip(resps, docs)]


def build_predictions_instruct(
    resps: list[list[str]], docs: list[dict]
) -> list[list[str]]:
    # Apply code extraction to clean responses before concatenating with prompt
    # Note: The original code tried to remove trailing ```, but our extract_code
    # function handles this more robustly
    return [
        [
            doc["prompt"] + extract_code(r)
            for r in resp
        ]
        for resp, doc in zip(resps, docs)
    ]
