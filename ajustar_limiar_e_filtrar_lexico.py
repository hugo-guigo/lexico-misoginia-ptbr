#!/usr/bin/env python3
"""
AJUSTE FINAL DO LÉXICO DE MISOGINIA (SEM LLM)

Etapas:
1. Carrega léxico estatístico
2. Reclassifica polaridade por percentil do score
3. Aplica pós-filtro linguístico
4. Salva CSV, JSON e estatísticas finais

Autor: Hugo Guilherme
"""

import pandas as pd
import json
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================

INPUT_CSV = Path("lexico_misoginia_output/lexico_misoginia_v1.csv")
OUTPUT_DIR = Path("lexico_misoginia_output")

OUTPUT_CSV = OUTPUT_DIR / "lexico_misoginia_v2_final.csv"
OUTPUT_JSON = OUTPUT_DIR / "lexico_misoginia_v2_final.json"
OUTPUT_STATS = OUTPUT_DIR / "estatisticas_final.txt"

# Percentis para limiar
UPPER_PERCENTILE = 0.95   # top 5% → misógino
LOWER_PERCENTILE = 0.05   # bottom 5% → não-misógino

# Blacklist mínima de radicais funcionais
RADICAIS_GENERICOS = {
    "pra", "pod", "fal", "vai", "faz",
    "dia", "tod", "pess", "cois"
}

# Frequência mínima em textos misóginos
MIN_FREQ_POS = 3


# ==============================================================================
# FUNÇÕES DE FILTRO
# ==============================================================================

def termo_valido(t):
    """
    Filtro linguístico mínimo:
    - string
    - tamanho mínimo
    - apenas letras
    - mais de um caractere distinto (remove aaa, kkk)
    """
    return (
        isinstance(t, str)
        and len(t) >= 4
        and t.isalpha()
        and len(set(t)) > 1
    )


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 70)
    print("AJUSTE FINAL DO LÉXICO DE MISOGINIA (SEM LLM)")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # 1. Carregar léxico
    # --------------------------------------------------------------------------
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)

    print(f"\n📥 Léxico carregado: {len(df)} termos")

    # --------------------------------------------------------------------------
    # 2. Limiar por percentil
    # --------------------------------------------------------------------------
    upper_pct = df["score"].quantile(UPPER_PERCENTILE)
    lower_pct = df["score"].quantile(LOWER_PERCENTILE)

    print("\n🎯 LIMIARES POR PERCENTIL")
    print(f"   Superior (95%): {upper_pct:.4f}")
    print(f"   Inferior (5%):  {lower_pct:.4f}")

    df["polarity"] = df["score"].apply(
        lambda x:
            "misogynistic" if x >= upper_pct else
            "non-misogynistic" if x <= lower_pct else
            "neutral"
    )

    # --------------------------------------------------------------------------
    # 3. Pós-filtro linguístico
    # --------------------------------------------------------------------------
    print("\n🧹 APLICANDO PÓS-FILTRO LINGUÍSTICO")

    total_before = len(df)

    # Filtro estrutural do termo
    df = df[df["term"].apply(termo_valido)]

    # Remover radicais genéricos
    df = df[~df["term"].isin(RADICAIS_GENERICOS)]

    # Reforçar associação com misoginia
    df = df[
        (df["polarity"] != "misogynistic") |
        (df["freq_misogynistic"] >= MIN_FREQ_POS)
    ]

    total_after = len(df)

    print(f"   Termos antes: {total_before}")
    print(f"   Termos depois: {total_after}")
    print(f"   Removidos: {total_before - total_after}")

    # --------------------------------------------------------------------------
    # 4. Ordenar resultado
    # --------------------------------------------------------------------------
    df = df.sort_values("score", ascending=False)

    # --------------------------------------------------------------------------
    # 5. SEPARAÇÃO: LÉXICO NÚCLEO x CONTEXTUAL
    # --------------------------------------------------------------------------

    LEXICO_NUCLEO = OUTPUT_DIR / "lexico_misoginia_nucleo.csv"
    LEXICO_CONTEXTO = OUTPUT_DIR / "lexico_misoginia_contextual.csv"

    # Léxico núcleo: ofensa direta
    lexico_nucleo = df[
        (df["polarity"] == "misogynistic") &
        (df["freq_misogynistic"] >= 5)
    ].copy()

    # Léxico contextual: termos associados, mas não ofensivos isoladamente
    lexico_contextual = df[
        (df["polarity"] == "neutral") &
        (df["score"] > 0) &
        (df["total_freq"] >= 5)
    ].copy()

    lexico_nucleo.to_csv(LEXICO_NUCLEO, index=False, encoding="utf-8")
    lexico_contextual.to_csv(LEXICO_CONTEXTO, index=False, encoding="utf-8")

    print("\n📚 SEPARAÇÃO DO LÉXICO")
    print(f"   Léxico núcleo: {len(lexico_nucleo)} termos")
    print(f"   Léxico contextual: {len(lexico_contextual)} termos")


    # --------------------------------------------------------------------------
    # 6. Salvar CSV e JSON
    # --------------------------------------------------------------------------
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, ensure_ascii=False, indent=2)

    # --------------------------------------------------------------------------
    # 7. Estatísticas finais
    # --------------------------------------------------------------------------
    with open(OUTPUT_STATS, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("ESTATÍSTICAS FINAIS DO LÉXICO DE MISOGINIA\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total de termos: {len(df)}\n")
        f.write(f"Misóginos: {(df['polarity'] == 'misogynistic').sum()}\n")
        f.write(f"Não-misóginos: {(df['polarity'] == 'non-misogynistic').sum()}\n")
        f.write(f"Neutros: {(df['polarity'] == 'neutral').sum()}\n\n")

        f.write("TOP 30 TERMOS MISÓGINOS:\n")
        f.write("-" * 70 + "\n")

        top_30 = df[df["polarity"] == "misogynistic"].head(30)
        for _, row in top_30.iterrows():
            f.write(
                f"{row['term']:<25} | "
                f"Score: {row['score']:>7.4f} | "
                f"Freq+: {row['freq_misogynistic']:>5} | "
                f"Freq-: {row['freq_non_misogynistic']:>5}\n"
            )

    # --------------------------------------------------------------------------
    # 8. Resumo final
    # --------------------------------------------------------------------------
    print("\n💾 ARQUIVOS GERADOS:")
    print(f"   - {OUTPUT_CSV.name}")
    print(f"   - {OUTPUT_JSON.name}")
    print(f"   - {OUTPUT_STATS.name}")

    print("\n" + "=" * 70)
    print("✅ PROCESSO FINAL CONCLUÍDO")
    print("=" * 70)


if __name__ == "__main__":
    main()
