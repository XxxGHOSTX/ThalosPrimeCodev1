"""Configuration helpers for Thalos Prime prototypes."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, List


@dataclass
class UISettings:
    font_family: str = "Courier"
    font_size: int = 12
    matrix_speed_ms: int = 120


@dataclass
class SecuritySettings:
    passphrase: str = "thalos-prime-prototype"
    allow_parameter_export: bool = False


@dataclass
class DataSourceSettings:
    default_sqlite_path: str = ":memory:"


@dataclass
class CoreSettings:
    max_context_items: int = 100
    ui: UISettings = field(default_factory=UISettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    data_sources: DataSourceSettings = field(default_factory=DataSourceSettings)


def load_settings(path: str | Path) -> CoreSettings:
    payload = json.loads(Path(path).read_text())
    return CoreSettings(
        max_context_items=payload.get("max_context_items", 100),
        ui=UISettings(**payload.get("ui", {})),
        security=SecuritySettings(**payload.get("security", {})),
        data_sources=DataSourceSettings(**payload.get("data_sources", {})),
    )


def save_settings(settings: CoreSettings, path: str | Path) -> None:
    payload: Dict[str, object] = {
        "max_context_items": settings.max_context_items,
        "ui": settings.ui.__dict__,
        "security": settings.security.__dict__,
        "data_sources": settings.data_sources.__dict__,
    }
    Path(path).write_text(json.dumps(payload, indent=2))
