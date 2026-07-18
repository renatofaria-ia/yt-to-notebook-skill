# notebooklm-to-notes

Converte notebooks do NotebookLM em um vault Obsidian minimalista, com briefing editorial em pt-BR, mapa mental Mermaid, proveniência de fontes e validação automática.

O projeto transforma fontes de um notebook em um pacote de conhecimento legível, rastreável e pronto para reabertura no Obsidian, sem carregar artefatos brutos de auditoria no vault final.

## Entrega

- Inventário de fontes com título, URL quando disponível, tipo e ID do NotebookLM.
- Briefing editorial em pt-BR com Sumário Executivo e seções H2 numeradas.
- Mapa mental nativo convertido para Mermaid e inserido na posição editorial correta.
- Frontmatter para recuperação semântica, conexões e proveniência.
- Índice e histórico locais para cada notebook.
- Validação do staging antes da publicação.

## Estrutura do vault

```text
<deck>/
  .obsidian/
    graph.json
  neurons/
  notebooks/
    <slug>/
      <slug>.md
      index.md
      log.md
```

O vault não usa `evidence/`, `sources/`, `index.md` ou `log.md` na raiz. O conteúdo principal fica em `notebooks/<slug>/<slug>.md`.

## Instalação

```bash
python -m pip install -r requirements.txt
python -m notebooklm auth check --test --json
```

A CLI `notebooklm` precisa estar instalada e autenticada no ambiente.

## Uso

Gerar e validar no staging interno:

```bash
python scripts/extrair_notebook.py --notebook <UUID> --deck <diretório-do-vault>
```

Publicar o notebook validado:

```bash
python scripts/extrair_notebook.py --notebook <UUID> --deck <diretório-do-vault> --publish
```

Parâmetros editoriais opcionais:

- `--description`
- `--tag`
- `--knowledge-domain`
- `--neuron`
- `--related-summary`

## Validação

```bash
python scripts/validar_nota.py --deck <diretório-do-vault> --pt-br
python -m unittest discover -s tests
```

O validador confere UTF-8 sem BOM, frontmatter, tags, `source_links`, links semânticos, ordem do mapa Mermaid, seções em pt-BR e ausência de estrutura legada.

## Contratos

- A extração só é publicada depois de o staging passar na validação.
- `source_links` preserva a origem de cada fonte mesmo quando o NotebookLM não entrega URL.
- O mapa mental é pequeno, legível e derivado do artefato nativo do NotebookLM.
- O vault final mantém apenas conhecimento editorial e metadados necessários para recuperação.

## Estrutura do repositório

- `scripts/extrair_notebook.py`: inventaria fontes, gera artefatos, monta o vault e publica.
- `scripts/validar_nota.py`: valida o contrato estrutural e editorial.
- `references/`: contrato, estrutura progressiva, formato visual e exemplo mínimo.
- `tests/`: regressões do extrator e do validador.
- `agents/openai.yaml`: metadata e prompt padrão da interface da skill.
- `SKILL.md`: instruções operacionais para agentes.

## Referências

- [Contrato de fidelidade](references/contrato-fidelidade.md)
- [Deck progressivo](references/deck-progressivo.md)
- [Formato visual](references/formato-visual.md)
- [Exemplo de vault minimalista](references/exemplo-vault-minimalista.md)

## Licença

[MIT](LICENSE)