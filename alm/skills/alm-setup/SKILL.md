---
name: alm-setup
description: Use when the user wants to configure, create, update or review the IBM ALM/ELM (EWM, DOORS Next) settings of a project — "configurar o ALM", "setup do ALM", "atualizar o alm.json", trocar project area, times, membros, tipos de work item, iterações, planos, pastas ou tipos de requisito.
---

# alm-setup

Conduz o usuário, em conversa, na criação ou atualização do arquivo de configuração `alm/pa_<nome>.json` do
projeto em que ele está trabalhando (um arquivo por project area do CCM; chamado de "alm.json" no resto deste
texto). `<nome>` = `ccm.project-area` em lower_case e snake_case, sem acentos (ex.: `Gestão de Vendas` → `pa_gestao_de_vendas.json`, `APP MOBILE` → `pa_app_mobile.json`). As skills
alm-ccm e alm-rm leem esse arquivo. Todas as consultas usam as tools do MCP `alm`; o
arquivo é gravado por você, no formato exato abaixo.

## 1. Verificar a conexão

Chame `whoami()` (sem parâmetros). Saída: `{userUUID, userId, name, emailAddress, archived}`.

- **Sucesso:** cumprimente pelo `name` ("Olá, <nome>!") e, dali em diante, trate o usuário pelo
  primeiro nome em todas as mensagens da conversa.

Se der erro:

- **Credencial ausente ou errada** (arquivo não encontrado, falha de login, HTTP 401): peça ao usuário que crie ou
  corrija `~/.config/mcp-alm/alm.properties` (Windows: `%APPDATA%\mcp-alm\alm.properties`, ou o caminho em
  `MCP_ALM_CONFIG`) com:
  ```ini
  [DEFAULT]
  server = https://alm.SEU-SERVIDOR
  user = SEU_USUARIO
  password = SUA_SENHA
  ```
  Nunca leia nem mostre esse arquivo: ele tem a senha. Espere o usuário confirmar e chame de novo.
- **Outro erro:** mostre a mensagem e pare.

## 2. Arquivo existente

Procure `alm/pa_*.json` no projeto.

- **Nenhum:** siga para as etapas e crie um novo.
- **Um:** use-o sem perguntar.
- **Vários:** liste-os pelo `ccm.project-area` de cada um (mais a opção "configurar outra project area") e
  pergunte qual usar.

Com o arquivo escolhido, mostre um resumo (project areas e quantos itens há em cada seção) e pergunte o que fazer:
atualizar tudo, só `ccm`, só `rm`, uma seção específica, ou configurar outra project area (arquivo novo). Refaça só
as etapas dessa escolha e preserve o resto do arquivo.

## 3. Etapas (uma pergunta por vez)

Ofereça sempre as opções que a tool devolveu, mostrando ao usuário só o `name` (label), nunca o identifier/uuid/attribute: ids ficam só nas chamadas e no alm.json. Aqui as opções são uma lista numerada só com o `name`; a regra de tabela Código | Título do power não vale nesta skill. Nunca escolha pelo usuário nem pule uma etapa por achar que "todos"
ou "nenhum" basta. Passe **exatamente** os valores das colunas "Entrada" (ids vêm de saídas anteriores, nunca
nomes) e grave só os campos da coluna "alm.json".

**ccm** (`pa` = `project_area_uuid` escolhido)

| #   | Tool e entrada                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Saída                                                                                                                                                             | alm.json (`ccm.`)                                                                                    |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 1   | `list_project_areas(app_type="CCM")` logo de início, sem perguntar nada antes, e mostre a lista numerada (`name`) para o usuário escolher. Só se ele não achar a dele, peça um trecho do nome e chame de novo com `search_name` (≥3 chars)                                                                                                                                                                                                                              | `[{name, project_area_uuid, url, summary, description, cm_enabled}]`                                                                                              | `project-area` = `name`; `project-area-identifier` = `project_area_uuid`                             |
| 2   | `ccm_list_team_areas(project_area_identifier=pa)`; para cada time escolhido, `list_workitem_categories(project_area_identifier=pa)`                                                                                                                                                                                                                                                                                                                                     | Times: `[{name, identifier, parent}]` (`parent`: `identifier` do time pai ou `null`). Categorias: as que têm `defaultTeamArea.itemId` igual ao identifier do time | `team-areas` `{name: {identifier, categories}}`, em que `categories` é `{nome da categoria: itemId}` |
| 3   | `ccm_list_members(project_area_identifier=pa, team_area_identifiers=[identifier dos times])` (lista não vazia). "Todos" é resposta válida do usuário                                                                                                                                                                                                                                                                                                                    | `[{identifier (login), name, team-areas: [identifier]}]`                                                                                                          | `members` `{identifier: name}`                                                                       |
| 4a  | `ccm_list_workitem_types(project_area_identifier=pa)`                                                                                                                                                                                                                                                                                                                                                                                                                   | `[{identifier, name}]`                                                                                                                                            | `workitem-types` `{name: {identifier, fields}}`                                                      |
| 4b  | Para cada tipo: `ccm_list_workitem_fields(project_area_identifier=pa, workitem_type=identifier do tipo)` (`"task"`, não `"Tarefa"`). `required: true` entra sempre; o campo `Categoria`/`category` entra sempre, mesmo se `required: false`; pergunte os demais opcionais **um tipo por vez** (uma mensagem por tipo, espere a resposta antes de passar ao próximo). Remova o campo `Team Area` (`rtc_cm:teamArea`) dos fields: ele é read-only e derivado da categoria | `[{name, attribute, required: bool, kind}]`                                                                                                                       | `workitem-types[name].fields` `{name: attribute}`, sempre com categoria e sem `rtc_cm:teamArea`      |
| 5a  | `ccm_list_iterations(project_area_identifier=pa)`. Lista longa → pergunte antes um filtro (ano, trecho do nome ou "não terminadas" por `end-date`) e mostre com datas. O usuário escolhe **primeiro** em quais iterações vai trabalhar                                                                                                                                                                                                                                                                                                   | `[{name, identifier, start-date?, end-date?, parent?}]` (datas `AAAA-MM-DD`; nome repetido vem como caminho)                                                      | `iterations` `{name: {identifier, plans}}`                                                           |
| 5b  | Uma única chamada `ccm_list_iteration_plans(project_area_identifier=pa, iteration_identifiers=[identifier de todas as iterações escolhidas])`; agrupe o resultado pelo campo `iteration` e, para **cada** iteração, uma de cada vez, mostre só os planos dela e pergunte quais incluir (uma mensagem por iteração, espere a resposta antes da próxima)                                                                                                                  | `[{name, identifier, team-area, iteration}]` (`team-area`: time dono; `null` se o dono é a própria pa) | `iterations[nome da iteração].plans` `{name: {identifier, team-area?}}` |

**rm** (`pa_rm` = `project_area_uuid` da área RM)

| #   | Tool e entrada                                                                                                                                                                                                                                                                                                                                                   | Saída                                                                                                     | alm.json (`rm.`)                                                     |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1   | `get_project_area(app_type="CCM", project_area_uuid=pa, include_associations=True)` → sugira a de `associations.rm`; confirme ou escolha em `list_project_areas(app_type="RM")`. O `project_area_name` da associação pode diferir do nome real: grave o `name` de `list_project_areas(app_type="RM")`/`get_project_area(app_type="RM", project_area_uuid=pa_rm)` | `{name, project_area_uuid, ..., associations: {rm: [{project_area_name, project_area_uuid, link_type}]}}` | `project-area` = `name` da área RM; `project-area-identifier` = uuid |
| 2   | `rm_get_configuration(project_area_identifier=pa_rm)`. Grave sem perguntar, mas mostre                                                                                                                                                                                                                                                                           | `{component ('_<uuid-componente>'), configuration ('_<uuid-stream>', id da stream)}`                                      | `component`, `configuration`                                         |
| 3   | `rm_list_members(project_area_identifier=pa_rm)`. Proponha os logins escolhidos no ccm e deixe ajustar                                                                                                                                                                                                                                                           | `[{identifier (login), name}]`                                                                            | `members` `{identifier: name}`                                       |
| 4   | `rm_list_folders(project_area_identifier=pa_rm, component=component, configuration=configuration)`                                                                                                                                                                                                                                                               | `[{name (caminho sem "root/"), identifier ('FR_...')}]`                                                   | `folders` `{name: identifier}`                                       |
| 5   | `rm_list_requirement_types(project_area_identifier=pa_rm, component=component, configuration=configuration)`                                                                                                                                                                                                                                                     | `[{name, identifier ('OT_...')}]`                                                                         | `requirements-types` `{name: identifier}`                            |

Tipos: todas as entradas e saídas são strings com o **identifier** (`_...`, `FR_...`, `OT_...` ou o
identifier do tipo, como `task`), nunca URLs: o MCP monta as URLs. `configuration` é o id da stream. Em erro de tipo ou
`LookupError`, mostre a mensagem e refaça a etapa; não invente id.

## 4. Gravar

Mostre o JSON completo, peça confirmação e grave `alm/pa_<nome>.json` na raiz do projeto (se `ccm.project-area`
mudou num arquivo existente, grave com o novo nome e apague o antigo). Formato: todas as seções são
mapas cujas chaves são os `name` devolvidos pelas tools, em kebab-case, sem campos a mais.

O formato exato é definido pelo JSON Schema #[[file:assets/pa.schema.json]]. O arquivo gerado deve validar contra
esse schema; use-o como fonte da verdade sobre campos obrigatórios, prefixos de identifier e o que não pode
aparecer (ex.: `Team Area` nos fields, `team-area: null` ou `iteration` nos planos).

```json
{
  "ccm": {
    "project-area": "<PROJETO>",
    "project-area-identifier": "_<uuid-pa-ccm>",
    "team-areas": {
      "<Equipe>": {
        "identifier": "_<uuid-equipe>",
        "categories": { "<Categoria>": "_<uuid-categoria>" }
      }
    },
    "members": { "<login>": "<Nome do Membro>" },
    "workitem-types": {
      "Tarefa": {
        "identifier": "task",
        "fields": {
          "Categoria": "rtc_cm:category",
          "Atendido por": "rtc_cm:filedAgainst",
          "Planejado para": "rtc_cm:plannedFor"
        }
      }
    },
    "iterations": {
      "<Iteração>": {
        "identifier": "_<uuid-iteração>",
        "plans": {
          "<Plano>": { "identifier": "_<uuid-plano>", "team-area": "_<uuid-equipe>" }
        }
      }
    }
  },
  "rm": {
    "project-area": "<PROJETO>",
    "project-area-identifier": "_<uuid-pa-rm>",
    "component": "_<uuid-componente>",
    "configuration": "_<uuid-stream>",
    "members": { "<login>": "<Nome do Membro>" },
    "folders": { "<Pasta>": "FR_<id>" },
    "requirements-types": { "<Tipo de Requisito>": "OT_<id>" }
  }
}
```

- `fields`: `{name do campo: attribute}`. Não grave `kind`, `required` nem valores: a skill alm-ccm os consulta
  na hora com `ccm_list_field_values`. Não inclua `Team Area` (`rtc_cm:teamArea`): é read-only e derivado da
  categoria. Inclua sempre o campo `Categoria`/`category`, mesmo que a tool o devolva como opcional, pois ele
  define o Team Area correto; use o `attribute` devolvido pela tool.
- `team-areas`: `{name: {identifier, categories}}`. O `identifier` é o UUID do time; `categories` é um mapa
  `{nome da categoria: itemId}` das categorias vinculadas ao time, obtidas de `list_workitem_categories` onde
  `defaultTeamArea.itemId` é igual ao identifier do time. O Team Area do work item é derivado da categoria
  (Atendido por / Filed Against) e não pode ser definido diretamente via OSLC; ao criar um work item, preencha
  apenas `category`.
- `iterations`: `{name: {identifier, plans}}` (as datas servem apenas para o usuário escolher). Não há seção
  `plans` solta: cada plano fica dentro da iteração a que pertence.
- `iterations[nome].plans`: `{name: {identifier, team-area}}`, de `ccm_list_iteration_plans`. Com `team-area`
  `null` (dono é a própria project area), não grave a chave. Não grave `iteration`: é o `identifier` da iteração
  pai. Iteração sem plano escolhido fica com `"plans": {}`.

## 5. Conferir

Depois de gravar (ou alterar) o arquivo, confira o formato contra o JSON Schema #[[file:assets/pa.schema.json]]: releia
o schema e o arquivo gravado e verifique campo a campo que o JSON satisfaz o schema — seções e campos obrigatórios
presentes, sem propriedades a mais, prefixos de identifier corretos (`_`, `FR_`, `OT_`), `team-areas` como
`{nome: {identifier, categories}}`, planos só com `identifier` e, se houver, `team-area` (nunca `null` nem
`iteration`) e nenhum `Team Area`/`rtc_cm:teamArea` nos fields. Se algo não bater, corrija o arquivo e confira de
novo antes de seguir. Esta é uma conferência de estrutura feita por você, sem ferramenta externa.

Em seguida, confirme que os ids funcionam: para cada plano gravado em cada iteração, chame
`ccm_list_workitems(pa, iteration=iteração.identifier, team_areas=[plano.team-area])` (sem `team_areas` se o plano
não tiver `team-area`) e mostre quantos work items vieram. Só leitura: não crie itens de teste.

## Erros comuns

| Erro                                                       | Certo                                                                       |
| ---------------------------------------------------------- | --------------------------------------------------------------------------- |
| Gravar o arquivo no repositório do MCP ou como `alm.json`  | `alm/pa_<nome>.json` na raiz do projeto do usuário                          |
| snake_case, listas, objetos com `uuid`/`url`               | Mapas com chaves em kebab-case, como no exemplo                             |
| Salvar todos os membros, campos ou iterações sem perguntar | Mostrar e deixar o usuário escolher                                         |
| Omitir os planos ou gravá-los numa lista `plans` solta     | Planos dentro de `iterations[nome].plans`, escolhidos por iteração          |
| Gravar `iteration` ou `team-area: null` no plano           | Só `identifier` e, se houver, `team-area`                                   |
| Criar work item de teste                                   | Conferência só com leitura                                                  |
| Tentar definir Team Area diretamente na criação            | Definir apenas `category` (Atendido por); Team Area é derivado da categoria |
| Gravar `team-areas` como `{nome: identifier}`              | Gravar como `{nome: {identifier, categories}}`                              |
| Incluir `rtc_cm:teamArea` nos fields do work item          | Omitir: é read-only, derivado da categoria                                  |
| Omitir `Categoria` por ela ser opcional                    | Incluir sempre `Categoria`/`category`: ela define o Team Area correto       |
