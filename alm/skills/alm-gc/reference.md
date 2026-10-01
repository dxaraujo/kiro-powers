# alm-gc — referência

Project areas em detalhe, configuração global (GC), formato do recurso OSLC e qnames dos links. Para o dia a dia
(usuários e rastreabilidade), o SKILL.md basta.

## Recurso OSLC

Várias tools devolvem o recurso cru:
`{url, id, title, types: [qname], properties: {qname: valor}, links: {qname: [{url, title?}]}}`.
Chaves em qname (`dcterms:title`, `rtc_cm:state`); o `title` do link vem quando o servidor o expõe.

## Project areas

| Tool | Entrada | Saída |
|---|---|---|
| `list_project_areas(app_type, search_name?, cm_enabled?)` | `app_type`: `CCM`, `RM`, `QM`, `GC`; `search_name` ≥3; `cm_enabled` (não vale para GC) | `[{name, project_area_uuid, url, summary, description, cm_enabled}]`, por nome |
| `get_project_area(app_type, project_area_uuid? \| name?, include_team_areas=False, include_timelines=False, include_associations=False)` | exatamente um: uuid ou trecho do nome | `{name, project_area_uuid, summary, description, cm_enabled, team_areas?, timelines?, associations?}`. Vários nomes: `{requires_selection, matching_project_areas: [{name, project_area_uuid}]}` |

`include_*`: peça só o que vai usar (cada um é uma requisição a mais).

- `team_areas`: árvore `[{name, team_area_uuid, children: [...]}]`.
- `timelines`: `[{id, label, timeline_uuid, iterations: [{id, label, iteration_uuid, start_date, end_date, children}]}]`.
- `associations`: `{rm|ccm|qm|gc: [{project_area_name, project_area_uuid, link_type}]}`. É o caminho para achar a
  área RM/QM ligada a uma área CCM (`link_type` como `implements`, `tracks-rm`, `tested-by`). O
  `project_area_name` pode diferir do nome real: confirme com `get_project_area` no app de destino.

Times e iterações em lista plana, com ids prontos para o alm.json: `ccm_list_team_areas` e `ccm_list_iterations`
(alm-setup).

## Configuração global (GC)

| Tool | Entrada | Saída |
|---|---|---|
| `search_global_configuration(gc_project_area_uuid, search_term="*", configuration_type="*")` | uuid da área **GC** (`list_project_areas(app_type="GC")`); trecho do título; `Stream`, `Baseline` ou `*` | `[{url, title, types, ...}]` |
| `get_global_configuration(gc_config_id)` | id **numérico** (> 0), o fim da `url` da GC | recurso + `contributedConfigs: [{url, title}]` (GCs filhas) e `localConfigs: [{url, title}]` (streams/baselines de rm, qm, ccm) |

A `url` de uma GC é o valor de:

| Parâmetro | Tool | Skill |
|---|---|---|
| `global_configuration_url` | `get_requirement`, `search_requirement`, `create_requirement` | alm-rm (reference.md) |
| `gc_uri` | `get_workitem`, `search_workitems` | alm-ccm (reference.md) |
| `gc_context` | `link_testartifact_and_requirement` | alm-gc |

**Exemplo — "o que compõe a baseline global Release 2.0?":**

```text
list_project_areas(app_type="GC")                                     → uuid da área GC
search_global_configuration(<uuid>, "Release 2.0", "Baseline")        → url .../gc/configuration/42
get_global_configuration(42)                                          → localConfigs (streams/baselines RM, QM, CCM)
```

Responda com a tabela Código | Título das `localConfigs`, com uma coluna App (rm/qm/ccm, pela `url`).

## qnames dos links de rastreabilidade

`list_linked_*` devolve `link_type` em qname. Traduza para o usuário:

| `link_type` | Mostrar |
|---|---|
| `calm:implementsRequirement` | implementa |
| `oslc_cm:affectsRequirement` | afeta |
| `oslc_cm:tracksRequirement` | rastreia |
| `oslc_cm:testedByTestCase` | testado por |
| `oslc_qm:validatesRequirement` | valida |
