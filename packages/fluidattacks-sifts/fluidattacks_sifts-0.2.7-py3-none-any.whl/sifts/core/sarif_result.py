import json
from typing import Any, TypeAlias

import sarif_om
from sarif_om import SarifLog

from sifts.analysis.criteria_data import DEFINES_REQUIREMENTS, DEFINES_VULNERABILITIES
from sifts.common_types.snippets import ItemAnalysisResult
from sifts.config import SiftsConfig
from sifts.core.repository import get_repo_branch, get_repo_head_hash, get_repo_remote
from sifts.io.db.sqlite import SQLiteVulnDB

SarifReportComponent: TypeAlias = (
    SarifLog
    | list["SarifReportComponent"]
    | dict[str, "SarifReportComponent"]
    | tuple["SarifReportComponent"]
    | set["SarifReportComponent"]
    | str
    | int
)


def _get_rule(vuln_id: str) -> sarif_om.ReportingDescriptor:
    content = DEFINES_VULNERABILITIES[vuln_id]

    return sarif_om.ReportingDescriptor(
        id=vuln_id,
        name=content["en"]["title"],
        full_description=sarif_om.MultiformatMessageString(
            text=content["en"]["description"],
        ),
        help_uri=(
            "https://help.fluidattacks.com/portal/en/kb/articles/"
            f"criteria-vulnerabilities-{vuln_id}"
        ),
        help=sarif_om.MultiformatMessageString(
            text=content["en"]["recommendation"],
        ),
        properties={"auto_approve": True},
    )


def _rule_is_present(base: sarif_om.SarifLog, rule_id: str) -> bool:
    return any(rule.id == rule_id for rule in base.runs[0].tool.driver.rules)


def _taxa_is_present(base: sarif_om.SarifLog, taxa_id: str) -> bool:
    return any(rule.id == taxa_id for rule in base.runs[0].taxonomies[0].taxa)


def _get_context_region(
    vulnerability: ItemAnalysisResult,
    db_client: SQLiteVulnDB,
) -> sarif_om.Region:
    snippet = db_client.get_snippet(
        root_id=vulnerability["root_id"],
        path=vulnerability["where"],
        hash_=vulnerability["snippet_hash"],
    )
    if snippet:
        region = sarif_om.Region(
            start_line=snippet.start_point[0],
            end_line=snippet.end_point[0],
            snippet=sarif_om.ArtifactContent(
                rendered={"text": snippet.snippet_content},
                text=snippet.snippet_content,
            ),
            start_column=snippet.start_point[1],
            end_column=snippet.end_point[1],
            source_language=snippet.language,
        )
    else:
        region = sarif_om.Region()

    return region


def _get_taxa(requirement_id: str) -> sarif_om.ReportingDescriptor:
    content = DEFINES_REQUIREMENTS[requirement_id]
    return sarif_om.ReportingDescriptor(
        id=requirement_id,
        name=content["en"]["title"],
        short_description=sarif_om.MultiformatMessageString(
            text=content["en"]["summary"],
        ),
        full_description=sarif_om.MultiformatMessageString(
            text=content["en"]["description"],
        ),
        help_uri=(
            "https://help.fluidattacks.com/portal/en/kb/articles/"
            f"criteria-requirements-{requirement_id}"
        ),
    )


def attrs_serializer(obj: SarifReportComponent) -> SarifReportComponent:
    return (
        {
            attribute.metadata["schema_property_name"]: attrs_serializer(
                obj.__dict__[attribute.name],
            )
            for attribute in obj.__attrs_attrs__
            if obj.__dict__[attribute.name] != attribute.default
        }
        if hasattr(obj, "__attrs_attrs__")
        else obj
    )


def simplify_sarif(sarif_obj: SarifLog) -> dict[str, Any]:
    result: dict[str, Any] = json.loads(json.dumps(sarif_obj, default=attrs_serializer))
    return result


def _get_base(config: SiftsConfig, vulns: list[ItemAnalysisResult]) -> SarifLog:
    db_client = SQLiteVulnDB(
        str(config.results_db_path),
    )
    base = SarifLog(
        version="2.1.0",
        schema_uri=("https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json"),
        runs=[
            sarif_om.Run(
                tool=sarif_om.Tool(
                    driver=sarif_om.ToolComponent(
                        name="skims",
                        rules=[
                            _get_rule(check) for check in config.analysis.include_vulnerabilities
                        ],
                        version="1.0.0",
                        semantic_version="1.0.0",
                    ),
                ),
                results=[],
                version_control_provenance=[
                    sarif_om.VersionControlDetails(
                        repository_uri=get_repo_remote(config.analysis.working_dir),
                        revision_id=get_repo_head_hash(
                            config.analysis.working_dir,
                        ),
                        branch=get_repo_branch(config.analysis.working_dir),
                    ),
                ],
                taxonomies=[
                    sarif_om.ToolComponent(
                        name="criteria",
                        version="1",
                        information_uri=(
                            "https://help.fluidattacks.com/portal/en/kb/"
                            "articles/criteria/requirements"
                        ),
                        organization="Fluidattacks",
                        short_description=sarif_om.MultiformatMessageString(
                            text="The fluidattacks security requirements",
                        ),
                        taxa=[],
                        is_comprehensive=False,
                    ),
                ],
                web_responses=[],
            ),
        ],
    )
    for vulnerability in vulns:
        rule_id = vulnerability["suggested_criteria_code"]
        if not rule_id:
            continue

        result = sarif_om.Result(
            rule_id=rule_id,
            level="note",
            message=sarif_om.MultiformatMessageString(
                text=vulnerability["reason"],
                properties={},
            ),
            locations=[
                sarif_om.Location(
                    physical_location=sarif_om.PhysicalLocation(
                        artifact_location=sarif_om.ArtifactLocation(
                            uri=vulnerability["where"],
                        ),
                        region=sarif_om.Region(
                            start_line=vulnerability["specific"],
                        ),
                        context_region=_get_context_region(vulnerability, db_client),
                    ),
                ),
            ],
            taxa=[],
        )
        # append rule if not is present
        if not _rule_is_present(base, rule_id):
            base.runs[0].tool.driver.rules.append(_get_rule(rule_id))

        for taxa_id in DEFINES_VULNERABILITIES[rule_id]["requirements"]:
            if not _taxa_is_present(base, taxa_id):
                base.runs[0].taxonomies[0].taxa.append(_get_taxa(taxa_id))

        result.taxa = [
            sarif_om.ReportingDescriptorReference(
                id=taxa_id,
                tool_component=sarif_om.ToolComponentReference(name="criteria"),
            )
            for taxa_id in DEFINES_VULNERABILITIES[rule_id]["requirements"]
        ]
    return base


def get_sarif(vulns: list[ItemAnalysisResult], config: SiftsConfig) -> dict[str, Any]:
    return simplify_sarif(_get_base(config, vulns))
