import math
from langchain_ollama import ChatOllama
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from .config import (
    MODEL_NAME,
    TEMPERATURE,
    NUM_CTX,
    TARGET_EVENT_TYPES,
    SBERT_MODEL_NAME,
)

from .event_specs import EVENT_SPECS


from .schemas import (
    DetectionOutput,
    ClassificationOutput,
    ScoringOutput,
    CoreOutput,
    SplitOutput,
    RoleOutput,
    State,
)



from .prompts import (
    build_node1_prompt,
    build_node2_prompt,
    build_node2_scoring_prompt,
    build_node3_prompt,
    build_node4_prompt,
    build_node5_prompt,
)


from .utils import (
    invoke_validated_json as _invoke_validated_json,
    looks_coordinated,
    print_node_io,
    source_contains,
)


import re
from pathlib import Path

PROMPT_DIR = Path("exported_prompts")
PROMPT_DIR.mkdir(parents=True, exist_ok=True)


def invoke_validated_json(llm, prompt, schema, node_name):
    match = re.search(r"Node\s+(\d+)", node_name)

    if match:
        node_id = match.group(1)
        filename = f"Node_{node_id}_FULL_PROMPT.txt"
        path = PROMPT_DIR / filename

        # Only save the first actual prompt for each Node
        if not path.exists():
            path.write_text(prompt, encoding="utf-8")
            print(f"[PROMPT EXPORTED] {path}")

    return _invoke_validated_json(
        llm,
        prompt,
        schema,
        node_name,
    )


# Global settings

_llm = None
_embedding_model = None
_event_type_embeddings = None

SUPPORTED_EVENT_TYPES = {
    "Manufacturing",
    "Competition",
    "Supply",
    "Investment",
}

# Temporary Node 2 refine thresholds.
SBERT_REFINE_MIN_SCORE = 0.50
SBERT_REFINE_MIN_MARGIN = 0.03


NODE2_METHOD = "hybrid"

FUSION_ALPHA = 0.5
SOFTMAX_TEMPERATURE = 1.0
MULTILABEL_THRESHOLD = 0.35
SIMILARITY_MIN_COSINE = 0.30


COMPANY_REFERENCES = {
    "we",
    "our",
    "us",
    "ourselves",
    "our company",
    "the company",
    "company",
}


# Model loaders

def get_llm():
    global _llm

    if _llm is None:
        _llm = ChatOllama(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            num_ctx=NUM_CTX,
        )

    return _llm


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            SBERT_MODEL_NAME
        )

    return _embedding_model


# Validation / helpers

def validate_target_event_types():
    configured = set(TARGET_EVENT_TYPES)

    if configured != SUPPORTED_EVENT_TYPES:
        raise ValueError(
            "TARGET_EVENT_TYPES must contain exactly: "
            "Manufacturing, Competition, Supply, Investment. "
            f"Current config: {sorted(configured)}"
        )


def best_event_type(scores: dict) -> tuple[str, float, float]:
    ranked = sorted(
        (
            (event_type, float(scores[event_type]))
            for event_type in TARGET_EVENT_TYPES
        ),
        key=lambda x: x[1],
        reverse=True,
    )

    if not ranked:
        return "NON_TARGET", 0.0, 0.0

    best_type, best_score = ranked[0]

    second_score = (
        ranked[1][1]
        if len(ranked) > 1
        else 0.0
    )

    margin = best_score - second_score

    return best_type, best_score, margin


def normalize_subject(subject: str, company: str) -> str:
    subject = subject.strip()
    lowered = subject.lower()

    if lowered in COMPANY_REFERENCES:
        return company

    if lowered == company.lower():
        return company

    ignore_tokens = {
        "inc",
        "incorporated",
        "corp",
        "corporation",
        "company",
        "co",
        "ltd",
        "limited",
        "plc",
        "llc",
        "holdings",
        "holding",
        "group",
        "the",
        "&",
        "and",
    }

    tokens = [
        token.strip(".,")
        for token in company.split()
        if token.strip(".,").lower() not in ignore_tokens
    ]

    if tokens and lowered == tokens[0].lower():
        return company

    initials = "".join(
        token[0]
        for token in tokens
        if token
    ).lower()

    if lowered == initials:
        return company

    return subject


def build_event_type_text(event_type: str) -> str:
    spec = EVENT_SPECS[event_type]

    definition = spec.get("definition", "")
    examples = spec.get("examples", "")

    example_text = ""

    if examples:
        if isinstance(examples, list):
            example_text = (
                " Examples: "
                + " | ".join(
                    str(x)
                    for x in examples[:3]
                )
            )
        else:
            example_text = (
                f" Examples: {examples}"
            )

    return (
        f"{event_type}. "
        f"{definition}"
        f"{example_text}"
    ).strip()


def get_event_type_embeddings():
    global _event_type_embeddings

    validate_target_event_types()

    if _event_type_embeddings is None:
        model = get_embedding_model()

        texts = [
            build_event_type_text(event_type)
            for event_type in TARGET_EVENT_TYPES
        ]

        embeddings = model.encode(
            texts,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

        _event_type_embeddings = {
            event_type: embedding
            for event_type, embedding in zip(
                TARGET_EVENT_TYPES,
                embeddings,
            )
        }

    return _event_type_embeddings


def embedding_event_scores(evidence: str) -> dict:
    """
    Trigger removed.
    Compare the whole event-centered evidence span against event-type prototypes.
    """
    model = get_embedding_model()

    event_embedding = model.encode(
        evidence,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    type_embeddings = get_event_type_embeddings()

    scores = {}

    for event_type in TARGET_EVENT_TYPES:
        similarity = cos_sim(
            event_embedding,
            type_embeddings[event_type],
        ).item()

        scores[event_type] = round(similarity, 4)

    return scores


def should_refine_classification(
    llm_event_type: str,
    embedding_event_type: str,
    embedding_score: float,
    embedding_margin: float,
) -> bool:

    if llm_event_type == "NON_TARGET":
        return (
            embedding_score >= SBERT_REFINE_MIN_SCORE
            and embedding_margin >= SBERT_REFINE_MIN_MARGIN
        )

    if (
        llm_event_type != embedding_event_type
        and embedding_score >= SBERT_REFINE_MIN_SCORE
        and embedding_margin >= SBERT_REFINE_MIN_MARGIN
    ):
        return True

    return False


# NODE 1

def node1_detect_events(state: State):
    """
    Long text -> event-centered evidence spans.

    Node 1 favors recall.
    It does NOT classify event type.
    It does NOT extract trigger / SRO / modifiers.
    """
    node_input = {
        "text": state["text"],
    }

    result, elapsed, repairs = invoke_validated_json(
        get_llm(),
        build_node1_prompt(state["text"]),
        DetectionOutput,
        "Node 1",
    )

    print("\nNode 1 raw LLM spans:")
    for item in result.events:
        print(item.model_dump())

    detected_events = []
    seen = set()


    for item in result.events:
        evidence = item.evidence.strip()

        if not evidence:
            continue

        if evidence not in state["text"]:
            print(
                "[Node 1 WARNING] Evidence is not an "
                f"exact substring of the source text:\n{evidence}"
            )

        key = evidence.lower()

        if key in seen:
            continue

        seen.add(key)

        candidate_id = (
            f"C{len(detected_events) + 1:03d}"
        )

        detected_events.append({
            "candidate_id": candidate_id,
            "evidence": evidence,
        })

    node_output = {
        "events": detected_events,
        "detected_count": len(detected_events),
        "time_sec": round(elapsed, 2),
        "repairs": repairs,
    }

    print_node_io(
        "Node 1 | Detect event-centered spans",
        node_input,
        node_output,
    )

    return {
        "detected_events": detected_events,
    }



# NODE 2


def similarity_softmax(scores: dict) -> dict:
    if SOFTMAX_TEMPERATURE <= 0:
        raise ValueError(
            "SOFTMAX_TEMPERATURE must be positive."
        )

    scaled = {
        event_type: float(scores[event_type])
        / SOFTMAX_TEMPERATURE
        for event_type in TARGET_EVENT_TYPES
    }

    maximum = max(scaled.values())

    exp_scores = {
        event_type: math.exp(score - maximum)
        for event_type, score in scaled.items()
    }

    total = sum(exp_scores.values())

    return {
        event_type: exp_scores[event_type] / total
        for event_type in TARGET_EVENT_TYPES
    }


def calculate_fusion_scores(
    llm_scores: dict,
    similarity_scores: dict,
) -> dict:
    if not 0 <= FUSION_ALPHA <= 1:
        raise ValueError(
            "FUSION_ALPHA must be between 0 and 1."
        )

    p_other = float(llm_scores["NON_TARGET"])

    return {
        event_type: (
            FUSION_ALPHA * float(llm_scores[event_type])
            + (1 - FUSION_ALPHA)
            * (1 - p_other)
            * float(similarity_scores[event_type])
        )
        for event_type in TARGET_EVENT_TYPES
    }


def select_multilabel_types(
    scores: dict,
) -> list[str]:
    selected = [
        event_type
        for event_type in TARGET_EVENT_TYPES
        if scores[event_type] >= MULTILABEL_THRESHOLD
    ]

    return selected if selected else ["NON_TARGET"]



# NODE 2

def node2_classify_events(state: State):
    """
    Multi-label event classification.

    Node 2-1: LLM classification or confidence scoring.
    Node 2-2: SBERT independently calculates similarity scores.

    Final classification supports LLM-only, similarity-only,
    and LLM-SBERT fusion.

    Each selected event type becomes a separate candidate.
    NON_TARGET candidates continue to Node 3.
    """

    validate_target_event_types()

    if NODE2_METHOD not in {"llm", "similarity", "hybrid"}:
        raise ValueError(
            f"Invalid NODE2_METHOD: {NODE2_METHOD}"
        )

    events = state.get(
        "detected_events",
        [],
    )

    node_input = {
        "events": events,
        "method": NODE2_METHOD,
    }

    if not events:
        print_node_io(
            "Node 2 | Multi-label classification",
            node_input,
            {"results": []},
        )

        return {
            "candidates": [],
            "non_target_candidates": [],
        }

    candidates = []
    non_targets = []
    classification_results = []

    total_elapsed = 0.0
    total_repairs = 0

    for event in events:

        candidate_id = event["candidate_id"]

        llm_event_types = []
        llm_scores = None
        fusion_scores = None

        # Node 2-1: LLM classification

        if NODE2_METHOD == "llm":

            result, elapsed, repairs = invoke_validated_json(
                get_llm(),
                build_node2_prompt([event]),
                ClassificationOutput,
                f"Node 2-1 {candidate_id}",
            )

            total_elapsed += elapsed
            total_repairs += repairs

            if not result.events:
                raise ValueError(
                    "Node 2-1 returned no classification for "
                    f"{candidate_id}"
                )

            for item in result.events:

                if item.candidate_id != candidate_id:
                    raise ValueError(
                        "Node 2 candidate_id mismatch: "
                        f"expected {candidate_id}, "
                        f"got {item.candidate_id}"
                    )

                if item.event_type not in (
                    SUPPORTED_EVENT_TYPES | {"NON_TARGET"}
                ):
                    raise ValueError(
                        f"Unexpected event type: {item.event_type}"
                    )

                if item.event_type not in llm_event_types:
                    llm_event_types.append(item.event_type)

            target_types = [
                event_type
                for event_type in llm_event_types
                if event_type != "NON_TARGET"
            ]

            final_event_types = (
                target_types
                if target_types
                else ["NON_TARGET"]
            )

        elif NODE2_METHOD == "hybrid":

            result, elapsed, repairs = invoke_validated_json(
                get_llm(),
                build_node2_scoring_prompt([event]),
                ScoringOutput,
                f"Node 2-1 {candidate_id}",
            )

            total_elapsed += elapsed
            total_repairs += repairs

            if len(result.events) != 1:
                raise ValueError(
                    "Node 2-1 expected one scoring result for "
                    f"{candidate_id}, got {len(result.events)}"
                )

            scored_event = result.events[0]

            if scored_event.candidate_id != candidate_id:
                raise ValueError(
                    "Node 2 candidate_id mismatch: "
                    f"expected {candidate_id}, "
                    f"got {scored_event.candidate_id}"
                )

            llm_scores = scored_event.scores.model_dump()

            llm_event_types = [
                event_type
                for event_type in TARGET_EVENT_TYPES
                if llm_scores[event_type] >= 0.5
            ]

            if not llm_event_types:
                llm_event_types = ["NON_TARGET"]

        # Node 2-2: SBERT similarity scoring

        embedding_scores = embedding_event_scores(
            event["evidence"]
        )

        (
            embedding_event_type,
            embedding_confidence,
            embedding_margin,
        ) = best_event_type(embedding_scores)

        relative_scores = similarity_softmax(
            embedding_scores
        )

        if NODE2_METHOD == "similarity":

            if embedding_confidence < SIMILARITY_MIN_COSINE:
                final_event_types = ["NON_TARGET"]
            else:
                final_event_types = select_multilabel_types(
                    relative_scores
                )

        
        elif NODE2_METHOD == "hybrid":

            fusion_scores = calculate_fusion_scores(
                llm_scores,
                relative_scores,
            )

            final_event_types = select_multilabel_types(
                fusion_scores
            )


        # Keep independent classification results

        classification_results.append({
            "candidate_id": candidate_id,
            "method": NODE2_METHOD,
            "llm_event_types": llm_event_types,
            "llm_scores": llm_scores,
            "embedding_event_type": embedding_event_type,
            "embedding_confidence": round(
                embedding_confidence, 4
            ),
            "embedding_margin": round(
                embedding_margin, 4
            ),
            "embedding_scores": embedding_scores,
            "relative_scores": relative_scores,
            "fusion_scores": fusion_scores,
            "final_event_types": final_event_types,
        })

        # Expand labels into separate candidates for Node 3

        for event_type in final_event_types:

            record = {
                **event,
                "event_type": event_type,
                "llm_event_types": llm_event_types,
                "llm_scores": llm_scores,
                "final_event_types": final_event_types,
                "embedding_event_type": embedding_event_type,
                "embedding_confidence": round(
                    embedding_confidence, 4
                ),
                "embedding_margin": round(
                    embedding_margin, 4
                ),
                "embedding_scores": embedding_scores,
                "relative_scores": relative_scores,
                "fusion_scores": fusion_scores,
                "classification_method": NODE2_METHOD,
            }

            if event_type == "NON_TARGET":
                non_targets.append(record)
            else:
                candidates.append(record)

    node_output = {
        "method": NODE2_METHOD,
        "results": classification_results,
        "target_count": len(candidates),
        "non_target_count": len(non_targets),
        "time_sec": round(total_elapsed, 2),
        "repairs": total_repairs,
    }

    print_node_io(
        "Node 2 | Multi-label classification",
        node_input,
        node_output,
    )

    return {
        "candidates": candidates,
        "non_target_candidates": non_targets,
    }


# NODE 3

def node3_core_entity(state: State):
    """
    Extract source-grounded core S-R-O events
    for each classified candidate, including NON_TARGET.
    """

    target_candidates = state.get(
        "candidates",
        [],
    )

    non_target_candidates = state.get(
        "non_target_candidates",
        [],
    )

    candidates = (
        target_candidates
        + non_target_candidates
    )

    node_input = {
        "target_candidates": target_candidates,
        "non_target_candidates": non_target_candidates,
    }

    if not candidates:
        print_node_io(
            "Node 3 | Extract core triple",
            node_input,
            {"events": []},
        )

        return {
            "core_events": [],
        }

    events = []

    total_elapsed = 0.0
    total_repairs = 0

    for candidate in candidates:

        result, elapsed, repairs = invoke_validated_json(
            get_llm(),
            build_node3_prompt(
                state["company"],
                [candidate],
            ),
            CoreOutput,
            f"Node 3 {candidate['candidate_id']}",
        )

        total_elapsed += elapsed
        total_repairs += repairs

        if not result.events:
            continue

        for item in result.events:

            if item.candidate_id != candidate["candidate_id"]:
                raise ValueError(
                    "Node 3 candidate_id mismatch: "
                    f"expected {candidate['candidate_id']}, "
                    f"got {item.candidate_id}"
                )

            subject = normalize_subject(
                item.subject,
                state["company"],
            )

            subject_type = item.subject_type
            object_type = item.object_type

            if subject == state["company"]:
                subject_type = "ORG"

            object_value = item.object.strip()

            relation_surface = (
                item.relation_surface.strip()
            )

            if not relation_surface or not source_contains(
                candidate["evidence"],
                relation_surface,
            ):
                print(
                    "[Node 3 warning] Skipping ungrounded relation: "
                    f"{relation_surface!r} "
                    f"for {candidate['candidate_id']} "
                    f"({candidate['event_type']})"
                )
                continue

            relation = relation_surface

            events.append({
                **candidate,
                "subject": subject,
                "subject_type": subject_type,
                "relation_surface": relation_surface,
                "relation": relation,
                "object": object_value,
                "object_type": object_type,
            })

    node_output = {
        "events": events,
        "time_sec": round(total_elapsed, 2),
        "repairs": total_repairs,
    }

    print_node_io(
        "Node 3 | Extract source-grounded S-R-O",
        node_input,
        node_output,
    )

    return {
        "core_events": events,
    }

# NODE 4


def node4_split_objects(state: State):
    events = state.get(
        "core_events",
        [],
    )

    node_input = {
        "events": events,
    }

    atomic_events = []

    for event in events:
        if looks_coordinated(event["object"]):
            result, _, _ = invoke_validated_json(
                get_llm(),
                build_node4_prompt(event),
                SplitOutput,
                f"Node 4 {event['candidate_id']}",
            )

            objects = [
                item.model_dump()
                for item in result.objects
            ]

        else:
            objects = [{
                "object": event["object"],
                "object_type": event["object_type"],
            }]

        if not objects:
            raise ValueError(
                "Node 4 returned no object for "
                f"{event['candidate_id']}"
            )

        valid_objects = []

        for item in objects:
            object_value = item["object"].strip()

            if not object_value:
                continue

            if not source_contains(
                event["evidence"],
                object_value,
            ):
                continue

            valid_objects.append({
                "object": object_value,
                "object_type": item["object_type"],
            })

        if not valid_objects:
            valid_objects = [{
                "object": event["object"],
                "object_type": event["object_type"],
            }]

        for index, item in enumerate(
            valid_objects,
            start=1,
        ):
            atomic_events.append({
                **event,
                "atomic_id": (
                    f"{event['candidate_id']}"
                    f"_A{index:02d}"
                ),
                "broad_object": event["object"],
                "object": item["object"],
                "object_type": item["object_type"],
            })

    print_node_io(
        "Node 4 | Split independent noun entities",
        node_input,
        {"events": atomic_events},
    )

    return {
        "atomic_events": atomic_events,
    }


# NODE 5

def node5_roles(state: State):
    events = state.get(
        "atomic_events",
        [],
    )

    node_input = {
        "events": events,
    }

    enriched_events = []

    for event in events:

        # Target events use type-specific roles.
        # NON_TARGET keeps only generic roles.
        if event["event_type"] == "NON_TARGET":
            expected_roles = (
                "time",
                "location",
            )
        else:
            expected_roles = (
                EVENT_SPECS[
                    event["event_type"]
                ]["roles"]
            )

        result, _, _ = invoke_validated_json(
            get_llm(),
            build_node5_prompt(
                event,
                expected_roles=expected_roles,
            ),
            RoleOutput,
            f"Node 5 {event['atomic_id']}",
        )

        unexpected = sorted(
            set(result.roles)
            - set(expected_roles)
        )

        if unexpected:
            raise ValueError(
                "Node 5 unexpected roles for "
                f"{event['atomic_id']}: "
                f"{unexpected}"
            )

        roles = {}

        for role in expected_roles:

            value = str(
                result.roles.get(
                    role,
                    "NA",
                )
            ).strip()

            if not value:
                value = "NA"

            # Role values must be grounded in source evidence.
            if (
                value != "NA"
                and not source_contains(
                    event["evidence"],
                    value,
                )
            ):
                value = "NA"

            # Avoid duplicating S / R / O values as roles.
            if value != "NA":

                normalized_value = (
                    value.lower().strip()
                )

                normalized_subject = (
                    event["subject"]
                    .lower()
                    .strip()
                )

                normalized_object = (
                    event["object"]
                    .lower()
                    .strip()
                )

                normalized_relation_surface = (
                    event.get(
                        "relation_surface",
                        event["relation"],
                    )
                    .lower()
                    .strip()
                )

                if normalized_value in {
                    normalized_subject,
                    normalized_object,
                    normalized_relation_surface,
                }:
                    value = "NA"

            if (
                event["event_type"] != "NON_TARGET"
                and role == "location"
                and value != "NA"
            ):
                facility_value = str(
                    result.roles.get(
                        "facility",
                        "NA",
                    )
                ).strip()

                if (
                    facility_value != "NA"
                    and value.lower()
                    in facility_value.lower()
                ):
                    value = "NA"

            # Amount should contain a numeric value.
            if (
                role == "amount"
                and value != "NA"
            ):
                if not any(
                    char.isdigit()
                    for char in value
                ):
                    value = "NA"

            roles[role] = value

        enriched_events.append({
            **event,
            "roles": roles,
        })

    print_node_io(
        "Node 5 | Extract semantic roles",
        node_input,
        {"events": enriched_events},
    )

    return {
        "enriched_events": enriched_events,
    }


# NODE 6

def node6_finalize(state: State):
    events = state.get(
        "enriched_events",
        [],
    )

    node_input = {
        "events": events,
    }

    final_events = []

    for event in events:
        final_event = {
            "event_type": event["event_type"],
            "subject": event["subject"],
            "subject_type": event["subject_type"],
            "relation": event["relation"],
            "object": event["object"],
            "object_type": event["object_type"],
        }

        for role, value in event["roles"].items():
            if value != "NA":
                final_event[role] = value

        final_events.append(final_event)

    prediction = {
        "events": final_events,
    }

    print_node_io(
        "Node 6 | Finalize N-ary",
        node_input,
        prediction,
    )

    return {
        "prediction": prediction,
    }
