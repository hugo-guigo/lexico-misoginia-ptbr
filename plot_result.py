#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from collections import defaultdict

import nltk
from nltk.stem import RSLPStemmer

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    average_precision_score,
)

# =========================
# Utilidades
# =========================

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def clean_text_basic(text: str) -> str:
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize_and_stem(text: str, stemmer: RSLPStemmer):
    tokens = re.findall(r"\b\w+\b", clean_text_basic(text))
    # stem em tudo (mesma lógica que você usou no micro experimento)
    return [stemmer.stem(tok) for tok in tokens if tok]

def extract_unigrams_and_bigrams(stems):
    unis = stems
    bis = [f"{stems[i]}_{stems[i+1]}" for i in range(len(stems) - 1)]
    return unis, bis

def load_lexicon_scores(lex_path: str):
    lex_df = pd.read_csv(lex_path)
    # espera colunas: term, score
    term2score = dict(zip(lex_df["term"].astype(str), lex_df["score"].astype(float)))
    return lex_df, term2score

def lexicon_doc_score(text: str, term2score: dict, stemmer: RSLPStemmer,
                      use_bigrams=True, use_unigrams=True):
    stems = tokenize_and_stem(text, stemmer)
    unis, bis = extract_unigrams_and_bigrams(stems)

    matched_scores = []

    if use_unigrams:
        for u in unis:
            s = term2score.get(u)
            if s is not None:
                matched_scores.append(float(s))

    if use_bigrams:
        for b in bis:
            s = term2score.get(b)
            if s is not None:
                matched_scores.append(float(s))

    if not matched_scores:
        return 0.0, 0.0, 0  # mean_score, misog_ratio, count

    matched_scores = np.array(matched_scores, dtype=float)
    mean_score = float(matched_scores.mean())
    misog_ratio = float((matched_scores > 0).mean())
    count = int(len(matched_scores))
    return mean_score, misog_ratio, count

def lexicon_final_score(mean_score: float, misog_ratio: float):
    # Fórmula que vocês usaram:
    # score = mean_score + misog_ratio * 2
    return mean_score + misog_ratio * 2.0

def plot_confusion_matrix(cm, labels, title, outpath: Path):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(cm)
    ax.set_title(title)
    ax.set_xlabel("Predito")
    ax.set_ylabel("Verdadeiro")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    # valores na matriz
    for (i, j), v in np.ndenumerate(cm):
        ax.text(j, i, str(v), ha="center", va="center")

    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)

def plot_hist(values, title, xlabel, outpath: Path, bins=60):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(values, bins=bins)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequência")
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)

def plot_f1_vs_threshold(thresholds, f1s, best_t, best_f1, outpath: Path):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(thresholds, f1s)
    ax.set_title("F1 (classe misógina) vs threshold — Léxico")
    ax.set_xlabel("Threshold")
    ax.set_ylabel("F1 (classe 1)")
    ax.axvline(best_t)
    ax.text(best_t, best_f1, f"  best={best_t:.2f}", va="bottom")
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)

def plot_pr_curve(y_true, decision_scores, outpath: Path):
    precision, recall, thr = precision_recall_curve(y_true, decision_scores)
    ap = average_precision_score(y_true, decision_scores)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(recall, precision)
    ax.set_title(f"Precision–Recall Curve (AP={ap:.4f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)
    return ap

# =========================
# Main
# =========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="corpus_unificado_final.csv")
    parser.add_argument("--lexicon", default="lexico_misoginia_output/lexico_misoginia_v1.csv")
    parser.add_argument("--outdir", default="outputs/plots")
    parser.add_argument("--lex_threshold", type=float, default=-2.25,
                        help="threshold final do léxico (score_doc >= t => class 1)")
    parser.add_argument("--scan_min", type=float, default=-6.0)
    parser.add_argument("--scan_max", type=float, default=3.0)
    parser.add_argument("--scan_step", type=float, default=0.2)
    parser.add_argument("--holdout", type=float, default=0.20)
    parser.add_argument("--svm_c", type=float, default=0.30)
    parser.add_argument("--max_features", type=int, default=50000)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    ensure_dir(outdir)

    # NLTK stemmer
    nltk.download("rslp", quiet=True)
    stemmer = RSLPStemmer()

    # -------------------------
    # Carregar dados e léxico
    # -------------------------
    df = pd.read_csv(args.corpus)
    df = df.dropna(subset=["text", "label"]).copy()
    df["label"] = df["label"].astype(int)
    df["text"] = df["text"].astype(str)

    lex_df, term2score = load_lexicon_scores(args.lexicon)

    # salvar um resumo numérico do léxico
    lex_score_desc = lex_df["score"].describe().to_dict()

    # -------------------------
    # 1) RESULTADOS — LÉXICO PURO
    # -------------------------
    print("⏳ Computando score do léxico por documento...")
    mean_scores = []
    misog_ratios = []
    counts = []
    final_scores = []

    for t in df["text"].values:
        mean_s, ratio, c = lexicon_doc_score(
            t, term2score, stemmer,
            use_bigrams=True,  # seu léxico agora tem unigram+bigram
            use_unigrams=True
        )
        mean_scores.append(mean_s)
        misog_ratios.append(ratio)
        counts.append(c)
        final_scores.append(lexicon_final_score(mean_s, ratio))

    df["lex_mean_score"] = mean_scores
    df["lex_misog_ratio"] = misog_ratios
    df["lex_match_count"] = counts
    df["lex_final_score"] = final_scores

    # Histograma score doc
    plot_hist(
        df["lex_final_score"].values,
        title="Distribuição do score do léxico por documento",
        xlabel="lex_final_score",
        outpath=outdir / "lexicon_doc_score_hist.png",
        bins=80
    )

    # Histograma score termos do léxico
    plot_hist(
        lex_df["score"].values,
        title="Distribuição dos scores dos termos no léxico",
        xlabel="term_score",
        outpath=outdir / "lexicon_term_score_hist.png",
        bins=80
    )

    # F1 vs threshold scan
    thresholds = np.arange(args.scan_min, args.scan_max + 1e-9, args.scan_step)
    f1s = []

    y_true = df["label"].values
    for thr in thresholds:
        y_pred = (df["lex_final_score"].values >= thr).astype(int)
        # F1 da classe 1:
        # cálculo manual simples pra não depender de average options
        tp = int(((y_true == 1) & (y_pred == 1)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())
        prec = tp / (tp + fp + 1e-9)
        rec = tp / (tp + fn + 1e-9)
        f1 = 2 * prec * rec / (prec + rec + 1e-9)
        f1s.append(float(f1))

    f1s = np.array(f1s, dtype=float)
    best_idx = int(np.argmax(f1s))
    best_t = float(thresholds[best_idx])
    best_f1 = float(f1s[best_idx])

    plot_f1_vs_threshold(
        thresholds, f1s, best_t, best_f1,
        outpath=outdir / "lexicon_f1_vs_threshold.png"
    )

    # Confusion matrix no threshold escolhido (args.lex_threshold)
    lex_thr = float(args.lex_threshold)
    y_pred_lex = (df["lex_final_score"].values >= lex_thr).astype(int)
    cm_lex = confusion_matrix(y_true, y_pred_lex, labels=[0, 1])
    plot_confusion_matrix(
        cm_lex, labels=["0", "1"],
        title=f"Matriz de confusão — Léxico (thr={lex_thr})",
        outpath=outdir / "lexicon_confusion_matrix.png"
    )

    lex_report = classification_report(y_true, y_pred_lex, digits=4, output_dict=True)

    # -------------------------
    # 2) RESULTADOS — CLASSIFICADOR SVM (holdout)
    # -------------------------
    print("⏳ Treinando SVM (holdout) para gerar PR curve e matriz de confusão...")
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"].values, df["label"].values,
        test_size=args.holdout,
        random_state=42,
        stratify=df["label"].values
    )

    # TF-IDF com limpeza+stemming (aprox do que vocês fizeram)
    # (Mantém compatibilidade sem precisar “stemmer dentro do vectorizer” muito complexo.)
    def analyzer(text):
        stems = tokenize_and_stem(text, stemmer)
        # ngrams 1-2 em stems
        unis, bis = extract_unigrams_and_bigrams(stems)
        return unis + bis

    vectorizer = TfidfVectorizer(
        analyzer=analyzer,
        max_features=args.max_features,
        sublinear_tf=True
    )

    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    clf = LinearSVC(C=args.svm_c)
    clf.fit(Xtr, y_train)

    # decision scores (para PR curve)
    decision = clf.decision_function(Xte)
    y_pred = (decision >= 0).astype(int)  # regra padrão do LinearSVC

    svm_report = classification_report(y_test, y_pred, digits=4, output_dict=True)
    cm_svm = confusion_matrix(y_test, y_pred, labels=[0, 1])

    plot_confusion_matrix(
        cm_svm, labels=["0", "1"],
        title=f"Matriz de confusão — LinearSVC (C={args.svm_c})",
        outpath=outdir / "svm_confusion_matrix.png"
    )

    ap = plot_pr_curve(
        y_true=y_test,
        decision_scores=decision,
        outpath=outdir / "svm_precision_recall_curve.png"
    )

    plot_hist(
        decision,
        title="Distribuição do decision_function — LinearSVC",
        xlabel="decision score",
        outpath=outdir / "svm_decision_score_hist.png",
        bins=80
    )

    # -------------------------
    # Salvar um resumo em JSON (pra colar no PRISM)
    # -------------------------
    summary = {
        "corpus": {
            "n_docs": int(len(df)),
            "n_pos": int((df["label"] == 1).sum()),
            "n_neg": int((df["label"] == 0).sum()),
        },
        "lexicon": {
            "path": args.lexicon,
            "n_terms": int(len(lex_df)),
            "score_describe": lex_score_desc,
            "best_threshold_f1_scan": {"threshold": best_t, "f1_pos": best_f1},
            "chosen_threshold": lex_thr,
            "classification_report_at_chosen_threshold": lex_report,
            "confusion_matrix_at_chosen_threshold": cm_lex.tolist(),
        },
        "svm": {
            "holdout": float(args.holdout),
            "C": float(args.svm_c),
            "max_features": int(args.max_features),
            "classification_report": svm_report,
            "confusion_matrix": cm_svm.tolist(),
            "average_precision": float(ap),
        },
        "outputs": {
            "plots_dir": str(outdir),
            "plots": [
                "lexicon_doc_score_hist.png",
                "lexicon_term_score_hist.png",
                "lexicon_f1_vs_threshold.png",
                "lexicon_confusion_matrix.png",
                "svm_precision_recall_curve.png",
                "svm_confusion_matrix.png",
                "svm_decision_score_hist.png",
            ],
        },
    }

    with open(outdir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n✅ Pronto!")
    print(f"📁 Gráficos e métricas em: {outdir.resolve()}")
    print("🧾 Arquivo resumo: metrics_summary.json")

if __name__ == "__main__":
    main()
