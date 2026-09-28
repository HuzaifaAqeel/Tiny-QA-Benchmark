# ⚡ Tiny-QA-Benchmark

**Micro-benchmark suite for LLMs — a 52-item gold set, a synthetic pack generator, and a CI-ready eval harness that exposes model failures in seconds.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

Big eval suites are slow and expensive to run on every commit. **Tiny-QA-Benchmark** is the opposite:
an ultra-lightweight QA benchmark designed as the *unit test* for your LLM system. A hand-crafted
52-question gold set gives you deterministic regression checks in seconds, the generator CLI mints
bespoke synthetic packs for any language / topic / difficulty, and the evaluator scores any
LiteLLM-compatible model on exact-match accuracy, Levenshtein-ratio accuracy, and latency.

## Features

- **52-item gold set** (`data/core_en/`) — hand-crafted English QA pairs with SHA-256 provenance
  hashes for deterministic regression testing
- **Synthetic generator CLI** — mint custom micro-benchmarks on demand: `--num`, `--languages`,
  `--categories`, `--difficulty`, any LiteLLM provider
- **Offline-friendly evaluator** — exact-match + Levenshtein-ratio scoring, latency percentiles,
  JSON results for dashboards
- **Multilingual packs** — pre-built synthetic packs included (English 40-pack; extend to 10+ languages)
- **CI-ready** — seconds-long runs, JSON output, deterministic seeds
- **Croissant metadata** — JSON-LD dataset descriptors for discoverability

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

**Evaluate a model on the gold set** (any LiteLLM model id; needs the provider's API key):

```bash
python tools/eval/eval.py --dataset data/core_en/core_en.json \
    --model gemini/gemini-2.5-flash --out eval_results.json
# 🔹 gemini/gemini-2.5-flash: EM=94.2% | Lev≥0.75=98.1% | p50=0.42s
```

**No API key? Run the mock demo** — the full scoring pipeline with canned answers:

```bash
python examples/run_demo_eval.py
```

**Generate a synthetic pack** (needs an LLM provider key):

```bash
python -m tools.generator.tinyqabenchmarkpp.generate \
    --num 20 --languages en --categories science,history --difficulty medium \
    --model gemini/gemini-2.5-flash --output-file my_pack.json
```

## How It Works

1. **Gold set** — 52 hand-written QA items (`text`, `label`, `context`, `tags`, `lang`, `sha256`)
   form an immutable core you never edit — regressions show up as diffs, not debates.
2. **Generate** — the generator few-shot-prompts an LLM for new items in the same schema,
   validates the JSON structure, and stamps each item with a SHA-256 hash.
3. **Evaluate** — each model answer is normalized (case, articles, punctuation) then scored with
   exact match and Levenshtein ratio; per-item latencies give you p50/p95 for cost awareness.

## Environment variables

| Variable | Needed for |
|----------|------------|
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | Live evals + pack generation (any LiteLLM provider) |

Copy `.env.example` to `.env`. The mock demo runs with no keys.

## Project structure

```
tiny-qa-benchmark/
├── tools/
│   ├── eval/eval.py              # evaluator: EM + Levenshtein scoring, JSON output
│   └── generator/                # synthetic pack generator (LiteLLM-powered CLI)
├── data/
│   ├── core_en/core_en.json      # 52-item immutable gold set
│   └── pack_en_40.json           # pre-built 40-item English synthetic pack
├── metadata/                     # Croissant JSON-LD descriptors
├── examples/
│   └── run_demo_eval.py          # offline mock demo of the eval pipeline
├── LICENCE.data_packs.md         # synthetic data packs license
└── LICENCE.paper.md              # paper license
```

## License

Code: Apache-2.0 — see [LICENSE](LICENSE). Synthetic data packs: see
[LICENCE.data_packs.md](LICENCE.data_packs.md).
