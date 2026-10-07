---
name: "alm-sync"
description: "Synchronize the IBM DOORS Next (RM) documentation previously downloaded as an Open Knowledge Format (OKF) bundle by alm-download: compare the last modification in the ALM with the date each OKF file was generated, mark pending, new and removed artifacts in sync.md and download again only what changed, through the `alm` MCP. Use when the user asks to sincronizar a documentação, o que mudou no ALM, atualizar os requisitos baixados, verificar se a documentação está atualizada ou sincronizar o requisito 123."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.2"
---

# alm-sync

Mantém o bundle da **alm-download** em dia sem baixar tudo de novo: consulta só a data de modificação no ALM
(`rm_list_modified`, sem conteúdo) e baixa de novo apenas o que mudou. O formato de `sync.md`, `index.md`,
`log.md` e dos arquivos está em [../alm-download/reference.md](../alm-download/reference.md): **leia-o antes de
gravar**.

## Antes de chamar

1. **Leia `.kiro/config/alm-power/pa_*.json`** (um → use; vários → pergunte): os três parâmetros das `rm_*`,
   `rm.folders` e `rm.download.path`. Sem `rm` → **alm-setup**.
2. **Leia `<path>/sync.md`**. Sem `rm.download.path` ou sem `sync.md` → não há o que sincronizar: ofereça a
   **alm-download**.

## Fluxo

1. **Pastas do RM:** `rm_list_folders(...)` (lento em componente grande: avise) e compare com `rm.folders`:
   - Mesmo identifier com outro nome (pasta renomeada ou movida) → atualize a chave em `rm.folders` sem perguntar;
     os artefatos dela aparecem como movidos no passo 2.
   - Identifier que não está em `rm.folders` (pasta nova, inclusive subpasta de uma já baixada) → liste-as e
     pergunte quais entram. As escolhidas vão para `rm.folders` e são buscadas no passo 2 (artefatos = `novo`).
   - Identifier de `rm.folders` que sumiu → a pasta foi apagada; os artefatos dela caem em `removido` no passo 2.
2. **Verificar (só datas):**
   - `rm_list_modified(<ids do sync.md>)` numa chamada (a tool divide em lotes). Para cada id: Última atualização
     ALM = `modified`; id que não voltou → `removido`.
   - `rm_search_requirements(folder=<identifier>)` para cada pasta já baixada (pelo identifier: o nome pode ter
     mudado no passo 1) e cada pasta nova aceita no passo 1. Vieram 1000 → avise que a pasta pode estar truncada (novos podem ficar de fora). Para cada resultado:
     - id fora do `sync.md` → linha `novo` (Generated OKF vazio);
     - id no `sync.md` com `path` diferente do arquivo registrado (título mudou, pasta movida/renomeada ou artefato
       movido entre pastas baixadas) → `pendente`, com a nota `movido` quando a pasta mudou.
   - Id do `sync.md` que voltou em `rm_list_modified` mas não apareceu em nenhuma busca → foi movido para uma pasta
     fora do download: trate como `removido` (nota `fora das pastas baixadas`).
   - Demais: `pendente` se Última atualização ALM > Generated OKF (texto ISO, compare direto); senão `atualizado`.
     Linha `erro` volta a ser `pendente`, para tentar de novo.
3. **Gravar o `sync.md`** com as datas e status novos (`generated` = agora, `by: "process:alm-sync"`).
4. **Mostrar** só o que não está `atualizado`: tabela **Código | Título | Pasta | Última atualização ALM |
   Generated OKF | Status**. Tudo `atualizado` → diga isso e pare (atualize só `rm.download.last-download`).
5. **Confirmar e baixar** `pendente` e `novo`: `rm_get_requirement(id, links="bundle")` → grava como veio em
   `<rm.download.path>/<path>` (`path` da busca do passo 2; caminho mudou → apaga o arquivo antigo, ver
   reference.md) → a linha volta como `atualizado` com o `generated.at` e o `sources[0].last_modified` do arquivo
   novo. Erro → `erro: <mensagem curta>` e segue.
6. **Removidos:** pergunte, por lista, se apaga os arquivos. Apagou → tira a linha do `sync.md`. Manteve → grava
   `status: deprecated` no frontmatter do arquivo e a linha fica `removido`.
7. **Fechar:** `sync.md` final; `pa_*.json` se `rm.folders` mudou; `index.md` regerado se entrou, saiu, mudou de
   nome ou de pasta algum artefato; `log.md` com um `**Update**` por baixado e um `**Deprecation**` por removido;
   `rm.download.last-download` = agora (UTC). Responda com a contagem por status.

## Pedido pontual

"Sincroniza o 2010", "o UC 2010 está atualizado?" → `rm_list_modified(["2010"])`, compare com a linha do
`sync.md` e, se `pendente` (ou se o usuário pediu para baixar), baixe só ele e atualize a linha, `index.md` (se o
nome mudou) e `log.md`. Id fora do `sync.md` → pergunte a pasta (`rm.folders`) e trate como `novo`.

## Regras

- Verificar não baixa conteúdo: só `rm_list_folders`, `rm_list_modified` e `rm_search_requirements`.
  `rm_get_requirement` só para `pendente`/`novo` confirmados.
- Nunca apague arquivo sem confirmação. A confirmação do passo 5 cobre apagar o arquivo antigo de um artefato
  que mudou de caminho (ele foi substituído); diga isso ao pedir a confirmação. Só leitura no ALM.
- Mostre nomes de pasta e tipo, nunca `FR_`/`OT_`.
