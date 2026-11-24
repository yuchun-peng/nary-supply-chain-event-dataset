import sys
import time
from pathlib import Path
from collections import Counter


# Paths

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))


from nary_extraction.config import (
    MODEL_NAME,
    RUN_LIMIT,
)

from nary_extraction.graph import (
    build_graph,
)

from nary_extraction.utils import (
    load_json,
    save_json,
)


# Experiment settings

SEEDS = range(41, 46)

EXP1_DIR = ROOT / "data" / "experiments"
OUTPUT_DIR = ROOT / "data" / "output"

EXPECTED_CHUNKS = 50


# Helpers

def get_event_type(item):
    return (
        item.get("event_type")
        or item.get("final_event_type")
        or "UNKNOWN"
    )


def run_seed(seed: int) -> dict:

    exp1_file = (
        EXP1_DIR
        / f"exp1_dataset_seed{seed}.json"
    )

    output_file = (
        OUTPUT_DIR
        / f"predictions_exp1_seed{seed}.json"
    )

    if not exp1_file.exists():
        raise FileNotFoundError(
            f"Missing dataset: {exp1_file}"
        )

    dataset = load_json(exp1_file)

    if len(dataset) != EXPECTED_CHUNKS:
        raise ValueError(
            f"Seed {seed}: expected {EXPECTED_CHUNKS} "
            f"chunks, found {len(dataset)}."
        )

    if RUN_LIMIT is None:
        records = dataset
    else:
        records = dataset[:RUN_LIMIT]

    if len(records) != EXPECTED_CHUNKS:
        raise ValueError(
            f"Seed {seed}: RUN_LIMIT restricts "
            f"the experiment to {len(records)} chunks. "
            f"Expected {EXPECTED_CHUNKS}."
        )

    # Build a separate graph for each seed.
    graph = build_graph()

    predictions = []

    total_counts = {
        "node1_detected_events": 0,
        "node2_total_classified": 0,
        "node2_target_candidates": 0,
        "node2_non_target_candidates": 0,
        "node3_core_events": 0,
        "node4_atomic_events": 0,
        "node5_enriched_events": 0,
        "final_events": 0,
    }

    total_node2_target_distribution = Counter()

    print()
    print("=" * 70)
    print(f"N-ARY EXTRACTION PIPELINE | SEED {seed}")
    print("=" * 70)

    print(f"Model: {MODEL_NAME}")
    print(f"Seed: {seed}")
    print(f"Chunks: {len(records)}")
    print(f"Input: {exp1_file}")
    print(f"Output: {output_file}")

    start = time.perf_counter()

    for index, record in enumerate(
        records,
        start=1,
    ):

        print(
            f"\n\n[Seed {seed}] "
            f"[{index}/{len(records)}] "
            f"{record['chunk_id']} | "
            f"{record['company']}"
        )

        print("-" * 70)

        try:

            state = graph.invoke({
                "chunk_id": record["chunk_id"],
                "company": record["company"],
                "text": record["text"],
            })

            detected_events = state.get(
                "detected_events",
                [],
            )

            candidates = state.get(
                "candidates",
                [],
            )

            non_target_candidates = state.get(
                "non_target_candidates",
                [],
            )

            core_events = state.get(
                "core_events",
                [],
            )

            atomic_events = state.get(
                "atomic_events",
                [],
            )

            enriched_events = state.get(
                "enriched_events",
                [],
            )

            prediction = state.get(
                "prediction",
                {"events": []},
            )

            final_events = prediction.get(
                "events",
                [],
            )

            node2_target_distribution = Counter(
                get_event_type(item)
                for item in candidates
            )

            node2_total_classified = (
                len(candidates)
                + len(non_target_candidates)
            )

            # Pipeline diagnostics

            print(
                "\n--- PIPELINE COUNTS ---"
            )

            print(
                "Node 1 detected events:",
                len(detected_events),
            )

            print(
                "Node 2 total classified:",
                node2_total_classified,
            )

            print(
                "Node 2 target candidates:",
                len(candidates),
            )

            print(
                "Node 2 non-target candidates:",
                len(non_target_candidates),
            )

            print(
                "Node 2 target distribution:",
                dict(node2_target_distribution),
            )

            print(
                "Node 3 core events:",
                len(core_events),
            )

            print(
                "Node 4 atomic events:",
                len(atomic_events),
            )

            print(
                "Node 5 enriched events:",
                len(enriched_events),
            )

            print(
                "Final events:",
                len(final_events),
            )

            # Node 1 / Node 2 consistency check

            if (
                len(detected_events)
                != node2_total_classified
            ):

                print(
                    "\n!!! WARNING !!!"
                )

                print(
                    "Node 1 detected count does not "
                    "match Node 2 classified count."
                )

                print(
                    "Node 1:",
                    len(detected_events),
                )

                print(
                    "Node 2 total:",
                    node2_total_classified,
                )

            # Diagnostic samples

            if detected_events:

                print(
                    "\nNode 1 sample:"
                )

                for item in detected_events[:3]:
                    print(" ", item)

            if candidates:

                print(
                    "\nNode 2 target sample:"
                )

                for item in candidates[:3]:

                    print(
                        " ",
                        get_event_type(item),
                        "|",
                        item.get("evidence", ""),
                    )

            if non_target_candidates:

                print(
                    "\nNode 2 non-target sample:"
                )

                for item in non_target_candidates[:3]:

                    print(
                        " ",
                        item.get(
                            "initial_llm_event_type",
                            "UNKNOWN",
                        ),
                        "->",
                        item.get(
                            "event_type",
                            "UNKNOWN",
                        ),
                        "|",
                        item.get("evidence", ""),
                    )

            # Accumulate pipeline counts

            total_counts[
                "node1_detected_events"
            ] += len(detected_events)

            total_counts[
                "node2_total_classified"
            ] += node2_total_classified

            total_counts[
                "node2_target_candidates"
            ] += len(candidates)

            total_counts[
                "node2_non_target_candidates"
            ] += len(non_target_candidates)

            total_counts[
                "node3_core_events"
            ] += len(core_events)

            total_counts[
                "node4_atomic_events"
            ] += len(atomic_events)

            total_counts[
                "node5_enriched_events"
            ] += len(enriched_events)

            total_counts[
                "final_events"
            ] += len(final_events)

            total_node2_target_distribution.update(
                node2_target_distribution
            )

            # Save prediction

            predictions.append({
                "chunk_id": record["chunk_id"],
                "company": record["company"],
                "text": record["text"],
                "events": final_events,

                "pipeline_counts": {
                    "node1_detected_events":
                        len(detected_events),

                    "node2_total_classified":
                        node2_total_classified,

                    "node2_target_candidates":
                        len(candidates),

                    "node2_non_target_candidates":
                        len(non_target_candidates),

                    "node2_target_distribution":
                        dict(node2_target_distribution),

                    "node3_core_events":
                        len(core_events),

                    "node4_atomic_events":
                        len(atomic_events),

                    "node5_enriched_events":
                        len(enriched_events),

                    "final_events":
                        len(final_events),
                },

                "status": "ok",
            })

        except Exception as error:

            print(
                f"\nERROR: {error}"
            )

            predictions.append({
                "chunk_id": record["chunk_id"],
                "company": record["company"],
                "text": record["text"],
                "events": [],
                "status": "error",
                "error": str(error),
            })

        # Save after every chunk.
        save_json(
            output_file,
            predictions,
        )

    elapsed = (
        time.perf_counter()
        - start
    )

    ok = sum(
        item["status"] == "ok"
        for item in predictions
    )

    error_count = len(predictions) - ok

    # Summary for this seed

    print()
    print("=" * 70)
    print(f"SEED {seed} | TOTAL PIPELINE COUNTS")
    print("=" * 70)

    for key, value in total_counts.items():
        print(
            f"{key}: {value}"
        )

    print(
        "\nNode 2 target distribution:"
    )

    if total_node2_target_distribution:

        for event_type, count in (
            total_node2_target_distribution
            .most_common()
        ):

            print(
                f"  {event_type}: {count}"
            )

    else:
        print(
            "  No target candidates"
        )

    print()
    print(f"Seed: {seed}")
    print(f"Finished: {ok}/{len(predictions)} chunks")
    print(f"Errors: {error_count}")
    print(f"Final events: {total_counts['final_events']}")
    print(f"Time: {elapsed:.1f}s")
    print(f"Saved: {output_file}")

    return {
        "seed": seed,
        "chunks": len(records),
        "successful_chunks": ok,
        "errors": error_count,
        "final_events": total_counts["final_events"],
        "elapsed_seconds": round(elapsed, 2),
        "output_file": str(output_file),
    }


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("=" * 70)
    print("EXP1 MULTI-SEED EXTRACTION")
    print("=" * 70)

    print(f"Model: {MODEL_NAME}")
    print(f"Seeds: {list(SEEDS)}")
    print(f"Chunks per seed: {EXPECTED_CHUNKS}")
    print(f"Total chunks: {len(SEEDS) * EXPECTED_CHUNKS}")

    # Validate all inputs before starting LLM inference.

    for seed in SEEDS:

        exp1_file = (
            EXP1_DIR
            / f"exp1_dataset_seed{seed}.json"
        )

        if not exp1_file.exists():
            raise FileNotFoundError(
                f"Missing dataset: {exp1_file}"
            )

    overall_start = time.perf_counter()

    results = []

    for seed in SEEDS:

        result = run_seed(seed)
        results.append(result)

    total_elapsed = (
        time.perf_counter()
        - overall_start
    )

    # Final comparison

    print()
    print("=" * 70)
    print("EXP1 MULTI-SEED EXTRACTION SUMMARY")
    print("=" * 70)

    print(
        f"{'Seed':<8}"
        f"{'Success':<12}"
        f"{'Errors':<10}"
        f"{'Events':<12}"
        f"{'Time(s)':<12}"
    )

    print("-" * 70)

    for result in results:

        print(
            f"{result['seed']:<8}"
            f"{result['successful_chunks']:<12}"
            f"{result['errors']:<10}"
            f"{result['final_events']:<12}"
            f"{result['elapsed_seconds']:<12.1f}"
        )

    print("-" * 70)

    total_events = sum(
        result["final_events"]
        for result in results
    )

    total_errors = sum(
        result["errors"]
        for result in results
    )

    print(f"Total predicted events: {total_events}")
    print(f"Total chunk errors: {total_errors}")
    print(f"Total time: {total_elapsed:.1f}s")

    summary_file = (
        OUTPUT_DIR
        / "exp1_multiseed_summary.json"
    )

    save_json(
        summary_file,
        results,
    )

    print()
    print(f"Summary saved: {summary_file}")

    print()
    print("=" * 70)
    print("ALL FIVE SEEDS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()