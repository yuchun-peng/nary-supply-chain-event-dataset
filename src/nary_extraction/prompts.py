import json

from .config import (
    TARGET_EVENT_TYPES,
    ENTITY_TYPES,
)

from .event_specs import EVENT_SPECS


def build_event_definitions() -> str:
    blocks = []

    for event_type in TARGET_EVENT_TYPES:
        spec = EVENT_SPECS[event_type]

        definition = spec.get(
            "definition",
            "",
        )

        boundary = spec.get(
            "boundary",
            "",
        )

        examples = spec.get(
            "examples",
            "",
        )

        blocks.append(
            f"""Event Type: {event_type}
Definition: {definition}
Boundary: {boundary}
Examples:
{examples}"""
        )

    return "\n\n".join(blocks)


# NODE 1

def build_node1_prompt(
    text: str,
) -> str:

    return f"""

Identify all text spans in this SEC 10-K text that may describe a business or operational event.

Rules:
- Scan the entire text and identify all plausible event evidence, including events expressed descriptively.
- Copy evidence verbatim from the source text. Do not rewrite, summarize, or truncate it.
- Preserve sufficient context for each event to be understood independently.
- Keep distinct events in separate spans when possible, without breaking their context.
- Do not invent information or use ellipses.


EXAMPLE INPUT:

A acquired Company B for $10 million. The acquisition is expected to generate
additional revenue next year. The company also manufactures components in Michigan.

EXAMPLE OUTPUT:

{{
  "events": [
    {{
      "evidence": "A acquired Company B for $10 million. The acquisition is expected to generate additional revenue next year."
    }},
    {{
      "evidence": "The company also manufactures components in Michigan."
    }}
  ]
}}

TEXT:

{text}

Return JSON only.
""".strip()



# NODE 2

def build_node2_prompt(
    events: list[dict],
) -> str:

    items = [
        {
            "candidate_id": item["candidate_id"],
            "evidence": item["evidence"],
        }
        for item in events
    ]

    return f"""
Classify all business or operational events expressed in each candidate into their applicable task labels.

EVENT TYPES

{build_event_definitions()}

Possible labels:
- Manufacturing
- Competition
- Supply
- Investment
- NON_TARGET

Rules:
- Classify based on the events expressed in the evidence and their definitions.
- Assign one label per distinct event, allowing multiple labels for the same candidate_id when different event types are present.
- Do not assign multiple labels to a single event merely because the definitions overlap.
- Do not classify based only on isolated keywords.
- Use NON_TARGET only when none of the four target event types applies.
- Do not infer events or create new event types.

INPUT EVENTS

{json.dumps(
    items,
    ensure_ascii=False,
    indent=2,
)}

Return JSON only:

{{
  "events": [
    {{
      "candidate_id": "C001",
      "event_type": "Manufacturing"
    }},
    {{
      "candidate_id": "C001",
      "event_type": "Supply"
    }}
  ]
}}
""".strip()



def build_node2_scoring_prompt(
    events: list[dict],
) -> str:
    items = [
        {
            "candidate_id": item["candidate_id"],
            "evidence": item["evidence"],
        }
        for item in events
    ]

    return f"""
Classify event candidates from SEC 10-K filings.

EVENT DEFINITIONS

{build_event_definitions()}

TASK

Assign an independent confidence score from 0 to 1
for each of the four target event types.

Manufacturing, Competition, Supply, Investment.

MULTI-LABEL RULES

- A candidate may express multiple distinct event types.
- Score all four categories independently.
- The scores do not need to sum to 1.
- Give high scores only to explicitly supported events.
- Do not assign high scores merely due to overlapping
  definitions or shared keywords.
- Do not invent events or use outside information.
- Score NON_TARGET highly only when none of the
  four target event types is supported.
- If any target event clearly applies,
  NON_TARGET should receive a low score.
- All five scores must be between 0 and 1.

INPUT

{json.dumps(items, ensure_ascii=False, indent=2)}

Return exactly one JSON object with this structure:

{{
  "events": [
    {{
      "candidate_id": "C001",
      "scores": {{
        "Manufacturing": 0.0,
        "Competition": 0.0,
        "Supply": 0.0,
        "Investment": 0.0,
        "NON_TARGET": 0.0
      }}
    }}
  ]
}}

Return JSON only.
""".strip()


# NODE 3

def build_node3_prompt(company: str, events: list[dict]) -> str:
    items = [
        {
            "candidate_id": e["candidate_id"],
            "event_type": e["event_type"],
            "evidence": e["evidence"],
        }
        for e in events
    ]

    return f"""
Extract Subject-Relation-Object (S-R-O) triples
from the evidence for each assigned event type.

Filing company: {company}
Allowed entity types: {list(ENTITY_TYPES)}

Rules:
- Do not assume the filing company is the subject.
  Use the actual actor; resolve company pronouns when clear.
- Do not use nouns, entity names, or full clauses as relations.
  relation_surface must be an exact verb phrase from the source.
- Do not swap subject and object or extract incomplete objects.
- Do not invent facts or mix different events.
  If no valid triple exists, return an empty list.
  Keep coordinated objects together for Node 4.

Input:
{json.dumps(items, ensure_ascii=False)}

Return JSON only:
{{
  "events": [
    {{
      "candidate_id": "C001",
      "subject": "...",
      "subject_type": "ORG",
      "relation_surface": "...",
      "relation": "...",
      "object": "...",
      "object_type": "PRODUCT"
    }}
  ]
}}
""".strip()


# NODE 4

def build_node4_prompt(
    event: dict,
) -> str:

    return f"""
Split the object only if it contains multiple independent
noun entities or noun phrases.

INPUT

subject:
{event["subject"]}

relation:
{event["relation"]}

object:
{event["object"]}

object_type:
{event["object_type"]}

evidence:
{event["evidence"]}

RULES

- Split only when each part can independently form:
  subject + same relation + object.
- Do NOT split verbs, predicates, clauses, purposes, or results.
- "and", "or", or commas do NOT automatically require splitting.
- Preserve source wording.
- If there is only one valid noun object, return it unchanged.
- Keep the correct entity type for each returned object.
- Return ONE JSON object only.
- Do NOT include explanations, headings, markdown, notes,
  labels, or any text outside the JSON.

EXAMPLE 1

subject:
Company A

relation:
supply

object:
batteries and electronic components

Output:
{{
  "objects": [
    {{
      "object": "batteries",
      "object_type": "PRODUCT"
    }},
    {{
      "object": "electronic components",
      "object_type": "PRODUCT"
    }}
  ]
}}

EXAMPLE 2

object:
"standalone value and contribute to the success of our businesses"

Do NOT split.
"contribute to..." is another predicate, not another noun object.

Return EXACTLY one valid JSON object in this structure:

{{
  "objects": [
    {{
      "object": "...",
      "object_type": "..."
    }}
  ]
}}
""".strip()


# NODE 5

def build_node5_prompt(
    event: dict,
    expected_roles: tuple[str, ...],
) -> str:

    role_template = {
        role: "NA"
        for role in expected_roles
    }

    item = {
        "event_type": event["event_type"],
        "subject": event["subject"],
        "relation_surface": event.get(
            "relation_surface",
            event["relation"],
        ),
        "relation": event["relation"],
        "object": event["object"],
        "evidence": event["evidence"],
    }

    return f"""
Extract semantic roles for this event.

EVENT

{json.dumps(
    item,
    ensure_ascii=False,
    indent=2,
)}

ALLOWED ROLES

{json.dumps(
    expected_roles,
    ensure_ascii=False,
)}

RULES

- Extract only information that semantically modifies or describes the event.
- Use the complete evidence span.
- Do not use information that belongs to a different event.
- Do not copy the subject, object, relation_surface, or relation into a role unless the role adds distinct information.
- Location must be a geographic place, not a facility name.
- If a role is not explicitly supported by the evidence, return "NA".
- Use exact spans from the evidence.
- Return JSON only.

Return EXACTLY one valid JSON object in this structure:

{{
  "roles": {json.dumps(
      role_template,
      ensure_ascii=False,
      indent=2,
  )}
}}
""".strip()


# Repair

def build_repair_prompt(
    raw: str,
    error: str,
    schema: dict,
) -> str:

    return f"""
Convert the previous response into valid JSON matching the schema.

RULES

- Return ONE JSON object only.
- Return JSON only.
- Do not explain.
- Do not write code.
- Do not use markdown.
- Do not add headings, notes, labels, or commentary.
- Do not add new information.
- Preserve the intended extracted values.
- Match the schema exactly.

ERROR

{error}

SCHEMA

{json.dumps(
    schema,
    ensure_ascii=False,
    indent=2,
)}

PREVIOUS OUTPUT

{raw}
""".strip()
