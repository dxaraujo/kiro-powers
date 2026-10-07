---
name: "alm-sync"
description: "Synchronize the IBM DOORS Next (RM) documentation previously downloaded as an Open Knowledge Format (OKF) bundle by alm-download: compare the last modification in the ALM with the date each OKF file was generated, mark pending, new and removed artifacts in sync.md and download again only what changed, through the `alm` MCP. Use when the user asks to sincronizar a documentação, o que mudou no ALM, atualizar os requisitos baixados, verificar se a documentação está atualizada ou sincronizar o requisito 123."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.1"
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

1. **Verificar (só datas):**
   - `rm_list_modified(<ids do sync.md>)` numa chamada (a tool divide em lotes). Para cada id: Última atualização
     ALM = `modified`; id que não voltou → `removido`.
   - Novos: `rm_search_requirements(folder=rm.folders[<pasta>])` para cada pasta do `sync.md`; id que não está no
     `sync.md` → linha `novo` (Generated OKF vazio). Pasta que o usuário nunca baixou não entra.
   - Demais: `pendente` se Última atualização ALM > Generated OKF (texto ISO, compare direto); senão `atualizado`.
     Linha `erro` volta a ser `pendente`, para tentar de novo.
2. **Gravar o `sync.md`** com as datas e status novos (`generated` = agora, `by: "process:alm-sync"`).
3. **Mostrar** só o que não está `atualizado`: tabela **Código | Título | Pasta | Última atualização ALM |
   Generated OKF | Status**. Tudo `atualizado` → diga isso e pare (atualize só `rm.download.last-download`).
4. **Confirmar e baixar** `pendente` e `novo`: `rm_get_requirement(id, links="bundle")` → grava como veio em
   `<rm.download.path>/<path>` (`path` da busca do passo 1, que já reflete título novo; troca de título:
   reference.md) → a linha volta como `atualizado` com o `generated.at` e o `sources[0].last_modified` do arquivo
   novo. Erro → `erro: <mensagem curta>` e segue.
5. **Removidos:** pergunte, por lista, se apaga os arquivos. Apagou → tira a linha do `sync.md`. Manteve → grava
   `status: deprecated` no frontmatter do arquivo e a linha fica `removido`.
6. **Fechar:** `sync.md` final; `index.md` regerado se entrou, saiu ou mudou de nome algum artefato; `log.md` com
   um `**Update**` por baixado e um `**Deprecation**` por removido; `rm.download.last-download` = agora (UTC).
   Responda com a contagem por status.

## Pedido pontual

"Sincroniza o 2010", "o UC 2010 está atualizado?" → `rm_list_modified(["2010"])`, compare com a linha do
`sync.md` e, se `pendente` (ou se o usuário pediu para baixar), baixe só ele e atualize a linha, `index.md` (se o
nome mudou) e `log.md`. Id fora do `sync.md` → pergunte a pasta (`rm.folders`) e trate como `novo`.

## Regras

- Verificar não baixa conteúdo: só `rm_list_modified` e `rm_search_requirements`. `rm_get_requirement` só para
  `pendente`/`novo` confirmados.
- Nunca apague arquivo sem confirmação. Só leitura no ALM.
- Mostre nomes de pasta e tipo, nunca `FR_`/`OT_`.
