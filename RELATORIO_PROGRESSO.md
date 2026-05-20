# Relatório de Progresso — IC PIBIC 2025/2026

> **Léxico de Misoginia em Português Brasileiro para Detecção Automática em Ambientes Digitais**
>
> Projeto vinculado: **PI06069-2022** · UFG / Instituto de Informática
>
> **Pesquisador:** Hugo Guilherme de Assis Paula
> **Orientadora:** Profa. Dra. Deborah Silva Alves Fernandes
>
> Data deste relatório: **2026-05-19**

---

## 1. Sumário executivo

O projeto avançou da fase de fundamentação para a fase operacional. **Cinco das seis
tarefas previstas no plano foram concluídas:** (1) a taxonomia formal das 11 classes de
misoginia digital está escrita e fundamentada na literatura; (2) o léxico V3 foi
construído pelo método semente TF-IDF + expansão PMI (Monteles, 2023) sobre um corpus
unificado de 74.338 documentos, resultando em **531 termos**; (3) os termos misóginos
foram anotados automaticamente por similaridade vetorial e uma planilha de votação foi
preparada para os 3 anotadores do grupo; (4) um corpus de teste com 333 frases já
rotuladas (ToLD-BR) + 100 vagas para notícias foi montado; (5–6) **quatro modelos foram
treinados e comparados** (SVM, Regressão Logística, Random Forest, MLP como proxy de RNN)
no corpus de treino e no corpus de teste.

**O que falta para fechar o ciclo:** (a) **votação dos 3 anotadores** sobre os 268 termos
misóginos do V3, para gerar o léxico validado final; (b) **coleta de textos de notícias**
para enriquecer o corpus de teste e melhorar a avaliação fora do domínio do Twitter;
(c) substituir o MLP por **LSTM/GRU real** quando o ambiente tiver PyTorch/TensorFlow
(atualmente bloqueado por espaço em disco). Nada disso é bloqueante para apresentar o
estado atual.

---

## 2. Tarefa 1 — Taxonomia das 11 classes ✅

Documento principal: **[`taxonomia_misoginia_digital.md`](taxonomia_misoginia_digital.md)**
(392 linhas em Markdown, versionável).

A taxonomia adotada tem **11 classes de misoginia digital** (recorte explícito: violência
verbal/discursiva em meios digitais; exclui violência física):

| ID | Classe | Origem |
|----|--------|--------|
| 1 | Descrédito | Anzovino, Fersini & Rosso (2018) |
| 2 | Estereotipização | Anzovino et al. (2018); Glick & Fiske (1997) |
| 3 | Assédio Sexual | Anzovino et al.; Jane (2017); Mantilla (2015) |
| 4 | Ameaças de Violência | Anzovino et al.; Mantilla (2015) |
| 5 | Dominação | Manne (2017); Anzovino et al. (2018) |
| 6 | Derailing | Anzovino et al. (2018) |
| 7 | Culpabilização da Vítima | Sultana, Sarker & Bosu (2021); Manne (2017) |
| 8 | Objetificação Sexual | Anzovino et al.; Massanari (2017) |
| 9 | Neossexismo | Manne (2020); Banet-Weiser & Miltner (2016) |
| 10 | Misogynoir | Bailey (2010) — **contribuição original ao contexto BR** |
| 11 | Violência Política Digital | **contribuição original do projeto** |

**Fundamentação teórica.** O documento cita explicitamente os especialistas que propuseram
cada categoria, incluindo a taxonomia original de **5 categorias** de Anzovino et al.
(2018) e como o projeto **desmembra** "Stereotype & Objectification" em duas classes (2 e
8) e "Sexual Harassment & Threats" em duas (3 e 4), além de **acrescentar** Culpabilização
da Vítima (7) e Neossexismo (9). As classes 10 (Misogynoir) e 11 (Violência Política
Digital) são contribuições originais que precisam de **aprovação explícita da orientadora**.

**Pendente.** Reunião com o grupo para validar coletivamente a taxonomia, especialmente
as duas classes originais.

---

## 3. Tarefa 2 — Construção do léxico V3 ✅

Script: **[`outputs/pipeline_semente_pmi.py`](outputs/pipeline_semente_pmi.py)**

Pipeline em duas etapas, seguindo **Monteles (2023)** adaptado para detecção de misoginia
e usando **lematização spaCy** (`pt_core_news_lg`) em vez de stemming RSLP:

### Etapa 2a — Semente TF-IDF (400 termos)

Saída: [`outputs/lexico_semente_tfidf.csv`](outputs/lexico_semente_tfidf.csv).

- Calcula TF-IDF separadamente para a classe misógina e não-misógina.
- Score discriminativo: `score = tfidf_mis / (tfidf_non + ε)`.
- Seleciona **top-200 por classe** → 200 sementes misóginas + 200 sementes não-misóginas.

### Etapa 2b — Expansão por PMI (531 termos no V3)

Saída: [`outputs/lexico_misoginia_v3_semente_pmi.csv`](outputs/lexico_misoginia_v3_semente_pmi.csv)
e [`.json`](outputs/lexico_misoginia_v3_semente_pmi.json).

- Para cada lema candidato x do corpus, calcula
  **O(x) = PMI(x, semente_misógino) − PMI(x, semente_não_misógino)** (eq. 3-2 de Monteles).
- Aceita se `|O(x)| ≥ 1.5`.
- Resultado: **268 termos misóginos + 263 termos não-misóginos = 531 termos** no léxico V3.

**Parâmetros usados:**

| Parâmetro | Valor | Significado |
|---|---|---|
| `TOP_N_SEMENTE` | 200 | top N por classe na semente |
| `MIN_FREQ_SEMENTE` | 5 | freq. mínima do lema no subcorpus |
| `PMI_THRESHOLD` | 1.5 | limiar do score O(x) |
| `WINDOW_SIZE` | 5 | janela de coocorrência |
| `MIN_FREQ_EXPAND` | 5 | freq. mínima do candidato |
| `MIN_COOCORR` | 3 | mínimo de coocorrências válidas |

### Top-10 termos misóginos do V3

| Termo | score_norm | O(x) | freq_mis | freq_non |
|---|---|---|---|---|
| canalha | 4.07 | 4.07 | 105 | 70 |
| comunista | 3.99 | 3.99 | 72 | 49 |
| ladrão | 3.72 | 3.72 | 43 | 30 |
| feminista | 3.42 | 3.42 | 90 | 90 |
| bandido | 3.31 | 3.31 | 138 | 90 |
| safar | 3.30 | 3.30 | 41 | 12 |
| congresso | 3.30 | 3.30 | 57 | 33 |
| pastor | 3.27 | 3.27 | 52 | 19 |
| esquerdista | 3.20 | 3.20 | 62 | 52 |
| absurdo | 3.05 | 3.05 | 63 | 84 |

### Problema conhecido: ruído político

O corpus contém **muito comentário político insultuoso** rotulado como misógino
(`canalha`, `comunista`, `bandido`, `esquerdista`, `pastor`) — esses termos não são
intrinsecamente misóginos, mas aparecem **estatisticamente associados** à classe positiva
porque o discurso misógino brasileiro frequentemente se sobrepõe ao discurso político de
ódio. Esse ruído é **esperado** e será tratado na Tarefa 3 (votação humana removerá os
termos que o grupo não considerar misóginos).

---

## 4. Tarefa 3 — Aplicação da taxonomia + validação manual ✅ (parte automática)

Scripts: **[`outputs/anotar_lexico.py`](outputs/anotar_lexico.py)** com modos
`--gerar-planilha` (executado) e `--consolidar` (executar após votação).

### Anotação automática (concluída)

Para cada um dos 268 termos misóginos do V3, o pipeline calcula a similaridade vetorial
(spaCy) entre o lema e o **centróide** das palavras-âncora de cada classe da taxonomia,
sugerindo a categoria de maior similaridade. Resultado em
[`outputs/lexico_v3_anotado.csv`](outputs/lexico_v3_anotado.csv):

| Categoria sugerida | Nº termos |
|---|---|
| Violência Política Digital (11) | 35 |
| Ameaças de Violência (4) | 31 |
| Descrédito (1) | 27 |
| Neossexismo (9) | 17 |
| Assédio Sexual (3) | 15 |
| Estereotipização (2) | 3 |
| Misogynoir (10) | 1 |
| Objetificação Sexual (8) | 1 |
| Derailing (6) | 1 |
| _(sem sugestão — abaixo do limiar)_ | 137 |

A grande quantidade de "Violência Política Digital" reflete o ruído político mencionado.
A votação humana vai redistribuir esses termos (muitos sairão como "não misógino").

### Pendente: votação do grupo (3 anotadores)

Arquivo: **[`outputs/planilha_votacao_grupo.csv`](outputs/planilha_votacao_grupo.csv)**

Cada anotador deve preencher, para cada termo, duas colunas:
- `anotadorN_eh_misogino` — `0` (não) ou `1` (sim)
- `anotadorN_categoria` — `1`–`11` (apenas se `eh_misogino=1`)

Após os 3 preencherem, rodar:

```bash
python3 outputs/anotar_lexico.py --consolidar
```

O script:
- Calcula **Kappa de Fleiss** entre os 3 anotadores (na decisão binária e na categórica).
- Gera o **léxico V3 validado final** ([`outputs/lexico_v3_validado_final.csv`](outputs/lexico_v3_validado_final.csv)) com apenas os termos em que a maioria votou "misógino", anotando a categoria majoritária.
- Salva concordância em [`outputs/concordancia_kappa_fleiss.csv`](outputs/concordancia_kappa_fleiss.csv).

---

## 5. Tarefa 4 — Corpus de frases de teste ✅ (template)

Script: **[`outputs/montar_corpus_teste.py`](outputs/montar_corpus_teste.py)**
Saída: **[`outputs/corpus_teste_frases.csv`](outputs/corpus_teste_frases.csv)**

**Composição atual** (esperando preenchimento):

| Categoria | Quantidade | Origem |
|---|---|---|
| Misóginas (label=1) | 133 | ToLD-BR, com ≥ 2 votos de misoginia no anotador |
| Não-misóginas (label=0) | 200 | ToLD-BR, **nenhum** dos rótulos de toxicidade ativado |
| Vagas para notícias | 100 | em branco, preencher manualmente |

Colunas: `text, label, categoria_id, categoria_nome, fonte, anotador, votos_misoginia_told`.

### Pendente: preenchimento manual

1. Para cada uma das 133 linhas misóginas, preencher `categoria_id` (1–11) e
   `categoria_nome` (ver tabela na seção 2).
2. Para as 100 linhas em branco com `fonte=noticias`: coletar textos reais de notícias /
   redes sociais brasileiros, preencher `text`, `label` (0/1), e — quando `label=1` — a
   categoria. **Sugestão de fontes**: comentários sobre mulheres políticas
   (deputadas, ministras), atletas (jornalistas esportivas, atletas mulheres) e
   jornalistas (figuras públicas atacadas em redes).

---

## 6. Tarefas 5 e 6 — Treinamento e comparação de modelos ✅

Script: **[`outputs/experimentos_modelos.py`](outputs/experimentos_modelos.py)**
Resultados: **[`outputs/resultados_modelos.csv`](outputs/resultados_modelos.csv)**

### Setup

- **Features:** TF-IDF de lemas (unigramas, máx. 10.000 features) + 3 features
  derivadas do léxico (`mean_score`, `misog_ratio`, `match_count`).
- **Modelos comparados** (com `class_weight='balanced'` para lidar com o desbalanceamento
  ~80/20):
  - **SVM** (`LinearSVC`)
  - **Regressão Logística**
  - **Random Forest** (100 árvores, profundidade máxima 20)
  - **MLP** — proxy de RNN (1 camada oculta, 64 neurônios)
- **Cross-validation:** 3-fold no corpus de treino (35.791 docs após limpeza).
- **Teste out-of-sample:** os 333 documentos rotulados do corpus de teste (ToLD-BR
  held-out, sem notícias ainda).

### Resultados — cross-validation (corpus de treino)

| Modelo | F1 (misógino) | Precisão | Recall |
|---|---|---|---|
| SVM (LinearSVC) | 0.529 ± 0.006 | 0.440 | 0.664 |
| **Regressão Logística** | **0.554 ± 0.004** | 0.456 | 0.706 |
| Random Forest | 0.477 ± 0.003 | 0.410 | 0.570 |
| MLP (proxy RNN) | 0.467 ± 0.017 | 0.639 | 0.368 |

### Resultados — corpus de teste (out-of-sample)

| Modelo | F1 (misógino) | Precisão | Recall |
|---|---|---|---|
| **SVM (LinearSVC)** | **0.871** | 0.910 | 0.835 |
| Regressão Logística | 0.846 | 0.920 | 0.782 |
| Random Forest | 0.560 | 0.718 | 0.459 |
| MLP (proxy RNN) | 0.506 | 1.000 | 0.338 |

### Leitura dos resultados

- **A diferença CV × teste é grande** porque o corpus de treino tem o ruído político
  (insultos políticos rotulados como misoginia) e o corpus de teste foi montado com
  rótulos de alta confiança (≥ 2 votos no ToLD-BR). O F1 de teste perto de **0.87** mostra
  que os modelos lineares (SVM, LR) generalizam bem para o "subconjunto limpo".
- **SVM e Regressão Logística** dominam — esperado em texto curto com TF-IDF.
- **Random Forest** tem pior desempenho que os lineares (típico em alta dimensão).
- **MLP** sofreu com o desbalanceamento (`precision=1.0, recall=0.34` no teste — está
  classificando quase tudo como "não-misógino" exceto casos muito confiantes).

### TODO RNN real

O ambiente atual **não tem PyTorch nem TensorFlow** (a instalação falhou por falta de
espaço em disco no `/`). O `MLPClassifier` foi usado como proxy de modelo neural denso.
**Próximo passo:** quando o ambiente tiver espaço, instalar `torch` e implementar
**LSTM/GRU** com embeddings spaCy ou aleatórios + camada de atenção opcional, para
comparação justa com SVM/LR no recall.

### Comparação votação humana × pipeline (Tarefa 6, parte final)

Saída: [`outputs/relatorio_comparacao_votacao_pipeline.txt`](outputs/relatorio_comparacao_votacao_pipeline.txt).

Atualmente **vazio** (esperando os votos do grupo). Quando a planilha estiver preenchida,
basta rodar de novo o `experimentos_modelos.py` para regenerar a matriz de confusão
entre a categoria sugerida pelo pipeline e a categoria votada pela maioria do grupo.

---

## 7. Próximos passos (checklist)

### Grupo de pesquisa (3 anotadores)
- [ ] Cada anotador abre [`outputs/planilha_votacao_grupo.csv`](outputs/planilha_votacao_grupo.csv) e preenche suas 2 colunas para os 268 termos.
- [ ] Devolver o arquivo preenchido (cada anotador devolve uma cópia ou consolidam num único arquivo).

### Orientadora
- [ ] Validar a taxonomia formal em [`taxonomia_misoginia_digital.md`](taxonomia_misoginia_digital.md), com atenção às classes 10 (Misogynoir) e 11 (Violência Política Digital) — contribuições originais.
- [ ] Revisar as 6 "pontos abertos para discussão" no fim da taxonomia (sobreposição de classes, granularidade, rótulo múltiplo, etc.).

### Pesquisador (Hugo)
- [ ] Coletar ~100 frases de notícias / redes brasileiras e preencher as linhas com `fonte=noticias` em [`outputs/corpus_teste_frases.csv`](outputs/corpus_teste_frases.csv).
- [ ] Preencher `categoria_id` (1–11) para as 133 linhas misóginas do ToLD-BR.
- [ ] (Quando houver espaço) instalar `torch` e substituir o MLP por LSTM/GRU.

### Assistente (Claude)
- [ ] Re-rodar `anotar_lexico.py --consolidar` após o grupo votar.
- [ ] Re-rodar `experimentos_modelos.py` com o léxico validado final + corpus de teste ampliado (notícias).
- [ ] Gerar relatório final comparando concordância grupo × pipeline.

---

## 8. Como reproduzir tudo localmente

```bash
# Pré-requisitos
pip install spacy scikit-learn pandas numpy scipy nltk
python -m spacy download pt_core_news_lg

# Tarefa 2 — léxico V3 (lematização cacheia em outputs/_cache_lemmas.pkl)
python3 outputs/pipeline_semente_pmi.py

# Tarefa 3 — anotação automática + planilha de votação
python3 outputs/anotar_lexico.py --gerar-planilha

# Tarefa 4 — corpus de teste (template)
python3 outputs/montar_corpus_teste.py

# Tarefa 5/6 — treinar e comparar 4 modelos
python3 outputs/experimentos_modelos.py

# Após o grupo votar:
python3 outputs/anotar_lexico.py --consolidar
python3 outputs/experimentos_modelos.py  # re-roda com léxico validado
```

Cada script é **idempotente** — pode ser executado várias vezes sem efeitos colaterais.
O cache de lemas é gerado uma vez (~3 min) e reutilizado nas demais execuções.

---

## 9. Repositório

Todo o código, dados de saída e documentação estão disponíveis no GitHub:

🔗 **https://github.com/hugo-guigo/lexico-misoginia-ptbr**

Para compartilhar progresso com a orientadora e o grupo, basta enviar o link acima — o
GitHub renderiza tudo (incluindo este relatório e a taxonomia) com formatação
adequada.
