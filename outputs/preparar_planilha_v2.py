#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preparar_planilha_v2.py
=======================

Gera a **planilha de votação v2** do grupo de pesquisa, conforme orientações
da Profa. Dra. Deborah Silva Alves Fernandes (jun/2026):

- **Removida** a coluna `eh_misogino`: palavras isoladas têm apenas o
  significado de dicionário; só podem ser tratadas como integrantes de
  conteúdo com traços de misoginia **em contexto**.
- **Adicionada** a coluna `dependencia_contextual` (baixo / médio / alto),
  pré-preenchida por heurística da razão `freq_mis / (freq_mis + freq_non)`.
- **Adicionada** a coluna `exemplo_uso`: primeira ocorrência real do termo
  em documento com `label=1` (ou `label=0` marcado, se não houver).
- **Taxonomia reduzida** (revisão jun/2026): 7 classes principais (5 Anzovino
  + 2 Sultana) + 2 subclasses transversais (T1 Misogynoir, T2 Violência
  Política Digital). Classes antigas 6 (Derailing) e 9 (Neossexismo) foram
  removidas; 10 e 11 viraram transversais.

Saída: `outputs/planilha_votacao_grupo_v2.csv`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- #
# Caminhos
# --------------------------------------------------------------------------- #
RAIZ = Path(__file__).resolve().parents[1]
ENTRADA_V3_ANOTADO = RAIZ / "outputs" / "lexico_v3_anotado.csv"
CORPUS = RAIZ / "corpus_unificado_final.csv"
SAIDA = RAIZ / "outputs" / "planilha_votacao_grupo_v2.csv"

# --------------------------------------------------------------------------- #
# Mapeamento da taxonomia antiga (11 classes) → revisada (7 + 2 transversais)
# --------------------------------------------------------------------------- #
NOMES_NOVOS = {
    1: "Descrédito",
    2: "Estereotipização",
    3: "Assédio Sexual",
    4: "Ameaças de Violência",
    5: "Dominação",
    6: "Culpabilização da Vítima",
    7: "Objetificação Sexual",
}

# old_id -> (new_id, transversal)
#   new_id pode ser None quando não há equivalente lexical claro (anotador decide)
MAPA = {
    1: (1, ""),           # Descrédito → Descrédito
    2: (2, ""),           # Estereotipização → Estereotipização
    3: (3, ""),           # Assédio Sexual → Assédio Sexual
    4: (4, ""),           # Ameaças → Ameaças
    5: (5, ""),           # Dominação → Dominação
    6: (None, ""),        # Derailing removida (anotador decide a classe)
    7: (6, ""),           # Culpabilização (antiga 7) → 6
    8: (7, ""),           # Objetificação (antiga 8) → 7
    9: (1, ""),           # Neossexismo → Descrédito (mais comum lexicalmente)
    10: (1, "T1"),        # Misogynoir → Descrédito + T1
    11: (1, "T2"),        # Violência Política Digital → Descrédito + T2
}

# --------------------------------------------------------------------------- #
# Heurísticas
# --------------------------------------------------------------------------- #
def grau_dependencia(freq_mis: float, freq_non: float) -> str:
    """
    Heurística de pré-preenchimento da dependência contextual.

    Razão = freq_mis / (freq_mis + freq_non):
      - razão ≥ 0.75 → uso quase sempre hostil       → 'baixo'
      - 0.40 ≤ razão < 0.75 → uso ambíguo            → 'médio'
      - razão < 0.40 → palavra de uso comum         → 'alto'

    O grau é o quanto o significado misógino depende do contexto.
    Termos raros fora de contexto misógino → dependência baixa (significado
    quase fixado). Termos comuns em qualquer contexto → dependência alta.
    """
    total = float(freq_mis) + float(freq_non)
    if total <= 0:
        return "alto"
    razao = float(freq_mis) / total
    if razao >= 0.75:
        return "baixo"
    if razao >= 0.40:
        return "médio"
    return "alto"


def carregar_corpus_label1(corpus_path: Path) -> list[str]:
    """Carrega apenas os documentos com label=1, em lowercase, para busca rápida."""
    df = pd.read_csv(corpus_path)
    df = df[df["label"] == 1].copy()
    df["text"] = df["text"].astype(str)
    df = df[df["text"].str.len() > 5]  # remove ruído de IDs numéricos
    return df["text"].tolist()


def carregar_corpus_label0(corpus_path: Path) -> list[str]:
    df = pd.read_csv(corpus_path)
    df = df[df["label"] == 0].copy()
    df["text"] = df["text"].astype(str)
    df = df[df["text"].str.len() > 5]
    return df["text"].tolist()


def encontrar_exemplo(term: str, docs_label1: list[str],
                      docs_label0: list[str], max_len: int = 200) -> str:
    """
    Procura a primeira ocorrência do termo (case-insensitive, word-boundary)
    em documentos label=1. Se não encontrar, tenta label=0 com prefixo [label=0].
    Trunca a `max_len` caracteres adicionando '…'.
    """
    if not term:
        return ""
    padrao = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
    for texto in docs_label1:
        if padrao.search(texto):
            return _truncar(texto, max_len)
    for texto in docs_label0:
        if padrao.search(texto):
            return f"[label=0] {_truncar(texto, max_len)}"
    # fallback: substring match (não word boundary) em label=1
    term_lower = term.lower()
    for texto in docs_label1:
        if term_lower in texto.lower():
            return _truncar(texto, max_len)
    return ""


def _truncar(texto: str, max_len: int) -> str:
    texto = " ".join(texto.split())  # normaliza espaços
    return texto if len(texto) <= max_len else texto[:max_len].rstrip() + "…"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> int:
    if not ENTRADA_V3_ANOTADO.exists():
        print(f"❌ Não encontrei {ENTRADA_V3_ANOTADO}. "
              f"Rode `python3 outputs/anotar_lexico.py --gerar-planilha` primeiro.")
        return 1
    if not CORPUS.exists():
        print(f"❌ Não encontrei {CORPUS}.")
        return 1

    print(f"📥 Léxico anotado: {ENTRADA_V3_ANOTADO.name}")
    df = pd.read_csv(ENTRADA_V3_ANOTADO)
    df_mis = df[df["polarity"] == "misogino"].copy().reset_index(drop=True)
    print(f"   {len(df_mis)} termos com traços de misoginia para preparar")

    print(f"📥 Corpus: {CORPUS.name}")
    docs_l1 = carregar_corpus_label1(CORPUS)
    docs_l0 = carregar_corpus_label0(CORPUS)
    print(f"   {len(docs_l1)} documentos label=1, {len(docs_l0)} documentos label=0")

    # Remapear classe antiga para nova + transversal
    novas_classes: list[int | str] = []
    novos_nomes: list[str] = []
    transversais: list[str] = []
    for _, row in df_mis.iterrows():
        old_id = row.get("categoria_id_sugerida")
        if pd.isna(old_id):
            novas_classes.append("")
            novos_nomes.append("")
            transversais.append("")
            continue
        try:
            old_id_int = int(old_id)
        except (ValueError, TypeError):
            novas_classes.append("")
            novos_nomes.append("")
            transversais.append("")
            continue
        novo_id, transversal = MAPA.get(old_id_int, (None, ""))
        if novo_id is None:
            novas_classes.append("")
            novos_nomes.append("")
        else:
            novas_classes.append(novo_id)
            novos_nomes.append(NOMES_NOVOS[novo_id])
        transversais.append(transversal)

    # Dependência contextual e exemplo de uso
    deps: list[str] = []
    exemplos: list[str] = []
    print("⚙️  Computando dependência contextual + exemplos de uso...")
    for i, row in df_mis.iterrows():
        freq_mis = row.get("freq_mis", 0) or 0
        freq_non = row.get("freq_non", 0) or 0
        deps.append(grau_dependencia(freq_mis, freq_non))
        ex = encontrar_exemplo(str(row["term"]), docs_l1, docs_l0)
        exemplos.append(ex)
        if (i + 1) % 50 == 0:
            print(f"   {i + 1}/{len(df_mis)} termos processados")

    planilha = pd.DataFrame({
        "term": df_mis["term"],
        "classe_lexical_sugerida": novas_classes,
        "nome_classe": novos_nomes,
        "transversal": transversais,
        "dependencia_contextual": deps,
        "exemplo_uso": exemplos,
        "anotador1_classe": "",
        "anotador1_dependencia": "",
        "anotador2_classe": "",
        "anotador2_dependencia": "",
        "anotador3_classe": "",
        "anotador3_dependencia": "",
        "comentarios": "",
    })

    planilha.to_csv(SAIDA, index=False, encoding="utf-8")
    print(f"\n💾 Saída: {SAIDA}")
    print(f"   {len(planilha)} termos · {len(planilha.columns)} colunas")

    # Resumo
    print("\n📊 Distribuição de classe lexical sugerida:")
    contagem_classe = planilha["classe_lexical_sugerida"].value_counts(dropna=False)
    for k, v in contagem_classe.items():
        nome = NOMES_NOVOS.get(int(k), "—") if k not in ("", None) and not pd.isna(k) else "(sem sugestão)"
        print(f"   {k!s:>6} {nome:<28} {v:>4} termos")

    print("\n📊 Distribuição de subclasse transversal:")
    print(planilha["transversal"].value_counts(dropna=False).to_string())

    print("\n📊 Distribuição de dependência contextual (heurística):")
    print(planilha["dependencia_contextual"].value_counts().to_string())

    print("\n📊 Exemplos de uso encontrados:")
    encontrados = (planilha["exemplo_uso"].astype(str).str.len() > 0).sum()
    print(f"   {encontrados}/{len(planilha)} ({encontrados/len(planilha):.1%})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
