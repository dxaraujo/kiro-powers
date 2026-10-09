---
name: "alm-qm"
description: "Query, search or list IBM ETM/RQM (QM) test artifacts through the `alm` MCP (read-only). Use when the user asks about caso de teste (CT, TC, test case), plano de teste (PT, test plan), suíte de teste (ST), script de teste (SCT), registro de execução (TER, execution record), resultado de teste (RT, resultado de execução), atributos/schema de artefato de teste, componentes, streams e baselines do QM; \"me mostre o caso de teste 123\", \"baixar ct 123\", \"pt 45\", \"casos de teste de <pessoa>\", \"planos de teste da PA\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.2"
---

# alm-qm

Guia das tools de teste (ETM/RQM/QM) do MCP `alm` (`mcp_alm/ibm/test.py`, nomes do IBM Engineering AI Hub).
Não há tools de criação/edição de artefato de teste: só leitura. Links com requisitos e work items
(`link_testartifact_and_requirement`, `link_workitem_and_testartifact`, `list_linked_*`) estão em **alm-gc**.

## Siglas e sinônimos

O termo do usuário define o `artifact_type`; o número é o **id web** (`oslc:shortId`), único só dentro do tipo
("ct 123" = `get_testartifact(pa_qm, "TestCase", id="123")`).

| Sigla | Termos do usuário | Tipo | `artifact_type` |
|---|---|---|---|
| **CT** | caso de teste, test case, TC, cenário de teste | Caso de Teste | `TestCase` |
| **PT** | plano de teste, test plan, TP | Plano de Teste | `TestPlan` |
| **ST** | suíte de teste, suíte, test suite, TS | Suíte de Teste | `TestSuite` |
| **SCT** | script de teste, script, test script, roteiro de teste | Script de Teste | `TestScript` |
| **TER** | registro de execução, execution record, ER | Registro de Execução | `TestCaseExecutionRecord` |
| **RT** | resultado de teste, resultado de execução, test result | Resultado de Teste | `TestCaseResult` |
| — | registro de execução de suíte | Registro de Execução de Suíte | `TestSuiteExecutionRecord` |
| — | resultado de suíte | Resultado de Suíte | `TestSuiteResult` |

Reconheça o termo sem diferenciar maiúsculas, acentos, singular/plural ou separador: "ct 123", "CT123",
"ct:123", "ct-123", "caso de teste 123", "os CTs do plano". Responda sempre com a **sigla canônica** (1ª
coluna). Termo que não está aqui nem em `artifact_type` → pergunte o tipo; não adivinhe.

- **PT** aqui é Plano de Teste; Protótipo é **PRT** (alm-rm). "Teste 123" sem tipo → pergunte (CT, PT...), pois o
  id só é único dentro do tipo.

## Antes de chamar

1. **Leia `.kiro/config/power/alm/pa_*.json`**: `pa_qm` = `qm.project-area-identifier`, sem chamar o servidor.
   Sem a seção `qm`, descubra a área uma vez pela associação da área CCM:
   `get_project_area(app_type="CCM", project_area_uuid=ccm.project-area-identifier, include_associations=True)`
   → `associations.qm[0].project_area_uuid`, e sugira a **alm-setup** para gravá-la. Não liste todas as áreas QM.
   Sem associação, ou erro de catálogo/403 → o projeto não tem testes no ETM: diga isso e pare.
   **Sem setup** (sem arquivo; regra do steering): área CCM já escolhida na conversa → use a associação acima; senão
   pergunte um trecho do nome do projeto → `list_project_areas(app_type="QM", search_name=<trecho>)` e o usuário
   escolhe pelo nome. Guarde `pa_qm` na conversa. Pessoa (`owner`) → login dito pelo usuário ou `get_user` (alm-gc).
2. `configuration` é opcional: só passe se o usuário pedir uma stream/baseline específica.
3. Mostre nomes e ids web, nunca URLs (veja "Como responder").

## Como responder

Listas e buscas de artefatos de teste (`search_testartifact`, links):

| Código | Título |
|---|---|
| 123 | CT - Cadastrar usuário com e-mail válido |

`Código` = id web (`oslc:shortId`, o mesmo que vai em `get_testartifact(..., id=...)`); `Título` = `title`. Como
o id só é único dentro do tipo, se a lista misturar tipos use a sigla no código (`CT 123`, `PT 45`).

Em toda lista ou busca, mesmo com um só resultado: **sempre** uma tabela markdown que comece pelas colunas
**Código | Título**, nesta ordem, e nada de lista só com títulos. Pode acrescentar outras colunas úteis que a
tool já devolveu (ex.: estado, responsável, iteração). Sem resultado,
diga "Nenhum item encontrado" e mostre os filtros usados. Ao ler um item só, comece por `**<código>** — <título>`.

## artifact_type

`TestPlan`, `TestCase`, `TestSuite`, `TestScript`, `TestCaseExecutionRecord`, `TestCaseResult`,
`TestSuiteExecutionRecord`, `TestSuiteResult` (exatamente assim; outro valor dá erro).

## Tools

Recurso OSLC: `{url, id, title, types, properties: {qname: valor}, links: {qname: [{url, title?}]}}`.

| Tool | Entrada | Saída |
|---|---|---|
| `search_testartifact(project_area_uuid, artifact_type, filters?, properties?, configuration?)` | `filters`: `{campo: valor}` (igualdade, combinados com "e"); `properties`: lista de campos a devolver | `[recurso]` (até 1000). Padrão: id, título, modificação, tipo |
| `get_testartifact(project_area_uuid, artifact_type, id? \| url?, fetch_all=False, configuration?)` | um dos dois: id web ou URL | recurso. Sem `fetch_all`: título, `oslc:shortId`, responsável (`links.dcterms:contributor`), modificação. Com `fetch_all`: todos os campos e links |
| `get_testartifact_schema(project_area_uuid, artifact_type)` | — | `{artifactType, shapes: [{url, title, describes, properties: [{name, title, predicate, required, value_type, allowed_values, default, ...}]}]}` (inclui atributos custom, categorias, estados, prioridades) |
| `get_qm_component(project_area_uuid, component_name?, component_uuid?)` | trecho do nome e/ou UUID | `[{url, id, title, ...}]` |
| `get_qm_component_configuration(project_area_uuid, component_uuid?, configuration_name?, configuration_type?, configuration_uuid?)` | `configuration_type`: `Stream` ou `Baseline` | `[{url, title, types, component}]` |

Campos de `filters`/`properties`: `title` (ou `name`), `id` (id web), `owner`, `creator`, `created`,
`modified`, `description`, ou um qname (`dcterms:title`). `owner`/`creator` recebem a **URL** do usuário
(`https://<servidor>/jts/users/<login>`).

Não suportados em `search_testartifact`: `customAttributeFilters`, `categoryFilters`, `linkFilters`. Para filtrar por
categoria ou atributo custom, peça `properties` com o campo e filtre o resultado.

`configuration` aceita UUID (`_...`) ou URL da configuração local do ETM.

## Fluxos

- **Casos de teste de alguém:** `search_testartifact(pa_qm, "TestCase", filters={"owner":
  "https://<servidor>/jts/users/<login>"})`; o servidor sai do `url` de qualquer recurso já lido, e o login, de
  `members` do alm.json.
- **CT pelo número:** `get_testartifact(pa_qm, "TestCase", id="123")`. Se for precisar de passos, categorias ou
  links, já chame com `fetch_all=True` (evita uma segunda leitura).
- **Requisitos que um CT valida:** `list_linked_requirements(url do CT)` (alm-gc).

## Erros

| Mensagem | O que fazer |
|---|---|
| `artifact_type inválido` | Use um dos 8 valores acima |
| `Informe id ou url (um dos dois)` | Passe só um |
| `{tipo} N não encontrado` | Confira o id web e o tipo (CT ≠ PT) |
| `Project area _x não está no catálogo 'oslc' de /qm` | O projeto não usa QM (ou o usuário não tem acesso); informe e pare |
| `HTTP 403` | Sem permissão no ETM; informe e pare (não tente outras áreas) |
| `Campo desconhecido` | Use as chaves acima ou um qname |
