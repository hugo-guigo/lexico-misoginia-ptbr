#!/usr/bin/env python3
"""
Classificador de misoginia — SVM + TF-IDF + score do léxico
"""
import re
import pandas as pd
import numpy as np
from pathlib import Path
from nltk.stem import RSLPStemmer
import nltk
nltk.download('rslp', quiet=True)

from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from scipy.sparse import hstack, csr_matrix
from sklearn.metrics import classification_report

# ==============================
# 1. CARREGAR DADOS E LÉXICO
# ==============================
df = pd.read_csv("corpus_unificado_final.csv").dropna(subset=["text", "label"])
df["label"] = df["label"].astype(int)

lex_df = pd.read_csv("lexico_misoginia_output/lexico_misoginia_v1.csv")
term_score = dict(zip(lex_df["term"], lex_df["score"]))

stemmer = RSLPStemmer()

print(f"Total documentos: {len(df)}")
print(f"Misóginos: {(df['label']==1).sum()} | Não-misóginos: {(df['label']==0).sum()}")

# ==============================
# 2. PRÉ-PROCESSAMENTO
# ==============================
def preprocess(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|@\w+|#\w+', '', text)
    text = re.sub(r'[^a-záéíóúãõâêîôûàèìòùç\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def stemmed_text(texts):
    result = []
    for text in texts:
        tokens = re.findall(r"\b\w+\b", preprocess(text))
        stems = [stemmer.stem(t) for t in tokens]
        result.append(" ".join(stems))
    return result

# ==============================
# 3. FEATURE: SCORE DO LÉXICO
# ==============================
def lexicon_features(texts):
    scores = []
    for text in texts:
        tokens = re.findall(r"\b\w+\b", preprocess(text))
        stems = [stemmer.stem(t) for t in tokens]
        bigrams = [stems[i] + "_" + stems[i+1] for i in range(len(stems)-1)]
        features = stems + bigrams
        matched = [term_score[f] for f in features if f in term_score]
        if not matched:
            mean_s = 0.0
            misog_ratio = 0.0
        else:
            mean_s = sum(matched) / len(matched)
            misog_ratio = sum(1 for s in matched if s > 0) / len(matched)
        scores.append([mean_s, misog_ratio, len(matched)])
    return csr_matrix(np.array(scores))

# ==============================
# 4. MONTAR FEATURES COMBINADAS
# ==============================
print("\n⏳ Extraindo features...")

texts = df["text"].tolist()
y = df["label"].values

# TF-IDF sobre stems
stems = stemmed_text(texts)
tfidf = TfidfVectorizer(max_features=50000, ngram_range=(1,2), min_df=3, sublinear_tf=True)
X_tfidf = tfidf.fit_transform(stems)

# Score do léxico (3 features numéricas)
X_lex = lexicon_features(texts)

# Concatenar
X = hstack([X_tfidf, X_lex])
print(f"✅ Features: TF-IDF {X_tfidf.shape[1]} + léxico 3 = {X.shape[1]} total")

# Concatenar
X_hybrid = hstack([X_tfidf, X_lex])
X_tfidf_only = X_tfidf

print(f"✅ Features híbridas: TF-IDF {X_tfidf.shape[1]} + léxico 3 = {X_hybrid.shape[1]} total")
print(f"✅ Features TF-IDF puro: {X_tfidf_only.shape[1]}")# ==============================

# ==============================
# 5. CROSS-VALIDATION
# ==============================
print("\n⏳ Rodando cross-validation (5 folds)...")

feature_sets = {
    "TF-IDF only": X_tfidf_only,
    "TF-IDF + Lexicon": X_hybrid
}

models = {
    "LinearSVC": LinearSVC(class_weight='balanced', max_iter=3000, C=0.5),
    "LogisticRegression": LogisticRegression(class_weight='balanced', max_iter=3000, C=0.5, solver='saga')
}

for feat_name, X_current in feature_sets.items():
    print(f"\n##############################")
    print(f"FEATURE SET: {feat_name}")
    print(f"##############################")
    
    for name, model in models.items():
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        results = cross_validate(model, X_current, y, cv=cv,
                                 scoring=['f1', 'precision', 'recall'], n_jobs=-1)
        print(f"\n=== {name} ===")
        print(f"  F1:        {results['test_f1'].mean():.4f} ± {results['test_f1'].std():.4f}")
        print(f"  Precision: {results['test_precision'].mean():.4f} ± {results['test_precision'].std():.4f}")
        print(f"  Recall:    {results['test_recall'].mean():.4f} ± {results['test_recall'].std():.4f}")# ==============================

# ==============================
# 6. AJUSTE FINO PARA PRECISION (pesquisa)
# ==============================
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report

feature_sets = {
    "TF-IDF only": X_tfidf_only,
    "TF-IDF + Lexicon": X_hybrid
}

for feat_name, X_current in feature_sets.items():
    print(f"\n====================================")
    print(f"AJUSTE FINO — {feat_name}")
    print(f"====================================")

    X_train, X_test, y_train, y_test = train_test_split(
        X_current, y, test_size=0.2, stratify=y, random_state=42
    )

    print("\n=== AJUSTE DE C — foco em precision ===")
    best_C = None
    best_precision = 0

    for C in [0.01, 0.05, 0.1, 0.3, 0.5, 1.0]:
        m = LinearSVC(class_weight=None, max_iter=2000, C=C)
        m.fit(X_train, y_train)
        y_pred = m.predict(X_test)

        p = precision_score(y_test, y_pred)
        r = recall_score(y_test, y_pred)
        f = f1_score(y_test, y_pred)

        marker = ""
        if p > best_precision:
            best_precision = p
            best_C = C
            marker = " ← MELHOR PRECISION"

        print(f"  C={C:.2f} | Precision: {p:.4f} | Recall: {r:.4f} | F1: {f:.4f}{marker}")

    print(f"\n=== RELATÓRIO FINAL — {feat_name} | melhor C por precision = {best_C:.2f} ===")
    final = LinearSVC(class_weight=None, max_iter=2000, C=best_C)
    final.fit(X_train, y_train)
    y_pred_final = final.predict(X_test)
    print(classification_report(y_test, y_pred_final))
