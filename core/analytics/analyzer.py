"""Camada: core. Análise estatística de dados extraídos."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from statistics import mean, stdev

from core.extraction import CardExtraido, ResultadoExtracao

from .models import (
    EstatisticasConfianca,
    EstatisticasEntidades,
    EstatisticasHierarquia,
    EstatisticasNatureza,
    EstatisticasTexto,
    FrequenciaItem,
    RelatorioExtracao,
)

# Palavras muito comuns a ignorar
STOPWORDS_PT = {
    "de", "para", "com", "um", "uma", "o", "a", "os", "as",
    "que", "é", "e", "ou", "se", "não", "em", "por", "do",
    "da", "dos", "das", "na", "no", "nas", "nos", "à", "ao",
    "aos", "aqueles", "esse", "aquele", "este", "isto", "essa",
}

# Siglas/abreviaturas comuns que não são realmente entidades de negócio
STOPWORDS_SIGLAS = {
    # Preposições e conjunções
    "POR", "PARA", "COM", "SEM", "ENTRE", "SOBRE", "ANTE",
    "DE", "A", "O", "E", "OU", "QUE", "SE", "EM", "DO", "DA",
    
    # Interrogativas/demonstrativas
    "CASO", "ONDE", "QUANDO", "QUAL", "COMO", "QUEM", "QUAL",
    
    # Palavras temporais
    "ENQUANTO", "DURANTE", "DEPOIS", "ANTES", "ENTÃO", "ATRÁS",
    
    # Verbos comuns
    "NECESSÁRIO", "NECESSITO", "NECESSITA", "DEVE", "PODEM",
    "PODE", "PODIA", "PODERIA", "FAZER", "FEITO", "FAÇA", "FIZER",
    "DAR", "DADO", "DÁ", "QUER", "QUEREMOS", "QUER", "SER",
    "ESTÁ", "ESTÃO", "ESTÁ", "FORAM", "FORAM", "HAVERÁ",
    
    # Advérbios
    "ASSIM", "AINDA", "TAMBÉM", "TALVEZ", "AQUI", "ALI", "LÁ",
    "CÁ", "ACOLÁ", "AGORA", "JÁ", "LOGO", "NUNCA", "SEMPRE",
    "AQUI", "AÍ", "CIMA", "BAIXO",
    
    # Quantificadores
    "MAIS", "MENOS", "MUITO", "POUCO", "TODO", "NADA", "TUDO",
    "CADA", "QUALQUER", "ALGUM", "NENHUM",
    
    # Artigos
    "UM", "UMA", "UNS", "UMAS", "OS", "AS",
}



class AnalisadorExtracao:
    """Analisa dados extraídos e gera relatório completo."""

    def analisar(self, resultado: ResultadoExtracao) -> RelatorioExtracao:
        """Analisa resultado de extração e retorna relatório."""
        cards = resultado.cards

        # Análises por tema
        natureza_stats = self._analisar_natureza(cards)
        entidades_stats = self._analisar_entidades(cards)
        texto_stats = self._analisar_texto(cards)
        hierarquia_stats = self._analisar_hierarquia(cards)
        confianca_stats = self._analisar_confianca(cards)

        # Classificação por confiança
        alta_confianca = len([c for c in cards if self._confianca_geral(c) > 0.8])
        media_confianca = len([c for c in cards if 0.5 <= self._confianca_geral(c) <= 0.8])
        baixa_confianca = len([c for c in cards if self._confianca_geral(c) < 0.5])

        return RelatorioExtracao(
            total_cards=len(cards),
            natureza=natureza_stats,
            entidades=entidades_stats,
            texto=texto_stats,
            hierarquia=hierarquia_stats,
            confianca=confianca_stats,
            cards_de_alta_confianca=alta_confianca,
            cards_de_media_confianca=media_confianca,
            cards_de_baixa_confianca=baixa_confianca,
        )

    def _confianca_geral(self, card: CardExtraido) -> float:
        """Calcula confiança geral (média das 4 dimensões)."""
        return (
            card.confianca_tipo
            + card.confianca_cerne
            + card.confianca_natureza
            + card.confianca_hierarquia
        ) / 4.0

    def _analisar_natureza(self, cards: list[CardExtraido]) -> EstatisticasNatureza:
        """Analisa distribuição de natureza da atividade."""
        counter = Counter(c.natureza_atividade or "indefinida" for c in cards)

        distribuicao = dict(counter)
        distribuicao_pct = {
            nat: (cont / len(cards)) * 100 for nat, cont in distribuicao.items()
        }

        confianca_media = {}
        for natureza in distribuicao:
            cards_natureza = [c for c in cards if c.natureza_atividade == natureza]
            if cards_natureza:
                confianca_media[natureza] = mean(
                    c.confianca_natureza for c in cards_natureza
                )

        indefinidas = distribuicao.get("indefinida", 0)

        return EstatisticasNatureza(
            total_cards=len(cards),
            distribuicao=distribuicao,
            distribuicao_pct=distribuicao_pct,
            confianca_media_por_natureza=confianca_media,
            cards_sem_natureza_definida=indefinidas,
        )

    def _analisar_entidades(self, cards: list[CardExtraido]) -> EstatisticasEntidades:
        """Analisa entidades extraídas, filtrando stop words."""
        todas_entidades = []
        counter_entidades = Counter()

        for card in cards:
            # Filtrar stop words de siglas
            entidades_filtradas = [
                e for e in card.entidades 
                if e.upper() not in STOPWORDS_SIGLAS
            ]
            todas_entidades.extend(entidades_filtradas)
            counter_entidades.update(entidades_filtradas)

        top_50 = [
            FrequenciaItem(
                item=ent,
                contagem=cont,
                percentual=(cont / len(todas_entidades)) * 100 if todas_entidades else 0,
            )
            for ent, cont in counter_entidades.most_common(50)
        ]

        return EstatisticasEntidades(
            total_entidades_unicas=len(counter_entidades),
            total_mencoes=len(todas_entidades),
            top_entidades=top_50,
            siglas_mais_comuns=counter_entidades.most_common(20),
        )

    def _analisar_texto(self, cards: list[CardExtraido]) -> EstatisticasTexto:
        """Analisa características de texto (cerne, título, descrição)."""
        comprimentos_cerne = [len(c.cerne) for c in cards if c.cerne]
        comprimentos_titulo = [len(c.titulo) for c in cards if c.titulo]
        comprimentos_desc = [len(c.descricao or "") for c in cards if c.descricao]

        # Palavras mais comuns
        todas_palavras = []
        for card in cards:
            texto = f"{card.titulo} {card.descricao or ''} {card.cerne}".lower()
            # Remover HTML/tags
            texto = re.sub(r'<[^>]+>', ' ', texto)
            texto = re.sub(r'&[a-z]+;', ' ', texto)  # Remover entidades HTML
            palavras = re.findall(r'\b\w+\b', texto)
            todas_palavras.extend(
                p for p in palavras if len(p) > 3 and p not in STOPWORDS_PT
            )

        counter_palavras = Counter(todas_palavras)
        top_palavras = [
            FrequenciaItem(
                item=pal,
                contagem=cont,
                percentual=(cont / len(todas_palavras)) * 100 if todas_palavras else 0,
            )
            for pal, cont in counter_palavras.most_common(100)
        ]

        return EstatisticasTexto(
            comprimento_medio_cerne=mean(comprimentos_cerne) if comprimentos_cerne else 0,
            comprimento_medio_titulo=mean(comprimentos_titulo) if comprimentos_titulo else 0,
            comprimento_medio_descricao=mean(comprimentos_desc) if comprimentos_desc else 0,
            cernes_vazios=len([c for c in cards if not c.cerne]),
            descricoes_vazias=len([c for c in cards if not c.descricao]),
            palavras_comuns=top_palavras,
        )

    def _analisar_hierarquia(self, cards: list[CardExtraido]) -> EstatisticasHierarquia:
        """Analisa estrutura hierárquica."""
        profundidades = [c.profundidade_hierarquia for c in cards]

        dist_profundidade = Counter(profundidades)

        okrs = len([c for c in cards if c.tipo_hierarquia.value == "okr"])
        initiatives = len([c for c in cards if c.tipo_hierarquia.value == "iniciativa"])
        historias = len([c for c in cards if c.tipo_hierarquia.value == "historia"])

        # Filhos por OKR/Iniciativa (média)
        filhos_por_okr = []
        filhos_por_init = []
        for card in cards:
            if card.tipo_hierarquia.value == "okr" and card.filhos_ids:
                filhos_por_okr.append(len(card.filhos_ids))
            if card.tipo_hierarquia.value == "iniciativa" and card.filhos_ids:
                filhos_por_init.append(len(card.filhos_ids))

        return EstatisticasHierarquia(
            profundidade_media=mean(profundidades) if profundidades else 0,
            profundidade_maxima=max(profundidades) if profundidades else 0,
            profundidade_minima=min(profundidades) if profundidades else 0,
            distribuicao_profundidade=dict(dist_profundidade),
            cards_com_pai=len([c for c in cards if c.pai_id]),
            cards_orfaos=len([c for c in cards if c.eh_orfao]),
            cards_com_filhos=len([c for c in cards if c.filhos_ids]),
            cards_solitarios=len([c for c in cards if c.eh_solitario]),
            okrs_raiz=okrs,
            initiatives_por_okr_media=mean(filhos_por_okr) if filhos_por_okr else 0,
            historias_por_initiative_media=mean(filhos_por_init) if filhos_por_init else 0,
        )

    def _analisar_confianca(self, cards: list[CardExtraido]) -> EstatisticasConfianca:
        """Analisa distribuição de confiança."""
        conf_tipos = [c.confianca_tipo for c in cards]
        conf_cernes = [c.confianca_cerne for c in cards]
        conf_naturezas = [c.confianca_natureza for c in cards]
        conf_hierarquias = [c.confianca_hierarquia for c in cards]

        # Distribuição em faixas (0.0-0.2, 0.2-0.4, etc.)
        def _distribuir_em_faixas(valores):
            faixas = defaultdict(int)
            for v in valores:
                faixa = int(v * 5) * 0.2  # 0.0, 0.2, 0.4, 0.6, 0.8, 1.0
                faixa = min(faixa, 1.0)
                faixas[f"{faixa:.1f}"] += 1
            return dict(faixas)

        penalidades = [c.penalidade_orfandade for c in cards]

        return EstatisticasConfianca(
            confianca_media_tipo=mean(conf_tipos) if conf_tipos else 0,
            confianca_media_cerne=mean(conf_cernes) if conf_cernes else 0,
            confianca_media_natureza=mean(conf_naturezas) if conf_naturezas else 0,
            confianca_media_hierarquia=mean(conf_hierarquias) if conf_hierarquias else 0,
            distribuicao_confianca_tipo=_distribuir_em_faixas(conf_tipos),
            distribuicao_confianca_cerne=_distribuir_em_faixas(conf_cernes),
            penalidade_media=mean(penalidades) if penalidades else 0,
            cards_com_penalidade=len([c for c in cards if c.penalidade_orfandade > 0]),
        )
