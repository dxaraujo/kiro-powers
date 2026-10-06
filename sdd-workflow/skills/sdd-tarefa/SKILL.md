---
name: "sdd-tarefa"
description: "Ponto de entrada do fluxo SDD para qualquer papel — recebe o número de uma Task (ou Defeito/IB), identifica o papel pelo prefixo da Task ([ESPEC] especificador, [BE] codificador, [QA] testador, configuráveis no sdd-projeto.md), chega ao IB pai, à pasta compartilhada .kiro/specs/ib-<id>-<slug>/ e à branch da funcionalidade (sugere o nome e aguarda confirmação ao criar), oferece assumir e iniciar a Task no ALM (se houver o power alm) e encaminha para a skill do papel (sdd-especificar, sdd-criar-spec, sdd-implementar-spec ou sdd-testar). Use quando a pessoa disser \"vamos trabalhar na task 123\", \"pegar a task 123\", \"atender a task 123\", \"iniciar task\". Não gera documentação, código nem testes."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "task, tarefa, atender task, trabalhar na task, pegar task, iniciar task, nova task, defeito, ib, alm, especificar, codificar, testar, gate, handoff"
---

# sdd-tarefa — Entrada de uma Task (qualquer papel)

Leia antes: o steering do power `sdd-workflow` (papéis, gates, pasta, branch, fases) e `.kiro/steering/sdd-projeto.md`
(prefixos das Tasks, branch base, ALM). Sem `sdd-projeto.md` → ofereça a `sdd-setup` e pare.

## Passo 1 — Ler a Task

**Com o power `alm`:** use a skill **`alm-ccm`** com os ids de `alm/pa_*.json`. Leia o work item completo
(descrição, comentários, links, pai e filhos) **e o IB pai** com as Tasks irmãs.

- Informado um **Item de Backlog** → liste as Tasks filhas e pergunte qual atender.
- Extraia: `task` (id, título, tipo, estado, url), `ib` (id, título, descrição, critérios de aceite, url),
  `irmas` (Tasks de cada papel → id, responsável, estado).

**Sem o power `alm`** (MCP indisponível) → não trave: se a pasta do IB já existe, os dados vêm do `status.md`;
se não, peça à pessoa número, título, descrição e critérios do IB e das Tasks, e registre `ALM: sem power` no
`status.md`. Leitura falhou com o ALM instalado (401, não encontrado) → informe a causa, peça para conferir o
número ou rodar `alm-setup`, e pare. **Nunca invente dados do work item.**

## Passo 2 — Papel

Pelo prefixo do título da Task (tabela **Work items** do `sdd-projeto.md`; padrão abaixo):

| Prefixo | Papel | Próxima skill |
|---|---|---|
| `[ESPEC]` | especificador | `sdd-especificar` |
| `[BE]` | codificador | `sdd-criar-spec` (sem `tasks.md`) ou `sdd-implementar-spec` |
| `[BD]` | fora do fluxo (mudança de banco tratada com quem administra o banco) | só atualize o campo `Banco (DDL)` do `status.md` |
| `[QA]` | testador | `sdd-testar` |
| sem prefixo / Defeito | pergunte o papel (sim/não pela mais provável — Defeito sem IB costuma ser uma só pessoa em todos os papéis) | — |

## Passo 3 — Pasta e branch existentes

1. `git fetch --quiet` e procure a pasta do IB (`.kiro/specs/ib-<idIB>-*/`; Defeito/Task sem IB:
   `.kiro/specs/task-<id>-*/`) na branch atual **e** nas branches remotas com o prefixo do `sdd-projeto.md`
   (`git ls-tree -r --name-only origin/<branch> -- .kiro/specs/`).
2. Achou → leia o `status.md` (branch, fase, papéis). Se a branch atual não é a do `status.md`:
   ```
   A spec do IB <id> está na branch <branch> (fase: <fase>). Trocar para ela? (sim/não)
   ```
   `sim` → `git switch <branch>` (ou `git switch --track origin/<branch>`).
   Há alterações locais não commitadas → avise e pare; nunca use `stash`/`reset` por conta própria.
3. Confira se a fase permite o papel:

| Papel | Fase esperada | Fase diferente |
|---|---|---|
| especificador | `documentando` (inclusive devolução), `validando`, `aguardando-aprovacao` (ou pasta inexistente) | adiante sem devolução aberta → correção só via `sdd-retrabalho` |
| codificador | `especificado`, `planejando`, `implementando` (inclusive devolução), `em-revisao`, `bloqueado` | antes de `especificado` → **pare**: "A especificação ainda não foi aprovada (fase: <fase>; especificador: <nome>)." |
| testador | `em-teste` | antes de `em-teste` → **pare**: "O PR ainda não foi aberto (fase: <fase>; codificador: <nome>)." |

   Devolução `aberta` na seção **Devoluções** destinada a este papel → informe-a no encaminhamento (Passo 6); a skill
   do papel a trata no Passo 0 (via `sdd-retrabalho`, modo recebimento).

## Passo 4 — Primeira vez no IB (só especificador, sem pasta)

1. **Classifique** pelo sentido do texto, cruzando com o código (estrutura descrita no steering de estrutura do
   projeto):

| Classe | Sinais | Documentação exigida |
|---|---|---|
| `NOVA-FUNCIONALIDADE` | "criar/implementar/incluir", funcionalidade que não existe no código | HF + REG + ET + CT |
| `ALTERACAO` | funcionalidade existente citada + nova regra, ajuste, evolução | HF + REG (só as que mudam) + ET + CT |
| `CORRETIVA` | Defeito, "corrigir", "erro", "bug", comportamento divergente | ET (causa raiz + correção) + CT de regressão; HF/REG só se a regra mudar |
| `MANUTENCAO` | ação pontual de dados ou operação ("reprocessar os registros da demanda X", "ajustar a carga") | ET + CT |

   Sinais claros → informe. Dúvida entre duas → confirmação **sim/não** da mais provável. Sem sinal → pergunte.
   Corretiva com prioridade Alta/Crítica → `fast-track: sim` (ET e CT enxutos, sem HF).

2. **Sugira a branch e aguarde a resposta** (não crie antes do "ok"):
   ```
   Branch sugerida: <prefixo><funcionalidade>   (do título do IB: "<título>")
   Confirma, ou informe outro nome:
   ```
   `<funcionalidade>` = kebab-case do assunto do IB, sem acentos e sem número, ≤ 40 chars
   (ex.: `feature/limitar-tentativas-login`). Já existe branch com esse nome → avise e sugira outro.
   Confirmado → `git fetch` e `git switch -c <branch> origin/<base>` (branch base do `sdd-projeto.md`).

3. **Pasta:** `.kiro/specs/ib-<idIB>-<slug>/` (Defeito/Task avulsa: `task-<id>-<slug>/`). Crie o `status.md` a
   partir de [references/status-template.md](references/status-template.md): papéis com as Tasks irmãs, branch,
   artefatos **só os exigidos pela classe**, `fase: documentando`.

## Passo 5 — Assumir e iniciar a Task (pergunta única; nunca alterar sem "sim")

Só com o power `alm` (sem ele, pule este passo e registre o responsável só no `status.md`):
- `Quer assumir a Task <id>? (responsável atual: <nome|ninguém>)` → `ccm_update_workitem(id, fields={"dcterms:contributor": login})`
  (login = `whoami()`, conferido em `members` do `alm/pa_*.json`). **Item de Backlog nunca muda de responsável (é do P.O.).**
- Tarefa sem Estimativa → pergunte as horas → `rtc_cm:estimate` = horas × 3600000.
- Estado inicial (Novo) → `Iniciar?` — use a ação retornada por `ccm_list_workitem_states(id)`.

Registre no `status.md` (tabela **Papéis**): Task, responsável — login da pessoa ou `agente:<nome>` quando um agente
assume o papel (ex.: `agente:sdd-codificador`) — e situação `em andamento`.

## Passo 6 — Encaminhar

```
📋 Task <id> — <título>   ·   papel: <especificador | codificador | testador>
IB: <id — título>  ·  Classe: <classe>  ·  Fase: <fase>
Branch: <branch>  ·  Pasta: .kiro/specs/ib-<id>-<slug>/
Recebido de: <papel anterior, data do gate — ou "início">  ·  Devolução: <R-nnn — resumo | nenhuma>
Próximo: <sdd-especificar | sdd-criar-spec | sdd-implementar-spec | sdd-testar>
```

Siga para a skill do papel passando: Task, IB (título, descrição, critérios, URL), classe, pasta e branch.
As skills seguintes **não releem o ALM**.

## Modo lote

Lista de Tasks/IBs ou "os IBs da sprint" → leia e classifique todos, mostre uma tabela
(`IB | Título | Classe | Branch sugerida | Pasta existe?`) e delegue à skill **`sdd-lote`**.

## Regras

- O ALM (ou a pessoa) é a fonte dos dados das Tasks; o código é a fonte para saber se a funcionalidade existe; o
  `status.md` é a fonte da fase.
- Escrita no `status.md`: só o papel da fase atual, sempre com `git pull --rebase` antes e commit + push logo depois;
  Histórico só por acréscimo (regras e resolução de conflito no steering do power, Convenções).
- Nunca pule um gate: o codificador não começa antes do GATE 1 (`especificado`), o testador antes do GATE 2
  (`em-teste`). As etapas são assíncronas: o sinal é a `fase` do `status.md` na branch remota.
- Toda alteração no ALM e toda troca/criação de branch só com "sim" explícito.
- Falha no meio → informe a etapa e preserve o que já foi criado.
