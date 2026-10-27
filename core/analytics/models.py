"""Camada: core. Modelos para análise e estatísticas de dados extraídos."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field


@dataclass
class FrequenciaItem:
    """Item de frequência para ordenação."""
    item: str
    contagem: int
    percentual: float = 0.0


@dataclass
class EstatisticasNatureza:
    """Estatísticas sobre natureza da atividade."""
    total_cards: int
    distribuicao: dict[str, int] = field(default_factory=dict)
    distribuicao_pct: dict[str, float] = field(default_factory=dict)
    
    confianca_media_por_natureza: dict[str, float] = field(default_factory=dict)
    cards_sem_natureza_definida: int = 0


@dataclass
class EstatisticasEntidades:
    """Estatísticas sobre entidades extraídas."""
    total_entidades_unicas: int = 0
    total_mencoes: int = 0
    
    top_entidades: list[FrequenciaItem] = field(default_factory=list)
    entidades_por_categoria: dict[str, int] = field(default_factory=dict)
    
    siglas_mais_comuns: list[tuple[str, int]] = field(default_factory=list)


@dataclass
class EstatisticasTexto:
    """Estatísticas sobre textos (cerne, descrição)."""
    comprimento_medio_cerne: float = 0.0
    comprimento_medio_titulo: float = 0.0
    comprimento_medio_descricao: float = 0.0
    
    cernes_vazios: int = 0
    descricoes_vazias: int = 0
    
    palavras_comuns: list[FrequenciaItem] = field(default_factory=list)


@dataclass
class EstatisticasHierarquia:
    """Estatísticas sobre estrutura hierárquica."""
    profundidade_media: float = 0.0
    profundidade_maxima: int = 0
    profundidade_minima: int = 0
    
    distribuicao_profundidade: dict[int, int] = field(default_factory=dict)
    
    cards_com_pai: int = 0
    cards_orfaos: int = 0
    cards_com_filhos: int = 0
    cards_solitarios: int = 0
    
    okrs_raiz: int = 0
    initiatives_por_okr_media: float = 0.0
    historias_por_initiative_media: float = 0.0


@dataclass
class EstatisticasConfianca:
    """Estatísticas sobre confiança nas classificações."""
    confianca_media_tipo: float = 0.0
    confianca_media_cerne: float = 0.0
    confianca_media_natureza: float = 0.0
    confianca_media_hierarquia: float = 0.0
    
    distribuicao_confianca_tipo: dict[str, int] = field(default_factory=dict)
    distribuicao_confianca_cerne: dict[str, int] = field(default_factory=dict)
    
    penalidade_media: float = 0.0
    cards_com_penalidade: int = 0


class RelatorioExtracao(BaseModel):
    """Relatório completo de análise da extração."""
    total_cards: int
    
    natureza: EstatisticasNatureza
    entidades: EstatisticasEntidades
    texto: EstatisticasTexto
    hierarquia: EstatisticasHierarquia
    confianca: EstatisticasConfianca
    
    cards_de_alta_confianca: int = 0
    cards_de_media_confianca: int = 0
    cards_de_baixa_confianca: int = 0
