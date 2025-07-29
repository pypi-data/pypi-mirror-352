from pathlib import Path

import pytest

import build_wheel_metadata


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).parents[1]


def test_build_wheel_metadata(project_root: Path) -> None:
    expected_name = "build-wheel-metadata"
    expected_version = build_wheel_metadata.__version__

    metadata = build_wheel_metadata.prepare_metadata(
        project_root.as_posix(), isolate=True
    )

    assert metadata["Name"] == expected_name
    assert metadata["Version"] == expected_version
