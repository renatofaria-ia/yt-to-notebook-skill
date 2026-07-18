# Contrato de fidelidade

A fidelidade do `notebooklm-to-notes` é editorial e verificável no próprio vault. A extração preserva a identidade das fontes e os IDs dos artefatos que originaram o briefing e o mapa mental, sem armazenar respostas brutas ou diretórios de evidência.

## Saída obrigatória

```text
<deck>/
  .obsidian/graph.json
  neurons/
  notebooks/<slug>/
    <slug>.md
    index.md
    log.md
```

O resumo principal exige frontmatter com `notebook_id`, `briefing_artifact_id`, `mind_map_note_id`, `source_count` e `source_links`.

Cada item de `source_links` inclui `title`, `type`, `notebooklm_source_id` e `url` quando a origem fornecer uma URL HTTP(S). O corpo do resumo repete as fontes em `## Fontes originais`.

## Integridade editorial

- O briefing começa com `## 1. Sumário Executivo` e continua com seções H2 numeradas.
- O Mermaid aparece em uma única seção `## Mapa mental`, entre a seção 1 e a seção 2.
- O resumo contém descrição semântica de 180 a 320 caracteres e de 4 a 8 tags hierárquicas.
- Links em `neuron_links` e `related_summaries` apontam para arquivos existentes no mesmo vault.
- Todos os textos Markdown e JSON usam UTF-8 sem BOM e sem mojibake.

## Publicação

O extrator monta o conteúdo em staging, executa o validador e só então copia a pasta do notebook para o vault final. O staging inválido nunca é publicado.