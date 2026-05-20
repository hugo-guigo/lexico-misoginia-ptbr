#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Expansão automática de léxico de misoginia usando Gemini (SDK novo)
Autor: Hugo
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path
from getpass import getpass

from google import genai

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

NOME_ARQUIVO_LEXICO = "lexico_misoginia_v1_ajustado.csv"
PASTA_SAIDA = "lexico_misoginia_output"
MODELO_GEMINI = "gemini-2.5-flash"
DELAY_ENTRE_REQUISICOES = 1.2  # segundos

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def localizar_lexico():
    """
    Procura o arquivo do léxico em:
    1. Diretório atual
    2. Pasta lexico_misoginia_output
    3. Diretório pai
    """
    caminhos = [
        Path.cwd() / NOME_ARQUIVO_LEXICO,
        Path.cwd() / PASTA_SAIDA / NOME_ARQUIVO_LEXICO,
        Path.cwd().parent / NOME_ARQUIVO_LEXICO,
        Path.cwd().parent / PASTA_SAIDA / NOME_ARQUIVO_LEXICO,
    ]

    for caminho in caminhos:
        if caminho.exists():
            print(f"✅ Léxico encontrado em: {caminho}")
            return caminho

    raise FileNotFoundError(
        f"❌ Arquivo {NOME_ARQUIVO_LEXICO} não encontrado em nenhum local esperado."
    )


def configurar_api():
    print("=" * 70)
    print("CONFIGURAÇÃO DA API GEMINI")
    print("=" * 70)

    api_key = getpass("🔑 Cole sua API Key do Gemini: ").strip()

    if not api_key:
        print("❌ API Key vazia.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print("✅ API Gemini configurada com sucesso\n")
    return client


def prompt_expansao(termo):
    return f"""
Você é um pesquisador em linguística computacional.

Dado o radical ou termo abaixo, gere variações lexicalmente relacionadas
que possam ser usadas em discurso misógino em português brasileiro.

Regras:
- Retorne APENAS uma lista separada por vírgulas
- Não explique nada
- Não repita o termo original
- Use apenas palavras plausíveis

Termo: "{termo}"
"""


def expandir_termo(client, termo):
    response = client.models.generate_content(
        model=MODELO_GEMINI,
        contents=prompt_expansao(termo)
    )

    texto = response.text.strip()

    if not texto:
        return []

    termos = [t.strip().lower() for t in texto.split(",") if t.strip()]
    return list(set(termos))


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():
    caminho_lexico = localizar_lexico()
    client = configurar_api()

    print("📥 Carregando léxico...")
    df = pd.read_csv(caminho_lexico)

    if "termo" not in df.columns:
        print("❌ O CSV precisa ter uma coluna chamada 'termo'")
        sys.exit(1)

    termos_originais = sorted(
        t for t in df["termo"].dropna().unique()
        if termo_valido(t)
    )

    novos_termos = set()

    for termo in termos_originais:
        print(f"🔍 Expandindo: {termo}")
        try:
            expansoes = expandir_termo(client, termo)
            novos_termos.update(expansoes)
            time.sleep(DELAY_ENTRE_REQUISICOES)
        except Exception as e:
            print(f"⚠️ Erro ao expandir '{termo}': {e}")

    print("\n📊 Consolidando resultados...")

    todos_termos = sorted(set(termos_originais) | novos_termos)
    df_final = pd.DataFrame({"termo": todos_termos})

    os.makedirs(PASTA_SAIDA, exist_ok=True)
    caminho_saida = Path(PASTA_SAIDA) / "lexico_misoginia_expandido_gemini.csv"

    df_final.to_csv(caminho_saida, index=False, encoding="utf-8")

    print("=" * 70)
    print("✅ EXPANSÃO FINALIZADA COM SUCESSO")
    print(f"📁 Arquivo salvo em: {caminho_saida}")
    print(f"📈 Total de termos: {len(df_final)}")
    print("=" * 70)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    def termo_valido(t):
        return (
           isinstance(t, str)
           and len(t) >= 4
           and t.isalpha()
           and not set(t) <= {"a"}
        )

    main()
