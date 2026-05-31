# src/sotl/recommend.py
from dataclasses import dataclass

import pandas as pd


@dataclass
class Recommendation:
    pick: str | None
    score_col: str
    reason_rows: pd.DataFrame  # candidates within budget, best first


def recommend(
    df: pd.DataFrame, task: str, max_price_out: float, prefer_efficient: bool
) -> Recommendation:
    score_col = "swe_bench" if task == "coding" else "mmlu_pro"
    cand = df.copy()
    cand["price_out"] = pd.to_numeric(cand["price_out"], errors="coerce")
    cand[score_col] = pd.to_numeric(cand[score_col], errors="coerce")
    cand = cand[cand["price_out"] <= max_price_out].dropna(subset=[score_col, "price_out"])
    if cand.empty:
        return Recommendation(pick=None, score_col=score_col, reason_rows=cand)
    if prefer_efficient:
        # value: score per $ (clip price to avoid div-by-zero for free models)
        cand["_rank"] = cand[score_col] / cand["price_out"].clip(lower=0.01)
        rank_col = "_rank"
    else:
        rank_col = score_col
    cand = cand.sort_values([rank_col, "price_out"], ascending=[False, True]).reset_index(drop=True)
    return Recommendation(pick=str(cand.loc[0, "name"]), score_col=score_col, reason_rows=cand)
