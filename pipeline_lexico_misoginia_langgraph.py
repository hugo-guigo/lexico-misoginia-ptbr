# ==========================================================
# PIPELINE DE CONSTRUÇÃO DE LÉXICO DE MISOGINIA (LANGGRAPH)
# ==========================================================

import os
import re
import glob
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from typing import TypedDict, List

import spacy
from gensim.models import FastText
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

import matplotlib.pyplot as plt
from wordcloud import WordCloud

from langgraph.graph import StateGraph

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

BASE_CORPUS_DIR = "lexicons_corpus_misoginia"
OUTPUT_DIR = "outputs"
LIMIAR_SCORE = 0.2
N_CLUSTERS = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🔧 Carregando spaCy pt_core_news_lg...")
nlp = spacy.load("pt_core_news_lg")
print("✅ spaCy carregado")

STOPWORDS = nlp.Defaults.stop_words


# ==========================================================
# ESTADO GLOBAL DO GRAFO
# ==========================================================

class LexiconState(TypedDict):
    texts: List[str]
    labels: List[int]
    lex_lem: pd.DataFrame
    lex_raw: pd.DataFrame


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def limpar_texto(texto: str) -> List[str]:
    texto = texto.lower()
    texto = re.sub(r"http\S+|www\S+", "", texto)
    texto = re.sub(r"[^a-zà-ú\s]", " ", texto)
    tokens = [t for t in texto.split() if len(t) > 2 and t not in STOPWORDS]
    return tokens


def score_associacao(f_mis, f_non):
    if f_mis + f_non == 0:
        return 0.0
    return (f_mis - f_non) / (f_mis + f_non)


# ==========================================================
# NÓ 1 — CARREGAMENTO DOS CORPORA
# ==========================================================

def load_corpus(state: LexiconState):
    texts, labels = [], []

    for csv_path in glob.glob(f"{BASE_CORPUS_DIR}/**/*.csv", recursive=True):
        try:
            df = pd.read_csv(csv_path)
        except:
            continue

        text_col = None
        label_col = None

        for c in df.columns:
            if c.lower() in ["text", "comment", "comentario"]:
                text_col = c
            if "misog" in c.lower() or "label" in c.lower():
                label_col = c

        if not text_col or not label_col:
            continue

        for _, row in df.iterrows():
            if pd.isna(row[text_col]) or pd.isna(row[label_col]):
                continue
            texts.append(str(row[text_col]))
            labels.append(int(row[label_col]))

    print(f"📊 TOTAL FINAL: {len(texts)} documentos")
    state["texts"] = texts
    state["labels"] = labels
    return state


# ==========================================================
# NÓ 2 — CONSTRUÇÃO DO LÉXICO
# ==========================================================

def construir_lexico(texts, labels, lematizar=True):
    freq_mis = Counter()
    freq_non = Counter()

    for texto, label in zip(texts, labels):
        tokens = limpar_texto(texto)
        if lematizar:
            doc = nlp(" ".join(tokens))
            tokens = [t.lemma_ for t in doc if t.lemma_ not in STOPWORDS]

        for t in tokens:
            if label == 1:
                freq_mis[t] += 1
            else:
                freq_non[t] += 1

    rows = []
    for termo in set(freq_mis) | set(freq_non):
        fm = freq_mis[termo]
        fn = freq_non[termo]
        score = score_associacao(fm, fn)
        polarity = "misogynistic" if score >= LIMIAR_SCORE else "non-misogynistic"
        lex_type = "core" if score >= LIMIAR_SCORE else "contextual"

        rows.append([termo, fm, fn, score, polarity, lex_type])

    return pd.DataFrame(
        rows,
        columns=["term", "freq_misogynistic", "freq_non_misogynistic",
                 "score", "polarity", "lexicon_type"]
    )


def build_lexicons(state: LexiconState):
    print("🔨 Construindo léxico LEMATIZADO...")
    state["lex_lem"] = construir_lexico(
        state["texts"], state["labels"], lematizar=True
    )

    print("🔨 Construindo léxico NÃO lematizado...")
    state["lex_raw"] = construir_lexico(
        state["texts"], state["labels"], lematizar=False
    )

    state["lex_lem"].to_csv(f"{OUTPUT_DIR}/lexico_lematizado.csv", index=False)
    state["lex_raw"].to_csv(f"{OUTPUT_DIR}/lexico_nao_lematizado.csv", index=False)

    return state


# ==========================================================
# NÓ 3 — CLUSTERIZAÇÃO + FASTTEXT
# ==========================================================

def clusterizar(df: pd.DataFrame, tag: str):
    termos = df["term"].tolist()

    model = FastText(
        sentences=[[t] for t in termos],
        vector_size=100,
        window=3,
        min_count=1,
        workers=4,
        epochs=50
    )

    X = np.array([model.wv[t] for t in termos])

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    labels = kmeans.fit_predict(X)

    df["cluster"] = labels
    df.to_csv(f"{OUTPUT_DIR}/lexico_{tag}_clusterizado.csv", index=False)

    sil = silhouette_score(X, labels)
    print(f"📐 Silhouette ({tag}): {sil:.3f}")

    # PCA plot
    pca = PCA(n_components=2)
    X2 = pca.fit_transform(X)

    plt.figure(figsize=(8, 6))
    plt.scatter(X2[:, 0], X2[:, 1], c=labels)
    plt.title(f"Clusterização ({tag})")
    plt.savefig(f"{OUTPUT_DIR}/clusters_{tag}.png")
    plt.close()

    # Wordcloud por cluster
    for c in range(N_CLUSTERS):
        words = df[df.cluster == c]["term"].tolist()
        if not words:
            continue
        wc = WordCloud(width=800, height=400, background_color="white")
        wc.generate(" ".join(words))
        wc.to_file(f"{OUTPUT_DIR}/wordcloud_{tag}_cluster_{c}.png")

        df[df.cluster == c].to_csv(
            f"{OUTPUT_DIR}/cluster_{tag}_{c}.csv", index=False
        )


def cluster_step(state: LexiconState):
    print("🔹 Clusterização: lematizado")
    clusterizar(state["lex_lem"], "lematizado")

    print("🔹 Clusterização: não lematizado")
    clusterizar(state["lex_raw"], "nao_lematizado")

    return state


# ==========================================================
# CONSTRUÇÃO DO GRAFO
# ==========================================================

graph = StateGraph(LexiconState)

graph.add_node("load", load_corpus)
graph.add_node("lexicons", build_lexicons)
graph.add_node("cluster", cluster_step)

graph.set_entry_point("load")
graph.add_edge("load", "lexicons")
graph.add_edge("lexicons", "cluster")

pipeline = graph.compile()


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":
    pipeline.invoke({})
