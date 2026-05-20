# Taxonomia da Misoginia Digital em Português Brasileiro

> Documento de trabalho — Iniciação Científica PIBIC 2025/2026
> Projeto PI06069-2022 · UFG / Instituto de Informática
> Pesquisador: Hugo Guilherme de Assis Paula · Orientadora: Deborah Silva Alves Fernandes
>
> **Status:** versão para discussão com o grupo de pesquisa.

---

## 1. Introdução e escopo

Este documento apresenta a taxonomia de **misoginia digital** adotada no projeto: um
conjunto de **11 classes** que categorizam, por *tipo de violência*, as manifestações
misóginas dirigidas a mulheres em ambientes digitais.

### 1.1 Recorte do objeto

A taxonomia trata da misoginia **expressa pela linguagem em meios digitais** — comentários,
postagens, tweets, mensagens. O recorte é deliberadamente **verbal/discursivo e digital**:

- **Inclui:** ofensas, estereótipos, sexualização não consentida, ameaças verbais,
  silenciamento, desqualificação, neossexismo e ataques interseccionais expressos em texto.
- **Exclui:** a violência **física** propriamente dita (agressão, feminicídio), bem como
  crimes digitais que não se realizam primariamente pela linguagem (ex.: vazamento de
  imagens íntimas, *stalking* técnico). Esses fenômenos são relevantes para o tema, mas
  estão fora do escopo de um **léxico de termos**, que opera sobre palavras e expressões.

Essa delimitação é metodologicamente necessária: o produto final do projeto é um léxico
aplicável a modelos de aprendizado de máquina, e um léxico só captura o que se manifesta
**no texto**.

### 1.2 Distinção conceitual: sexismo × misoginia

A taxonomia parte da distinção formulada por **Manne (2017)**:

- **Sexismo** — a dimensão **ideológica/justificativa** do patriarcado: o conjunto de
  crenças que naturaliza e racionaliza a hierarquia de gênero.
- **Misoginia** — a dimensão **punitiva/coercitiva**: o "braço de aplicação da lei" do
  patriarcado, que **pune e controla** as mulheres que transgridem as normas de gênero e
  **recompensa** as que se conformam.

As 11 classes descrevem, portanto, **mecanismos de punição e controle** — não apenas
crenças. Uma mesma palavra pode ser sexista ou misógina conforme o uso; a taxonomia
classifica o **ato discursivo** de hostilidade.

---

## 2. Fundamentação: as classificações dos especialistas

A taxonomia **não é original em sua maior parte** — ela sintetiza e adapta classificações
já consolidadas por especialistas em misoginia. Esta seção apresenta cada fonte e o que
ela contribui, atendendo à exigência de "verificar as classificações feitas por
especialistas e citá-los".

### 2.1 Manne (2017, 2020) — arcabouço conceitual

Kate Manne, em *Down Girl: The Logic of Misogyny* (2017) e *Entitled* (2020), não propõe
uma lista de categorias operacionais, mas fornece o **arcabouço teórico**: misoginia como
sistema que **policia** o comportamento feminino. Desse arcabouço derivam classes ligadas a
**controle** (Dominação), **punição** (Ameaças, Descrédito) e a lógica de
**culpabilização** da mulher que "saiu da linha" (Culpabilização da Vítima).

### 2.2 Anzovino, Fersini & Rosso (2018) — taxonomia para classificação automática

No artigo *Automatic identification and classification of misogynistic language on
Twitter* (CoNLL 2018), os autores propõem a **primeira taxonomia operacional** de misoginia
para detecção automática, com **5 categorias**:

| Categoria original (Anzovino et al., 2018) | Definição resumida |
|---|---|
| **Discredit** | Insulto/difamação da mulher sem outra intenção maior. |
| **Stereotype & Objectification** | Imagem fixa e simplificada da mulher; descrição do corpo feminino ou comparação a padrões estreitos. |
| **Sexual Harassment & Threats of Violence** | Investidas sexuais não solicitadas; intenção de impor poder por meio de ameaças de violência. |
| **Dominance** | Afirmação da superioridade masculina e da desigualdade de gênero. |
| **Derailing** | Justificação do abuso, rejeição da responsabilidade masculina, desvio da conversa. |

Esta é a base direta das classes 1–6 e 8 da nossa taxonomia. Note-se que Anzovino et al.
**agrupam** estereótipo e objetificação numa só categoria, e **agrupam** assédio sexual e
ameaças — nossa taxonomia os **desmembra** (ver seção 4).

### 2.3 Sultana, Sarker & Bosu (2021) — rubrica de anotação

Em *A Rubric to identify misogynistic and sexist texts in developer communications*, os
autores desenvolvem uma **rubrica de anotação** para identificar misoginia e sexismo em
comunicações profissionais de desenvolvedores de software. A contribuição relevante para
nós é metodológica: a rubrica operacionaliza as categorias em **critérios verificáveis por
anotadores humanos**, e reforça classes de hostilidade **implícita** (Descrédito,
Culpabilização da Vítima, Neossexismo) que vão além do insulto explícito.

### 2.4 Bailey (2010) — misogynoir

Moya Bailey cunhou o termo **misogynoir** para nomear a opressão específica, na intersecção
de **misoginia e racismo**, dirigida a **mulheres negras**. Nenhum dos léxicos brasileiros
de discurso de ódio analisados (HateBR, ToLD-BR, MOL, OFFCOMBR) contempla essa intersecção
— daí a classe 10 ser uma **contribuição original** deste projeto para o contexto
brasileiro.

### 2.5 Outras fontes

- **Glick & Fiske (1997)** — *Ambivalent Sexism Inventory*: sexismo hostil × benevolente,
  base para a classe Estereotipização.
- **Jane (2017)** e **Mantilla (2015)** — misoginia online e *gendertrolling*: base para
  Assédio Sexual e Ameaças de Violência no recorte digital.
- **Massanari (2017)** — culturas tóxicas em plataformas (#Gamergate): base para
  Objetificação e Assédio.
- **Banet-Weiser & Miltner (2016)** e **Manne (2020)** — *backlash* antifeminista em rede:
  base para Neossexismo.

---

## 3. As 11 classes da taxonomia

Para cada classe: **definição**, **características/manifestações**, **significado** (o que o
ato busca produzir) e **exemplos de palavras/expressões** (em forma legível — lemas). Os
exemplos são **ilustrativos**; a lista final de termos virá do léxico construído a partir
do corpus (Tarefas 2–3).

---

### Classe 1 — Descrédito

**Definição.** Difamação ou desqualificação da mulher, minando sua credibilidade,
competência ou autoridade, sem uma intenção ofensiva mais específica.

**Características.** Termos que questionam a capacidade intelectual, infantilizam,
patologizam (associam a desequilíbrio mental) ou minimizam as conquistas femininas.

**Significado.** Retirar da mulher o direito de ser levada a sério — especialmente em
espaços de poder, debate e conhecimento.

**Exemplos.** *incompetente, burra, histérica, louca, mimimi, surtada, despreparada,
"não sabe do que fala"*.

**Referências.** Anzovino et al. (2018) — *Discredit*; Sultana et al. (2021).

---

### Classe 2 — Estereotipização

**Definição.** Atribuição à mulher de características, papéis e comportamentos fixos com
base em estereótipos de gênero.

**Características.** Reduções a papéis domésticos/tradicionais, estereótipos físicos,
generalizações sobre "como as mulheres são".

**Significado.** Aprisionar a identidade feminina num modelo pré-definido, negando
individualidade e legitimando expectativas restritivas.

**Exemplos.** *mulherzinha, "do lar", TPM, fofoqueira, "lugar de mulher", "dirige mal",
"mulher de verdade"*.

**Referências.** Glick & Fiske (1997); Anzovino et al. (2018) — *Stereotype*.

---

### Classe 3 — Assédio Sexual

**Definição.** Sexualização não consentida da mulher em espaços digitais.

**Características.** Comentários não solicitados sobre o corpo, propostas e investidas
sexuais, insultos de natureza sexual, uso pejorativo da identidade/orientação sexual.

**Significado.** Impor poder sobre a mulher reduzindo sua presença pública a um corpo
disponível ao desejo masculino.

**Exemplos.** *"manda nudes", "senta aqui", piranha, vadia, safada, piriguete, "tá pedindo"*.

**Referências.** Anzovino et al. (2018) — *Sexual Harassment*; Jane (2017); Mantilla (2015).

---

### Classe 4 — Ameaças de Violência

**Definição.** Intimidação da mulher por meio de ameaças de violência física, sexual ou
psicológica.

**Características.** Ameaças diretas, incitação à agressão, expressão do desejo de que a
mulher sofra dano.

**Significado.** Silenciar e afastar a mulher do espaço público pela produção de medo.

**Exemplos.** *"vai apanhar", "merece morrer", estuprável, "calar na porrada", "devia
sumir"*.

**Referências.** Anzovino et al. (2018) — *Threats of Violence*; Jane (2017); Mantilla (2015).

---

### Classe 5 — Dominação

**Definição.** Exercício de controle sobre a mulher e imposição da hierarquia patriarcal.

**Características.** Imperativos de silêncio e obediência, negação da agência feminina,
resistência à liderança e à autonomia da mulher.

**Significado.** Reafirmar a superioridade masculina e manter a mulher em posição
subordinada.

**Exemplos.** *"cala a boca", "volta pra cozinha", "obedece", "lugar de mulher é em casa",
"quem manda é o homem"*.

**Referências.** Manne (2017); Anzovino et al. (2018) — *Dominance*.

---

### Classe 6 — Derailing (Desvio de Conversa)

**Definição.** Estratégia discursiva que desvia, invalida ou minimiza questões legítimas
levantadas por mulheres.

**Características.** "E os homens?", *whataboutism*, acusações de vitimismo, negação da
responsabilidade masculina, mudança de foco do debate.

**Significado.** Impedir que a denúncia ou o argumento da mulher avance, esvaziando-o.

**Exemplos.** *"e os homens?", "nem todo homem", "tá de mimimi", "vitimismo", "exagero"*.

**Atenção.** Classe **estruturalmente difícil** de capturar por léxico isolado — depende
fortemente do contexto conversacional. Ver seção 5.

**Referências.** Anzovino et al. (2018) — *Derailing*; Manne (2017).

---

### Classe 7 — Culpabilização da Vítima

**Definição.** Responsabilização da própria mulher pelas agressões e problemas que sofre.

**Características.** "Ela provocou", questionamento de roupas e comportamento, inversão da
lógica de responsabilidade, minimização da agressão sofrida.

**Significado.** Transferir a culpa do agressor para a vítima, legitimando a violência.

**Exemplos.** *"ela provocou", "de saia curta", "tava bêbada", "pediu", "foi atrás"*.

**Referências.** Sultana et al. (2021); Manne (2017).

---

### Classe 8 — Objetificação Sexual

**Definição.** Redução da mulher a objeto sexual ou a partes do corpo.

**Características.** Desumanização por hipersexualização, classificação e "avaliação"
física, linguagem de mercadoria.

**Significado.** Negar à mulher o estatuto de sujeito, tratando-a como coisa de consumo.

**Exemplos.** *"pedaço de carne", rabuda, peituda, "só serve pra isso", "boa de cama"*.

**Referências.** Anzovino et al. (2018) — *Objectification*; Massanari (2017).

---

### Classe 9 — Neossexismo

**Definição.** Forma moderna e sutil de sexismo que **nega a existência** da discriminação
de gênero.

**Características.** Discurso de "igualdade já alcançada", ataque ao feminismo, apelo à
"meritocracia", negação de privilégios masculinos.

**Significado.** Deslegitimar a luta por direitos das mulheres apresentando-a como
desnecessária ou oportunista.

**Exemplos.** *feminazi, "já tem igualdade", "feminismo é mimizento", "vitimismo
feminista", "querem privilégio"*.

**Referências.** Manne (2020); Banet-Weiser & Miltner (2016).

---

### Classe 10 — Misogynoir ⚠️ contribuição original

**Definição.** Opressão na **intersecção de misoginia e racismo**, dirigida
especificamente a **mulheres negras**.

**Características.** Hipersexualização racializada, estereótipos específicos (ex.:
agressividade, "mulher-objeto"), insultos que cruzam gênero e raça.

**Significado.** Submeter a mulher negra a uma dupla opressão que nem o léxico de misoginia
nem o de racismo, isoladamente, capturam.

**Exemplos.** insultos raciais dirigidos a mulheres negras combinados a sexualização ou
desqualificação; estereótipos sobre cabelo e corpo.

**Lacuna crítica.** Nenhum léxico brasileiro de discurso de ódio contempla a intersecção.

**Referências.** Bailey (2010); Silva (2022) — *Racismo Algorítmico*.

---

### Classe 11 — Violência Política Digital ⚠️ contribuição original

**Definição.** Ataques sistemáticos, baseados em gênero, contra mulheres em posições de
liderança ou disputa política.

**Características.** Deslegitimação da mulher política **por ser mulher**, ataques
coordenados em períodos eleitorais, *doxxing* de candidatas e parlamentares.

**Significado.** Afastar mulheres da participação política e do exercício do poder.

**Exemplos.** desqualificação de candidatas/parlamentares com apelo ao gênero;
"incompetente porque é mulher"; "o cargo ficaria melhor com um homem".

**Lacuna crítica.** Ausente em todos os léxicos brasileiros analisados; especialmente
relevante no contexto das eleições de 2018, 2020, 2022 e 2024.

**Referências.** Mantilla (2015); Jane (2017); SciELO Brasil (2023) — estudo #ELEITAS.

---

## 4. Tabela-resumo

| ID | Classe | Foco do ato | Origem |
|----|--------|-------------|--------|
| 1 | Descrédito | Minar credibilidade/competência | Anzovino et al. (2018) |
| 2 | Estereotipização | Aprisionar em papéis fixos | Anzovino et al.; Glick & Fiske |
| 3 | Assédio Sexual | Sexualização não consentida | Anzovino et al. (2018) |
| 4 | Ameaças de Violência | Intimidar por medo | Anzovino et al. (2018) |
| 5 | Dominação | Controlar e subordinar | Manne; Anzovino et al. |
| 6 | Derailing | Desviar/invalidar a fala da mulher | Anzovino et al. (2018) |
| 7 | Culpabilização da Vítima | Inverter a culpa | Sultana et al.; Manne |
| 8 | Objetificação Sexual | Reduzir a objeto/corpo | Anzovino et al.; Massanari |
| 9 | Neossexismo | Negar a discriminação | Manne (2020); Banet-Weiser & Miltner |
| 10 | Misogynoir | Opressão raça + gênero | Bailey (2010) — **original no projeto** |
| 11 | Violência Política Digital | Afastar mulheres do poder | **original no projeto** |

Classes 1–9: adaptadas das taxonomias de Anzovino et al. (2018) e Sultana et al. (2021).
Em relação a Anzovino et al., **desmembramos** "Stereotype & Objectification" em duas
classes (2 e 8) e "Sexual Harassment & Threats of Violence" em duas (3 e 4), e
**acrescentamos** Culpabilização da Vítima (7) e Neossexismo (9). Classes 10 e 11 são
contribuições originais para o contexto brasileiro.

---

## 5. Pontos abertos para discussão com o grupo

Itens que o grupo de pesquisa precisa avaliar e decidir:

1. **Derailing (classe 6) e léxico de termos.** Derailing é fortemente dependente do
   contexto conversacional e pode não ser bem capturado por palavras isoladas. Manter como
   classe (consistência com Anzovino et al.) ou marcar como "não cobrível por léxico"?

2. **Sobreposição entre classes.** Estereotipização (2) × Objetificação (8) e Descrédito
   (1) × Neossexismo (9) têm fronteiras difusas. Definir regra de desempate para a anotação
   (ex.: prioridade por classe de menor ID, ou rótulo múltiplo permitido?).

3. **Classes 10 e 11 — originais.** Misogynoir e Violência Política Digital precisam de
   validação da orientadora e de fundamentação adicional, por não derivarem diretamente das
   taxonomias-fonte. Há risco de **baixa frequência** de termos exclusivos no corpus.

4. **Granularidade.** Anzovino et al. usam 5 categorias; nós usamos 11. Mais granularidade
   melhora a riqueza semântica, mas fragmenta os dados e dificulta a concordância entre
   anotadores. O grupo concorda com as 11?

5. **Rótulo único × múltiplo.** Um termo/frase pode pertencer a mais de uma classe. Decidir
   se a anotação (Tarefa 3) será de rótulo único (maioria) ou permitirá múltiplos rótulos.

6. **Termos-âncora por classe.** A anotação automática (Tarefa 3) precisará de listas de
   palavras-âncora por classe. O grupo deve revisar/aprovar essas listas a partir dos
   exemplos da seção 3.

---

## Referências

ANZOVINO, M.; FERSINI, E.; ROSSO, P. Automatic identification and classification of
misogynistic language on Twitter. In: *Proc. 24th CoNLL*, 2018.

BAILEY, M. Misogynoir in Medical Media. *Catalyst*, 2010.

BANET-WEISER, S.; MILTNER, K. M. #MasculinitySoFragile: Culture, structure, and networked
misogyny. *Feminist Media Studies*, v. 16, n. 1, p. 171–174, 2016.

GLICK, P.; FISKE, S. T. The Ambivalent Sexism Inventory. *JPSP*, v. 70, n. 3, 1997.

JANE, E. A. *Misogyny Online: A Short (and Brutish) History*. SAGE, 2017.

MANNE, K. *Down Girl: The Logic of Misogyny*. Oxford University Press, 2017.

MANNE, K. *Entitled: How Male Privilege Hurts Women*. Crown Publishing, 2020.

MANTILLA, K. *Gendertrolling: How Misogyny Went Viral*. Praeger, 2015.

MASSANARI, A. #Gamergate and The Fappening. *New Media & Society*, v. 19, n. 3, 2017.

SILVA, T. *Racismo Algorítmico*. Edições Sesc, 2022.

SULTANA, S.; SARKER, J.; BOSU, A. A Rubric to identify misogynistic and sexist texts in
developer communications. 2021.
