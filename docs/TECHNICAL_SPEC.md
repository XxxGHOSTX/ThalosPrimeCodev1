# Thalos Prime SBI - Technical Specification (Prototype)

## Goals
- Provide a standalone architecture for a custom SBI platform.
- Avoid external ML frameworks in the core implementation.
- Establish UI foundations for a windowed application with a matrix-style background and adjustable controls.

## Implemented in this Prototype
- Minimal tokenizer and rolling memory buffer (100 interactions).
- Dependency-free matrix operations (dot, matmul, softmax).
- Tensor prototype with minimal broadcasting and elementwise ops.
- Basic response pipeline with confidence scoring and intent analysis.
- Encrypted model store prototype (XOR + hash verification).
- SQLite-backed knowledge base for structured notes.
- Data sources (SQLite + in-memory) for retrieval and SQL inspection.
- Multi-stage pipeline orchestration (analyze, retrieve, generate, evaluate).
- Security policy + encryption wrappers for parameter access control.
- Tkinter UI with:
  - Floating main window panel.
  - Toolbar for font and size settings (4-32).
  - Matrix speed control.
  - Collapsible system status panel.
  - Enter-to-submit behavior.
  - Matrix-style animated background.

## Not Implemented (Out of Scope)
- 200M+ parameter transformer model.
- Full OS or full-stack cryptographic parameter storage.
- Model training pipelines or large-scale data ingestion.
- Legal/business formation or copyright registration.

## Expansion Plan
1. Implement a tensor library with broadcasting and automatic differentiation.
2. Build a transformer stack from first principles.
3. Add secure parameter storage (encrypted on disk).
4. Introduce a modular plugin system for data sources.
5. Package as a cross-platform desktop application.
