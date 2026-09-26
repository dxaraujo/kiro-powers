---
name: alm-rm
description: Use when the user asks about IBM DOORS Next (RM) artifacts through the `alm` MCP — consultar, buscar, listar, criar ou atualizar um requisito (REQ, RF, RNF), história de usuário (HU, HF, HNF), caso de uso (UC), regra (RN, REG), mensagem (MSG), especificação técnica (ET), especificação de leiaute (EL), protótipo (PRT), diagrama (DG), termo de glossário (GL), imagem (IMG) ou documento de visão (DV); pastas, tipos de artefato, componentes, streams e baselines do RM; "me mostre o requisito 123456", "me mostre o uc 123456", "baixar hu 123", "requisitos da pasta 01-Requisitos", "crie uma HU".
---

# alm-rm

Guia das tools de requisitos (DOORS Next/RM) do MCP `alm`. Há dois grupos:

- **`rm_*`** (`mcp_alm/rm.py`): usam os ids do `alm/pa_*.json` e devolvem saída enxuta, com atributos e
  valores pelo **nome**. **Prefira estas.**
- **Genéricas** (`mcp_alm/ibm/requirements.py`, nomes do IBM Engineering AI Hub): URLs e recurso OSLC cru.
  Use para baselines, change sets, configuração global ou outra project area fora do alm.json.

Links com work items e testes e configuração global estão em **alm-gc**.

## Siglas

"uc 123456", "uc:123456" ou "baixar hu 123456" = requisito de `id` 123456. O número é global: leia com
`rm_get_requirement(requirement_id="123456")` qualquer que seja a sigla, e use a sigla só para conferir o `type`
ou para criar/filtrar (tipo em `rm.requirements-types` e, em geral, pasta em `rm.folders`).

| Sigla | Tipo (`rm.requirements-types`) |
|---|---|
| **REQ**, RF, RNF | Requisito |
| **HU**, HF, HNF | História de Usuário |
| **UC** | Caso de Uso |
| **RN**, REG | Regra |
| **MSG** | Mensagem |
| **ET** | Especificação Técnica |
| **EL** | Especificação de Leiaute |
| **PRT** | Protótipo |
| **DG** | Diagrama |
| **GL** | Termos de Glossário |
| **IMG** | Imagem |
| **DV** | Documento de Visão |

**PT** é Plano de Teste (alm-qm), não Protótipo. Siglas de work item (IB, TR, DF...) estão em **alm-ccm**.

## Antes de chamar

1. **Leia `alm/pa_*.json`** (vários → pergunte qual; um → use). A seção `rm` tem tudo que as tools `rm_*` pedem:
   `project-area-identifier`, `component`, `configuration` (stream), `folders` (`{caminho: 'FR_...'}`),
   `requirements-types` (`{nome: 'OT_...'}`) e `members`.
2. Sem o arquivo, sugira a skill **alm-setup**.
3. Mostre ao usuário nomes de tipo e pasta, nunca `FR_`/`OT_`/URLs. A exceção é o código do requisito (veja
   "Como responder").

## Como responder

Listas e buscas de requisitos (`rm_search_requirements`, `search_requirement`, requisitos de uma pasta, links):

| Código | Título |
|---|---|
| 123456 | UC01 - Cadastrar usuário |

`Código` = `id` numérico do requisito (o mesmo que vai em `rm_get_requirement(requirement_id=...)`); `Título` =
`title`.

Em toda lista ou busca, mesmo com um só resultado: **sempre** uma tabela markdown que comece pelas colunas
**Código | Título**, nesta ordem, e nada de lista só com títulos. Pode acrescentar outras colunas úteis que a
tool já devolveu (ex.: estado, responsável, iteração). Sem resultado,
diga "Nenhum item encontrado" e mostre os filtros usados. Ao ler um item só, comece por `**<código>** — <título>`.

## Tools `rm_*` (preferidas)

Parâmetros fixos em todas: `project_area_identifier`, `component`, `configuration` (valores do alm.json).

| Tool | Entrada extra | Saída |
|---|---|---|
| `rm_search_requirements(..., text?, folder?, requirement_type?)` | ao menos um: `text` (busca no título/corpo), `folder` (`FR_...`), `requirement_type` (`OT_...`); combinados com "e" | `[{id, title, type (nome), folder (nome), url}]` (até 1000) |
| `rm_get_requirement(..., requirement_id)` | id numérico (string) | `{id, title, type, folder, text (texto sem marcação), attributes: {nome do atributo: valor}, links: {qname: [{url, title?}]}, url}` |
| `rm_create_requirement(..., requirement_type, folder, title, text, attributes?)` | `OT_...`, `FR_...`; `text`: texto ou XHTML; `attributes`: `{nome: valor}` (enumeração pelo nome) | `{id, title, url}` |
| `rm_update_requirement(..., requirement_id, title?, text?, attributes?)` | ao menos um dos três | `{id, title, url}` |

- `rm_search_requirements` exige ao menos um filtro (texto, pasta ou tipo). Prefira pasta e/ou tipo do alm.json;
  a busca só por texto varre o componente inteiro e pode levar vários segundos.
- Para saber os atributos válidos de um tipo, envie o nome: em erro a mensagem lista os válidos e, para
  enumeração, os valores. Não é preciso consultar o schema antes.
- Para ligar a um work item: `link_workitem_and_requirement(workitem_url, requirement_url)` (alm-gc), com a
  `url` devolvida aqui.

## Tools genéricas

Recurso OSLC: `{url, id, title, types, properties: {qname: valor}, links: {qname: [{url, title?}]}}`.
Texto do requisito em `properties["jazz_rm:primaryText"]`; pasta em `links["nav:parent"]`.

| Tool | Entrada | Saída |
|---|---|---|
| `get_project_components(project_area, component_id?)` | título exato ou UUID da área RM | `[recurso do componente]` |
| `get_rm_component_configuration(project_area_uuid, component_id, configuration_type="all")` | `stream`, `baseline`, `changeset` ou `all` | `[{url, title, types}]` (1 requisição por configuração) |
| `get_rm_component_types(project_area_uuid, component_id, configuration_url?)` | — | `[{url (…/types/OT_...), title, describes, properties: [{name, title, predicate, required, value_type, allowed_values, default, ...}]}]` |
| `list_rm_component_folders(component_url, configuration_url?)` | URLs | `[{url (…/folders/FR_...), title, parent (url ou None na raiz), ...}]` (1 query por pasta) |
| `get_requirement(project_area_uuid, component_id, requirement_id, configuration_url?, global_configuration_url?)` | id numérico; uma configuração no máximo | recurso OSLC |
| `search_requirement(project_area_uuid, component_id, search_text, configuration_url?, global_configuration_url?)` | texto | `[recurso resumido]` (**até 100**) |
| `create_requirement(project_area_url, component_url, artifact_type_url, title, description, primary_text, configuration_url?, folder_url?, global_configuration_url?)` | tudo em URL; `folder_url` de pasta (`FR_`), nunca módulo (`MD_`) | recurso criado |

- Sem configuração, as genéricas usam a primeira stream do componente.
- `create_requirement` recusa baseline: só stream ou change set.

## Erros

| Mensagem | O que fazer |
|---|---|
| `Atributo 'x' não existe no tipo. Válidos: ...` | Mostre os válidos pelo nome e pergunte |
| `Valor 'x' inválido para 'y'. Válidos: ...` | Idem |
| `requirement_id deve ser numérico` | Use `rm_search_requirements(text=...)` para buscar por texto |
| `Informe ao menos um filtro` | Pergunte a pasta, o tipo ou um texto |
| `Requisito N não encontrado` | Confira a stream (`configuration`) e o componente |
| `folder_url é um módulo (MD_)` | Use uma pasta de `rm.folders` |
| `Não é possível criar requisito em baseline` | Use a stream do alm.json |

Não crie requisitos de teste para "verificar" algo: use leitura.
