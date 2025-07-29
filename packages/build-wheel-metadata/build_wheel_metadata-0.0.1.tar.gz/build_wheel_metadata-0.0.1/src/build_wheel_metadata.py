from __future__ import annotations

import tempfile
from contextlib import contextmanager
from importlib.metadata import Distribution
from importlib.util import find_spec

from build import ProjectBuilder
from build.env import DefaultIsolatedEnv, Installer

__author__ = "Dhia Hmila"
__version__ = "0.0.1"
__all__ = ["prepare_metadata"]


def prepare_metadata(
    srcdir: str,
    isolate: bool = True,
    installer: Installer | None = None,
) -> dict:
    installer = installer or ("pip" if find_spec("uv") is None else "uv")
    with project_builder(srcdir, isolate, installer) as builder:
        return extract_metadata(builder)


@contextmanager
def project_builder(
    srcdir: str,
    isolate: bool = True,
    installer: Installer = "pip",
):
    if not isolate:
        return (yield ProjectBuilder(srcdir))

    distribution = "wheel"
    with DefaultIsolatedEnv(installer=installer) as env:
        builder = ProjectBuilder.from_isolated_env(env, srcdir)
        env.install(builder.build_system_requires)
        env.install(builder.get_requires_for_build(distribution))
        yield builder


def extract_metadata(builder: ProjectBuilder) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        dist_info_path = builder.prepare("wheel", tmpdir, {"quiet": "True"})

        dist = Distribution.at(dist_info_path)

        return dict(dist.metadata)
