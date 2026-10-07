# Bundle OKF da documentação do RM

Formato que a **alm-download** grava e a **alm-sync** mantém. `<path>` = `rm.download.path` do
`.kiro/config/alm-power/pa_*.json`, relativo à raiz do repositório. `<path>` é a raiz de um **bundle OKF v0.2**
([SPEC.md](https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md) §3):

```
<path>/
  index.md                              # §8: listagem do bundle
  log.md                                # §9: histórico de downloads e sincronismos
  sync.md                               # concept: situação de cada artefato
  <pasta do RM>/<id>-<slug>.md          # um concept por artefato (saída de rm_get_requirement)
```

## Artefato

- **Arquivo:** `<path>/<path do artefato>`, onde o `path` do artefato vem de `rm_search_requirements` (o MCP
  aplica a regra: `<caminho da pasta no RM>/<id>-<slug do título>.md`, ex.: `03-Casos de Uso/2010-uc-cadastrar-cliente.md`).
  Não monte o nome à mão. Não use o `folder` da busca para a pasta: ele traz só o nome da última pasta.
- **Conteúdo:** a saída de `rm_get_requirement(id, links="bundle")` **exatamente como veio**. Ela já é um concept
  OKF conforme: `type`, `sources[0].last_modified` (última modificação no ALM) e `generated.at` (quando foi gerado).
- **Links no corpo:** com `links="bundle"`, embed sai `![<id> <título>](<caminho relativo>)` e hyperlink para
  artefato `[<id> <título>](<caminho relativo>)`, apontando para o arquivo do outro artefato no bundle (ex.:
  `![23434 REG Validar data fim periodo PAB](<../03 Regras Negócio/23434-reg-validar-data-fim-periodo-pab.md>)`).
  Artefato de pasta não baixada = link quebrado, tolerado pelo OKF (§6.1); passa a funcionar quando a pasta for
  baixada. Não reescreva os links.
- **Caminho mudou** (título novo, pasta renomeada/movida ou artefato movido de pasta): o arquivo novo vai para o
  `path` atual; depois de gravá-lo, apague o arquivo antigo registrado no `sync.md` (e qualquer outro `<id>-*.md`
  na pasta nova) e atualize o link da linha. Pasta antiga que ficou vazia pode ser apagada.
- **Removido do ALM e mantido pelo usuário:** acrescente `status: deprecated` (§5.4) ao frontmatter do arquivo,
  logo depois de `generated`. Não invente outra chave.

## `sync.md`

Todo `.md` do bundle que não é `index.md`/`log.md` precisa de frontmatter com `type` (§11): `sync.md` é um concept.

```markdown
---
type: Relatório de Sincronismo
title: Sincronismo ALM → OKF
description: Situação de cada artefato do DOORS Next baixado neste bundle.
generated: { by: "process:alm-sync", at: "2026-10-06T18:00:00Z" }
---
| Artefato | Pasta | Última atualização ALM | Generated OKF | Status |
|---|---|---|---|---|
| [2010 — UC - Cadastrar cliente](</03-Casos de Uso/2010-uc-cadastrar-cliente.md>) | 03-Casos de Uso | 2026-10-05T19:42:00Z | 2026-10-06T13:00:00Z | atualizado |
```

- `generated.at` = instante da última gravação do `sync.md` (a última verificação); `by` = `process:alm-download`
  ou `process:alm-sync`, conforme a skill que gravou.
- **Última atualização ALM** = `modified` de `rm_search_requirements`/`rm_list_modified` (ou
  `sources[0].last_modified` do arquivo). **Generated OKF** = `generated.at` do arquivo. Ambos em ISO 8601 UTC
  (`...Z`): compare como texto.
- Link bundle-relative com `/` (§6.1) entre `<...>` (pastas do RM têm espaço). `|` no título vira `\|`.
- Uma linha por artefato, ordenada por pasta e id.

| Status | Quando |
|---|---|
| `atualizado` | baixado e Última atualização ALM ≤ Generated OKF |
| `pendente` | Última atualização ALM > Generated OKF (mudou no ALM depois do download) ou o `path` atual difere do arquivo registrado (nota `movido` se mudou de pasta) |
| `novo` | está numa pasta do RM e ainda não foi baixado (Generated OKF vazio) |
| `removido` | não existe mais no ALM (não voltou em `rm_list_modified`) ou saiu das pastas baixadas (nota `fora das pastas baixadas`) |
| `erro` | o download falhou; a mensagem curta vai depois do status (`erro: HTTP 403`) |

## `index.md`

Sem frontmatter, exceto `okf_version` (§8, §12). Uma seção por pasta do RM; entrada com o `description` do
concept quando houver:

```markdown
---
okf_version: "0.2"
---
# 03-Casos de Uso

* [2010 — UC - Cadastrar cliente](</03-Casos de Uso/2010-uc-cadastrar-cliente.md>) - Cadastro de um novo cliente no sistema.

# Bundle

* [Sincronismo ALM → OKF](/sync.md) - Situação de cada artefato do DOORS Next baixado neste bundle.
```

Regere o arquivo inteiro sempre que entrar, sair ou mudar de nome um artefato.

## `log.md`

§9: título `# Histórico da documentação do RM`, grupos `## AAAA-MM-DD` (data de hoje), **mais novo primeiro**; se
o grupo de hoje já existe, acrescente nele. Uma linha por evento:

```markdown
## 2026-10-06
* **Creation**: Download de 3 pastas e 120 artefatos do DOORS Next.
* **Update**: [2010 — UC - Cadastrar cliente](</03-Casos de Uso/2010-uc-cadastrar-cliente.md>) baixado de novo.
* **Deprecation**: [2033 — RN - Regra antiga](</04-Regras/2033-rn-regra-antiga.md>) removido do ALM.
```
