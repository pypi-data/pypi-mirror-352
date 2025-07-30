import math
from collections.abc import Iterable
from contextlib import suppress
from typing import Any

from sifts.analysis.criteria_data import DEFINES_VULNERABILITIES
from sifts.analysis.types import VulnerabilityAssessment
from sifts.common_types.snippets import SnippetHit
from sifts.io.db.data_loaders import KNN_DATA
from sifts.llm.router import RouterStrict

SIMILARITY_THRESHOLD = 0.7


def compare_vectors(vector1: list[float], vector2: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(vector1, vector2, strict=False))

    norm1 = math.sqrt(sum(x * x for x in vector1))
    norm2 = math.sqrt(sum(x * x for x in vector2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(dot_product / (norm1 * norm2))


def compare_two_keys(key1: str, key2: str) -> float:
    with suppress(KeyError):
        vector1 = KNN_DATA[key1][0]
        vector2 = KNN_DATA[key2][0]
        return compare_vectors(vector1, vector2)

    with suppress(KeyError):
        vector1 = KNN_DATA[DEFINES_VULNERABILITIES[key1]["en"]["title"]][0]
        vector2 = KNN_DATA[DEFINES_VULNERABILITIES[key2]["en"]["title"]][0]
        return compare_vectors(vector1, vector2)

    return 0.0


def generate_vuln_context_markdown(vuln_criteria: dict[str, Any]) -> str:
    return f"{vuln_criteria['en']['title']}\n"


def get_vuln_criteria(finding_code: str) -> dict[str, Any]:
    return DEFINES_VULNERABILITIES[finding_code]


def filter_candidate_codes(candidates: list[SnippetHit]) -> list[SnippetHit]:
    candidate_codes: list[SnippetHit] = []
    processed_indices = set()

    for i, candidate in enumerate(candidates):
        if i in processed_indices:
            continue

        code = candidate["_source"]["metadata"]["criteria_code"]
        candidate_codes.append(candidate)

        # Mark similar candidates as processed
        for j, other_candidate in enumerate(candidates):
            if i != j and j not in processed_indices:
                other_code = other_candidate["_source"]["metadata"]["criteria_code"]
                if code == other_code or compare_two_keys(code, other_code) >= 0.8:  # noqa: PLR2004
                    processed_indices.add(j)

    return candidate_codes


def generate_candidate_text(defines_codes: Iterable[str]) -> str:
    if not defines_codes:
        return ""

    # Filter similar candidates
    filtered_candidates: list[str] = []
    for defines_code in defines_codes:
        # Check if this candidate is similar to any already filtered candidate
        is_similar = False
        for filtered in filtered_candidates:
            try:
                similarity = compare_two_keys(
                    DEFINES_VULNERABILITIES[defines_code]["en"]["title"],
                    DEFINES_VULNERABILITIES[filtered]["en"]["title"],
                )
            except KeyError:
                continue
            if similarity >= SIMILARITY_THRESHOLD:
                is_similar = True
                break

        # If not similar to any existing candidate, add it
        if not is_similar:
            filtered_candidates.append(defines_code)

    return "\n".join(
        [
            generate_vuln_context_markdown(get_vuln_criteria(x))
            for x in filtered_candidates[:5]
            if x in DEFINES_VULNERABILITIES
        ],
    )


async def find_most_similar_finding(
    router: RouterStrict,
    result: VulnerabilityAssessment,
) -> str:
    response = await router.aembedding(
        "voyage-3",
        [f"{result.vulnerability_type + result.explanation}"],
        caching=True,
    )
    embedding = response["data"][0]["embedding"]
    top = [
        (finding_title, compare_vectors(KNN_DATA[finding_title][0], embedding))
        for finding_title in KNN_DATA
        if finding_title in KNN_DATA
    ]

    sorted_top = sorted(top, key=lambda x: x[1], reverse=True)
    finding_title = sorted_top[0][0] if sorted_top else ""
    return next(
        x
        for x in DEFINES_VULNERABILITIES
        if DEFINES_VULNERABILITIES[x]["en"]["title"] == finding_title
    )
