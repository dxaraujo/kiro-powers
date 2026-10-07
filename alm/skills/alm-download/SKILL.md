---
name: "alm-download"
description: "Download the IBM DOORS Next (RM) documentation into the repository as an Open Knowledge Format (OKF) bundle, one Markdown file per artifact, through the `alm` MCP. Use when the user asks to baixar toda a documentação, baixar os requisitos, exportar o RM, baixar a pasta X do RM, gerar a documentação em OKF, trazer os requisitos para o repositório ou continuar um download interrompido. To check what changed since the last download and update only that, use alm-sync."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.1.0"
---

# alm-download

Baixa os artefatos do DOORS Next para `<rm.download.path>/<pasta do RM>/<id>-<slug>.md` e grava `sync.md`,
`index.md` e `log.md`. O formato do bundle está em [reference.md](reference.md): **leia-o antes de gravar**.
Atualizar só o que mudou depois → **alm-sync**. Um artefato só, para ler → **alm-rm**.

**Quem grava os artefatos é o MCP** (`rm_download_requirements`): o conteúdo não passa pela conversa. O `sync.md`
é a fila e a memória do download: linha `novo` = falta baixar. Se a sessão cair ou o contexto for compactado,
releia o `sync.md` e siga das linhas `novo`/`erro`.

## Antes de chamar

1. **Leia `.kiro/config/alm-power/pa_*.json`** (um → use; vários → pergunte). Da seção `rm`: os três parâmetros
   de todas as `rm_*` (`project_area_identifier`, `component`, `configuration`), `rm.folders` e `rm.download`.
   Sem arquivo ou sem `rm` → ofereça a **alm-setup**.
2. Sem `rm.download.path` → pergunte a pasta raiz (sugira `docs/alm`), relativa à raiz do repositório, com `/`, e
   grave `rm.download = {"path": ...}` no `pa_*.json`. `dest` das chamadas = caminho **absoluto** dessa pasta
   (raiz do repositório + `path`).
3. Já existe `<path>/sync.md`:
   - com linhas `novo` ou `erro` → é um download interrompido: mostre quantas faltam por pasta e ofereça
     **continuar** (vá direto ao passo 5 do fluxo, só com essas linhas, sem refazer o inventário);
   - sem elas → já há documentação baixada: sugira a **alm-sync**. Siga com o download completo só se o usuário
     quiser.

## Fluxo

1. **Escopo:** todas as pastas de `rm.folders` ou as que o usuário disser (pelo nome; pasta fora do arquivo →
   alm-setup).
2. **Inventário:** por pasta, `rm_count_folder(folder)` e `rm_list_folder(folder)` → `[{id, title, modified}]`
   (só a pasta, sem subpastas, sem teto). `count` ≠ tamanho da lista → avise que a listagem da pasta está
   inconsistente no servidor.
3. **Confirmar:** tabela **Pasta | Artefatos** com o total e a pasta de destino, e peça confirmação.
4. **Gravar a fila:** `sync.md` com uma linha por artefato, status `novo`, Última atualização ALM = `modified`,
   Generated OKF vazio, Artefato sem link (`<id> — <título>`). Download de só algumas pastas com `sync.md`
   existente → substitua só as linhas dessas pastas. Grave antes de baixar o primeiro.
5. **Baixar em blocos de 50 ids**, pasta a pasta, na ordem do `sync.md`:
   `rm_download_requirements(requirement_ids=<bloco>, dest=<absoluto>)` → por id
   `{id, path, last_modified, generated_at, replaced?}` ou `{id, error}`. Depois de **cada** bloco, atualize só as
   linhas dele no `sync.md`: link = `path`, Última atualização ALM = `last_modified`, Generated OKF =
   `generated_at`, status `atualizado`; ou `erro: <mensagem curta>`. Informe `<pasta>: N/total`. Nunca chame
   `rm_get_requirement` nem leia os arquivos gravados.
6. **Fechar** (formatos em [reference.md](reference.md)):
   - `sync.md` com `generated` = agora, `by: "process:alm-download"`;
   - `index.md` regerado (de cada arquivo, leia só o frontmatter: `title`, `description`);
   - `log.md` com `**Creation**` (primeiro download) ou `**Update**` (pastas baixadas de novo);
   - `rm.download.last-download` = agora, ISO 8601 UTC (`...Z`), no `pa_*.json`.
7. **Responder:** tabela **Pasta | Baixados | Erros** e o caminho de `sync.md`. Sobrou `erro` → diga que pedir
   "continuar o download" tenta de novo só esses.

## Regras

- Só leitura no ALM. Grava apenas dentro de `<path>` e o `rm.download` do `pa_*.json`.
- Não edite o conteúdo dos artefatos: o arquivo é o que o MCP gravou. A única exceção é `status: deprecated` da
  alm-sync.
- Mostre nomes de pasta e tipo, nunca `FR_`/`OT_`.
