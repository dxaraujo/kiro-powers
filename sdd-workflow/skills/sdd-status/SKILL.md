---
name: "sdd-status"
description: "Painel do fluxo SDD — mostra onde parei: IBs com pasta em .kiro/specs/ (local, worktrees e branches remotas), fase, de quem é a vez (especificador, codificador ou testador), minhas Tasks, situação do ALM e do banco (DDL), progresso do tasks.md, devoluções abertas, PRs, lotes em andamento, IBs planejados ainda não iniciados (planejamento-agil, sem ALM) e inconsistências. Somente leitura. SEMPRE use esta skill (leia-a antes de responder) em \"onde parei\", \"onde parei?\", \"status\", \"painel\", \"bom dia\", \"o que tem pendente\", \"o que tenho pra fazer\", \"qual a próxima task\", \"retomar\" — não responda só com git status/log."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "status, painel, onde parei, bom dia, pendencias, o que falta, o que tenho pra fazer, proxima task, andamento, retomar, dashboard, devolucoes, pr, sprint atual"
---

# sdd-status — Onde parei

Somente leitura: não altera nenhum arquivo nem o ALM. A tabela de fases ("Vez de") está no
steering do power `sdd-workflow`. As etapas são assíncronas: o que vale é o `status.md` mais recente de cada
branch remota. Sem `.kiro/steering/sdd-projeto.md` → avise que o fluxo não está configurado (`sdd-setup`).

## Coleta

1. Pastas `.kiro/specs/ib-*/` e `.kiro/specs/task-*/` da branch atual, das worktrees (`git worktree list`) **e de
   todas as branches remotas** (`git fetch --quiet` +
   `git ls-tree -r --name-only origin/<branch> -- .kiro/specs/`; o `status.md` remoto com
   `git show origin/<branch>:<caminho>`) — procedimento em
   [localizar-ib.md](../sdd-tarefa/references/localizar-ib.md), passo 1. Obrigatório: a pasta do IB costuma estar só
   na branch da funcionalidade; uma branch sem pasta em `.kiro/specs/` é que pode ser ignorada.
2. De cada `status.md`: IB, título, classe, branch, fase, PR, ALM, Banco (DDL), papéis (Task, responsável,
   situação), artefatos, achados de validação e devoluções abertas, retries, e as **pendências de ALM** (linhas
   `ALM pendente: <ação>` do Histórico sem um `ALM feito: <ação>` depois).
3. De cada `tasks.md`: itens `[x]` / total; primeiro item pendente.
4. Lotes: `.kiro/local/lote-*.md` com IBs ainda no meio do modo.
5. Sprint atual (sem ALM, ou para cruzar com ele): `planejamento-agil/backlog.json` (ou `SPRINT N.md`) da sprint
   atual (a de menor número com Tasks sem `Feito = OK` no `SPRINT N.md`) — IBs e Tasks planejados, responsável (`equipe.json` → `login`). IB planejado **sem pasta**
   em nenhuma branch → "planejado, não iniciado". "Minhas Tasks" sem ALM = Tasks do planejamento e dos `status.md`
   cujo responsável é o login da pessoa (`git config user.name`/`equipe.json`; sem correspondência, pergunte).
6. Consistência: artefato listado sem arquivo; arquivo `HF/REG/ET/CT` sem linha no `status.md`; fase `em-teste`
   com itens pendentes no `tasks.md` ou sem PR; devolução `aberta` com fase que não é a do papel destino;
   `concluido` com `Banco (DDL)` diferente de `aplicada em prod` (implantação bloqueada); Histórico fora de ordem
   cronológica ou `fase` que não bate com o último registro do Histórico (sinal de conflito mal resolvido).

## Painel

```
📋 SDD — <data>  ·  você: <login>

| IB | Título | Branch | Fase | Vez de | ALM | Banco | tasks.md | Próxima ação |
|---|---|---|---|---|---|---|---|---|
| 123 | limitar tentativas de login | feature/limitar-tentativas-login | implementando | codificador (ana) | publicado | — | 5/7 | item 6 — testes e cobertura |
| 124 | … | feature/ajustar-reprocessamento | documentando | especificador (—) | pendente | pendente | 6/6 | devolução R-012 (testes reprovados, FALHA_DOC) |
| 125 | … | feature/corrigir-filtro-relatorio | em-teste | testador (bruno) | publicado | pendente | 4/4 | testes bloqueados: DDL não aplicada em dev |

Minhas Tasks: codificador 611 (IB 123) · especificador 901 (IB 900, validando)
Devoluções abertas: R-012 (IB 124 → especificador)
Lote em andamento: lote-2026-10-05-0930 — 2 PRs abertos · 1 em revisão · 1 bloqueado
Planejados não iniciados (Sprint 3): IB-07 limitar tentativas de login — [ESPEC] T-19 (ana) · IB-08 …
Implantação bloqueada: IB 120 (concluído, DDL não aplicada em produção)
ALM pendente (fazer com o power alm): IB 124 — publicar HF/REG/ET e concluir [ESPEC] 901
⚠️ Inconsistências: ib-123 — REG-02-*.md existe mas não está no status.md
```

Próxima ação por fase:

| Fase | Próxima ação |
|---|---|
| `documentando` | `sdd-especificar` (ou a devolução aberta) |
| `validando`, `aguardando-aprovacao` | `sdd-validar-requisitos` (GATE 1) |
| `especificado` | codificador: `sdd-tarefa` com a Task do codificador → `sdd-criar-spec` |
| `planejando` | `sdd-criar-spec` |
| `implementando` | primeiro item pendente ou a devolução aberta (`sdd-implementar-spec`) |
| `em-revisao` | `sdd-revisar` |
| `bloqueado` | decisão da pessoa responsável (`sdd-implementar-spec`, 4.1) |
| `em-teste` | testador: `sdd-tarefa` com a Task do testador → `sdd-testar` (se o Banco estiver `pendente`, aguardar a DDL em dev) |
| `concluido` | nada — ou acompanhar a DDL em produção, se pendente |

Sem nenhuma pasta: "Nenhum IB em andamento." + os planejados não iniciados da sprint atual, se houver
("Próxima: [ESPEC] T-19 do IB-07 — diga *vamos trabalhar na task T-19*"); sem planejamento, "Diga o número da
próxima Task (`sdd-tarefa`)."
