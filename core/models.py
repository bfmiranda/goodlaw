"""Camada: core. Contratos de dados entre núcleo e interfaces.

Proibido importar bibliotecas de interface aqui (ver tests/test_architecture.py).
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class NivelHierarquia(str, Enum):
    OKR = "okr"
    INICIATIVA = "iniciativa"
    HISTORIA = "historia"
    TAREFA = "tarefa"
    DESCONHECIDO = "desconhecido"


class NaturezaAtividade(str, Enum):
    DESENVOLVIMENTO_NOVO = "desenvolvimento_novo"
    EXPERIMENTACAO = "experimentacao"
    MELHORIA = "melhoria"
    MANUTENCAO_CORRETIVA = "manutencao_corretiva"
    MANUTENCAO_EVOLUTIVA = "manutencao_evolutiva"
    OPERACAO_SUPORTE = "operacao_suporte"
    IMPLANTACAO_CONFIGURACAO = "implantacao_configuracao"
    INDEFINIDA = "indefinida"


# Naturezas que nunca podem ser enquadradas (conservadorismo fiscal).
NATUREZAS_EXCLUIDAS = frozenset({
    NaturezaAtividade.MANUTENCAO_CORRETIVA,
    NaturezaAtividade.OPERACAO_SUPORTE,
    NaturezaAtividade.IMPLANTACAO_CONFIGURACAO,
    NaturezaAtividade.INDEFINIDA,
})


class ResultadoClassificacao(str, Enum):
    ENQUADRAVEL = "enquadravel"
    REVISAO_HUMANA = "revisao_humana"
    NAO_ENQUADRAVEL = "nao_enquadravel"


class Criterio(str, Enum):
    ELEMENTO_NOVO = "elemento_tecnologicamente_novo"
    INCERTEZA_TECNICA = "incerteza_tecnica"
    METODO_SISTEMATICO = "metodo_sistematico"
    EVIDENCIAS = "evidencias_rastreaveis"


class Etapa(str, Enum):
    COLETA = "coleta"
    EXTRACAO = "extracao"
    EXCLUSAO = "exclusao"
    ENQUADRAMENTO = "enquadramento"
    CLUSTERIZACAO = "clusterizacao"


class Card(BaseModel):
    id: str
    empresa_id: str
    titulo: str
    descricao: str = ""
    nivel: NivelHierarquia = NivelHierarquia.DESCONHECIDO
    pais_ids: list[str] = Field(default_factory=list)
    filhos_ids: list[str] = Field(default_factory=list)
    relacionados_ids: list[str] = Field(default_factory=list)
    coletado_em: datetime = Field(default_factory=_agora)

    @property
    def orfao(self) -> bool:
        """Sem pai (OKR é topo, não conta como órfão)."""
        return not self.pais_ids and self.nivel != NivelHierarquia.OKR

    @property
    def solitario(self) -> bool:
        return not (self.pais_ids or self.filhos_ids or self.relacionados_ids)


class Classificacao(BaseModel):
    card_id: str
    cerne: str
    natureza: NaturezaAtividade
    entidades: dict[str, list[str]] = Field(default_factory=dict)
    criterios: dict[Criterio, bool] = Field(default_factory=dict)
    motivo_exclusao: str | None = None
    evidencias_faltantes: list[str] = Field(default_factory=list)
    confianca: float = Field(ge=0.0, le=1.0)
    resultado: ResultadoClassificacao
    versao_regras: str

    @model_validator(mode="after")
    def _conservadorismo_fiscal(self) -> "Classificacao":
        if self.resultado != ResultadoClassificacao.ENQUADRAVEL:
            return self
        faltando = [c.value for c in Criterio if not self.criterios.get(c, False)]
        if faltando:
            raise ValueError(f"Enquadrável exige todos os critérios; faltando: {faltando}")
        if self.natureza in NATUREZAS_EXCLUIDAS:
            raise ValueError(f"Natureza '{self.natureza.value}' não pode ser enquadrável")
        if self.motivo_exclusao:
            raise ValueError("Card com motivo de exclusão não pode ser enquadrável")
        return self


class RevisaoHumana(BaseModel):
    revisor: str
    revisado_em: datetime = Field(default_factory=_agora)
    confirmou: bool
    resultado_final: ResultadoClassificacao
    comentario: str = ""


class RegistroAuditoria(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    card_id: str
    coletado_em: datetime
    etapa: Etapa
    regra: str
    referencia_normativa: str | None = None  # ex.: "Manual Lei do Bem, p. 32"
    trecho_card: str
    resultado: str
    confianca: float = Field(ge=0.0, le=1.0)
    versao_regras: str
    criado_em: datetime = Field(default_factory=_agora)
    revisao: RevisaoHumana | None = None
