from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TypeVar

from opensearchpy import AsyncOpenSearch
from pydantic import BaseModel, Field
from tinydb import TinyDB

from sifts.io.db.base import AnalysisDB
from sifts.llm.router import RouterStrict

T = TypeVar("T")


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VulnerabilityStatus(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


class VulnerabilityAssessment(BaseModel):
    is_vulnerable: bool = Field(
        description="Final determination of vulnerability status ",
    )
    vulnerability_type: str = Field(
        description="Specific vulnerability category (e.g., 'SQL Injection', 'XSS', 'CSRF') or "
        "null if no vulnerability detected",
    )
    confidence: ConfidenceLevel = Field(
        description="Confidence level based on code coverage completeness and clarity of "
        "vulnerability patterns",
    )
    explanation: str = Field(
        description="If the code is safe it generates a very short description."
        "But if the code is vulnerable, it generates a detailed explanation, including"
        "vulnerability mechanics, affected code paths,"
        "potential exploits, and supporting evidence from analyzed functions. ",
    )
    analyzed_functions: list[str] = Field(
        description="Comprehensive list of all function names examined during this assessment to "
        "document analysis coverage",
    )
    vulnerability_chain: list[str] = Field(
        description="Ordered sequence of functions that form the complete vulnerability path from"
        " entry point to exploitation point",
    )
    vulnerable_function: str = Field(
        description="Name of the specific function where the vulnerability was identified",
    )

    vulnerable_line: int = Field(description="Line number of the vulnerable function")


class KindTypeScript(str, Enum):
    """Tags used by ctags to identify different code elements in TypeScript."""

    ALIAS = "alias"  # Alias in TypeScript (type aliases, import aliases)
    CLASS = "class"  # Classes in TypeScript
    CONSTANT = "constant"  # Constants/readonly variables
    ENUM = "enum"  # Enumerations
    ENUMERATOR = "enumerator"  # Individual values within an enumeration
    FUNCTION = "function"  # Functions (global or module-level)
    GENERATOR = "generator"  # Generator functions
    INTERFACE = "interface"  # Interfaces
    METHOD = "method"  # Methods (functions within classes)
    NAMESPACE = "namespace"  # Namespaces and modules
    PROPERTY = "property"  # Properties (class or interface members)
    VARIABLE = "variable"  # Variables (let, var, etc.)

    # The following types are disabled in the configuration but included for completeness
    LOCAL = "local"  # Local variables (disabled)
    PARAMETER = "parameter"  # Function/method parameters (disabled)

    @classmethod
    def from_string(cls, value: str) -> "KindTypeScript":
        """Convert a string to enum value, case-insensitive."""
        try:
            return cls(value.lower())
        except ValueError:
            # Default to FUNCTION if unknown
            return cls.FUNCTION

    @classmethod
    def enabled_kinds(cls) -> set[str]:
        """Return the set of enabled kinds from configuration."""
        return {
            cls.ALIAS.value,
            cls.CLASS.value,
            cls.CONSTANT.value,
            cls.ENUM.value,
            cls.ENUMERATOR.value,
            cls.FUNCTION.value,
            cls.GENERATOR.value,
            cls.INTERFACE.value,
            cls.METHOD.value,
            cls.NAMESPACE.value,
            cls.PROPERTY.value,
            cls.VARIABLE.value,
        }

    @classmethod
    def disabled_kinds(cls) -> set[str]:
        """Return the set of disabled kinds from configuration."""
        return {cls.LOCAL.value, cls.PARAMETER.value}


@dataclass
class TreeExecutionContext:
    working_dir: Path
    tiny_db: TinyDB
    db_client: AnalysisDB
    analysis_dir: Path
    open_client: AsyncOpenSearch
    router: RouterStrict
