"""Testes para o módulo de análise (core/analytics)."""
import pytest

from core.extraction import CardExtraido, ResultadoExtracao, TipoHierarquia
from core.analytics import AnalisadorExtracao, RelatorioExtracao


@pytest.fixture
def cards_exemplo():
    """Cria alguns cards de exemplo para teste."""
    return [
        CardExtraido(
            card_id=1,
            titulo="Implementar API REST",
            descricao="Criar API REST com autenticação JWT",
            cerne="Implementar API REST com JWT",
            entidades=["API", "JWT"],
            natureza_atividade="desenvolvimento_novo",
            confianca_natureza=0.8,
            confianca_tipo=0.9,
            confianca_cerne=0.95,
            confianca_hierarquia=0.95,
            tipo_hierarquia=TipoHierarquia.TAREFA,
            profundidade_hierarquia=3,
            pai_id=2,
            filhos_ids=[],
            eh_orfao=False,
            eh_solitario=True,
            penalidade_orfandade=0.0,
        ),
        CardExtraido(
            card_id=2,
            titulo="Corrigir bug crítico",
            descricao="Fix no módulo de login",
            cerne="Corrigir bug no login",
            entidades=["LOGIN"],
            natureza_atividade="manutencao_corretiva",
            confianca_natureza=0.9,
            confianca_tipo=0.9,
            confianca_cerne=0.95,
            confianca_hierarquia=0.95,
            tipo_hierarquia=TipoHierarquia.HISTORIA,
            profundidade_hierarquia=2,
            pai_id=3,
            filhos_ids=[1],
            eh_orfao=False,
            eh_solitario=False,
            penalidade_orfandade=0.0,
        ),
        CardExtraido(
            card_id=4,
            titulo="Card órfão",
            descricao="Card sem pai",
            cerne="Card órfão sem pai",
            entidades=[],
            natureza_atividade="indefinida",
            confianca_natureza=0.1,
            confianca_tipo=0.6,
            confianca_cerne=0.95,
            confianca_hierarquia=0.5,
            tipo_hierarquia=TipoHierarquia.TAREFA,
            profundidade_hierarquia=0,
            pai_id=None,
            filhos_ids=[],
            eh_orfao=True,
            eh_solitario=True,
            penalidade_orfandade=0.15,
        ),
    ]


def test_analisar_natureza(cards_exemplo):
    """Testa análise de natureza da atividade."""
    resultado = ResultadoExtracao(
        cards=cards_exemplo,
        tempo_processamento=0.0,
        total_cards_processados=3,
        total_cards_extraidos=3,
        total_orfaos=1,
        total_solitarios=2,
        confianca_media_geral=0.75,
        distribuicao_tipos={"tarefa": 2, "historia": 1},
    )
    analisador = AnalisadorExtracao()
    
    relatorio = analisador.analisar(resultado)
    
    assert relatorio.natureza.total_cards == 3
    assert "desenvolvimento_novo" in relatorio.natureza.distribuicao
    assert relatorio.natureza.distribuicao["desenvolvimento_novo"] == 1
    assert relatorio.natureza.distribuicao["indefinida"] == 1
    assert relatorio.natureza.cards_sem_natureza_definida == 1


def test_analisar_entidades(cards_exemplo):
    """Testa análise de entidades."""
    resultado = ResultadoExtracao(
        cards=cards_exemplo,
        tempo_processamento=0.0,
        total_cards_processados=3,
        total_cards_extraidos=3,
        total_orfaos=1,
        total_solitarios=2,
        confianca_media_geral=0.75,
        distribuicao_tipos={"tarefa": 2, "historia": 1},
    )
    analisador = AnalisadorExtracao()
    
    relatorio = analisador.analisar(resultado)
    
    assert relatorio.entidades.total_entidades_unicas == 3
    assert relatorio.entidades.total_mencoes == 3
    siglas = [s[0] for s in relatorio.entidades.siglas_mais_comuns]
    assert "API" in siglas
    assert "JWT" in siglas
    assert "LOGIN" in siglas


def test_analisar_hierarquia(cards_exemplo):
    """Testa análise de hierarquia."""
    resultado = ResultadoExtracao(
        cards=cards_exemplo,
        tempo_processamento=0.0,
        total_cards_processados=3,
        total_cards_extraidos=3,
        total_orfaos=1,
        total_solitarios=2,
        confianca_media_geral=0.75,
        distribuicao_tipos={"tarefa": 2, "historia": 1},
    )
    analisador = AnalisadorExtracao()
    
    relatorio = analisador.analisar(resultado)
    
    assert relatorio.hierarquia.cards_com_pai == 2
    assert relatorio.hierarquia.cards_orfaos == 1
    assert relatorio.hierarquia.cards_solitarios == 2
    assert relatorio.hierarquia.cards_com_filhos == 1
    assert relatorio.hierarquia.profundidade_maxima == 3
    assert relatorio.hierarquia.profundidade_minima == 0


def test_analisar_confianca(cards_exemplo):
    """Testa análise de confiança."""
    resultado = ResultadoExtracao(
        cards=cards_exemplo,
        tempo_processamento=0.0,
        total_cards_processados=3,
        total_cards_extraidos=3,
        total_orfaos=1,
        total_solitarios=2,
        confianca_media_geral=0.75,
        distribuicao_tipos={"tarefa": 2, "historia": 1},
    )
    analisador = AnalisadorExtracao()
    
    relatorio = analisador.analisar(resultado)
    
    assert relatorio.confianca.confianca_media_tipo > 0
    assert relatorio.confianca.confianca_media_cerne == 0.95
    assert relatorio.confianca.cards_com_penalidade == 1
    assert relatorio.confianca.penalidade_media > 0


def test_classificacao_qualidade(cards_exemplo):
    """Testa classificação por qualidade de confiança."""
    resultado = ResultadoExtracao(
        cards=cards_exemplo,
        tempo_processamento=0.0,
        total_cards_processados=3,
        total_cards_extraidos=3,
        total_orfaos=1,
        total_solitarios=2,
        confianca_media_geral=0.75,
        distribuicao_tipos={"tarefa": 2, "historia": 1},
    )
    analisador = AnalisadorExtracao()
    
    relatorio = analisador.analisar(resultado)
    
    total = (
        relatorio.cards_de_alta_confianca +
        relatorio.cards_de_media_confianca +
        relatorio.cards_de_baixa_confianca
    )
    assert total == 3


def test_relatorio_estrutura(cards_exemplo):
    """Testa estrutura do relatório."""
    resultado = ResultadoExtracao(
        cards=cards_exemplo,
        tempo_processamento=0.0,
        total_cards_processados=3,
        total_cards_extraidos=3,
        total_orfaos=1,
        total_solitarios=2,
        confianca_media_geral=0.75,
        distribuicao_tipos={"tarefa": 2, "historia": 1},
    )
    analisador = AnalisadorExtracao()
    
    relatorio = analisador.analisar(resultado)
    
    # Verificar estrutura
    assert isinstance(relatorio, RelatorioExtracao)
    assert relatorio.total_cards == 3
    assert relatorio.natureza is not None
    assert relatorio.entidades is not None
    assert relatorio.texto is not None
    assert relatorio.hierarquia is not None
    assert relatorio.confianca is not None
