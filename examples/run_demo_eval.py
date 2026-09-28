#!/usr/bin/env python3
"""Demo: run the TQB++ evaluator on the 52-item gold set with a mock model.

The real evaluator calls any LLM via LiteLLM (needs an API key). This demo
patches `litellm.completion` with a local mock so the full scoring pipeline —
exact-match accuracy, Levenshtein-ratio accuracy, latency percentiles —
runs end to end with no key. The metrics printed are computed for real by
`tools/eval/eval.py`; only the model answers are canned.
"""
import importlib.util
import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

EVAL_PATH = os.path.join(ROOT, "tools", "eval", "eval.py")

# Canned answers for the first items of data/core_en/core_en.json.
# Mix of exact hits, near misses, and wrong answers to show the metrics move.
MOCK_ANSWERS = {
    "What is the capital of France?": "Paris",
    "Who wrote Romeo and Juliet?": "William Shakespeare",
    "What is 2 + 2?": "4",
    "What is the largest planet in our solar system?": "Jupiter",
    "Who painted the Mona Lisa?": "Leonardo da Vinci",
    "What is the derivative of sin(x)?": "cosx",  # near miss: gold is "cos(x)"
    "Who discovered penicillin?": "Louis Pasteur",  # wrong: gold is Alexander Fleming
    "What is 5 factorial?": "100",  # wrong: gold is "120"
    "In what year did the Berlin Wall fall?": "1989",
    "What is the time complexity of binary search on a sorted array?": "O(n)",  # wrong: O(log n)
    "What is the atomic number of carbon?": "6",
    "What is the speed of light in vacuum (m/s)?": "300000000",  # near miss: 299792458
}


def _load_eval_module():
    spec = importlib.util.spec_from_file_location("tqb_eval", EVAL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_completion(**kwargs):
    messages = kwargs.get("messages", [])
    question = messages[-1]["content"] if messages else ""
    answer = MOCK_ANSWERS.get(question, "I don't know")
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=answer))]
    )


def main(n: int = 12) -> None:
    eval_mod = _load_eval_module()
    dataset_path = os.path.join(ROOT, "data", "core_en", "core_en.json")
    with open(dataset_path) as f:
        dataset = json.load(f)[:n]

    with patch.object(eval_mod.litellm, "completion", side_effect=fake_completion):
        result = eval_mod.eval_model("demo-mock", dataset, temperature=0.0, seed=42)

    print()
    print("=" * 64)
    print(f"demo-mock on core_en (first {result['n']} items)")
    print("=" * 64)
    print(f"  Exact-match accuracy : {result['accuracy_em']*100:5.1f}%")
    print(f"  Lev-ratio >= 0.75    : {result['accuracy_lev>=0.75']*100:5.1f}%")
    print(f"  Latency p50          : {result['latency_p50']*1000:5.1f} ms")
    print()
    print(f"  {'question':<38}{'gold':<22}{'pred':<18}EM")
    print("  " + "-" * 60)
    for row in result["detail"]:
        q = row["question"][:36]
        print(f"  {q:<38}{row['gold'][:20]:<22}{row['pred'][:16]:<18}{row['em']}")
    print()
    print("Done. Swap demo-mock for any LiteLLM model id + API key for a live run.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 12)
