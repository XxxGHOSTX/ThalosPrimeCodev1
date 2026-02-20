"""Storage helpers for Thalos Prime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .thalos_sbi_core import ModelStore


@dataclass
class ParameterSnapshot:
    name: str
    tensors: Dict[str, List[float]]


class ParameterRepository:
    def __init__(self, store: ModelStore) -> None:
        self.store = store

    def save_snapshot(self, snapshot: ParameterSnapshot) -> None:
        self.store.save(snapshot.name, snapshot.tensors)

    def load_snapshot(self, name: str) -> ParameterSnapshot:
        return ParameterSnapshot(name=name, tensors=self.store.load(name))
