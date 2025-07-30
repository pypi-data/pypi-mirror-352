import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

EXCLUDE_DIRS: list[str] = []


class LinesConfig(BaseModel):
    file: Path
    lines: list[int]

    @field_validator("file", mode="before")
    @classmethod
    def convert_file_to_path(cls, value: str | Path) -> Path:
        value = str(value).strip()
        if isinstance(value, str) and value.startswith("/") and not Path(value).exists():
            value = value.lstrip("/")
        """Convert file to a Path object if it's a string."""
        return Path(value)


class OutputConfig(BaseModel):
    format: str = "json"
    path: Path = Field(default=Path("output.json"))

    @field_validator("path", mode="before")
    @classmethod
    def convert_path_to_path_object(cls, value: str | Path) -> Path:
        """Convert path to a Path object if it's a string."""
        return Path(value)

    @field_validator("path")
    @classmethod
    def validate_output_path(cls, value: Path) -> Path:
        """Validate and prepare the output path directory."""
        # For output paths, we attempt to create the directory
        if not value.parent.exists():
            try:
                value.parent.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                msg = f"Cannot create output directory: {value.parent}: {e!s}"
                raise ValueError(msg) from e

        # Check if we can write to the directory
        if not os.access(value.parent, os.W_OK):
            msg = f"No write permission for output directory: {value.parent}"
            raise ValueError(msg)

        return value


class RuntimeConfig(BaseModel):
    parallel: bool = False
    threads: int = 1


class ExecutionContext(BaseModel):
    group_name: str | None = Field(default=None, description="Group name")
    root_id: str | None = Field(default=None, description="Root ID")
    root_nickname: str | None = Field(default=None, description="Root nickname")


class AnalysisConfig(BaseModel):
    include_files: list[str] = Field(default_factory=list)
    exclude_files: list[str] = Field(default_factory=list)
    lines_to_check: list[LinesConfig] = Field(default_factory=list)
    include_vulnerabilities: list[str] = Field(default_factory=list)
    exclude_vulnerabilities: list[str] = Field(default_factory=list)
    working_dir: Path = Field(
        default=Path("."),  # noqa: PTH201
        description="Directory to work in",
    )
    split_subdirectories: bool = Field(
        default=True,
        description=(
            "The project may contain multiple subjects, determining whether it"
            " should be analyzed in a different process."
        ),
    )
    use_default_exclude_files: bool = Field(
        default=True,
        description="Use default exclude files",
    )
    use_default_vulnerabilities_exclude: bool = Field(
        default=True,
        description="Use default vulnerabilities exclude",
    )
    strict_mode: bool = Field(
        default=True,
        description="Use strict mode",
    )
    enable_navigation: bool = Field(
        default=False,
        description="Enable navigation",
    )

    @field_validator("working_dir", mode="before")
    @classmethod
    def convert_working_dir_to_path(cls, value: str | Path) -> Path:
        """Convert working_dir to a Path object if it's a string."""
        return Path(value)

    @field_validator("working_dir")
    @classmethod
    def validate_working_dir(cls, value: Path) -> Path:
        """Validate that the working directory exists."""
        if not value.exists():
            msg = f"Working directory does not exist: {value}"
            raise ValueError(msg)
        if not value.is_dir():
            msg = f"Working directory is not a directory: {value}"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def merge_lines_for_same_files(self) -> "AnalysisConfig":
        """Merge lines_to_check entries that reference the same file path."""
        if not self.lines_to_check:
            return self

        # Dictionary to store merged lines by file path
        merged_lines_by_path: dict[Path, list[int]] = {}

        # Collect all lines by file path
        for line_config in self.lines_to_check:
            # Normalize the path for consistent comparison
            file_path = line_config.file
            if file_path not in merged_lines_by_path:
                merged_lines_by_path[file_path] = []

            # Add lines to the merged list, avoiding duplicates
            for line in line_config.lines:
                if line not in merged_lines_by_path[file_path]:
                    merged_lines_by_path[file_path].append(line)

        # Sort line numbers for deterministic output
        for path, lines in merged_lines_by_path.items():
            merged_lines_by_path[path] = sorted(lines)

        # Create new merged lines_to_check list
        merged_configs: list[LinesConfig] = []
        for file_path, lines in merged_lines_by_path.items():
            merged_configs.append(LinesConfig(file=file_path, lines=lines))

        # Replace the original list with the merged list
        self.lines_to_check = merged_configs
        return self

    @model_validator(mode="after")
    def validate_file_paths(self) -> "AnalysisConfig":
        """Validate that files referenced for analysis exist."""
        # Validate all paths in lines_to_check
        for line_config in self.lines_to_check:
            file_path = line_config.file
            # Check if file exists as absolute path
            if not file_path.exists():
                # Check if file exists relative to working_dir
                working_dir_path = Path(self.working_dir, file_path)
                if not working_dir_path.exists():
                    msg = f"File specified in lines_to_check does not exist: {file_path}"
                    raise ValueError(
                        msg,
                    )

        # Validate non-glob patterns in include_files
        for include_pattern in self.include_files:
            # Only validate exact file references (not glob patterns)
            if (
                "*" not in include_pattern
                and "?" not in include_pattern
                and (file_path := Path(include_pattern))
            ) and not file_path.exists():
                # Check if file exists relative to working_dir
                working_dir_path = self.working_dir / file_path
                if not working_dir_path.exists():
                    msg = f"File specified in include_files does not exist: {file_path}"
                    raise ValueError(msg)

        return self


class SiftsConfig(BaseModel):
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    context: ExecutionContext = Field(default_factory=ExecutionContext)
    results_db_path: Path = Field(default=Path("results/my_database9.db"))

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "SiftsConfig":
        """Load configuration from a YAML file."""
        path = Path(config_path) if isinstance(config_path, str) else config_path
        if not path.exists():
            msg = f"Config file not found: {path}"
            raise FileNotFoundError(msg)

        with path.open() as file:
            config_data = yaml.safe_load(file)

        return cls.model_validate(config_data)
