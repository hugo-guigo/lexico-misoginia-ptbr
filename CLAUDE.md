# CLAUDE.md — Projeto IC: Léxico de Misoginia em Português Brasileiro

> Leia este arquivo inteiro antes de executar qualquer comando ou modificar qualquer arquivo.
> Para embasamento conceitual detalhado, leia também `contexto_ic.md`.

---

## O QUE É ESTE PROJETO

Iniciação Científica (PIBIC 2025/2026) na Universidade Federal de Goiás — Instituto de Informática.

**Objetivo:** Construir um léxico estruturado em português brasileiro para detecção automática de misoginia e violência contra a mulher em ambientes digitais, com aplicação em modelos de aprendizado de máquina.

**Pesquisador:** Hugo Guilherme de Assis Paula
**Orientadora:** Deborah Silva Alves Fernandes
**Projeto vinculado:** PI06069-2022

---

## PREFERÊNCIAS DE COMUNICAÇÃO

- **Respostas do assistente:** podem ser em **inglês** — o usuário não precisa de respostas em português. Mensagens de status, explicações e diálogo na conversa: inglês está ok.
- **Conteúdo do projeto** (código, comentários de código, docstrings, arquivos `.md` de entrega, CSV/JSON de saída, planilhas, relatórios, documentos para o grupo/orientadora): **continua em português brasileiro**, conforme as convenções do projeto.

---

## MAPA DE ARQUIVOS (estado real)

```
lexicos/
├── CLAUDE.md                                # este arquivo
├── contexto_ic.md                           # embasamento conceitual detalhado
├── README.md                                # visão geral do projeto
├── RELATORIO_PROGRESSO.md                   # relatório atual de progresso
├── taxonomia_misoginia_digital.md           # ENTREGA TAREFA 1 — 7 classes + 2 transversais
├── corpus_unificado_final.csv               # corpus principal: 74.338 docs (label 0/1)
│
├── outputs/                                 # pipeline V3 (atual)
│   ├── pipeline_semente_pmi.py              # Tarefa 2 — semente TF-IDF + expansão PMI
│   ├── anotar_lexico.py                     # Tarefa 3 — anotação automática + Kappa
│   ├── preparar_planilha_v2.py              # Tarefa 3 — planilha v2 (jun/2026)
│   ├── montar_corpus_teste.py               # Tarefa 4 — corpus de teste
│   ├── experimentos_modelos.py              # Tarefas 5/6 — SVM, LR, RF, MLP
│   ├── lexico_semente_tfidf.csv             # semente top-N por classe
│   ├── lexico_misoginia_v3_semente_pmi.csv/.json   # V3 — léxico após expansão PMI
│   ├── lexico_v3_anotado.csv                # V3 com classe lexical sugerida
│   ├── planilha_votacao_grupo_v2.csv        # ⭐ planilha para os 3 anotadores
│   ├── corpus_teste_frases.csv              # Tarefa 4 — frases rotuladas (held-out)
│   ├── resultados_modelos.csv               # resultados dos 4 modelos
│   └── plots/                               # gráficos de avaliação
│
├── artigo_erigo/                            # artigo curto para submissão ao ERIGO (LaTeX/SBC)
│   ├── artigo_erigo.tex
│   ├── referencias.bib
│   └── sbc-template.sty, sbc.bst, caption2.sty
│
└── docs/                                    # documentos locais (gitignored)
    ├── literatura/                          # PDFs de referência (copyrighted)
    └── orientacoes_profa/                   # orientações da Profa. Dra. Deborah
```

> **Nota.** Scripts V1/V2 em stems RSLP foram **removidos** do repositório em
> jun/2026 (`misogyny_lexicon_builder.py`, `classifier.py`,
> `pipeline_lexico_bigramas.py`, `pipeline_lexico_misoginia_langgraph.py`,
> `ajustar_limiar_e_filtrar_lexico.py`, `expandir_lexico_misoginia_gemini.py`,
> `micro_experiment_unigram.py`, `plot_result.py` e a pasta `lexico_misoginia_output/`).
> A pipeline atual usa apenas V3 (lematização spaCy + Monteles).
> Recuperar via `git log -- <arquivo>` se necessário.

**Datasets originais** (em `lexicons_corpus_misoginia/`):
- `HateBR_MOL/dataset/HateBR.csv` — 7.000 comentários do Instagram
- `ToLD-BR/ToLD-BR.csv` — 21.000 tweets com categorias (inclui coluna `misogyny`)
- `Portuguese-Hate-Speech/` — discurso de ódio hierárquico
- `OFFCOMBR/OffComBR2.arff` — tweets ofensivos com 81 categorias
- `OLID-BR/` — linguagem ofensiva brasileira

---

## ESTADO ATUAL DAS TAREFAS

### ✅ Tarefa 1 — Taxonomia
**Status: CONCLUÍDA (entrega escrita; pendente apenas validação coletiva do grupo)**

Documento `taxonomia_misoginia_digital.md` (Markdown — versionável; converter para `.docx` se o grupo pedir). **7 classes lexicais principais** + **2 subclasses transversais** (revisão pós-orientações da Profa. Deborah, jun/2026; substitui versão anterior de 11 classes). Escopo: hostilidade verbal/discursiva em meios digitais — exclui violência física.

| ID | Classe / Subclasse | Tipo | Origem |
|----|--------------------|------|--------|
| 1 | Descrédito | Principal | Anzovino et al. (2018) |
| 2 | Estereotipização | Principal | Anzovino et al. (2018) |
| 3 | Assédio Sexual | Principal | Anzovino et al. (2018) |
| 4 | Ameaças de Violência | Principal | Anzovino et al. (2018) |
| 5 | Dominação | Principal | Anzovino et al. (2018) |
| 6 | Culpabilização da Vítima | Principal | Sultana et al. (2021) |
| 7 | Objetificação Sexual | Principal | Sultana et al. (2021) |
| T1 | Misogynoir | Transversal (opcional) | Bailey (2010) |
| T2 | Violência Política Digital | Transversal (opcional) | Contribuição do projeto |

**Removidas em jun/2026:** Derailing (estruturalmente conversacional, não capturável por léxico) e Neossexismo (modo discursivo transversal — termos típicos viram Descrédito ou Dominação + T2 se político).

Fundamentação: Manne (2017/2020), Anzovino, Fersini & Rosso (2018), Sultana, Sarker & Bosu (2021), Bailey (2010), com citações explícitas no documento.

**Importante (metodológico):** as categorias são **classes lexicais sugeridas**, não classificação definitiva de misoginia. A unidade analítica segura é a **ocorrência contextualizada**.

**Pendente:** discussão coletiva do grupo para validar a taxonomia revisada.

---

### 🔄 Tarefa 2 — Construção do Léxico (Semente TF-IDF + Expansão PMI)
**Status: EM EXECUÇÃO**

Implementar `outputs/pipeline_semente_pmi.py` seguindo Monteles (2023):

**Etapa 2a — Semente TF-IDF:**
- Pré-processamento com **lematização spaCy** (`pt_core_news_lg`) — não stems.
- TF-IDF calculado por classe (misógino vs. não-misógino).
- Score discriminativo: `tfidf_mis / (tfidf_non + ε)`.
- Selecionar top-N por classe → `outputs/lexico_semente_tfidf.csv`.

**Etapa 2b — Expansão PMI:**
- Filtrar docs contendo termos da semente.
- Calcular coocorrências em janela deslizante.
- `O(x) = PMI(x, set_mis) − PMI(x, set_não_mis)` (Monteles, eq. 3-2).
- Threshold inicial `|O(x)| ≥ 1.5` → `outputs/lexico_misoginia_v3_semente_pmi.csv/.json`.

**Parâmetros configuráveis no topo do script:**
```python
TOP_N_SEMENTE    = 200    # top N por classe
MIN_FREQ_SEMENTE = 5
PMI_THRESHOLD    = 1.5
WINDOW_SIZE      = 5
MIN_FREQ_EXPAND  = 5
MIN_COOCORR      = 3
```

---

### ⏳ Tarefa 3 — Aplicar Taxonomia + Validação Manual (item "d" do Plano SIGAA)
**Status: NÃO INICIADA** (depende de 2)

- `outputs/anotar_lexico.py` — mapeia cada termo do V3 a uma classe lexical (1–7) via palavras-âncora da Tarefa 1.
- `outputs/preparar_planilha_v2.py` — gera `outputs/planilha_votacao_grupo_v2.csv` na estrutura revisada pela Profa.: **sem** coluna `eh_misogino` (palavras isoladas não são misóginas); **com** colunas `dependencia_contextual` (baixo/médio/alto) e `exemplo_uso` (frase real do corpus).
- Cada anotador valida/ajusta `classe_lexical` e `dependencia_contextual`.
- Calcular Kappa/Fleiss entre os 3 votos. Referência de formato: `lexicons_corpus_misoginia/HateBR_MOL/annotators/final_concordancia_Kappa_Fleiss.csv`.
- Consolidação → `outputs/lexico_v3_validado_final.csv/.json` com classe lexical majoritária e grau de dependência.

---

### ⏳ Tarefa 4 — Corpus de Frases de Teste
**Status: NÃO INICIADA** (depende de 3)

1. Extrair ~200–500 frases de **dados held-out** não usados na construção do léxico (a coluna `misogyny` do ToLD-BR é a melhor fonte).
2. Combinar com textos de notícias / internet brasileiros (coletados pelo usuário).
3. Rotular manualmente: com traços de misoginia (1) / sem traços (0).
4. Identificar a classe lexical (1–7) e transversais (T1/T2) opcionais para cada frase com label=1.
5. Salvar em `outputs/corpus_teste_frases.csv` com colunas: `text`, `label`, `categoria_id`, `categoria_nome`, `transversal`, `fonte`, `anotador`.

---

### ⏳ Tarefa 5 — Treinar Modelos com o Léxico
**Status: NÃO INICIADA** (depende de 4)

Usar `outputs/experimentos_modelos.py` (já implementado): treina no corpus principal, avalia no corpus de teste da Tarefa 4. Features: TF-IDF (lemas) + features do léxico V3 validado (`mean_score`, `misog_ratio`, `match_count`). Avaliação binária e por classe lexical.

---

### ⏳ Tarefa 6 — Experimentos com Mais Modelos
**Status: NÃO INICIADA** (depende de 4 e 5)

Novo script `outputs/experimentos_modelos.py`. Modelos: **SVM** (baseline), **Random Forest**, **Regressão Logística**, **RNN (LSTM/GRU)**. Tabela comparativa e comparação votação manual × pipeline automático.

---

## DECISÕES TÉCNICAS FIXADAS

**Não altere sem discutir:**

1. **Processamento de tokens:** **lematização com spaCy** (`pt_core_news_lg`) — não stems RSLP. Justificativa: o grupo precisa votar em termos legíveis. O código antigo em stems RSLP foi removido do repositório em jun/2026 (recuperável via git history).

2. **Corpus:** `corpus_unificado_final.csv` com 74.338 docs. Label 0 = não-misógino, Label 1 = misógino. Proporção: ~80% não-misógino (desbalanceado).

3. **Taxonomia:** **7 classes principais + 2 transversais** conforme `taxonomia_misoginia_digital.md` (revisão jun/2026). Não adicionar ou remover classes sem aprovação da orientadora.

4. **Léxico final para experimentos:** `outputs/lexico_v3_validado_final.csv` — usar este quando estiver pronto, não o V1 nem o V2 diretamente. **V1 e V2 (com stems) estão descontinuadas** — não aparecem em entregas atuais.

5. **Métricas prioritárias:** F1-Score (classe com traços de misoginia), Precision, Recall. Accuracy não é suficiente dado o desbalanceamento.

6. **Terminologia:** usar **"termos que podem estar associados a textos com traços de misoginia"** (forma curta: "termos com traços de misoginia") em vez de "termos misóginos". Palavras isoladas têm apenas significado de dicionário; só podem ser tratadas como integrantes de conteúdo com traços de misoginia **em contexto**.

---

## PROBLEMAS CONHECIDOS

1. **Ruído político no corpus:** HateBR e ToLD-BR contêm misoginia política, mas também insultos políticos genéricos. Termos como `bolsonar`, `lula`, `petist` podem aparecer no léxico. Tratar na anotação manual (Tarefa 3).

2. **Desbalanceamento de classes:** 80% não-misógino vs 20% misógino. Modelos precisam de `class_weight='balanced'` ou oversampling.

3. **NLTK offline:** A rede do ambiente não permite download de recursos NLTK. Stopwords/stemmer estão embutidos quando usados. Para lematização, usar **spaCy com `pt_core_news_lg` já instalado**.

4. **Categoria Derailing:** difícil de capturar por léxico isolado — é estruturalmente dependente de contexto conversacional. Esperar baixa cobertura para esta categoria.

5. **Léxicos legados (V1/V2) em stems:** os arquivos em `lexico_misoginia_output/` estão em stems RSLP. O V3 novo será em lemas spaCy e **não é compatível** com o V1/V2 — são entregas paralelas, não sequenciais.

---

## CONVENÇÕES DO PROJETO

- **Idioma do conteúdo do projeto:** português brasileiro (comentários de código, docstrings, arquivos de entrega, CSV/JSON, relatórios).
- **Idioma da conversa com o assistente:** inglês ok (ver "PREFERÊNCIAS DE COMUNICAÇÃO" acima).
- **Formato dos outputs:** CSV (para humanos) + JSON (para máquinas) sempre em par.
- **Encoding:** UTF-8 em todos os arquivos.
- **Nomes de arquivos:** snake_case, sem acentos.
- **Termos no léxico V3:** **lemas spaCy** (forma legível), não stems.
- **Colunas obrigatórias no léxico V3:** `term`, `polarity`, `score_norm`, `categoria_id`, `categoria_nome`, `freq_mis`, `freq_non`, `origem`.

---

## PRÓXIMOS PASSOS IMEDIATOS

1. **Tarefa 2:** implementar `outputs/pipeline_semente_pmi.py` (semente TF-IDF + expansão PMI em lemas) e rodar no corpus.
2. **Tarefa 3:** `outputs/anotar_lexico.py` + planilha de votação do grupo + Kappa/Fleiss.
3. **Tarefa 4:** corpus de teste — ToLD-BR held-out + textos de notícias coletados pelo usuário.
4. **Tarefas 5 e 6:** depois de 4.

---

## REFERÊNCIAS PRINCIPAIS

- Monteles, T. (2023). *Expansão automática de léxico para Análise de Sentimentos de Twitter*. UFG/INF. *(método PMI adaptado)*
- Manne, K. (2017). *Down Girl: The Logic of Misogyny*. *(taxonomia base — sexismo × misoginia)*
- Anzovino, M., Fersini, E., Rosso, P. (2018). *Automatic identification and classification of misogynistic language on Twitter*. *(taxonomia + detecção automática)*
- Sultana, S., Sarker, S., Bosu, A. (2021). *A rubric to identify misogynistic and sexist texts from software developer communications*. *(rubrica de anotação)*
- Bailey, M. (2010). *They aren't talking about me*. *(conceito de misogynoir)*
- Vargas, F. et al. (2022). HateBR. *(dataset principal)*
- Leite, J. A. et al. (2020). ToLD-BR. *(dataset secundário)*
