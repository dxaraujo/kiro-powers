---
name: "alm-ccm"
description: "Query, list, read, create, update, change state or comment IBM EWM/RTC (CCM) work items through the `alm` MCP. Use when the user asks about um item de trabalho (work item, WI), tarefa (task, TR, TF), defeito (bug, defect, erro, DF), item de backlog (IB, backlog, story, PBI), dívida técnica (DT), impedimento (IMP), risco (RSC) ou reunião (REU); itens de uma sprint, iteração, plano ou time; estimativa, responsável, prioridade, descrição ou comentário de um WI; \"me mostre o ib:123456\", \"baixar ib 123\", \"tr 456\", \"df 789\", \"minhas tarefas\", \"tarefas de <pessoa>\", \"crie um defeito\", \"mova para Em Desenvolvimento\", \"muda a estimativa para 6h\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.3"
---

# alm-ccm

Work items do EWM pelo MCP `alm`, com as tools `ccm_*`: recebem os ids do `.kiro/config/power/alm/pa_*.json` e devolvem saída
enxuta. As tools genéricas do IBM AI Hub (`get_workitem`, `search_workitems`, `create_workitem`,
`get_workitem_schema`...) estão em [reference.md](reference.md): leia-o **só** se as `ccm_*` não cobrirem o pedido.
Criar iteração/plano é na **alm-setup**; usuários e links com requisitos/testes, na **alm-gc**.

## Antes de chamar

1. **Leia `.kiro/config/power/alm/pa_*.json`** (um → use; vários → pergunte qual). Sem arquivo → regra "Sem setup"
   do steering (abaixo, o que perguntar). Dele saem, sem chamar o servidor (`pa` = `ccm.project-area-identifier`):

   | Preciso de | Onde está |
   |---|---|
   | tipo (`task`, `defect`...) | `workitem-types[nome].identifier` |
   | campos do tipo (nome → attribute) | `workitem-types[nome].fields` |
   | tipos de link (nome → attribute) | `link-types` |
   | iteração / sprint | `iterations[nome].identifier` |
   | plano | `iterations[it].plans[nome]` → `{identifier, team-area?}` |
   | time | `team-areas[nome].identifier` |
   | categoria (Filed Against) | `team-areas[time].categories[nome]` |
   | pessoa (login) | `members` `{login: nome}`; "minhas" = `userId` do `whoami` |

2. Nome que não está no arquivo → não invente: descubra pela linha da tabela "Sem setup" (e sugira mapeá-lo na
   alm-setup).
3. Mostre **nomes** ao usuário, nunca UUIDs/URLs/attributes (exceção: o código do item).

### Sem setup

Pergunte/descubra **só** o que o pedido usa, na ordem em que precisar, e guarde na conversa:

| Preciso de | Como obter (escolha por nome, em lista numerada) |
|---|---|
| `pa` (project area CCM) | Pergunte um trecho do nome → `list_project_areas(app_type="CCM", search_name=<trecho>)`. Ler um item pelo número **só para cabeçalho, descrição e comentários** não precisa: `ccm_get_workitem(id, fields={})`. Se o pedido cita atributos (responsável, estimativa, prioridade...), precisa: pergunte a área e monte `fields` com `ccm_list_workitem_fields` |
| tipo | `ccm_list_workitem_types(pa)` (ou o identifier usual da tabela de siglas) |
| campos do tipo / atributos na leitura | `ccm_list_workitem_fields(pa, <tipo>)`; na leitura, use `{name: attribute}` dos campos que o pedido citar (ou os `required` + responsável, estimativa, iteração) |
| tipos de link | `ccm_list_link_types(pa, <tipo>)`, só os que o pedido citar |
| iteração / sprint | `ccm_list_iterations(pa)` filtrado por trecho do nome ou "não terminadas" |
| plano | `ccm_list_iteration_plans(pa, iteration_identifiers=[<iteração>])` |
| time | `ccm_list_team_areas(pa)` |
| categoria | `list_workitem_categories(project_area_item_id=pa, limit=500)`, filtrada pelo time |
| pessoa | "minhas" = `userId` do `whoami`; outra → `ccm_list_members(pa, team_area_identifiers=[<time>])` ou `get_user` (alm-gc) |

Daqui em diante, onde o texto diz "do alm.json", sem setup vale o que foi descoberto acima nesta conversa.

## Siglas e sinônimos

O termo do usuário indica o **tipo**; o número é o id global do work item ("baixar ib 123456" = WI 123456). O tipo
escolhe o mapa `fields` na leitura e o `workitem_type` ao criar ou filtrar.

| Sigla | Termos do usuário | Tipo (`workitem-types`) | identifier usual |
|---|---|---|---|
| **WI** | work item, item de trabalho, item, workitem | qualquer tipo | — |
| **IB** | item de backlog, backlog, story, user story (no EWM), PBI | Item de Backlog | `com.ibm.team.apt.workItemType.story` |
| **TR** | tarefa, task, tf, tsk, atividade | Tarefa | `task` |
| **DF** | defeito, bug, defect, erro, falha, incidente | Defeito | `defect` |
| **DT** | dívida técnica, débito técnico, tech debt, débito | Dívida Técnica | do alm.json |
| **IMP** | impedimento, impediment, bloqueio | Impedimento | `com.ibm.team.workitem.workItemType.impediment` |
| **RSC** | risco, risk | Risco | `com.ibm.team.workitem.workItemType.risk` |
| **REU** | reunião, retrospectiva, retro, meeting, cerimônia | Reunião | `com.ibm.team.workitem.workItemType.retrospective` |

Reconheça o termo sem diferenciar maiúsculas, acentos, singular/plural ou separador: "ib 123", "IB123",
"ib:123", "ib-123", "item de backlog 123", "os IBs da sprint". Responda sempre com a **sigla canônica** (1ª
coluna). Termo que não está aqui nem em `workitem-types` → pergunte o tipo; não adivinhe.

- O identifier válido é o do alm.json (sem setup, o de `ccm_list_workitem_types`); a coluna "usual" é só referência.
- **"História"/"HU" é do RM** (alm-rm), não IB. Só trate como IB se o usuário disser "story" ou "item de backlog",
  ou se falar de sprint/plano/backlog do EWM; na dúvida, pergunte.
- Siglas de outras skills: requisitos (REQ, HU, UC, RN...) → **alm-rm**; testes (CT, PT, TER...) → **alm-qm**.

## Como responder

- **Listas** (mesmo com um resultado): tabela markdown que começa por **Código | Título** (`id` | `title`); pode
  acrescentar colunas que a tool já devolveu (tipo, estado, responsável, iteração). Sem resultado: "Nenhum item
  encontrado" + os filtros usados. Vieram **1000** itens → avise que a lista pode estar truncada e sugira filtrar
  mais (estado, tipo, time).
- **Um item:** comece por `**<código>** — <título>` e mostre o documento de `ccm_get_workitem` como veio, sem a
  linha `url` (ela serve às tools de link da alm-gc, não ao usuário).

## Tools

`resumo` = `{id, title, type, state, owner (login ou "unassigned"), iteration, url}`.

| Tool | Entrada | Saída |
|---|---|---|
| `ccm_list_workitems(project_area_identifier, iteration?, team_areas?, owner?, state?, workitem_type?)` | ≥1 de `iteration` (id), `team_areas` ([ids], inclui subtimes), `owner` (login). `state` = **nome** ("Novo"); `workitem_type` = identifier | `[resumo]` (≤1000, sem aviso de corte) |
| `ccm_get_workitem(workitem_id, fields, link_types?)` | `fields` = `workitem-types[tipo].fields`; `link_types` = `link-types` | Markdown + YAML (abaixo) |
| `ccm_list_field_values(project_area_identifier, workitem_type, attribute)` | attribute do mapa `fields` | `{kind, required, values: [{identifier, name, default}]}`; `values` vazio para text/integer/date/member |
| `ccm_create_workitem(project_area_identifier, workitem_type, summary, description?, fields?, parent?)` | `description` em Markdown; `fields` `{attribute: valor}`; `parent` = id do pai | `resumo` |
| `ccm_update_workitem(workitem_id, fields?, description?, state?)` | `description` **substitui** a inteira; `state` = **nome** do estado destino (a tool acha a ação e confere a mudança) | `resumo` |
| `ccm_list_workitem_states(workitem_id)` | — | `{state, actions: [{name, result-state}]}` |
| `add_comment_to_workitem(workitem_id, comment, mentions?)` | `mentions` = logins (viram `@login`) | comentário |

### Leitura (`ccm_get_workitem`)

```markdown
---
id: 1001
type: Tarefa
title: Implementar cadastro de clientes
state: Em Desenvolvimento
url: "https://alm.example.com/ccm/resource/itemName/com.ibm.team.workitem.WorkItem/1001"
attributes:
  Responsável: Bruno Lima
  Estimativa: "4h"
links:
  Pai:
    - "1000: Épico de cadastro"
---
<descrição em Markdown>

## Comentários
**bruno.lima · 2026-01-12 14:30**
Iniciado.
```

- `attributes`/`links` trazem só os campos de `fields` e os links de `link_types`, com os nomes do alm.json. Campo
  vazio é omitido. Datas em Brasília (`AAAA-MM-DD HH:MM`).
- Tipo do item desconhecido: use o mapa da sigla (ou o do tipo mais comum) e confira o `type` do cabeçalho; se for
  outro tipo do alm.json, chame **uma** vez de novo com o mapa certo.
- O `url` do cabeçalho é o que as tools de link da alm-gc recebem.

### Gravação: do nome lido para o valor gravado

`fields` usa o **attribute** como chave. Ache-o no mesmo mapa da leitura: `workitem-types[tipo].fields["Estimativa"]`
→ `rtc_cm:estimate`. O valor depende do `kind`:

| kind | Valor em `fields` | Origem (sem chamada, quando possível) |
|---|---|---|
| category | uuid `_...` | `team-areas[time].categories[nome]` |
| iteration | uuid `_...` | `iterations[nome].identifier` |
| member | **login** (a leitura mostra o nome) | `members` |
| enumeration, release, team-area | `identifier` | `ccm_list_field_values` (mostre os `name`; sugira `default: true`) |
| duração (estimativa) | **ms** (a leitura mostra `4h`): `h × 3600000` | — |
| text, integer, date, boolean | literal (`AAAA-MM-DD` para data) | usuário |

Exemplo — "muda a estimativa do WI 1001 para 6h": `fields["Estimativa"]` → `rtc_cm:estimate`; confirme;
`ccm_update_workitem("1001", fields={"rtc_cm:estimate": 21600000})`.

### Descrição (Markdown)

- O EWM só guarda texto, `<br/>`, negrito, itálico e links: títulos viram negrito, listas viram linhas `• `/`1. `
  e sublistas saem planas. Escreva parágrafos e listas simples.
- Alterar: leia com `ccm_get_workitem`, edite o corpo **sem** o cabeçalho YAML e **sem** `## Comentários`, e mande o
  corpo inteiro (substitui o atual). Ler → gravar → ler não muda o texto.
- Citar outro WI: escreva o tipo e o número ("Tarefa 1002"); o EWM cria sozinho o link "Menções". Não há embed.

## Fluxos

- **Itens de um plano:** `ccm_list_workitems(pa, iteration=iterations[it].identifier,
  team_areas=[plano["team-area"]])`; plano sem `team-area` → omita `team_areas`. É **uma** chamada.
- **Minhas / de alguém:** `owner=<login>` (+ `iteration` se citada).
- **Filtro de estado:** `state` aceita **um** nome, por igualdade. Um estado ("os Novos") → passe na tool.
  Negação ou vários estados ("abertas", "não concluídas", "Novo ou Em Andamento") → chame **sem** `state` e filtre
  o resultado pela coluna `state`; não faça uma chamada por estado. "Abertas" = estado diferente dos finais do
  workflow (Concluído, Fechado, Resolvido, Cancelado...); na dúvida sobre quais são finais, pergunte.
  `workitem_type` vai sempre na tool.
- **Ler:** `ccm_get_workitem(id, fields, link_types)`. Precisa de campo fora do alm.json → `get_workitem(fetch_all=True)`
  ([reference.md](reference.md)) e sugira mapear o campo na alm-setup.
- **Criar:**
  1. Tipo pelo alm.json. Para cada campo do mapa `fields` que seja obrigatório ou que o usuário citou, resolva o
     valor pela tabela acima. Só chame `ccm_list_field_values` para kinds que não estão no alm.json — e uma vez
     por attribute, não para conferir o que o arquivo já tem.
  2. A categoria define o time do item (não dá para escolher o time direto): use uma categoria do time desejado.
  3. Mostre o resumo (por nomes) e peça confirmação. Depois `ccm_create_workitem(...)` e responda com código,
     título e url.
- **Atualizar / mudar estado:** confirme e chame `ccm_update_workitem(id, fields?, description?, state="<nome>")`;
  campos e estado podem ir na mesma chamada. Erro de estado → `ccm_list_workitem_states(id)` e ofereça os
  `result-state`.
- **Comentar:** `add_comment_to_workitem(id, comment, mentions=[logins])`.
- **Links entre work items** (pai, filho, relacionado, bloqueia...): o MCP só grava **na criação** —
  `ccm_create_workitem(..., parent=<id do pai>)` ou, para outros tipos, `create_workitem(..., links=...)`
  ([reference.md](reference.md)). **Não há tool para ligar dois work items que já existem** nem para remover link:
  diga isso ao usuário e oriente a fazer na UI web do EWM. Não tente por `fields` nem por `description` (citar
  "Tarefa 1002" na descrição cria só o link "Menções", não pai/filho). Links com requisitos e testes → alm-gc.

## Erros

| Mensagem (trecho) | O que fazer |
|---|---|
| `Informe ao menos um filtro` | Use iteração/plano, time ou login do alm.json |
| `Tipo 'x' não existe` / `Atributo 'x' não existe no tipo` | Identifier do tipo (`task`, não `Tarefa`) e attribute do alm.json |
| `Estado 'x' não existe no workflow. Estados: ...` | Mostre os estados listados e pergunte |
| `O servidor não mudou o estado` | Transição não sai do estado atual ou exige campo: mostre `ccm_list_workitem_states` |
| HTTP 403 `o atributo X precisa ser preenchido` | O processo exige o campo para salvar: peça o valor e repita com ele em `fields` |
| HTTP 403 / `Permission Denied` (outros) | Falta permissão no processo: informe e pare |
| HTTP 400/409 ao criar | Faltou obrigatório ou valor inválido: confira com `ccm_list_field_values` |
| HTTP 412 | Edição concorrente: releia o item e repita **uma** vez |
| `O servidor aceitou, mas ... não apareceu` | Peça para conferir na UI; não repita às cegas |

## Regras

- **Confirme toda escrita** (criar, atualizar, mudar estado, comentar) com um resumo por nomes: é visível ao time e
  não há desfazer pelo MCP. Uma escrita por vez; confirme ao usuário pelo `resumo` devolvido.
- Nunca invente identifiers, literais de enumeração ou logins.
- Não crie work items para "testar" algo: use leitura.
