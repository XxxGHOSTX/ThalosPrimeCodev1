# Thalos Prime Prototype Architecture

This document outlines the prototype's building blocks so future work can extend
it into the requested SBI system.

## Core Components

- **SBI Core** (`thalos_sbi_core.py`): Tokenizer, memory buffer, tensor ops,
  intent analysis, response synthesis, and lightweight storage primitives.
- **Security** (`security.py`): Access policy, hashing, and encryption wrappers
  for parameter payloads.
- **Data Sources** (`data_sources.py`): In-memory and SQLite-backed sources to
  support retrieval and SQL inspection workflows.
- **Pipeline** (`pipeline.py`): Multi-stage pipeline for analysis, retrieval,
  generation, and evaluation.
- **Storage** (`storage.py`): Repository helpers that coordinate model snapshots.

## Runtime Flow

1. UI (Tkinter) accepts user input.
2. Pipeline analyzes intent and optionally retrieves data.
3. Core generates a response and updates memory and knowledge base.
4. Security and storage components manage model artifacts.

## Future Expansion

- Expand tensor engine to support full transformer computation.
- Replace heuristics with learned components.
- Add packaging to produce desktop installers.
