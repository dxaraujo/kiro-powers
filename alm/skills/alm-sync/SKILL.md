---
name: "alm-sync"
description: "Download and keep in sync the IBM DOORS Next (RM) documentation as an Open Knowledge Format (OKF) bundle in the repository, one Markdown file per artifact, through the `alm` MCP. The MCP lists the folders, writes the files, sync.md and index.md itself; the skill only drives it. Use when the user asks to baixar toda a documentação, baixar os requisitos, exportar o RM, baixar a pasta X do RM, gerar a documentação em OKF, trazer os requisitos para o repositório, continuar o download, sincronizar a documentação, o que mudou no ALM, atualizar os requisitos baixados, verificar se a documentação está atualizada ou sincronizar o requisito 123."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "2.0.0"
---

# alm-sync

Baixa e mantém em dia a documentação do DOORS Next em `<rm.download.path>/<pasta do RM>/<id>-<slug>.md`, um
bundle OKF com `sync.md` (situação de cada artefato) e `index.md`. **O MCP faz o trabalho pesado**: lista as pastas,
grava os arquivos, o `sync.md` e o `index.md`, e devolve só resumos. Listas e conteúdo de artefato não passam pela
conversa. O primeiro download e os sincronismos seguintes são o mesmo fluxo: no primeiro, tudo vem como `novo`.

## Antes de chamar

1. **Leia `.kiro/config/alm-power/pa_*.json`** (um → use; vários → pergunte): os três parâmetros das `rm_*`
   (`project_area_identifier`, `component`, `configuration`), `rm.folders` e `rm.download`. Sem `rm` → ofereça a
   **alm-setup**.
2. Sem `rm.download.path` → pergunte a pasta raiz (sugira `docs/alm`), relativa à raiz do repositório, com `/`, e
   grave `rm.download = {"path": ...}`. `dest` de todas as chamadas = caminho **absoluto** dessa pasta (raiz do
   repositório + `path`).
3. Formato antigo: `rm.download.last-download` → renomeie para `last-sync`; `<path>/log.md` → apague.

## Fluxo

1. **Pastas do RM:** `rm_list_folders(...)` e compare com `rm.folders`:
   - mesmo identifier com outro nome (pasta renomeada ou movida) → atualize a chave sem perguntar;
   - identifier novo (inclusive subpasta de uma já baixada) → liste e pergunte quais entram;
   - identifier de `rm.folders` que sumiu → tire de `rm.folders` (os artefatos dela saem no passo 2).
2. **Inventário:** `rm_sync_plan(folders=rm.folders, dest)`. O MCP lista cada pasta, compara com o `sync.md`,
   **apaga os arquivos removidos** (não estão mais em nenhuma pasta) e regrava o `sync.md`. Mostre:
   - tabela **Pasta | Total | Novo | Pendente | Atualizado | Erro** (de `pastas`);
   - `removidos` (já apagados), como lista **Código | Título | Pasta**;
   - `inconsistentes` (count ≠ listados no servidor): avise que nada foi removido e que os `nao_confirmados` serão
     conferidos no próximo sincronismo.
3. **Nada a baixar** (`a_baixar = 0`) → diga que está tudo atualizado, grave `rm.download.last-sync` e pare.
4. **Confirmar e baixar:** mostre `a_baixar` e peça confirmação. Depois chame
   `rm_download_requirements(dest)` repetidamente até `restantes = 0`: cada chamada baixa os próximos 50 da fila e
   grava o `sync.md` (e o `index.md` ao terminar). Informe o progresso a cada chamada. Erro de um artefato não para
   o lote: acumule os `erros`.
5. **Fechar:** `rm.download.last-sync` = agora, ISO 8601 UTC (`...Z`); grave o `pa_*.json` (pastas e
   `last-sync`). Responda com o total baixado, os erros e o caminho do `sync.md`. Sobrou erro → diga que rodar a
   alm-sync de novo tenta só esses.

**Retomar:** se a sessão cair ou o contexto for compactado, rode o fluxo de novo. A fila está no `sync.md`: o que
já foi baixado fica `atualizado` e só o resto é baixado.

## Pedido pontual

"Sincroniza o 2010", "baixa o UC 2010" → `rm_download_requirements(dest, requirement_ids=["2010"])` (grava o
arquivo e a linha do `sync.md`). "O 2010 está atualizado?" → `rm_list_modified(["2010"])` e compare com a coluna
Generated OKF da linha do `sync.md`.

## Regras

- Nunca chame `rm_get_requirement` nem `rm_list_folder` neste fluxo, e nunca escreva `sync.md`, `index.md` ou os
  arquivos dos artefatos: só o MCP grava no bundle. Só leitura no ALM.
- Removidos são sempre apagados (pelo `rm_sync_plan`). Para manter um artefato, mantenha a pasta em `rm.folders`.
- Mostre nomes de pasta e tipo, nunca `FR_`/`OT_`.
