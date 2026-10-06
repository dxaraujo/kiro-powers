---
name: "sdd-retrabalho"
description: "Devoluções e aprendizado contínuo do fluxo SDD — toda reprovação depois de um gate (testes reprovados, PR rejeitado, falha na spec descoberta na codificação, correção pedida sobre algo aceito) passa por aqui: classifica a causa raiz (código, spec SDD, documentação ou mudança de escopo), devolve ao papel certo (especificador ou codificador) com a fase e a Task do ALM (se houver) reabertas, registra o retrabalho de cada papel que refaz trabalho (causa raiz e induzidos) em .kiro/aprendizado/retrabalho.md, alimenta o checklist pré-voo e propõe promoção a regra após 3 ocorrências. Use em \"PR rejeitado\", \"teste reprovado\", \"faltou X\", \"isso foi retrabalho\", \"devolver para especificação\", \"resumo do aprendizado\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "retrabalho, devolucao, devolver, pr rejeitado, teste reprovado, faltou, nao ficou certo, causa raiz, aprendizado, checklist, promocao, melhoria continua"
---

# sdd-retrabalho — Devoluções e aprendizado

Regras do processo: o steering do power `sdd-workflow` (seção **Devoluções e retrabalho**).
Arquivos: `.kiro/aprendizado/retrabalho.md` (log, só acréscimo), `.kiro/aprendizado/checklists/<skill>.md`,
`.kiro/aprendizado/promocoes/`. Formatos nos READMEs de cada pasta.

## Quando age

| Modo | Quando | Quem chama |
|---|---|---|
| **Devolução** | testes reprovados · PR rejeitado na revisão humana · codificador acha falha na spec/documentação · correção pedida sobre algo aceito | `sdd-testar`, `sdd-implementar-spec`, a pessoa diretamente |
| **Recebimento** | um papel começa a refazer trabalho por causa de uma devolução | `sdd-especificar`, `sdd-criar-spec`, `sdd-implementar-spec`, `sdd-testar` (Passo 0 de cada uma) |
| **Resumo** | "resumo do aprendizado" e ao fim de cada lote | pessoa / `sdd-lote` |

Antes de um gate não há retrabalho: achados da `sdd-validar-requisitos` antes do GATE 1 e reprovações do judge
antes do GATE 3 são o ciclo normal (a validação alimenta o checklist da `sdd-especificar` direto; o judge tem retry próprio).
Já **toda devolução do codificador ao especificador** (depois do GATE 1) é retrabalho e é sempre registrada.

## Modo devolução

### 0. Achar o IB

Sem a pasta do IB na branch atual (a pessoa costuma informar só a Task ou o IB), localize-a por
[localizar-ib.md](../sdd-tarefa/references/localizar-ib.md) — `status.md` nas worktrees e nas branches remotas;
sem ALM e sem pasta, o planejamento. Achou em outra branch → pergunte se troca para ela (mesmo texto e regras da
`sdd-tarefa`, Passo 3.2: alteração local não commitada → avise e pare). Não achou → peça o IB e pare; não
classifique nem registre nada sem o `status.md`.

Anote a **Task do papel que detectou** (quem chamou: `[QA]` em testes reprovados e PR rejeitado no teste, `[BE]`
quando o codificador acha falha na documentação, a Task de quem pediu a correção) — é ela que vai no commit.

### 1. Evidência — onde estava a informação?

Para cada problema (cada CT reprovado ou motivo de rejeição do PR é um item), consulte na ordem e anote
`consta: arquivo:linha` ou `não consta`:

1. `requirements.md` / `design.md` / `tasks.md` do IB
2. `HF.md` / `REG-*.md` / `ET.md` / `CT.csv`
3. A Task/IB no ALM (descrição, comentários), o código existente e o banco (MCP de consulta, somente leitura)
4. Steering (`.kiro/steering/*.md`, inclusive `sdd-projeto.md`) e skills de código do projeto
5. `retrabalho.md` — já aconteceu algo parecido?

### 2. Classificar a causa raiz (proposta; quem confirma é uma pessoa)

| Se a informação… | Categoria | Papel da causa raiz |
|---|---|---|
| estava na spec e o código não fez | `FALHA_IMPLEMENTADOR` | codificador |
| estava na spec, o código errou e o judge aprovou | `FALHA_JUDGE_SEVERIDADE` (+ letra da rubrica) | codificador (judge) |
| era convenção do steering/skill e o código violou | `FALHA_STEERING` | codificador |
| estava na HF/REG/ET e não foi para a spec SDD | `FALHA_SPEC` | codificador (`sdd-criar-spec`) |
| estava no ALM/código/banco e não entrou na HF/REG/ET/CT, ou a documentação estava errada (inclusive o CT) | `FALHA_DOC` | especificador (`sdd-especificar`; a validação deixou passar) |
| não estava em lugar nenhum, mas o time sempre faz assim | `PREFERENCIA_NAO_DOCUMENTADA` | papel onde deveria estar (vira candidato a steering) |
| não estava em lugar nenhum — decisão nova | `MUDANCA_ESCOPO` | P.O. — **não é retrabalho**: encerre sem registrar e sugira nova Task/IB |

```
🔎 Devolução — IB <id> · gatilho: <testes reprovados | PR rejeitado | falha na spec | correção pedida>
| # | Problema | Evidência | Categoria proposta | Volta para |
| 1 | CT004: pedido cancelado foi faturado | REG-02 consta; código não filtra a situação | FALHA_IMPLEMENTADOR | codificador |
| 2 | PR: falta tratar reexecução | HF não tem cenário de reexecução | FALHA_DOC | especificador |
Confirma? ("ok" ou corrija por item)
```

A pessoa confirma ou corrige a categoria e **a decisão dela prevalece**: sem evidência escrita, avise uma vez o
risco (ex.: "sem registro, pode ser `MUDANCA_ESCOPO`") e, se ela mantiver, registre com a evidência que ela informou
(`Evidência: informado por <pessoa> — <fonte>`). Não recuse nem re-pergunte a mesma classificação.

Itens com destinos diferentes → a devolução vai ao papel **mais a montante** (especificador antes de codificador):
a partir dali o IB passa de novo por todos os papéis seguintes, levando todos os itens.

### 3. Registrar a causa raiz

Acrescente ao final de `retrabalho.md` uma entrada **causa raiz** por item confirmado (formato do arquivo, com
o próximo `R-<nnn>`; `Responsável` = o responsável do papel da causa raiz na tabela **Papéis** do `status.md` — não
invente `agente:<nome>`), e atualize **obrigatoriamente** o checklist da skill culpada (sem o checklist atualizado
a devolução não está registrada — liste na confirmação os arquivos de checklist que vão mudar):
`FALHA_IMPLEMENTADOR`/`FALHA_STEERING` → `sdd-implementar-spec` · `FALHA_JUDGE_SEVERIDADE` → `sdd-revisar` ·
`FALHA_SPEC` → `sdd-criar-spec` · `FALHA_DOC` → `sdd-especificar` **e** `sdd-validar-requisitos` (a falha passou pela validação). Mesmo achado já listado → incremente e some a Task; novo →
acrescente a linha. Expire itens sem reincidência nas últimas 10 Tasks registradas.

### 4. Devolver

1. `git pull --rebase` antes de escrever (a devolução é uma das exceções em que quem detecta escreve fora da sua
   fase — regras de escrita em steering do power). `status.md`: seção **Devoluções** (`R-<nnn> | gatilho | causa | volta para | situação: aberta`), `fase` →
   `documentando` (especificador) ou `implementando` (codificador); papel que recebe → `devolvido <data>`;
   artefatos que vão mudar → `rascunho`; `Retries do judge` → 0.
2. Numa só confirmação: commit `Task <id da Task do papel que detectou, anotada no passo 0> - Registrar devolução
   R-<nnn>` — **não** a Task do papel que recebe (ex.: CT reprovado → `Task <[QA]> - …`, nunca a `[ESPEC]`) —
   com `status.md`, `retrabalho.md`, os checklists e `testes.md` ou o motivo do PR, + push (é o sinal assíncrono para quem recebe) + comentário no PR, se ele já existir.
   Com power ALM: comentário na Task do papel que recebe (`Devolução R-<nnn>: <resumo> — ver status.md`) e reabrir
   essa Task (ação de `ccm_list_workitem_states`, ex.: Reabrir/Refazer). A Task do codificador continua aberta até o merge.
3. Informe o próximo passo: especificador → `sdd-tarefa` com a Task `[ESPEC]` (corrige pela `sdd-especificar`, valida
   pela `sdd-validar-requisitos`, novo GATE 1 e republicação, se houver ALM); codificador → `sdd-tarefa` com a `[BE]`
   (corrige, judge e atualiza o mesmo PR). Só o CT estava errado (código certo) → o especificador corrige o CT,
   refaz o GATE 1 do CT e o IB volta direto para `em-teste`.

## Modo recebimento (cada papel que refaz trabalho)

No Passo 0 da skill do papel, se o `status.md` tem devolução `aberta` que passa por ele:

1. Este papel é o da **causa raiz** → a entrada já existe; só referencie `R-<nnn>` no Histórico.
2. Não é (ex.: o codificador refazendo porque a documentação mudou; o testador reexecutando os CTs) → acrescente uma
   entrada **induzida** em `retrabalho.md` (`Origem: induzido por R-<nnn>`, papel, o que precisou refazer). Não
   atualize checklist com induzidas.
3. Ao passar o seu gate, marque na seção **Devoluções**: `<papel> refez em <data>`. A devolução fecha
   (`situação: resolvida`) quando os testes do IB são aprovados de novo (GATE 3).

## Modo resumo

```
📊 Aprendizado — <N> registros desde <data> (<N> causas raiz · <N> induzidos)
Causas raiz por categoria: FALHA_IMPLEMENTADOR <n> · FALHA_JUDGE_SEVERIDADE <n> · FALHA_SPEC <n> · FALHA_DOC <n> · …
Custo (induzidos por causa raiz): FALHA_DOC → <n> refações · …
Por rubrica: D <n> · E <n> · …   ·   Por gatilho: testes <n> · PR <n> · codificação <n>
Perto de promoção (2 ocorrências): <itens>
```

## Promoção (≥ 3 causas raiz em Tasks distintas)

```
📈 Candidato a regra permanente
Achado: "<…>" — <N> ocorrências (Tasks <a>, <b>, <c>; responsáveis <…>)
Destino proposto: <sdd-projeto.md → Regras promovidas (por skill) | steering do projeto | skill de código do projeto>
Diff proposto:
<trecho exato>
Aplicar? ("ok")
```

"ok" → aplique o diff, crie `promocoes/<data>-<slug>.md`, remova o item do checklist. As skills `sdd-*` vêm do
power e não são editadas no projeto: regra de uma skill do fluxo ou da rubrica do judge vai para a seção
**Regras promovidas** do `.kiro/steering/sdd-projeto.md` (sempre carregada), sob o nome da skill. Ocorrências todas do mesmo
responsável (pessoa ou agente) → avise que pode ser particularidade dele antes de propor.

## Regras

- Nada é gravado nem devolvido sem confirmação de uma pessoa; promoção sempre com "ok" explícito.
- `retrabalho.md` nunca é reescrito — só acréscimo.
- `MUDANCA_ESCOPO` nunca vira aprendizado (o fluxo não deve aprender a antecipar o que não foi pedido).
- Uma devolução nunca pula papéis: depois da correção, o IB passa de novo por todos os gates seguintes.
