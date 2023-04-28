from __future__ import annotations

import pydantic
import asyncio
import pytest
import typing as t

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_summarize(mocker: MockerFixture):
    import service

    s_runner = mocker.patch("service.summarizer_runner")
    s_runner.async_run = s_runner.object(service.summarizer_runner, "async_run")
    future = asyncio.Future()
    future.set_result(
        [{"summary_text": "The quick brown fox jumps over the lazy dog."}]
    )
    s_runner.async_run.return_value = future

    res = await service.summarize("asdfasdf")
    assert res == "The quick brown fox jumps over the lazy dog."


@pytest.mark.asyncio
async def test_categorize(mocker: MockerFixture):
    import service

    c_runner = mocker.patch("service.categorizer_runner")
    c_runner.async_run = c_runner.object(service.categorizer_runner, "async_run")
    future = asyncio.Future()
    future.set_result({"labels": ["entertainment"], "scores": [0.5805]})
    c_runner.async_run.return_value = future

    res = await service.categorize(
        service.ClassificationInput(text="asdfasdf", categories=["asdfasd", "asdfasd"])
    )
    assert isinstance(res, dict) and res == {"entertainment": 0.5805}


@pytest.mark.asyncio
async def test_make_analysis(mocker: MockerFixture):
    import service

    c_runner = mocker.patch("service.categorizer_runner")
    c_runner.async_run = c_runner.object(service.categorizer_runner, "async_run")
    future = asyncio.Future()
    future.set_result({"labels": ["entertainment"], "scores": [0.5805]})
    c_runner.async_run.return_value = future

    s_runner = mocker.patch("service.summarizer_runner")
    s_runner.async_run = s_runner.object(service.summarizer_runner, "async_run")
    future = asyncio.Future()
    future.set_result(
        [{"summary_text": "The quick brown fox jumps over the lazy dog."}]
    )
    s_runner.async_run.return_value = future

    res = await service.make_analysis(
        service.ClassificationInput(text="asdfasdf", categories=["asdfasd", "asdfasd"])
    )

    assert isinstance(res, pydantic.BaseModel) and res.dict() == {
        "summary": "The quick brown fox jumps over the lazy dog.",
        "categories": {"entertainment": 0.5805},
    }
