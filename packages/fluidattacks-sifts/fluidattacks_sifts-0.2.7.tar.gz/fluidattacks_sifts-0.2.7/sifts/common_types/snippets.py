import logging
from typing import NamedTuple, TypedDict

import tiktoken
from more_itertools import mark_ends


class Metadata(TypedDict):
    finding_id: str
    criteria_code: str
    vulnerability_id: str
    organization_id: str
    finding_title: str
    where: str
    specific: int
    group: str
    snippet_offset: int
    vulnerable_function_code_hash: str


class Embeddings(TypedDict):
    vulnerable_function: list[float]
    abstract_propose: list[float]
    detailed_behavior: list[float]


class Source(TypedDict):
    metadata: Metadata
    vulnerable_function_code: str
    fixed_function_code: str | None
    vulnerability_knowledge: str | None
    vulnerable_line_content: str
    abstract_propose: str
    detailed_behavior: str
    embeddings: Embeddings


class SnippetHit(TypedDict):
    _index: str
    _id: str
    _score: float
    _source: Source
    ReRankingScore: float


class ItemAnalysisResult(TypedDict):
    pk: str
    sk: str
    candidate_index: int | None
    commit: str
    group_name: str
    inputTokens: int | None
    outputTokens: int | None
    ranking_score: float | None
    reason: str
    root_id: str
    snippet_hash: str
    specific: str | None
    suggested_criteria_code: str | None
    suggested_finding_title: str | None
    totalTokens: int | None
    vulnerability_id_candidate: str | None
    vulnerable: bool
    where: str
    line_start: int | None
    line_end: int | None
    column_start: int | None
    column_end: int | None
    cost: float | None
    trace_id: str | None


class Snippet(NamedTuple):
    pk: str
    sk: str
    commit: str
    end_point: list[int | None]
    group_name: str | None
    hash_type: str
    language: str
    root_id: str | None
    root_nickname: str | None
    snippet_content: str | None
    snippet_hash: str
    start_point: list[int | None]
    where: str
    name: str | None


class Vulnerable(NamedTuple):
    function_hash: str
    defines_code: str
    defines_title: str
    description: str
    where: str
    specific: int
    candidate_id: str
    root_id: str | None = None
    cost: float | None = None
    candidate_index: int | None = None
    trace_id: str | None = None


class Safe(NamedTuple):
    function_hash: str
    description: str
    where: str
    root_id: str | None = None
    candidate_id: str | None = None
    cost: float | None = None
    candidate_index: int | None = None
    trace_id: str | None = None


LOGGER = logging.getLogger(__name__)


def extract_function_content(
    lines: list[str],
    line_number_start: int,
    line_number_end: int,
    column_number_start: int,
    column_number_end: int,
) -> str | None:
    function_content = []
    try:
        for is_first, is_last, line in mark_ends(lines[line_number_start - 1 : line_number_end]):
            if is_first:
                function_content.append(line[column_number_start - 1 :])
            elif is_last:
                function_content.append(line[:column_number_end])
            else:
                function_content.append(line)
    except IndexError:
        return None
    return "\n".join(function_content).replace("\t", "  ")


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    return len(encoding.encode(string))
