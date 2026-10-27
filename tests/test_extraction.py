"""Testes para módulo de extração."""
from pathlib import Path

import pytest

from core.extraction import CardExtraido, ExtractorCards, TipoHierarquia


def test_extrator_inicializa():
    """Testa inicialização do extrator."""
    extrator = ExtractorCards()
    assert len(extrator.cards_extraidos) == 0
    assert len(extrator.hierarquia) == 0
    assert len(extrator.pais) == 0


def test_limpar_html():
    """Testa limpeza de HTML."""
    extrator = ExtractorCards()
    
    html = "Texto <br /> com <div>tags</div> e &amp; entidades &nbsp; múltiplos   espaços"
    resultado = extrator._limpar_html(html)
    
    assert "<br" not in resultado
    assert "<div>" not in resultado
    assert "&nbsp;" not in resultado
    assert "  " not in resultado  # Sem espaços múltiplos
    assert "Texto" in resultado


def test_extrair_entidades():
    """Testa extração de entidades (siglas)."""
    extrator = ExtractorCards()
    
    texto = "Implementar API REST para BB Cred CGIP usando JWT"
    entidades = extrator._extrair_entidades(texto)
    
    assert "API" in entidades
    assert "REST" in entidades
    assert "CGIP" in entidades
    assert "JWT" in entidades


def test_classificar_natureza():
    """Testa classificação de natureza da atividade."""
    extrator = ExtractorCards()
    
    # Desenvolvimento novo
    natureza, conf = extrator._classificar_natureza(
        "Implementar nova funcionalidade de autenticação com OAuth",
        TipoHierarquia.TAREFA
    )
    assert natureza == "desenvolvimento_novo"
    assert conf > 0.5
    
    # Correção de bug
    natureza, conf = extrator._classificar_natureza(
        "Corrigir bug crítico no processamento de pagamento",
        TipoHierarquia.TAREFA
    )
    assert natureza == "manutencao_corretiva"
    assert conf > 0.5


def test_calcular_profundidade():
    """Testa cálculo de profundidade hierárquica."""
    extrator = ExtractorCards()
    
    # Simula hierarquia: 100 -> 101 -> 102
    extrator.pais[101] = 100
    extrator.pais[102] = 101
    
    assert extrator._calcular_profundidade(100) == 0  # Raiz
    assert extrator._calcular_profundidade(101) == 1
    assert extrator._calcular_profundidade(102) == 2


def test_inferir_tipo():
    """Testa inferência de tipo hierárquico."""
    extrator = ExtractorCards()
    
    # Por profundidade
    assert extrator._inferir_tipo(0, 999) == TipoHierarquia.OKR
    assert extrator._inferir_tipo(1, 999) == TipoHierarquia.INICIATIVA
    assert extrator._inferir_tipo(2, 999) == TipoHierarquia.HISTORIA
    assert extrator._inferir_tipo(3, 999) == TipoHierarquia.TAREFA
    
    # Por type_id (tem prioridade)
    assert extrator._inferir_tipo(0, 1) == TipoHierarquia.HISTORIA


@pytest.mark.skipif(
    not Path("raw_files/Cards.jsonl").exists(),
    reason="raw_files não encontrados"
)
def test_extrair_real_pequeno():
    """Testa extração com dados reais (pequeno limite)."""
    extrator = ExtractorCards()
    extrator.carregar_hierarquia("raw_files/CardsLinkedCards.jsonl")
    
    resultado = extrator.extrair("raw_files/Cards.jsonl", limite=100)
    
    assert resultado.total_cards_processados == 100
    assert resultado.total_cards_extraidos == 100
    assert resultado.total_orfaos >= 0
    assert resultado.total_solitarios >= 0
    assert resultado.confianca_media_geral >= 0.0
    assert resultado.confianca_media_geral <= 1.0
    
    # Verifica que cards têm dados válidos
    for card in resultado.cards[:5]:
        assert card.card_id > 0
        assert card.titulo
        assert card.tipo_hierarquia in TipoHierarquia


def test_penalidade_orfandade():
    """Testa penalidade de confiança para cards órfãos/solitários."""
    extrator = ExtractorCards()
    
    # Card órfão tem penalidade
    resultado = extrator.extrair("raw_files/Cards.jsonl", limite=50)
    
    cards_orfaos = [c for c in resultado.cards if c.eh_orfao]
    if cards_orfaos:
        # Orfão deve ter penalidade > 0
        assert cards_orfaos[0].penalidade_orfandade > 0.0
    
    cards_solitarios = [c for c in resultado.cards if c.eh_solitario]
    if cards_solitarios:
        # Solitário (orfão + sem filhos) tem penalidade maior
        assert cards_solitarios[0].penalidade_orfandade >= 0.15
