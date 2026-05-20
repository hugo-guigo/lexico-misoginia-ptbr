# Léxico de Misoginia em Português Brasileiro

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PIBIC](https://img.shields.io/badge/PIBIC-2025%2F2026-green.svg)](https://propesq.ufg.br)

Construção de um **léxico estruturado em português brasileiro** para detecção
automática de **misoginia e violência contra a mulher em ambientes digitais**, com
aplicação em modelos de aprendizado de máquina.

> Iniciação Científica PIBIC 2025/2026 · Universidade Federal de Goiás · Instituto de
> Informática · Projeto vinculado **PI06069-2022**
>
> **Pesquisador:** Hugo Guilherme de Assis Paula
> **Orientadora:** Profa. Dra. Deborah Silva Alves Fernandes

---

## 📚 Por onde começar

| Documento | O que contém |
|---|---|
| [`taxonomia_misoginia_digital.md`](taxonomia_misoginia_digital.md) | **Taxonomia formal** das 11 classes de misoginia digital, com citações dos especialistas (Anzovino, Manne, Sultana, Bailey). Entrega da Tarefa 1. |
| [`RELATORIO_PROGRESSO.md`](RELATORIO_PROGRESSO.md) | **Relatório de progresso** atual — leia este se você é orientadora/colega revisando o andamento. |
| [`contexto_ic.md`](contexto_ic.md) | Embasamento conceitual detalhado (referência interna). |
| [`CLAUDE.md`](CLAUDE.md) | Instruções de trabalho do projeto e decisões técnicas fixadas. |

## 🗂️ Estrutura do repositório

```
.
├── README.md                          # este arquivo
├── LICENSE                            # MIT
├── CLAUDE.md                          # instruções e estado do projeto
├── contexto_ic.md                     # embasamento conceitual
├── taxonomia_misoginia_digital.md     # ⭐ Tarefa 1 — taxonomia das 11 classes
├── RELATORIO_PROGRESSO.md             # ⭐ relatório de progresso
│
├── corpus_unificado_final.csv         # corpus principal (74.338 docs antes de limpeza)
│
├── outputs/                           # ⭐ artefatos do pipeline
│   ├── pipeline_semente_pmi.py        # Tarefa 2 — semente TF-IDF + PMI
│   ├── anotar_lexico.py               # Tarefa 3 — anotação automática + votação
│   ├── montar_corpus_teste.py         # Tarefa 4 — corpus de teste
│   ├── experimentos_modelos.py        # Tarefa 5/6 — SVM, RL, RF, MLP
│   │
│   ├── lexico_semente_tfidf.csv       # semente (top-200 por classe)
│   ├── lexico_misoginia_v3_semente_pmi.csv/.json  # V3 — léxico expandido por PMI
│   ├── lexico_v3_anotado.csv          # V3 com categoria sugerida automaticamente
│   ├── planilha_votacao_grupo.csv     # planilha para os 3 anotadores do grupo
│   ├── corpus_teste_frases.csv        # corpus de teste (template)
│   └── resultados_modelos.csv         # resultados dos modelos
│
├── lexico_misoginia_output/           # léxicos legados V1/V2 (em stems RSLP)
│
├── misogyny_lexicon_builder.py        # léxico V1 (LLR, RSLP)
├── classifier.py                      # classificador base (SVM + TF-IDF do V1)
├── pipeline_lexico_bigramas.py        # pipeline de bigramas (PMI + LLR)
├── pipeline_lexico_misoginia_langgraph.py  # pipeline LangGraph + FastText + KMeans
└── ...
```

## ⚙️ Como rodar

**Pré-requisitos** (Python 3.10+):

```bash
pip install spacy scikit-learn pandas numpy scipy nltk gensim
python -m spacy download pt_core_news_lg
```

**Pipeline completo** (cache de lemas é gerado na primeira execução, depois reutilizado):

```bash
# Tarefa 2 — construir o léxico V3 (semente TF-IDF + expansão PMI)
python3 outputs/pipeline_semente_pmi.py

# Tarefa 3 — anotar automaticamente + gerar planilha de votação
python3 outputs/anotar_lexico.py --gerar-planilha

# Tarefa 4 — montar o corpus de teste (template para rotulação manual)
python3 outputs/montar_corpus_teste.py

# Tarefa 5/6 — treinar modelos e comparar
python3 outputs/experimentos_modelos.py
```

Após o grupo preencher a planilha de votação:

```bash
python3 outputs/anotar_lexico.py --consolidar
# gera lexico_v3_validado_final.csv + concordancia_kappa_fleiss.csv
```

## 📊 Datasets utilizados

| Dataset | Tamanho | Uso | Licença |
|---|---|---|---|
| HateBR / HateBRXplain | 7.000 / 7.000 | Treino | Própria |
| ToLD-BR (binário e per-categoria) | 21.000 / 21.000 | Treino + teste (held-out) | Própria |
| Portuguese-Hate-Speech | 5.670 | Treino | Própria |
| OFFCOMBR | — | Análise | Própria |
| OLID-BR | — | Análise | Própria |

Os datasets originais **não fazem parte deste repositório** (têm licenças próprias e
totalizam ~76 MB). Eles são baixados do GitHub do projeto correspondente. O arquivo
agregado `corpus_unificado_final.csv` aqui no repo é o produto de unificação binária
desses datasets.

## 📜 Referências principais

- **Anzovino, M.; Fersini, E.; Rosso, P.** (2018) — *Automatic identification and
  classification of misogynistic language on Twitter*. CoNLL.
- **Manne, K.** (2017) — *Down Girl: The Logic of Misogyny*. Oxford University Press.
- **Sultana, S.; Sarker, S.; Bosu, A.** (2021) — *A Rubric to identify misogynistic and
  sexist texts in developer communications*.
- **Bailey, M.** (2010) — *Misogynoir in Medical Media*. Catalyst.
- **Monteles, T.** (2023) — *Expansão automática de léxico para Análise de Sentimentos de
  Twitter*. UFG/INF. (método PMI adaptado)
- **Vargas, F. et al.** (2022) — HateBR.
- **Leite, J. A. et al.** (2020) — ToLD-BR.

Lista completa em [`taxonomia_misoginia_digital.md`](taxonomia_misoginia_digital.md).

## 🤝 Como contribuir

Este é o repositório oficial da IC. Contribuições do grupo de pesquisa:

1. **Votação da taxonomia**: 3 anotadores devem preencher
   [`outputs/planilha_votacao_grupo.csv`](outputs/planilha_votacao_grupo.csv).
2. **Coleta de notícias**: adicionar frases reais de notícias/redes sociais nas linhas
   `fonte=noticias` de [`outputs/corpus_teste_frases.csv`](outputs/corpus_teste_frases.csv).
3. **Issues / PRs**: bem-vindos para apontar erros na taxonomia ou propor classes
   adicionais com fundamentação teórica.

## 📄 Licença

[MIT](LICENSE) — uso livre, com atribuição. Datasets de terceiros têm suas licenças
próprias.
