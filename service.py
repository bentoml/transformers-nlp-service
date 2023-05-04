from __future__ import annotations

import typing as t
import asyncio

import pydantic

import bentoml
from download_model import TEXT
from download_model import CATEGORIES
from download_model import get_runner
from download_model import MAX_LENGTH
from download_model import summarization_model
from download_model import classification_model
from download_model import CATEGORICAL_THRESHOLD

summarizer_runner = get_runner("summarization", summarization_model)
categorizer_runner = get_runner("zero-shot-classification", classification_model)

svc = bentoml.Service(
    name="transformers-nlp-service", runners=[summarizer_runner, categorizer_runner]
)


@svc.api(input=bentoml.io.Text.from_sample(TEXT), output=bentoml.io.Text())
async def summarize(text: str) -> str:
    generated = await summarizer_runner.async_run(text, max_length=MAX_LENGTH)
    return generated[0]["summary_text"]


class ClassificationInput(pydantic.BaseModel):
    text: str
    categories: t.List[str]

    class Config:
        extra = "forbid"


@svc.api(
    input=bentoml.io.JSON(pydantic_model=ClassificationInput), output=bentoml.io.JSON()
)
async def categorize(input_data: ClassificationInput) -> dict[str, float]:
    predictions = await categorizer_runner.async_run(
        input_data.text, input_data.categories, multi_label=True
    )
    return {
        c: p
        for c, p in zip(predictions["labels"], predictions["scores"])
        if p > CATEGORICAL_THRESHOLD
    }


class GeneralAnalysisOutput(pydantic.BaseModel):
    summary: str
    categories: t.Dict[str, float]


@svc.api(
    input=bentoml.io.JSON.from_sample(
        ClassificationInput(text=TEXT, categories=CATEGORIES)
    ),
    output=bentoml.io.JSON.from_sample(
        GeneralAnalysisOutput(
            summary=" Hunter Schafer wore a bias-cut white silk skirt, a single ivory-colored feather and nothing else . The look debuted earlier this month at fashion house Ann Demeulemeester's show in Paris . It was designed by Ludovic de Saint Sernin, the label's creative director since December .",
            categories={
                "entertainment": 0.5805651545524597,
                "world": 0.5592136979103088,
            },
        )
    ),
)
async def make_analysis(input_data: ClassificationInput) -> GeneralAnalysisOutput:
    text, categories = input_data.text, input_data.categories
    results = [
        res
        for res in await asyncio.gather(
            summarizer_runner.async_run(text, max_length=MAX_LENGTH),
            categorizer_runner.async_run(text, categories, multi_label=True),
        )
    ]
    return GeneralAnalysisOutput(
        summary=results[0][0]["summary_text"],
        categories={
            c: p
            for c, p in zip(results[1]["labels"], results[1]["scores"])
            if p > CATEGORICAL_THRESHOLD
        },
    )
