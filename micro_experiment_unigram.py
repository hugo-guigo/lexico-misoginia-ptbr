from pathlib import Path
import pandas as pd
import re
from sklearn.metrics import classification_report
from nltk.stem import RSLPStemmer
import nltk
from nltk.util import bigrams

nltk.download('rslp')

stemmer = RSLPStemmer()

# ==============================
# 1. CARREGAR TODOS OS CORPUS (RECURSIVO)
# ==============================

corpus_path = "corpus_unificado_final.csv"
df = pd.read_csv(corpus_path)

# ==============================
# 2. CARREGAR LÉXICO
# ==============================

lex_path = "lexico_misoginia_output/lexico_misoginia_v1.csv"
lex_df = pd.read_csv(lex_path)
term_score = dict(zip(lex_df["term"], lex_df["score"]))
print("\n=== DISTRIBUIÇÃO DOS SCORES ===")
print(lex_df["score"].describe())

# ==============================
# 3. LIMPEZA DO DATASET
# ==============================

print("Labels NaN:", df["label"].isna().sum())

df = df.dropna(subset=["label", "text"])
df["label"] = df["label"].astype(int)

print("Total documentos para teste:", len(df))

y_true = df["label"]

# ==============================
# 4. FUNÇÃO DE PREDIÇÃO (UNIGRAMA)
# ==============================
def predict_text(text, threshold):

    tokens = re.findall(r"\b\w+\b", str(text).lower())
    stems = [stemmer.stem(token) for token in tokens]

    bigrams = [
        stems[i] + "_" + stems[i+1]
        for i in range(len(stems) - 1)
    ]

    features = stems + bigrams

    total_score = sum(term_score.get(f, 0) for f in features)

    return 1 if total_score >= threshold else 0

# ==============================
# 5. GRID SEARCH DE THRESHOLD (vetorizado)
# ==============================
from sklearn.metrics import f1_score, classification_report
import numpy as np

y_true = df["label"]

print("⏳ Pré-computando scores...")

def compute_score(text):
    tokens = re.findall(r"\b\w+\b", str(text).lower())
    stems = [stemmer.stem(t) for t in tokens]
    bigrams_list = [stems[i] + "_" + stems[i+1] for i in range(len(stems) - 1)]
    features = stems + bigrams_list
    
    matched_scores = [term_score[f] for f in features if f in term_score]
    
    if not matched_scores:
        return 0.0
    
    mean_score = sum(matched_scores) / len(matched_scores)
    
    # Bônus proporcional à presença de termos misóginos
    misog_scores = [s for s in matched_scores if s > 0]
    misog_ratio = len(misog_scores) / len(matched_scores)
    
    return mean_score + misog_ratio * 2

# Calcula todos os scores UMA VEZ só
scores = df["text"].apply(compute_score)
print(f"✅ Scores computados para {len(scores)} documentos")

# Busca fina de threshold
thresholds = np.arange(-6, 3, 0.25)
best_threshold = None
best_f1 = 0
results = []

for t in thresholds:
    y_pred = (scores >= t).astype(int)
    f1 = f1_score(y_true, y_pred, pos_label=1)
    results.append((t, f1))
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = t

print("\n=== F1 (classe misógina) por threshold ===")
for t, f1 in results:
    marker = " ← MELHOR" if t == best_threshold else ""
    print(f"  Threshold {t:+.1f} | F1: {f1:.4f}{marker}")

print(f"\n=== RELATÓRIO COMPLETO — threshold {best_threshold} ===")
y_pred_best = (scores >= best_threshold).astype(int)
print(classification_report(y_true, y_pred_best))
