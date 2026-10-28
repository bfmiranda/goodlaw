#!/usr/bin/env python3
"""Script para gerar relatório completo de extração com visualizações."""
import json
import sys
from pathlib import Path
from typing import Optional

# Importar módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.extraction import ExtractorCards
from core.analytics import AnalisadorExtracao, RelatorioExtracao


def salvar_relatorio_json(relatorio: RelatorioExtracao, caminho: Path) -> None:
    """Salva relatório como JSON."""
    dados = {
        "total_cards": relatorio.total_cards,
        "natureza": {
            "distribuicao": relatorio.natureza.distribuicao,
            "distribuicao_pct": {k: round(v, 2) for k, v in relatorio.natureza.distribuicao_pct.items()},
            "confianca_media_por_natureza": {
                k: round(v, 3) for k, v in relatorio.natureza.confianca_media_por_natureza.items()
            },
            "cards_sem_natureza_definida": relatorio.natureza.cards_sem_natureza_definida,
        },
        "entidades": {
            "total_entidades_unicas": relatorio.entidades.total_entidades_unicas,
            "total_mencoes": relatorio.entidades.total_mencoes,
            "top_entidades": [
                {"entidade": f.item, "contagem": f.contagem, "percentual": round(f.percentual, 2)}
                for f in relatorio.entidades.top_entidades[:20]
            ],
            "siglas_mais_comuns": [
                {"sigla": s, "contagem": c} for s, c in relatorio.entidades.siglas_mais_comuns[:15]
            ],
        },
        "texto": {
            "comprimento_medio_cerne": round(relatorio.texto.comprimento_medio_cerne, 1),
            "comprimento_medio_titulo": round(relatorio.texto.comprimento_medio_titulo, 1),
            "comprimento_medio_descricao": round(relatorio.texto.comprimento_medio_descricao, 1),
            "cernes_vazios": relatorio.texto.cernes_vazios,
            "descricoes_vazias": relatorio.texto.descricoes_vazias,
            "palavras_comuns_top_20": [
                {"palavra": f.item, "contagem": f.contagem, "percentual": round(f.percentual, 2)}
                for f in relatorio.texto.palavras_comuns[:20]
            ],
        },
        "hierarquia": {
            "profundidade_media": round(relatorio.hierarquia.profundidade_media, 2),
            "profundidade_maxima": relatorio.hierarquia.profundidade_maxima,
            "profundidade_minima": relatorio.hierarquia.profundidade_minima,
            "distribuicao_profundidade": relatorio.hierarquia.distribuicao_profundidade,
            "cards_com_pai": relatorio.hierarquia.cards_com_pai,
            "cards_orfaos": relatorio.hierarquia.cards_orfaos,
            "cards_com_filhos": relatorio.hierarquia.cards_com_filhos,
            "cards_solitarios": relatorio.hierarquia.cards_solitarios,
            "okrs_raiz": relatorio.hierarquia.okrs_raiz,
            "initiatives_por_okr_media": round(relatorio.hierarquia.initiatives_por_okr_media, 2),
            "historias_por_initiative_media": round(relatorio.hierarquia.historias_por_initiative_media, 2),
        },
        "confianca": {
            "confianca_media_tipo": round(relatorio.confianca.confianca_media_tipo, 3),
            "confianca_media_cerne": round(relatorio.confianca.confianca_media_cerne, 3),
            "confianca_media_natureza": round(relatorio.confianca.confianca_media_natureza, 3),
            "confianca_media_hierarquia": round(relatorio.confianca.confianca_media_hierarquia, 3),
            "distribuicao_confianca_tipo": relatorio.confianca.distribuicao_confianca_tipo,
            "distribuicao_confianca_cerne": relatorio.confianca.distribuicao_confianca_cerne,
            "penalidade_media": round(relatorio.confianca.penalidade_media, 3),
            "cards_com_penalidade": relatorio.confianca.cards_com_penalidade,
        },
        "qualidade": {
            "cards_alta_confianca": relatorio.cards_de_alta_confianca,
            "cards_media_confianca": relatorio.cards_de_media_confianca,
            "cards_baixa_confianca": relatorio.cards_de_baixa_confianca,
            "pct_alta": round((relatorio.cards_de_alta_confianca / relatorio.total_cards) * 100, 2),
            "pct_media": round((relatorio.cards_de_media_confianca / relatorio.total_cards) * 100, 2),
            "pct_baixa": round((relatorio.cards_de_baixa_confianca / relatorio.total_cards) * 100, 2),
        },
    }
    
    with open(caminho, "w") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def imprimir_resumo_console(relatorio: RelatorioExtracao) -> None:
    """Imprime resumo formatado no console."""
    print("\n" + "=" * 70)
    print(" RELATÓRIO COMPLETO DE EXTRAÇÃO - GOODLAW".center(70))
    print("=" * 70 + "\n")

    print(f"📊 VISÃO GERAL")
    print(f"  Total de cards processados: {relatorio.total_cards:,}")
    print()

    print(f"🏷️  NATUREZA DA ATIVIDADE")
    for nat, cont in sorted(relatorio.natureza.distribuicao.items(), key=lambda x: -x[1])[:10]:
        pct = relatorio.natureza.distribuicao_pct.get(nat, 0)
        conf = relatorio.natureza.confianca_media_por_natureza.get(nat, 0)
        print(f"  {nat:.<40} {cont:>6} ({pct:>5.1f}%) [conf: {conf:.3f}]")
    print()

    print(f"🔤 ENTIDADES (SIGLAS/ACRÔNIMOS)")
    print(f"  Total único: {relatorio.entidades.total_entidades_unicas} | Total menções: {relatorio.entidades.total_mencoes}")
    print(f"  Top 10 siglas:")
    for sigla, cont in relatorio.entidades.siglas_mais_comuns[:10]:
        pct = (cont / relatorio.entidades.total_mencoes) * 100
        print(f"    {sigla:.<15} {cont:>5} ({pct:>5.1f}%)")
    print()

    print(f"📝 TEXTO")
    print(f"  Comprimento médio cerne:     {relatorio.texto.comprimento_medio_cerne:>6.1f} chars")
    print(f"  Comprimento médio título:    {relatorio.texto.comprimento_medio_titulo:>6.1f} chars")
    print(f"  Comprimento médio descrição: {relatorio.texto.comprimento_medio_descricao:>6.1f} chars")
    print(f"  Cernes vazios:               {relatorio.texto.cernes_vazios:>6}")
    print(f"  Descrições vazias:           {relatorio.texto.descricoes_vazias:>6}")
    print(f"  Palavras mais comuns (top 5):")
    for palavra in relatorio.texto.palavras_comuns[:5]:
        print(f"    {palavra.item:.<20} {palavra.contagem:>5}")
    print()

    print(f"🌳 HIERARQUIA")
    print(f"  Profundidade média:       {relatorio.hierarquia.profundidade_media:>6.2f}")
    print(f"  Profundidade máxima:      {relatorio.hierarquia.profundidade_maxima:>6}")
    print(f"  Profundidade mínima:      {relatorio.hierarquia.profundidade_minima:>6}")
    print(f"  Cards com pai:            {relatorio.hierarquia.cards_com_pai:>6}")
    print(f"  Cards órfãos:             {relatorio.hierarquia.cards_orfaos:>6} ({(relatorio.hierarquia.cards_orfaos/relatorio.total_cards)*100:.1f}%)")
    print(f"  Cards com filhos:         {relatorio.hierarquia.cards_com_filhos:>6}")
    print(f"  Cards solitários:         {relatorio.hierarquia.cards_solitarios:>6} ({(relatorio.hierarquia.cards_solitarios/relatorio.total_cards)*100:.1f}%)")
    print(f"  OKRs (raiz):              {relatorio.hierarquia.okrs_raiz:>6}")
    print(f"  Initiatives/OKR (média):  {relatorio.hierarquia.initiatives_por_okr_media:>6.2f}")
    print(f"  Histórias/Initiative (md): {relatorio.hierarquia.historias_por_initiative_media:>6.2f}")
    print()

    print(f"🎯 CONFIANÇA")
    print(f"  Tipo (média):              {relatorio.confianca.confianca_media_tipo:>6.3f}")
    print(f"  Cerne (média):             {relatorio.confianca.confianca_media_cerne:>6.3f}")
    print(f"  Natureza (média):          {relatorio.confianca.confianca_media_natureza:>6.3f}")
    print(f"  Hierarquia (média):        {relatorio.confianca.confianca_media_hierarquia:>6.3f}")
    print(f"  Penalidade (média):        {relatorio.confianca.penalidade_media:>6.3f}")
    print(f"  Cards com penalidade:      {relatorio.confianca.cards_com_penalidade:>6}")
    print()

    print(f"✅ QUALIDADE GERAL")
    print(f"  Alta (>0.8):               {relatorio.cards_de_alta_confianca:>6} ({(relatorio.cards_de_alta_confianca/relatorio.total_cards)*100:.1f}%)")
    print(f"  Média (0.5-0.8):           {relatorio.cards_de_media_confianca:>6} ({(relatorio.cards_de_media_confianca/relatorio.total_cards)*100:.1f}%)")
    print(f"  Baixa (<0.5):              {relatorio.cards_de_baixa_confianca:>6} ({(relatorio.cards_de_baixa_confianca/relatorio.total_cards)*100:.1f}%)")
    print()
    print("=" * 70 + "\n")


def gerar_relatorio(
    tamanho_amostra: Optional[int] = None,
    salvar_json_em: Optional[Path] = None,
) -> None:
    """Gera relatório de extração."""
    raiz = Path(__file__).parent.parent
    raw_files = raiz / "raw_files"

    print(f"📂 Carregando dados de {raw_files}...")

    extractor = ExtractorCards()
    extractor.carregar_tipos(raw_files / "CardTypes.jsonl")
    extractor.carregar_hierarquia(raw_files / "CardsLinkedCards.jsonl")

    print(f"✓ Tipos carregados")
    print(f"✓ Hierarquia carregada")

    print(f"🔄 Processando cards...")
    resultado = extractor.extrair(raw_files / "Cards.jsonl", limite=tamanho_amostra)

    print(f"✓ Extração completa: {len(resultado.cards)} cards processados")

    print(f"📈 Analisando resultados...")
    analisador = AnalisadorExtracao()
    relatorio = analisador.analisar(resultado)

    imprimir_resumo_console(relatorio)

    if salvar_json_em:
        print(f"💾 Salvando relatório em {salvar_json_em}...")
        salvar_relatorio_json(relatorio, salvar_json_em)
        print(f"✓ Relatório salvo com sucesso")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Gera relatório completo de extração com análises estatísticas"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Número de cards para processar (padrão: todos)",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Salvar relatório em JSON neste caminho",
    )

    args = parser.parse_args()

    gerar_relatorio(
        tamanho_amostra=args.sample,
        salvar_json_em=args.json,
    )
