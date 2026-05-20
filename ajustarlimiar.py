python3 << 'EOF'
import pandas as pd
import json

# Carregar léxico
df = pd.read_csv('lexico_misoginia_output/lexico_misoginia_v1.csv')

print("=" * 70)
print("RECLASSIFICANDO COM LIMIAR AJUSTADO")
print("=" * 70)

# Ajustar limiar para 0.01 (mais sensível)
df['polarity'] = df['score'].apply(lambda x: 
    'misogynistic' if x > 0.01 else 
    'non-misogynistic' if x < -0.01 else 
    'neutral'
)

# Salvar CSV
df.to_csv('lexico_misoginia_output/lexico_misoginia_v1_ajustado.csv', index=False)

# Salvar JSON
lexicon_dict = df.to_dict('records')
with open('lexico_misoginia_output/lexico_misoginia_v1_ajustado.json', 'w', encoding='utf-8') as f:
    json.dump(lexicon_dict, f, ensure_ascii=False, indent=2)

print(f"\n✅ Léxico reclassificado!")
print(f"   Total de termos: {len(df)}")
print(f"   Misóginos: {(df['polarity'] == 'misogynistic').sum()}")
print(f"   Não-misóginos: {(df['polarity'] == 'non-misogynistic').sum()}")
print(f"   Neutros: {(df['polarity'] == 'neutral').sum()}")

print("\n📋 TOP 30 TERMOS MISÓGINOS:")
print("-" * 70)
top_misog = df[df['polarity'] == 'misogynistic'].nlargest(30, 'score')
for idx, row in top_misog.iterrows():
    print(f"   {row['term']:<20} | Score: {row['score']:>7.4f} | Freq+: {row['freq_misogynistic']:>5} | Freq-: {row['freq_non_misogynistic']:>5}")

# Salvar estatísticas
with open('lexico_misoginia_output/estatisticas_ajustado.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("ESTATÍSTICAS DO LÉXICO DE MISOGINIA (AJUSTADO)\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Total de termos: {len(df)}\n")
    f.write(f"Termos misóginos: {(df['polarity'] == 'misogynistic').sum()}\n")
    f.write(f"Termos não-misóginos: {(df['polarity'] == 'non-misogynistic').sum()}\n")
    f.write(f"Termos neutros: {(df['polarity'] == 'neutral').sum()}\n\n")
    
    f.write("TOP 50 TERMOS MAIS MISÓGINOS:\n")
    f.write("-" * 70 + "\n")
    top_50 = df[df['polarity'] == 'misogynistic'].nlargest(50, 'score')
    for idx, row in top_50.iterrows():
        f.write(f"{row['term']:<25} | Score: {row['score']:>7.4f} | Freq+: {row['freq_misogynistic']:>5} | Freq-: {row['freq_non_misogynistic']:>5}\n")

print(f"\n💾 Arquivos salvos:")
print(f"   - lexico_misoginia_v1_ajustado.csv")
print(f"   - lexico_misoginia_v1_ajustado.json")
print(f"   - estatisticas_ajustado.txt")

print("\n" + "=" * 70)
print("✅ PROCESSO CONCLUÍDO!")
print("=" * 70)
EOF

