"""Thalos Prime SBI core (prototype).

This module provides a minimal, dependency-free foundation to demonstrate the
intended architecture: tokenizer, memory buffer, simple matrix utilities, and
response generation. It is intentionally small and transparent so it can be
expanded safely.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
import secrets
import sqlite3
import time
from typing import Dict, Iterable, List, Tuple


@dataclass
class Tokenizer:
    """A tiny whitespace tokenizer with reversible mapping."""

    vocab: Dict[str, int] = field(default_factory=lambda: {"<unk>": 0})
    inv_vocab: Dict[int, str] = field(default_factory=lambda: {0: "<unk>"})

    def encode(self, text: str) -> List[int]:
        tokens = []
        for token in text.strip().split():
            if token not in self.vocab:
                idx = len(self.vocab)
                self.vocab[token] = idx
                self.inv_vocab[idx] = token
            tokens.append(self.vocab[token])
        return tokens

    def decode(self, ids: Iterable[int]) -> str:
        return " ".join(self.inv_vocab.get(i, "<unk>") for i in ids)


@dataclass
class RollingMemory:
    """Stores the last N interactions for context."""

    max_items: int = 100
    history: List[Tuple[str, str]] = field(default_factory=list)

    def append(self, prompt: str, response: str) -> None:
        self.history.append((prompt, response))
        if len(self.history) > self.max_items:
            self.history = self.history[-self.max_items :]

    def as_text(self) -> str:
        lines = []
        for idx, (prompt, response) in enumerate(self.history, start=1):
            lines.append(f"[{idx}] USER: {prompt}")
            lines.append(f"[{idx}] THALOS: {response}")
        return "\n".join(lines)


class MatrixOps:
    """Minimal matrix utilities implemented from scratch."""

    @staticmethod
    def dot(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            raise ValueError("Vector length mismatch")
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def matmul(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        if not a or not b or len(a[0]) != len(b):
            raise ValueError("Matrix shape mismatch")
        result: List[List[float]] = []
        for row in a:
            new_row = []
            for col_idx in range(len(b[0])):
                col = [b[row_idx][col_idx] for row_idx in range(len(b))]
                new_row.append(MatrixOps.dot(row, col))
            result.append(new_row)
        return result

    @staticmethod
    def softmax(values: List[float]) -> List[float]:
        max_val = max(values)
        exps = [math.exp(v - max_val) for v in values]
        total = sum(exps)
        return [v / total for v in exps]


class Tensor:
    """Lightweight tensor with minimal broadcasting support."""

    def __init__(self, data: List[float], shape: Tuple[int, ...]) -> None:
        self.data = data
        self.shape = shape
        if self._size(shape) != len(data):
            raise ValueError("Tensor data size does not match shape")

    @staticmethod
    def from_nested(values: List[List[float]]) -> "Tensor":
        rows = len(values)
        cols = len(values[0]) if rows else 0
        flat = [item for row in values for item in row]
        return Tensor(flat, (rows, cols))

    @staticmethod
    def _size(shape: Tuple[int, ...]) -> int:
        size = 1
        for dim in shape:
            size *= dim
        return size

    def to_nested(self) -> List[List[float]]:
        if len(self.shape) != 2:
            raise ValueError("Only 2D tensors can be converted to nested lists")
        rows, cols = self.shape
        return [
            self.data[row * cols : (row + 1) * cols]
            for row in range(rows)
        ]

    def add(self, other: "Tensor") -> "Tensor":
        return Tensor(self._binary_op(other, lambda a, b: a + b), self._broadcast_shape(other))

    def mul(self, other: "Tensor") -> "Tensor":
        return Tensor(self._binary_op(other, lambda a, b: a * b), self._broadcast_shape(other))

    def _broadcast_shape(self, other: "Tensor") -> Tuple[int, ...]:
        if len(self.shape) != len(other.shape):
            raise ValueError("Broadcasting only supports equal rank tensors")
        shape = []
        for dim_a, dim_b in zip(self.shape, other.shape):
            if dim_a == dim_b:
                shape.append(dim_a)
            elif dim_a == 1:
                shape.append(dim_b)
            elif dim_b == 1:
                shape.append(dim_a)
            else:
                raise ValueError("Incompatible tensor shapes for broadcasting")
        return tuple(shape)

    def _binary_op(self, other: "Tensor", op) -> List[float]:
        shape = self._broadcast_shape(other)
        size = self._size(shape)
        data = []
        for idx in range(size):
            a = self._value_at_broadcast_index(idx, shape)
            b = other._value_at_broadcast_index(idx, shape)
            data.append(op(a, b))
        return data

    def _value_at_broadcast_index(self, index: int, target_shape: Tuple[int, ...]) -> float:
        if len(self.shape) == 1:
            return self.data[index % self.shape[0]]
        rows, cols = target_shape
        row = index // cols
        col = index % cols
        source_row = row if self.shape[0] != 1 else 0
        source_col = col if self.shape[1] != 1 else 0
        return self.data[source_row * self.shape[1] + source_col]


class CryptoManager:
    """Simple XOR-based encryption for prototype storage."""

    def __init__(self, passphrase: str) -> None:
        self.key = hashlib.sha256(passphrase.encode("utf-8")).digest()

    def encrypt(self, payload: bytes) -> bytes:
        return self._xor(payload)

    def decrypt(self, payload: bytes) -> bytes:
        return self._xor(payload)

    def _xor(self, payload: bytes) -> bytes:
        return bytes(b ^ self.key[idx % len(self.key)] for idx, b in enumerate(payload))


class ModelStore:
    """Stores serialized parameters with hash verification."""

    def __init__(self, crypto: CryptoManager) -> None:
        self.crypto = crypto
        self._store: Dict[str, bytes] = {}
        self._hashes: Dict[str, str] = {}

    def save(self, name: str, parameters: Dict[str, List[float]]) -> None:
        raw = json.dumps(parameters).encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        encrypted = self.crypto.encrypt(raw)
        self._store[name] = encrypted
        self._hashes[name] = digest

    def load(self, name: str) -> Dict[str, List[float]]:
        encrypted = self._store[name]
        raw = self.crypto.decrypt(encrypted)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != self._hashes[name]:
            raise ValueError("Model parameter hash mismatch")
        return json.loads(raw.decode("utf-8"))


class KnowledgeBase:
    """SQLite-backed memory for structured notes."""

    def __init__(self, path: str = ":memory:") -> None:
        self.connection = sqlite3.connect(path)
        self._init_schema()

    def _init_schema(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            \"\"\"
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            \"\"\"
        )
        self.connection.commit()

    def add_note(self, topic: str, content: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            \"INSERT INTO notes (topic, content, created_at) VALUES (?, ?, ?)\",
            (topic, content, time.time()),
        )
        self.connection.commit()

    def fetch_notes(self, topic: str) -> List[str]:
        cursor = self.connection.cursor()
        cursor.execute(
            \"SELECT content FROM notes WHERE topic = ? ORDER BY created_at DESC\",
            (topic,),
        )
        return [row[0] for row in cursor.fetchall()]


class IntentAnalyzer:
    """Heuristic intent detection for prototype reasoning."""

    def classify(self, prompt: str) -> str:
        lowered = prompt.lower()
        if any(word in lowered for word in ["why", "explain", "how"]):
            return "analysis"
        if any(word in lowered for word in ["build", "create", "design"]):
            return "creation"
        if any(word in lowered for word in ["fix", "error", "issue"]):
            return "troubleshoot"
        return "general"


class ResponseSynthesizer:
    """Creates a response based on intent, context, and score."""

    def compose(self, prompt: str, intent: str, score: float, context_hash: str) -> str:
        return (
            "THALOS PRIME (prototype) processed your request as intent "
            f"'{intent}' with confidence {score:.2f}. Context hash: {context_hash}."
        )


@dataclass
class SBIConfig:
    """Configuration for the SBI core."""

    max_context_items: int = 100
    seed: int = 0
    db_path: str = ":memory:"
    passphrase: str = "thalos-prime-prototype"


class ThalosSBICore:
    """Prototype SBI engine with deterministic pseudo-reasoning pipeline."""

    def __init__(self, config: SBIConfig | None = None) -> None:
        self.config = config or SBIConfig()
        self.tokenizer = Tokenizer()
        self.memory = RollingMemory(max_items=self.config.max_context_items)
        self.knowledge = KnowledgeBase(self.config.db_path)
        self.crypto = CryptoManager(self.config.passphrase)
        self.model_store = ModelStore(self.crypto)
        self.intent = IntentAnalyzer()
        self.synthesizer = ResponseSynthesizer()
        self.rng = secrets.SystemRandom(self.config.seed)

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _score(self, tokens: List[int]) -> float:
        # A minimal scoring function using token ids and time.
        if not tokens:
            return 0.0
        time_factor = (time.time() % 10) / 10
        score = sum((t + 1) * (idx + 1) for idx, t in enumerate(tokens))
        return (score / (len(tokens) * 10)) + time_factor

    def generate(self, prompt: str) -> str:
        tokens = self.tokenizer.encode(prompt)
        context = self.memory.as_text()
        score = self._score(tokens)
        digest = self._hash(prompt + context)[:12]
        intent = self.intent.classify(prompt)
        response = self.synthesizer.compose(prompt, intent, score, digest)
        self.memory.append(prompt, response)
        self.knowledge.add_note("interactions", f"{prompt} -> {response}")
        return response


__all__ = [
    "CryptoManager",
    "IntentAnalyzer",
    "KnowledgeBase",
    "MatrixOps",
    "ModelStore",
    "ResponseSynthesizer",
    "SBIConfig",
    "Tensor",
    "ThalosSBICore",
    "Tokenizer",
    "RollingMemory",
]
