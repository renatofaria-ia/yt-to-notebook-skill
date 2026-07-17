---
name: notebooklm-to-notes
description: Extraia conhecimento de notebooks do NotebookLM e entregue bundles Open Knowledge Format (OKF) 0.1 visuais. Use para transformar, exportar ou persistir notebooks no Obsidian, Markdown ou Notion, inclusive ao montar um deck progressivo de segundo cérebro com resumos de notebook, resumos opcionais de fontes e cross-links didáticos.
---

# notebooklm-to-notes

Gere conhecimento em PT-BR claro, visual e rastreável. O **bundle OKF 0.1 local**  é sempre a fonte de verdade; TL;DR, callouts, tabelas, Mermaid, emojis, mapa mental e cola rápida são a camada editorial.

## Referências obrigatórias

Leia `references/formato-okf.md`, `references/formato-visual.md`, `references/deck-progressivo.md` e `references/exemplo-deck-okf.md` antes de escrever.

## Fluxo de extração

1. Confirme a sessão: `notebooklm auth check --test --json`.
2. Liste notebooks e fontes; use o ID completo. Registre título, ID, URL conhecida e status de cada fonte.
3. Peça ao NotebookLM um **pacote estruturado de conteúdo**, seguindo `references/deck-progressivo.md`. Não peça YAML, caminhos, Mermaid nem OKF pronto: a skill aplica persistência e apresentação.
4. Crie a síntese visual, os índices, o log, o YAML e as citações. Preserve limites e fontes com erro; não invente conteúdo, URLs ou identificadores.
5. Depois da síntese, pergunte se o usuário quer resumos das fontes. Só então consulte cada fonte pronta, crie `sources/` e atualize índices, síntese e log.

## Escolher o destino

- **Bundle independente (padrão):** se o usuário indicar uma pasta ou arquivo `.md`, crie um bundle irmão com `index.md`, `log.md`, `sintese.md` e `sources/`.
- **Deck progressivo:** quando o usuário mencionar *deck*, *segundo cérebro* ou indicar uma raiz de conhecimento, crie ou reutilize a raiz abaixo. Não mova bundles históricos sem pedido explícito.

```text
<deck>/
  index.md
  log.md
  notebooks/
    index.md
    <notebook-slug>/
      index.md
      <notebook-slug>.md
      sources/                 # somente após confirmação do usuário
        index.md
        <fonte-slug>.md
```

`<notebook-slug>.md`  é o conceito principal. Não use um arquivo como diretório.

## Conceitos, links e proveniência

Todo `.md` exceto `index.md` e `log.md` tem YAML UTF-8 sem BOM e `type` não vazio.

```yaml
---
type: NotebookLM Summary
title: <título humano>
description: <uma frase>
tags: [notebooklm, <tema>]
timestamp: <ISO 8601>
notebook_id: <id conhecido>
origin: notebooklm
source_ready_count: <número>
source_error_count: <número>
---
```

- Fontes usam `type: NotebookLM Source`, `source_id`, `source_status` e `resource` somente quando a URL  é conhecida.
- Sínteses e fontes terminam em `# Citations`. A síntese cita conceitos em `/notebooks/<slug>/sources/` quando existirem.
- Coloque entre aspas valores YAML com `:`, `#`, `{}` ou `[]`.
- Use links Markdown absolutos relativos  à raiz. Nunca use `file://`, caminhos de disco ou wikilinks.

## Cross-links didáticos

Crie no máximo três links em `## Conhecimento relacionado` de cada síntese. Um link só é válido se o NotebookLM explicitou a relação ou se os dois conceitos compartilham ao menos duas tags normalizadas. Escreva a explicação junto do link. Fontes ligam somente ao conceito principal. Não crie banco de grafo, arquivos de arestas ou hubs de tags.

## Camada visual e validação

A síntese segue, quando aplicável: H1, TL;DR, proveniência, ideia central, desenvolvimento, aplicação, mapa, cola rápida e citações. O conteúdo essencial deve permanecer legível em Markdown puro.

- Nunca use entidades HTML em Mermaid; em `mindmap`, use rótulos simples, sem aspas.
- Escreva em PT-BR natural e acentuado; identificadores, URLs, tags e código podem permanecer em ASCII.
- Valide bundle: `python scripts/validar_nota.py --bundle <bundle> --pt-br`.
- Valide deck: `python scripts/validar_nota.py --deck <deck> --pt-br`.

Para Notion, gere primeiro o bundle local e publique apenas um espelho visual se houver conector.

## Compatibilidade

`python scripts/validar_nota.py --profile portable <arquivo>` permanece apenas para artefatos legados.
