---
name: notebooklm-to-notes
description: Converte notebooks do NotebookLM em vaults Obsidian minimalistas com briefing editorial em pt-BR, mapa mental Mermaid, proveniência das fontes e validação automática. Use quando for preciso extrair, resumir ou publicar um notebook em Markdown estruturado para um segundo cérebro.
---

# notebooklm-to-notes

Gere um briefing editorial em pt-BR e um mapa mental Mermaid para cada notebook. Preserve a proveniência no frontmatter e publique somente após validar o staging.

## Estrutura de saída

```text
<deck>/
  .obsidian/graph.json
  neurons/
  notebooks/<slug>/
    <slug>.md
    index.md
    log.md
```

Não crie `evidence/`, conceitos individuais de fonte, `index.md` ou `log.md` na raiz.

## Fluxo

1. Confirme a sessão com `python -m notebooklm auth check --test --json`.
2. Execute `python scripts/extrair_notebook.py --notebook <UUID> --deck <vault> --publish`.
3. O extrator inventaria as fontes, gera briefing e mapa mental, baixa os artefatos, monta o staging, valida e publica apenas o notebook aprovado.

## Contrato

- Escreva em UTF-8 sem BOM e rejeite mojibake.
- Preserve `briefing_artifact_id`, `mind_map_note_id`, descrição, 4-8 tags hierárquicas, domínios, neurônios, resumos relacionados e `source_links`.
- Registre título, URL absoluta quando disponível, tipo e ID do NotebookLM em cada `source_links`.
- Mantenha uma única seção `## Mapa mental` entre `## 1. Sumário Executivo` e `## 2.`.
- Inclua `## Fontes originais` e valide com `python scripts/validar_nota.py --deck <vault> --pt-br`.

Leia `references/contrato-fidelidade.md` para o contrato completo e `references/formato-visual.md` antes de ajustar a apresentação editorial.