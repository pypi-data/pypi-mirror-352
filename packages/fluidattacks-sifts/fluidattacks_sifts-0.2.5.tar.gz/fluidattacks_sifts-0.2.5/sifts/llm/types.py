from enum import Enum
from typing import Literal, TypedDict

from sifts.llm.prompts import Prompts


class ModelParameters(TypedDict):
    top_findings: list[str]
    finding_candidates_exclusion: list[str]
    exclusion_candidates_finding_title: list[str]
    prompts: Prompts


class AnalyzeVulnerabilityParams(TypedDict):
    isVulnerable: Literal["true", "false", "unknown"]
    vulnerabilityType: str
    confidence: Literal["high", "medium", "low"]
    explanation: str
    vulnerableFunction: str


class FinishAnalysisParams(TypedDict):
    isVulnerable: Literal["true", "false", "unknown"]
    vulnerabilityType: str
    confidence: Literal["high", "medium", "low"]
    explanation: str
    analyzedFunctions: list[str]
    vulnerabilityChain: list[str]
    vulnerableFunction: str
    method_id: str
    additionalProperties: bool


class FunctionRequestItem(TypedDict):
    functionName: str  # Plain function name without class prefixes
    calledFrom: str  # Plain function name of the calling function
    reason: str  # Security concern reason


class RequestChildFunctionParams(TypedDict):
    functionRequests: list[FunctionRequestItem]


class RequestParentFunctionParams(TypedDict):
    currentFunction: str
    reason: str


class ToolFunction(str, Enum):
    REQUEST_CHILD_FUNCTION = "requestChildFunction"
    REQUEST_PARENT_FUNCTION = "requestParentFunction"
    FINISH_ANALYSIS = "finishAnalysis"
