# notebooklm-to-notes

Converte notebooks do NotebookLM em um vault Obsidian minimalista, com briefing editorial em pt-BR, mapa mental nativo, proveniência preservada e validação automática.

O objetivo do projeto não é apenas exportar notas. Ele transforma fontes soltas em um deck de conhecimento progressivo, auditável e pronto para uso como segundo cérebro.

## O que este projeto entrega

- Inventário literal das fontes, preservando título, ID, URL e tipo quando disponíveis.
- Briefing editorial em pt-BR com Sumário Executivo, desenvolvimento e seções estruturadas.
- Mapa mental nativo inserido no ponto certo do texto, sem deslocar a hierarquia editorial.
- Frontmatter com metadados operacionais para rastreio, reabertura e manutenção.
- Saída organizada para Obsidian, com índice por notebook e log de histórico.
- Validação automática do staging antes da publicação.
- Fluxo determinístico, com foco em fidelidade, legibilidade e rastreabilidade.

## O que sai no vault

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

O conteúdo principal fica em `notebooks/<slug>/<slug>.md`.
O `index.md` organiza a navegação local e o `log.md` registra a atualização editorial.

## Como funciona

1. O script consulta o inventário de fontes do NotebookLM.
2. Em seguida, gera um briefing em português do Brasil.
3. O mapa mental é produzido como artefato separado.
4. O mapa é inserido após `## 1. Sumário Executivo` e antes da seção `## 2.`.
5. O staging é validado com o validador do repositório.
6. Se `--publish` for usado, somente o notebook validado é copiado para o vault final.

## Instalação

```bash
python -m pip install -r requirements.txt
```

Pré-requisito adicional: a CLI `notebooklm` precisa estar disponível no ambiente.

## Uso

Extrair um notebook para um staging local:

```bash
python scripts/extrair_notebook.py --notebook <UUID> --deck <diretório-do-vault>
```

Publicar o notebook validado no vault final:

```bash
python scripts/extrair_notebook.py --notebook <UUID> --deck <diretório-do-vault> --publish
```

Parâmetros opcionais:

- `--description`
- `--tag`
- `--knowledge-domain`
- `--neuron`
- `--related-summary`

Esses campos permitem adaptar o pacote para um contexto editorial específico sem perder o contrato de fidelidade.

## Validação

```bash
python scripts/validar_nota.py --deck <diretório-do-vault> --pt-br
python -m unittest discover -s tests
```

O validador confere, entre outros pontos:

- UTF-8 sem BOM.
- Frontmatter YAML presente.
- Descrição com tamanho adequado.
- Tags hierárquicas.
- `source_count` compatível com `source_links`.
- Presença de `## Mapa mental` exatamente uma vez.
- Ordem correta entre Sumário Executivo, mapa mental e seção 2.
- Ausência de referências a `evidence/` no corpo final.

## Contratos do projeto

- O vault final é minimalista e não depende de índices globais na raiz.
- A síntese deve permanecer em pt-BR.
- A proveniência das fontes precisa continuar verificável no próprio texto.
- O mapa mental deve ser pequeno, legível e derivado do conteúdo extraído.
- A extração só é publicada quando o staging passa na validação.

## Estrutura do repositório

- `scripts/extrair_notebook.py`: orquestra inventário, briefing, mapa mental e publicação.
- `scripts/validar_nota.py`: valida o contrato estrutural e textual do deck.
- `references/`: documentação de fidelidade, formato visual, deck progressivo e exemplos.
- `tests/`: regressões da extração e da validação.
- `agents/openai.yaml`: configuração de interface e prompt padrão do skill.
- `SKILL.md`: contrato operacional do agente.

## Potencial do projeto

Este repositório funciona bem como base para:

- organização de pesquisa com rastreabilidade;
- resumo de aulas, cursos e vídeos longos;
- padronização editorial de conteúdo derivado de fontes brutas;
- criação de um segundo cérebro com recuperação confiável;
- automações futuras para ingestão de outras origens.

## Referências

- [Contrato de fidelidade](references/contrato-fidelidade.md)
- [Deck progressivo](references/deck-progressivo.md)
- [Formato OKF](references/formato-okf.md)
- [Formato visual](references/formato-visual.md)
- [Exemplo OKF](references/exemplo-okf.md)
- [Exemplo de deck OKF](references/exemplo-deck-okf.md)
- [Exemplo de fidelidade](references/exemplo-fidelidade.md)
- [Exemplo de bundle OKF](references/exemplo-bundle-okf.md)
- [Exemplo gold](references/exemplo-gold.md)

## Licença

[MIT](LICENSE)