import json

import aioboto3

from sifts.common_types.snippets import ItemAnalysisResult, Safe, Vulnerable
from sifts.io.db.base import AnalysisDB
from sifts.io.db.dynamodb import DynamoVulnDB


def convert_analysis_result(
    response: Vulnerable | Safe,
    group_name: str,
) -> ItemAnalysisResult:
    vulnerability: ItemAnalysisResult = {
        "pk": f"ROOT#{response.root_id}#PATH#{response.where}",
        "sk": f"SNIPPET#{response.function_hash}#CANDIDATE#{response.candidate_id}",
        "group_name": group_name,
        "commit": "",
        "root_id": response.root_id or "",
        "snippet_hash": response.function_hash,
        "where": response.where,
        "reason": response.description,
        "candidate_index": response.candidate_index,
        "ranking_score": None,
        "vulnerability_id_candidate": None,
        "inputTokens": None,
        "outputTokens": None,
        "totalTokens": None,
        "suggested_criteria_code": None,
        "vulnerable": False,
        "specific": None,
        "suggested_finding_title": None,
        "line_start": None,
        "line_end": None,
        "column_start": None,
        "column_end": None,
        "cost": response.cost,
        "trace_id": response.trace_id,
    }
    if isinstance(response, Vulnerable):
        vulnerability["vulnerable"] = True
        vulnerability["suggested_finding_title"] = response.defines_title
        vulnerability["suggested_criteria_code"] = response.defines_code
        vulnerability["specific"] = str(response.specific)
    return vulnerability


async def process_result(
    vulnerability: ItemAnalysisResult,
    db_client: AnalysisDB,
) -> ItemAnalysisResult:
    await db_client.insert_vulnerability(vulnerability)
    if isinstance(db_client, DynamoVulnDB) and vulnerability["vulnerable"]:
        await submit_vulnerability_to_sqs(vulnerability)
    return vulnerability


async def submit_vulnerability_to_sqs(result: ItemAnalysisResult) -> None:
    session = aioboto3.Session()
    async with session.client("sqs", region_name="us-east-1") as sqs_client:
        await sqs_client.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/205810638802/integrates_llm_report",
            MessageBody=json.dumps(
                {
                    "id": f"{result['snippet_hash']}_{result['commit']}",
                    "task": "report_llm",
                    "args": [result["root_id"], result["where"], result["snippet_hash"], "None"],
                },
            ),
        )
