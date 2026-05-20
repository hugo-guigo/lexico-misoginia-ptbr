# contexto_ic.md — Referência Conceitual e Teórica

> Arquivo de suporte ao CLAUDE.md. Leia quando precisar de embasamento teórico,
> entender decisões metodológicas, ou implementar algo relacionado à taxonomia.

---

## 1. CONTEXTO E PROBLEMA

### O problema central

A detecção automática de discurso de ódio misógino em português brasileiro carece de recursos lexicais adequados. Os léxicos existentes (HateBR, ToLD-BR, MOL, OFFCOMBR) tratam misoginia como subcategoria genérica do discurso de ódio, resultando em:

- Baixa granularidade semântica
- Pouca distinção entre violência explícita e implícita
- Ausência de categorias interseccionais (ex.: misogynoir)
- Léxicos construídos para inglês sendo usados para português

### O que este projeto constrói

Um léxico especializado em misoginia digital em português brasileiro com:
- Termos categorizados por tipo de violência (11 categorias)
- Validação por múltiplos anotadores
- Metodologia replicável documentada
- Aplicabilidade em modelos de ML

---

## 2. TAXONOMIA DAS 11 CATEGORIAS

### Bases teóricas

A taxonomia sintetiza três fontes:
1. **Manne (2017, 2020):** fundamento filosófico — misoginia como "braço punitivo" do patriarcado
2. **Anzovino, Fersini & Rosso (2018):** primeira taxonomia para classificação automática no Twitter
3. **Sultana, Sarker & Bosu (2021):** taxonomia para textos digitais profissionais

**Distinção fundamental (Manne, 2017):**
- **Sexismo** = dimensão ideológica/justificativa da hierarquia patriarcal
- **Misoginia** = dimensão punitiva/coercitiva que pune mulheres que transgridem normas

### As 11 categorias em detalhe

#### Categoria 1 — Descrédito
Difamação ou desqualificação da mulher sem intenção ofensiva explícita, minando credibilidade, competência ou autoridade.
- **Manifestações:** termos que questionam capacidade intelectual, infantilizam, minimizam conquistas
- **Exemplos de stems:** `imbecil`, `cretin`, `débil`, `pirralh`, `cafaj`, `ordinári`, `molusc`, `crápul`
- **Refs:** Sultana et al. (2021); Anzovino et al. (2018)

#### Categoria 2 — Estereotipização
Atribuição de características/papéis fixos com base em estereótipos de gênero.
- **Manifestações:** papéis domésticos, estereótipos físicos, generalização de comportamentos femininos
- **Exemplos de stems:** `mulherzinh`, `loirinh`, `tpm`, `gord`, `magr`, `mocinh`
- **Refs:** Glick & Fiske (1997); Anzovino et al. (2018)

#### Categoria 3 — Assédio Sexual
Sexualização não consentida em espaços digitais.
- **Manifestações:** comentários sobre corpo, propostas sexuais, insultos sexuais, uso pejorativo de identidade sexual
- **Exemplos de stems:** `safad`, `piranh`, `vadi`, `piriguet`, `sapat`, `sapata`, `fême`, `vagin`
- **Refs:** Jane (2017); Mantilla (2015)

#### Categoria 4 — Ameaças de Violência
Intimidação com ameaças de violência física, sexual ou psicológica.
- **Manifestações:** ameaças diretas, incitação, expressões de desejo de sofrimento
- **Exemplos de stems:** `incit`, `incitaç`, `apanh`, `viol`, `atir`, `terror`, `maldit`
- **Refs:** Jane (2017); Mantilla (2015)

#### Categoria 5 — Dominação
Exercício de controle e imposição de hierarquia patriarcal.
- **Manifestações:** imperativos de silêncio, negação de agência, resistência à liderança feminina
- **Exemplos de stems:** `quintal`, `rebeld`, `varr`, `cass`, `manobr`, `deveri`
- **Refs:** Manne (2017); Anzovino et al. (2018)

#### Categoria 6 — Derailing
Estratégia discursiva de desvio e invalidação de questões legítimas levantadas por mulheres.
- **Manifestações:** "e os homens?", acusações de vitimismo, whataboutism, minimização
- **ATENÇÃO:** Difícil de capturar por léxico isolado — depende de contexto conversacional
- **Exemplos de stems:** `mimad`, `artificial` (em contexto de "causa artificial")
- **Refs:** Manne (2017); MOL (Vargas et al., 2024)

#### Categoria 7 — Culpabilização da Vítima
Responsabilização da mulher pelos problemas/agressões que sofre.
- **Manifestações:** "ela pediu", questionamento de roupas/comportamento, minimização de agressão
- **Exemplos de stems:** `submiss`, `decot` (em contexto culpabilizador)
- **Refs:** Sultana et al. (2021); Manne (2017)

#### Categoria 8 — Objetificação Sexual
Redução da mulher a objeto sexual ou partes do corpo.
- **Manifestações:** desumanização por hipersexualização, classificações físicas, linguagem de mercadoria
- **Exemplos de stems:** `biscat`, `raparig`, `farinh`, `pelud`, `culh`, `fuf`, `pên`
- **Refs:** Anzovino et al. (2018); Massanari (2017)

#### Categoria 9 — Neossexismo
Forma moderna e sutil de sexismo que nega existência de discriminação.
- **Manifestações:** discurso de "igualdade já alcançada", ataques ao feminismo, "meritocracia"
- **Exemplos de stems:** `feminazi`, `feminaz`, `feminist` (pejorativo), `gayz`, `demasi`
- **Refs:** Manne (2020); Banet-Weiser & Miltner (2016)

#### Categoria 10 — Misogynoir ⚠️ CONTRIBUIÇÃO ORIGINAL
Intersecção de misoginia e racismo direcionada especificamente a mulheres negras.
- **Conceito:** cunhado por Moya Bailey (2010)
- **Manifestações:** hipersexualização racializada, estereótipos específicos de mulheres negras
- **LACUNA CRÍTICA:** Nenhum léxico existente contempla — é uma contribuição original deste projeto
- **Exemplos de stems:** `muçulman` (interseção gênero+religião/raça), `pret` (quando misógino racial)
- **Refs:** Bailey (2010); Silva (2022) — Racismo Algorítmico

#### Categoria 11 — Violência Política Digital ⚠️ CONTRIBUIÇÃO ORIGINAL
Ataques sistemáticos contra mulheres em posições de liderança política.
- **Manifestações:** deslegitimação por gênero, ataques coordenados em eleições, doxxing de políticas
- **LACUNA CRÍTICA:** Ausente em todos os léxicos existentes
- **Contexto BR:** Intensificada nas eleições 2018, 2020, 2022, 2024
- **Exemplos de stems:** `deput`, `senad`, `mandat`, `inelegível`, `traid` (em contexto político)
- **Refs:** Mantilla (2015); Jane (2017); SciELO Brasil (2023)

---

## 3. CORPUS E DATASETS

### corpus_unificado_final.csv
- **Tamanho:** 74.338 documentos
- **Origem:** Fusão de HateBR + ToLD-BR + variações anotadas
- **Colunas:** `text`, `label`, `source`
- **Label:** 0 = não-misógino (60.170), 1 = misógino (14.168)
- **Proporção:** ~80/20 — **desbalanceado**, usar class_weight='balanced' nos modelos
- **Atenção:** Muitos textos são apenas números (IDs) — filtrar com `len(text) > 5`

### HateBR (lexicons_corpus_misoginia/HateBR_MOL/)
- 7.000 comentários do Instagram
- Anotados por especialistas com 3 camadas
- Categorias: offensive, hate speech, sexism entre outros
- Melhor dataset para misoginia no Instagram

### ToLD-BR (lexicons_corpus_misoginia/ToLD-BR/)
- 21.000 tweets
- **Colunas separadas por tipo de ódio:** misogyny, racism, homophobia, insult, obscene, xenophobia
- `ToLD-BR/experiments/data/agreement_files/misogyny_alpha.csv` — concordância específica para misoginia
- Melhor dataset para isolar misoginia de outros tipos de ódio

### OFFCOMBR (lexicons_corpus_misoginia/OFFCOMBR/)
- Tweets em formato .arff (Weka)
- 81 categorias hierárquicas
- Dataset mais antigo (2017) — pode estar desatualizado

---

## 4. PIPELINE TÉCNICO

### Pré-processamento padrão
```python
def preprocess(text):
    text = text.lower()
    # remover URLs, menções, hashtags
    # remover não-letras PT
    # tokenizar
    # remover stopwords (lista embutida ~200 termos PT-BR)
    # aplicar stemmer RSLP simplificado
    return lista_de_stems
```

### Stemmer RSLP
- Implementação simplificada embutida (sem NLTK)
- Suficiente para fins lexicográficos
- Se precisar do RSLP original: `from nltk.stem import RSLPStemmer` (requer NLTK instalado)
- **Todos os termos do léxico estão em formato stem**

### Features do classificador
1. TF-IDF sobre stems (max_features=50.000, ngram_range=(1,2), sublinear_tf=True)
2. Features do léxico (3 valores por documento):
   - `mean_score`: média dos scores dos termos encontrados
   - `misog_ratio`: proporção de termos com score > 0
   - `match_count`: número de termos encontrados

### Resultado dos experimentos (já realizados)
| Configuração | F1 (classe mis) | Precision | Recall |
|---|---|---|---|
| TF-IDF puro (LinearSVC) | 0.6189 | — | — |
| TF-IDF + Léxico (LinearSVC) | 0.6347 | — | — |
| Léxico puro (threshold -2.2) | ~0.49 | — | — |
| Alta precisão (C=best, sem balanceamento) | — | ~0.77 | ~0.14–0.19 |

---

## 5. LÉXICOS: EVOLUÇÃO DAS VERSÕES

### V1 (lexico_misoginia_v1.csv)
- **Método:** Log-Likelihood Ratio + suavização de Laplace + prior ajustado (α=0.2)
- **Tamanho:** 8.767 termos totais, 1.959 misóginos
- **Problema:** Muitos termos políticos e genéricos, limiar fraco

### V2 (lexico_misoginia_v2_final.csv)
- **Método:** V1 com filtragem por percentil 95% + filtro linguístico
- **Tamanho:** 4.109 termos, 188 misóginos no núcleo
- **Problema:** Ainda tem ruído político; núcleo pequeno (188 termos)

### V3 (lexico_misoginia_v3_semente_pmi.csv)
- **Método:** Semente TF-IDF (Monteles, 2023) + expansão PMI
- **Tamanho:** 1.324 termos totais, 399 misóginos brutos
- **Validado:** 130 misóginos com categoria taxonômica

### V3 Validado Final (lexico_v3_validado_final.csv)
- **Colunas:** term, polarity, score_norm, O_score, pmi_mis, pmi_non, freq_mis, freq_non, n_cooc_mis, n_cooc_non, origem, decisao, categoria_id, categoria_nome, confianca, obs_anotacao
- **Este é o arquivo para usar nos experimentos (Tarefas 5 e 6)**

---

## 6. TAREFAS 4, 5 E 6 — ORIENTAÇÕES

### Tarefa 4: Corpus de Frases de Teste

**Objetivo:** ~200-500 frases rotuladas manualmente para avaliar o léxico em texto não visto.

**Estratégia recomendada:**
1. Extrair frases misóginas dos datasets originais por categoria
2. Usar `ToLD-BR/experiments/data/agreement_files/misogyny_alpha.csv` como base — já tem anotações
3. Complementar com coleta manual de comentários de notícias sobre mulheres
4. Rotular com: `text`, `label`, `categoria_id`, `categoria_nome`, `fonte`, `anotador`

**Formato do arquivo de saída:**
```csv
text,label,categoria_id,categoria_nome,fonte,anotador
"texto aqui",1,3,Assédio Sexual,ToLD-BR,Hugo
```

### Tarefa 5: Avaliação do Léxico

**O que já existe:** `classifier.py` com SVM + TF-IDF + features do léxico.

**O que fazer:**
1. Carregar `lexico_v3_validado_final.csv`
2. Aplicar o classificador do corpus de teste (Tarefa 4)
3. Avaliar por categoria (não só binário)
4. Comparar com baseline (sem léxico)

### Tarefa 6: Múltiplos Modelos

**Modelos a implementar:**
```python
from sklearn.ensemble import RandomForestClassifier          # RF
from sklearn.linear_model import LogisticRegression          # RL
from tensorflow.keras.layers import LSTM, GRU                # RNN
```

**Comparação final:**
- SVM (já feito)
- Random Forest
- Regressão Logística
- RNN (LSTM ou GRU com embeddings BERTimbau ou word2vec PT)
- Ver se a votação manual do grupo concorda com o pipeline automático

**Métricas:** Precision, Recall, F1 (classe 1), F1-macro, AUC-ROC

---

## 7. REFERÊNCIAS COMPLETAS

```
ANZOVINO, M.; FERSINI, E.; ROSSO, P. (2018). Automatic identification and classification 
of misogynistic language on Twitter. CONLL 2018.

BAILEY, M. (2010). Misogynoir in Medical Media. Catalyst.

GLICK, P.; FISKE, S.T. (1997). The Ambivalent Sexism Inventory. JPSP, v.70, n.3.

JANE, E.A. (2017). Misogyny Online: A Short (and Brutish) History. SAGE.

LEITE, J.A. et al. (2020). Toxic Language Detection in Social Media for Brazilian 
Portuguese: New Dataset and Multilingual Analysis. AACL 2020.

MANNE, K. (2017). Down Girl: The Logic of Misogyny. Oxford University Press.

MANNE, K. (2020). Entitled: How Male Privilege Hurts Women. Crown Publishing.

MANTILLA, K. (2015). Gendertrolling: How Misogyny Went Viral. Praeger.

MONTELES, T. (2023). Expansão automática de léxico para Análise de Sentimentos 
de Twitter. TCC, UFG/INF.

SILVA, T. (2022). Racismo Algorítmico. Edições Sesc.

SOUZA, F.; NOGUEIRA, R.; LOTUFO, R. (2020). BERTimbau: Pretrained BERT Models 
for Brazilian Portuguese. BRACIS 2020.

SULTANA, S.; SARKER, J.; BOSU, A. (2021). A Rubric to identify misogynistic and 
sexist texts in developer communications.

VARGAS, F. et al. (2022). HateBR: A Large Expert Annotated Corpus of Brazilian 
Instagram Comments. LREC 2022.

VARGAS, F. et al. (2024). Context-aware and expert data resources for Brazilian 
Portuguese hate speech detection. NLP, v.31, n.2.
```
