---
name: "sdd-alm-publicar-planejamento"
description: "Publica no IBM ALM/EWM (skill alm-ccm) SOMENTE a sprint atual do planejamento ágil gerado pela sdd-planejamento — cria IBs e Tasks com vínculo pai-filho na iteração da sprint, guarda os IDs no backlog.json e, na virada de sprint, move para a próxima iteração os itens não concluídos (sem recriar) e publica os itens novos. Suporta dry-run e criação de iteração/plano. Use em \"publica a sprint no ALM\", \"virada de sprint\", \"fechar sprint no ALM\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "alm, publicar, planejamento, sprint atual, virada de sprint, fechar sprint, migrar itens, sprint, ib, backlog, task, ewm, oslc, ccm, plannedFor, agile, mcp"
---

# sdd-alm-publicar-planejamento — Sprint atual no ALM

## Objetivo

Publicar no IBM ALM/EWM os IBs e Tasks gerados pelo planejamento ágil do projeto, criando:
- **IBs** (Item de Backlog) com **Pontos de História**, **Prioridade** e vínculo à iteração da sprint (`plannedFor`)
- **Tasks** subordinadas a cada IB com vínculo pai-filho (`rtc_cm:parent`) e **Estimativa** em horas
- **Responsável:** IBs sempre com o **P.O.**; Tasks com o responsável do planejamento, ou vazias (quem atender o
  IB assume as Tasks vazias, via `sdd-tarefa`)
- Associação automática de cada work item à iteração/sprint no EWM

> **Somente a sprint atual.** Sprints futuras mudam a cada reajuste — publicá-las cedo gera work items que depois
> precisam ser movidos ou cancelados. Esta skill publica **apenas a sprint atual** (ver "Sprint atual" abaixo);
> as próximas ficam só no planejamento local até virarem a sprint atual.

> **Iterações e planos:** se a sprint ainda não existir no EWM, a skill cria a iteração
> (`ccm_create_iteration`) e o plano (`ccm_create_iteration_plan`) — sempre após confirmação (Passo 4).
> Exige a permissão "Modify structures of iterations" na PA; sem ela, peça a quem administra a PA.

---

## Power ALM

Requer o MCP `alm` (power ALM no Kiro). Todas as operações no EWM são feitas com a skill **`alm-ccm`** do
power; configuração da PA (tipos, iterações, planos) e erros de conexão ficam com o power (`alm-setup`).

Arquivos de planejamento: `planejamento-agil/SPRINT N.md`.

---

## Passo 1 — Validar Pré-condições

### Power ALM

Verificar que o power ALM está ativo e a PA configurada. Se não estiver, orientar a rodar a skill `alm-setup`.

### Arquivos de planejamento

Verificar que existem arquivos `SPRINT N.md` em `planejamento-agil/`.
Se não existirem, orientar a executar primeiro a skill `sdd-planejamento`.

---

## Passo 2 — Conferir tipos, iterações, time e plano

Com a skill `alm-ccm`, conferir que existem na PA:
- os tipos **Item de Backlog** e **Tarefa**;
- as iterações/planos correspondentes às sprints do planejamento;
- os times (team areas) da PA.

Se algo faltar, rodar a skill `alm-setup` para atualizar a configuração. A associação sprint → iteração é
feita pelo nome/datas da iteração e registrada no campo `iteracao` do `backlog.json` (Passo 3): com certeza, segue
sem perguntar; sem certeza, pede confirmação (sim/não); sem iteração correspondente, trata no Passo 4.

### Confirmar time (team area) e plano

Antes de gerar o preview, **sempre confirmar com o usuário** em qual **time** e em qual **plano** os IBs e Tasks
de cada sprint serão criados. Propor o plano da iteração da sprint e o time dono desse plano, mostrando só os nomes:

```
Onde criar os work items:

| Sprint | Iteração            | Plano                 | Time                     |
|--------|---------------------|-----------------------|--------------------------|
| 1      | Sprint 1 - 2026-09  | Sprint 01 - Projeto   | Equipe A  |
| 2      | ...                 | ...                   | ...                      |

Confirma? (sim, ou indique o plano/time correto por sprint)
```

Se a iteração tiver mais de um plano ou nenhum, listar as opções via `alm-ccm` e pedir que o usuário escolha.
Registrar o escolhido nos campos `plano` e `time` do `backlog.json`.

---

## Sprint atual e modos de execução

**Sprint atual** = a sprint cujo período (em `Planejamento Ágil.md`; ou `projeto.inicio` + `duracao_sprint_semanas`
do `equipe.json`) contém a data de hoje. Hoje antes do início ou entre sprints → a próxima a começar.
Confirme com o usuário: `Sprint atual: Sprint N (<início> a <fim>). Publicar esta? (sim/não)`.

| Modo | Quando | O que faz |
|---|---|---|
| **Publicação** | a sprint atual ainda não está no EWM | Passos 1–6 só para a sprint atual |
| **Virada de sprint** | acionado pela `sdd-planejamento` após o reajuste (ou "virada de sprint") | Passo 7 (migrar não concluídos) e depois Passos 3–6 só para os itens novos da nova sprint atual |

## Passo 3 — Gerar preview do backlog (backlog.json)

Antes de publicar, gerar um preview da estrutura de IBs e tasks localmente:

1. Ler **só** o `SPRINT N.md` da sprint atual e o `Backlog.md`; ler o `backlog.json` existente (ele guarda os IDs
   do ALM de publicações anteriores)
2. Extrair IBs e tasks da sprint atual — itens que já têm `alm_id` no `backlog.json` **não são recriados**; a `complexidade` vem da coluna Complexidade da `SPRINT N.md` e a
   `prioridade` da coluna Prioridade do `Backlog.md` (pelo `IB-XX`)
3. `responsavel` (login): ler de `planejamento-agil/equipe.json` (campo `login`; conferido em `members` do
   `alm/pa_*.json`):
   - **IB** → o membro com `po: true` (sem arquivo ou sem P.O., perguntar uma única vez e gravar no `equipe.json`);
   - **Task** → o responsável definido no planejamento; sem responsável definido, `null` (fica vazia no ALM).
4. `estimativa_horas` de cada Task não vem do planejamento: pedir ao usuário numa única tabela por sprint
5. Gerar `planejamento-agil/backlog.json` com a estrutura:

```json
{
  "sprints": [
    {
      "numero": 1,
      "iteracao": "Sprint 1 - 2026-09",
      "plano": "Sprint 01 - Projeto",
      "time": "Equipe A",
      "ibs": [
        {
          "id": "IB-01",
          "titulo": "Título do IB",
          "complexidade": 5,
          "prioridade": "Alta",
          "responsavel": "po.login",
          "alm_id": null,
          "estado_alm": null,
          "tasks": [
            { "id": "T-01", "titulo": "Task 1", "tipo": "BE", "responsavel": "dev.login", "estimativa_horas": 8, "alm_id": null },
            { "id": "T-02", "titulo": "Task 2", "tipo": "FE", "responsavel": null, "estimativa_horas": 6, "alm_id": null }
          ]
        }
      ]
    }
  ]
}
```

Cada IB e Task no `backlog.json` tem também `alm_id` (`null` até ser criado) e `estado_alm`. O arquivo acumula as
sprints já publicadas (é o mapa `IB-XX`/`T-XX` → work item); a sprint atual é acrescentada, nunca sobrescreve as anteriores.

Apresentar ao usuário um resumo:
```
Preview — Sprint N (atual): X IBs, Y tasks novos · Z já publicados (ignorados) → Plano "[plano]" · Time "[time]"
```

Aguardar confirmação antes de prosseguir.

---

## Passo 4 — Dry-run (validação sem publicar)

Validar com a skill `alm-ccm`, **sem criar nada**:

1. Verificar a conexão com o ALM
2. Verificar se as iterações, planos e times do `backlog.json` existem
3. Verificar se os tipos Item de Backlog e Tarefa existem
4. Validar os campos obrigatórios de cada tipo contra o ALM (ver abaixo)
5. Exibir o que SERIA publicado

### Campos por tipo

| Campo | `attribute` | Item de Backlog | Tarefa | Valores aceitos |
|-------|-------------|:---------------:|:------:|-----------------|
| Pontos de História | `rtc_ext:com.ibm.team.apt.attribute.complexity` | ✅ | — | 0, 1, 2, 3, 5, 8, 13, 20, 40, 100 (nomes no ALM: `5 pts`) |
| Prioridade | `oslc_cmx:priority` | ✅ | — | os `name` do ALM da PA — criticidade alta/média/baixa → o valor equivalente (mapeamento confirmado com o usuário) |
| Responsável | `dcterms:contributor` | ✅ P.O. | se definido no planejamento | login de `members` do `alm/pa_*.json` |
| Estimativa | `rtc_cm:estimate` | — | ✅ **obrigatória** | horas > 0 |

Nunca inventar valores de Pontos de História e Prioridade — buscar os aceitos com a skill **`alm-ccm`**
(`ccm_list_field_values(pa, "com.ibm.team.apt.workItemType.story", attribute)`).

- Casar `complexidade` e `prioridade` de cada IB pelo `name` e guardar o `identifier` para a criação.
- `complexidade` fora da escala (ex.: 21) ou `prioridade` sem correspondente (ex.: planejamento em
  alta/média/baixa e ALM com outros nomes) → mostrar os valores do ALM e pedir ao usuário o mapeamento;
  gravar o valor escolhido no `backlog.json`.
- Responsável fora de `members` → mostrar os membros e perguntar.
- Os demais obrigatórios de cada tipo (Categoria, Atendido por) também vão na criação — **"Não designado" não
  conta como preenchido** e o ALM recusa o item. Categoria da Tarefa pelo tipo da task: liste as categorias
  da PA (`alm-ccm`), proponha a mais próxima de cada prefixo ([ESPEC], [BE], [BD], [QA]…), confirme o mapeamento
  uma vez e grave-o no `backlog.json` (`categorias`); sem correspondente → perguntar.
- Nenhum work item é publicado com campo obrigatório vazio: IB sem complexidade, prioridade ou responsável (P.O.),
  ou Task sem estimativa → perguntar. Task sem responsável é permitida.

**Se houver sprints sem iteração ou sem plano:** mostre o que falta e pergunte se deseja:
- (a) **Criar no EWM** — para cada sprint: `ccm_create_iteration(project_area_identifier, parent=<identifier da
  iteração pai em ccm_list_iterations — a release/timeline atual>, name, start_date, end_date)` (datas
  `AAAA-MM-DD` do planejamento) e, em seguida, `ccm_create_iteration_plan(project_area_identifier, name,
  iteration=<identifier criado>, plan_type="com.ibm.team.apt.plantype.kanbanBoard", team_area=<time confirmado>)`.
  Confirme pai, nomes e datas numa tabela antes de criar; depois rode `alm-setup` para atualizar o `pa_*.json`.
- (b) Ajustar a iteração no `backlog.json` para uma existente e rodar novamente
- (c) Publicar sem `plannedFor` (work items sem sprint no EWM)
- (d) Cancelar

---

## Passo 5 — Publicar a sprint atual

Para cada IB da sprint atual **sem `alm_id`**, com a skill `alm-ccm`:

1. **Criar o IB** (tipo Item de Backlog) com título `IB-XX - Título do IB`, no **time** confirmado, na
   iteração do **plano** confirmado (Planejado para), com **Pontos de História** e **Prioridade** — ambos em
   `fields` do `ccm_create_workitem`, pelo `identifier` validado no Passo 4:
   `{"rtc_cm:teamArea": ..., "rtc_cm:plannedFor": ..., "rtc_ext:com.ibm.team.apt.attribute.complexity": ..., "oslc_cmx:priority": ..., "dcterms:contributor": login do P.O.}`.
2. **Criar cada Task** (tipo Tarefa) com título `T-XX - Título da Task`, **filha do IB** criado, no mesmo time e
   na mesma iteração, com **Estimativa** e, se definido, **Responsável**:
   `{..., "rtc_cm:estimate": estimativa_horas × 3600000}` + `"dcterms:contributor": login` só quando o
   planejamento definir (sem responsável, omitir o campo) — o EWM guarda a
   estimativa em milissegundos; confira no EWM que a primeira Task mostra as horas certas.

> **Ordem obrigatória:** sempre criar **primeiro o IB** e só depois as suas Tasks. O vínculo com o IB pai é
> informado **na criação da Task** (nunca como passo posterior) — sem o id do IB já criado, não criar a Task.

Após cada criação, gravar `alm_id` (e `estado_alm`) no `backlog.json` — é o que torna a skill retomável e evita
duplicar em caso de erro parcial.

---

## Passo 6 — Verificar resultado no EWM

Após publicar a sprint atual, verificar no EWM:
1. IBs criados com título correto (`IB-XX - Título`)
2. Tasks subordinadas visíveis dentro de cada IB
3. Campo "Planned For" na iteração correta e time (team area) confirmado
4. P.O. como responsável, Pontos de História e Prioridade nos IBs; Estimativa (e responsável, se definido) nas Tasks — conforme o `backlog.json`
5. IBs e Tasks aparecendo no plano confirmado (listar os itens do plano via `alm-ccm`)
6. Vínculo pai-filho entre Task → IB

**Se algo estiver errado:**
- Verificar tipos e iterações via `alm-ccm` (ou `alm-setup`)
- Corrigir os work items existentes via `alm-ccm`

---

## Passo 7 — Virada de sprint (migrar não concluídos)

Executado quando a sprint N terminou e a `sdd-planejamento` já fez o reajuste (a sprint N+1 é a nova atual).

1. **Estado real:** para cada IB e Task da sprint N com `alm_id`, ler o estado no EWM (`ccm_get_workitem`).
   Concluído = estado **Pronto** (ou equivalente de conclusão retornado por `ccm_list_workitem_states`).
   O EWM é a fonte da verdade: devolva à `sdd-planejamento` a lista de concluídos para marcar `Feito = OK`.
2. **Não concluídos:** mostre a tabela e confirme:
   ```
   Não concluídos na Sprint N → migrar para Sprint N+1 (<iteração>):
   | Work item | Título | Estado | Ação |
   | 123456 | IB-03 - … | Em Desenvolvimento | mover |
   | 123460 | T-07 - … | Novo | mover |
   Confirma? (sim / ajustar)
   ```
3. **Mover, nunca recriar:** `ccm_update_workitem(id, fields={"rtc_cm:plannedFor": <iteração da sprint N+1>})` em
   cada item não concluído — o IB e as Tasks pendentes dele; Tasks já concluídas ficam na sprint N.
   Registre o motivo com `add_comment_to_workitem(id, "Migrado da Sprint N para a Sprint N+1 — não concluído.")`.
4. **IB parcialmente feito:** o IB migra junto com as Tasks pendentes; os Pontos de História permanecem no IB
   (contam na sprint em que ele terminar, regra da `sdd-planejamento`).
5. Atualize `backlog.json` (`sprint`, `estado_alm`) e siga para os Passos 3–6 com os itens **novos** da sprint N+1.

---

## Tratamento de Erros

| Situação | Ação |
|----------|------|
| Power ALM indisponível / erro de conexão | Ver power ALM (`alm-setup`) |
| Tipo de WI ou iteração não encontrados | Conferir via `alm-ccm`; atualizar configuração com `alm-setup` |
| Erro ao criar vínculo | Verificar IDs dos work items pai/filho |
| Nenhum SPRINT N.md | Executar a skill `sdd-planejamento` primeiro |

---

## Regras Gerais

- **Nunca** publicar sem que o usuário tenha visto o preview (backlog.json) e confirmado.
- **Nunca** criar work items sem o time (team area) e o plano confirmados pelo usuário.
- **Nunca** criar IB sem Pontos de História, Prioridade e o P.O. como responsável, nem Task sem Estimativa em horas.
- Task sem responsável no planejamento fica **vazia** — quem atender o IB (`sdd-tarefa`) assume a Task; o IB fica sempre com o P.O.
- **Sempre** criar o IB antes das Tasks e criar cada Task já vinculada ao IB pai.
- **Nunca** sobrescrever work items existentes sem confirmação explícita.
- **Sempre** fazer dry-run antes da primeira publicação numa PA nova.
- **Somente a sprint atual** é publicada — nunca criar work items de sprints futuras.
- Na virada, itens não concluídos são **movidos** (`plannedFor`) para a nova sprint — nunca recriados nem cancelados.
- Item com `alm_id` no `backlog.json` nunca é criado de novo.
- **Sempre** informar o total de IBs e tasks publicados ao concluir.
- Em caso de erro parcial, os work items já criados **não são revertidos** — informar ao usuário quais foram criados e quais falharam.
- Iterações e planos só são criados no EWM após confirmação explícita (Passo 4, opção a).

---

## Encerramento

Após publicação bem-sucedida:

```
✅ Planejamento publicado no ALM — <projeto>

Sprint N (atual) : X IBs + Y tasks criados → Plano "[plano]" · Time "[time]"
Migrados da Sprint N-1 : Z work items (virada de sprint)

Próximo passo: verificar o plano da sprint no EWM. As próximas sprints serão publicadas quando virarem a atual.
```

