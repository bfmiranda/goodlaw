# Copilot Instructions for GoodLaw

## Overview
GoodLaw is a B2B analysis tool that classifies Businessmap tasks as qualifying R&D under Brazil's **Lei do Bem** (tax incentive), based on the **Frascati Manual** and Lei do Bem regulations.

## Build, Test & Run

**Setup:**
```bash
pip install -r requirements.txt
```

**Run tests:**
```bash
pytest                              # Full test suite
pytest tests/test_models.py         # Test models only
pytest -k test_core_nao_importa     # Run architecture test
```

**Start the application:**
```bash
streamlit run streamlit_app.py
```

## Architecture: Core/Interface Separation

This is a **hard architectural boundary**—enforce it always.

### Core Layer (`core/`)
- **Contains:** All business logic, data models, rules, extraction, classification, clustering, audit
- **Tech:** Python + Pydantic, no dependencies on frameworks
- **Prohibited imports:** `streamlit`, `fastapi`, `fasthtml`, `starlette`, `plotly`, `pyvis`, `dash`, `app`
- **Enforced by:** `tests/test_architecture.py` (must pass in every PR)

**Structure:**
- `models.py` — Pydantic contracts: `Card`, `Classificacao`, `RegistroAuditoria`, enums
- `ingest/` — Businessmap collection
- `extraction/` — Entity extraction, task essence, activity nature
- `rules/` — Lei do Bem + Frascati exclusions and classification criteria
- `clustering/` — Task grouping
- `audit/` — Audit trail generation

### App Layer (`app/`)
- **Contains:** Streamlit interface only
- **Does:** Calls `core/` functions, displays results
- **Never:** Implements business rules, fiscal criteria, or calculations
- **Principle:** Just UI—all logic lives in `core/`

**Note:** Future API layer (`api/`) will also call the same `core/` without modification.

## Key Conventions

### Fiscal Conservatism (Non-Negotiable)
When in doubt, classify as **not eligible** or **needs human review**—never **eligible**. False positives risk audit/penalties for the client.
- `Classificacao` model rejects "enquadrável" unless all 4 criteria are met AND nature is not excluded
- Excluded natures (hardcoded): corrective maintenance, operational support, off-the-shelf implementation, indefinite

### Language & Comments
- Code and domain names in Portuguese
- Comments concise; explain *why*, not *what*
- Document fiscal/regulatory decisions inline with manual + section reference

### Testing
- All `core/` changes require tests in `tests/`
- Tests are the contract between layers
- No Streamlit/framework dependencies in `tests/`
- Architecture test must always pass: `pytest tests/test_architecture.py`

### Model Versioning
- `RegistroAuditoria` always includes `versao_regras` (rules version)
- When rules change, update version; audit trail stays immutable

### Pipeline Stages (Order Matters)
1. **Extraction**: Entities, task essence (1 sentence), activity nature, OKR → Initiative → Story → Task hierarchy
   - Orphaned/standalone cards flagged with lower confidence
2. **Exclusions** (before any positive): Applied first, blocks enquadrement
   - Maintenance, generic improvements, canned software, migrations, standard integrations, support, training, deploys, pure business gains
   - Children of maintenance stay excluded (even if parent is innovative)
3. **Enquadrement** (all remaining): Technologically new + real technical uncertainty + systematic method + traceable evidence

### Code Organization
- Indicate layer in new files: e.g., `# Camada: core` or `# Camada: app`
- Incremental construction: smallest logical step per commit
- New features in `core/` with corresponding tests; integrate into `app/` after validation

## Audit Trail
Every step generates `RegistroAuditoria`:
- Input: card, stage, rule, normative reference (manual + section/page)
- Output: classification, confidence, rules version, human review flag
- Contract: Pydantic model in `core/models.py`
- Display: Nothing appears in UI without audit record

## Imports at Layer Boundaries
**core/models.py** imports:
```python
from pydantic import BaseModel, ...
from enum import Enum
from datetime import datetime
```
✓ Standard library, Pydantic only

**app/streamlit_app.py** imports:
```python
from core.models import Card, Classificacao, RegistroAuditoria
import streamlit as st
import plotly, pyvis, networkx  # ✓ OK for app layer only
```

If you need to add a new core function, put it in `core/` and test it. If you need to visualize or interact with results, add it to `app/` and call `core/` functions.

## When Creating New Tests
- Test only behavior that core changes introduce/fix
- Don't test language features or constants
- For architecture: ensure `tests/test_architecture.py` still passes
- For models: add to `tests/test_models.py` or new file in `tests/`

## MCP Servers

Two MCP servers are configured for this repository:

### Python MCP
- **Location:** `~/.copilot/servers/python.json`
- **Purpose:** Direct Python execution and REPL access within Copilot sessions
- **Usage:** Run scripts, inspect `core/` models, execute tests interactively
- **Example:** `python -c "from core.models import Classificacao; print(Classificacao.__fields__)"`

### Playwright MCP
- **Location:** `~/.copilot/servers/playwright.json`
- **Purpose:** Browser automation and UI testing for Streamlit app
- **Usage:** Capture screenshots, validate Streamlit page renders, simulate user interactions
- **Note:** Requires Node.js and `mcp-playwright` npm package

Both are **enabled by default**. To use them:
- Type `/mcp` in Copilot CLI to manage servers
- Use in prompts: "Run this Python test" or "Open Streamlit and click the button"

## References
- **Manual de Frascati** — OECD definition of R&D activities
- **Lei do Bem manual** — Brazilian fiscal regulations
- **CLAUDE.md** — Full context (Portuguese); consult for edge cases
