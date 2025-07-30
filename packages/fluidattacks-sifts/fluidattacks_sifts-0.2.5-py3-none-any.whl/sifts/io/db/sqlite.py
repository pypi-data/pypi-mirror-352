import asyncio
import json
import sqlite3
from pathlib import Path
from typing import cast

import aiosqlite

from sifts.common_types.snippets import ItemAnalysisResult, Snippet
from sifts.io.db.base import AnalysisDB


class SQLiteVulnDB(AnalysisDB):
    def __init__(self, db_file: str = "vulnerabilities.db") -> None:
        self.db_file = db_file
        output_path = Path(db_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
        self._lock = asyncio.Lock()

    def _initialize_db(self) -> None:
        conn = sqlite3.connect(self.db_file, timeout=30.0)
        # Habilitar el modo WAL para mejorar la concurrencia y establecer busy_timeout
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                pk TEXT,
                sk TEXT,
                candidate_index INTEGER,
                "commit" TEXT,
                group_name TEXT,
                inputTokens INTEGER,
                outputTokens INTEGER,
                ranking_score REAL,
                reason TEXT,
                root_id TEXT,
                snippet_hash TEXT,
                specific TEXT,
                cost REAL,
                suggested_criteria_code TEXT,
                suggested_finding_title TEXT,
                totalTokens INTEGER,
                vulnerability_id_candidate TEXT,
                vulnerable BOOLEAN,
                "where" TEXT,
                trace_id TEXT,
                PRIMARY KEY (pk, sk),
                FOREIGN KEY(snippet_hash) REFERENCES snippets(snippet_hash)
            )""",
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snippets (
                pk TEXT,
                sk TEXT,
                "commit" TEXT,
                end_point TEXT,
                group_name TEXT,
                hash_type TEXT,
                language TEXT,
                root_id TEXT,
                root_nickname TEXT,
                snippet_content TEXT,
                snippet_hash TEXT UNIQUE,
                start_point TEXT,
                "where" TEXT,
                name TEXT,
                PRIMARY KEY (pk, sk)
            )""",
        )
        conn.commit()
        conn.close()

    async def get_vulnerability(self, pk: str, sk: str) -> ItemAnalysisResult | None:
        async with aiosqlite.connect(self.db_file, timeout=30.0) as conn:
            cursor = await conn.execute(
                """SELECT * FROM vulnerabilities WHERE pk = ? AND sk = ?""",
                (pk, sk),
            )
            row = await cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            raw_dict = dict(zip(columns, row, strict=True))
            return cast(ItemAnalysisResult, raw_dict)
        return None

    async def insert_vulnerability(self, vuln: ItemAnalysisResult) -> bool:
        async with self._lock, aiosqlite.connect(self.db_file, timeout=30.0) as conn:
            columns = []
            values = []
            placeholders = []

            for key, value in vuln.items():
                if value is not None:
                    columns.append(f'"{key}"' if key in ["commit", "where"] else key)
                    values.append(value)
                    placeholders.append("?")

            query = f"""INSERT OR REPLACE INTO vulnerabilities (
                {", ".join(columns)}
            ) VALUES ({", ".join(placeholders)})"""  # noqa: S608

            await conn.execute(query, tuple(values))
            await conn.commit()
        return True

    async def insert_snippet(self, snippet: Snippet) -> bool:
        async with self._lock, aiosqlite.connect(self.db_file, timeout=30.0) as conn:
            snippet_dict = snippet._asdict()
            columns = []
            values = []
            placeholders = []

            for key, value in snippet_dict.items():
                if value is not None:
                    columns.append(f'"{key}"' if key in ["commit", "where"] else key)
                    # JSON serialize lists
                    if key in ["end_point", "start_point"] and value is not None:
                        value = json.dumps(value)  # noqa: PLW2901
                    values.append(value)
                    placeholders.append("?")

            query = f"""INSERT OR REPLACE INTO snippets (
                {", ".join(columns)}
            ) VALUES ({", ".join(placeholders)})"""  # noqa: S608

            await conn.execute(query, tuple(values))
            await conn.commit()
        return True

    async def aget_snippet(self, root_id: str, path: str, hash_: str) -> Snippet | None:
        async with aiosqlite.connect(self.db_file, timeout=30.0) as conn:
            pk = f"PATH#{path}#SNIPPET#{hash_}"
            sk = f"ROOT#{root_id}"
            cursor = await conn.execute(
                """SELECT * FROM snippets WHERE pk = ? AND sk = ?""",
                (pk, sk),
            )
            row = await cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            item = dict(zip(columns, row, strict=True))

            # Convert JSON strings to lists
            if item.get("end_point"):
                item["end_point"] = json.loads(item["end_point"])
            if item.get("start_point"):
                item["start_point"] = json.loads(item["start_point"])

            return Snippet(**item)
        return None

    def get_snippet(self, root_id: str, path: str, hash_: str) -> Snippet | None:
        with sqlite3.connect(self.db_file, timeout=30.0) as conn:
            cursor = conn.execute(
                """SELECT * FROM snippets WHERE pk = ? AND sk = ?""",
                (f"PATH#{path}#SNIPPET#{hash_}", f"ROOT#{root_id}"),
            )
            row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            item = dict(zip(columns, row, strict=True))

            # Convert JSON strings to lists
            if item.get("end_point"):
                item["end_point"] = json.loads(item["end_point"])
            if item.get("start_point"):
                item["start_point"] = json.loads(item["start_point"])

            return Snippet(**item)
        return None

    async def get_vulnerabilities_by_snippet(
        self,
        root_id: str,
        path: str,
        snippet_hash: str,
    ) -> list[ItemAnalysisResult]:
        pk = f"ROOT#{root_id}#PATH#{path}"
        snippet_prefix = f"SNIPPET#{snippet_hash}%"
        async with aiosqlite.connect(self.db_file, timeout=30.0) as conn:
            cursor = await conn.execute(
                """SELECT * FROM vulnerabilities WHERE pk = ? AND sk LIKE ?""",
                (pk, snippet_prefix),
            )
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description]

        vulnerabilities = []
        for row in rows:
            raw_dict = dict(zip(columns, row, strict=True))
            vulnerabilities.append(cast(ItemAnalysisResult, raw_dict))
        return vulnerabilities

    async def get_vulnerabilities_vulnerable(self) -> list[ItemAnalysisResult]:
        async with aiosqlite.connect(self.db_file, timeout=30.0) as conn:
            cursor = await conn.execute(
                """SELECT * FROM vulnerabilities WHERE vulnerable = 1""",
            )
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description]

        return [cast(ItemAnalysisResult, dict(zip(columns, row, strict=True))) for row in rows]
