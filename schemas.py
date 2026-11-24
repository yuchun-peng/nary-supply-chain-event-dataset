from typing import Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field


# Shared types

EntityType = Literal[
    "ORG",
    "COMP",
    "PERSON",
    "PRODUCT",
    "TECHNOLOGY",
    "MATERIAL",
    "FACILITY",
    "LOCATION",
    "SEGMENT",
    "REGULATION",
    "AGREEMENT",
    "IMPACT_EVENT",
    "METRIC_VALUE",
    "TIME",
    "OTHER",
]


EventType = Literal[
    "Competition",
    "Manufacturing",
    "Supply",
    "Investment",
    "NON_TARGET",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )


# NODE 1

class DetectedEvent(StrictModel):
    """
    Node 1 returns an event-centered evidence span.
    """
    evidence: str = Field(
        min_length=1
    )


class DetectionOutput(StrictModel):
    events: list[DetectedEvent]


# NODE 2

class ClassifiedEvent(StrictModel):
    candidate_id: str = Field(
        min_length=1
    )

    event_type: EventType


class ClassificationOutput(StrictModel):
    events: list[ClassifiedEvent]



# NODE 2 — Confidence Scoring for Fusion

class EventTypeScores(StrictModel):
    Manufacturing: float = Field(ge=0.0, le=1.0)
    Competition: float = Field(ge=0.0, le=1.0)
    Supply: float = Field(ge=0.0, le=1.0)
    Investment: float = Field(ge=0.0, le=1.0)
    NON_TARGET: float = Field(ge=0.0, le=1.0)


class ScoredEvent(StrictModel):
    candidate_id: str = Field(min_length=1)
    scores: EventTypeScores


class ScoringOutput(StrictModel):
    events: list[ScoredEvent]


# NODE 3

class CoreEvent(StrictModel):
    candidate_id: str = Field(
        min_length=1
    )

    subject: str = Field(
        min_length=1
    )

    subject_type: EntityType

    # Exact verb / verb phrase copied from evidence.
    relation_surface: str = Field(
        min_length=1
    )

    # Normalized/base-form relation.
    relation: str = Field(
        min_length=1
    )

    object: str = Field(
        min_length=1
    )

    object_type: EntityType


class CoreOutput(StrictModel):
    events: list[CoreEvent]


# NODE 4

class AtomicObject(StrictModel):
    object: str = Field(
        min_length=1
    )

    object_type: EntityType


class SplitOutput(StrictModel):
    objects: list[AtomicObject]


# NODE 5

class RoleOutput(StrictModel):
    roles: dict[str, str]


# GRAPH STATE

class State(TypedDict, total=False):
    # Input / metadata
    chunk_id: str
    company: str
    text: str
    ground_truth: list[dict]

    # Node 1
    detected_events: list[dict]

    # Node 2
    candidates: list[dict]
    non_target_candidates: list[dict]

    # Node 3
    core_events: list[dict]

    # Node 4
    atomic_events: list[dict]

    # Node 5
    enriched_events: list[dict]

    # Node 6
    prediction: dict
