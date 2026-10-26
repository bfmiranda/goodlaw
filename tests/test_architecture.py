"""Garante a separação núcleo/interface: core/ não importa bibliotecas de interface."""
import ast
from pathlib import Path

PROIBIDOS = {"streamlit", "fastapi", "fasthtml", "starlette", "plotly", "pyvis", "dash", "app"}
CORE = Path(__file__).resolve().parent.parent / "core"


def _imports(arquivo: Path) -> set[str]:
    nomes = set()
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        if isinstance(no, ast.Import):
            nomes |= {a.name.split(".")[0] for a in no.names}
        elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            nomes.add(no.module.split(".")[0])
    return nomes


def test_core_nao_importa_interface():
    violacoes = {
        str(f.relative_to(CORE.parent)): sorted(_imports(f) & PROIBIDOS)
        for f in CORE.rglob("*.py")
        if _imports(f) & PROIBIDOS
    }
    assert not violacoes, f"core/ importando interface: {violacoes}"
