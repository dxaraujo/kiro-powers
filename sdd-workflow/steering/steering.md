---
inclusion: always
---

# Fluxo SDD (power sdd-workflow)

Fluxo de **Spec-Driven Development** em três papéis assíncronos, com gates humanos, devoluções com causa raiz e
aprendizado contínuo. É agnóstico de linguagem e de projeto: tudo o que é do projeto (steering de produto,
tecnologia e estrutura, comandos de build/teste, branch base, banco, testes funcionais, executores) está em
**`.kiro/steering/sdd-projeto.md`**, gerado pela skill **`sdd-setup`**.

> Sem `.kiro/steering/sdd-projeto.md` no workspace → antes de qualquer skill `sdd-*`, ofereça rodar a `sdd-setup`
> ("configurar o sdd-workflow"). Ela também cria os agentes (`sdd-especificador`, `sdd-codificador`, `sdd-revisor`,
> `sdd-orquestrador`) — o power não traz agentes prontos.

Termos: **IB** = item de backlog (a funcionalidade, do P.O.); **Task** = o trabalho de um papel no IB. Com o power
**`alm`** (IBM ELM) eles são work items do EWM; sem ele, a pessoa informa os dados e o fluxo segue igual.

## Papéis e fluxo

Cada IB passa por três etapas **assíncronas**, cada uma com a sua Task. Cada papel pode ser exercido por uma
**pessoa** ou por um **agente** do Kiro — inclusive misturando. O sinal entre as etapas é o `status.md` do IB,
publicado na branch: quem pega a etapa seguinte olha a `fase` e começa, sem esperar ninguém.

| Papel | Task (prefixo padrão) | Skills | Agente que pode assumir |
|---|---|---|---|
| **Especificador** | `[ESPEC]` | `sdd-tarefa` → `sdd-especificar` → `sdd-validar-requisitos` (GATE 1) → `sdd-alm-publicar-requisitos` (se houver ALM) | `sdd-especificador` (+ `sdd-revisor` na validação) |
| **Codificador** | `[BE]` | `sdd-tarefa` → `sdd-criar-spec` (+ análise) → `sdd-implementar-spec` → `sdd-revisar` → PR (GATE 2) | `sdd-codificador` ou executor do projeto (+ `sdd-revisor` como judge) |
| **Testador** | `[QA]` | `sdd-tarefa` → `sdd-testar` → decide o PR (GATE 3) | qualquer agente com a skill `sdd-testar` |

Os prefixos das Tasks são configuráveis em `sdd-projeto.md`; `[BD]` (mudança de banco) fica fora do fluxo.

O especificador entrevista a pessoa sobre as decisões de negócio em aberto (uma pergunta por vez, registradas em
`decisoes.md`) e entrega **o quê** (negócio: HF, REG, ET, CT), validado como especificação formal. O codificador
decide **como** (requirements, design e tasks da spec SDD), porque depende do código: funcionalidades análogas,
componentes existentes, padrões e skills de código do projeto — e a spec passa por uma análise independente antes
do código. O testador executa a funcionalidade do PR e decide se ele é aprovado.

```
ESPECIFICADOR  sdd-especificar ─► sdd-validar-requisitos ─► ═ GATE 1 ═ ─► (ALM) publica + conclui [ESPEC]   fim
                     ▲                    │               requisitos            fase: especificado
                     └──── achados ◄──────┘ (≤ 2 rodadas)  aprovados
                                                                  ┊ status.md na branch (assíncrono)
CODIFICADOR    sdd-criar-spec ─► análise ─► sdd-implementar-spec ─► sdd-revisar (judge, retry ≤ 2) ─► ═ GATE 2 ═ PR
                                                                                  fase: em-teste
                                                                  ┊
TESTADOR       sdd-testar (CTs na branch do PR) ─┬─ aprovados ─► ═ GATE 3 ═ PR aprovado → merge → concluido
                                                 └─ reprovados ─► DEVOLUÇÃO (retrabalho → etapa de origem)
```

| Gate | Critério de saída | Quem libera |
|---|---|---|
| **GATE 1 — requisitos aprovados** | HF/REG/ET/CT com validação `PRONTO` (rubrica V1–V10), sem achado bloqueante não aceito | **sempre uma pessoa** (o especificador responsável) |
| **GATE 2 — PR aberto** | judge `APROVADO`; testes + cobertura (comandos do `sdd-projeto.md`) ok; PR da branch do IB para a branch base aberto | o codificador (a abertura do PR é confirmada por uma pessoa) |
| **GATE 3 — PR aprovado** | todos os CTs aprovados com evidência em `testes.md` | o testador decide; **uma pessoa** aprova o PR e faz o merge |

- GATE 1 e GATE 3 são humanos mesmo quando todos os papéis são agentes.
- Nenhuma etapa começa sem o gate anterior: a `sdd-tarefa` confere a `fase` do `status.md`.
- Ao fim de cada etapa, o `status.md` é commitado e a branch recebe push (com confirmação) — é assim que a etapa
  seguinte, em outra máquina, enxerga que pode começar.
- Vários IBs de uma vez: `sdd-lote` (especificação até o GATE 1, codificação até o GATE 2).

## ALM opcional

Todo passo de ALM (publicar HF/REG/ET no DOORS Next, links de rastreabilidade, comentários, mudar estado de Task)
só acontece **se o power `alm` (MCP `alm`) estiver disponível**, usando as skills dele (`alm-ccm`, `alm-rm`,
`alm-gc`) e os ids de `alm/pa_*.json`. Sem ele, o passo é registrado no `status.md` (`ALM: sem power — não
publicado`) e o fluxo segue — o ALM nunca trava o processo.

Com ALM: `[ESPEC]` conclui no GATE 1 (após publicar); `[BE]` e `[QA]` concluem no merge (GATE 3); uma devolução
reabre a Task do papel que recebe.

## Banco de dados fora do fluxo

Mudanças de esquema (DDL, Task `[BD]`) **não entram no fluxo**: são tratadas com quem administra o banco. A
necessidade é definida na ET (seção "Alterações de Banco") e acompanhada no `status.md` (campo `Banco (DDL)`:
`não se aplica | pendente | aplicada em dev | aplicada em prod`).

- Não bloqueia especificação nem codificação.
- **Bloqueia os testes** enquanto não estiver `aplicada em dev` (a `sdd-testar` para e informa).
- **Bloqueia a implantação** enquanto não estiver `aplicada em prod` (registrado no `status.md` e na descrição do PR).

## Devoluções e retrabalho

Toda reprovação **depois de um gate** é uma devolução e passa pela skill **`sdd-retrabalho`**, que classifica a
causa raiz, devolve à etapa onde está o erro e registra o retrabalho. Gatilhos:

| Gatilho | Quem detecta |
|---|---|
| Testes reprovados (CT falhou na execução do PR) | testador (`sdd-testar`) |
| PR rejeitado na revisão humana | pessoa que revisa o PR |
| Documentação incompleta ou errada descoberta na codificação | codificador (`sdd-criar-spec` ou `sdd-implementar-spec`) — **sempre registrada** |
| Correção pedida sobre algo já aceito | qualquer pessoa |

Rota pela causa raiz:

| Causa raiz (categoria) | Volta para | Depois percorre de novo |
|---|---|---|
| código — `FALHA_IMPLEMENTADOR`, `FALHA_JUDGE_SEVERIDADE`, `FALHA_STEERING` no código | codificador (`sdd-implementar-spec`, modo correção) | judge → PR atualizado (GATE 2) → testes (GATE 3) |
| spec SDD — `FALHA_SPEC` (estava na HF/REG/ET e o codificador não levou para a spec) | codificador (`sdd-criar-spec`) | implementação → judge → GATE 2 → GATE 3 |
| documentação — `FALHA_DOC` (HF/REG/ET/CT incompleta ou errada) | especificador (`sdd-especificar` → `sdd-validar-requisitos`) | GATE 1 (só o que mudou) → republicação (se ALM) → spec e codificação* → GATE 2 → GATE 3 |
| decisão nova — `MUDANCA_ESCOPO` | P.O. decide (nova Task/IB ou ajuste de escopo) | não é retrabalho; não volta pelo fluxo |

\* Só o CT estava errado e o código está certo → o especificador corrige o CT e o IB volta direto para `em-teste`.

**Cada papel que refaz trabalho registra a sua entrada** em `.kiro/aprendizado/retrabalho.md`: a do papel onde
estava o erro é a **causa raiz**; as dos papéis seguintes são **induzidas** (apontam para a causa raiz). Só a causa
raiz alimenta checklists e promoções; as induzidas medem o custo da falha.
Regras promovidas (3 ocorrências) vão para a seção **Regras promovidas** do `sdd-projeto.md` — cada skill
`sdd-*` as aplica como parte dela.

## O que dizer

| Quero… | Diga | Skill / agente |
|---|---|---|
| configurar o fluxo no projeto (agentes, comandos, steering) | "configurar o sdd-workflow" | `sdd-setup` |
| pegar minha Task (qualquer papel) | "vamos trabalhar na task 123" | `sdd-tarefa` |
| documentar os requisitos | "gera a HF / as REGs / a ET / os CTs" | `sdd-especificar` |
| validar e aprovar os requisitos (GATE 1) | "valida os requisitos" | `sdd-validar-requisitos` |
| publicar no ALM (se houver power) | "publica a documentação no ALM" | `sdd-alm-publicar-requisitos` |
| gerar a spec SDD (codificador) | "gera a spec" | `sdd-criar-spec` |
| implementar e abrir o PR (GATE 2) | "implementa" (ou "Start task" no `tasks.md`) | `sdd-implementar-spec` → `sdd-codificador` / executor do projeto |
| revisar (judge) | "revisa o IB 123" | `sdd-revisar` / agente `sdd-revisor` |
| testar o PR e decidir (GATE 3) | "executa os CTs" | `sdd-testar` |
| registrar PR aprovado/mergeado ou rejeitado | "PR do IB 123 aprovado" · "PR rejeitado: <motivo>" | `sdd-testar` (merge) · `sdd-retrabalho` (rejeição) |
| devolver / corrigir algo já aceito | "faltou X no que foi feito" | `sdd-retrabalho` |
| vários IBs | "especifica os IBs da sprint" · "implementa os IBs especificados" | `sdd-lote` / agente `sdd-orquestrador` |
| ver onde parei / de quem é a vez | "onde parei?" | `sdd-status` |
| planejar sprints | "monta o planejamento" · "virada de sprint" · "publica a sprint no ALM" | `sdd-planejamento` · `sdd-alm-publicar-planejamento` |

Padrões de código: as skills de código do projeto que a `sdd-setup` ligou a cada agente (listadas em
`sdd-projeto.md`) — carregue a do artefato **antes** de escrevê-lo.

## Pasta e branch

- **Pasta:** `.kiro/specs/ib-<id>-<slug>/` — uma por IB, compartilhada pelos três papéis.
  Defeito ou Task avulsa (sem IB pai): `.kiro/specs/task-<id>-<slug>/`.
  `<slug>` = kebab-case curto do título, sem acentos (ex.: `ib-123-limitar-tentativas-login`).
- **Branch:** `<prefixo><funcionalidade>` a partir da branch base (ambos em `sdd-projeto.md`; padrão `feature/`),
  criada pelo especificador. A `sdd-tarefa` **sugere** o nome (kebab-case do título do IB, ≤ 40 chars) e **aguarda
  a confirmação**. É a mesma branch para documentação, spec, código e evidências de teste — um único PR.
- Pasta e branch ficam registradas no `status.md`; quem assume um papel chega a elas pela Task → IB pai.

| Arquivo | Gerado por | Conteúdo |
|---|---|---|
| `status.md` | `sdd-tarefa` (atualizado por todas) | IB, papéis (pessoa ou agente), branch, fase, ALM, Banco (DDL), artefatos, validação, devoluções, PR |
| `decisoes.md` | `sdd-especificar` (entrevista) | Decisões de negócio `D-<nn>`: pergunta, decisão, quem decidiu, situação |
| `HF.md` | `sdd-especificar` | História funcional — narrativa + cenários Gherkin |
| `REG-<nn>-<slug>.md` | `sdd-especificar` | Uma regra de negócio por arquivo |
| `ET.md` | `sdd-especificar` | Dados, interfaces, operações, integrações, alterações de banco |
| `CT.csv` | `sdd-especificar` | Casos de teste (importáveis no ALM QM) |
| `validacao-<N>.md` | `sdd-validar-requisitos` | Relatório da validação formal (rubrica V1–V10) por rodada |
| `requirements.md` | `sdd-criar-spec` (codificador) | Requisitos EARS rastreados à HF/REG |
| `design.md` | `sdd-criar-spec` (codificador) | Pattern grounding, reaproveitamento, componentes, decisões técnicas, riscos |
| `tasks.md` | `sdd-criar-spec` (codificador) | Checklist Kiro (`- [ ] N.` + `_Requisitos: x.y_`) |
| `analise-spec-<N>.md` | `sdd-revisor` (análise da spec) | Análise da spec SDD antes do código (rubrica S1–S6) |
| `revisao-<N>.md` | `sdd-revisar` | Relatório do judge |
| `testes.md` | `sdd-testar` | Execução dos CTs por rodada: resultado e evidência de cada um |

## Ciclo de status dos artefatos

`rascunho → aprovado → publicado → implementado`

- **aprovado** só no GATE 1 (artefato alterado numa devolução volta a `rascunho` e é reaprovado). A spec SDD é
  aprovada pelo próprio codificador ao fim da `sdd-criar-spec` (o judge a confronta com o código).
- **publicado** quando o artefato tem ID no ALM (sem ALM, fica `aprovado`).
- **implementado** quando o judge emitiu `APROVADO` para o código.

## Fases (`status.md` → campo `fase`)

`documentando → validando → aguardando-aprovacao → especificado → planejando → implementando → em-revisao → em-teste → concluido`

| Fase | Significa | Vez de |
|---|---|---|
| `documentando`, `validando`, `aguardando-aprovacao` | requisitos / validação / GATE 1 | especificador |
| `especificado` | GATE 1 liberado — pronto para codificar | codificador |
| `planejando` | codificador gerando a spec SDD | codificador |
| `implementando`, `em-revisao` | codificação / judge | codificador |
| `em-teste` | GATE 2 liberado — PR aberto, aguardando os testes | testador |
| `concluido` | GATE 3 — testes aprovados, PR aprovado e mergeado | — |
| `bloqueado` | 2 reprovações do judge ou erro de ambiente | pessoa responsável pelo IB (decide o próximo passo) |

Devolução → a fase volta para a do papel que recebe (`documentando` ou `implementando`), e o `status.md` registra
a devolução (seção **Devoluções**).

## Convenções

- **Escrita no `status.md`** (cada IB tem o seu; o risco é entre papéis do mesmo IB):
  - só o papel da fase atual escreve (tabela "Vez de"); exceções: o gate que muda a fase e a devolução registrada
    por quem a detectou;
  - antes de escrever, `git pull --rebase`; depois, commit e push na hora (commit pequeno só do `status.md` quando
    não houver outro artefato junto);
  - Histórico só por acréscimo, sempre no fim — nunca editar linhas antigas;
  - conflito: mantenha os campos do remoto e reaplique só a sua mudança; se o campo `fase` divergir, vale a do
    registro mais recente no Histórico — avise a pessoa antes de seguir.
- Commit: padrão do `sdd-projeto.md` (padrão: `Task <id> - <verbo no infinitivo> <descrição>`) — `<id>` é a Task
  **do papel que fez o trabalho** (`[ESPEC]` para documentação, `[BE]` para spec SDD e código, `[QA]` para
  evidências de teste), seja pessoa ou agente.
- Agente nunca faz merge nem `--force`; push só com confirmação de uma pessoa. Merge: só a pessoa que aprova o PR.
- Toda alteração no ALM (estado, responsável, comentário) só com "sim" de uma pessoa — e só se houver ALM.
- Banco (MCP de consulta do `sdd-projeto.md`): **somente leitura** — exceto os scripts de massa de teste
  declarados no `sdd-projeto.md`, executados pelo testador.
- Nunca invente tabela, coluna, classe, endpoint ou regra: confirme no código, no banco ou na documentação.
- Aprendizado do time: `.kiro/aprendizado/` (versionado). Estado local de lote: `.kiro/local/` (gitignored).
