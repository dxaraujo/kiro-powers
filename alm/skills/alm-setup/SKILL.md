---
name: "alm-setup"
description: "Configure, create, update or review the IBM ALM/ELM (EWM, DOORS Next, ETM) settings of a project in .kiro/config/alm-power/pa_<nome>.json, and create iterations or iteration plans. Use when the user says \"configurar o ALM\", \"setup do ALM\", \"atualizar o alm.json\", \"falta o campo/link/iteração X no alm.json\", \"criar sprint/iteração\", \"criar plano (Kanban, Backlog)\", or wants to change project area, times, categorias, membros, tipos de work item, campos, tipos de link, iterações, planos, pastas, tipos de requisito ou a área de testes."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.1"
---

# alm-setup

Conduz o usuário, em conversa, na criação ou atualização de `.kiro/config/alm-power/pa_<nome>.json` (o "alm.json"): a memória das
skills alm-ccm, alm-rm e alm-qm. Ele guarda nomes → identifiers já descobertos para que as outras skills não
consultem o servidor a cada pedido. `<nome>` = `ccm.project-area` em snake_case minúsculo, sem acentos
(`Gestão de Vendas` → `pa_gestao_de_vendas.json`). O MCP não lê esse arquivo: você o grava, no formato exato abaixo.

## 1. Verificar a conexão

`whoami()` → `{userUUID, userId, name, emailAddress, archived}`. Cumprimente pelo `name` e, dali em diante, trate o
usuário pelo primeiro nome.

Erro de credencial (`Arquivo de credenciais não encontrado`, `Chave(s) ausente(s)`, `Falha de login`, HTTP 401):
peça ao usuário que crie ou corrija `~/.config/mcp-alm/alm.properties` (Windows: `%APPDATA%\mcp-alm\alm.properties`,
ou o caminho em `MCP_ALM_CONFIG`) e o proteja com `chmod 600`:

```ini
[DEFAULT]
server = https://alm.SEU-SERVIDOR
user = SEU_USUARIO
password = SUA_SENHA
```

`server` sem barra final e sem context root. CA corporativa: `REQUESTS_CA_BUNDLE`. **Nunca leia nem mostre esse
arquivo** (tem a senha). Espere o usuário confirmar e chame `whoami` de novo. Outro erro: mostre a mensagem e pare.

## 2. Arquivo existente

Procure `.kiro/config/alm-power/pa_*.json` no projeto do usuário.

- **Nenhum:** faça todas as etapas.
- **Um:** use-o sem perguntar. **Vários:** liste pelo `ccm.project-area` (+ "configurar outra project area") e
  pergunte.

Com o arquivo escolhido, mostre um resumo (quantos itens há em cada seção) e pergunte o que fazer: tudo, só `ccm`,
só `rm`, só `qm`, uma seção (ex.: só `link-types`, só iterações) ou outra project area. Refaça só essas etapas e
preserve o resto. Pedido pontual vindo de outra skill ("falta o campo Severidade") → vá direto à etapa dele.

## 3. Etapas (uma pergunta por vez)

Mostre ao usuário só o `name` das opções, em lista numerada; identifiers ficam só nas chamadas e no arquivo. Nunca
escolha pelo usuário nem pule uma etapa por achar que "todos" ou "nenhum" basta. Passe **exatamente** os valores da
coluna "Entrada" (ids vêm de saídas anteriores, nunca nomes) e grave só o que diz a coluna "alm.json".

**ccm** (`pa` = `project_area_uuid` escolhido)

| # | Tool e entrada | Saída | alm.json (`ccm.`) |
|---|---|---|---|
| 1 | `list_project_areas(app_type="CCM")` logo de início, sem perguntar nada. Se o usuário não achar a dele, peça um trecho (≥3) e repita com `search_name` | `[{name, project_area_uuid, ...}]` | `project-area` = `name`; `project-area-identifier` = `project_area_uuid` |
| 2 | `ccm_list_team_areas(project_area_identifier=pa)`; mostre a árvore (via `parent`) e pergunte os times. Depois **uma** chamada `list_workitem_categories(project_area_item_id=pa, limit=500)` e distribua as categorias pelos times | Times: `[{name, identifier, parent}]`. Categorias: `[{itemId, name, archived, defaultTeamArea?}]` | `team-areas` `{name: {identifier, categories}}`; `categories` = `{name: itemId}` das não arquivadas com `defaultTeamArea.itemId` == identifier do time |
| 3 | `ccm_list_members(project_area_identifier=pa, team_area_identifiers=[ids dos times])` (≥1). "Todos" é resposta válida | `[{identifier (login), name, team-areas}]` | `members` `{login: name}` |
| 4a | `ccm_list_workitem_types(project_area_identifier=pa)`; pergunte quais tipos | `[{identifier, name}]` | `workitem-types` `{name: {identifier, fields}}` |
| 4b | Para cada tipo, **um por vez**: `ccm_list_workitem_fields(project_area_identifier=pa, workitem_type=<identifier>)` (`"task"`, não `"Tarefa"`). Entram sempre: os `required: true` e a categoria (`rtc_cm:filedAgainst`). Sugira os úteis no dia a dia (responsável `dcterms:contributor`, planejado para `rtc_cm:plannedFor`, estimativa `rtc_cm:estimate`, prioridade, severidade) e pergunte os demais. Nunca inclua `rtc_cm:teamArea` | `[{name, attribute, required, kind}]` | `workitem-types[name].fields` `{nome: attribute}` |
| 4c | `ccm_list_link_types(project_area_identifier=pa, workitem_type=<qualquer tipo escolhido>)`; pergunte quais o projeto usa (sugira pai, filhos, implementa requisito, menções) | `[{name, attribute}]` | `link-types` `{nome: attribute}` |
| 5a | `ccm_list_iterations(project_area_identifier=pa)`. Lista longa → pergunte antes um filtro (ano, trecho do nome ou "não terminadas" por `end-date`) e mostre com datas. O usuário escolhe as iterações | `[{name, identifier, start-date?, end-date?, parent?}]` | `iterations` `{name: {identifier, plans}}` |
| 5b | **Uma** chamada `ccm_list_iteration_plans(project_area_identifier=pa, iteration_identifiers=[todas as escolhidas])`; agrupe por `iteration` e pergunte os planos de cada iteração, uma por vez | `[{name, identifier, team-area, iteration}]` | `iterations[it].plans` `{name: {identifier, team-area?}}` |

**Nomes de `fields` e `link-types` são do projeto**: proponha o `name` da tool em português (ex.: "Filed Against" →
"Categoria", "Parent" → "Pai") e deixe o usuário ajustar. `ccm_get_workitem` mostra campos e links com esses nomes,
e a alm-ccm os usa para achar o attribute na gravação.

**rm** (`pa_rm` = uuid da área RM)

| # | Tool e entrada | Saída | alm.json (`rm.`) |
|---|---|---|---|
| 1 | `get_project_area(app_type="CCM", project_area_uuid=pa, include_associations=True)` → sugira a de `associations.rm`; confirme ou escolha em `list_project_areas(app_type="RM")`. Grave o `name` real da área RM (o `project_area_name` da associação pode diferir). **Guarde `associations.qm`** para a etapa qm | `{..., associations: {rm, qm, ...: [{project_area_name, project_area_uuid, link_type}]}}` | `project-area`, `project-area-identifier` |
| 2 | `rm_get_configuration(project_area_identifier=pa_rm)`. Grave sem perguntar, mas mostre | `{component, configuration}` (primeiro componente, primeira stream) | `component`, `configuration` |
| 3 | `rm_list_members(project_area_identifier=pa_rm)`. Proponha os logins escolhidos no ccm | `[{identifier, name}]` | `members` `{login: name}` |
| 4 | `rm_list_folders(project_area_identifier=pa_rm, component, configuration)` | `[{name ('01-Req/Funcionais'), identifier ('FR_...')}]` | `folders` `{name: identifier}` |
| 5 | `rm_list_requirement_types(project_area_identifier=pa_rm, component, configuration)` | `[{name, identifier ('OT_...')}]` | `requirements-types` `{name: identifier}` |

O RM não guarda campos nem links: `rm_get_requirement` mostra os nomes do DOORS Next e a gravação usa os mesmos.

**qm** (opcional): com o `associations.qm` da etapa rm 1, confirme com
`get_project_area(app_type="QM", project_area_uuid=<uuid>)`. Achou → grave `qm.project-area` (`name`) e
`qm.project-area-identifier`. Sem associação, ou erro de catálogo/403 → o projeto não usa o ETM: omita `qm`.

Tipos: entradas e saídas são **identifiers** (`_...`, `FR_...`, `OT_...`, `task`), nunca URLs. Em erro ou
`LookupError`, mostre a mensagem e refaça a etapa; não invente id.

## 4. Gravar

Mostre o JSON completo, peça confirmação e grave `.kiro/config/alm-power/pa_<nome>.json` no projeto do usuário (se
`ccm.project-area` mudou, grave com o novo nome e apague o antigo). O formato é definido pelo JSON Schema
#[[file:assets/pa.schema.json]] (fonte da verdade). `$schema` é sempre a **primeira** propriedade:

```json
{
  "$schema": "https://raw.githubusercontent.com/dxaraujo/kiro-powers/main/alm/skills/alm-setup/assets/pa.schema.json",
  "ccm": {
    "project-area": "<PROJETO>",
    "project-area-identifier": "_<uuid-pa-ccm>",
    "team-areas": {
      "<Equipe>": { "identifier": "_<uuid-equipe>", "categories": { "<Categoria>": "_<uuid-categoria>" } }
    },
    "members": { "<login>": "<Nome do Membro>" },
    "workitem-types": {
      "Tarefa": {
        "identifier": "task",
        "fields": {
          "Categoria": "rtc_cm:filedAgainst",
          "Planejado para": "rtc_cm:plannedFor",
          "Responsável": "dcterms:contributor",
          "Estimativa": "rtc_cm:estimate"
        }
      }
    },
    "link-types": {
      "Pai": "rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.parent",
      "Filhos": "rtc_cm:com.ibm.team.workitem.linktype.parentworkitem.children",
      "Implementa requisito": "oslc_cm:implementsRequirement"
    },
    "iterations": {
      "<Iteração>": {
        "identifier": "_<uuid-iteração>",
        "plans": { "<Plano>": { "identifier": "_<uuid-plano>", "team-area": "_<uuid-equipe>" } }
      }
    }
  },
  "rm": {
    "project-area": "<PROJETO RM>",
    "project-area-identifier": "_<uuid-pa-rm>",
    "component": "_<uuid-componente>",
    "configuration": "_<uuid-stream>",
    "members": { "<login>": "<Nome do Membro>" },
    "folders": { "<Pasta>": "FR_<id>" },
    "requirements-types": { "<Tipo de Requisito>": "OT_<id>" }
  },
  "qm": {
    "project-area": "<PROJETO QM>",
    "project-area-identifier": "_<uuid-pa-qm>"
  }
}
```

- `fields`: só `{nome: attribute}`; nada de `kind`, `required` ou valores (a alm-ccm os consulta na hora).
- Plano: só `identifier` e, se não for `null`, `team-area`; nunca `iteration`. Iteração sem plano: `"plans": {}`.
- O arquivo não tem segredos: pode ir para o git do projeto, para o time todo usar.

## 5. Conferir

1. **Estrutura:** releia o schema e o arquivo gravado e confira campo a campo: `$schema` primeiro, obrigatórios
   presentes, nada a mais, prefixos (`_`, `FR_`, `OT_`), categoria presente e `rtc_cm:teamArea` ausente em cada
   tipo, planos sem `null`/`iteration`. Corrija e confira de novo se algo não bater.
2. **Ids:** para cada plano gravado, `ccm_list_workitems(pa, iteration=<it>.identifier, team_areas=[plano.team-area])`
   (sem `team_areas` se o plano não tiver time) e mostre quantos itens vieram. Só leitura.

## Criar iteração ou plano (só quando pedido)

Mostre o resumo e peça confirmação antes. Depois de criar, inclua o item em `iterations` do alm.json (etapa 5).

- **Iteração:** `ccm_create_iteration(project_area_identifier=pa, parent=<identifier da iteração/timeline pai>,
  name, start_date, end_date?, iteration_id?, iteration_type?)`. Datas `AAAA-MM-DD` (fuso de Brasília).
- **Plano:** `ccm_create_iteration_plan(project_area_identifier=pa, name, iteration=<identifier>, plan_type,
  team_area?)`. Pergunte o tipo pelo nome e passe o id:

  | Mostrar | `plan_type` |
  |---|---|
  | Quadro de tarefas Kanban | `com.ibm.team.apt.plantype.kanbanBoard` |
  | Backlog do Produto | `com.ibm.team.apt.plantype.product.backlog` |

  Omita `team_area` para o plano ser da própria project area. O servidor pode normalizar o tipo conforme o
  processo; se o usuário questionar, confira com `ccm_list_iteration_plans`.
- Essas tools usam serviços internos da UI web: `HTTP 403`/`Permission Denied` = o usuário não tem a permissão de
  processo ("Modify structures of iterations" / planos). Informe e pare; **não tente variações** do payload.

## Erros comuns

| Erro | Certo |
|---|---|
| Gravar no repositório do MCP ou como `alm.json` | `.kiro/config/alm-power/pa_<nome>.json` no projeto do usuário |
| Listas ou objetos com `uuid`/`url` | Mapas com chaves em kebab-case, como no exemplo |
| Salvar tudo sem perguntar | Mostrar e deixar o usuário escolher |
| `list_workitem_categories` uma vez por time | Uma chamada com `limit=500` e filtrar por `defaultTeamArea.itemId` |
| `Categoria` → `rtc_cm:category`, ou omitir a categoria | `Categoria` → `rtc_cm:filedAgainst`, sempre presente: ela define o time do work item |
| `rtc_cm:teamArea` nos fields | Omitir: read-only, derivado da categoria |
| Planos numa lista `plans` solta, com `iteration` ou `team-area: null` | Dentro de `iterations[nome].plans`, só `identifier` (+ `team-area`) |
| Membro novo não aparece em `ccm_list_members` | O MCP carrega os usuários uma vez por processo: peça para reiniciar o cliente |
| Criar work item ou plano para "testar" | Conferência só com leitura |
