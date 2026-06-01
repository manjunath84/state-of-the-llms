# tests/test_validate_models.py
import importlib.util
from pathlib import Path

import pandas as pd

# scripts/ is not a package; load the module by path.
_SPEC = importlib.util.spec_from_file_location(
    "validate_models",
    Path(__file__).resolve().parents[1] / "scripts" / "validate_models.py",
)
validate_models = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(validate_models)
validate = validate_models.validate


def _good_row(name: str, *, is_open: str = "false", price_out=10, mmlu=70.0) -> dict:
    return {
        "name": name, "lab": "Lab", "release_date": "2026-01-01", "params": "unknown",
        "context_window": 128000, "price_in": 1, "price_out": price_out,
        "mmlu_pro": mmlu, "swe_bench": 40.0, "arena_elo": 1300, "is_open": is_open,
        "source_url": "https://example.com/x", "last_verified": "2026-05-31",
        "metric_type": "reported_by_lab", "confidence": "high", "metric_notes": "",
    }


def _good_df(n: int = 12) -> pd.DataFrame:
    return pd.DataFrame([_good_row(f"M{i}", price_out=1 + i, mmlu=60 + i) for i in range(n)])


def test_clean_data_has_no_problems():
    assert validate(_good_df()) == []


def test_placeholder_text_is_flagged():
    df = _good_df()
    df.loc[0, "metric_notes"] = "SEED ROW - verify/replace before demo"
    problems = validate(df)
    assert any("placeholder" in p for p in problems)


def test_blank_provenance_is_flagged():
    df = _good_df()
    df.loc[1, "source_url"] = ""
    df.loc[2, "last_verified"] = "unknown"
    problems = validate(df)
    assert any("source_url is blank" in p for p in problems)
    assert any("last_verified is blank" in p for p in problems)


def test_non_url_source_is_flagged():
    df = _good_df()
    df.loc[0, "source_url"] = "artificialanalysis.ai/models/x"  # no scheme
    assert any("not a URL" in p for p in validate(df))


def test_unparseable_is_open_is_flagged():
    df = _good_df()
    df.loc[0, "is_open"] = "maybe"
    assert any("is_open not boolean" in p for p in validate(df))


def test_too_few_numeric_rows_is_flagged():
    # 12 rows but only 3 with numeric swe_bench → scatter (price_out vs swe_bench)
    # would be sparse. Cast to object first: real CSVs with "unknown" cells load
    # the column as object dtype, and assigning a str into an int64/float64
    # column raises in this pandas version.
    df = _good_df(12)
    df["swe_bench"] = df["swe_bench"].astype(object)
    df.loc[3:, "swe_bench"] = "unknown"
    assert any("scatter is sparse" in p for p in validate(df))


def test_missing_column_short_circuits():
    df = _good_df().drop(columns=["is_open"])
    problems = validate(df)
    assert len(problems) == 1
    assert "missing required columns" in problems[0]
