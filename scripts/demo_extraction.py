#!/usr/bin/env python3
"""Script demonstrativo: Pipeline de Extração Stage 1.

Processa dados brutos do Businessmap e extrai:
- Entidades (siglas, nomes)
- Cerne (1 frase essencial)
- Natureza da atividade
- Contexto hierárquico (OKR > Iniciativa > História > Tarefa)
- Penalidade por orfandade (cards sem pai/filhos)
"""
import json
import sys
from pathlib import Path

# Adiciona raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.extraction import ExtractorCards


def main():
    print("=" * 80)
    print("PIPELINE DE EXTRAÇÃO - STAGE 1")
    print("=" * 80)
    print()

    raw_dir = Path(__file__).resolve().parent.parent / "raw_files"
    if not raw_dir.exists():
        print("❌ Pasta 'raw_files' não encontrada")
        return

    print("📁 Carregando dados brutos do Businessmap...")
    print()

    # Inicializa extrator
    extrator = ExtractorCards()

    # Carrega relações hierárquicas
    print("1️⃣  Carregando hierarquia de cards...")
    extrator.carregar_hierarquia(raw_dir / "CardsLinkedCards.jsonl")
    print(f"   ✓ Hierarquia carregada")
    print()

    # Extrai dados (limite pequeno para demonstração)
    print("2️⃣  Extraindo cerne, entidades e natureza...")
    resultado = extrator.extrair(raw_dir / "Cards.jsonl", limite=1000)
    print()

    # Estatísticas gerais
    print("📊 ESTATÍSTICAS DE EXTRAÇÃO")
    print("-" * 80)
    print(f"Total processado:       {resultado.total_cards_processados}")
    print(f"Total extraído:         {resultado.total_cards_extraidos}")
    print(f"Cards órfãos:           {resultado.total_orfaos}")
    print(f"Cards solitários:       {resultado.total_solitarios}")
    print(f"Confiança média:        {resultado.confianca_media_geral:.2%}")
    print()

    # Distribuição de tipos
    print("📈 DISTRIBUIÇÃO DE TIPOS")
    print("-" * 80)
    for tipo, contagem in sorted(resultado.distribuicao_tipos.items()):
        percentual = (contagem / resultado.total_cards_extraidos) * 100
        print(f"  {tipo:20} {contagem:6} ({percentual:5.1f}%)")
    print()

    # Exemplos de cards extraídos
    print("🔍 EXEMPLOS DE CARDS EXTRAÍDOS")
    print("-" * 80)

    # Exemplo 1: Card com boa confiança
    melhor = max(resultado.cards, key=lambda c: c.confianca_cerne)
    print(f"\n✨ Card com MELHOR CERNE:")
    print(f"   ID:              {melhor.card_id}")
    print(f"   Título:          {melhor.titulo[:60]}...")
    print(f"   Cerne:           {melhor.cerne}")
    print(f"   Tipo:            {melhor.tipo_hierarquia.value}")
    print(f"   Natureza:        {melhor.natureza_atividade}")
    print(f"   Entidades:       {', '.join(melhor.entidades[:5])}")
    print(f"   Profundidade:    {melhor.profundidade_hierarquia}")
    print(f"   Confiança:       {melhor.confianca_cerne:.2%}")
    print(f"   Orfandade:       {'SIM' if melhor.eh_orfao else 'NÃO'}")
    print(f"   Penalidade:      {melhor.penalidade_orfandade:.2%}")

    # Exemplo 2: Card órfão/solitário
    solitarios = [c for c in resultado.cards if c.eh_solitario]
    if solitarios:
        solitario = solitarios[0]
        print(f"\n🚨 Card SOLITÁRIO (órfão + sem filhos):")
        print(f"   ID:              {solitario.card_id}")
        print(f"   Título:          {solitario.titulo[:60]}...")
        print(f"   Cerne:           {solitario.cerne}")
        print(f"   Tipo:            {solitario.tipo_hierarquia.value}")
        print(f"   Profundidade:    {solitario.profundidade_hierarquia}")
        print(f"   Penalidade:      {solitario.penalidade_orfandade:.2%} ⚠️")

    # Exemplo 3: Card com entidades extraídas
    com_entidades = [c for c in resultado.cards if c.entidades]
    if com_entidades:
        exemplo = com_entidades[0]
        print(f"\n🏷️  Card COM ENTIDADES EXTRAÍDAS:")
        print(f"   ID:              {exemplo.card_id}")
        print(f"   Título:          {exemplo.titulo[:60]}...")
        print(f"   Entidades:       {', '.join(exemplo.entidades)}")
        print(f"   Natureza:        {exemplo.natureza_atividade}")

    print()
    print("=" * 80)
    print("✅ EXTRAÇÃO CONCLUÍDA")
    print("=" * 80)
    print()
    print("Próximos passos:")
    print("  1. Stage 2: Aplicar exclusões (manutenção, suporte, etc.)")
    print("  2. Stage 3: Classificar restantes como enquadráveis")
    print("  3. Gerar RegistroAuditoria para cada decisão")
    print()


if __name__ == "__main__":
    main()
