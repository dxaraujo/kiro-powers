---
name: "alm-download"
description: "Download the IBM DOORS Next (RM) documentation into the repository as an Open Knowledge Format (OKF) bundle, one Markdown file per artifact, through the `alm` MCP. Use when the user asks to baixar toda a documentação, baixar os requisitos, exportar o RM, baixar a pasta X do RM, gerar a documentação em OKF ou trazer os requisitos para o repositório. To check what changed since the last download and update only that, use alm-sync."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.1"
---

# alm-download

Baixa os artefatos do DOORS Next para `<rm.download.path>/<pasta do RM>/<id>-<slug>.md` e grava `sync.md`,
`index.md` e `log.md`. O formato do bundle está em [reference.md](reference.md): **leia-o antes de gravar**.
Atualizar só o que mudou depois → **alm-sync**. Um artefato só, para ler → **alm-rm**.

## Antes de chamar

1. **Leia `.kiro/config/alm-power/pa_*.json`** (um → use; vários → pergunte). Da seção `rm`: os três parâmetros
   de todas as `rm_*` (`project_area_identifier`, `component`, `configuration`), `rm.folders` e `rm.download`.
   Sem arquivo ou sem `rm` → ofereça a **alm-setup**.
2. Sem `rm.download.path` → pergunte a pasta raiz (sugira `docs/alm`), relativa à raiz do repositório, com `/`, e
   grave `rm.download = {"path": ...}` no `pa_*.json`.
3. Já existe `<path>/sync.md` → avise que há documentação baixada e sugira a **alm-sync** (só o que mudou). Siga
   com o download completo só se o usuário quiser.

## Fluxo

1. **Escopo:** todas as pastas de `rm.folders` ou as que o usuário disser (pelo nome; pasta fora do arquivo →
   alm-setup).
2. **Listar:** por pasta, `rm_search_requirements(folder=rm.folders[<pasta>])` → `[{id, title, type, folder,
   modified, path, url}]`. Vieram 1000 → avise que a pasta pode estar truncada.
3. **Confirmar:** mostre a tabela **Pasta | Artefatos** com o total e a pasta de destino, e peça confirmação.
4. **Baixar:** para cada artefato, `rm_get_requirement(id, links="bundle")` e grave a saída como veio em
   `<rm.download.path>/<path do artefato>` (troca de título: [reference.md](reference.md)). Erro em um artefato não
   para o lote: anote `erro: <mensagem curta>` e siga. Muitos artefatos → informe o progresso por pasta.
5. **Gravar o bundle** (formatos em [reference.md](reference.md)):
   - `sync.md` com uma linha por artefato: Última atualização ALM = `sources[0].last_modified` e Generated OKF =
     `generated.at` do arquivo gravado; status `atualizado` (ou `erro`). Download de só algumas pastas com
     `sync.md` existente → substitua só as linhas dessas pastas.
   - `index.md` regerado; `log.md` com `**Creation**` (primeiro download) ou `**Update**` (pastas baixadas de novo).
   - `rm.download.last-download` = agora, ISO 8601 UTC (`...Z`), no `pa_*.json`.
6. **Responder:** tabela **Pasta | Baixados | Erros** e o caminho de `sync.md`.

## Regras

- Só leitura no ALM. Grava apenas dentro de `<path>` e o `rm.download` do `pa_*.json`.
- Não edite o conteúdo dos artefatos: o arquivo é a saída do MCP. A única exceção é `status: deprecated` da
  alm-sync.
- Mostre nomes de pasta e tipo, nunca `FR_`/`OT_`.
