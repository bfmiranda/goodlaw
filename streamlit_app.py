"""Camada: interface. Só exibe dados do core/ — sem regra de negócio aqui."""
import sys
from pathlib import Path

import streamlit as st

# Adiciona raiz do projeto ao path para importar core/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.models import ResultadoClassificacao

st.set_page_config(page_title="Inovação · Lei do Bem", layout="wide")
st.title("Análise de inovação — Lei do Bem")
st.caption("MVP local. Os dados do cliente não saem deste ambiente.")

st.info("Pipeline ainda não conectado. Classificações possíveis: "
        + ", ".join(r.value for r in ResultadoClassificacao))
