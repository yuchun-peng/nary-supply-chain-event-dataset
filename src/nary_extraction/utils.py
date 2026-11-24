import json
import re
import time
from pathlib import Path

from pydantic import ValidationError

from .prompts import build_repair_prompt


def load_json(path: Path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_json(
    path: Path,
    data,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def extract_json(
    raw: str,
):

    text = raw.strip()

    if text.startswith("```"):

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

    start = text.find("{")
    end = text.rfind("}")

    if (
        start == -1
        or end == -1
        or end < start
    ):
        raise ValueError(
            "No JSON object found."
        )

    return json.loads(
        text[start:end + 1]
    )


def invoke_validated_json(
    llm,
    prompt: str,
    model_class,
    node_name: str,
):

    start = time.perf_counter()

    response = llm.invoke(prompt)

    raw = response.content

    repairs = 0

    try:

        data = extract_json(raw)

        result = model_class.model_validate(
            data
        )

    except (
        json.JSONDecodeError,
        ValidationError,
        ValueError,
    ) as error:

        repairs += 1

        print(
            f"\n{node_name} | Validation failed"
        )

        print(
            f"Error: {error}"
        )

        print("Raw output")
        print(raw)

        repair_prompt = build_repair_prompt(
            raw=raw,
            error=str(error),
            schema=model_class.model_json_schema(),
        )

        repaired_response = llm.invoke(
            repair_prompt
        )

        repaired_raw = (
            repaired_response.content
        )

        print("Repaired output")
        print(repaired_raw)

        repaired_data = extract_json(
            repaired_raw
        )

        result = model_class.model_validate(
            repaired_data
        )

    elapsed = (
        time.perf_counter()
        - start
    )

    return (
        result,
        elapsed,
        repairs,
    )


def normalize_text(
    text: str,
) -> str:

    return " ".join(
        str(text)
        .lower()
        .split()
    )


def source_contains(
    source: str,
    value: str,
) -> bool:

    if not value:
        return False

    return (
        normalize_text(value)
        in normalize_text(source)
    )


def trigger_matches_source(
    source: str,
    trigger: str,
) -> bool:

    if not trigger:
        return False

    source_norm = normalize_text(
        source
    )

    trigger_norm = normalize_text(
        trigger
    )

    if trigger_norm in source_norm:
        return True

    trigger_words = (
        trigger_norm.split()
    )

    if not trigger_words:
        return False

    return all(
        word in source_norm
        for word in trigger_words
    )


def looks_coordinated(
    text: str,
) -> bool:

    lowered = text.lower()

    return (
        "," in text
        or " and " in lowered
        or " or " in lowered
        or ";" in text
    )


def shorten(
    value,
    limit: int = 180,
) -> str:

    text = str(value).replace(
        "\n",
        " ",
    )

    if len(text) <= limit:
        return text

    return (
        text[:limit]
        + "..."
    )


def print_node_io(
    name: str,
    node_input,
    node_output,
) -> None:

    print(
        f"\n{name}"
    )

    print("Input")

    print(
        json.dumps(
            node_input,
            ensure_ascii=False,
            indent=2,
        )
    )

    print("Output")

    print(
        json.dumps(
            node_output,
            ensure_ascii=False,
            indent=2,
        )
    )
