# ==========================================================
# LÉXICO DE BIGRAMAS MISÓGINOS - INTEGRADO LANGGRAPH
# ==========================================================

import os
import re
import glob
import math
import pandas as pd
from collections import Counter
from typing import TypedDict, List

import spacy
from langgraph.graph import StateGraph

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

BASE_CORPUS_DIR = "lexicons_corpus_misoginia"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

nlp = spacy.load("pt_core_news_lg")
STOPWORDS = nlp.Defaults.stop_words

FREQ_MIN = 5
PMI_MIN = 1
LLR_MIN = 10

sexual_keywords = [
    "gostosa","puta","vadia","safada","cama","corpo",
    "sexo","transar","trepar"
]

# ==========================================================
# ESTADO DO GRAFO
# ==========================================================

class LexiconState(TypedDict):
    texts_mis: List[str]
    texts_non: List[str]

# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"http\S+|www\S+", "", texto)
    texto = re.sub(r"[^a-zà-ú\s]", " ", texto)
    tokens = [t for t in texto.split() if len(t) > 2 and t not in STOPWORDS]
    return tokens

def load_corpus(state: LexiconState):

    texts_mis = []
    texts_non = []

    for csv_path in glob.glob(f"{BASE_CORPUS_DIR}/**/*.csv", recursive=True):
        try:
            df = pd.read_csv(csv_path)
        except:
            continue

        text_col = None
        label_col = None

        for c in df.columns:
            if c.lower() in ["text","comment","comentario"]:
                text_col = c
            if "misog" in c.lower() or "label" in c.lower():
                label_col = c

        if not text_col or not label_col:
            continue

        for _, row in df.iterrows():
            if pd.isna(row[text_col]) or pd.isna(row[label_col]):
                continue
            if int(row[label_col]) == 1:
                texts_mis.append(str(row[text_col]))
            else:
                texts_non.append(str(row[text_col]))

    print("Textos misóginos:", len(texts_mis))
    print("Textos não-misóginos:", len(texts_non))

    state["texts_mis"] = texts_mis
    state["texts_non"] = texts_non
    return state

# ==========================================================
# EXTRAÇÃO BIGRAMAS
# ==========================================================

def extrair_bigrams(texts):

    bigram = Counter()
    unigram = Counter()

    for texto in texts:
        tokens = limpar_texto(texto)
        for i in range(len(tokens)-1):
            bigram[(tokens[i], tokens[i+1])] += 1
        for t in tokens:
            unigram[t] += 1

    total_tokens = sum(unigram.values())
    return bigram, unigram, total_tokens

# ==========================================================
# PMI
# ==========================================================

def calcular_pmi(bigram, unigram, total_tokens):

    pmi_dict = {}

    for (w1,w2), freq in bigram.items():

        p_w1 = unigram[w1] / total_tokens
        p_w2 = unigram[w2] / total_tokens
        p_w1w2 = freq / total_tokens

        if p_w1w2 > 0:
            pmi = math.log2(p_w1w2 / (p_w1 * p_w2))
            pmi_dict[(w1,w2)] = pmi

    return pmi_dict

# ==========================================================
# LOG-LIKELIHOOD
# ==========================================================

def log_likelihood(k11,k12,k21,k22):

    def safe_log(x):
        return math.log(x) if x > 0 else 0

    N = k11+k12+k21+k22
    row1 = k11+k12
    row2 = k21+k22
    col1 = k11+k21
    col2 = k12+k22

    E11 = row1*col1/N
    E12 = row1*col2/N
    E21 = row2*col1/N
    E22 = row2*col2/N

    ll = 2*(
        k11*safe_log(k11/E11) +
        k12*safe_log(k12/E12) +
        k21*safe_log(k21/E21) +
        k22*safe_log(k22/E22)
    )

    return ll

# ==========================================================
# FILTRO LINGUÍSTICO
# ==========================================================

female_terms = [
    "mulher","mulheres","menina","meninas",
    "moça","moças","garota","garotas"
]

explicit_offensive = [
    "vadia","puta","safada","vagabunda",
    "piranha","cadela","vaca","burra",
    "imunda","nojenta","inútil"
]

def filtro_linguistico(bigram):

    w1, w2 = bigram

    if w1 in female_terms:
        return True

    return False

# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classificar_tipo(bigram):
    if any(p in sexual_keywords for p in bigram):
        return "sexualizada"
    return "direta"

# ==========================================================
# CONSTRUÇÃO DO LÉXICO FINAL
# ==========================================================

def construir_lexico(state: LexiconState):

    big_mis, uni_mis, total_mis = extrair_bigrams(state["texts_mis"])
    big_non, uni_non, total_non = extrair_bigrams(state["texts_non"])

    pmi = calcular_pmi(big_mis, uni_mis, total_mis)

    rows = []

    for bg, freq_mis in big_mis.items():

        if freq_mis < FREQ_MIN:
            continue

        freq_non = big_non.get(bg, 0)

        # score polaridade
        score = (freq_mis - freq_non) / (freq_mis + freq_non + 1e-9)

        # LLR
        llr = log_likelihood(
            freq_mis,
            total_mis - freq_mis,
            freq_non,
            total_non - freq_non
        )

        if llr < LLR_MIN:
            continue

        if bg not in pmi or pmi[bg] < PMI_MIN:
            continue

        if score <= 0:
            continue

        if not filtro_linguistico(bg):
            continue

        tipo = classificar_tipo(bg)

        rows.append([
            " ".join(bg),
            freq_mis,
            freq_non,
            round(score,3),
            round(pmi[bg],3),
            round(llr,3),
            tipo
        ])

    df_final = pd.DataFrame(
        rows,
        columns=[
            "bigram",
            "freq_mis",
            "freq_non",
            "score",
            "pmi",
            "llr",
            "misogyny_type"
        ]
    )

    df_final.to_csv(
        f"{OUTPUT_DIR}/lexico_bigramas_final.csv",
        index=False
    )

    print("Léxico final salvo.")
    print("Total de bigramas selecionados:", len(df_final))

    return state

# ==========================================================
# GRAFO
# ==========================================================

graph = StateGraph(LexiconState)

graph.add_node("load", load_corpus)
graph.add_node("build", construir_lexico)

graph.set_entry_point("load")
graph.add_edge("load", "build")

pipeline = graph.compile()

if __name__ == "__main__":
    pipeline.invoke({})
