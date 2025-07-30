from sifts.common_types.snippets import ItemAnalysisResult, Snippet


class AnalysisDB:
    async def get_vulnerability(self, pk: str, sk: str) -> ItemAnalysisResult | None:
        msg = "Method get_vulnerability not implemented"
        raise NotImplementedError(msg)

    async def insert_vulnerability(self, vuln: ItemAnalysisResult) -> bool:
        msg = "Method insert_vulnerability not implemented"
        raise NotImplementedError(msg)

    async def insert_snippet(self, snippet: Snippet) -> bool:
        msg = "Method insert_snippet not implemented"
        raise NotImplementedError(msg)

    async def aget_snippet(self, root_id: str, path: str, hash_: str) -> Snippet | None:
        msg = "Method get_snippet not implemented"
        raise NotImplementedError(msg)

    def get_snippet(self, root_id: str, path: str, hash_: str) -> Snippet | None:
        msg = "Method get_snippet not implemented"
        raise NotImplementedError(msg)

    async def get_vulnerabilities_by_snippet(
        self,
        root_id: str,
        path: str,
        snippet_hash: str,
    ) -> list[ItemAnalysisResult]:
        msg = "Method get_vulnerabilities_by_snippet not implemented"
        raise NotImplementedError(msg)

    async def get_vulnerabilities_vulnerable(self) -> list[ItemAnalysisResult]:
        msg = "Method get_vulnerabilities_vulnerable not implemented"
        raise NotImplementedError(msg)
