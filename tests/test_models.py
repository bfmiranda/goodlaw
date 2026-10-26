import pytest
from pydantic import ValidationError

from core.models import (
    Card, Classificacao, Criterio, NaturezaAtividade as N, NivelHierarquia, ResultadoClassificacao as R,
)

TODOS = {c: True for c in Criterio}


def _cls(**kw):
    base = dict(card_id="1", cerne="x", natureza=N.DESENVOLVIMENTO_NOVO, criterios=TODOS,
                confianca=0.9, resultado=R.ENQUADRAVEL, versao_regras="0.1")
    return Classificacao(**{**base, **kw})


def test_enquadravel_valido():
    assert _cls().resultado == R.ENQUADRAVEL


def test_enquadravel_sem_todos_criterios_falha():
    with pytest.raises(ValidationError):
        _cls(criterios={**TODOS, Criterio.INCERTEZA_TECNICA: False})


def test_manutencao_corretiva_nunca_enquadravel():
    with pytest.raises(ValidationError):
        _cls(natureza=N.MANUTENCAO_CORRETIVA)


def test_motivo_exclusao_impede_enquadravel():
    with pytest.raises(ValidationError):
        _cls(motivo_exclusao="customização de ERP")


def test_nao_enquadravel_sem_criterios_ok():
    assert _cls(criterios={}, resultado=R.NAO_ENQUADRAVEL).resultado == R.NAO_ENQUADRAVEL


def test_orfao_e_solitario():
    tarefa = Card(id="t", empresa_id="e", titulo="t", nivel=NivelHierarquia.TAREFA)
    okr = Card(id="o", empresa_id="e", titulo="o", nivel=NivelHierarquia.OKR, filhos_ids=["i"])
    assert tarefa.orfao and tarefa.solitario
    assert not okr.orfao and not okr.solitario
