from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("name", ["board.py", "ai.py", "game.py"])
def test_only_main_prints_or_reads_input(name):
    source = (ROOT / name).read_text()
    assert "print(" not in source
    assert "input(" not in source
