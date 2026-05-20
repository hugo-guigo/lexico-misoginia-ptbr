#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Tarefa 2 — Construção do léxico V3 em lemas spaCy.

Etapas:
    1. Pré-processamento: limpeza + lematização (spaCy pt_core_news_lg).
       Resultado cacheado em outputs/_cache_lemmas.parquet.
    2. Etapa 2a — Semente TF-IDF: top-N lemas por classe (misógino vs. não)
       ordenados pelo score discriminativo tfidf_mis / (tfidf_non + eps).
    3. Etapa 2b — Expansão PMI: para cada lema candidato x, calcular
           O(x) = PMI(x, set_mis) - PMI(x, set_nao_mis)
       (Monteles 2023, eq. 3-2). Aceitar |O(x)| >= PMI_THRESHOLD.

Saídas em outputs/:
    - lexico_semente_tfidf.csv             # semente (top-N por classe)
    - lexico_misoginia_v3_semente_pmi.csv  # V3 expandido por PMI
    - lexico_misoginia_v3_semente_pmi.json # mesma coisa em JSON

Uso:
    python3 outputs/pipeline_semente_pmi.py
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

# ============================================================
# CONFIGURAÇÕES
# ============================================================

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CORPUS_PATH  = RAIZ_PROJETO / "corpus_unificado_final.csv"
DIR_SAIDA    = RAIZ_PROJETO / "outputs"
CACHE_LEMMAS = DIR_SAIDA / "_cache_lemmas.pkl"

SAIDA_SEMENTE = DIR_SAIDA / "lexico_semente_tfidf.csv"
SAIDA_V3_CSV  = DIR_SAIDA / "lexico_misoginia_v3_semente_pmi.csv"
SAIDA_V3_JSON = DIR_SAIDA / "lexico_misoginia_v3_semente_pmi.json"

# Parâmetros do pipeline (Monteles, 2023, adaptado)
TOP_N_SEMENTE    = 200    # top N por classe para a semente
MIN_FREQ_SEMENTE = 5      # frequência mínima do lema no subcorpus da classe
PMI_THRESHOLD    = 1.5    # limiar |O(x)| para aceitar o lema na expansão
WINDOW_SIZE      = 5      # janela deslizante de coocorrência
MIN_FREQ_EXPAND  = 5      # frequência mínima do candidato no corpus
MIN_COOCORR      = 3      # mínimo de coocorrências válidas com a semente
EPS_TFIDF        = 1e-6   # epsilon do score discriminativo

# Pré-processamento
MIN_TEXT_LEN     = 3      # descarta textos com menos de 3 caracteres alfabéticos
SPACY_MODEL      = "pt_core_news_lg"
SPACY_BATCH      = 256
SPACY_NPROC      = 1      # spaCy pode falhar com >1 em alguns ambientes
ALLOWED_POS      = {"NOUN", "VERB", "ADJ", "ADV", "PROPN", "INTJ"}

# Stopwords extras de domínio (ruído sem valor discriminativo)
DOMAIN_STOP = {
    "rt", "user", "url", "https", "http", "www", "com", "br",
    "kkk", "kkkk", "kkkkk", "haha", "hehe", "hahah", "hahaha",
    "ne", "tô", "tá", "vc", "voce", "voces", "pra", "ai", "ah",
    "uhuu", "oi", "ola", "obrigad", "obrigada", "obrigado",
}

# ============================================================
# UTILIDADES
# ============================================================

REGEX_URL     = re.compile(r"https?://\S+|www\.\S+")
REGEX_USER    = re.compile(r"@\w+")
REGEX_HASHTAG = re.compile(r"#(\w+)")
REGEX_NUM     = re.compile(r"\b\d+\b")
REGEX_NAO_ALPHA = re.compile(r"[^a-záéíóúâêôãõçàü ]", flags=re.IGNORECASE)


def limpar_texto(texto: str) -> str:
    """Pré-limpeza simples antes da lematização."""
    if not isinstance(texto, str):
        return ""
    t = texto.lower()
    t = REGEX_URL.sub(" ", t)
    t = REGEX_USER.sub(" ", t)
    t = REGEX_HASHTAG.sub(r" \1", t)
    t = REGEX_NUM.sub(" ", t)
    t = REGEX_NAO_ALPHA.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def carregar_corpus() -> pd.DataFrame:
    """Carrega corpus_unificado_final.csv e remove ruído conhecido."""
    print(f"📥 Lendo corpus: {CORPUS_PATH.name}")
    df = pd.read_csv(CORPUS_PATH)
    print(f"   bruto: {len(df):,} docs")

    # Linhas com texto puramente numérico (lixo do source Kappa_Fleiss)
    mascara_lixo = df["text"].astype(str).str.fullmatch(r"\s*\d+\s*", na=False)
    df = df[~mascara_lixo].copy()

    # Textos curtos demais
    df["text"] = df["text"].astype(str)
    df = df[df["text"].str.replace(REGEX_NAO_ALPHA, "", regex=True).str.len() >= MIN_TEXT_LEN]

    # Deduplicar por (text, label)
    df = df.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)

    print(f"   após filtros: {len(df):,} docs")
    print(f"   distribuição label:\n{df['label'].value_counts().to_string()}")
    return df


def carregar_spacy() -> spacy.Language:
    print(f"🧠 Carregando spaCy: {SPACY_MODEL}")
    nlp = spacy.load(SPACY_MODEL, disable=["parser", "ner"])
    return nlp


def lematizar_em_lote(textos: list[str], nlp: spacy.Language) -> list[list[str]]:
    """Lematiza uma lista de textos retornando, para cada um, a lista de lemas filtrados."""
    textos_limpos = [limpar_texto(t) for t in textos]
    docs_lemas: list[list[str]] = []
    total = len(textos_limpos)
    for i, doc in enumerate(nlp.pipe(textos_limpos, batch_size=SPACY_BATCH, n_process=SPACY_NPROC)):
        lemas = []
        for tok in doc:
            if tok.is_stop or tok.is_punct or tok.is_space:
                continue
            if tok.pos_ not in ALLOWED_POS:
                continue
            lema = tok.lemma_.strip().lower()
            if not lema or len(lema) < 3:
                continue
            if lema in DOMAIN_STOP:
                continue
            if not lema.replace("-", "").isalpha():
                continue
            lemas.append(lema)
        docs_lemas.append(lemas)
        if (i + 1) % 5000 == 0:
            print(f"   ... {i + 1:,}/{total:,} docs lematizados")
    return docs_lemas


def lematizar_com_cache(df: pd.DataFrame) -> pd.DataFrame:
    """Carrega o cache de lemas se existir; senão lematiza e salva (pickle)."""
    if CACHE_LEMMAS.exists():
        print(f"♻️  Usando cache de lemas: {CACHE_LEMMAS.name}")
        cache = pd.read_pickle(CACHE_LEMMAS)
        if len(cache) == len(df):
            df = df.copy()
            df["lemas"] = cache["lemas"].tolist()
            return df
        print("   cache desatualizado — refazendo")

    nlp = carregar_spacy()
    print(f"🛠️  Lematizando {len(df):,} documentos (pode demorar)")
    lemas = lematizar_em_lote(df["text"].tolist(), nlp)
    df = df.copy()
    df["lemas"] = lemas
    cache = pd.DataFrame({"lemas": lemas})
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    cache.to_pickle(CACHE_LEMMAS)
    print(f"💾 Cache salvo em {CACHE_LEMMAS.name}")
    return df


# ============================================================
# ETAPA 2a — SEMENTE TF-IDF
# ============================================================

def construir_semente(df: pd.DataFrame) -> pd.DataFrame:
    """Gera a semente: top-N lemas por classe ordenados por score discriminativo."""
    print("\n=== Etapa 2a — Semente TF-IDF ===")
    docs_str = [" ".join(l) for l in df["lemas"]]
    labels = df["label"].values

    vec = TfidfVectorizer(
        min_df=MIN_FREQ_SEMENTE,
        max_df=0.95,
        token_pattern=r"(?u)\b[a-záéíóúâêôãõçàü\-]{3,}\b",
        sublinear_tf=True,
    )
    X = vec.fit_transform(docs_str)
    vocab = np.array(vec.get_feature_names_out())
    print(f"   vocabulário: {len(vocab):,} lemas")

    # Soma de TF-IDF por classe
    mis_idx = np.where(labels == 1)[0]
    non_idx = np.where(labels == 0)[0]
    tfidf_mis = np.asarray(X[mis_idx].sum(axis=0)).flatten()
    tfidf_non = np.asarray(X[non_idx].sum(axis=0)).flatten()

    # Frequência bruta por classe (contagem de docs em que o lema aparece)
    presenca = (X > 0).astype(int)
    freq_mis = np.asarray(presenca[mis_idx].sum(axis=0)).flatten()
    freq_non = np.asarray(presenca[non_idx].sum(axis=0)).flatten()

    score_mis = tfidf_mis / (tfidf_non + EPS_TFIDF)
    score_non = tfidf_non / (tfidf_mis + EPS_TFIDF)

    df_voc = pd.DataFrame({
        "term": vocab,
        "tfidf_mis": tfidf_mis,
        "tfidf_non": tfidf_non,
        "freq_mis": freq_mis,
        "freq_non": freq_non,
        "score_mis": score_mis,
        "score_non": score_non,
    })

    semente_mis = (
        df_voc[df_voc["freq_mis"] >= MIN_FREQ_SEMENTE]
        .sort_values("score_mis", ascending=False)
        .head(TOP_N_SEMENTE)
        .assign(polarity="misogino")
    )
    semente_non = (
        df_voc[df_voc["freq_non"] >= MIN_FREQ_SEMENTE]
        .sort_values("score_non", ascending=False)
        .head(TOP_N_SEMENTE)
        .assign(polarity="nao_misogino")
    )

    semente = pd.concat([semente_mis, semente_non], ignore_index=True)
    semente["origem"] = "tfidf_seed"
    semente["score_norm"] = np.where(
        semente["polarity"] == "misogino",
        semente["score_mis"],
        semente["score_non"],
    )

    cols = ["term", "polarity", "score_norm", "freq_mis", "freq_non",
            "tfidf_mis", "tfidf_non", "score_mis", "score_non", "origem"]
    semente = semente[cols]
    semente.to_csv(SAIDA_SEMENTE, index=False, encoding="utf-8")
    print(f"💾 Semente salva: {SAIDA_SEMENTE.name} ({len(semente)} termos)")
    print(f"   misógino: {(semente.polarity == 'misogino').sum()}  | "
          f"não-misógino: {(semente.polarity == 'nao_misogino').sum()}")
    return semente


# ============================================================
# ETAPA 2b — EXPANSÃO POR PMI
# ============================================================

def contar_coocorrencias(
    docs_lemas: list[list[str]],
    set_alvo: set[str],
    janela: int,
) -> tuple[dict[str, int], dict[str, int], int]:
    """
    Para cada lema do corpus, conta:
      - cooc_alvo[x]  = nº de janelas em que x co-ocorre com algum lema do set_alvo
      - freq_x[x]     = nº total de ocorrências de x
    Retorna também o total de janelas analisadas (para normalizar PMI).
    """
    cooc_alvo: dict[str, int] = defaultdict(int)
    freq_x:    dict[str, int] = defaultdict(int)
    total_janelas = 0

    for lemas in docs_lemas:
        n = len(lemas)
        for i, lema in enumerate(lemas):
            freq_x[lema] += 1
            ini = max(0, i - janela)
            fim = min(n, i + janela + 1)
            janela_lemas = lemas[ini:i] + lemas[i + 1:fim]
            total_janelas += 1
            if any(j in set_alvo for j in janela_lemas):
                cooc_alvo[lema] += 1

    return cooc_alvo, freq_x, total_janelas


def calcular_pmi_set(
    docs_lemas: list[list[str]],
    set_alvo: set[str],
    janela: int,
) -> tuple[dict[str, float], dict[str, int]]:
    """
    PMI(x, set_alvo) = log( P(x, set_alvo) / (P(x) * P(set_alvo)) ).
    Aqui as probabilidades são estimadas em nível de janelas.
    """
    cooc, freq, total = contar_coocorrencias(docs_lemas, set_alvo, janela)
    if total == 0:
        return {}, freq

    # P(set_alvo) = nº de janelas com ao menos um membro do set_alvo / total
    p_alvo = sum(cooc.values()) / total if total else 0
    p_alvo = max(p_alvo, 1e-12)

    pmi: dict[str, float] = {}
    for x, c in cooc.items():
        p_x = freq[x] / total
        p_xy = c / total
        if p_x <= 0 or p_xy <= 0:
            continue
        pmi[x] = math.log(p_xy / (p_x * p_alvo))
    return pmi, freq


def expandir_por_pmi(
    df: pd.DataFrame,
    semente: pd.DataFrame,
) -> pd.DataFrame:
    """Etapa 2b — calcula O(x) = PMI(x, set_mis) − PMI(x, set_não_mis) e filtra."""
    print("\n=== Etapa 2b — Expansão PMI ===")
    set_mis = set(semente.loc[semente.polarity == "misogino", "term"])
    set_non = set(semente.loc[semente.polarity == "nao_misogino", "term"])
    print(f"   set semente — misógino: {len(set_mis)}  | não-misógino: {len(set_non)}")

    docs_lemas = df["lemas"].tolist()

    print("   calculando PMI com set misógino...")
    pmi_mis, freq_total = calcular_pmi_set(docs_lemas, set_mis, WINDOW_SIZE)
    print("   calculando PMI com set não-misógino...")
    pmi_non, _ = calcular_pmi_set(docs_lemas, set_non, WINDOW_SIZE)

    # Coocorrências brutas para o filtro MIN_COOCORR
    cooc_mis, _, _ = contar_coocorrencias(docs_lemas, set_mis, WINDOW_SIZE)
    cooc_non, _, _ = contar_coocorrencias(docs_lemas, set_non, WINDOW_SIZE)

    # Frequência por classe
    print("   computando freq_mis / freq_non por documento...")
    labels = df["label"].values
    freq_mis_doc: dict[str, int] = defaultdict(int)
    freq_non_doc: dict[str, int] = defaultdict(int)
    for lemas, lab in zip(docs_lemas, labels):
        unique = set(lemas)
        if lab == 1:
            for x in unique:
                freq_mis_doc[x] += 1
        else:
            for x in unique:
                freq_non_doc[x] += 1

    # Calcula O(x) para todos os lemas com frequência mínima
    registros = []
    todos_lemas = set(freq_total.keys())
    for x in todos_lemas:
        if freq_total[x] < MIN_FREQ_EXPAND:
            continue
        c_mis = cooc_mis.get(x, 0)
        c_non = cooc_non.get(x, 0)
        if (c_mis + c_non) < MIN_COOCORR:
            continue
        pm = pmi_mis.get(x, 0.0)
        pn = pmi_non.get(x, 0.0)
        ox = pm - pn
        registros.append({
            "term": x,
            "O_score": ox,
            "pmi_mis": pm,
            "pmi_non": pn,
            "cooc_mis": c_mis,
            "cooc_non": c_non,
            "freq_total": freq_total[x],
            "freq_mis": freq_mis_doc.get(x, 0),
            "freq_non": freq_non_doc.get(x, 0),
        })

    df_exp = pd.DataFrame(registros)
    print(f"   candidatos pós-filtros básicos: {len(df_exp):,}")

    df_exp = df_exp[df_exp["O_score"].abs() >= PMI_THRESHOLD].copy()
    df_exp["polarity"] = np.where(df_exp["O_score"] > 0, "misogino", "nao_misogino")
    df_exp["score_norm"] = df_exp["O_score"].abs()

    # Marca quais termos já vinham da semente
    set_semente = set(semente["term"])
    df_exp["origem"] = np.where(df_exp["term"].isin(set_semente), "semente+pmi", "pmi_expandido")

    df_exp = df_exp.sort_values(["polarity", "score_norm"], ascending=[True, False])
    cols = ["term", "polarity", "score_norm", "O_score", "pmi_mis", "pmi_non",
            "cooc_mis", "cooc_non", "freq_mis", "freq_non", "freq_total", "origem"]
    df_exp = df_exp[cols].reset_index(drop=True)

    n_mis = (df_exp.polarity == "misogino").sum()
    n_non = (df_exp.polarity == "nao_misogino").sum()
    print(f"   V3 final — misógino: {n_mis}  | não-misógino: {n_non}  (|O(x)| ≥ {PMI_THRESHOLD})")

    return df_exp


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)

    df = carregar_corpus()
    df = lematizar_com_cache(df)

    semente = construir_semente(df)
    v3 = expandir_por_pmi(df, semente)

    v3.to_csv(SAIDA_V3_CSV, index=False, encoding="utf-8")
    v3.to_json(SAIDA_V3_JSON, orient="records", force_ascii=False, indent=2)
    print(f"\n💾 V3 salvo: {SAIDA_V3_CSV.name}  +  {SAIDA_V3_JSON.name}")
    print(f"   total de termos: {len(v3)}")

    # Amostras
    print("\nTOP 20 termos misóginos (V3):")
    print(v3[v3.polarity == "misogino"].head(20).to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
