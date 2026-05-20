#!/usr/bin/env python3
"""
CONSTRUTOR DE LÉXICO DE MISOGINIA - VERSÃO SIMPLIFICADA
Usa NLTK ao invés de spaCy (compatível com Python 3.8)
"""

import pandas as pd
import numpy as np
import nltk
import re
from nltk import pos_tag
from collections import defaultdict
from pathlib import Path
import json

# Download de recursos NLTK (primeira vez)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('rslp')  # Stemmer português

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

# Configurações
CORPUS_DIR = Path("lexicons_corpus_misoginia")
OUTPUT_DIR = Path("lexico_misoginia_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Inicializar recursos
stop_words = set(stopwords.words('portuguese'))
stemmer = RSLPStemmer()

print("✅ NLTK configurado!")

def preprocess_text(text):
    """Limpeza básica do texto"""
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)       # remove URLs
    text = re.sub(r'@\w+', '', text)                  # remove menções
    text = re.sub(r'#\w+', '', text)                  # remove hashtags
    text = re.sub(r'[^a-záéíóúãõâêîôûàèìòùç\s]', '', text)  # só letras PT
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_terms(text):
    """Extrai unigramas e bigramas (apenas N e ADJ, stemizados)"""
    tokens = word_tokenize(text, language='portuguese')
    tagged = pos_tag(tokens)
    
    filtered = []
    for token, pos in tagged:
        if (
            token.isalpha()
            and len(token) > 2
            and token not in stop_words
            and pos.startswith(("N", "J"))  # "J" = adjetivo no tagset do NLTK (JJ, JJR, JJS)
        ):
            stem = stemmer.stem(token)
            filtered.append(stem)
    
    terms = []
    # Unigramas
    terms.extend(filtered)
    # Bigramas
    for i in range(len(filtered) - 1):
        bigram = filtered[i] + "_" + filtered[i + 1]
        terms.append(bigram)
    
    return terms

# ==============================================================================
# CARREGAMENTO GENÉRICO DE CORPUS
# ==============================================================================

def load_generic_corpus(file_path):
    """
    Carrega corpus de forma genérica
    Tenta detectar automaticamente colunas de texto e rótulo
    """
    print(f"\n📥 Carregando: {file_path.name}")
    
    # Tentar diferentes separadores
    for sep in [',', '\t', ';']:
        try:
            df = pd.read_csv(file_path, sep=sep)
            if len(df.columns) > 1:
                break
        except:
            continue
    
    print(f"   Linhas: {len(df)}, Colunas: {len(df.columns)}")
    print(f"   Colunas: {list(df.columns)}")
    
    # Detectar coluna de texto
    text_col = None
    for col in df.columns:
        if any(word in col.lower() for word in ['text', 'comment', 'tweet', 'message', 'content', 'post']):
            text_col = col
            break
    
    if not text_col:
        # Pegar primeira coluna com texto
        for col in df.columns:
            if df[col].dtype == 'object':
                text_col = col
                break
    
    # Detectar coluna de rótulo
    label_col = None
    for col in df.columns:
        if any(word in col.lower() for word in ['label', 'class', 'hate', 'toxic', 'offensive', 
                                                  'misogyny', 'sexism', 'sentiment']):
            label_col = col
            break
    
    if not text_col:
        raise ValueError(f"❌ Não foi possível detectar coluna de texto em {file_path.name}")
    
    if not label_col:
        print(f"   ⚠️  Coluna de rótulo não detectada. Usando primeira coluna numérica.")
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                label_col = col
                break
    
    print(f"   ✅ Texto: {text_col}")
    print(f"   ✅ Rótulo: {label_col}")
    
    # Padronizar
    df_clean = pd.DataFrame()
    df_clean['text'] = df[text_col]
    
    # Tentar converter rótulo para binário
    if label_col:
        values = df[label_col]

        # Se já for numérico
        if pd.api.types.is_numeric_dtype(values):
            df_clean['label'] = values
        else:
            values = values.astype(str).str.lower()

            def map_label(v):
                if any(word in v for word in ['hate', 'toxic', 'offensive', 'misog', 'sexist']):
                    return 1
                if any(word in v for word in ['non', 'normal', 'neutral', 'not']):
                    return 0
                return np.nan

            df_clean['label'] = values.apply(map_label)
    else:
        df_clean['label'] = np.nan
    
    df_clean = df_clean.dropna(subset=['text'])
    df_clean = df_clean.dropna(subset=['label'])
    df_clean['label'] = df_clean['label'].astype(int)
    df_clean['label'] = df_clean['label'].apply(lambda x: 0 if x == 0 else 1)
    
    print(f"   📊 Após limpeza: {len(df_clean)} documentos")
    print(f"   📊 Classe 1 (misógino): {(df_clean['label'] == 1).sum()}")
    print(f"   📊 Classe 0 (não-misógino): {(df_clean['label'] == 0).sum()}")
    
    return df_clean

def load_all_corpus():
    """Carrega todos os corpus encontrados"""
    print("=" * 70)
    print("🔍 PROCURANDO DATASETS")
    print("=" * 70)
    
    # Procurar todos arquivos CSV
    csv_files = list(CORPUS_DIR.rglob('*.csv'))
    csv_files += list(CORPUS_DIR.rglob('*.tsv'))
    
    if not csv_files:
        raise FileNotFoundError(f"Nenhum arquivo encontrado em {CORPUS_DIR.absolute()}")
    
    print(f"\n✅ Encontrados {len(csv_files)} arquivos")
    
    all_data = []
    
    for file_path in csv_files:
        try:
            df = load_generic_corpus(file_path)
            df['source'] = file_path.stem
            all_data.append(df)
        except Exception as e:
            print(f"   ⚠️  Erro: {e}")
    
    if not all_data:
        raise ValueError("Nenhum corpus foi carregado com sucesso!")
    
    unified = pd.concat(all_data, ignore_index=True)
    
    print("\n" + "=" * 70)
    print("📊 CORPUS UNIFICADO")
    print("=" * 70)
    print(f"Total de documentos: {len(unified)}")
    print(f"Classe 1 (misógino): {(unified['label'] == 1).sum()}")
    print(f"Classe 0 (não-misógino): {(unified['label'] == 0).sum()}")
    
    return unified

# ==============================================================================
# PRÉ-PROCESSAMENTO COM NLTK
# ==============================================================================

def calculate_polarity_bayes(corpus_df):
    """Calcula polaridade com Log-Likelihood Ratio ponderado"""
    print("\n" + "=" * 70)
    print("🔢 CALCULANDO POLARIDADES (LLR ponderado)")
    print("=" * 70)
    
    term_positive = defaultdict(int)
    term_negative = defaultdict(int)
    
    positive_count = 0
    negative_count = 0
    
    total = len(corpus_df)
    
    for idx, row in corpus_df.iterrows():
        if idx % 1000 == 0:
            print(f"   Processando: {idx}/{total} ({idx/total*100:.1f}%)")
        
        text = preprocess_text(row['text'])
        terms = set(extract_terms(text))
        
        if row['label'] == 1:
            positive_count += 1
            for term in terms:
                term_positive[term] += 1
        else:
            negative_count += 1
            for term in terms:
                term_negative[term] += 1
    
    print(f"\n✅ Processamento concluído!")
    print(f"   Documentos misóginos: {positive_count}")
    print(f"   Documentos não-misóginos: {negative_count}")
    
    lexicon = []
    all_terms = set(list(term_positive.keys()) + list(term_negative.keys()))
    
    print(f"\n📊 Total de termos únicos: {len(all_terms)}")
    
    epsilon = 1e-9
    
    for term in all_terms:
        freq_pos = term_positive[term]
        freq_neg = term_negative[term]
        total_freq = freq_pos + freq_neg
        
        is_bigram = "_" in term
        min_freq = 8 if is_bigram else 5
        if total_freq < min_freq:
            continue
        
        # Suavização de Laplace
        prob_pos = (freq_pos + 1) / (positive_count + 2)
        prob_neg = (freq_neg + 1) / (negative_count + 2)
        
        # Prior das classes (correção de desbalanceamento)
        prior_pos = positive_count / (positive_count + negative_count)
        prior_neg = negative_count / (positive_count + negative_count)
        
        # Log-Likelihood Ratio corrigido pelo prior
        alpha = 0.2
        log_ratio = np.log((prob_pos + epsilon) / (prob_neg + epsilon)) \
                  + alpha * np.log(prior_pos / prior_neg)
        
        # Ponderação por frequência + filtro diferenciado unigrama/bigrama
        score = log_ratio * np.log(1 + total_freq)
        
        # Definir polaridade
        if score > 0:
            polarity = "misogynistic"
        elif score < 0:
            polarity = "non-misogynistic"
        else:
            polarity = "neutral"
        
        lexicon.append({
            'term': term,
            'score': round(score, 4),
            'polarity': polarity,
            'freq_misogynistic': freq_pos,
            'freq_non_misogynistic': freq_neg,
            'total_freq': total_freq,
            'log_ratio': round(log_ratio, 4)
        })
    
    lexicon_df = pd.DataFrame(lexicon)
    lexicon_df = lexicon_df.sort_values('score', ascending=False)
    
    print(f"\n📊 Léxico gerado:")
    print(f"   Total de termos: {len(lexicon_df)}")
    print(f"   Misóginos: {(lexicon_df['polarity'] == 'misogynistic').sum()}")
    print(f"   Não-misóginos: {(lexicon_df['polarity'] == 'non-misogynistic').sum()}")
    print(f"   Neutros: {(lexicon_df['polarity'] == 'neutral').sum()}")
    
    return lexicon_df

# ==============================================================================
# SALVAR RESULTADOS
# ==============================================================================

def save_lexicon(lexicon_df, filename="lexico_misoginia_v1.csv"):
    """Salva o léxico"""
    output_csv = OUTPUT_DIR / filename
    output_json = OUTPUT_DIR / filename.replace('.csv', '.json')
    
    lexicon_df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n💾 Salvo: {output_csv}")
    
    lexicon_dict = lexicon_df.to_dict('records')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(lexicon_dict, f, ensure_ascii=False, indent=2)
    print(f"💾 Salvo: {output_json}")
    
    # Top termos
    print("\n📋 TOP 20 TERMOS MISÓGINOS:")
    print("-" * 70)
    top_misog = lexicon_df[lexicon_df['polarity'] == 'misogynistic'].head(20)
    for idx, row in top_misog.iterrows():
        print(f"   {row['term']:<20} | Score: {row['score']:.4f} | Freq: {row['freq_misogynistic']}")
    
    return output_csv

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 70)
    print("CONSTRUÇÃO DE LÉXICO DE MISOGINIA - PT-BR")
    print("Versão Simplificada (NLTK)")
    print("=" * 70)
    
    try:
        # Carregar corpus
        corpus_df = load_all_corpus()
        
        #Salvar corpus unificado para experimentos
        corpus_df.to_csv("corpus_unificado_final.csv", index=False)
        print("\n📁 Corpus unificado salvo como corpus_unificado_final.csv")
        print("   Total de documentos:", len(corpus_df))
        print("   Misóginos:", (corpus_df["label"] == 1).sum())
        print("   Não-misóginos:", (corpus_df["label"] == 0).sum())
        
        # Calcular polaridades
        lexicon_df = calculate_polarity_bayes(corpus_df)
        
        # Salvar
        save_lexicon(lexicon_df)
        
        print("\n" + "=" * 70)
        print("✅ PROCESSO CONCLUÍDO!")
        print("=" * 70)
        print(f"\n📂 Arquivos em: {OUTPUT_DIR.absolute()}")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\n💡 SOLUÇÃO:")
        print("   1. Execute o script 'dataset_inspector.py' primeiro")
        print("   2. Verifique a estrutura dos seus datasets")
        print("   3. Ajuste os mapeamentos se necessário")

if __name__ == "__main__":
    main()
