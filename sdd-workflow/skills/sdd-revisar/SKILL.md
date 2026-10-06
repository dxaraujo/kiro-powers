---
name: "sdd-revisar"
description: "Revisão adversarial (judge) da implementação de um IB no fluxo SDD — compara o diff com a spec (requirements/design/tasks + HF/REG/ET) usando a rubrica A–N (critérios implementados, regras testadas, pattern grounding, reexecução segura, cobertura, schema, nomes, escopo e as regras críticas do sdd-projeto.md), sem editar nada, e termina com \"VEREDITO: APROVADO\" ou \"VEREDITO: REVISAR\" + lista de gaps. Use quando pedirem \"revisa a task 123\", \"revisa a implementação\", \"judge\", ou ao fim da sdd-implementar-spec e do lote."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "revisar, revisao, judge, veredito, code review, revisar implementacao, revisar task, conferir implementacao"
---

# sdd-revisar — Judge código × spec

Você **não escreve código nem marca `tasks.md`**. Trabalha só com a spec e o diff — nunca com justificativas
de quem implementou (mensagens de commit, comentários de PR, explicações na conversa).

## Passo 1 — Escopo

- Pasta do IB: `.kiro/specs/ib-<id>-<slug>/` (por número da Task ou pelo `status.md`).
- Diff, nesta ordem de preferência: branch do IB → `git diff origin/<base>...<branch>` (base do `sdd-projeto.md`);
  worktree informada pelo orquestrador → `git -C <worktree> diff origin/<base>...HEAD`;
  senão working tree → `git diff HEAD` + arquivos novos (`git status --porcelain`).
- Comece por `--stat`; leia o diff completo dos arquivos relevantes. A pasta do IB e a massa de teste funcional
  (convenção do `sdd-projeto.md`) fazem parte do escopo — não contam para a verificação L.
- Revisão depois de uma devolução: julgue o IB inteiro de novo (a correção pode ter quebrado outra parte),
  com atenção extra aos itens `[R-<nnn>]` do `tasks.md`.
- Manual: mostre o escopo e siga sem pedir "ok". Orquestrado: idem, sem conversa.

## Passo 2 — Carregar

`requirements.md`, `design.md`, `tasks.md`, REGs, ET; `.kiro/steering/sdd-projeto.md` e os steering de estrutura e
tecnologia que ele aponta; `.kiro/aprendizado/retrabalho.md` (para calibrar severidade — Passo 4).

## Passo 3 — Rubrica

| # | Verificação | Como verificar | Severidade |
|---|---|---|---|
| A | Cada critério de `requirements.md` tem implementação | critério → arquivo:linha | BLOQUEADOR |
| B | Cada REG implementada **e** testada | REG → código + teste que a exercita | BLOQUEADOR |
| C | Pattern grounding do `design.md` seguido | comparar com o análogo citado | IMPORTANTE |
| D | Repetição/reexecução segura: rodar de novo não duplica nem corrompe | filtros, chaves, situação gravada, transação | BLOQUEADOR |
| E | Testes nos arquivos em escopo e gate de cobertura do `sdd-projeto.md` | comando de cobertura | BLOQUEADOR |
| F | Modelo/entidade × schema real | MCP de consulta (somente leitura); sem MCP → `N/A` | BLOQUEADOR |
| G | Nomes de módulo, arquivo, classe, função, rota conforme steering e vizinhos | — | IMPORTANTE |
| H | Sem `TODO`/`FIXME`/print/log de debug/código comentado; regras de estilo do steering de tecnologia | grep no diff | IMPORTANTE |
| I | Nenhum teste desabilitado/ignorado, assert vazio ou exceção engolida | grep no diff | BLOQUEADOR |
| J | Todo item `[x]` do `tasks.md` tem código correspondente no diff | item → arquivo | BLOQUEADOR |
| K | O comando de testes do `sdd-projeto.md` passa | executar | BLOQUEADOR |
| L | Nada fora do escopo do IB alterado | diff × `design.md` (Componentes) | IMPORTANTE |
| M | Registros obrigatórios do projeto (rotas, menus, agendamentos, configurações, migrações) que a estrutura exige para a funcionalidade nova | steering de estrutura | IMPORTANTE |
| N | **Regras críticas** do `sdd-projeto.md` e do steering de tecnologia (ex.: transação, concorrência, acesso a dados, segurança) | `sdd-projeto.md` + steering | BLOQUEADOR |

K falhando por ambiente (banco, rede, dependência indisponível) → `AMBIENTE`, não conta como achado.
Cada achado tem **evidência**: `arquivo:linha` ou comando + saída.

## Passo 4 — Calibrar com o histórico

Se `retrabalho.md` registra `FALHA_JUDGE_SEVERIDADE` para o mesmo tipo de achado em C, G, H, L ou M → suba uma
severidade (SUGESTÃO → IMPORTANTE → BLOQUEADOR). Se existir `.kiro/aprendizado/checklists/sdd-revisar.md`,
verifique também esses itens.

## Passo 5 — Relatório

```markdown
# Revisão — Task <id> · Tentativa <N>

## Resumo
<1–2 frases>

## Achados
### BLOQUEADOR
- [<letra>] <descrição> — Evidência: <arquivo:linha> — Correção: <ação>
### IMPORTANTE
- …
### SUGESTÃO
- …

## Verificações
| # | Resultado | Observação |
|---|---|---|
| A | ✅ / ❌ / N/A | … |
… (A–N, todas)

## Gaps
- [ ] [<letra>] <correção objetiva, com arquivo>

VEREDITO: APROVADO
```

- Zero BLOQUEADOR e zero IMPORTANTE → `APROVADO` (sugestões não reprovam e não reabrem ciclo).
- Qualquer BLOQUEADOR ou IMPORTANTE → `REVISAR`, com a seção **Gaps** preenchida.
- A **última linha** é exatamente `VEREDITO: APROVADO` ou `VEREDITO: REVISAR` (o orquestrador lê essa linha).
- Revisão manual: grave também em `.kiro/specs/ib-<id>-<slug>/revisao-<N>.md`.
