---
name: "alm-sync"
description: "Download and keep in sync the IBM DOORS Next (RM) documentation as an Open Knowledge Format (OKF) bundle in the repository, one Markdown file per artifact, through the `alm` MCP. The MCP lists the folders, writes the files, sync.md and index.md itself; the skill only drives it. Use when the user asks to baixar toda a documentação, baixar os requisitos, exportar o RM, baixar a pasta X do RM, gerar a documentação em OKF, trazer os requisitos para o repositório, continuar o download, sincronizar a documentação, o que mudou no ALM, atualizar os requisitos baixados, verificar se a documentação está atualizada, sincronizar o requisito 123, subir as alterações para o ALM, publicar no ALM o que alterei no md ou enviar o 2010 alterado para o ALM."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "2.2.1"
---

# alm-sync

Baixa e mantém em dia a documentação do DOORS Next em `<rm.download.path>/<pasta do RM>/<id>-<slug>.md`, um
bundle OKF com `sync.md` (situação de cada artefato) e `index.md`. **O MCP faz o trabalho pesado**: lista as pastas,
grava os arquivos, o `sync.md` e o `index.md`, e devolve só resumos. Listas e conteúdo de artefato não passam pela
conversa. O primeiro download e os sincronismos seguintes são o mesmo fluxo: no primeiro, tudo vem como `novo`.
O caminho inverso (arquivo editado → ALM) é o fluxo **Subir alterações**, que roda sozinho, sem o sincronismo.

## Antes de chamar

1. **Leia `.kiro/config/alm-power/pa_*.json`** (um → use; vários → pergunte): os três parâmetros das `rm_*`
   (`project_area_identifier`, `component`, `configuration`), `rm.folders` e `rm.download`. Sem `rm` → ofereça a
   **alm-setup**.
2. Sem `rm.download.path` → pergunte a pasta raiz (sugira `docs/alm/<nome>`, mesmo `<nome>` do `pa_<nome>.json`), relativa à raiz do repositório, com `/`, e
   grave `rm.download = {"path": ...}`. `dest` de todas as chamadas = caminho **absoluto** dessa pasta (raiz do
   repositório + `path`).
   Gravou o `path` agora, ou falta `.kiro/hooks/alm-okf-created-<nome>.kiro.hook` → gere-o como em **4. Gravar** da
   **alm-setup** (um hook por project area).
3. Formato antigo: `rm.download.last-download` → renomeie para `last-sync`; `<path>/log.md` → apague.

## Fluxo

1. **Pastas do RM:** `rm_list_folders(...)` e compare com `rm.folders`:
   - mesmo identifier com outro nome (pasta renomeada ou movida) → atualize a chave sem perguntar;
   - identifier novo (inclusive subpasta de uma já baixada) → liste e pergunte quais entram;
   - identifier de `rm.folders` que sumiu → tire de `rm.folders` (os artefatos dela saem no passo 2).
2. **Inventário:** `rm_sync_plan(folders=rm.folders, dest)`. O MCP lista cada pasta, compara com o `sync.md`,
   **apaga os arquivos removidos** (não estão mais em nenhuma pasta) e regrava o `sync.md`. Mostre:
   - tabela **Pasta | Total | Novo | Pendente | Atualizado | Modificado | Erro** (de `pastas`);
   - `removidos` (já apagados), como lista **Código | Título | Pasta**;
   - `inconsistentes` (count ≠ listados no servidor): avise que nada foi removido e que os `nao_confirmados` serão
     conferidos no próximo sincronismo.
3. **Nada a baixar** (`a_baixar = 0`) → diga que está tudo atualizado, grave `rm.download.last-sync` e pare.
4. **Confirmar e baixar:** mostre `a_baixar` e peça confirmação. Depois chame
   `rm_download_requirements(dest)` repetidamente até `restantes = 0`: cada chamada baixa os próximos 50 da fila e
   grava o `sync.md` (e o `index.md` ao terminar). Informe o progresso a cada chamada. Erro de um artefato não para
   o lote: acumule os `erros`.
   `modificado` = ao baixar, o MCP trocou um link da UI web do DOORS Next pelo arquivo do bundle: o arquivo
   difere do ALM e precisa subir. Fica `modificado` até o ALM mudar; aí volta para a fila.
5. **Fechar:** `rm.download.last-sync` = agora, ISO 8601 UTC (`...Z`); grave o `pa_*.json` (pastas e
   `last-sync`). Responda com o total baixado, os erros e o caminho do `sync.md`. Sobrou erro → diga que rodar a
   alm-sync de novo tenta só esses.
6. **Sentido inverso:** linhas `modificado` no `sync.md` → liste-as (**Código | Título | Pasta**) e pergunte se
   pode subir para o ALM. Sim → **Subir alterações** com esses ids. Assim o sincronismo vale nos dois sentidos.

**Retomar:** se a sessão cair ou o contexto for compactado, rode o fluxo de novo. A fila está no `sync.md`: o que
já foi baixado fica `atualizado` e só o resto é baixado.

## Subir alterações

Fluxo próprio: roda ao fim do sincronismo (passo 6) ou direto, quando o usuário editou arquivos do bundle e pede
para subir ("sobe o 2010 e o 2011 para o ALM") — **sem** rodar o sincronismo antes.

1. **Quais:** os ids que o usuário informar; sem ids, as linhas `modificado` do `sync.md`. Id sem arquivo no
   `sync.md` → diga que não está baixado e pule.
2. **Conflito:** `rm_list_modified(ids)` e compare cada `modified` com a coluna Generated OKF da linha. ALM mais
   novo → **não suba**: o artefato mudou no ALM depois do download e a gravação apagaria essa mudança. Ofereça
   baixar de novo (`rm_download_requirements(dest, requirement_ids=[...])`) para refazer a edição sobre a versão
   atual.
3. **Ler o arquivo** (`<dest>/<path da linha>`): `title`, `embedded` e o corpo (tudo depois do cabeçalho YAML).
   `attributes`/`links` só sobem os que o usuário disser que alterou (gravar um tipo de link substitui a lista
   inteira daquele tipo: mande a lista completa do arquivo).
4. **Confirmar:** mostre **Código | Título | O que sobe** (texto, título, atributos/links pelos nomes) e peça
   confirmação do lote.
5. **Gravar**, um artefato por vez, pela ferramenta de gravação da alm-rm:
   `rm_update_requirement(id, title=<title>, text=<corpo>, embedded=<embedded>, attributes=<só os alterados>)`.
   Sem o `embedded`, todo embed vira hyperlink. Erro num artefato não para os outros: acumule.
6. **Reconciliar:** `rm_download_requirements(dest, requirement_ids=<os gravados>)`: o MCP regrava o arquivo e a
   linha do `sync.md` (`atualizado`) com a versão que ficou no ALM. Responda com os gravados, os conflitos e os
   erros.

## Pedido pontual

"Sincroniza o 2010", "baixa o UC 2010" → `rm_download_requirements(dest, requirement_ids=["2010"])` (grava o
arquivo e a linha do `sync.md`). "O 2010 está atualizado?" → `rm_list_modified(["2010"])` e compare com a coluna
Generated OKF da linha do `sync.md`.

## Regras

- Nunca chame `rm_get_requirement` nem `rm_list_folder` neste fluxo, e nunca escreva `sync.md`, `index.md` ou os
  arquivos dos artefatos: só o MCP grava no bundle.
- No ALM, só leitura, exceto em **Subir alterações**, e sempre com confirmação do usuário.
- Removidos são sempre apagados (pelo `rm_sync_plan`). Para manter um artefato, mantenha a pasta em `rm.folders`.
- Mostre nomes de pasta e tipo, nunca `FR_`/`OT_`.
