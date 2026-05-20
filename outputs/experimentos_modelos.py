#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Tarefas 5 + 6 — Treinamento e comparação de múltiplos modelos.

Modelos comparados:
    - LinearSVC               (Tarefa 5: baseline; já existia em classifier.py)
    - LogisticRegression
    - RandomForestClassifier
    - MLPClassifier           (PROXY de RNN — ver TODO abaixo)

Features:
    - TF-IDF de lemas spaCy (mesmo pré-processamento da Tarefa 2)
    - Features do léxico V3 validado:
        * mean_score
        * misog_ratio
        * match_count

Avaliação:
    - 5-fold cross-validation no corpus de treino (corpus_unificado_final.csv)
    - Validação final no corpus de teste (outputs/corpus_teste_frases.csv)
    - Comparação votação manual (Tarefa 3) × pipeline automático

Saídas:
    - outputs/resultados_modelos.csv
    - outputs/relatorio_comparacao_votacao_pipeline.txt

⚠️  TODO RNN real: este script usa MLPClassifier como proxy de rede neural porque
    o ambiente não tem torch/tensorflow instalados (ImportError + sem espaço para
    instalar). Quando esses pacotes estiverem disponíveis, substituir o bloco
    `RodadaMLP` por um LSTM/GRU usando embeddings spaCy ou treinados do zero.

Uso:
    python3 outputs/experimentos_modelos.py
"""

from __future__ import annotations

import json
import pickle
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import spacy
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from scipy.sparse import csr_matrix, hstack

# ============================================================
# CONFIGURAÇÕES
# ============================================================

RAIZ = Path(__file__).resolve().parent.parent
CORPUS_TREINO = RAIZ / "corpus_unificado_final.csv"
CORPUS_TESTE  = RAIZ / "outputs" / "corpus_teste_frases.csv"

# Léxico final (após votação humana). Se ainda não existir, cai para o V3 bruto.
LEXICO_FINAL  = RAIZ / "outputs" / "lexico_v3_validado_final.csv"
LEXICO_V3     = RAIZ / "outputs" / "lexico_misoginia_v3_semente_pmi.csv"

# Reaproveita o cache de lemas do pipeline Tarefa 2 (mesmas 35,791 linhas)
CACHE_LEMMAS  = RAIZ / "outputs" / "_cache_lemmas.pkl"

SAIDA_RESULT  = RAIZ / "outputs" / "resultados_modelos.csv"
SAIDA_COMPARA = RAIZ / "outputs" / "relatorio_comparacao_votacao_pipeline.txt"

SPACY_MODEL = "pt_core_news_lg"
ALLOWED_POS = {"NOUN", "VERB", "ADJ", "ADV", "PROPN", "INTJ"}

REGEX_URL = re.compile(r"https?://\S+|www\.\S+")
REGEX_USER = re.compile(r"@\w+")
REGEX_NUM  = re.compile(r"\b\d+\b")
REGEX_NAO_ALPHA = re.compile(r"[^a-záéíóúâêôãõçàü ]", flags=re.IGNORECASE)


def limpar_texto(t: str) -> str:
    if not isinstance(t, str):
        return ""
    t = t.lower()
    t = REGEX_URL.sub(" ", t)
    t = REGEX_USER.sub(" ", t)
    t = REGEX_NUM.sub(" ", t)
    t = REGEX_NAO_ALPHA.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


# ============================================================
# CARREGAMENTO DE DADOS
# ============================================================

def carregar_lexico() -> dict[str, dict]:
    """Carrega o léxico V3 validado se existir; senão usa o V3 bruto."""
    if LEXICO_FINAL.exists():
        print(f"📥 Léxico validado: {LEXICO_FINAL.name}")
        df = pd.read_csv(LEXICO_FINAL)
        # já vem só misógino + categoria
        df["polarity"] = "misogino"
        df["score_norm"] = 1.0
    else:
        print(f"⚠️  Não encontrei {LEXICO_FINAL.name}; usando V3 bruto: {LEXICO_V3.name}")
        df = pd.read_csv(LEXICO_V3)
        df = df[df["polarity"] == "misogino"].copy()
    return {row["term"]: {"polarity": row["polarity"],
                          "score": float(row.get("score_norm", 1.0))}
            for _, row in df.iterrows()}


def carregar_treino() -> pd.DataFrame:
    """Lê o corpus, aplica o mesmo pré-processamento do pipeline Tarefa 2."""
    df = pd.read_csv(CORPUS_TREINO)
    mascara_lixo = df["text"].astype(str).str.fullmatch(r"\s*\d+\s*", na=False)
    df = df[~mascara_lixo].copy()
    df["text"] = df["text"].astype(str)
    df = df[df["text"].str.replace(REGEX_NAO_ALPHA, "", regex=True).str.len() >= 3]
    df = df.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)

    if CACHE_LEMMAS.exists():
        cache = pd.read_pickle(CACHE_LEMMAS)
        if len(cache) == len(df):
            df["lemas"] = cache["lemas"].tolist()
            return df

    # Cache desatualizado: relematizar
    print("♻️  Recriando cache de lemas (vai demorar)")
    nlp = spacy.load(SPACY_MODEL, disable=["parser", "ner"])
    lemas_list = []
    textos_limpos = [limpar_texto(t) for t in df["text"]]
    for doc in nlp.pipe(textos_limpos, batch_size=256):
        lemas = [tok.lemma_.lower() for tok in doc
                 if tok.pos_ in ALLOWED_POS
                 and not tok.is_stop
                 and not tok.is_punct
                 and tok.lemma_.isalpha()
                 and len(tok.lemma_) >= 3]
        lemas_list.append(lemas)
    df["lemas"] = lemas_list
    pd.DataFrame({"lemas": lemas_list}).to_pickle(CACHE_LEMMAS)
    return df


def carregar_teste(nlp: spacy.Language) -> pd.DataFrame:
    """Lê o corpus de teste e lematiza on-the-fly (ele é pequeno)."""
    if not CORPUS_TESTE.exists():
        print(f"⚠️  Corpus de teste {CORPUS_TESTE.name} não existe — pulando avaliação out-of-sample.")
        return pd.DataFrame()
    df = pd.read_csv(CORPUS_TESTE)
    df = df.dropna(subset=["text", "label"])
    df = df[df["text"].astype(str).str.strip() != ""]
    df["label"] = df["label"].astype(int)
    textos = [limpar_texto(t) for t in df["text"]]
    lemas_list = []
    for doc in nlp.pipe(textos, batch_size=128):
        lemas = [tok.lemma_.lower() for tok in doc
                 if tok.pos_ in ALLOWED_POS
                 and not tok.is_stop
                 and not tok.is_punct
                 and tok.lemma_.isalpha()
                 and len(tok.lemma_) >= 3]
        lemas_list.append(lemas)
    df["lemas"] = lemas_list
    return df.reset_index(drop=True)


# ============================================================
# FEATURES
# ============================================================

def features_lexico(lemas_docs: list[list[str]], lexico: dict[str, dict]) -> np.ndarray:
    """Para cada doc: [mean_score, misog_ratio, match_count]."""
    feats = np.zeros((len(lemas_docs), 3))
    for i, lemas in enumerate(lemas_docs):
        matched = [lexico[l]["score"] for l in lemas if l in lexico]
        if matched:
            feats[i, 0] = float(np.mean(matched))
            feats[i, 1] = sum(1 for s in matched if s > 0) / len(lemas)
            feats[i, 2] = len(matched)
    return feats


def construir_features(treino_df, teste_df, lexico):
    """Constrói TF-IDF (treino) + features léxico, para treino e teste."""
    docs_treino_str = [" ".join(l) for l in treino_df["lemas"]]
    vec = TfidfVectorizer(min_df=5, max_df=0.95, ngram_range=(1, 1),
                          max_features=10_000,
                          token_pattern=r"(?u)\b[a-záéíóúâêôãõçàü\-]{3,}\b",
                          sublinear_tf=True)
    X_tfidf_treino = vec.fit_transform(docs_treino_str)
    lex_treino = features_lexico(treino_df["lemas"].tolist(), lexico)
    scaler = StandardScaler()
    lex_treino_s = scaler.fit_transform(lex_treino)
    X_treino = hstack([X_tfidf_treino, csr_matrix(lex_treino_s)])
    y_treino = treino_df["label"].values

    if len(teste_df) > 0:
        X_tfidf_teste = vec.transform([" ".join(l) for l in teste_df["lemas"]])
        lex_teste = scaler.transform(features_lexico(teste_df["lemas"].tolist(), lexico))
        X_teste = hstack([X_tfidf_teste, csr_matrix(lex_teste)])
        y_teste = teste_df["label"].values
    else:
        X_teste, y_teste = None, None

    print(f"   features dim: {X_treino.shape[1]} (TF-IDF {X_tfidf_treino.shape[1]} + léxico 3)")
    return X_treino, y_treino, X_teste, y_teste, vec


# ============================================================
# MODELOS
# ============================================================

def construir_modelos() -> dict[str, object]:
    return {
        "SVM (LinearSVC)":      LinearSVC(class_weight="balanced", max_iter=5000),
        "Regressão Logística":  LogisticRegression(class_weight="balanced",
                                                   max_iter=5000, solver="liblinear"),
        "Random Forest":        RandomForestClassifier(n_estimators=100,
                                                       class_weight="balanced",
                                                       n_jobs=-1, random_state=42,
                                                       max_depth=20),
        # TODO RNN real: trocar por LSTM/GRU quando torch ou tensorflow estiverem
        # disponíveis. Aqui usamos MLP como proxy de modelo neural denso.
        "MLP (proxy RNN)":      MLPClassifier(hidden_layer_sizes=(64,),
                                              max_iter=50, random_state=42,
                                              early_stopping=True,
                                              validation_fraction=0.1,
                                              n_iter_no_change=5),
    }


def avaliar_cv(modelos, X, y, n_splits=3):
    print(f"\n=== Cross-validation {n_splits}-fold (corpus de treino) ===", flush=True)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    resultados = []
    for nome, modelo in modelos.items():
        print(f"   [start] {nome}", flush=True)
        f1s, precs, recs = [], [], []
        for fold, (tr, va) in enumerate(skf.split(X, y), 1):
            print(f"      fold {fold}/{n_splits} fit...", flush=True)
            modelo.fit(X[tr], y[tr])
            pred = modelo.predict(X[va])
            f1s.append(f1_score(y[va], pred, pos_label=1))
            precs.append(precision_score(y[va], pred, pos_label=1, zero_division=0))
            recs.append(recall_score(y[va], pred, pos_label=1, zero_division=0))
            print(f"      fold {fold} F1={f1s[-1]:.3f}  P={precs[-1]:.3f}  R={recs[-1]:.3f}", flush=True)
        resultados.append({
            "modelo": nome, "fonte": "cv_treino",
            "f1_misog":   float(np.mean(f1s)),   "f1_std":   float(np.std(f1s)),
            "prec_misog": float(np.mean(precs)), "prec_std": float(np.std(precs)),
            "rec_misog":  float(np.mean(recs)),  "rec_std":  float(np.std(recs)),
        })
        print(f"   [done]  {nome}  F1={np.mean(f1s):.3f}±{np.std(f1s):.3f}  "
              f"P={np.mean(precs):.3f}  R={np.mean(recs):.3f}", flush=True)
    return resultados


def avaliar_teste(modelos, X_treino, y_treino, X_teste, y_teste):
    print("\n=== Avaliação no corpus de teste (out-of-sample) ===", flush=True)
    resultados = []
    for nome, modelo in modelos.items():
        print(f"   [fit] {nome}", flush=True)
        modelo.fit(X_treino, y_treino)
        pred = modelo.predict(X_teste)
        f1 = f1_score(y_teste, pred, pos_label=1)
        prec = precision_score(y_teste, pred, pos_label=1, zero_division=0)
        rec = recall_score(y_teste, pred, pos_label=1, zero_division=0)
        resultados.append({
            "modelo": nome, "fonte": "teste",
            "f1_misog": f1, "prec_misog": prec, "rec_misog": rec,
        })
        print(f"   {nome:24s}  F1={f1:.3f}  P={prec:.3f}  R={rec:.3f}", flush=True)
        print(classification_report(y_teste, pred, target_names=["nao_mis", "misogino"],
                                    zero_division=0), flush=True)
    return resultados


# ============================================================
# COMPARAÇÃO VOTAÇÃO MANUAL × PIPELINE (Tarefa 6)
# ============================================================

def comparar_votacao_pipeline():
    """
    Compara, para cada termo do léxico V3:
      - categoria escolhida pela maioria do grupo (planilha de votação)
      - categoria sugerida pelo pipeline (anotar_lexico.py)
    """
    planilha = RAIZ / "outputs" / "planilha_votacao_grupo.csv"
    anotado  = RAIZ / "outputs" / "lexico_v3_anotado.csv"
    if not planilha.exists() or not anotado.exists():
        msg = "⚠️  Sem planilha votação ou lexico_v3_anotado.csv — comparação pulada."
        print(msg)
        return msg

    pl = pd.read_csv(planilha)
    an = pd.read_csv(anotado)

    # Maioria por anotador
    cols_cat = ["anotador1_categoria", "anotador2_categoria", "anotador3_categoria"]
    cat_maioria = []
    for _, r in pl.iterrows():
        votos = [int(r[c]) for c in cols_cat if pd.notna(r[c]) and str(r[c]).strip() != ""]
        if not votos:
            cat_maioria.append(np.nan)
            continue
        from collections import Counter
        cat_maioria.append(Counter(votos).most_common(1)[0][0])
    pl["cat_maioria_grupo"] = cat_maioria

    merge = pl[["term", "cat_maioria_grupo"]].merge(
        an[["term", "categoria_id_sugerida"]], on="term", how="inner"
    )
    merge = merge.dropna(subset=["cat_maioria_grupo"])
    merge["categoria_id_sugerida"] = pd.to_numeric(merge["categoria_id_sugerida"],
                                                   errors="coerce")
    merge = merge.dropna(subset=["categoria_id_sugerida"])
    if len(merge) == 0:
        msg = "⚠️  Nenhum termo com voto humano + sugestão automática para comparar."
        print(msg)
        return msg

    concordancia = (merge["cat_maioria_grupo"] == merge["categoria_id_sugerida"]).mean()
    confusao = pd.crosstab(merge["cat_maioria_grupo"], merge["categoria_id_sugerida"],
                           rownames=["voto_humano"], colnames=["pipeline"])
    relatorio = (
        f"Comparação votação manual × pipeline automático\n"
        f"================================================\n"
        f"Termos comparados: {len(merge)}\n"
        f"Concordância: {concordancia:.2%}\n\n"
        f"Matriz de confusão:\n{confusao.to_string()}\n"
    )
    print(relatorio)
    return relatorio


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    print("📥 Carregando léxico final / V3 bruto...")
    lexico = carregar_lexico()
    print(f"   {len(lexico)} termos no léxico")

    print("📥 Carregando corpus de treino (com cache de lemas)...")
    treino_df = carregar_treino()
    print(f"   {len(treino_df):,} docs | misóginos: {(treino_df.label == 1).sum():,}")

    print("📥 Carregando corpus de teste...")
    nlp = spacy.load(SPACY_MODEL, disable=["parser", "ner"])
    teste_df = carregar_teste(nlp)
    print(f"   {len(teste_df)} docs no teste")

    print("\n🛠️  Construindo features...")
    X_tr, y_tr, X_te, y_te, _vec = construir_features(treino_df, teste_df, lexico)

    modelos = construir_modelos()

    cv_resultados = avaliar_cv(modelos, X_tr, y_tr)
    teste_resultados = (avaliar_teste(modelos, X_tr, y_tr, X_te, y_te)
                        if X_te is not None and len(y_te) > 0 else [])

    df_res = pd.DataFrame(cv_resultados + teste_resultados)
    df_res.to_csv(SAIDA_RESULT, index=False, encoding="utf-8")
    print(f"\n💾 Resultados: {SAIDA_RESULT.name}")

    relatorio = comparar_votacao_pipeline()
    SAIDA_COMPARA.write_text(relatorio, encoding="utf-8")
    print(f"💾 Comparação: {SAIDA_COMPARA.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
