# Exemplo de deck OKF progressivo

```text
segundo-cerebro/
  index.md
  log.md
  notebooks/
    index.md
    pesquisa-ia/
      index.md
      pesquisa-ia.md
      sources/
        index.md
        artigo-principal.md
```

## Conceito do notebook

```yaml
---
type: NotebookLM Summary
title: Pesquisa de IA
description: Síntese progressiva de um notebook sobre IA.
tags: [ia, pesquisa, notebooklm]
timestamp: 2026-07-17T12:00:00-03:00
notebook_id: notebook-conhecido
origin: notebooklm
source_ready_count: 1
source_error_count: 0
---
```

O corpo termina com `# Citations` e usa links como `/notebooks/pesquisa-ia/sources/artigo-principal.md`. `sources/` só  é criado após o usuário pedir resumos por fonte.
