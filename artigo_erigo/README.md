# Artigo ERIGO — Léxico de Misoginia em PT-BR (preliminar)

> **Estado:** rascunho preliminar conforme orientações da Profa. Deborah
> (`orientacoes_formais_aluno_erigo.pdf`) e do esqueleto textual
> (`esqueleto_textual_artigo_erigo.pdf`).
>
> **Versão técnica relatada:** apenas o pipeline V3 (lematização spaCy +
> Monteles TF-IDF + PMI). V1 e V2 (com stems RSLP) **não** aparecem neste
> manuscrito.

## Arquivos

- `artigo_erigo.tex` — corpo do artigo (5 seções: Introdução, Trabalhos
  Relacionados, Metodologia, Resultados Preliminares, Conclusão).
- `referencias.bib` — bibliografia em formato BibTeX.
- `sbc-template.sty`, `sbc.bst`, `caption2.sty` — template oficial da SBC
  (Sociedade Brasileira de Computação), versão 2016.
- `figs/`, `tabelas/` — diretórios para figuras e tabelas (atualmente
  vazios; o artigo usa apenas tabelas em LaTeX, sem imagens).

## Como compilar

Pré-requisitos: distribuição TeX Live ou MiKTeX completa, com `pdflatex` e
`bibtex` disponíveis no PATH.

```bash
cd artigo_erigo
pdflatex artigo_erigo
bibtex artigo_erigo
pdflatex artigo_erigo
pdflatex artigo_erigo
```

A compilação tripla é necessária para resolver referências cruzadas e
bibliografia.

### Compilando no Overleaf (alternativa sem instalar TeX local)

1. Acesse [https://www.overleaf.com](https://www.overleaf.com) e crie um
   projeto em branco.
2. Faça upload de todos os arquivos deste diretório (incluindo
   `sbc-template.sty`, `sbc.bst`, `caption2.sty`, `referencias.bib` e
   `artigo_erigo.tex`).
3. Defina `artigo_erigo.tex` como o arquivo principal.
4. Compile (`Recompile`).

## Checklist antes de submeter

- [ ] Verificar que o PDF cabe no **limite de páginas do ERIGO** (consultar
      edital; tipicamente 6 a 8 páginas para artigo curto).
- [ ] Confirmar que a definição operacional de misoginia aparece **antes**
      da descrição dos dados (já está: Seção 1, parágrafo 3).
- [ ] Confirmar que há **apenas uma linha experimental** (V3) — não citar
      V1/V2.
- [ ] Confirmar que há **apenas uma tabela principal de resultados**
      (Tabela 3 — `tab:resultados`).
- [ ] Verificar termos: o documento deve usar **"textos com traços de
      misoginia"**, nunca "textos misóginos" categoricamente. Buscar por
      "termos misóginos" — deve retornar 0 ocorrências.
- [ ] Revisar a lista de autores e e-mails no preâmbulo (`\author`,
      `\address`).
- [ ] Atualizar números na Tabela 1 (`tab:corpora`) para o total exato
      dos corpora utilizados (atualmente `46.338` para "demais fontes
      agregadas" é o saldo de `74.338 - 7.000 - 21.000` — verificar
      composição real antes de submeter).

## Decisões editoriais (das orientações da Profa.)

1. **Estudo preliminar** — escopo enxuto, sem prometer entregas futuras.
2. **Pipeline único** — apenas V3, sem reabrir a história de V1/V2.
3. **Tabela única de resultados** — só o teste *out-of-sample*; resultados
   de cross-validation no corpus de treino (que tinha ruído político) ficam
   fora do artigo.
4. **Taxonomia (7 + 2)** — apenas como enquadramento conceitual, não como
   eixo central da contribuição.
5. **Terminologia cautelosa** — "termos que podem estar associados a textos
   com traços de misoginia"; palavras isoladas têm apenas o significado de
   dicionário.
