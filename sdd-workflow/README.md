# sdd-workflow

Power do Kiro com um fluxo de **Spec-Driven Development** em três papéis assíncronos — **especificador**,
**codificador** e **testador** —, cada um exercido por uma pessoa ou por um agente, com gates humanos, devoluções com
causa raiz e aprendizado contínuo. Agnóstico de linguagem e de projeto: o que é do projeto fica num steering gerado
pela skill `sdd-setup`.

```
especificador  entrevista → HF/REG/ET/CT → validação V1–V10 → GATE 1 (pessoa) → publica no ALM (opcional)
codificador    spec SDD (EARS/design/tasks) → análise S1–S6 → implementação → judge A–N → GATE 2 (PR)
testador       executa os CTs no PR → GATE 3 (pessoa aprova e faz o merge) ou devolução com causa raiz
```

## Conteúdo

| Arquivo | Função |
|---|---|
| `plugin.json` | Manifesto e keywords de ativação |
| `steering/steering.md` | O processo: papéis, gates, fases, pasta/branch, devoluções, "o que dizer" — sempre carregado |
| `skills/sdd-setup/` | Configura o projeto (`.kiro/steering/sdd-projeto.md`), cria os agentes e o `.kiro/aprendizado/` |
| `skills/sdd-tarefa/` | Entrada de qualquer papel pela Task |
| `skills/sdd-especificar/` | Entrevista de decisões + HF, REG, ET e CT |
| `skills/sdd-validar-requisitos/` | Validação formal (V1–V10) e GATE 1 |
| `skills/sdd-alm-publicar-requisitos/` | Publica HF/REG/ET no DOORS Next (só com o power `alm`) |
| `skills/sdd-criar-spec/` | Spec SDD do Kiro (`requirements.md`, `design.md`, `tasks.md`) + análise S1–S6 |
| `skills/sdd-implementar-spec/` | Implementa o `tasks.md`, judge e PR (GATE 2) |
| `skills/sdd-revisar/` | Judge adversarial (rubrica A–N) |
| `skills/sdd-testar/` | Executa os CTs no PR e decide o GATE 3 |
| `skills/sdd-retrabalho/` | Devoluções, causa raiz, checklists pré-voo e promoção de regras |
| `skills/sdd-lote/` | Vários IBs em worktrees, por papel |
| `skills/sdd-status/` | Painel "onde parei" |
| `skills/sdd-planejamento/` | Planejamento ágil (backlog, Planning Poker, sprints, Excel) |
| `skills/sdd-alm-publicar-planejamento/` | Publica a sprint atual no EWM (só com o power `alm`) |

## Agentes

Powers não distribuem agentes. A `sdd-setup` cria em `.kiro/agents/` do projeto:

| Agente | Papel |
|---|---|
| `sdd-especificador` | documentação de um IB no lote |
| `sdd-codificador` | spec e implementação (delegando a executores do projeto, se houver) |
| `sdd-revisor` | judge, validação de requisitos e análise da spec — sem escrita |
| `sdd-orquestrador` | lote de IBs até o GATE 1 ou GATE 2 |

Para cada agente ela pergunta quais skills e MCPs já existentes (do projeto, do usuário ou de outros powers) ele pode
usar, e quais arquivos de steering usar quando o projeto não segue o padrão do Kiro (`product.md`, `tech.md`,
`structure.md`).

## Pré-requisitos

- Repositório git com uma branch base e PRs.
- Opcional: [`kiro-cli`](https://kiro.dev) (validação dos agentes), um MCP de consulta ao banco (somente leitura) e o
  power [`alm`](../alm/) (IBM ELM) para ler Tasks, publicar requisitos e planejamento.
- Planejamento: Python 3 com `openpyxl`.

## Primeiros passos

1. Instale o power pelo painel **Powers** do Kiro (pasta `sdd-workflow` deste repositório ou uma cópia local).
2. No projeto, peça **"configurar o sdd-workflow"** (`sdd-setup`) e responda às perguntas.
3. Comece pela Task: **"vamos trabalhar na task 123"** — ou **"onde parei?"**.

Depois de atualizar o power, peça "atualizar os agentes do sdd" para refazer os caminhos e prompts dos agentes.
Os agentes só usam caminhos relativos — `.kiro/...` (raiz do repositório) e `~/.kiro/...` (home) —, então os `.kiro/agents/*.json` versionados servem em Linux, macOS e Windows.

Sem o power `alm`, as Tasks são atendidas pelos ids do planejamento (`planejamento-agil/backlog.json`, gerado pela
`sdd-planejamento`): "vamos trabalhar na task T-03".

## Licença

[MIT](../LICENSE)
