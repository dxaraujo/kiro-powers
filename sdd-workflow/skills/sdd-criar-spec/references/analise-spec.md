# Análise da spec SDD (antes de codificar)

Confere, com olhar independente, se `requirements.md`, `design.md` e `tasks.md` do IB são fiéis à documentação
aprovada (HF, REGs, ET, CT, `decisoes.md`) e à constitution do projeto (steering de **tecnologia** e **estrutura**
e as **regras críticas** do `.kiro/steering/sdd-projeto.md`) — **antes** de qualquer código. Executada pelo agente
`sdd-revisor` (só leitura): ele devolve o relatório e quem chamou grava `analise-spec-<N>.md` na pasta do IB.

## Rubrica

| # | Verificação | Como verificar | Severidade |
|---|---|---|---|
| S1 | Toda REG, todo cenário da HF e toda decisão `decidida` de `decisoes.md` têm critério EARS em `requirements.md` | cruzar `Origem:` dos requisitos com a lista de REGs, cenários e `D-nn` | BLOQUEANTE |
| S2 | Todo critério EARS tem item no `tasks.md` (`_Requisitos: N.M_`) e é coberto por algum CT do `CT.csv` | critério → task; critério → CT | BLOQUEANTE |
| S3 | Nenhum requisito, design ou task introduz regra de negócio que não esteja na documentação | ler requisitos e decisões técnicas do `design.md` | BLOQUEANTE |
| S4 | O `design.md` respeita a constitution: padrões e camadas do steering de estrutura, regras do steering de tecnologia e as **regras críticas** do `sdd-projeto.md` (transação, idempotência, acesso a dados, segurança) | steering + `sdd-projeto.md` | BLOQUEANTE |
| S5 | Funcionalidade análoga, componentes reaproveitados e caminhos citados existem no código | `glob`/`read` nos caminhos | AJUSTE |
| S6 | Todo componente do `design.md` aparece em algum item do `tasks.md`, e todo item do `tasks.md` corresponde a um componente/requisito | cruzar as duas listas | AJUSTE |

Cada achado tem evidência (`arquivo:linha` ou referência ausente) e a correção esperada.

## Relatório

```markdown
## Análise da spec — IB <id> · rodada <N>
| # | Resultado | Achado | Evidência | Correção |
|---|---|---|---|---|
| S1 | ✅ | | | |
| S2 | ❌ BLOQUEANTE | critério 2.3 sem CT | requirements.md:41 · CT.csv | <spec: ajustar critério> ou <doc: CT ausente → devolução> |
…
ANALISE: OK | AJUSTAR
```

- Qualquer BLOQUEANTE → `AJUSTAR`. Achados só de AJUSTE não impedem `OK`.
- Marque em cada achado se a falta é **da spec** (o codificador corrige) ou **da documentação** (ex.: cenário da HF
  sem CT, regra contraditória) — esta última vira devolução pela `sdd-retrabalho` (`FALHA_DOC`).
