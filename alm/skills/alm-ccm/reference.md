# alm-ccm — tools genéricas (IBM AI Hub)

Use só quando as `ccm_*` não cobrem: campo fora do alm.json, filtro por data/texto, links entre work items na
criação, schema completo. Retornam o recurso OSLC `{url, id, title, types, properties: {qname: valor},
links: {qname: [{url, title?}]}}`; o `title` do link traz o nome (estado, prioridade, iteração, pessoa).

| Tool | Entrada | Saída |
|---|---|---|
| `get_workitem(workitem_id? \| workitem_oslc_url?, fetch_all=False, gc_uri?)` | um dos dois | recurso. Sem `fetch_all`: tipo, id, título, descrição, responsável, estado, prioridade, severidade. Com `fetch_all`: todos os campos (40+ chaves, caro) e `comments` |
| `search_workitems(project_area_item_id, filter, attributes?, gc_uri?)` | `filter`: **string JSON**; `attributes`: chaves separadas por vírgula (inclua sempre `id,summary`) | `[recurso]` (≤1000) |
| `create_workitem(project_area_id, work_item_type, attributes?, links?)` | `attributes`, `links`: **strings JSON** | recurso criado |
| `get_workitem_schema(project_area_item_id, workitem_type?, include?)` | `include` ⊂ attributes, enumerations, workflows, linkTypes, createMetadata. **Sempre passe o tipo** (sem ele percorre todos, lento) | schema |
| `list_workitem_categories(project_area_item_id, include_archived=False, limit=100, offset=0)` | `limit` ≤ 500 | `[{itemId, name, archived, defaultTeamArea?}]` |
| `list_workitem_releases(...)` | idem | `[{itemId, name, archived}]` |

## Chaves de atributo (search/create)

`id`, `summary`, `description`, `workItemType`, `owner`, `creator`, `created`, `modified`, `tags`,
`internalState`, `internalPriority`, `internalSeverity`, `category`, `target` (planejado para), `foundIn`,
`teamArea`, `projectArea`; ou o `oslc:name` do shape, ou um qname. Chave desconhecida vira `rtc_ext:<chave>`.

Valores: uuid `_...` (category/target/teamArea/foundIn), login ou uuid (owner/creator), literal
(`priority.literal.l01`), id de estado (`com.ibm.team.workitem.taskWorkflow.state.s1`) ou URL.

## `filter` de `search_workitems`

```json
{"operator": "AND", "attributeExpressions": [
  {"attributeId": "target", "operator": "is", "values": ["_<iteração>"]},
  {"attributeId": "summary", "operator": "contains", "values": ["login"]},
  {"attributeId": "modified", "operator": "after", "values": ["2026-01-01T00:00:00Z"]}]}
```

- Operadores: `is`/`equals`, `is not`, `in`, `before`/`after` (ISO), `contains` (só summary/description).
- Só AND. `OR` com uma expressão; "A ou B" no mesmo campo → `in`. Sem `termExpressions`/`similarityExpressions`.
- Erro `Operador OR entre expressões não é suportado` → use `in` ou faça duas buscas.

## `links` de `create_workitem`

`[{"endpointId": "parent", "targetWorkItemId": "1000"}]`. `endpointId`: `parent`, `children`, `related`, `blocks`,
`dependsOn`, `predecessor`, `successor`, `duplicateOf`, `duplicates`, `resolves`, `resolvedBy`.
