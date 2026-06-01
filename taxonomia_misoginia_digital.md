# Taxonomia da Misoginia Digital em Português Brasileiro

> Documento de trabalho — Iniciação Científica PIBIC 2025/2026
> Projeto PI06069-2022 · UFG / Instituto de Informática
> Pesquisador: Hugo Guilherme de Assis Paula · Orientadora: Deborah Silva Alves Fernandes
>
> **Status:** versão revisada após orientações da Profa. Dra. Deborah (jun/2026).
> Substitui a versão anterior de 11 classes.

---

## Nota metodológica fundamental

O projeto categoriza palavras e expressões segundo a taxonomia abaixo, mas essas
categorias devem ser entendidas como **classes lexicais sugeridas**, **não** como
classificação definitiva de misoginia. A unidade analítica mais segura é a
**ocorrência contextualizada**: uma palavra, isolada, possui apenas o significado
de dicionário; só pode ser tratada como integrante de um texto **com traços de
misoginia** quando observada em contexto.

Por essa razão, em todo o material do projeto adotamos a expressão **"termos que
podem estar associados a textos com traços de misoginia"** (ou, na forma curta,
**"termos com traços de misoginia"**) — evitando a categórica **"termos
misóginos"**.

---

## 1. Introdução e escopo

Este documento apresenta a taxonomia adotada no projeto: **7 classes lexicais
principais** que organizam, por *tipo de hostilidade discursiva*, os termos
associados a manifestações de misoginia em ambientes digitais, mais **2
subclasses transversais** (não obrigatórias) que podem coexistir com qualquer
classe principal.

### 1.1 Recorte do objeto

A taxonomia trata da misoginia **expressa pela linguagem em meios digitais** —
comentários, postagens, tweets, mensagens. O recorte é deliberadamente
**verbal/discursivo e digital**:

- **Inclui:** ofensas, estereótipos, sexualização não consentida, ameaças
  verbais, silenciamento, desqualificação e ataques interseccionais expressos
  em texto.
- **Exclui:** a violência **física** propriamente dita (agressão, feminicídio),
  bem como crimes digitais que não se realizam primariamente pela linguagem
  (ex.: vazamento de imagens íntimas, *stalking* técnico).

Essa delimitação é metodologicamente necessária: o produto final do projeto é
um léxico aplicável a modelos de aprendizado de máquina, e um léxico só captura
o que se manifesta **no texto**.

### 1.2 Distinção conceitual: sexismo × misoginia

A taxonomia parte da distinção formulada por **Manne (2017)**:

- **Sexismo** — a dimensão **ideológica/justificativa** do patriarcado: o
  conjunto de crenças que naturaliza e racionaliza a hierarquia de gênero.
- **Misoginia** — a dimensão **punitiva/coercitiva**: o "braço de aplicação da
  lei" do patriarcado, que **pune e controla** as mulheres que transgridem as
  normas de gênero.

As 7 classes principais descrevem **mecanismos lexicais associados a punição e
controle** — mas, repetimos, a definição de cada ocorrência depende sempre do
contexto.

---

## 2. Fundamentação: as classificações dos especialistas

A taxonomia **não é original em sua maior parte** — ela sintetiza e adapta
classificações já consolidadas por especialistas em misoginia. Esta seção
apresenta cada fonte e o que ela contribui.

### 2.1 Manne (2017, 2020) — arcabouço conceitual

Kate Manne fornece o **arcabouço teórico**: misoginia como sistema que
**policia** o comportamento feminino. Desse arcabouço derivam classes ligadas
a **controle** (Dominação), **punição** (Ameaças, Descrédito) e a lógica de
**culpabilização** da mulher que "saiu da linha" (Culpabilização da Vítima).

### 2.2 Anzovino, Fersini & Rosso (2018) — taxonomia para classificação automática

No artigo *Automatic identification and classification of misogynistic language
on Twitter* (CoNLL 2018), os autores propõem a **primeira taxonomia operacional**
voltada à detecção automática, com **5 categorias**:

| Categoria original (Anzovino et al., 2018) | Definição resumida |
|---|---|
| **Discredit** | Insulto/difamação da mulher sem outra intenção maior. |
| **Stereotype & Objectification** | Imagem fixa e simplificada da mulher; descrição do corpo feminino ou comparação a padrões estreitos. |
| **Sexual Harassment & Threats of Violence** | Investidas sexuais não solicitadas; intenção de impor poder por meio de ameaças de violência. |
| **Dominance** | Afirmação da superioridade masculina e da desigualdade de gênero. |
| **Derailing** | Justificação do abuso, rejeição da responsabilidade masculina, desvio da conversa. |

Esta é a base das **classes 1–5** da nossa taxonomia. Em relação a Anzovino
et al., **desmembramos** "Sexual Harassment & Threats of Violence" em duas
classes separadas (3 e 4), por ter implicações lexicais bastante distintas no
material brasileiro.

### 2.3 Sultana, Sarker & Bosu (2021) — rubrica de anotação

Em *A Rubric to identify misogynistic and sexist texts in developer
communications*, os autores desenvolvem uma rubrica que operacionaliza as
categorias em **critérios verificáveis por anotadores humanos**. Eles tratam
**Objetificação Sexual** e **Culpabilização da Vítima** como classes
**separadas** — adotamos essa separação como base das **classes 6 e 7**.

### 2.4 Bailey (2010) — misogynoir

Moya Bailey cunhou o termo **misogynoir** para nomear a opressão específica,
na intersecção de **misoginia e racismo**, dirigida a **mulheres negras**.
Nenhum dos léxicos brasileiros de discurso de ódio analisados (HateBR, ToLD-BR,
MOL, OFFCOMBR) contempla essa intersecção. Por essa razão, Misogynoir aparece
na nossa taxonomia como **subclasse transversal T1**: pode coexistir com
qualquer classe principal quando o alvo é mulher negra.

### 2.5 Outras fontes

- **Glick & Fiske (1997)** — *Ambivalent Sexism Inventory*: sexismo hostil ×
  benevolente; reforça a Estereotipização.
- **Jane (2017)** e **Mantilla (2015)** — misoginia online e *gendertrolling*:
  base para Assédio Sexual e Ameaças de Violência no recorte digital.
- **Massanari (2017)** — culturas tóxicas em plataformas: base para
  Objetificação e Assédio.

---

## 3. As 7 classes principais

Para cada classe: **definição**, **características/manifestações**,
**significado** e **exemplos de palavras/expressões** (em forma legível —
lemas). Os exemplos são **ilustrativos**; a lista final de termos vem do
léxico construído a partir do corpus.

---

### Classe 1 — Descrédito

**Definição.** Termos associados à difamação ou desqualificação da mulher,
minando sua credibilidade, competência ou autoridade.

**Características.** Termos que questionam a capacidade intelectual,
infantilizam, patologizam (associam a desequilíbrio mental) ou minimizam as
conquistas femininas.

**Significado.** Retirar da mulher o direito de ser levada a sério —
especialmente em espaços de poder, debate e conhecimento.

**Exemplos.** *incompetente, burra, histérica, louca, mimimi, surtada,
despreparada, "não sabe do que fala"*.

**Referências.** Anzovino et al. (2018) — *Discredit*; Sultana et al. (2021).

---

### Classe 2 — Estereotipização

**Definição.** Termos que atribuem à mulher características, papéis e
comportamentos fixos com base em estereótipos de gênero.

**Características.** Reduções a papéis domésticos/tradicionais, estereótipos
físicos, generalizações sobre "como as mulheres são".

**Significado.** Aprisionar a identidade feminina num modelo pré-definido,
negando individualidade e legitimando expectativas restritivas.

**Exemplos.** *mulherzinha, "do lar", TPM, fofoqueira, "lugar de mulher",
"dirige mal", "mulher de verdade"*.

**Referências.** Glick & Fiske (1997); Anzovino et al. (2018) — *Stereotype*.

---

### Classe 3 — Assédio Sexual

**Definição.** Termos associados à sexualização não consentida da mulher em
espaços digitais.

**Características.** Comentários não solicitados sobre o corpo, propostas e
investidas sexuais, insultos de natureza sexual, uso pejorativo da
identidade/orientação sexual.

**Significado.** Impor poder sobre a mulher reduzindo sua presença pública a
um corpo disponível ao desejo masculino.

**Exemplos.** *"manda nudes", "senta aqui", piranha, vadia, safada, piriguete,
"tá pedindo"*.

**Referências.** Anzovino et al. (2018) — *Sexual Harassment*; Jane (2017);
Mantilla (2015).

---

### Classe 4 — Ameaças de Violência

**Definição.** Termos que intimidam a mulher por meio de ameaças de violência
física, sexual ou psicológica.

**Características.** Ameaças diretas, incitação à agressão, expressão do desejo
de que a mulher sofra dano.

**Significado.** Silenciar e afastar a mulher do espaço público pela produção
de medo.

**Exemplos.** *"vai apanhar", "merece morrer", estuprável, "calar na porrada",
"devia sumir"*.

**Referências.** Anzovino et al. (2018) — *Threats of Violence*; Jane (2017);
Mantilla (2015).

---

### Classe 5 — Dominação

**Definição.** Termos associados ao exercício de controle sobre a mulher e à
imposição da hierarquia patriarcal.

**Características.** Imperativos de silêncio e obediência, negação da agência
feminina, resistência à liderança e à autonomia da mulher.

**Significado.** Reafirmar a superioridade masculina e manter a mulher em
posição subordinada.

**Exemplos.** *"cala a boca", "volta pra cozinha", "obedece", "lugar de mulher
é em casa", "quem manda é o homem"*.

**Referências.** Manne (2017); Anzovino et al. (2018) — *Dominance*.

---

### Classe 6 — Culpabilização da Vítima

**Definição.** Termos que responsabilizam a própria mulher pelas agressões e
problemas que sofre.

**Características.** "Ela provocou", questionamento de roupas e comportamento,
inversão da lógica de responsabilidade, minimização da agressão sofrida.

**Significado.** Transferir a culpa do agressor para a vítima, legitimando a
violência.

**Exemplos.** *"ela provocou", "de saia curta", "tava bêbada", "pediu",
"foi atrás"*.

**Referências.** Sultana et al. (2021); Manne (2017).

---

### Classe 7 — Objetificação Sexual

**Definição.** Termos que reduzem a mulher a objeto sexual ou a partes do corpo.

**Características.** Desumanização por hipersexualização, classificação e
"avaliação" física, linguagem de mercadoria.

**Significado.** Negar à mulher o estatuto de sujeito, tratando-a como coisa
de consumo.

**Exemplos.** *"pedaço de carne", rabuda, peituda, "só serve pra isso",
"boa de cama"*.

**Referências.** Sultana et al. (2021); Anzovino et al. (2018) —
*Objectification*; Massanari (2017).

---

## 4. Subclasses transversais

As duas subclasses abaixo **não são obrigatórias** e **podem coexistir com
qualquer classe principal**. Servem para sinalizar dimensões interseccionais
ou contextuais que o léxico precisa registrar, mas que não constituem classes
lexicais autônomas.

### T1 — Misogynoir

**Quando aplica.** Quando o termo ou expressão remete à opressão na
intersecção de misoginia e racismo, dirigida especificamente a mulheres
negras (Bailey, 2010).

**Uso.** Marcar como transversal `T1` em adição à classe principal
correspondente (ex.: um insulto sexualizado direcionado a mulher negra recebe
`classe principal = 3 (Assédio Sexual)` + `transversal = T1`).

**Lacuna crítica.** Nenhum léxico brasileiro de discurso de ódio contempla a
intersecção — registrar `T1` é a única forma de torná-la visível neste
recurso.

**Referências.** Bailey (2010); Silva (2022) — *Racismo Algorítmico*.

### T2 — Violência Política Digital

**Quando aplica.** Quando o ataque é dirigido a uma mulher em **papel
político** (candidata, parlamentar, militante), com base em gênero.

**Uso.** Marcar como transversal `T2` em adição à classe principal
correspondente (ex.: "incompetente porque é mulher" dirigido a parlamentar
recebe `classe principal = 1 (Descrédito)` + `transversal = T2`).

**Lacuna crítica.** Ausente em todos os léxicos brasileiros analisados;
especialmente relevante no contexto eleitoral brasileiro recente.

**Referências.** Mantilla (2015); Jane (2017); SciELO Brasil (2023) — estudo
#ELEITAS.

---

## 5. Classes da versão anterior que foram removidas

A versão anterior do documento (11 classes) continha duas classes adicionais
que **foram removidas** nesta revisão. As razões são metodológicas:

### Derailing (removida)

Em Anzovino et al. (2018), *Derailing* designa a estratégia discursiva de
desviar, invalidar ou minimizar questões legítimas levantadas por mulheres
(ex.: "e os homens?", *whataboutism*, acusações de vitimismo).

**Por que removemos.** Derailing é **estruturalmente conversacional**: depende
fortemente do contexto de turno-de-fala, do interlocutor e do tópico. Tentar
capturá-lo por **léxico isolado** produziria falsos positivos altíssimos
(qualquer "e os homens?" fora de contexto não é misoginia). É um fenômeno
real, mas não é uma classe **lexical** estável — pertence a análises
pragmáticas/discursivas, não a léxicos de unigramas/bigramas.

### Neossexismo (removida)

A versão anterior trazia Neossexismo (negação da discriminação de gênero,
ataque ao feminismo) como classe 9, com base em Manne (2020) e Banet-Weiser &
Miltner (2016).

**Por que removemos.** Neossexismo é mais um **modo discursivo transversal**
(uma postura ideológica que pode atravessar várias classes) do que uma classe
lexical distinta. Os termos típicos (*feminazi*, *"já tem igualdade"*,
*"feminismo é mimizento"*) normalmente atuam como **Descrédito** (classe 1)
ou **Dominação** (classe 5) e, quando relevante o aspecto político, podem
receber a transversal **T2 (Violência Política Digital)**.

---

## 6. Tabela-resumo

| ID | Classe / Subclasse | Tipo | Origem |
|----|--------------------|------|--------|
| 1 | Descrédito | Principal | Anzovino et al. (2018) |
| 2 | Estereotipização | Principal | Anzovino et al.; Glick & Fiske |
| 3 | Assédio Sexual | Principal | Anzovino et al. (2018) |
| 4 | Ameaças de Violência | Principal | Anzovino et al. (2018) |
| 5 | Dominação | Principal | Manne; Anzovino et al. |
| 6 | Culpabilização da Vítima | Principal | Sultana et al. (2021); Manne |
| 7 | Objetificação Sexual | Principal | Sultana et al. (2021); Anzovino et al. |
| T1 | Misogynoir | Transversal (opcional) | Bailey (2010) |
| T2 | Violência Política Digital | Transversal (opcional) | Contribuição do projeto |

Cinco das sete classes principais derivam diretamente de Anzovino et al. (2018);
duas (6 e 7) seguem a separação proposta por Sultana et al. (2021). As duas
subclasses transversais (T1 e T2) capturam dimensões interseccionais que os
léxicos brasileiros existentes não registram.

---

## 7. Pontos abertos para discussão com o grupo

Itens que o grupo de pesquisa ainda precisa avaliar:

1. **Sobreposição entre classes principais.** Estereotipização (2) ×
   Objetificação (7), e Descrédito (1) × Dominação (5), têm fronteiras
   difusas. Definir regra de desempate para a anotação (ex.: prioridade pela
   classe de menor ID, ou permitir rótulo múltiplo principal?).

2. **Granularidade.** Anzovino et al. usam 5 categorias; nós usamos 7
   principais + 2 transversais. A redução em relação à versão anterior
   (11 classes) já contempla a recomendação de "reduzir o número de classes
   em NLP".

3. **Termos-âncora por classe.** A anotação automática precisará de listas de
   palavras-âncora por classe. O grupo deve revisar/aprovar essas listas a
   partir dos exemplos da seção 3.

4. **Dependência contextual.** Cada termo do léxico recebe, na planilha de
   votação, um **grau de dependência contextual** (`baixo`, `médio`, `alto`)
   e um **exemplo de uso** real do corpus. O grupo precisa validar a
   heurística de pré-preenchimento.

---

## Referências

ANZOVINO, M.; FERSINI, E.; ROSSO, P. Automatic identification and
classification of misogynistic language on Twitter. In: *Proc. 24th CoNLL*,
2018.

BAILEY, M. Misogynoir in Medical Media. *Catalyst*, 2010.

BANET-WEISER, S.; MILTNER, K. M. #MasculinitySoFragile: Culture, structure,
and networked misogyny. *Feminist Media Studies*, v. 16, n. 1, p. 171–174,
2016.

GLICK, P.; FISKE, S. T. The Ambivalent Sexism Inventory. *JPSP*, v. 70,
n. 3, 1997.

JANE, E. A. *Misogyny Online: A Short (and Brutish) History*. SAGE, 2017.

MANNE, K. *Down Girl: The Logic of Misogyny*. Oxford University Press, 2017.

MANNE, K. *Entitled: How Male Privilege Hurts Women*. Crown Publishing, 2020.

MANTILLA, K. *Gendertrolling: How Misogyny Went Viral*. Praeger, 2015.

MASSANARI, A. #Gamergate and The Fappening. *New Media & Society*, v. 19,
n. 3, 2017.

SILVA, T. *Racismo Algorítmico*. Edições Sesc, 2022.

SULTANA, S.; SARKER, J.; BOSU, A. A Rubric to identify misogynistic and
sexist texts in developer communications. 2021.
