"""Run with:  python -m pytest -q   (or just: python tests/test_build.py)"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
import build, charts  # noqa: E402


def test_build_runs_and_contains_title():
    out = build.build()
    html = out.read_text(encoding="utf-8")
    assert "Nobody should build it alone" in html and 'id="why"' in html


def test_feeder_scenarios():
    n = build.load("numbers.yaml")
    base = charts.feeder_stats(n, "base")
    coord = charts.feeder_stats(n, "coordinated")
    assert base["hours_over"] >= 1 and coord["hours_over"] == 0


if __name__ == "__main__":
    test_build_runs_and_contains_title(); test_feeder_scenarios(); print("ok")
