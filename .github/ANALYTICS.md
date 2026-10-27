# Análise de Extração (core/analytics)

## Visão Geral

Módulo de análise estatística que processa resultados da **etapa de extração** (Stage 1) e gera relatórios detalhados sobre:

- **Natureza da Atividade**: Distribuição de tipos (desenvolvimento novo, manutenção, etc.)
- **Entidades Extraídas**: Siglas, entidades técnicas, palavras-chave
- **Análise de Texto**: Comprimentos, palavras-chave mais comuns
- **Estrutura Hierárquica**: Profundidade, relacionamentos pai-filho, órfãos
- **Confiança**: Distribuição de scores de confiança por dimensão
- **Qualidade Geral**: Percentual de cards de alta/média/baixa confiança

## Estrutura

```
core/analytics/
├── models.py      # Pydantic models para estatísticas
├── analyzer.py    # Classe AnalisadorExtracao
└── __init__.py    # Exports
```

## Uso

### 1. Básico: Analisar Resultado de Extração

```python
from core.extraction import ExtractorCards
from core.analytics import AnalisadorExtracao

# Processar cards
extractor = ExtractorCards()
extractor.carregar_tipos("raw_files/CardTypes.jsonl")
extractor.carregar_hierarquia("raw_files/CardsLinkedCards.jsonl")
resultado = extractor.extrair("raw_files/Cards.jsonl", limite=5000)

# Analisar
analisador = AnalisadorExtracao()
relatorio = analisador.analisar(resultado)

# Usar relatório
print(f"Total: {relatorio.total_cards}")
print(f"Alta confiança: {relatorio.cards_de_alta_confianca}")
```

### 2. Gerar Relatório em JSON

```bash
python scripts/gerar_relatorio.py --sample 5000 --json data/relatorio.json
```

Gera arquivo JSON com:
- Distribuição de natureza (contagem + %)
- Top entidades (siglas)
- Palavras-chave mais comuns
- Hierarquia (profundidade, relacionamentos)
- Distribuição de confiança
- Qualidade geral

### 3. Visualizar Dashboard Streamlit

```bash
streamlit run app/extraction_dashboard.py
```

Renderiza:
- 📊 Gráficos de pizza (natureza, qualidade)
- 📈 Barras (siglas, palavras-chave)
- 🌳 Análise hierárquica
- 🎯 Distribuição de confiança
- 💡 Insights e recomendações

## Modelos

### `RelatorioExtracao`

Agregado principal contendo:
- `total_cards`: int — total processado
- `natureza`: EstatisticasNatureza
- `entidades`: EstatisticasEntidades
- `texto`: EstatisticasTexto
- `hierarquia`: EstatisticasHierarquia
- `confianca`: EstatisticasConfianca
- `cards_de_*_confianca`: int — classificação por qualidade

### `EstatisticasNatureza`

```python
{
    "distribuicao": {"desenvolvimento_novo": 1404, ...},
    "distribuicao_pct": {"desenvolvimento_novo": 28.1, ...},
    "confianca_media_por_natureza": {"desenvolvimento_novo": 0.670, ...},
    "cards_sem_natureza_definida": 1613,
}
```

### `EstatisticasEntidades`

```python
{
    "total_entidades_unicas": 3041,
    "total_mencoes": 14838,
    "top_entidades": [
        {"entidade": "BB", "contagem": 721, "percentual": 4.9},
        ...
    ],
    "siglas_mais_comuns": [("BB", 721), ("PARA", 412), ...],
}
```

### `EstatisticasTexto`

```python
{
    "comprimento_medio_cerne": 63.0,
    "comprimento_medio_titulo": 63.2,
    "comprimento_medio_descricao": 1502.0,
    "cernes_vazios": 2,
    "descricoes_vazias": 372,
    "palavras_comuns": [
        {"palavra": "como", "contagem": 3382, "percentual": ...},
        ...
    ],
}
```

### `EstatisticasHierarquia`

```python
{
    "profundidade_media": 1.43,
    "profundidade_maxima": 7,
    "cards_com_pai": 3243,
    "cards_orfaos": 1757,
    "cards_solitarios": 1538,
    "okrs_raiz": 573,
    "initiatives_por_okr_media": 23.81,
    "historias_por_initiative_media": 10.77,
}
```

### `EstatisticasConfianca`

```python
{
    "confianca_media_tipo": 0.815,
    "confianca_media_cerne": 0.950,
    "confianca_media_natureza": 0.514,
    "confianca_media_hierarquia": 0.792,
    "penalidade_media": 0.083,
    "cards_com_penalidade": 1757,
}
```

## Insights sobre Extração (5000 cards)

✓ **Pontos Fortes:**
- Cerne bem estruturado (95% confiança)
- Tipagem clara (81.5% confiança)
- 41.6% dos cards em alta qualidade
- 3,041 entidades únicas extraídas

⚠️ **Pontos de Atenção:**
- 32.3% "indefinida" (sem classificação clara)
- 35.1% órfãos (sem pai identificado)
- 30.8% solitários (sem pai e sem filhos)
- 7.4% descrições vazias

## Próximas Etapas

### Stage 2 (Exclusões)
Usar estatísticas para ajustar regras de exclusão Lei do Bem:
- Cards indefinidos precisam revisão
- Órfãos podem indicar dados incompletos
- Palavras-chave podem refinar heurísticas de natureza

### Caching
Para 512k cards:
- Considerar cache de ResultadoExtracao serializado
- Gerar apenas quando raw_files mudam
- Versionar cache por extractor versão + hash de tipos

### Clustering
Usar análise de entidades para agrupar cards por domínio:
- BB + PARA + PJ indicam contexto de crédito
- IA + UX + CLASS indicam contexto de produto
- Facilitar auditoria por domínio

## Testes

```bash
pytest tests/test_analytics.py -v
```

6 testes cobrem:
- Análise de natureza
- Extração de entidades
- Hierarquia
- Confiança
- Classificação por qualidade
- Estrutura do relatório
