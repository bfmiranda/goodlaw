# CLAUDE.md

Ferramenta comercial (B2B) que analisa cards do Businessmap e identifica esforço enquadrável como PD&I na **Lei do Bem**, com base no **Manual de Frascati** e no manual da Lei do Bem.

## Princípio central: conservadorismo fiscal
Na dúvida, o card fica **fora** ou em **revisão humana**, nunca dentro. Falso positivo = risco de glosa para o cliente.
Esta regra está codificada em `core/models.py` (`Classificacao` rejeita "enquadrável" sem os 4 critérios ou com natureza excluída). Não enfraquecer.

## Arquitetura: núcleo/interface (regra inviolável)
- `core/`: toda a lógica (coleta, extração, exclusões, classificação, clusterização, cálculo, auditoria). Python puro + Pydantic.
- `app/`: interface Streamlit. Só chama `core/` e exibe. Sem regra de negócio, critério fiscal ou cálculo.
- `core/` **nunca** importa Streamlit, FastAPI, FastHTML, Starlette, Plotly, PyVis, Dash.
- Contratos entre camadas: modelos Pydantic de `core/models.py`.
- Garantido por `tests/test_architecture.py` — o teste deve passar sempre.
- Evolução: FastAPI entra como nova camada (`api/`) sobre o mesmo `core/`.

```
core/
  models.py      # Card, Classificacao, RegistroAuditoria
  ingest/        # coleta Businessmap
  extraction/    # entidades, cerne, natureza da atividade
  rules/         # exclusões e critérios Lei do Bem / Frascati
  clustering/
  audit/
app/             # Streamlit (só interface)
tests/           # testes do core, sem interface
```

## Pipeline
1. **Extração**: entidades, cerne (1 frase), natureza da atividade, contexto da hierarquia OKR > Iniciativa > História > Tarefa. Cards órfãos/solitários são tratados com menos confiança.
2. **Exclusões** (antes de qualquer positivo): manutenção corretiva/preventiva, melhoria sem incerteza técnica, implantação/customização de software de prateleira, migração, integração padrão, suporte, treinamento, deploy, ganho só de negócio. Filho de manutenção em iniciativa inovadora **continua excluído**.
3. **Enquadramento** (todos): elemento tecnologicamente novo; incerteza técnica real; método sistemático; evidências rastreáveis.

## Auditoria
Toda etapa gera `RegistroAuditoria`: card, etapa, regra, referência normativa (manual + seção/página), trecho do card, resultado, confiança, versão das regras, revisão humana. Nada aparece no painel sem registro.

## Comandos
```
pip install -r requirements.txt
pytest
streamlit run app/streamlit_app.py
```

## Convenções
- Código e nomes de domínio em português; comentários sucintos.
- Todo código novo indica sua camada e vem com teste em `tests/` quando for `core/`.
- Construção incremental: o próximo passo mínimo.
