---
name: "alm-gc"
description: "Access cross-application IBM ELM data through the `alm` MCP: users, project areas, global configuration and traceability links. Use when the user needs quem sou eu / testar conexão, buscar usuário (login, nome, UUID), listar ou abrir project areas (PA) do CCM/RM/QM/GC, times (team areas), timelines, associações entre EWM, DOORS Next e ETM, configuração global (GC, stream, baseline global) e rastreabilidade (links entre work item, requisito e caso de teste — implementa, afeta, rastreia, valida, testa; \"o que está ligado a\", \"liga o WI ao requisito\")."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.1"
---

# alm-gc

Tools comuns do MCP `alm`: usuários, rastreabilidade entre apps, project areas e configuração global. Work items →
**alm-ccm**; requisitos (inclusive links entre requisitos) → **alm-rm**; testes → **alm-qm**.

Project areas em detalhe (`include_*`, associações), configuração global (GC), formato do recurso OSLC e qnames dos
links estão em [reference.md](reference.md): leia-o **só** quando o pedido for sobre isso.

## Antes de chamar

1. **Leia `.kiro/config/power/alm/pa_*.json`**: já tem os uuids de project area (ccm, rm, qm), times, membros e iterações. Com ele,
   **não** chame `list_project_areas`/`get_project_area` só para descobrir id.
2. Descubra no servidor só o que o arquivo não tem; se for algo recorrente, sugira a **alm-setup**.
3. Mostre **nomes**, nunca URLs/uuids (exceção: a coluna Código).

## Como responder

Toda lista sai como tabela markdown que começa por **Código | Título**, mesmo com um resultado; pode acrescentar
colunas que a tool já devolveu. Sem resultado: "Nenhum item encontrado" + filtros. Um item só: `**<código>** —
<título>`.

| Lista | Código | Título |
|---|---|---|
| Usuários (`get_user`, `matching_users`) | `userId` (login) | `name` |
| Project areas / times | `project_area_uuid` / `team_area_uuid` | `name` |
| Configurações globais | id numérico (`gc_config_id`) | `title` |
| `list_linked_*` | id do item ligado (número do WI/requisito, id web do teste), do `title` do link ou do fim da `url` | `title` sem o id; acrescente a coluna **Link** com o `link_type` traduzido (implementa, afeta, valida...) |

## Usuários

| Tool | Entrada | Saída |
|---|---|---|
| `whoami()` | — | `{userUUID, userId (login), name, emailAddress, archived}`. Testa a conexão |
| `get_user(user_uuid? \| search_term?)` | exatamente um: uuid `_...` ou termo ≥3 (login ou nome) | 1 achado: como `whoami`. Vários: `{requires_selection: true, matching_users: [≤5]}` → pergunte e repita com `user_uuid` |

- Pessoa do projeto → `members` do alm.json (`{login: nome}`), sem chamada. `get_user` só para quem não está lá.
- As tools de work item recebem o **login** direto: não chame `get_user` antes.
- A primeira `get_user` carrega todos os usuários (≈5 s) e fica em cache no processo: usuário novo só aparece
  depois de reiniciar o cliente.

## Rastreabilidade

Todas recebem **URLs**, não ids. Pegue sem chamada extra: `url` das listas (`ccm_list_workitems`,
`rm_search_requirements`, `search_testartifact`) ou do cabeçalho YAML de `ccm_get_workitem`/`rm_get_requirement`.

| Tool | Entrada | Saída |
|---|---|---|
| `list_linked_requirements(source_url)` | URL de work item ou teste | `[{link_type, url, title?}]` |
| `list_linked_workitems(source_url)` | URL de requisito ou teste | idem |
| `list_linked_testartifacts(source_url)` | URL de work item ou requisito | idem |
| `link_workitem_and_requirement(workitem_url, requirement_url, link_type="implements")` | `implements`, `affects`, `tracks` (formas `*by` gravam o mesmo) | work item atualizado |
| `link_workitem_and_testartifact(workitem_url, testartifact_url, link_type="affects")` | `affects`, `blocks`, `related`, `tests` (+ `*by`) | work item atualizado |
| `link_testartifact_and_requirement(testartifact_url, requirement_url, link_type="validates", gc_context?)` | `validates`/`validatedby`; `gc_context` = URL da GC se o ETM usar configurações | teste atualizado |

Escolha do `link_type` pelo pedido:

| Pedido | Tool e `link_type` |
|---|---|
| "o WI implementa / atende o requisito" | `link_workitem_and_requirement`, `implements` |
| "o defeito afeta o requisito" | `link_workitem_and_requirement`, `affects` |
| "o WI rastreia / acompanha o requisito" | `link_workitem_and_requirement`, `tracks` |
| "o CT valida / cobre o requisito" | `link_testartifact_and_requirement`, `validates` |
| "o WI é testado pelo CT" | `link_workitem_and_testartifact`, `tests` |
| "o defeito afeta / bloqueia o teste" | `link_workitem_and_testartifact`, `affects` / `blocks` |

- O link é gravado **no work item** ou **no teste**; o DOORS Next mostra o backlink. Por isso
  `list_linked_workitems(url de requisito)` pode vir vazio mesmo havendo link: consulte pelo lado do work item ou
  do teste antes de afirmar que não há.
- As tools só **acrescentam**: não há como remover pelo MCP. Antes de ligar, liste os links existentes para não
  duplicar e **confirme** mostrando `<código> — <título>` dos dois lados e o tipo do link.

**Exemplo — "liga o TR 1234 ao REQ 2001 como implementa":**

```text
ccm_get_workitem("1234", fields, link_types) → cabeçalho url (WI)
rm_get_requirement("2001")                   → cabeçalho url (requisito)
list_linked_requirements(<url do WI>)        → 2001 ainda não está ligado
(confirmação: "TR 1234 — <título> implementa REQ 2001 — <título>?")
link_workitem_and_requirement(<url do WI>, <url do requisito>, "implements")
```

Se a conversa já trouxe as URLs (listas, leituras anteriores), não leia de novo.

## Erros

| Mensagem | O que fazer |
|---|---|
| `Informe exatamente um entre: ...` | Passe só um dos parâmetros alternativos |
| `O termo de busca precisa de ao menos 3 caracteres` | Peça um trecho maior |
| `requires_selection: true` | Não é erro: mostre as opções pelo nome e repita com o uuid |
| `HTTP 401` / falha de login | Credencial em `~/.config/mcp-alm/alm.properties` (alm-setup); nunca leia o arquivo |
| `HTTP 403` | Sem acesso àquela área/app: informe e pare |
| Erro de configuração em `link_testartifact_and_requirement` | Passe `gc_context` com a URL da GC ([reference.md](reference.md)) |
