"""Run with:  python -m pytest -q   (or just: python tests/test_build.py)"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
import build, charts  # noqa: E402


def test_all_editions_build():
    outs = build.build_all()
    assert len(outs) >= 3
    for o in outs:
        html = o.read_text(encoding="utf-8")
        assert 'id="problem"' in html and 'id="annex"' in html


def test_feeder_scenarios():
    n = build.load("numbers.yaml")
    assert charts.feeder_stats(n, "base")["hours_over"] >= 1 and charts.feeder_stats(n, "coordinated")["hours_over"] == 0


if __name__ == "__main__":
    test_all_editions_build(); test_feeder_scenarios(); print("ok")
