---
name: "sdd-lote"
description: "Orquestra vários IBs do fluxo SDD de uma vez, respeitando as etapas assíncronas — modo especificação (requisitos pelo sdd-especificador, validação formal pelo sdd-revisor, GATE 1 único; publicação no ALM se houver o power alm), modo codificação (IBs especificados: spec SDD e implementação autônoma pelo sdd-codificador ou executores do projeto, judge sdd-revisor, retry ≤ 2 e abertura do PR — GATE 2) ou completo (mesma pessoa). Os testes ficam fora do lote (o testador decide cada PR). Uma worktree e uma branch por IB, com os nomes sugeridos e confirmados. Retomável pelo log em .kiro/local/. Use para \"especifica os IBs da sprint\", \"implementa os IBs especificados\", \"executa o lote dos IBs 1, 2, 3\", \"retoma o lote\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "lote, varios ibs, varias tasks, orquestrar, ibs da sprint, retomar lote, paralelo, worktree, automatizar, especificar em lote, codificar em lote"
---

# sdd-lote — Orquestração de vários IBs

Quem executa esta skill é o **orquestrador** (a sessão da pessoa ou o agente `sdd-orquestrador`). Ele faz os papéis
especificador e codificador **por agentes**, mantém o log e é o **único** que marca `tasks.md`, faz commit, push
(fim de cada etapa) e altera o ALM (só com o power `alm`). Papéis, gates e fases: o steering do power
`sdd-workflow`; branch base, executores e comandos: `.kiro/steering/sdd-projeto.md`.
Os testes (`sdd-testar`) não entram no lote — o testador (pessoa ou agente) testa cada PR e decide o GATE 3.

`<repo>` abaixo = nome da pasta do repositório; worktrees ficam ao lado dele: `../<repo>-wt-<funcionalidade>`.

## Passo 0 — Retomada

Existe `.kiro/local/lote-*.md` com IBs não finalizados? Mostre o estado (por IB: fase, retries, último veredito)
e pergunte se retoma. Retomar = pular os que já passaram do gate do modo e continuar os
demais da fase registrada.

## Passo 1 — Modo e montagem

1. **Modo** (pelo papel de quem pede; pergunte se não estiver claro):

| Modo | Para | Fases | Termina em |
|---|---|---|---|
| `especificacao` | especificador | A | GATE 1 de cada IB (+ publicação, se houver ALM) |
| `codificacao` | codificador | B | GATE 2 (PR aberto) de cada IB |
| `completo` | quem acumula os dois papéis | A + B | GATE 2 de cada IB |

2. **Entrada:** lista de IBs ou Tasks (Task → IB pai), ou "os IBs da sprint" (`alm-ccm`, se houver ALM). Para cada
   IB, rode a leitura da **`sdd-tarefa`** (Passos 1–3) — sem as perguntas de assumir/iniciar, que vão juntas no plano.
   - `especificacao`: IBs sem pasta ou em `documentando`/`validando`/`aguardando-aprovacao`.
   - `codificacao`: IBs em `especificado`/`planejando`/`implementando`/`em-revisao`; os demais saem do lote com o
     motivo ("requisitos ainda não aprovados" ou "PR já aberto").
3. **Plano — com as branches sugeridas; aguarde a resposta:**
```
📋 Lote <modo> — <N> IBs · base: <branch base> · paralelismo: 3 · retries: 2
| IB | Título | Classe | Branch | Worktree |
|---|---|---|---|---|
| 123 | Limitar tentativas de login | NOVA-FUNCIONALIDADE | feature/limitar-tentativas-login (sugerida) | ../<repo>-wt-limitar-tentativas-login |
| 124 | … | CORRETIVA | <existente> (do status.md) | ../<repo>-wt-<…> |
Assumir as Tasks <do especificador | do codificador> sem responsável e iniciar as novas? (sim/não — só com ALM)
Confirma as branches (ou informe outros nomes por IB) e o início do lote?
```
   Branch sugerida = prefixo do `sdd-projeto.md` + kebab-case do assunto do IB (≤ 40 chars); IB que já tem branch
   no `status.md` usa a dele.
4. Crie o log `.kiro/local/lote-<AAAA-MM-DD-HHMM>.md` (formato no fim).

## Passo 2 — Worktrees

```bash
git fetch --quiet
git worktree add ../<repo>-wt-<funcionalidade> -b <branch> origin/<base>   # nova (especificação)
git worktree add ../<repo>-wt-<funcionalidade> <branch>                    # existente (codificação/retomada)
```
Todo o trabalho do IB acontece **dentro da worktree**. Na especificação, a pasta `.kiro/specs/ib-<id>-<slug>/`
nasce lá (`status.md` pelo template da `sdd-tarefa`, com papéis e branch).

## Passo 3 — Fase A: especificação (modos `especificacao` e `completo`; paralelo, até 3)

Dispare um subagente **`sdd-especificador`** por IB:
```
ORCHESTRATED=true
IB: <id> · Task: <id> · Classe: <classe> · URL: <url> · Título/descrição/critérios: <dados lidos>
Worktree: <caminho absoluto> · Pasta da spec: <caminho absoluto>
```
Ele roda a `sdd-especificar` sem perguntas (dúvidas de negócio vão para "Dúvidas pendentes" da HF) e devolve o resumo.

**Validação (por IB):** dispare o subagente **`sdd-revisor`** para executar a **`sdd-validar-requisitos`** na pasta
do IB (olhar independente de quem escreveu) e grave o relatório devolvido em `validacao-<N>.md` e na seção de
validação do `status.md`. `AJUSTAR` → redispare o `sdd-especificador` com os achados (modo
ajuste) e valide de novo — no máximo 2 rodadas; o que restar vai como achado aberto para o GATE 1.

**GATE 1 (único para o lote):**
```
📋 GATE 1 — documentação
| IB | REGs | Cenários HF | Interfaces/queries ET | CTs | DDL | Dúvidas | Validação (rodada · resultado · achados abertos) |
Aprova todos? ("ok" · "ok exceto 124" · ou ajustes por IB)
```
- Ajuste → redispare o `sdd-especificador` só do IB, com o pedido; reapresente só ele.
- IB com achado bloqueante aberto só é aprovado se uma pessoa aceitar o achado explicitamente.
- Aprovados → `fase: especificado`; commit em cada worktree (padrão do `sdd-projeto.md`, ex.:
  `Task <id> - Especificar <funcionalidade>`); numa só confirmação para o lote: push de cada branch **a partir do
  repositório principal** (`git push origin <branch>`; nunca push nem merge de dentro das worktrees) — é o sinal
  para a codificação.
- Com power ALM → **`sdd-alm-publicar-requisitos`** para cada um, na sessão orquestradora (publica, rastreia e
  conclui a Task do especificador). Sem ALM → `ALM: sem power — não publicado` no `status.md`.
- IB recusado no gate → sai do lote com o motivo.

## Passo 4 — Fase B: codificação (modos `codificacao` e `completo`; paralelo, até 3 IBs)

Por IB, em loop:

0. **Spec SDD:** sem `tasks.md` (ou com devolução atendida pelo especificador), o **`sdd-codificador`** cria a spec
   primeiro pela **`sdd-criar-spec`**. Se ele reportar falta de negócio na documentação, abra a devolução
   pela **`sdd-retrabalho`** (gatilho "falha na spec na codificação" — retrabalho sempre registrado), tire o IB da
   fase B e siga para o próximo; ele volta ao lote depois do novo GATE 1.
   **Análise da spec:** em seguida dispare o subagente **`sdd-revisor`** para a análise S1–S6
   (`sdd-criar-spec/references/analise-spec.md`) e grave o relatório em `analise-spec-<N>.md`. `AJUSTAR` com falta da
   spec → redispare o codificador com os achados (no máximo 2 rodadas; persistindo, `bloqueado` com o motivo);
   falta da documentação → devolução, como acima. Só com `ANALISE: OK` o IB segue para a implementação.
1. DDL pendente (`Banco (DDL)`) **não** bloqueia a codificação — só os testes e a implantação.
2. **Implementar:** executor pela tabela **Executores** do `sdd-projeto.md` (pelo tipo dos itens do `tasks.md`); o
   que não casar com nenhuma linha → **`sdd-codificador`**.

   Prompt: `ORCHESTRATED=true`, worktree e pasta da spec (absolutos), itens a executar e — no retry — **só os gaps**
   (ou a **devolução aberta** `R-<nnn>` do `status.md` e os itens `[R-<nnn>]` do `tasks.md`, se o IB voltou por
   devolução — o codificador registra o retrabalho pela `sdd-retrabalho`, modo recebimento).
3. **Revisar:** dispare **`sdd-revisor`** com IB, pasta da spec, worktree e nº da tentativa — **nunca** o relatório
   do codificador. Leia a última linha.
4. **Decidir:**

| Resultado | Ação |
|---|---|
| `VEREDITO: APROVADO` | marcar `tasks.md` `[x]`; Spec SDD `implementado`; commit (padrão do `sdd-projeto.md`); IB pronto para o PR |
| `REVISAR` e retries < 2 | retries+1; volte ao item 2 com a seção **Gaps** |
| `REVISAR` e retries = 2 | `bloqueado`; guarde o histórico de vereditos no log |
| erro de ambiente | não conta retry; `bloqueado` com motivo AMBIENTE e pare esse IB |

5. **GATE 2 (agrupado, ao fim):** gere o texto do PR de cada IB aprovado (`sdd-implementar-spec`, Passo 5) e, numa
   só confirmação: push de cada branch a partir do repositório principal, abertura dos PRs (ferramenta do
   `sdd-projeto.md`, ou entrega dos textos para a pessoa abrir), `fase: em-teste` + link do PR no `status.md` e, com
   ALM, comentário em cada Task do testador. A Task do codificador continua aberta: fecha no merge (GATE 3).

Atualize o log após **cada** etapa (é o que permite retomar).

## Passo 5 — Encerramento

```
✅ Lote <modo> — <N> IBs
| IB | Fase | Branch | Retries | Gate | Observação |
Especificados (GATE 1): <ids>  ·  PRs abertos (GATE 2): <ids — links>
Bloqueados: <id> — <último veredito resumido>   ·   Fora do lote: <id> — <motivo>
Testes bloqueados por DDL pendente em dev: <ids>
```
Depois do lote: o testador pega cada Task de teste pela `sdd-tarefa` (`sdd-testar`), testa o PR e decide o GATE 3.
Devoluções (testes reprovados, PR rejeitado) passam pela `sdd-retrabalho`; um IB devolvido pode voltar a um lote.
Worktrees: `git worktree remove ../<repo>-wt-<funcionalidade>` quando o IB sair do lote (sem trabalho não commitado).

Mostre também o resumo do aprendizado: contagem do `.kiro/aprendizado/retrabalho.md` por categoria e itens dos
checklists com ≥ 2 ocorrências (candidatos a promoção — `sdd-retrabalho`).

## Formato do log

```markdown
# Lote <modo> <AAAA-MM-DD HH:MM> — <origem: lista | IBs da sprint N>

| IB | Branch | Worktree | Classe | Fase | Executor | Retries | Último veredito | Gate |
|---|---|---|---|---|---|---|---|---|
| 123 | feature/limitar-tentativas-login | ../<repo>-wt-limitar-tentativas-login | NOVA-FUNCIONALIDADE | implementando | sdd-codificador | 0 | — | — |

## Histórico
- <HH:MM> 123 — fase A concluída (4 REGs, 12 cenários, validação PRONTO na rodada 1)
- <HH:MM> 123 — tentativa 1 REVISAR: [D] repetição duplica registro; [E] cobertura abaixo do gate
```

## Regras

- Paralelismo máximo 3 IBs — respeite memória/CPU do build.
- Só o orquestrador marca `tasks.md`, faz commit/push e altera o ALM (só com o power `alm`); push ao fim de cada
  etapa, com confirmação, a partir do repositório principal; nunca merge, nunca `--force`.
- Nunca apagar worktree com trabalho não commitado.
- `status.md`: `git pull --rebase` antes de cada escrita e push logo depois — outras pessoas podem estar no mesmo
  IB fora do lote (regras de escrita no steering do power).
