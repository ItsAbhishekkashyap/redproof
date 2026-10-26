"""Shared fixtures for the Redproof test suite."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

DEMO_SCRIPT = Path(__file__).resolve().parents[1] / "demo" / "make_demo.py"


def _load_demo_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("make_demo", DEMO_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def demo_module() -> ModuleType:
    return _load_demo_module()


@pytest.fixture
def demo_repo(tmp_path: Path, demo_module: ModuleType) -> Path:
    return demo_module.make_demo(tmp_path / "demo-repo")