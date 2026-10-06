---
name: "sdd-status"
description: "Painel do fluxo SDD — mostra onde parei: IBs com pasta em .kiro/specs/ (local, worktrees e branches remotas), fase, de quem é a vez (especificador, codificador ou testador), minhas Tasks, situação do ALM e do banco (DDL), progresso do tasks.md, devoluções abertas, PRs, lotes em andamento e inconsistências. Somente leitura. Use em \"onde parei\", \"status\", \"painel\", \"bom dia\", \"o que tem pendente\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "status, painel, onde parei, bom dia, pendencias, o que falta, andamento, retomar, dashboard, devolucoes, pr"
---

# sdd-status — Onde parei

Somente leitura: não altera nenhum arquivo nem o ALM. A tabela de fases ("Vez de") está no
steering do power `sdd-workflow`. As etapas são assíncronas: o que vale é o `status.md` mais recente de cada
branch remota. Sem `.kiro/steering/sdd-projeto.md` → avise que o fluxo não está configurado (`sdd-setup`).

## Coleta

1. Pastas `.kiro/specs/ib-*/` e `.kiro/specs/task-*/` da branch atual, das worktrees (`git worktree list`) e das
   branches remotas com o prefixo do `sdd-projeto.md` (`git fetch --quiet` +
   `git ls-tree -r --name-only origin/<branch> -- .kiro/specs/`; o `status.md` remoto com
   `git show origin/<branch>:<caminho>`).
2. De cada `status.md`: IB, título, classe, branch, fase, PR, ALM, Banco (DDL), papéis (Task, responsável,
   situação), artefatos, achados de validação e devoluções abertas, retries.
3. De cada `tasks.md`: itens `[x]` / total; primeiro item pendente.
4. Lotes: `.kiro/local/lote-*.md` com IBs ainda no meio do modo.
5. Consistência: artefato listado sem arquivo; arquivo `HF/REG/ET/CT` sem linha no `status.md`; fase `em-teste`
   com itens pendentes no `tasks.md` ou sem PR; devolução `aberta` com fase que não é a do papel destino;
   `concluido` com `Banco (DDL)` diferente de `aplicada em prod` (implantação bloqueada); Histórico fora de ordem
   cronológica ou `fase` que não bate com o último registro do Histórico (sinal de conflito mal resolvido).

## Painel

```
📋 SDD — <data>  ·  você: <login>

| IB | Título | Branch | Fase | Vez de | ALM | Banco | tasks.md | Próxima ação |
|---|---|---|---|---|---|---|---|---|
| 123 | limitar tentativas de login | feature/limitar-tentativas-login | implementando | codificador (ana) | publicado | — | 5/7 | item 6 — testes e cobertura |
| 124 | … | feature/ajustar-reprocessamento | documentando | especificador (—) | sem power | pendente | 6/6 | devolução R-012 (testes reprovados, FALHA_DOC) |
| 125 | … | feature/corrigir-filtro-relatorio | em-teste | testador (bruno) | publicado | pendente | 4/4 | testes bloqueados: DDL não aplicada em dev |

Minhas Tasks: codificador 611 (IB 123) · especificador 901 (IB 900, validando)
Devoluções abertas: R-012 (IB 124 → especificador)
Lote em andamento: lote-2026-10-05-0930 — 2 PRs abertos · 1 em revisão · 1 bloqueado
Implantação bloqueada: IB 120 (concluído, DDL não aplicada em produção)
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

Sem nenhuma pasta: "Nenhum IB em andamento. Diga o número da próxima Task (`sdd-tarefa`)."
