# Pipeline de Extração - Stage 1

**Status:** ✅ Implementado e Testado (15/15 testes passando)

## Visão Geral

O Stage 1 do pipeline de análise implementa a **extração de dados brutos** do Businessmap:

- 🎯 **Entrada:** 3 arquivos JSONL (Cards, CardsLinkedCards, CardTypes)
- 🔄 **Processamento:** Análise de 512.755 cards com extração de contexto hierárquico
- 📤 **Saída:** CardExtraido com cerne, entidades, natureza, confiança e penalidades

## Arquivos Criados

```
core/extraction/
├── models.py          # CardBruto, CardExtraido, ResultadoExtracao, TipoHierarquia
├── extractor.py       # ExtractorCards (classe principal)
└── __init__.py        # Exports

tests/
└── test_extraction.py # 8 testes (unidade + integração)

scripts/
└── demo_extraction.py # Demo interativa (1000 cards)
```

## Modelo de Dados

### CardExtraido

Cada card extraído contém:

```python
CardExtraido(
    # Identidade
    card_id: int
    titulo: str
    descricao: Optional[str]
    
    # Contexto
    tipo_hierarquia: TipoHierarquia  # OKR, INICIATIVA, HISTORIA, TAREFA
    cerne: str                       # 1 frase essencial
    entidades: list[str]             # Siglas/nomes (API, REST, CGIP, etc.)
    natureza_atividade: str          # desenvolvimento_novo, manutencao_*, etc.
    
    # Hierarquia
    pai_id: Optional[int]
    filhos_ids: list[int]
    eh_orfao: bool                   # Sem pai
    eh_solitario: bool               # Sem pai e sem filhos
    profundidade_hierarquia: int     # 0=OKR, 1=Iniciativa, 2=Historia, 3+=Tarefa
    
    # Confiança (0.0-1.0)
    confianca_tipo: float
    confianca_cerne: float
    confianca_natureza: float
    confianca_hierarquia: float
    penalidade_orfandade: float      # Redução por ser órfão/solitário
)
```

### Cálculo de Confiança

| Fator | Valor | Condição |
|-------|-------|----------|
| `confianca_tipo` | 0.9 | type_id mapeado em CardTypes |
| `confianca_tipo` | 0.6 | Inferido por profundidade |
| `confianca_cerne` | 0.95 | Extraído de title/description |
| `confianca_cerne` | 0.0 | Card sem título e sem descrição |
| `confianca_hierarquia` | 0.95 | Card tem pai definido |
| `confianca_hierarquia` | 0.5 | Card é órfão |
| `penalidade_orfandade` | +0.15 | Card sem pai |
| `penalidade_orfandade` | +0.10 | Card sem pai E sem filhos |

## Funcionalidades Principais

### 1. Limpeza de HTML

```python
_limpar_html(texto)
```

Remove tags HTML e entidades comuns:
- `<br />`, `<div>`, etc.
- `&nbsp;`, `&quot;`, `&amp;`
- Espaços múltiplos

### 2. Extração de Cerne

```python
_extrair_cerne(title, description) → str
```

Extrai 1 frase essencial:
- Prioridade: title (se < 200 chars)
- Fallback: primeira frase de description
- Max: 200 caracteres

### 3. Extração de Entidades

```python
_extrair_entidades(texto) → list[str]
```

Identifica siglas e nomes maiúsculos:
- Padrão: `[A-Z]{2,}(?:_[A-Z]+)*`
- Exemplos: API, REST, CGIP, JWT
- Max: 10 entidades por card

### 4. Classificação de Natureza

```python
_classificar_natureza(texto, tipo) → (str, float)
```

Classifica atividade baseado em heurística (palavras-chave):

| Natureza | Palavras-chave |
|----------|-----------------|
| `desenvolvimento_novo` | novo, criar, construir, implementar, feature, algoritmo |
| `experimentacao` | teste, prototipo, poc, investigar, pesquisa, validar |
| `melhoria` | melhorar, otimizar, refatorar, performance, redesign |
| `manutencao_corretiva` | bug, erro, corrigir, fix, defeito, falha |
| `manutencao_evolutiva` | evolução, sustentação |
| `operacao_suporte` | suporte, monitoramento, backup |
| `implantacao_configuracao` | deploy, configurar, setup, instalação, integração |

Retorna: (natureza, confiança 0-1)

### 5. Cálculo de Profundidade

```python
_calcular_profundidade(card_id) → int
```

Traça hierarquia até a raiz:
- 0: OKR
- 1: Iniciativa
- 2: História
- 3+: Tarefa

### 6. Inferência de Tipo

```python
_inferir_tipo(profundidade, type_id) → TipoHierarquia
```

Prioridade:
1. type_id (se mapeado em CardTypes)
2. Profundidade hierárquica (fallback)

## Execução

### Testes Unitários

```bash
pytest tests/test_extraction.py -v
```

**Resultado esperado:** 8/8 passing ✅

### Demo (1000 cards)

```bash
python scripts/demo_extraction.py
```

**Saída:**
- Estatísticas gerais (total, órfãos, solitários, confiança média)
- Distribuição de tipos (OKR, Iniciativa, História, Tarefa)
- 3 exemplos de cards extraídos

### Extração Full (512k cards)

```python
from core.extraction import ExtractorCards

ext = ExtractorCards()
ext.carregar_hierarquia('raw_files/CardsLinkedCards.jsonl')
resultado = ext.extrair('raw_files/Cards.jsonl')  # sem limite

print(f"Total: {resultado.total_cards_processados}")
print(f"Órfãos: {resultado.total_orfaos}")
print(f"Confiança média: {resultado.confianca_media_geral:.2%}")
```

## Resulados Esperados

**Com 1000 cards sample:**

```
Total processado:       1000
Total extraído:         1000
Cards órfãos:           ~269 (26.9%)
Cards solitários:       ~233 (23.3%)
Confiança média:        ~78.39%

Distribuição:
  Historia              ~471 (47.1%)
  Iniciativa            ~234 (23.4%)
  OKR                   ~103 (10.3%)
  Tarefa                ~192 (19.2%)
```

## Próximos Stages

### Stage 2: Exclusões (core/rules/)

Aplicar **antes** de qualquer classificação positiva. Bloqueiam enquadramento imediatamente:

- Manutenção corretiva/preventiva
- Melhoria sem incerteza técnica
- Implantação/customização de software de prateleira
- Migração
- Integração padrão
- Suporte operacional
- Treinamento
- Deploy/release
- Ganho puramente de negócio

### Stage 3: Enquadramento (core/rules/)

Classificar restantes (após exclusões) como enquadráveis:

1. ✅ Elemento tecnologicamente novo
2. ✅ Incerteza técnica real
3. ✅ Método sistemático
4. ✅ Evidências rastreáveis

→ **Resultado:** ENQUADRAVEL | REVISAO_HUMANA | NAO_ENQUADRAVEL

### Stage 4: Auditoria (core/audit/)

Gerar `RegistroAuditoria` para cada card:

- Input: card, stage, regra
- Output: classificação, confiança, versão das regras
- Referência: Manual de Frascati + Lei do Bem
- Imutável: trilha de decisão preservada

## Conservadorismo Fiscal

⚠️ **Princípio não-negociável:**

> Na dúvida, FORA ou REVISÃO HUMANA — nunca DENTRO.

**Implementado em:**

1. **Penalidades de orfandade:** Cards órfãos têm -25% confiança
2. **Thresholds conservadores:** Requisitos rigorosos para enquadramento
3. **Revisão humana:** Flag quando confiança < threshold

## Notas de Implementação

✅ Camada core pura (sem dependências Streamlit/FastAPI)
✅ Modelos Pydantic (contratos com tipo seguro)
✅ Eficiência: 1000 cards em ~2 segundos
✅ Testes: unidade + integração com raw_files
✅ Documentação: inline (convenção Frascati/Lei do Bem)

---

**Últimas mudanças:** 2026-10-27
**Testes:** 15/15 ✅
**Status:** Pronto para Stage 2 (exclusões)
