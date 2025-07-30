from collections import defaultdict
from collections.abc import Iterable

from sifts.common_types.snippets import SnippetHit

MIN_SCORE_THRESHOLD = 0.5


def reciprocal_rank_fusion_with_score(
    hits_lists: Iterable[Iterable[SnippetHit]],
    top_n: int = 10,
    weight_score: float = 0.2,
) -> list[SnippetHit]:
    re_rank_scores = defaultdict(float)
    id_to_hit = {}

    for hit_list in hits_lists:
        for hit in hit_list:
            vuln_id = hit["_source"]["metadata"]["vulnerability_id"]
            if vuln_id not in id_to_hit:
                id_to_hit[vuln_id] = hit

    for vuln_id in id_to_hit:
        rrf_score = 0.0
        total_score = 0.0
        count = 0

        for hit_list in hits_lists:
            rank = next(
                (
                    rank + 1
                    for rank, h in enumerate(hit_list)
                    if h["_source"]["metadata"]["vulnerability_id"] == vuln_id
                ),
                float("inf"),
            )
            if rank != float("inf"):
                rrf_score += 1 / rank
                total_score += next(
                    h["_score"]
                    for h in hit_list
                    if h["_source"]["metadata"]["vulnerability_id"] == vuln_id
                )
                count += 1

        avg_score = total_score / count if count > 0 else 0.0

        final_score = (1 - weight_score) * rrf_score + weight_score * avg_score
        re_rank_scores[vuln_id] = final_score

    sorted_items = sorted(re_rank_scores.items(), key=lambda x: x[1], reverse=True)

    return [
        {**id_to_hit[vuln_id], "ReRankingScore": score}
        for vuln_id, score in sorted_items[:top_n]
        if score >= MIN_SCORE_THRESHOLD
    ]
