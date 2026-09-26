---
name: alm-ccm
description: Use when the user asks about IBM EWM/RTC (CCM) work items through the `alm` MCP — consultar, listar, buscar, criar, atualizar, mudar o estado ou comentar um item de trabalho (work item, WI), tarefa (task), defeito (bug, defect), item de backlog (IB, story), tarefa (TR), defeito (DF), dívida técnica (DT), impedimento (IMP), risco (RSC) ou reunião (REU); itens de uma sprint, iteração ou plano; "me mostre o ib:123456", "baixar ib 123", "tr 456", "df 789", "tarefas de <pessoa>", "crie um defeito", "mova para Em Desenvolvimento".
---

# alm-ccm

Guia das tools de work item (EWM/CCM) do MCP `alm`. Há dois grupos:

- **`ccm_*`** (`mcp_alm/ccm.py`): usam os ids do `alm/pa_*.json` e devolvem saída enxuta. **Prefira estas.**
- **Genéricas** (`mcp_alm/ibm/workitems.py`, nomes do IBM Engineering AI Hub): recurso OSLC completo, filtros
  livres. Use quando precisar de algo que as `ccm_*` não cobrem.

Usuários, project areas e links com requisitos/testes estão em **alm-gc**.

## Siglas

"ib 123456", "ib:123456", "baixar ib 123456" ou "tarefa 123456" = work item de número 123456. O número é global:
leia com `get_workitem(workitem_id="123456")` qualquer que seja a sigla, e use a sigla só para conferir o tipo
(`properties.dcterms:type`) ou para criar/filtrar. "Baixar"/"abrir"/"me mostre" = ler (`fetch_all=True` se pedir
detalhes, comentários ou links).

| Sigla | Tipo (`workitem-types`) | identifier |
|---|---|---|
| **IB** | Item de Backlog | `com.ibm.team.apt.workItemType.story` |
| **TR**, TAREFA | Tarefa | `task` |
| **DF**, BUG | Defeito | `defect` |
| **DT** | Dívida Técnica | — |
| **IMP** | Impedimento | `com.ibm.team.workitem.workItemType.impediment` |
| **RSC** | Risco | `com.ibm.team.workitem.workItemType.risk` |
| **REU** | Reunião | `com.ibm.team.workitem.workItemType.retrospective` |
| **WI** | qualquer work item | — |

Sem identifier na tabela (tipo customizado): use `workitem-types["<nome>"].identifier` do `pa_*.json`; se não
estiver lá, rode a alm-setup para incluir o tipo.

Siglas de requisito (UC, HU, RN...) estão em **alm-rm**; de teste (CT, PT, TER...) em **alm-qm**.

## Antes de chamar

1. **Leia `alm/pa_*.json`** (vários → pergunte qual; um → use). Dele saem, sem consultar o servidor:
   `ccm.project-area-identifier` (pa), `team-areas`, `members` (logins), `workitem-types[nome].identifier`
   (`task`, `defect`...), `workitem-types[nome].fields` (`{nome do campo: attribute}`), `iterations` (cada uma com seus `plans`).
2. Sem o arquivo, sugira a skill **alm-setup** antes de sair descobrindo ids.
3. Mostre ao usuário **nomes** (estado, iteração, pessoa), nunca URLs/UUIDs. A exceção é o código do item (veja
   "Como responder").

## Como responder

Listas e buscas de work items (`ccm_list_workitems`, `search_workitems`, itens de plano, filhos, links):

| Código | Título |
|---|---|
| 123456 | Corrigir validação do formulário de cadastro |

`Código` = `id` numérico do work item (o mesmo que vai em `get_workitem(workitem_id=...)`); `Título` = `title`.
Em `search_workitems`, inclua sempre `id,summary` em `attributes`, senão a tabela fica sem código.

Em toda lista ou busca, mesmo com um só resultado: **sempre** uma tabela markdown que comece pelas colunas
**Código | Título**, nesta ordem, e nada de lista só com títulos. Pode acrescentar outras colunas úteis que a
tool já devolveu (ex.: estado, responsável, iteração). Sem resultado,
diga "Nenhum item encontrado" e mostre os filtros usados. Ao ler um item só, comece por `**<código>** — <título>`.

## Tools `ccm_*` (preferidas)

Saída comum de work item (`resumo`): `{id, title, type, state, owner (login ou "unassigned"), iteration, url}`.

| Tool | Entrada | Saída |
|---|---|---|
| `ccm_list_workitems(project_area_identifier, iteration?, team_areas?, owner?, state?, workitem_type?)` | ao menos um entre `iteration` (id), `team_areas` ([ids], inclui subtimes) e `owner` (login). `state`: **nome** (`"Novo"`). `workitem_type`: identifier (`"task"`) | `[resumo]` (até 1000) |
| `ccm_list_field_values(project_area_identifier, workitem_type, attribute)` | `attribute` = valor de `fields` no alm.json (`"rtc_cm:filedAgainst"`) | `{kind, required, values: [{identifier, name, default}]}`. `values` vazio para text/integer/date/member |
| `ccm_create_workitem(project_area_identifier, workitem_type, summary, description?, fields?, parent?)` | `fields`: `{attribute: identifier de ccm_list_field_values ou valor}`; membro = login; `parent`: id do pai | `resumo` do item criado |
| `ccm_list_workitem_states(workitem_id)` | id numérico (string) | `{state, actions: [{name, result-state}]}` |
| `ccm_update_workitem(workitem_id, fields?, state?)` | `fields` como no create; `state`: **nome** do estado destino (`"Em Desenvolvimento"`) | `resumo` atualizado |

Fluxos:

- **Itens de um plano:** ache o plano em `iterations[iteração].plans[nome]` e chame
  `ccm_list_workitems(pa, iteration=iterations[iteração].identifier, team_areas=[plano.team-area])`.
  Se o plano não tiver `team-area` (dono é a própria pa), omita `team_areas`. Itens da iteração sem o time do plano não aparecem.
- **Criar:** para cada campo obrigatório do tipo no alm.json, chame `ccm_list_field_values` **só** para os de
  kind category/iteration/team-area/release/enumeration, mostre os `name`, e passe o `identifier` escolhido.
  Iteração e time também podem vir direto do alm.json (`iterations[nome].identifier`, `team-areas[nome].identifier`).
- **Mudar estado:** passe `state` pelo nome em `ccm_update_workitem`; ele escolhe a ação. Se falhar, a mensagem
  lista os estados válidos. `ccm_list_workitem_states` só é necessário para mostrar as opções ao usuário.

## Tools genéricas

Retornam o recurso OSLC `{url, id, title, types, properties: {qname: valor}, links: {qname: [{url, title?}]}}`.
O `title` de cada link traz o nome (estado "Novo", prioridade "Alta", iteração, pessoa).

| Tool | Entrada | Saída |
|---|---|---|
| `get_workitem(workitem_id? \| workitem_oslc_url?, fetch_all=False, gc_uri?)` | um dos dois; `project_area_id` é ignorado | recurso. Sem `fetch_all`: tipo (`properties.dcterms:type`), id, título, descrição, responsável (`links.dcterms:contributor`), estado (`links.rtc_cm:state`), prioridade, severidade, modificação. Com `fetch_all`: todos os campos e links + `comments: [recurso]` |
| `search_workitems(project_area_item_id, filter, attributes?, gc_uri?)` | `filter`: **string JSON** (abaixo); `attributes`: chaves separadas por vírgula | `[recurso]` (até 1000), só com os campos pedidos |
| `create_workitem(project_area_id, work_item_type, attributes?, links?)` | `attributes`: string JSON `{chave: valor}`; `links`: string JSON `[{endpointId, targetWorkItemId}]` | recurso criado |
| `add_comment_to_workitem(workitem_id, comment, mentions?)` | `mentions`: logins, viram `@login` no início | recurso do comentário |
| `get_workitem_schema(project_area_item_id, workitem_type?, include?)` | `include` ⊂ `attributes`, `enumerations`, `workflows`, `linkTypes`, `createMetadata` (este exige `workitem_type`); padrão `["attributes","enumerations"]` | `{projectAreaId, workItemTypes: [{id, title, attributes?: [{id, name, predicate, valueType, required, readOnly}], enumerations?: {nome: [{id, url, title}]}, workflows?: {states, actions}, linkTypes?, createMetadata?: {requiredProperties}}]}` |
| `list_workitem_categories(project_area_item_id, include_archived=False, limit=100, offset=0)` | `limit` 1–500 | `[{itemId, name, archived}]` |
| `list_workitem_releases(...)` | idem | `[{itemId, name, archived}]` |

`get_workitem_schema` sem `workitem_type` percorre **todos** os tipos (lento). Sempre passe o tipo.

### Chaves de atributo (search/create)

`id`, `summary`, `description`, `workItemType`, `owner`, `creator`, `created`, `modified`, `tags`,
`internalState`, `internalPriority`, `internalSeverity`, `category` (Atendido por), `target` (Planejado para),
`foundIn`, `teamArea`, `projectArea`. Também aceitam o `oslc:name` do shape ou um qname (`rtc_cm:plannedFor`);
chave desconhecida vira `rtc_ext:<chave>` (atributo custom).

Valores: UUID `_...` para category/target/teamArea/foundIn; login ou UUID para owner/creator; literal de
enumeração (`priority.literal.l01`); id de estado (`com.ibm.team.workitem.taskWorkflow.state.s1`); ou URL.

### filter de `search_workitems`

```json
{"operator": "AND", "attributeExpressions": [
  {"attributeId": "target", "operator": "is", "values": ["<identifier-da-iteração>"]},
  {"attributeId": "owner", "operator": "is", "values": ["<login>"]},
  {"attributeId": "summary", "operator": "contains", "values": ["login"]},
  {"attributeId": "modified", "operator": "after", "values": ["2026-01-01T00:00:00Z"]}]}
```

- Operadores: `is`/`equals`, `is not`, `in` (vários valores), `before`/`after` (datas ISO), `contains` (só
  `summary`/`description`, busca textual).
- `OR` só com uma expressão; para "A ou B" no mesmo campo use `in`.
- Não suportados: `termExpressions`, `similarityExpressions`.

### links de `create_workitem`

`endpointId`: `parent`, `children`, `related`, `blocks`, `dependsOn`, `predecessor`, `successor`, `duplicateOf`,
`duplicates`, `resolves`, `resolvedBy`. `targetWorkItemId`: número do outro work item.

## Erros

| Mensagem | O que fazer |
|---|---|
| `Informe ao menos um filtro: iteration, team_areas (time) ou owner` | Use o plano ou o login do alm.json |
| `Atributo 'x' não existe no tipo 'y'` | Use o attribute do alm.json e o identifier do tipo (`task`, não `Tarefa`) |
| `Estado 'x' não existe no workflow. Estados: ...` | Mostre os estados listados e pergunte |
| `O servidor não mudou o estado` | A transição não parte do estado atual; mostre `ccm_list_workitem_states` |
| HTTP 400/409 ao criar | Faltou campo obrigatório ou valor inválido; confira `required` em `ccm_list_field_values` |
| `Operador OR entre expressões não é suportado` | Troque por `in` ou faça duas buscas |

Não crie work items de teste para "verificar" algo: use leitura.
