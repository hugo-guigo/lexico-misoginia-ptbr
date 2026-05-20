#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Tarefa 3 — Anotação automática + planilha de votação do grupo.

Para cada termo do léxico V3 (misógino), sugere a categoria da taxonomia (1–11)
a partir da similaridade vetorial spaCy entre o lema do termo e o **centróide** de
palavras-âncora de cada classe. Gera também uma planilha em branco para a votação
manual de 3 anotadores e calcula Kappa/Fleiss quando os votos forem preenchidos.

Saídas:
    - outputs/lexico_v3_anotado.csv        # V3 + categoria sugerida + similaridade
    - outputs/planilha_votacao_grupo.csv   # planilha em branco para os anotadores
    - outputs/concordancia_kappa_fleiss.csv (se a planilha já estiver preenchida)
    - outputs/lexico_v3_validado_final.csv/.json (consolidação dos votos)

Uso:
    # 1. Após gerar o V3 (pipeline_semente_pmi.py):
    python3 outputs/anotar_lexico.py --gerar-planilha

    # 2. Após o grupo preencher a planilha:
    python3 outputs/anotar_lexico.py --consolidar
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import spacy

# ============================================================
# CONFIGURAÇÕES
# ============================================================

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
DIR_SAIDA    = RAIZ_PROJETO / "outputs"

ENTRADA_V3   = DIR_SAIDA / "lexico_misoginia_v3_semente_pmi.csv"
SAIDA_ANOT   = DIR_SAIDA / "lexico_v3_anotado.csv"
SAIDA_VOTOS  = DIR_SAIDA / "planilha_votacao_grupo.csv"
SAIDA_KAPPA  = DIR_SAIDA / "concordancia_kappa_fleiss.csv"
SAIDA_FINAL_CSV  = DIR_SAIDA / "lexico_v3_validado_final.csv"
SAIDA_FINAL_JSON = DIR_SAIDA / "lexico_v3_validado_final.json"

SIM_MINIMA = 0.30   # abaixo disso, marca "INCERTO" e deixa categoria em branco
SPACY_MODEL = "pt_core_news_lg"

# ============================================================
# ÂNCORAS POR CATEGORIA (derivadas da taxonomia, seção 3)
# ============================================================

ANCORAS: dict[int, dict] = {
    1: {
        "nome": "Descrédito",
        "ancoras": [
            "incompetente", "burra", "burro", "histérica", "louca", "surtada",
            "despreparada", "ignorante", "estúpida", "ridícula", "patética",
            "fracassada", "idiota", "tola", "imbecil", "desqualificada",
        ],
    },
    2: {
        "nome": "Estereotipização",
        "ancoras": [
            "mulherzinha", "fofoqueira", "fútil", "frágil", "delicada",
            "emotiva", "irracional", "vaidosa", "interesseira", "tpm",
            "menininha", "princesa", "doméstica", "submissa",
        ],
    },
    3: {
        "nome": "Assédio Sexual",
        "ancoras": [
            "piranha", "vadia", "safada", "piriguete", "puta", "vagabunda",
            "biscate", "galinha", "cachorra", "rapariga", "nudes", "gostosa",
            "tarada", "ninfeta",
        ],
    },
    4: {
        "nome": "Ameaças de Violência",
        "ancoras": [
            "apanhar", "morrer", "estuprar", "estuprável", "matar", "bater",
            "espancar", "queimar", "destruir", "sumir", "porrada", "tapa",
            "ameaça", "violência",
        ],
    },
    5: {
        "nome": "Dominação",
        "ancoras": [
            "calar", "obedecer", "submeter", "cozinha", "tanque", "fogão",
            "casa", "marido", "patrão", "mandar", "dono", "controlar",
            "subordinar", "lar",
        ],
    },
    6: {
        "nome": "Derailing",
        "ancoras": [
            "mimimi", "vitimismo", "exagero", "frescura", "drama",
            "vitimista", "chororô", "reclamação", "feminazi",
        ],
    },
    7: {
        "nome": "Culpabilização da Vítima",
        "ancoras": [
            "provocar", "merecer", "saia", "decote", "bebada", "bêbada",
            "pediu", "vagabunda", "vestida", "interesseira", "cavar",
        ],
    },
    8: {
        "nome": "Objetificação Sexual",
        "ancoras": [
            "rabuda", "peituda", "carne", "boa", "pedaço", "buceta", "bunda",
            "peito", "corpo", "boazuda", "gostosona", "tesão",
        ],
    },
    9: {
        "nome": "Neossexismo",
        "ancoras": [
            "feminazi", "feminismo", "feminista", "igualdade", "privilégio",
            "meritocracia", "ideologia", "mimizenta", "vitimista",
        ],
    },
    10: {
        "nome": "Misogynoir",
        "ancoras": [
            "preta", "negra", "macumbeira", "neguinha", "crespo", "carapinha",
            "macaca", "cabelo", "racial", "racismo",
        ],
    },
    11: {
        "nome": "Violência Política Digital",
        "ancoras": [
            "candidata", "deputada", "presidenta", "ministra", "política",
            "eleição", "vereadora", "feminismo", "esquerdista", "petista",
            "comunista",
        ],
    },
}


# ============================================================
# ANOTAÇÃO AUTOMÁTICA POR SIMILARIDADE VETORIAL
# ============================================================

def construir_centroides(nlp: spacy.Language) -> dict[int, np.ndarray]:
    """Calcula o centróide vetorial dos lemas-âncora de cada categoria."""
    centroides = {}
    for cid, info in ANCORAS.items():
        vetores = []
        for palavra in info["ancoras"]:
            tok = nlp(palavra)[0]
            if tok.has_vector and tok.vector_norm > 0:
                vetores.append(tok.vector / tok.vector_norm)
        if not vetores:
            print(f"⚠️  Categoria {cid} ({info['nome']}): sem vetores válidos")
            continue
        centroides[cid] = np.mean(vetores, axis=0)
    return centroides


def sugerir_categoria(
    termo: str,
    nlp: spacy.Language,
    centroides: dict[int, np.ndarray],
) -> tuple[int | None, float, str]:
    """Devolve (categoria_id, similaridade_max, nome_categoria) ou (None, 0, '')."""
    tok = nlp(termo)[0]
    if not tok.has_vector or tok.vector_norm == 0:
        return None, 0.0, ""
    v = tok.vector / tok.vector_norm
    sims = {cid: float(np.dot(v, c)) for cid, c in centroides.items()}
    cid_best = max(sims, key=sims.get)
    sim_best = sims[cid_best]
    if sim_best < SIM_MINIMA:
        return None, sim_best, ""
    return cid_best, sim_best, ANCORAS[cid_best]["nome"]


def anotar_lexico() -> pd.DataFrame:
    if not ENTRADA_V3.exists():
        print(f"❌ Não encontrei {ENTRADA_V3}. Rode pipeline_semente_pmi.py primeiro.")
        sys.exit(1)

    print(f"📥 Léxico V3: {ENTRADA_V3.name}")
    df = pd.read_csv(ENTRADA_V3)
    # anotar apenas a polaridade misógina
    df_mis = df[df["polarity"] == "misogino"].copy().reset_index(drop=True)
    print(f"   {len(df_mis)} termos misóginos para anotar")

    print(f"🧠 Carregando spaCy: {SPACY_MODEL}")
    nlp = spacy.load(SPACY_MODEL, disable=["parser", "ner"])
    centroides = construir_centroides(nlp)

    cat_id, cat_nome, sim = [], [], []
    todas_sims = []
    for termo in df_mis["term"]:
        cid, s, nome = sugerir_categoria(termo, nlp, centroides)
        cat_id.append(cid if cid is not None else "")
        cat_nome.append(nome)
        sim.append(round(s, 4))
        # tabela completa de similaridades (top 3)
        tok = nlp(termo)[0]
        if tok.has_vector and tok.vector_norm > 0:
            v = tok.vector / tok.vector_norm
            sims_all = sorted(
                ((cid, float(np.dot(v, c))) for cid, c in centroides.items()),
                key=lambda x: x[1], reverse=True
            )[:3]
            todas_sims.append("; ".join(f"{c}:{round(s,3)}" for c, s in sims_all))
        else:
            todas_sims.append("")

    df_mis["categoria_id_sugerida"] = cat_id
    df_mis["categoria_nome_sugerida"] = cat_nome
    df_mis["similaridade"] = sim
    df_mis["top3_cats"] = todas_sims

    df_mis.to_csv(SAIDA_ANOT, index=False, encoding="utf-8")
    print(f"💾 Anotado: {SAIDA_ANOT.name}")
    print("\nDistribuição da categoria sugerida:")
    print(df_mis["categoria_nome_sugerida"].value_counts(dropna=False).to_string())
    return df_mis


# ============================================================
# PLANILHA DE VOTAÇÃO DO GRUPO
# ============================================================

def gerar_planilha_votacao(df_anot: pd.DataFrame) -> None:
    """Gera CSV em branco com colunas para 3 anotadores votarem."""
    pl = pd.DataFrame({
        "term": df_anot["term"],
        "categoria_sugerida": df_anot["categoria_id_sugerida"],
        "nome_sugerido": df_anot["categoria_nome_sugerida"],
        "anotador1_eh_misogino": "",   # preencher 0 ou 1
        "anotador1_categoria": "",     # preencher 1..11
        "anotador2_eh_misogino": "",
        "anotador2_categoria": "",
        "anotador3_eh_misogino": "",
        "anotador3_categoria": "",
        "comentarios": "",
    })
    pl.to_csv(SAIDA_VOTOS, index=False, encoding="utf-8")
    print(f"💾 Planilha de votação: {SAIDA_VOTOS.name}")
    print("   Distribua o arquivo entre os 3 anotadores do grupo.")


# ============================================================
# CONCORDÂNCIA KAPPA/FLEISS
# ============================================================

def fleiss_kappa(matriz: np.ndarray) -> float:
    """
    Fleiss' kappa. matriz é (n_itens, n_categorias) com contagens por categoria.
    """
    n_itens, n_cat = matriz.shape
    n_anotadores_por_item = matriz.sum(axis=1)
    if not (n_anotadores_por_item == n_anotadores_por_item[0]).all():
        raise ValueError("Itens devem ter o mesmo número de anotadores.")
    n = int(n_anotadores_por_item[0])
    if n < 2:
        return float("nan")

    P_i = (matriz * (matriz - 1)).sum(axis=1) / (n * (n - 1))
    P_bar = P_i.mean()
    p_j = matriz.sum(axis=0) / (n_itens * n)
    P_e = (p_j ** 2).sum()
    if P_e == 1:
        return 1.0
    return float((P_bar - P_e) / (1 - P_e))


def consolidar_votos() -> None:
    if not SAIDA_VOTOS.exists():
        print(f"❌ Não encontrei {SAIDA_VOTOS}. Gere a planilha primeiro.")
        sys.exit(1)

    print(f"📥 Lendo planilha: {SAIDA_VOTOS.name}")
    pl = pd.read_csv(SAIDA_VOTOS)

    # Filtra linhas com os 3 votos preenchidos para "é_misogino"
    pl_eh = pl.dropna(subset=[
        "anotador1_eh_misogino", "anotador2_eh_misogino", "anotador3_eh_misogino"
    ])
    print(f"   {len(pl_eh)}/{len(pl)} linhas com os 3 votos de 'é_misogino'")

    if len(pl_eh) == 0:
        print("⚠️  A planilha ainda não foi preenchida. Abortando.")
        return

    # Fleiss para "é_misogino" (2 categorias: 0 e 1)
    matriz_eh = np.zeros((len(pl_eh), 2), dtype=int)
    for i, (_, row) in enumerate(pl_eh.iterrows()):
        for col in ["anotador1_eh_misogino", "anotador2_eh_misogino", "anotador3_eh_misogino"]:
            v = int(row[col])
            matriz_eh[i, v] += 1
    kappa_eh = fleiss_kappa(matriz_eh)
    print(f"\n📊 Fleiss κ (é_misógino): {kappa_eh:.4f}")

    # Fleiss para categoria (11 classes)
    pl_cat = pl.dropna(subset=[
        "anotador1_categoria", "anotador2_categoria", "anotador3_categoria"
    ])
    if len(pl_cat) > 0:
        matriz_cat = np.zeros((len(pl_cat), 11), dtype=int)
        for i, (_, row) in enumerate(pl_cat.iterrows()):
            for col in ["anotador1_categoria", "anotador2_categoria", "anotador3_categoria"]:
                v = int(row[col])
                if 1 <= v <= 11:
                    matriz_cat[i, v - 1] += 1
        kappa_cat = fleiss_kappa(matriz_cat)
        print(f"📊 Fleiss κ (categoria 1–11): {kappa_cat:.4f}")
    else:
        kappa_cat = float("nan")

    # Salva relatório
    rel = pd.DataFrame({
        "metrica": ["fleiss_kappa_eh_misogino", "fleiss_kappa_categoria"],
        "valor":   [kappa_eh, kappa_cat],
        "n_itens": [len(pl_eh), len(pl_cat) if len(pl_cat) > 0 else 0],
    })
    rel.to_csv(SAIDA_KAPPA, index=False, encoding="utf-8")
    print(f"💾 Concordância: {SAIDA_KAPPA.name}")

    # Léxico final: maioria "é_misogino" + categoria com mais votos
    print("\n🛠️  Consolidando léxico final...")
    finais = []
    for _, row in pl.iterrows():
        votos_eh = [row.get(c) for c in ["anotador1_eh_misogino",
                                         "anotador2_eh_misogino",
                                         "anotador3_eh_misogino"]]
        votos_eh = [int(v) for v in votos_eh if pd.notna(v)]
        if not votos_eh:
            continue
        maioria_eh = Counter(votos_eh).most_common(1)[0][0]
        if maioria_eh != 1:
            continue
        votos_cat = [row.get(c) for c in ["anotador1_categoria",
                                          "anotador2_categoria",
                                          "anotador3_categoria"]]
        votos_cat = [int(v) for v in votos_cat if pd.notna(v) and v != ""]
        if not votos_cat:
            continue
        cat_maioria = Counter(votos_cat).most_common(1)[0][0]
        nome = ANCORAS.get(cat_maioria, {}).get("nome", "?")
        finais.append({
            "term": row["term"],
            "categoria_id": cat_maioria,
            "categoria_nome": nome,
            "votos_eh_misogino": "/".join(map(str, votos_eh)),
            "votos_categoria": "/".join(map(str, votos_cat)),
        })

    df_final = pd.DataFrame(finais)
    df_final.to_csv(SAIDA_FINAL_CSV, index=False, encoding="utf-8")
    df_final.to_json(SAIDA_FINAL_JSON, orient="records", force_ascii=False, indent=2)
    print(f"💾 Léxico final validado: {SAIDA_FINAL_CSV.name}  ({len(df_final)} termos)")
    print("\nDistribuição por categoria:")
    print(df_final["categoria_nome"].value_counts().to_string())


# ============================================================
# MAIN
# ============================================================

def main():
    ap = argparse.ArgumentParser(description="Anotação + validação do léxico V3")
    ap.add_argument("--gerar-planilha", action="store_true",
                    help="Anota o V3 e gera a planilha de votação em branco.")
    ap.add_argument("--consolidar", action="store_true",
                    help="Lê os votos preenchidos e gera o léxico validado final.")
    args = ap.parse_args()

    if not args.gerar_planilha and not args.consolidar:
        ap.error("Escolha --gerar-planilha ou --consolidar")

    DIR_SAIDA.mkdir(parents=True, exist_ok=True)

    if args.gerar_planilha:
        df_anot = anotar_lexico()
        gerar_planilha_votacao(df_anot)

    if args.consolidar:
        consolidar_votos()


if __name__ == "__main__":
    main()
