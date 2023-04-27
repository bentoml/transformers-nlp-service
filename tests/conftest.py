from __future__ import annotations

import contextlib
import sys
import psutil
import os
import pytest
from pathlib import Path
import typing as t
import bentoml

if t.TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest

    P = t.TypeVar("P")
    Generator = t.Generator[P, None, None]

PROJECT_PATH = Path(__file__).parent.parent
BENTO_NAME = "multi-tasks-nlp"


@pytest.fixture(name="project_path", params=[PROJECT_PATH], scope="session")
def fixture_project_path(request: FixtureRequest):
    return request.param


@pytest.fixture(name="enable_grpc", params=[True, False], scope="function")
def fixture_enable_grpc(request: FixtureRequest):
    return request.param


@pytest.fixture(autouse=True)
@pytest.mark.tryfirst
def skip_by_server_type(request: FixtureRequest, enable_grpc: bool):
    marker = request.node.get_closest_marker("skip_server_type")
    if marker:
        if marker.args[0] not in ["grpc", "http"]:
            raise ValueError(
                f"skip_server_type marker only supports 'grpc' or 'http', got {marker.args[0]}"
            )
        if marker.args[0] == "grpc" and enable_grpc:
            pytest.skip("Skip gRPC server for HTTP tests.")
        if marker.args[0] == "http" and not enable_grpc:
            pytest.skip("Skip HTTP server for gRPC tests.")


# TODO: add distributed and container tests
@pytest.fixture(scope="function")
def host(
    clean_context: contextlib.ExitStack, project_path: str, enable_grpc: bool
) -> t.Generator[str, None, None]:
    from bentoml.testing.server import build, run_bento_server_standalone

    if psutil.WINDOWS and enable_grpc:
        pytest.skip("gRPC is not yet supported on Windows.")

    try:
        bento = bentoml.get(BENTO_NAME)
    except bentoml.exceptions.NotFound:
        bento = clean_context.enter_context(build(project_path, cleanup=False))

    with run_bento_server_standalone(
        bento.path,
        config_file=PROJECT_PATH.joinpath("config", "default.yaml").__fspath__(),
        use_grpc=enable_grpc,
        timeout=120,
    ) as host_url:
        yield host_url


@pytest.fixture(autouse=True, scope="session")
def bento_directory(request: FixtureRequest):
    os.chdir(PROJECT_PATH.__fspath__())
    sys.path.insert(0, PROJECT_PATH.__fspath__())
    yield
    os.chdir(request.config.invocation_dir)
    sys.path.pop(0)
