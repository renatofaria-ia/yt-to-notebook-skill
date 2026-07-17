# notebooklm-to-notes

Skill para transformar notebooks do NotebookLM em conhecimento **OKF 0.1** visual, rastreável e pronto para Obsidian, Markdown ou Notion. A versão atual é **v1.1.0**: além do bundle independente, ela suporta um deck hierárquico de segundo cérebro.

## O que entrega

- Síntese em PT-BR com TL;DR, callouts, tabelas, Mermaid e mapa mental quando útil.
- Frontmatter YAML OKF, `index.md`, `log.md`, citações e proveniência do NotebookLM.
- Resumos por fonte somente após confirmação do usuário, reduzindo trabalho e ruído.
- Cross-links didáticos entre notebooks, sem banco de grafo, wikilinks ou taxonomia paralela.
- Validação de UTF-8, YAML, Mermaid, pt-BR e estrutura do deck.

## Estruturas de saída

```text
<bundle>/
  index.md
  log.md
  sintese.md
  sources/
    index.md
    <fonte>.md
```

```text
<deck>/
  index.md
  log.md
  notebooks/
    index.md
    <notebook-slug>/
      index.md
      <notebook-slug>.md
      sources/                 # criado após confirmação do usuário
        index.md
        <fonte>.md
```

Exemplo:

```text
Use $notebooklm-to-notes para resumir o notebook "Curso X" no meu deck de segundo cérebro em C:/Notas.
```

A skill cria primeiro a síntese do notebook e então pergunta se deve gerar resumos de fontes. Bundles antigos permanecem intactos; não há migração automática.

## Validação

```powershell
python -m pip install -r requirements.txt
python .\scripts\validar_nota.py .\caminho\para\conceito.md
python .\scripts\validar_nota.py --bundle .\caminho\para\bundle --pt-br
python .\scripts\validar_nota.py --deck .\caminho\para\deck --pt-br
```

`--deck` exige a raiz, índices progressivos, conceito principal de cada notebook, proveniência mínima de fontes e links internos gerados válidos. `--bundle` continua permissivo conforme o OKF.

## Referências

- [Especificação OKF 0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- `references/formato-okf.md`
- `references/deck-progressivo.md`
- `references/exemplo-deck-okf.md`

## Licença

[MIT](LICENSE).
