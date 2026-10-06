---
name: "sdd-implementar-spec"
description: "Papel codificador do fluxo SDD — depois da spec criada pela sdd-criar-spec (a partir dos requisitos aprovados no GATE 1), implementa o tasks.md do IB: delega cada item ao executor configurado no sdd-projeto.md (agente do projeto ou sdd-codificador) ou o faz com as skills de código do projeto, roda os testes e o gate de cobertura, passa pelo judge (sdd-revisar) e abre o PR (GATE 2), que o testador vai testar e decidir. Também corrige devoluções (testes reprovados, PR rejeitado) e devolve ao especificador falhas encontradas na documentação. Use em \"implementa a task 123\", \"implementa a spec\", \"executa as tasks\", \"continua a implementação\", \"abre o PR\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "implementar, implementar spec, executar tasks, codificar, codificacao, implementa a task, continuar implementacao, start task, desenvolver, abrir pr, pull request, pr aprovado, pr rejeitado, merge"
---

# sdd-implementar-spec — Codificação, PR e devoluções (papel codificador)

Entrada: `.kiro/specs/ib-<id>-<slug>/` com `requirements.md`, `design.md`, `tasks.md` criados pela `sdd-criar-spec`
(o primeiro passo do codificador), na branch do `status.md` — normalmente via `sdd-tarefa` com a Task do codificador.
No Kiro, cada item do `tasks.md` também pode ser executado pelo botão **"Start task"** — as regras valem igual.
O papel pode ser de uma pessoa ou de um agente; os pontos marcados "pessoa" exigem confirmação humana.
Comandos, branch base, executores e ferramenta de PR: `.kiro/steering/sdd-projeto.md`.

## Modo

- **Manual** (padrão): apresenta o plano, aguarda "ok", marca `tasks.md` item a item.
- **Orquestrado** (`ORCHESTRATED=true`, pelo `sdd-orquestrador`): sem confirmações, **não marca** `tasks.md`,
  trabalha só na worktree informada; no retry corrige **apenas** os gaps recebidos.

## Passo 0 — Onde estou

`git status` limpo e branch = a do `status.md` (senão avise e pare); `git pull --ff-only`. Pela `fase`:

| Fase | Vá para |
|---|---|
| `especificado`, `planejando`, ou sem `tasks.md` | **`sdd-criar-spec`** primeiro (cria a spec) e depois volte aqui |
| `implementando`, `em-revisao` | Passo 1 (retome do primeiro item pendente do `tasks.md`) |
| `bloqueado` | Passo 4.1 |
| `em-teste` | nada a fazer: o PR está com o testador (GATE 3) — aguarde o resultado ou uma devolução |
| antes de `especificado` | pare: os requisitos ainda não foram aprovados (GATE 1) |

- **Devolução aberta** na seção **Devoluções** do `status.md` → acione **`sdd-retrabalho`** em modo recebimento
  (registra a causa raiz ou a induzida) e trabalhe **só** nos itens da devolução e nos itens novos/alterados do
  `tasks.md`.
- Checklist pré-voo: se existir `.kiro/aprendizado/checklists/sdd-implementar-spec.md`, considere os itens.
- Leia os steering de estrutura e tecnologia (apontados no `sdd-projeto.md`) e o `design.md` inteiro (tabela de
  pattern grounding).

## Passo 1 — Plano (modo manual)

```
📋 Implementação — IB <id> · Task <id>
Itens pendentes: <N> (de <M>) · Devolução: <R-nnn — resumo | nenhuma>
Executores: <item → executor da tabela Executores | sdd-codificador | direto com skills>
Análogo: <do design.md>
Ok para iniciar?
```

`fase: implementando` e papel Codificador `em andamento` no `status.md`.

## Passo 2 — Executar

| O item… | Quem executa |
|---|---|
| casa com uma linha da tabela **Executores** do `sdd-projeto.md` | o subagente/skill indicado, com a pasta do IB e os itens no prompt |
| demais itens de código | subagente **`sdd-codificador`** (ou você mesmo, carregando a skill de código do artefato **antes** de escrever) |
| testes e cobertura | as skills de teste do projeto (se houver) e os comandos do `sdd-projeto.md` |
| massa de teste funcional | a convenção do `sdd-projeto.md` (Testes funcionais), a partir do CT |

> Subagente começa sem o seu contexto: passe a pasta do IB, os itens, a worktree/branch e as regras inegociáveis.
> Sem ferramenta de subagente, faça você mesmo, em sequência.

DDL (ET "Alterações de Banco") está fora do fluxo e não bloqueia a codificação — implemente com as colunas novas e
teste no banco de teste do projeto; o `Banco (DDL)` do `status.md` só bloqueia os testes e a implantação.

Regras de implementação:
- **Imite o análogo** do `design.md`; nada de padrão novo sem perguntar.
- Banco pelo MCP de consulta **somente leitura**; respeite as regras críticas do `sdd-projeto.md`.
- Corretiva: escreva primeiro o teste que reproduz o defeito e veja-o falhar.
- Ao concluir cada item (modo manual): compile/cheque (comando do `sdd-projeto.md`) e marque `- [x]`.

### 2.1 — Falha na spec ou na documentação

- **A spec (sua) está errada ou incompleta, mas a documentação diz o certo** → corrija a spec pela
  **`sdd-criar-spec`** (é ajuste do próprio codificador; se o PR já foi aberto — GATE 2 —, é devolução `FALHA_SPEC`).
- **A documentação está incompleta ou errada** (falta regra para decidir, coluna que não existe, cenário que
  contradiz a REG) → **não decida no código.** Acione **`sdd-retrabalho`** em modo devolução com gatilho "falha na
  spec na codificação": ela registra o retrabalho (`FALHA_DOC`), devolve ao especificador e reabre a Task dele.
  O que já foi implementado e não depende do ponto em aberto fica commitado
  (ex.: `Task <id> - Implementar parcialmente <…>`).

## Passo 3 — Validar

Rode os comandos de **testes** e de **cobertura** do `sdd-projeto.md` e confira o gate nas classes/arquivos em
escopo (fora as exclusões declaradas).

Falha → corrija e rode de novo. Erro de ambiente (banco, rede, dependência indisponível) → reporte como AMBIENTE,
não "conserte" o ambiente.

## Passo 4 — Revisão (judge)

`fase: em-revisao`. Rode a revisão isolada: agente **`sdd-revisor`** (sem escrita) recebendo só a pasta do IB e o
diff (`git diff origin/<base>...HEAD`). Sem agente disponível, use a skill **`sdd-revisar`** — sem usar o
seu raciocínio de implementação como evidência.

- `VEREDITO: APROVADO` → Passo 5 (abrir o PR).
- `VEREDITO: REVISAR` → corrija **só** os gaps e volte ao Passo 3. Gap que é falha da spec → Passo 2.1.
- 2ª reprovação → `fase: bloqueado` e Passo 4.1.

### 4.1 — Bloqueado (decisão de uma pessoa)

Apresente o histórico de vereditos (`revisao-<N>.md`) e as opções; a pessoa responsável pelo IB decide:
1. **Corrigir com orientação** — a pessoa indica o caminho; zera os retries e volta ao Passo 2.
2. **Devolver à especificação** — os gaps vêm da spec → Passo 2.1.
3. **Aceitar a exceção** — a pessoa aceita explicitamente os achados restantes (registre no `status.md` e no
   `revisao-<N>.md`: quem aceitou e por quê) → Passo 5.

## Passo 5 — GATE 2: abrir o PR

Todos os itens `[x]`; nenhuma devolução `aberta`; `status.md`: Spec SDD `implementado`, papel Codificador `entregue
<data>`, linha no Histórico.

1. `git pull --ff-only`; confirme que a branch está atualizada com `origin/<base>` (se não, pergunte se faz merge
   da branch base na branch antes; conflito → resolva e repita os Passos 3 e 4).
2. Gere o texto do PR:
   ```
   Título: Task <id> - <descrição>   (IB <id> — <título>)
   Descrição:
   - IB <id> · Tasks: especificador <id> · codificador <id> · testador <id>
   - Requisitos: HF · REG-01..N · ET (ALM: <IDs | pendente — publicar com o power alm | sem power — não publicado>)
   - Spec: .kiro/specs/ib-<id>-<slug>/ (requirements · design · tasks)
   - Judge: revisao-<N>.md (APROVADO) · testes + cobertura: ok
   - Testes funcionais: pendentes — o testador executa os CTs (.kiro/specs/ib-<id>-<slug>/CT.csv) e decide o PR
   - Massa de teste: <caminho | n/a> · Banco (DDL): <não se aplica | pendente | aplicada em dev | aplicada em prod>
     (pendente/dev → implantação bloqueada até a DDL em produção)
   - Devoluções: <R-nnn… | nenhuma>
   ```
3. Numa só confirmação (pessoa): commit no padrão do `sdd-projeto.md`, push e abertura do PR da branch do IB →
   branch base com a ferramenta do `sdd-projeto.md`. Sem ferramenta por linha de comando → entregue o título e a
   descrição prontos para a pessoa abrir.
4. `status.md`: `fase: em-teste`, link do PR, linha no Histórico; commit e push do `status.md` — é o sinal assíncrono
   para o testador.
5. Com power ALM (opcional): comentário na Task do testador (`PR aberto para teste: <link> · Comece com: "vamos
   trabalhar na task <id>"`). A Task do codificador **continua aberta**: fecha no merge (GATE 3).

- Push recusado → informe e pare; nunca `--force`.

## Passo 6 — Devolução depois do PR

O PR é decidido pelo testador (`sdd-testar`, GATE 3). Testes reprovados ou PR rejeitado na revisão humana chegam
como **devolução** (`sdd-retrabalho`): o IB volta a `implementando` com os itens `[R-<nnn>]`. Corrija pelos Passos
1–4 (o judge reavalia o IB inteiro) e repita o Passo 5 — o mesmo PR é atualizado com os novos commits e o IB volta
a `em-teste`.

## Regras

- Nunca merge, nunca `--force`; push só com confirmação. O merge é da pessoa que aprova o PR (GATE 3).
- Nada de decidir no código o que a spec não diz — Passo 2.1.
- Correção sobre algo já aceito sempre passa por **`sdd-retrabalho`** antes de alterar.
