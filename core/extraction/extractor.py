"""Camada: core. Extração de entidades, cerne e natureza de cards."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import CardBruto, CardExtraido, ResultadoExtracao, TipoHierarquia


class ExtractorCards:
    """Extrai entidades, cerne e contexto hierárquico de cards Businessmap."""

    # Mapa: type_id → TipoHierarquia
    TIPO_MAPA = {
        1: TipoHierarquia.HISTORIA,  # Típico da Businessmap
        2: TipoHierarquia.TAREFA,
        3: TipoHierarquia.INICIATIVA,
        4: TipoHierarquia.OKR,
    }

    # Palavras-chave para detecção de natureza da atividade
    PALAVRAS_CHAVE_NATUREZA = {
        "desenvolvimento_novo": [
            "novo", "nova", "criar", "construir", "implementar",
            "feature", "funcionalidade", "algoritmo", "solução"
        ],
        "experimentacao": [
            "teste", "testar", "prototipo", "poc", "proof of concept",
            "investigar", "pesquisa", "validar", "verificar"
        ],
        "melhoria": [
            "melhorar", "otimizar", "refatorar", "performance",
            "eficiência", "redesign", "upgrade", "atualizar"
        ],
        "manutencao_corretiva": [
            "bug", "erro", "corrigir", "fix", "problema", "problema técnico",
            "defeito", "falha", "falha crítica"
        ],
        "manutencao_evolutiva": [
            "evolução", "manutenção", "sustentação", "suporte técnico"
        ],
        "operacao_suporte": [
            "suporte", "operação", "monitoramento", "observação",
            "manutenção preventiva", "backup", "restore"
        ],
        "implantacao_configuracao": [
            "implantação", "deploy", "configurar", "setup", "instalação",
            "migração de dados", "integração", "customização"
        ],
    }

    def __init__(self):
        self.cards_extraidos: list[CardExtraido] = []
        self.hierarquia: dict[int, list[int]] = defaultdict(list)  # pai_id -> [filho_ids]
        self.pais: dict[int, int] = {}  # card_id -> pai_id
        self.tipo_nome_cache: dict[int, str] = {}  # type_id -> nome

    def carregar_tipos(self, path_types: Path | str) -> None:
        """Carrega mapa de type_id → nome de tipo."""
        with open(path_types, 'r') as f:
            for line in f:
                data = json.loads(line)
                self.tipo_nome_cache[data['type_id']] = data['name'].lower()

    def carregar_hierarquia(self, path_links: Path | str) -> None:
        """Carrega relações pai-filho entre cards."""
        with open(path_links, 'r') as f:
            for line in f:
                data = json.loads(line)
                card_id = data['card_id']
                link_card_id = data['link_card_id']
                link_type = data['link_type']

                if link_type == 'parent':
                    self.pais[card_id] = link_card_id
                    self.hierarquia[link_card_id].append(card_id)
                elif link_type == 'child':
                    self.pais[link_card_id] = card_id
                    self.hierarquia[card_id].append(link_card_id)

    def _limpar_html(self, texto: str) -> str:
        """Remove tags HTML básicas."""
        if not texto:
            return ""
        texto = re.sub(r'<[^>]+>', ' ', texto)
        texto = texto.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&amp;', '&')
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    def _extrair_cerne(self, title: str, description: str) -> str:
        """Extrai 1 frase essencial do card (cerne)."""
        if title and len(title) < 200:
            return self._limpar_html(title)
        if description:
            desc_limpa = self._limpar_html(description)
            match = re.search(r'[^.!?]*[.!?]', desc_limpa)
            if match:
                frase = match.group(0).strip()
                if len(frase) > 20:
                    return frase[:200]
        return title or description[:100] or ""

    def _extrair_entidades(self, texto: str) -> list[str]:
        """Extrai possíveis entidades (nomes maiúsculas, siglas)."""
        if not texto:
            return []
        texto_limpo = self._limpar_html(texto)
        entidades = re.findall(r'\b[A-Z]{2,}(?:_[A-Z]+)*\b', texto_limpo)
        visto = set()
        resultado = []
        for e in entidades:
            if e not in visto and len(resultado) < 10:
                visto.add(e)
                resultado.append(e)
        return resultado

    def _classificar_natureza(self, texto: str, tipo: TipoHierarquia) -> tuple[str, float]:
        """Classifica natureza da atividade baseado em palavras-chave."""
        if not texto:
            return "indefinida", 0.0
        texto_lower = texto.lower()
        pontuacoes = {}
        for natureza, palavras in self.PALAVRAS_CHAVE_NATUREZA.items():
            matches = sum(1 for p in palavras if p in texto_lower)
            if matches > 0:
                pontuacoes[natureza] = matches
        if not pontuacoes:
            return "indefinida", 0.1
        melhor = max(pontuacoes.items(), key=lambda x: x[1])
        natureza, pontos = melhor
        confianca = min(pontos / sum(pontuacoes.values()), 1.0)
        return natureza, confianca

    def _calcular_profundidade(self, card_id: int) -> int:
        """Calcula profundidade na hierarquia (0 = raiz)."""
        profundidade = 0
        current = card_id
        visitados = set()
        while current in self.pais and current not in visitados:
            visitados.add(current)
            current = self.pais[current]
            profundidade += 1
        return profundidade

    def _inferir_tipo(self, profundidade: int, type_id: int) -> TipoHierarquia:
        """Infere tipo hierárquico baseado em profundidade."""
        if type_id in self.TIPO_MAPA:
            return self.TIPO_MAPA[type_id]
        if profundidade == 0:
            return TipoHierarquia.OKR
        elif profundidade == 1:
            return TipoHierarquia.INICIATIVA
        elif profundidade == 2:
            return TipoHierarquia.HISTORIA
        else:
            return TipoHierarquia.TAREFA

    def extrair(self, path_cards: Path | str, limite: Optional[int] = None) -> ResultadoExtracao:
        """Extrai dados de cards JSONL."""
        self.cards_extraidos = []
        total_processados = 0
        orfaos = 0
        solitarios = 0

        print(f"Iniciando extração de {path_cards}...")

        with open(path_cards, 'r') as f:
            for i, line in enumerate(f):
                if limite and i >= limite:
                    break
                if i % 50000 == 0:
                    print(f"  Processados: {i}...", flush=True)

                data = json.loads(line)
                card_bruto = CardBruto(**data)

                pai_id = self.pais.get(card_bruto.card_id)
                filhos_ids = self.hierarquia.get(card_bruto.card_id, [])
                eh_orfao = pai_id is None
                eh_solitario = eh_orfao and len(filhos_ids) == 0
                profundidade = self._calcular_profundidade(card_bruto.card_id)

                cerne = self._extrair_cerne(card_bruto.title, card_bruto.description or "")
                entidades = self._extrair_entidades(f"{card_bruto.title} {card_bruto.description or ''}")
                natureza, conf_natureza = self._classificar_natureza(
                    f"{card_bruto.title} {card_bruto.description or ''}", TipoHierarquia.TAREFA
                )
                tipo = self._inferir_tipo(profundidade, card_bruto.type_id)

                conf_tipo = 0.9 if card_bruto.type_id in self.TIPO_MAPA else 0.6
                conf_cerne = 0.95 if cerne else 0.0
                conf_hierarquia = 0.95 if not eh_orfao else 0.5

                penalidade = 0.0
                if eh_orfao:
                    penalidade += 0.15
                if eh_solitario:
                    penalidade += 0.10

                card_extraido = CardExtraido(
                    card_id=card_bruto.card_id,
                    titulo=card_bruto.title,
                    descricao=card_bruto.description,
                    tipo_hierarquia=tipo,
                    cerne=cerne,
                    entidades=entidades,
                    natureza_atividade=natureza,
                    pai_id=pai_id,
                    filhos_ids=filhos_ids,
                    eh_orfao=eh_orfao,
                    eh_solitario=eh_solitario,
                    profundidade_hierarquia=profundidade,
                    confianca_tipo=conf_tipo,
                    confianca_cerne=conf_cerne,
                    confianca_natureza=conf_natureza,
                    confianca_hierarquia=conf_hierarquia,
                    penalidade_orfandade=penalidade,
                )

                self.cards_extraidos.append(card_extraido)
                total_processados += 1

                if eh_orfao:
                    orfaos += 1
                if eh_solitario:
                    solitarios += 1

        dist_tipos = defaultdict(int)
        for card in self.cards_extraidos:
            dist_tipos[card.tipo_hierarquia.value] += 1

        confianca_media = (
            sum(c.confianca_tipo for c in self.cards_extraidos) / len(self.cards_extraidos)
            if self.cards_extraidos
            else 0.0
        )

        print(f"✓ Extração concluída: {total_processados} cards, {orfaos} órfãos, {solitarios} solitários")

        return ResultadoExtracao(
            total_cards_processados=total_processados,
            total_cards_extraidos=len(self.cards_extraidos),
            total_orfaos=orfaos,
            total_solitarios=solitarios,
            cards=self.cards_extraidos,
            confianca_media_geral=confianca_media,
            distribuicao_tipos=dict(dist_tipos),
        )
