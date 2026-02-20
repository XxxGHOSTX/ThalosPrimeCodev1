"""Data sources for Thalos Prime prototype."""
from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Iterable, List, Protocol


class DataSource(Protocol):
    name: str

    def query(self, query: str) -> Iterable[str]:
        ...


@dataclass
class InMemoryDataSource:
    name: str
    rows: List[str]

    def query(self, query: str) -> Iterable[str]:
        lowered = query.lower()
        return [row for row in self.rows if lowered in row.lower()]


class SQLiteDataSource:
    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.path = path

    def query(self, query: str) -> Iterable[str]:
        conn = sqlite3.connect(self.path)
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            return [" | ".join(str(col) for col in row) for row in cursor.fetchall()]
        finally:
            conn.close()
