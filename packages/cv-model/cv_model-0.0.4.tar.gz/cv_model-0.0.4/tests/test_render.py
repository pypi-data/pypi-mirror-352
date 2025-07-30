from pathlib import Path

import pytest
import cv_model as cm


@pytest.mark.parametrize(
    "ext", ["typ", "pdf", "svg", "png"]
)
def test_generate(tmp_path: Path, ext: str) -> None:
    cm.generate(cm.Resume.get_empty(), tmp_path / f"test.{ext}", "fantastic-cv")
