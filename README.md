# GoodLaw

Ferramenta B2B que classifica tarefas de desenvolvimento como elegíveis para incentivos fiscais R&D sob a **Lei do Bem** (Brasil), usando análise baseada no **Manual de Frascati**.

## Visão Geral

GoodLaw analisa cards do Businessmap e determina se o esforço de engenharia se qualifica como pesquisa, desenvolvimento e inovação (PD&I) sob critérios fiscais brasileiros:

- ✅ Elemento tecnologicamente novo
- ✅ Incerteza técnica real  
- ✅ Método sistemático
- ✅ Evidências rastreáveis

**Princípio fiscal:** Na dúvida, **fora** ou **revisão humana** — nunca dentro. Falsos positivos arriscam glosa para o cliente.

## Início Rápido

### Instalação
```bash
git clone https://github.com/bfmiranda/goodlaw.git
cd goodlaw
pip install -r requirements.txt
```

### Testes
```bash
pytest                    # Suite completa (7 testes)
pytest -k test_core      # Apenas testes de core
```

### Desenvolvimento
```bash
streamlit run streamlit_app.py
# App inicia em http://localhost:8501
```

## Arquitetura

**Camada Core** (`core/`)
- Toda a lógica de negócio: extração, classificação, auditoria
- Python + Pydantic, sem dependências de UI
- Garantida por `tests/test_architecture.py`

**Camada App** (`app/` / root)
- Interface Streamlit
- Apenas exibe dados de `core/`, sem lógica

```
core/
├── models.py           # Contratos Pydantic
├── ingest/            # Coleta Businessmap
├── extraction/        # Análise de tarefas
├── rules/             # Classificação Lei do Bem/Frascati
├── clustering/        # Agrupamento
└── audit/             # Trilha de auditoria
```

## Estado Atual (MVP)

✅ **Pronto para Deploy**
- 7/7 testes passando
- Barreira core/app validada
- Documentação completa

⏳ **Pendente**
- Integração Businessmap (ingest/)
- Análise de tarefas (extraction/)
- Lógica de classificação (rules/)

## Documentação

- **[CLAUDE.md](./CLAUDE.md)** — Contexto técnico + decisões arquiteturais (para LLMs)
- **[.github/copilot-instructions.md](./.github/copilot-instructions.md)** — Guia Copilot CLI (builds, tests, MCP)
- **[.github/DEPLOYMENT.md](./.github/DEPLOYMENT.md)** — Procedimentos de deployment

## Desenvolvimento

### Convenções

- Código em **português** (domínio + nomenclatura)
- Comentários sucintos (explique *por quê*, não *o quê*)
- Toda mudança em `core/` exige teste em `tests/`
- Construção incremental (um commit = um passo lógico)

### Rodando Testes

```bash
# Todos
pytest -v

# Arquitetura (deve passar sempre)
pytest tests/test_architecture.py

# Modelos e regras
pytest tests/test_models.py

# Coverage
pytest --cov=core tests/
```

## Deployment

### Local
```bash
streamlit run streamlit_app.py
```

### Docker
```bash
docker build -t goodlaw .
docker run -p 8501:8501 goodlaw
```

### Streamlit Cloud
```bash
git push origin main
# Auto-deploy para cloud.streamlit.app
```

Veja [.github/DEPLOYMENT.md](./.github/DEPLOYMENT.md) para checklist completo.

## Referências

- **Manual de Frascati** (OECD) — Definição de atividades R&D
- **Lei do Bem** — Regulamentação fiscal brasileira
- **Lei nº 11.196/2005** — Lei de Incentivos Fiscais (Brasil)

## Suporte

- 🛠️ Perguntas técnicas? Veja [CLAUDE.md](./CLAUDE.md)
- 🚀 Deploy? Veja [.github/DEPLOYMENT.md](./.github/DEPLOYMENT.md)
- 💡 Convenções de código? Veja [.github/copilot-instructions.md](./.github/copilot-instructions.md)

## Licença

[Adicionar licença conforme apropriado]

---

**Status:** MVP / Teste de Conceito  
**Último Update:** 2026-10-27  
**Testes:** ✅ 7/7 passando
