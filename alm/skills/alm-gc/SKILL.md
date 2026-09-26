---
name: alm-gc
description: Use when the user needs cross-application IBM ELM data through the `alm` MCP — quem sou eu / testar conexão, buscar usuário (login, nome, UUID), listar ou abrir project areas (PA) do CCM/RM/QM/GC, times (team areas), timelines, associações entre EWM, DOORS Next e ETM, configuração global (GC, stream, baseline global) e rastreabilidade (links entre work item, requisito e caso de teste — implementa, afeta, rastreia, valida, testa).
---

# alm-gc

Guia das tools comuns do MCP `alm` (módulo `mcp_alm/ibm/common.py`): usuários, project areas, global
configuration e links de rastreabilidade. As tools específicas estão em **alm-ccm** (work items), **alm-rm**
(requisitos) e **alm-qm** (testes).

## Antes de chamar

1. **Leia `alm/pa_*.json` do projeto** (criado pela skill alm-setup). Ele já tem os UUIDs de project area, times,
   membros, iterações, pastas e tipos. Com ele, **não** chame `list_project_areas`/`get_project_area` só para
   descobrir id.
2. Só descubra ids no servidor quando o arquivo não existir ou não tiver o dado.
3. Mostre ao usuário **nomes**, nunca URLs. A exceção é a coluna de código (veja "Como responder").

## Como responder

Toda lista (usuários, project areas, times, GCs, itens ligados) sai como tabela Código | Título:

| Código | Título |
|---|---|
| 123456 | Corrigir validação do formulário de cadastro |

| Lista | Código (o valor que as tools recebem) | Título |
|---|---|---|
| Usuários (`get_user`, `matching_users`) | `userId` (login) | `name` |
| Project areas / times | `project_area_uuid` / `team_area_uuid` | `name` |
| Configurações globais | id numérico (`gc_config_id`) | `title` |
| `list_linked_*` | id do item ligado (número do work item/requisito, id web do teste), tirado do `title` do link ou do fim da `url` | `title` sem o id |

Em toda lista ou busca, mesmo com um só resultado: **sempre** uma tabela markdown que comece pelas colunas
**Código | Título**, nesta ordem, e nada de lista só com títulos. Pode acrescentar outras colunas úteis que a
tool já devolveu (ex.: estado, responsável, iteração). Sem resultado,
diga "Nenhum item encontrado" e mostre os filtros usados. Ao ler um item só, comece por `**<código>** — <título>`.

## Formato de recurso OSLC

Várias tools devolvem o recurso cru:
`{url, id, title, types: [qname], properties: {qname: valor}, links: {qname: [{url, title?}]}}`.
Chaves em qname (`dcterms:title`, `rtc_cm:state`). `title` do link vem quando o servidor o expõe.

## Usuários

| Tool | Entrada | Saída |
|---|---|---|
| `whoami()` | — | `{userUUID, userId (login), name, emailAddress, archived}`. Testa a conexão |
| `get_user(user_uuid? \| search_term?)` | exatamente um: UUID `'_...'` ou termo ≥3 chars (login ou nome) | 1 achado: mesmo formato de `whoami`. Vários: `{error_message, requires_selection: true, matching_users: [até 5]}` → pergunte ao usuário e chame de novo com `user_uuid` |

- A primeira chamada carrega **todos** os usuários (≈5 s); as seguintes usam cache do processo.
- Nas tools de work item, `owner` aceita o **login** (`<login>`) direto: não chame `get_user` antes.

## Project areas

| Tool | Entrada | Saída |
|---|---|---|
| `list_project_areas(app_type, search_name?, cm_enabled?)` | `app_type`: `"CCM"`, `"RM"`, `"QM"` ou `"GC"`; `search_name` ≥3 chars; `cm_enabled` bool (não vale para GC) | `[{name, project_area_uuid, url, summary, description, cm_enabled}]` ordenado por nome |
| `get_project_area(app_type, project_area_uuid? \| name?, include_team_areas=False, include_timelines=False, include_associations=False)` | exatamente um: uuid ou trecho do nome | `{name, project_area_uuid, summary, description, cm_enabled, team_areas?, timelines?, associations?}`. Vários nomes: `{error_message, requires_selection, matching_project_areas: [{name, project_area_uuid}]}` |

Detalhe dos `include_*` (só peça o que vai usar: cada um é uma requisição a mais):

- `team_areas`: árvore `[{name, team_area_uuid, children: [...]}]`.
- `timelines`: `[{id, label, timeline_uuid, iterations: [{id, label, iteration_uuid, start_date, end_date, children}]}]`.
- `associations`: `{rm|ccm|qm|gc: [{project_area_name, project_area_uuid, link_type}]}`. É o caminho para achar a
  área RM/QM ligada a uma área CCM (ex.: `link_type` `implements`, `tracks-rm`, `tested-by`).

Para times/iterações em lista plana com ids prontos para o alm.json, prefira `ccm_list_team_areas` e
`ccm_list_iterations` (skill alm-setup).

## Global configuration (GC)

| Tool | Entrada | Saída |
|---|---|---|
| `search_global_configuration(gc_project_area_uuid, search_term="*", configuration_type="*")` | uuid da área **GC**; trecho do título; `"Stream"`, `"Baseline"` ou `"*"` | `[{url, title, types, ...}]` |
| `get_global_configuration(gc_config_id)` | id **numérico** (> 0) da GC | recurso OSLC + `contributedConfigs: [{url, title}]` (GCs filhas) e `localConfigs: [{url, title}]` (streams/baselines de rm/qm/ccm) |

A `url` de uma GC serve como `global_configuration_url` (alm-rm) e `gc_uri`/`gc_context`.

## Links de rastreabilidade

Todas recebem **URLs** (a `url` devolvida pelas tools de leitura), não ids.

| Tool | Entrada | Saída |
|---|---|---|
| `list_linked_requirements(source_url)` | URL de work item ou artefato de teste | `[{link_type (qname), url, title?}]` |
| `list_linked_workitems(source_url)` | URL de artefato de teste ou requisito | idem |
| `list_linked_testartifacts(source_url)` | URL de work item ou requisito | idem |
| `link_workitem_and_requirement(workitem_url, requirement_url, link_type="implements")` | `implements`, `affects`, `tracks` (as formas `*by` gravam o mesmo link) | work item atualizado (recurso OSLC) |
| `link_workitem_and_testartifact(workitem_url, testartifact_url, link_type="affects")` | `affects`, `blocks`, `related`, `tests` (+ formas `*by`) | work item atualizado |
| `link_testartifact_and_requirement(testartifact_url, requirement_url, link_type="validates", gc_context?)` | `validates`/`validatedby`; `gc_context` = URL de stream/baseline GC (se omitido, vem do `oslc_config.context` de uma das URLs) | artefato de teste atualizado |

- O link é gravado **no work item** ou **no teste**; o DOORS Next mostra o backlink sozinho. Por isso
  `list_linked_workitems(url de requisito)` pode vir vazio mesmo com link: consulte pelo lado do work item.
- Os links só **acrescentam**; não há tool para remover.
- Mapeamento: implements → `calm:implementsRequirement`, affects → `oslc_cm:affectsRequirement`,
  tracks → `oslc_cm:tracksRequirement`, tests → `oslc_cm:testedByTestCase`, validates →
  `oslc_qm:validatesRequirement`.

## Erros

| Mensagem | O que fazer |
|---|---|
| `Informe exatamente um entre: ...` | Passe só um dos parâmetros alternativos |
| `O termo de busca precisa de ao menos 3 caracteres` | Peça um trecho maior |
| `requires_selection: true` | Não é erro: mostre as opções pelo nome e chame de novo com o uuid |
| `HTTP 401` / falha de login | Credencial em `~/.config/mcp-alm/alm.properties` (veja alm-setup); nunca leia o arquivo |
| `HTTP 403` | O usuário não tem acesso àquela área/app; informe e pare |
