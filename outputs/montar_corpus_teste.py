#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Tarefa 4 — Monta o corpus de teste de frases.

Combina duas fontes (conforme decisão do usuário "Combinar fontes"):
    1. ToLD-BR — usando a coluna `misogyny` (>= 2 votos de anotadores = positivo
       de alta confiança). Pega também não-misóginas para compor o corpus.
    2. Notícias / internet coletadas pelo usuário — colunas vazias prontas
       para preenchimento manual.

Saída:
    - outputs/corpus_teste_frases.csv
       colunas: text, label, categoria_id, categoria_nome, fonte, anotador

Uso:
    python3 outputs/montar_corpus_teste.py [--n-misogino 200] [--n-nao 200]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
TOLD_PATH    = RAIZ_PROJETO / "lexicons_corpus_misoginia" / "ToLD-BR" / "ToLD-BR.csv"
SAIDA        = RAIZ_PROJETO / "outputs" / "corpus_teste_frases.csv"

CATEGORIAS_NOMES = {
    1: "Descrédito", 2: "Estereotipização", 3: "Assédio Sexual",
    4: "Ameaças de Violência", 5: "Dominação", 6: "Derailing",
    7: "Culpabilização da Vítima", 8: "Objetificação Sexual",
    9: "Neossexismo", 10: "Misogynoir", 11: "Violência Política Digital",
}


def construir() -> int:
    ap = argparse.ArgumentParser(description="Monta o corpus de teste (Tarefa 4)")
    ap.add_argument("--n-misogino", type=int, default=200,
                    help="quantas frases misóginas extrair do ToLD-BR (default: 200)")
    ap.add_argument("--n-nao", type=int, default=200,
                    help="quantas frases não-misóginas extrair (default: 200)")
    ap.add_argument("--n-noticias", type=int, default=100,
                    help="quantas linhas em branco reservar para notícias do usuário")
    ap.add_argument("--limiar-misogino", type=int, default=2,
                    help="mínimo de votos de anotadores ToLD-BR para classificar como misógino (default: 2 de 3)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if not TOLD_PATH.exists():
        print(f"❌ Não encontrei {TOLD_PATH}.")
        return 1

    print(f"📥 Lendo ToLD-BR: {TOLD_PATH.name}")
    df = pd.read_csv(TOLD_PATH)
    print(f"   {len(df):,} tweets | dist misoginia: {df['misogyny'].value_counts().to_dict()}")

    # Misóginas: misogyny >= limiar (alta confiança)
    mis = df[df["misogyny"] >= args.limiar_misogino].sample(
        n=min(args.n_misogino, (df["misogyny"] >= args.limiar_misogino).sum()),
        random_state=args.seed,
    )
    # Não-misóginas: nenhum dos rótulos de toxicidade ativado
    cols_tox = ["homophobia", "obscene", "insult", "racism", "misogyny", "xenophobia"]
    df["soma_tox"] = df[cols_tox].sum(axis=1)
    nao = df[df["soma_tox"] == 0].sample(
        n=min(args.n_nao, (df["soma_tox"] == 0).sum()),
        random_state=args.seed,
    )

    linhas = []
    for _, row in mis.iterrows():
        linhas.append({
            "text": row["text"],
            "label": 1,
            "categoria_id": "",          # preencher manualmente (1..11)
            "categoria_nome": "",        # idem
            "fonte": "ToLD-BR",
            "anotador": "",
            "votos_misoginia_told": int(row["misogyny"]),
        })
    for _, row in nao.iterrows():
        linhas.append({
            "text": row["text"],
            "label": 0,
            "categoria_id": "",
            "categoria_nome": "",
            "fonte": "ToLD-BR",
            "anotador": "",
            "votos_misoginia_told": 0,
        })

    # Linhas em branco para notícias coletadas pelo usuário
    for _ in range(args.n_noticias):
        linhas.append({
            "text": "",
            "label": "",
            "categoria_id": "",
            "categoria_nome": "",
            "fonte": "noticias",
            "anotador": "",
            "votos_misoginia_told": "",
        })

    out = pd.DataFrame(linhas)
    out.to_csv(SAIDA, index=False, encoding="utf-8")

    print(f"\n💾 Corpus de teste salvo: {SAIDA.name}")
    print(f"   misóginas (ToLD-BR, ≥{args.limiar_misogino} votos): {(out['label'] == 1).sum()}")
    print(f"   não-misóginas (ToLD-BR, sem toxicidade): {(out['label'] == 0).sum()}")
    print(f"   linhas em branco para notícias: {(out['fonte'] == 'noticias').sum()}")

    print("\n📋 Próximos passos manuais:")
    print("   1. Para cada linha com label=1, preencher categoria_id (1–11) e categoria_nome.")
    print("   2. Preencher as linhas 'noticias' com texto coletado, label e categoria.")
    print("   3. Categorias possíveis:")
    for cid, nome in CATEGORIAS_NOMES.items():
        print(f"      {cid:2d} = {nome}")

    return 0


if __name__ == "__main__":
    sys.exit(construir())
