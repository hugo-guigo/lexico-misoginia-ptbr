# Relatório de Progresso — IC PIBIC 2025/2026

> **Léxico de Misoginia em Português Brasileiro para Detecção Automática em Ambientes Digitais**
>
> Projeto vinculado: **PI06069-2022** · UFG / Instituto de Informática
>
> **Pesquisador:** Hugo Guilherme de Assis Paula
> **Orientadora:** Profa. Dra. Deborah Silva Alves Fernandes
>
> Data deste relatório: **2026-06-01** (revisão pós-orientações da Profa.)

---

## Nota metodológica

> Organizamos termos associados a manifestações discursivas de misoginia em
> classes taxonômicas, indicando, para cada item, sua classe primária sugerida,
> grau de dependência contextual e exemplo de uso. **A classificação final da
> misoginia depende da ocorrência em contexto.**

> O projeto pode categorizar palavras e expressões segundo a taxonomia, mas
> essas categorias devem ser entendidas como **classes lexicais sugeridas**,
> **não** como classificação definitiva de misoginia. A unidade analítica
> mais segura é a **ocorrência contextualizada**.

Por essa razão, em todo este relatório (e em todos os materiais do projeto)
adotamos a expressão **"termos que podem estar associados a textos com traços
de misoginia"** (forma curta: **"termos com traços de misoginia"**), evitando
a formulação categórica "termos misóginos".

---

## 1. Sumário executivo

O projeto avançou da fase de fundamentação para a fase operacional. **Cinco
das seis tarefas previstas no plano foram concluídas:** (1) a taxonomia formal
foi consolidada em **7 classes principais + 2 subclasses transversais**
(redução em relação à versão anterior de 11 classes, após orientações da
Profa. Deborah); (2) o léxico V3 foi construído pelo método semente
TF-IDF + expansão PMI (Monteles, 2023) sobre um corpus unificado de 74.338
documentos, resultando em **531 termos** que podem estar associados a textos
com traços de misoginia; (3) os termos foram anotados automaticamente por
similaridade vetorial e uma planilha de votação (v2) foi preparada para os
3 anotadores do grupo, com colunas de **dependência contextual** e
**exemplo de uso**; (4) um corpus de teste com 333 frases já rotuladas
(ToLD-BR) + 100 vagas para notícias foi montado; (5–6) **quatro modelos foram
treinados e comparados** (SVM, Regressão Logística, Random Forest, MLP como
proxy de RNN) no corpus de treino e no corpus de teste.

**O que falta para fechar o ciclo:** (a) **votação dos 3 anotadores** sobre os
268 termos com traços de misoginia do V3, para gerar o léxico validado final;
(b) **coleta de textos de notícias** para enriquecer o corpus de teste e
melhorar a avaliação fora do domínio do Twitter; (c) substituir o MLP por
**LSTM/GRU real** quando o ambiente tiver PyTorch/TensorFlow (atualmente
bloqueado por espaço em disco). Nada disso é bloqueante para apresentar o
estado atual.

---

## 2. Tarefa 1 — Taxonomia (7 classes principais + 2 transversais) ✅

Documento principal: **[`taxonomia_misoginia_digital.md`](taxonomia_misoginia_digital.md)**.

A taxonomia adotada (revisada em jun/2026) tem **7 classes lexicais principais**
mais **2 subclasses transversais** opcionais. Recorte explícito: hostilidade
verbal/discursiva em meios digitais; exclui violência física:

| ID | Classe | Tipo | Origem |
|----|--------|------|--------|
| 1 | Descrédito | Principal | Anzovino, Fersini & Rosso (2018) |
| 2 | Estereotipização | Principal | Anzovino et al.; Glick & Fiske (1997) |
| 3 | Assédio Sexual | Principal | Anzovino et al.; Jane (2017); Mantilla (2015) |
| 4 | Ameaças de Violência | Principal | Anzovino et al.; Mantilla (2015) |
| 5 | Dominação | Principal | Manne (2017); Anzovino et al. (2018) |
| 6 | Culpabilização da Vítima | Principal | Sultana, Sarker & Bosu (2021); Manne |
| 7 | Objetificação Sexual | Principal | Sultana et al.; Anzovino et al.; Massanari (2017) |
| T1 | Misogynoir | Transversal | Bailey (2010) |
| T2 | Violência Política Digital | Transversal | Contribuição original do projeto |

**Mudanças em relação à versão anterior (11 classes):**

- **Derailing** (antiga classe 6) removida — fenômeno estruturalmente
  conversacional, não capturável por léxico isolado de unigramas.
- **Neossexismo** (antiga classe 9) removido como classe própria — é um modo
  discursivo transversal; seus termos típicos atuam como Descrédito (1) ou
  Dominação (5), e quando relevante o aspecto político recebem a transversal
  T2.
- **Misogynoir** (antiga classe 10) → subclasse transversal **T1**, podendo
  coexistir com qualquer classe principal.
- **Violência Política Digital** (antiga classe 11) → subclasse transversal
  **T2**, podendo coexistir com qualquer classe principal.

A redução atende à recomendação da Profa. Deborah de que **muitas classes em
NLP aumentam a complexidade sem ganho proporcional** — sete classes
discrimináveis lexicalmente, mais duas dimensões interseccionais opcionais,
oferecem cobertura adequada e maior estabilidade na anotação.

**Pendente.** Reunião com o grupo para validar coletivamente a taxonomia
revisada e as listas de palavras-âncora por classe.

---

## 3. Tarefa 2 — Construção do léxico V3 ✅

Script: **[`outputs/pipeline_semente_pmi.py`](outputs/pipeline_semente_pmi.py)**

Pipeline em duas etapas, seguindo **Monteles (2023)** adaptado para detecção
de misoginia e usando **lematização spaCy** (`pt_core_news_lg`) em vez de
stemming RSLP. **V1 e V2 (com stems) foram descontinuadas** — V3 é a única
versão referenciada nos artefatos atuais.

### Etapa 2a — Semente TF-IDF (400 termos)

Saída: [`outputs/lexico_semente_tfidf.csv`](outputs/lexico_semente_tfidf.csv).

- Calcula TF-IDF separadamente para a classe com traços de misoginia e para a
  classe não-misógina.
- Score discriminativo: `score = tfidf_mis / (tfidf_non + ε)`.
- Seleciona **top-200 por classe** → 200 sementes (com traços) + 200 sementes
  (sem traços).

### Etapa 2b — Expansão por PMI (531 termos no V3)

Saída: [`outputs/lexico_misoginia_v3_semente_pmi.csv`](outputs/lexico_misoginia_v3_semente_pmi.csv)
e [`.json`](outputs/lexico_misoginia_v3_semente_pmi.json).

- Para cada lema candidato x do corpus, calcula
  **O(x) = PMI(x, semente_traços_misoginia) − PMI(x, semente_sem_traços)**
  (eq. 3-2 de Monteles).
- Aceita se `|O(x)| ≥ 1.5`.
- Resultado: **268 termos com traços de misoginia + 263 termos sem traços =
  531 termos** no léxico V3.

**Parâmetros usados:**

| Parâmetro | Valor | Significado |
|---|---|---|
| `TOP_N_SEMENTE` | 200 | top N por classe na semente |
| `MIN_FREQ_SEMENTE` | 5 | freq. mínima do lema no subcorpus |
| `PMI_THRESHOLD` | 1.5 | limiar do score O(x) |
| `WINDOW_SIZE` | 5 | janela de coocorrência |
| `MIN_FREQ_EXPAND` | 5 | freq. mínima do candidato |
| `MIN_COOCORR` | 3 | mínimo de coocorrências válidas |

### Top-10 termos com traços de misoginia do V3

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

O corpus contém **muito comentário político insultuoso** rotulado como
misógino (`canalha`, `comunista`, `bandido`, `esquerdista`, `pastor`) — esses
termos não são intrinsecamente misóginos, mas aparecem **estatisticamente
associados** à classe positiva porque o discurso misógino brasileiro
frequentemente se sobrepõe ao discurso político de ódio. Esse ruído é
**esperado**, ilustra exatamente por que a unidade analítica segura é a
**ocorrência em contexto** (não a palavra isolada), e será tratado na
Tarefa 3 (votação humana e atribuição de **grau de dependência contextual**).

---

## 4. Tarefa 3 — Aplicação da taxonomia + validação manual ✅ (parte automática)

Scripts: **[`outputs/anotar_lexico.py`](outputs/anotar_lexico.py)** e
**[`outputs/preparar_planilha_v2.py`](outputs/preparar_planilha_v2.py)** (este
último gera a planilha v2 conforme orientações da Profa.).

### Anotação automática (concluída)

Para cada um dos 268 termos com traços de misoginia do V3, o pipeline calcula
a similaridade vetorial (spaCy) entre o lema e o **centróide** das
palavras-âncora de cada classe da taxonomia, sugerindo a **classe lexical**
de maior similaridade. Resultado em
[`outputs/lexico_v3_anotado.csv`](outputs/lexico_v3_anotado.csv).

Após a redução da taxonomia (11 → 7 classes principais + 2 transversais):

| Classe lexical sugerida | Nº de termos |
|---|---|
| Descrédito (1) — pode incluir T2 | 44 |
| Ameaças de Violência (4) | 31 |
| Assédio Sexual (3) | 15 |
| Estereotipização (2) | 3 |
| Dominação (5) | (a confirmar após reanotação) |
| Culpabilização da Vítima (6) | (a confirmar após reanotação) |
| Objetificação Sexual (7) — incluindo migração de antiga 8 | 1 |
| _(sem sugestão — abaixo do limiar)_ | 137 |
| Termos marcados com transversal T2 (contexto político) | ~35 |
| Termos marcados com transversal T1 (Misogynoir) | 1 |

A grande quantidade de termos com transversal T2 reflete o ruído político
mencionado. A votação humana vai redistribuir esses termos (muitos podem
sair como "sem traços de misoginia" se o contexto típico for político-genérico
e não direcionado a mulheres).

### Pendente: votação do grupo (3 anotadores) — planilha v2

Arquivo: **[`outputs/planilha_votacao_grupo_v2.csv`](outputs/planilha_votacao_grupo_v2.csv)**

A planilha foi **reestruturada conforme orientações da Profa. Deborah**:

- **Removida** a coluna `anotadorN_eh_misogino` — palavras sozinhas têm
  apenas o significado de dicionário; **só podem ser classificadas como
  integrantes de conteúdos com traços de misoginia contextualmente**.
- **Adicionada** a coluna `dependencia_contextual` (valores: `baixo`, `médio`,
  `alto`) — quanto o significado misógino do termo depende do contexto.
- **Adicionada** a coluna `exemplo_uso` — uma frase real do corpus em que o
  termo aparece.
- Cada anotador valida/ajusta a **classe lexical** sugerida e o **grau de
  dependência contextual**.

Após os 3 preencherem, rodar o script de consolidação que calcula o **Kappa
de Fleiss** na concordância da classe e do grau de dependência, e gera o
léxico V3 validado final.

---

## 5. Tarefa 4 — Corpus de frases de teste ✅ (template)

Script: **[`outputs/montar_corpus_teste.py`](outputs/montar_corpus_teste.py)**
Saída: **[`outputs/corpus_teste_frases.csv`](outputs/corpus_teste_frases.csv)**

**Composição atual** (esperando preenchimento):

| Categoria | Quantidade | Origem |
|---|---|---|
| Com traços de misoginia (label=1) | 133 | ToLD-BR, com ≥ 2 votos de misoginia no anotador |
| Sem traços (label=0) | 200 | ToLD-BR, **nenhum** dos rótulos de toxicidade ativado |
| Vagas para notícias | 100 | em branco, preencher manualmente |

Colunas: `text, label, categoria_id, categoria_nome, fonte, anotador, votos_misoginia_told`.

### Pendente: preenchimento manual

1. Para cada uma das 133 linhas com label=1, preencher `categoria_id` (1–7) e
   `categoria_nome`; opcionalmente marcar `T1`/`T2` em coluna extra.
2. Para as 100 linhas em branco com `fonte=noticias`: coletar textos reais de
   notícias / redes sociais brasileiros, preencher `text`, `label` (0/1), e —
   quando `label=1` — a classe lexical principal.

---

## 6. Tarefas 5 e 6 — Treinamento e comparação de modelos ✅

Script: **[`outputs/experimentos_modelos.py`](outputs/experimentos_modelos.py)**
Resultados: **[`outputs/resultados_modelos.csv`](outputs/resultados_modelos.csv)**

### Setup

- **Features:** TF-IDF de lemas (unigramas, máx. 10.000 features) + 3 features
  derivadas do léxico V3 (`mean_score`, `misog_ratio`, `match_count`).
- **Modelos comparados** (com `class_weight='balanced'`):
  - **SVM** (`LinearSVC`)
  - **Regressão Logística**
  - **Random Forest** (100 árvores, profundidade máxima 20)
  - **MLP** — proxy de RNN (1 camada oculta, 64 neurônios)
- **Cross-validation:** 3-fold no corpus de treino (35.791 docs após limpeza).
- **Teste out-of-sample:** os 333 documentos rotulados do corpus de teste.

### Resultados — cross-validation (corpus de treino)

| Modelo | F1 (classe com traços) | Precisão | Recall |
|---|---|---|---|
| SVM (LinearSVC) | 0.529 ± 0.006 | 0.440 | 0.664 |
| **Regressão Logística** | **0.554 ± 0.004** | 0.456 | 0.706 |
| Random Forest | 0.477 ± 0.003 | 0.410 | 0.570 |
| MLP (proxy RNN) | 0.467 ± 0.017 | 0.639 | 0.368 |

### Resultados — corpus de teste (out-of-sample)

| Modelo | F1 (classe com traços) | Precisão | Recall |
|---|---|---|---|
| **SVM (LinearSVC)** | **0.871** | 0.910 | 0.835 |
| Regressão Logística | 0.846 | 0.920 | 0.782 |
| Random Forest | 0.560 | 0.718 | 0.459 |
| MLP (proxy RNN) | 0.506 | 1.000 | 0.338 |

### Leitura dos resultados

- **A diferença CV × teste é grande** porque o corpus de treino tem o ruído
  político (insultos políticos rotulados como misoginia) e o corpus de teste
  foi montado com rótulos de alta confiança (≥ 2 votos no ToLD-BR). O F1 de
  teste perto de **0.87** mostra que os modelos lineares (SVM, LR)
  generalizam bem para o "subconjunto limpo".
- **SVM e Regressão Logística** dominam — esperado em texto curto com TF-IDF.
- **Random Forest** tem pior desempenho que os lineares (típico em alta
  dimensão).
- **MLP** sofreu com o desbalanceamento (`precision=1.0, recall=0.34` no
  teste — está classificando quase tudo como "sem traços" exceto casos muito
  confiantes).

### TODO RNN real

O ambiente atual **não tem PyTorch nem TensorFlow** (a instalação falhou por
falta de espaço em disco). O `MLPClassifier` foi usado como proxy de modelo
neural denso. **Próximo passo:** quando o ambiente tiver espaço, instalar
`torch` e implementar **LSTM/GRU** com embeddings spaCy ou aleatórios +
camada de atenção opcional.

---

## 7. Próximos passos (checklist)

### Grupo de pesquisa (3 anotadores)
- [ ] Cada anotador abre [`outputs/planilha_votacao_grupo_v2.csv`](outputs/planilha_votacao_grupo_v2.csv) e preenche, para cada termo, sua **classe lexical sugerida** e o **grau de dependência contextual** (`baixo`/`médio`/`alto`).
- [ ] Devolver o arquivo preenchido.

### Orientadora
- [ ] Validar a taxonomia revisada (7 + 2) em [`taxonomia_misoginia_digital.md`](taxonomia_misoginia_digital.md).
- [ ] Revisar os pontos abertos para discussão no fim da taxonomia.

### Pesquisador (Hugo)
- [ ] Coletar ~100 frases de notícias / redes brasileiras e preencher as linhas com `fonte=noticias` em [`outputs/corpus_teste_frases.csv`](outputs/corpus_teste_frases.csv).
- [ ] Preencher `categoria_id` (1–7) para as 133 linhas com label=1 do ToLD-BR.
- [ ] (Quando houver espaço) instalar `torch` e substituir o MLP por LSTM/GRU.
- [ ] Submeter artigo curto ao ERIGO (em preparação em `artigo_erigo/`).

### Assistente (Claude)
- [ ] Re-rodar consolidação após o grupo votar.
- [ ] Re-rodar `experimentos_modelos.py` com o léxico validado final + corpus de teste ampliado.

---

## 8. Como reproduzir tudo localmente

```bash
# Pré-requisitos
pip install spacy scikit-learn pandas numpy scipy nltk
python -m spacy download pt_core_news_lg

# Tarefa 2 — léxico V3 (lematização cacheia em outputs/_cache_lemmas.pkl)
python3 outputs/pipeline_semente_pmi.py

# Tarefa 3 — anotação automática + planilha de votação v2
python3 outputs/anotar_lexico.py --gerar-planilha
python3 outputs/preparar_planilha_v2.py

# Tarefa 4 — corpus de teste (template)
python3 outputs/montar_corpus_teste.py

# Tarefa 5/6 — treinar e comparar 4 modelos
python3 outputs/experimentos_modelos.py
```

Cada script é **idempotente** — pode ser executado várias vezes sem efeitos
colaterais. O cache de lemas é gerado uma vez (~3 min) e reutilizado.

---

## 9. Repositório

Todo o código, dados de saída e documentação estão disponíveis no GitHub:

🔗 **https://github.com/hugo-guigo/lexico-misoginia-ptbr**
