import os
from pathlib import Path

import commitizen_wheel_provider
from commitizen_wheel_provider import WheelProvider

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).parents[1]


@pytest.fixture(autouse=True)
def root_cwd(project_root: Path):
    og = os.getcwd()
    try:
        os.chdir(project_root.as_posix())
        yield
    finally:
        os.chdir(og)


def test_commitizen_wheel_provider() -> None:
    config = {}
    provider = WheelProvider(config)
    expected_version = commitizen_wheel_provider.__version__

    assert provider.get_version() == expected_version
