"""Camada: interface. Só exibe dados do core/ — sem regra de negócio aqui."""
import streamlit as st

from core.models import ResultadoClassificacao

st.set_page_config(page_title="Inovação · Lei do Bem", layout="wide")
st.title("Análise de inovação — Lei do Bem")
st.caption("MVP local. Os dados do cliente não saem deste ambiente.")

st.info("Pipeline ainda não conectado. Classificações possíveis: "
        + ", ".join(r.value for r in ResultadoClassificacao))
