# Deck progressivo

O vault é um segundo cérebro editorial: cada notebook gera uma síntese independente, enquanto `neurons/` recebe conexões reutilizáveis quando existirem.

## Organização

```text
<deck>/
  neurons/
  notebooks/
    <notebook-slug>/
      <notebook-slug>.md
      index.md
      log.md
```

Não há índice global. `index.md` e `log.md` pertencem somente à pasta de cada notebook para manter descoberta e histórico próximos ao conteúdo.

## Conexões

- `neuron_links` aponta para conceitos canônicos em `neurons/`.
- `related_summaries` aponta para resumos já publicados em `notebooks/`.
- Só crie conexões que tenham relação editorial explícita; não crie hubs artificiais, banco de arestas ou links recíprocos automáticos.

## Grafo do Obsidian

O extrator preserva a configuração existente e atualiza `graph.json` com busca que oculta índices e logs, sem esconder o conteúdo principal. O grafo mostra sínteses, tags e neurônios válidos.