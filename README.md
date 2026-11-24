# N-ary Supply Chain Event Dataset

This repository accompanies the paper "A Curated N-ary Supply Chain Event Dataset: Preliminary Studies on LLM-assisted Extraction Framework", accepted at the KGBigdata 2026 Workshop, held in conjunction with IEEE BigData 2026.

## Overview

We present a curated N-ary supply chain event dataset derived from fiscal-year 2024 SEC Form 10-K filings of 34 companies in the automotive and technology ecosystem. The annotations are based on Item 1 (*Business*) and Item 1A (*Risk Factors*).

Each event is represented by an event category, a typed subject–relation–object triple, and optional qualifier role–value pairs. This representation preserves contextual attributes beyond conventional triples. The dataset was constructed through LLM-assisted pre-annotation followed by manual review and correction.

## Dataset Statistics

| Statistic | Value |
| --- | ---: |
| SEC Form 10-K filings | 34 |
| Annotated events | 18,362 |
| Event categories | 31 (30 named categories and `Other`) |
| Entity types | 15 (14 named types and `OTHER`) |
| Distinct entity names | 19,330 |

## Dataset and Annotation Schema

| File | Description |
| --- | --- |
| [`all_nary.json`](all_nary.json) | Complete dataset containing 18,362 annotated events across 31 event categories. |
| [`schemas/annotation_schema.md`](schemas/annotation_schema.md) | Definitions of the 31 event categories and 15 entity types, including examples and possible relation expressions. |

The dataset is distributed as a JSON array, with one annotated event per element. Relations listed in the annotation schema are illustrative rather than an exhaustive set of permitted expressions.

### Annotation Format

Each event includes six core fields and may contain additional qualifier attributes.

| Field | Description |
| --- | --- |
| `event_type` | Event category |
| `subject` | Subject argument |
| `subject_type` | Subject entity type |
| `relation` | Relation expression |
| `object` | Object argument |
| `object_type` | Object entity type |
| Additional fields | Optional qualifier attributes, such as `time` or `location` |

The following example illustrates the JSON representation; it is not a verbatim record from the corpus:

```json
{
  "event_type": "Manufacturing",
  "subject": "Alpha Corp.",
  "subject_type": "ORG",
  "relation": "manufacture",
  "object": "battery components",
  "object_type": "PRODUCT",
  "location": "Texas"
}
```

### Loading the Dataset

```python
import json

with open("all_nary.json", "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"Number of events: {len(events):,}")
print(events[0])
```

## Extraction Framework

The repository also provides the implementation of the six-stage LLM-assisted N-ary event extraction framework described in the paper:

1. Event candidate detection
2. Hybrid event classification using LLM confidence scores and Sentence-BERT similarity
3. Core triple and entity-type extraction
4. Compound-object decomposition
5. Qualifier extraction
6. N-ary event assembly and schema validation

The extraction experiments focus on **Competition, Manufacturing, Supply, and Investment**, a four-category subset of the full 31-category dataset. The framework uses **Llama 3 8B** via [Ollama](https://ollama.com/) and **Sentence-BERT** (`all-MiniLM-L6-v2`).

### Environment

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Install Ollama separately and download the language model:

```bash
ollama pull llama3:8b
```

### Experimental Runner

[`main.py`](main.py) is the five-seed runner used in Experiment 1 (seeds 41–45). Each run requires 50 passage-level inputs in a corresponding `data/experiments/exp1_dataset_seed*.json` file. These evaluation inputs are separate from the full annotation corpus; `all_nary.json` is not a direct input to this runner.

## Repository Structure

```text
.
├── README.md
├── all_nary.json
├── main.py
├── requirements.txt
├── schemas/
│   ├── annotation_schema.md
│   ├── core_rules.txt
│   └── event_families.txt
└── src/
    └── nary_extraction/
        ├── __init__.py
        ├── config.py
        ├── event_specs.py
        ├── graph.py
        ├── nodes.py
        ├── prompts.py
        ├── schemas.py
        └── utils.py
```

## Citation

If you use the dataset or extraction framework, please cite the accompanying paper:

> *A Curated N-ary Supply Chain Event Dataset: Preliminary Studies on LLM-assisted Extraction Framework.* KGBigdata 2026 Workshop, IEEE BigData 2026.
