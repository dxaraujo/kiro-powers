# alm-rm — tools genéricas (IBM AI Hub)

Use só para o que as `rm_*` não cobrem: baseline, change set, configuração global, outro componente ou project area
fora do alm.json. Trabalham com **URLs** e devolvem o recurso OSLC `{url, id, title, types, properties: {qname:
valor}, links: {qname: [{url, title?}]}}`. Texto em `properties["jazz_rm:primaryText"]` (XHTML); pasta em
`links["nav:parent"]`. Sem configuração, usam a primeira stream do componente.

| Tool | Entrada | Saída |
|---|---|---|
| `get_project_components(project_area, component_id?)` | título exato ou uuid da área RM | `[componente]` |
| `get_rm_component_configuration(project_area_uuid, component_id, configuration_type="all")` | `stream`, `baseline`, `changeset`, `all` | `[{url, title, types}]` |
| `get_rm_component_types(project_area_uuid, component_id, configuration_url?)` | — | `[{url (…/OT_...), title, properties: [{name, predicate, required, value_type, allowed_values, ...}]}]` |
| `list_rm_component_folders(component_url, configuration_url?)` | URLs | `[{url (…/FR_...), title, parent}]` (1 query por pasta: lento) |
| `get_requirement(project_area_uuid, component_id, requirement_id, configuration_url? \| global_configuration_url?)` | id numérico; no máximo uma configuração | recurso |
| `search_requirement(project_area_uuid, component_id, search_text, configuration_url?, global_configuration_url?)` | texto | `[recurso]` (**≤100**) |
| `create_requirement(project_area_url, component_url, artifact_type_url, title, description, primary_text, configuration_url?, folder_url?, global_configuration_url?)` | tudo em URL; pasta `FR_`, nunca módulo `MD_` | recurso |

- Ler um requisito numa **baseline**: `get_rm_component_configuration(..., "baseline")` → `url` da baseline →
  `get_requirement(..., configuration_url=<url>)`.
- `global_configuration_url`: a `url` de uma GC (alm-gc, `search_global_configuration`).
- `create_requirement` recusa baseline (`Não é possível criar requisito em baseline`) e módulo (`folder_url é um
  módulo (MD_)`).
