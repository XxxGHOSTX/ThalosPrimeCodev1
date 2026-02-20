"""Multi-stage pipeline orchestration for Thalos Prime."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .data_sources import DataSource
from .thalos_sbi_core import ThalosSBICore


@dataclass
class PipelineContext:
    prompt: str
    intent: str = "general"
    retrieved: List[str] = field(default_factory=list)
    response: str = ""
    confidence: float = 0.0


class SBIPipeline:
    def __init__(self, core: ThalosSBICore, data_sources: List[DataSource] | None = None) -> None:
        self.core = core
        self.data_sources = data_sources or []

    def analyze(self, context: PipelineContext) -> None:
        context.intent = self.core.intent.classify(context.prompt)

    def retrieve(self, context: PipelineContext) -> None:
        for source in self.data_sources:
            try:
                context.retrieved.extend(list(source.query(context.prompt)))
            except Exception:
                continue

    def generate(self, context: PipelineContext) -> None:
        response = self.core.generate(context.prompt)
        context.response = response
        context.confidence = self.core._score(self.core.tokenizer.encode(context.prompt))

    def evaluate(self, context: PipelineContext) -> None:
        if context.retrieved:
            context.response += f"\nRetrieved items: {len(context.retrieved)}"

    def run(self, prompt: str) -> PipelineContext:
        context = PipelineContext(prompt=prompt)
        self.analyze(context)
        self.retrieve(context)
        self.generate(context)
        self.evaluate(context)
        return context
