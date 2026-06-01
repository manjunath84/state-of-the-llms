# tests/test_narrate.py
from pathlib import Path

from sotl.config import Settings
from sotl.narrate import takeaway


class _BoomClient:
    class chat:  # noqa: N801
        class completions:  # noqa: N801
            @staticmethod
            def create(**_):
                raise AssertionError("API must not be called")


class _RaiseClient:  # simulates an API/network error at call time
    class chat:  # noqa: N801
        class completions:  # noqa: N801
            @staticmethod
            def create(**_):
                raise RuntimeError("api down")


class _FakeResp:
    def __init__(self, text):
        self.choices = [type("C", (), {"message": type("M", (), {"content": text})()})()]


class _FakeClient:
    def __init__(self, text):
        self._text = text

    class _Comp:
        def __init__(self, outer):
            self._outer = outer

        def create(self, **_):
            return _FakeResp(self._outer._text)

    class _Chat:
        def __init__(self, outer):
            self._outer = outer

        @property
        def completions(self):
            return _FakeClient._Comp(self._outer)

    @property
    def chat(self):
        return _FakeClient._Chat(self)


def _settings(tmp_path: Path, *, key=None, base_url="https://openrouter.ai/api/v1") -> Settings:
    return Settings(
        narration_api_key=key, narration_base_url=base_url,
        cache_path=tmp_path / "n.json", data_dir=tmp_path,
    )


def test_no_api_key_returns_fallback_and_caches(tmp_path):
    s = _settings(tmp_path)
    out = takeaway("coding_per_dollar", "B: 50 pts/$", s, client=_BoomClient())
    assert "B: 50 pts/$" in out
    assert s.cache_path.exists()


def test_cache_hit_does_not_call_api(tmp_path):
    s = _settings(tmp_path, key="or-x")
    takeaway("c1", "summary one", s, client=_FakeClient("cached!"))
    again = takeaway("c1", "summary one", s, client=_BoomClient())  # must hit cache
    assert again == "cached!"


def test_api_path_returns_model_text(tmp_path):
    s = _settings(tmp_path, key="or-x")
    out = takeaway("c2", "summary two", s, client=_FakeClient("frontier got cheap"))
    assert out == "frontier got cheap"


def test_api_error_falls_back_to_summary(tmp_path):
    s = _settings(tmp_path, key="or-x")  # key present, but the call raises
    out = takeaway("c5", "B leads on coding/$", s, client=_RaiseClient())
    assert out == "B leads on coding/$"  # demo-safe fallback (guardrail #6)


def test_cache_key_includes_model(tmp_path):
    s = _settings(tmp_path, key="or-x")
    a = takeaway("c4", "same summary", s,
                 model="meta-llama/llama-3.1-8b-instruct", client=_FakeClient("A"))
    b = takeaway("c4", "same summary", s,
                 model="qwen/qwen-2.5-7b-instruct", client=_FakeClient("B"))
    assert (a, b) == ("A", "B")  # distinct cache entries per narrator


def test_hallucinated_number_is_rejected(tmp_path):
    # guardrail #3: the narrator invents 85.2 / 67.1 (not in the input) → reject,
    # fall back to the deterministic summary. This is the exact failure observed
    # in the browser with Llama 3.1 8B.
    s = _settings(tmp_path, key="or-x")
    summary = "Open models average 80% on SWE-bench vs 81% for closed."
    bad = "Open scores 85.2% and closed 67.1% — a huge gap."
    out = takeaway("ovc", summary, s, client=_FakeClient(bad))
    assert out == summary


def test_faithful_number_use_is_kept(tmp_path):
    # The narrator rephrases but reuses only the input's numbers → keep it.
    s = _settings(tmp_path, key="or-x")
    summary = "DeepSeek-V4-Flash scores 79% at $0.28 per 1M output tokens."
    good = "At just $0.28, DeepSeek-V4-Flash already hits 79% on coding."
    out = takeaway("cpd", summary, s, client=_FakeClient(good))
    assert out == good


def test_number_free_prose_is_kept(tmp_path):
    s = _settings(tmp_path, key="or-x")
    summary = "Open models nearly match closed on coding for a fraction of the price."
    good = "Open weights have all but closed the coding gap, far cheaper."
    out = takeaway("ovc2", summary, s, client=_FakeClient(good))
    assert out == good
