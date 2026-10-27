# GoodLaw Deployment Checklist

## Pre-Deployment Verification ✓

### Tests
- [x] **Architecture test passes** — `core/` imports no UI frameworks
  ```bash
  pytest tests/test_architecture.py
  ```
- [x] **Model tests pass** — Fiscal conservatism rules enforced
  ```bash
  pytest tests/test_models.py
  ```
- [x] **All tests pass** (7/7)
  ```bash
  pytest
  ```

### Code Quality
- [x] **No framework imports in `core/`** — Verified by `test_architecture.py`
- [x] **Pydantic models enforce fiscal rules** — All classifications validated
- [x] **UI layer isolated** — `streamlit_app.py` only calls `core/`, no business logic

### Streamlit App
- [x] **App starts without errors**
  ```bash
  streamlit run streamlit_app.py
  ```
- [x] **Title displays correctly**: "Análise de inovação para a Lei do Bem"
- [x] **Imports work** — `core/models.ResultadoClassificacao` accessible
- [x] **Pipeline status message shows** — MVP notification + classification options

## Deployment Prerequisites

### Environment
```bash
# Install dependencies (production)
pip install -r requirements.txt

# Or with dev dependencies
pip install -r requirements.txt pytest
```

### Streamlit Configuration
Create `.streamlit/config.toml` for production:
```toml
[client]
showErrorDetails = false
[logger]
level = "warning"
[server]
port = 8501
headless = true
enableXsrfProtection = true
```

### Environment Variables (if needed)
- `PYTHONPATH`: Should point to project root (auto-set by `streamlit_app.py`)
- Optional: `BUSINESSMAP_API_KEY` (for future integration)
- Optional: `LOG_LEVEL` (default: "warning" in production)

## Deployment Steps

### 1. Local/Docker Deployment
```bash
# Clone repository
git clone https://github.com/bfmiranda/goodlaw.git
cd goodlaw

# Install dependencies
pip install -r requirements.txt

# Run tests (mandatory)
pytest

# Start Streamlit
streamlit run streamlit_app.py
```

### 2. Cloud Deployment (Streamlit Cloud / Heroku / Railway)
```bash
# Ensure these files exist and are committed
- streamlit_app.py (entry point)
- core/models.py (business logic)
- requirements.txt (dependencies)
- .streamlit/config.toml (optional, production config)
```

### 3. Docker Deployment
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Post-Deployment Validation

### Smoke Tests
- [ ] App loads without errors
- [ ] Title displays: "Análise de inovação para a Lei do Bem"
- [ ] Info box shows available classifications
- [ ] No console errors in browser dev tools

### Health Checks
```bash
# Check app endpoint
curl http://localhost:8501

# Check architecture (if tests are available)
pytest tests/test_architecture.py
```

## Known Limitations

1. **Pipeline not yet connected** — Currently MVP; shows classification options but no real analysis
2. **No authentication** — Local MVP only; add security before production
3. **No data persistence** — State resets on refresh; add session management if needed
4. **No Businessmap integration** — Awaiting ingest layer implementation

## Next Steps (Roadmap)

1. Implement `core/ingest/` for Businessmap API connection
2. Implement `core/extraction/` for entity & nature detection
3. Implement `core/rules/` classification logic
4. Add audit trail generation (`core/audit/`)
5. Add database/session persistence
6. Add authentication & authorization
7. Create FastAPI layer (`api/`) for programmatic access

## Support

For deployment issues:
- Check `tests/test_architecture.py` — core/interface boundary must hold
- Check Streamlit logs: `streamlit run streamlit_app.py --logger.level=debug`
- Consult `CLAUDE.md` for fiscal rule clarifications
- Consult `.github/copilot-instructions.md` for code conventions

---
**Last Updated:** 2026-10-27  
**Status:** Ready for deployment (MVP phase)  
**Tests:** 7/7 passing
