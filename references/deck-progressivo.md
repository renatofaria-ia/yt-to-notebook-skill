# Deck progressivo: extração e organização

## Estrutura canônica

```text
<deck>/
  index.md
  log.md
  notebooks/
    index.md
    <notebook-slug>/
      index.md
      <notebook-slug>.md
      sources/
        index.md
        <source-slug>.md
```

A raiz é o bundle OKF. `notebooks/` organiza conceitos por origem. Cada subdiretório contém o conceito principal; `sources/` só surge após a confirmação do usuário.

## Pacote solicitado ao NotebookLM

Use `notebooklm ask --json -n <notebook-id>` com solicitação equivalente:

```text
Responda em português do Brasil. Produza um pacote de extração para uma síntese fiel deste notebook, sem YAML, caminhos de arquivo, links Markdown, Mermaid ou formatação de ferramenta.

Inclua: título e descrição; TL;DR com até cinco pontos; ideias centrais, mecanismos, exemplos, números e limites; três a cinco tags; relações explicitamente sustentadas; fontes que apoiam cada afirmação; lacunas, divergências e fontes indisponíveis. Não complete informações ausentes nem invente referências.
```

A skill transforma esse pacote em Markdown visual, YAML e citações. As referências retornadas em JSON complementam a proveniência.

## Pacote por fonte

Após confirmação do usuário, use `notebooklm ask --json -n <notebook-id> -s <source-id>`:

```text
Responda em português do Brasil. Resuma exclusivamente esta fonte, sem YAML, caminhos, Mermaid ou links Markdown. Inclua título, descrição, argumentos, exemplos, números, limites, tags e lacunas. Não use conhecimento de outras fontes e não invente conteúdo.
```

Mantenha fontes em erro no inventário e no `log.md`; não gere resumo de conteúdo indisponível.

## índices, log e links

- O índice raiz declara somente `okf_version: "0.1"` e aponta para `/notebooks/`.
- `notebooks/index.md` lista notebooks e descrições.
- O índice de cada notebook aponta ao conceito principal e a `sources/` apenas quando ela existir.
- `log.md` registra criação e atualizações em `## AAAA-MM-DD`, mais recente primeiro.
- Use links absolutos relativos  à raiz, como `/notebooks/curso/curso.md`.

## Cross-linking e proveniência

Crie no máximo três links em `## Conhecimento relacionado`. Exija relação explícita na extração ou duas tags normalizadas em comum. A frase contextual expressa a semântica. Não gere grafo ou taxonomia paralela.

Síntese: `type: NotebookLM Summary`, `notebook_id`, `origin`, `source_ready_count` e `source_error_count`.

Fonte: `type: NotebookLM Source`, `source_id`, `source_status` e `resource` apenas quando conhecida.
