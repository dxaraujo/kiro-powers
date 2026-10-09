---
name: "alm-sync"
description: "Download and keep in sync, in both directions, the IBM DOORS Next (RM) documentation as an Open Knowledge Format (OKF) bundle in the repository, one Markdown file per artifact, through the `alm` MCP. The MCP lists the folders, writes the files, sync.md and index.md, and uploads the edited files itself; the skill only drives it. Use when the user asks to baixar toda a documentação, baixar os requisitos, exportar o RM, baixar a pasta X do RM, gerar a documentação em OKF, trazer os requisitos para o repositório, continuar o download, sincronizar a documentação, o que mudou no ALM, atualizar os requisitos baixados, verificar se a documentação está atualizada, sincronizar o requisito 123, subir as alterações para o ALM, publicar no ALM o que alterei no md ou enviar o 2010 alterado para o ALM."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "3.1.1"
---

# alm-sync

Mantém em sincronia, nos dois sentidos, a documentação do DOORS Next em
`<rm.download.path>/<pasta do RM>/<id>-<slug>.md`: um bundle OKF com `sync.md` (situação de cada artefato) e
`index.md`. **O MCP faz o trabalho pesado**: lista as pastas, grava os arquivos, o `sync.md` e o `index.md`, sobe os
md editados e devolve só resumos. Listas e conteúdo de artefato não passam pela conversa. O sincronismo **baixa
primeiro e depois sobe**; no primeiro, tudo vem como `novo`.

## Estados do `sync.md`

| Estado | Quando | Ação |
|---|---|---|
| `novo` | ainda não baixado | baixar |
| `sincronizado` | md igual ao ALM | — |
| `desatualizado` | há versão mais nova no ALM | baixar |
| `atualizado` | o md foi alterado e precisa ir para o ALM | subir |
| `normalizado` | o md **não** foi alterado; o ALM foge da regra embed/link do bundle | subir |
| `conflito` | md e ALM foram alterados | **perguntar ao usuário** qual versão fica |
| `erro: <msg>` | falha no download | baixar de novo |

O MCP detecta a alteração no md pelo `Hash` (sha256 do arquivo) e a do ALM pela coluna `Última atualização ALM`.
`normalizado` **não é falso positivo**: no md, embed e link para o bundle ficam iguais, então diff, hash e
`git diff` não mostram a diferença; ela só existe no XHTML do ALM. Não investigue nem compare arquivos: suba.
Artefato que mudou de pasta volta a `novo` na pasta nova (o arquivo antigo é apagado; com alteração local, vira
`conflito` e o arquivo fica).

## Embeds e links no md

Regra fixa do bundle: **artefato do bundle (id no `sync.md`) é sempre embed; o resto é sempre link**. Por isso o md
do bundle não tem `embedded`, e o `links:` do cabeçalho (rastreabilidade) é só de leitura: não sobe. Ao editar um md,
use:

| Referência | Formato |
|---|---|
| embed (artefato do bundle) | `[<id>](<id>)` |
| link para artefato de outra PA | `[<id>](<URL do ALM>)` |
| link externo | `[<texto descritivo>](<url>)` |

O que o download grava (`[id título](../03-Regras/2001-x.md)` e `[id título](URL do ALM)`) também vale.

## Antes de chamar

1. **Leia `.kiro/config/power/alm/pa_*.json`** (um → use; vários → pergunte): os três parâmetros das `rm_*`
   (`project_area_identifier`, `component`, `configuration`), `rm.folders` e `rm.download`. Sem `rm` → regra "Sem
   setup" do steering:
   - área RM, `component` e `configuration`: como na seção "Sem setup" da **alm-rm**;
   - pasta raiz do bundle: pergunte (sugira `docs/alm/<trecho do nome da área>`);
   - pastas a sincronizar: `rm_list_folders(...)` e o usuário escolhe. **Bundle já existe** (`sync.md` na pasta) →
     proponha todas as pastas que aparecem nele e avise que pasta **não** escolhida tem os arquivos apagados pelo
     `rm_sync_plan`. As escolhidas fazem o papel de `rm.folders` no fluxo;
   - sem arquivo, não grave `rm.folders` nem `last-sync` (passos 1, 3 e 7): o estado fica no `sync.md`. No fim,
     ofereça a alm-setup para guardar área, pastas e caminho.
2. Sem `rm.download.path` → pergunte a pasta raiz (sugira `docs/alm/<nome>`, mesmo `<nome>` do `pa_<nome>.json`),
   relativa à raiz do repositório, com `/`, e (havendo arquivo) grave `rm.download = {"path": ...}`. `dest` de todas as chamadas =
   caminho **absoluto** dessa pasta (raiz do repositório + `path`).

## Fluxo

1. **Pastas do RM:** `rm_list_folders(...)` e compare com `rm.folders`:
   - mesmo identifier com outro nome (pasta renomeada ou movida) → atualize a chave sem perguntar;
   - identifier novo (inclusive subpasta de uma já baixada) → liste e pergunte quais entram;
   - identifier de `rm.folders` que sumiu → tire de `rm.folders` (os artefatos dela saem no passo 2).
2. **Inventário:** `rm_sync_plan(folders=rm.folders, dest)`. O MCP lista cada pasta, compara com o `sync.md`,
   **apaga os arquivos removidos** (não estão mais em nenhuma pasta) e regrava o `sync.md`. Mostre:
   - tabela **Pasta | Total | Novo | Sincronizado | Desatualizado | Atualizado | Normalizado | Conflito | Erro** (de `pastas`;
     estado ausente = 0);
   - `removidos` (já apagados), como lista **Código | Título | Pasta**;
   - `inconsistentes` (count ≠ listados no servidor): avise que nada foi removido e que os `nao_confirmados` serão
     conferidos no próximo sincronismo.
3. **Nada a fazer** (`a_baixar = 0`, `a_subir = 0` e `conflitos` vazio) → diga que está tudo sincronizado, grave
   `rm.download.last-sync` e pare.
4. **Baixar:** com `a_baixar > 0`, mostre o total e peça confirmação. Depois chame `rm_download_requirements(dest)`
   repetidamente até `restantes = 0` (ou até só restarem os ids com erro): cada chamada baixa os próximos 50 e grava
   o `sync.md` (e o `index.md` ao terminar). Informe o progresso a cada chamada e acumule os `erros`.
5. **Conflitos:** para cada item de `conflitos`, mostre **Código | Título | Pasta** e **pergunte qual versão fica:
   md ou ALM**. Uma pergunta por artefato, ou uma para todos se o usuário preferir.
   - **ALM** → `rm_download_requirements(dest, requirement_ids=[...])`. Avise antes: a alteração do md é perdida.
   - **md** → `rm_upload_requirements(dest, requirement_ids=[...])`. Avise antes: a alteração feita no ALM é sobrescrita.
6. **Subir:** com `a_subir > 0`, liste as linhas `atualizado` e `normalizado` do `sync.md` (**Código | Título | Pasta |
   Estado**) e peça confirmação; diga que `normalizado` só troca hyperlink↔embed no ALM, sem mudar o texto.
   Depois chame `rm_upload_requirements(dest)` até `restantes = 0` (ou até só restarem erros). Cada chamada
   sobe título e corpo do md e baixa o requisito de novo (a linha fica `sincronizado`). Se o ALM mudou nesse
   meio-tempo, o MCP não sobe e devolve o id em `conflitos` → volte ao passo 5 com eles.
7. **Fechar:** `rm.download.last-sync` = agora, ISO 8601 UTC (`...Z`); grave o `pa_*.json` (pastas e `last-sync`).
   Responda com baixados, enviados, conflitos resolvidos (e a versão escolhida), os erros e o caminho do `sync.md`.
   Sobrou erro → diga que rodar a alm-sync de novo tenta só esses.

**Retomar:** se a sessão cair ou o contexto for compactado, rode o fluxo de novo. O estado está no `sync.md`.

## Pedido pontual

- "Sincroniza o 2010", "baixa o UC 2010" → `rm_download_requirements(dest, requirement_ids=["2010"])`. A linha está
  `atualizado` ou `conflito` → avise antes que a alteração do md se perde.
- "Sobe o 2010 e o 2011", "publica no ALM o que alterei" → `rm_sync_plan(...)`, para o MCP ver a alteração no md, e
  depois os passos 5 e 6 só com esses ids (sem ids: todos os `atualizado`/`normalizado`). Não precisa baixar antes.
- "O 2010 está atualizado?" → `rm_sync_plan(...)` e responda com o estado da linha do 2010 no `sync.md`.

## Regras

- Nunca chame `rm_get_requirement`, `rm_list_folder` nem `rm_update_requirement` neste fluxo, e nunca escreva
  `sync.md`, `index.md` ou os arquivos dos artefatos: só o MCP grava no bundle e sobe para o ALM.
- No ALM, só escreva nos passos 5 e 6, sempre com confirmação do usuário. Conflito **sempre** pergunta: nunca
  escolha a versão sozinho.
- Removidos são sempre apagados (pelo `rm_sync_plan`). Para manter um artefato, mantenha a pasta em `rm.folders`.
- Mostre nomes de pasta e tipo, nunca `FR_`/`OT_`.
