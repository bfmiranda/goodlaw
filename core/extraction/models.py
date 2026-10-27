"""Camada: core. Modelos de dados para o estágio de extração."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TipoHierarquia(str, Enum):
    """Tipos de card conforme Businessmap."""
    OKR = "okr"
    INICIATIVA = "iniciativa"
    HISTORIA = "historia"
    TAREFA = "tarefa"
    DESCONHECIDO = "desconhecido"


class CardBruto(BaseModel):
    """Card extraído diretamente do Businessmap (raw)."""
    card_id: int
    title: str
    description: Optional[str] = None
    type_id: Optional[int] = None
    board_id: int
    created_at: datetime
    last_modified: datetime
    archived_at: Optional[datetime] = None
    discarded_at: Optional[datetime] = None
    state: str  # "active", "archived", etc.


class ReferenciaHierarquica(BaseModel):
    """Referência a um card pai/filho."""
    card_id: int
    link_type: str  # "parent", "child"


class CardExtraido(BaseModel):
    """Card após extração: entidades, cerne, natureza, contexto."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    card_id: int
    titulo: str
    descricao: Optional[str] = None
    tipo_hierarquia: TipoHierarquia
    
    # Extração
    cerne: Optional[str] = None  # 1 frase: essência do card
    entidades: list[str] = Field(default_factory=list)  # Entidades extraídas
    natureza_atividade: Optional[str] = None  # Categoria da atividade
    
    # Contexto hierárquico
    pai_id: Optional[int] = None
    filhos_ids: list[int] = Field(default_factory=list)
    eh_orfao: bool = False  # Sem pai identificado
    eh_solitario: bool = False  # Sem pai e sem filhos
    profundidade_hierarquia: int = 0  # 0 = OKR, 1 = Iniciativa, etc.
    
    # Metadados de confiança
    confianca_tipo: float = 0.0  # 0-1: confiança na classificação de tipo
    confianca_cerne: float = 0.0  # 0-1: confiança na extração do cerne
    confianca_natureza: float = 0.0  # 0-1: confiança na natureza
    confianca_hierarquia: float = 0.0  # 0-1: confiança na posição hierárquica
    
    # Redução de confiança por orfandade
    penalidade_orfandade: float = 0.0  # 0-1: redução por ser órfão/solitário
    
    # Timestamps
    extraido_em: datetime = Field(default_factory=datetime.utcnow)
    versao_pipeline: str = "1.0"


class ResultadoExtracao(BaseModel):
    """Resultado da etapa de extração (agregado)."""
    total_cards_processados: int
    total_cards_extraidos: int
    total_orfaos: int
    total_solitarios: int
    
    cards: list[CardExtraido]
    
    # Estatísticas
    confianca_media_geral: float
    distribuicao_tipos: dict[str, int]  # {tipo: contagem}
    
    extraido_em: datetime = Field(default_factory=datetime.utcnow)
