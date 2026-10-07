---
name: "alm-sync"
description: "Synchronize the IBM DOORS Next (RM) documentation previously downloaded as an Open Knowledge Format (OKF) bundle by alm-download: compare the last modification in the ALM with the date each OKF file was generated, mark pending, new and removed artifacts in sync.md and download again only what changed, through the `alm` MCP. Use when the user asks to sincronizar a documentação, o que mudou no ALM, atualizar os requisitos baixados, verificar se a documentação está atualizada ou sincronizar o requisito 123."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.1.0"
---

# alm-sync

Mantém o bundle da **alm-download** em dia sem baixar tudo de novo: lista só **id + data de modificação** das
pastas (`rm_list_folder`, sem conteúdo) e baixa de novo apenas o que mudou, com o MCP gravando os arquivos
(`rm_download_requirements`: o conteúdo não passa pela conversa). O formato de `sync.md`, `index.md`, `log.md` e
dos arquivos está em [../alm-download/reference.md](../alm-download/reference.md): **leia-o antes de gravar**.

## Antes de chamar

1. **Leia `.kiro/config/alm-power/pa_*.json`** (um → use; vários → pergunte): os três parâmetros das `rm_*`,
   `rm.folders` e `rm.download.path`. Sem `rm` → **alm-setup**. `dest` = caminho **absoluto** de
   `rm.download.path` (raiz do repositório + `path`).
2. **Leia `<path>/sync.md`**. Sem `rm.download.path` ou sem `sync.md` → não há o que sincronizar: ofereça a
   **alm-download**.

## Fluxo

1. **Pastas do RM:** `rm_list_folders(...)` (lento em componente grande: avise) e compare com `rm.folders`:
   - Mesmo identifier com outro nome (pasta renomeada ou movida) → atualize a chave em `rm.folders` sem perguntar;
     os artefatos dela aparecem como movidos no passo 2.
   - Identifier que não está em `rm.folders` (pasta nova, inclusive subpasta de uma já baixada) → liste-as e
     pergunte quais entram. As escolhidas vão para `rm.folders` e são listadas no passo 2 (artefatos = `novo`).
   - Identifier de `rm.folders` que sumiu → a pasta foi apagada; os artefatos dela caem em `removido` no passo 2.
2. **Verificar (só id + modified):**
   - `rm_count_folder` + `rm_list_folder` para cada pasta já baixada (pelo identifier: o nome pode ter mudado no
     passo 1) e cada pasta nova aceita no passo 1. `count` ≠ tamanho da lista → avise que a listagem da pasta está
     inconsistente. Para cada `{id, modified}`:
     - id fora do `sync.md` → `novo` (Generated OKF vazio);
     - Pasta da linha ≠ pasta em que veio → `pendente`, nota `movido`;
     - `modified` > Generated OKF (texto ISO, compare direto) → `pendente` (título novo também muda o `modified`);
     - linha `erro` ou `novo` → `pendente`/`novo` de novo, para tentar outra vez;
     - senão `atualizado`. Última atualização ALM = `modified`.
   - Ids do `sync.md` que não vieram em nenhuma lista → `rm_list_modified(<esses ids>)` numa chamada: voltou → foi
     movido para fora das pastas baixadas: `removido` (nota `fora das pastas baixadas`); não voltou → `removido`.
3. **Gravar o `sync.md`** com as datas e status novos (`generated` = agora, `by: "process:alm-sync"`).
4. **Mostrar** só o que não está `atualizado`: tabela **Código | Título | Pasta | Última atualização ALM |
   Generated OKF | Status**. Tudo `atualizado` → diga isso e pare (atualize só `rm.download.last-download`).
5. **Confirmar e baixar** `pendente` e `novo` em blocos de 50 ids:
   `rm_download_requirements(requirement_ids=<bloco>, dest=<absoluto>)`. A tool grava no caminho atual e apaga o
   arquivo antigo do artefato (`replaced`) quando o título ou a pasta mudou. Depois de **cada** bloco, atualize as
   linhas dele no `sync.md`: link = `path`, Última atualização ALM = `last_modified`, Generated OKF =
   `generated_at`, `atualizado`; ou `erro: <mensagem curta>`. Sessão caiu → releia o `sync.md` e siga dos
   `pendente`/`novo`/`erro`.
6. **Removidos:** pergunte, por lista, se apaga os arquivos. Apagou → tira a linha do `sync.md`. Manteve → grava
   `status: deprecated` no frontmatter do arquivo e a linha fica `removido`.
7. **Fechar:** `sync.md` final; `pa_*.json` se `rm.folders` mudou; `index.md` regerado se entrou, saiu, mudou de
   nome ou de pasta algum artefato (leia só o frontmatter dos arquivos); `log.md` com um `**Update**` por baixado
   e um `**Deprecation**` por removido; `rm.download.last-download` = agora (UTC). Responda com a contagem por
   status.

## Pedido pontual

"Sincroniza o 2010", "o UC 2010 está atualizado?" → `rm_list_modified(["2010"])`, compare com a linha do
`sync.md` e, se `pendente` (ou se o usuário pediu para baixar), `rm_download_requirements(["2010"], dest)` e
atualize a linha, `index.md` (se o nome mudou) e `log.md`. Id fora do `sync.md` → trate como `novo` (a tool grava
na pasta do artefato no RM; pasta fora de `rm.folders` → avise).

## Regras

- Verificar não baixa conteúdo: só `rm_list_folders`, `rm_count_folder`, `rm_list_folder` e `rm_list_modified`.
  `rm_download_requirements` só para `pendente`/`novo` confirmados; nunca `rm_get_requirement`.
- Nunca apague arquivo sem confirmação. A confirmação do passo 5 cobre o arquivo antigo que a tool apaga quando o
  artefato mudou de caminho (ele foi substituído); diga isso ao pedir a confirmação. Só leitura no ALM.
- Mostre nomes de pasta e tipo, nunca `FR_`/`OT_`.
