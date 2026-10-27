# CLAUDE.md

Ferramenta comercial (B2B) que analisa cards do Businessmap e identifica esforço enquadrável como PD&I na **Lei do Bem**, com base no **Manual de Frascati** e no manual da Lei do Bem.

## Princípio Central: Conservadorismo Fiscal
Na dúvida, o card fica **fora** ou em **revisão humana**, nunca dentro. Falso positivo = risco de glosa para o cliente.
Esta regra está codificada em `core/models.py` (`Classificacao` rejeita "enquadrável" sem os 4 critérios ou com natureza excluída). **Não enfraquecer.**

## Arquitetura: Núcleo/Interface (Regra Inviolável)

**Core Layer** (`core/`)
- Contém: toda a lógica de negócio (coleta, extração, exclusões, classificação, clusterização, auditoria)
- Tech: Python puro + Pydantic (sem dependências de framework)
- Importações proibidas: `streamlit`, `fastapi`, `fasthtml`, `starlette`, `plotly`, `pyvis`, `dash`, `app`
- Garantia: `tests/test_architecture.py` valida esta barreira a cada execução
- Evolução: FastAPI entra como camada nova (`api/`) sobre o mesmo `core/` sem modificações

**App Layer** (`app/`)
- Contém: interface Streamlit apenas
- Faz: chama funções de `core/`, exibe resultados
- Nunca: implementa regras de negócio, critérios fiscais ou cálculos
- Princípio: UI pura — toda lógica vive em `core/`

**Contratos entre camadas:** Modelos Pydantic em `core/models.py`

```
goodlaw/
├── core/                           # Camada: Lógica de negócio
│   ├── models.py                   # Card, Classificacao, RegistroAuditoria, enums
│   ├── ingest/                     # Coleta de dados (Businessmap)
│   ├── extraction/                 # Extração: entidades, cerne, natureza da atividade
│   ├── rules/                      # Lei do Bem + Frascati (exclusões e classificação)
│   ├── clustering/                 # Agrupamento de tarefas
│   └── audit/                      # Trilha de auditoria
├── app/                            # Camada: Interface Streamlit
│   └── streamlit_app.py            # Entrada da app (no root atualmente)
├── tests/                          # Testes (sem dependências de interface)
│   ├── test_architecture.py        # Valida barreira core/app
│   ├── test_models.py              # Modelos Pydantic e regras
│   └── ...
├── .github/
│   ├── copilot-instructions.md     # Guia para Copilot CLI
│   ├── DEPLOYMENT.md               # Checklist de deployment
│   └── ...
└── CLAUDE.md                       # Este arquivo (contexto para IA)
```

## Pipeline de Classificação (Ordem Importa)

### 1. Extração (Confidence Lower on Orphans)
- Entidades extraídas
- Cerne do card (1 frase)
- Natureza da atividade identificada
- Contexto hierárquico: OKR → Iniciativa → História → Tarefa
- **Nota:** Cards órfãos/solitários = confiança reduzida

### 2. Exclusões (Aplicadas Antes de Qualquer Positivo)
Bloqueiam enquadramento imediatamente:
- Manutenção corretiva/preventiva
- Melhoria sem incerteza técnica
- Implantação/customização de software de prateleira
- Migração
- Integração padrão
- Suporte operacional
- Treinamento
- Deploy/release
- Ganho puramente de negócio

**Regra crítica:** Filho de tarefa de manutenção **continua excluído**, mesmo se a iniciativa pai é inovadora.

### 3. Enquadramento (Restante)
Todas as 4 condições devem ser atendidas:
1. Elemento tecnologicamente novo
2. Incerteza técnica real
3. Método sistemático
4. Evidências rastreáveis

## Auditoria (Garantia de Rastreabilidade)

Toda etapa de processamento gera `RegistroAuditoria`:
- **Input:** card, etapa de pipeline, regra aplicada
- **Referência normativa:** Manual de Frascati (seção/página) + Lei do Bem
- **Output:** classificação, confiança (0-10), versão das regras
- **Markup:** trecho do card analisado, flag de revisão humana
- **Contrato:** Pydantic model em `core/models.py`
- **Display:** Nada aparece no painel sem registro de auditoria

## Comandos Principais

```bash
# Setup
pip install -r requirements.txt

# Testes
pytest                              # Suite completa (7 testes)
pytest tests/test_architecture.py  # Valida barreira core/app
pytest tests/test_models.py        # Modelos e regras

# Desenvolvimento
streamlit run streamlit_app.py     # Inicia app em http://localhost:8501

# Verificações
pytest -v                          # Output verboso
pytest --tb=short                  # Erros resumidos
```

## Convenções de Código

### Linguagem & Domínio
- Código e nomes de domínio em **português** (ex: `NaturezaAtividade`, `ResultadoClassificacao`)
- Comentários **sucintos**: explique *por quê*, não *o quê*
- Decisões fiscais/regulatórias documentadas inline com referência (ex: "Manual de Frascati §3.2")

### Estrutura de Camadas
- Novo arquivo? Indique sua camada no cabeçalho:
  ```python
  """Camada: core. Extração de entidades..."""
  ```
  ou
  ```python
  """Camada: app. Interface Streamlit..."""
  ```

### Testes
- ✓ Toda mudança em `core/` exige teste em `tests/`
- ✓ Testes são o contrato entre camadas
- ✓ Nenhuma dependência Streamlit/framework em `tests/`
- ✓ `test_architecture.py` deve passar **sempre**
- ✓ Teste só comportamentos que sua mudança introduz/corrige; não teste features de linguagem, constantes ou re-exports

### Versionamento de Modelos
- `RegistroAuditoria` sempre inclui `versao_regras`
- Quando regras mudam → atualiza versão
- Trilha de auditoria permanece imutável (histórico preservado)

### Construção Incremental
- **Um commit = um passo lógico mínimo**
- Novo feature em `core/` → teste em `tests/` → integração em `app/` (cada um em commit separado se grande)
- Evitar mudanças não-relacionadas

## Testes de Arquitetura (test_core_nao_importa_interface)

Este teste **nunca deve falhar**:
```python
def test_core_nao_importa_interface():
    # Verifica que core/ não importa: streamlit, fastapi, ...
    # Garante a barreira de camadas
    assert not violacoes, f"core/ importando interface: {violacoes}"
```

Se falhar:
1. Remove importação proibida de `core/`
2. Move lógica para `app/` se necessário
3. Commit como correção de arquitetura

## Status Atual (MVP)

✅ **Pronto para deploy:**
- 7/7 testes passando
- Barreira core/app validada
- Homepage: "Análise de inovação para a Lei do Bem"
- Documentação: `.github/copilot-instructions.md` + `.github/DEPLOYMENT.md`

⏳ **Pendente:**
- Implementação de `core/ingest/` (conexão Businessmap)
- Implementação de `core/extraction/` (análise de cards)
- Implementação de `core/rules/` (lógica de classificação)
- Integração em `app/` após validação

## Referências

- **Manual de Frascati** — OECD definition of R&D activities (consulte para critérios técnicos)
- **Lei do Bem Manual** — Regulamentação fiscal brasileira (consulte para exclusões)
- **.github/copilot-instructions.md** — Guia para Copilot CLI (MCP servers, convenções, tests)
- **.github/DEPLOYMENT.md** — Checklist e procedimentos de deployment
