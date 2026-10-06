---
name: "sdd-criar-spec"
description: "Primeiro passo do codificador no fluxo SDD (com análise independente pelo sdd-revisor antes de codificar) — a partir dos requisitos aprovados do IB (HF/REG/ET/CT, GATE 1 — fase especificado) e do conhecimento do código (funcionalidades análogas, componentes existentes, steering e skills de código do projeto), cria a spec SDD no formato nativo do Kiro: requirements.md em EARS, design.md com pattern grounding e tasks.md executável pelo \"Start task\". Falta ou erro de negócio na documentação nunca é resolvido na spec: vira devolução ao especificador pela sdd-retrabalho (retrabalho sempre registrado). Em devoluções acrescenta itens [R-nnn] ao tasks.md. Use quando o codificador pegar a Task [BE] (\"gera a spec\", \"cria a spec\", \"gera as tasks\", \"planeja a implementação\")."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "spec, sdd, requirements, design, tasks, criar spec, gerar spec, gerar tasks, plano de implementacao, ears, planejar implementacao, codificador"
---

# sdd-criar-spec — Spec SDD do IB (papel codificador)

Entrada: pasta `.kiro/specs/ib-<id>-<slug>/` com `status.md` em `especificado` (GATE 1) e a documentação aprovada
(HF/REG/ET/CT). Saída: `requirements.md`, `design.md`, `tasks.md` — e o IB em `implementando`.
Leia antes: `.kiro/steering/sdd-projeto.md` e os steering de **estrutura** e **tecnologia** que ele aponta (stack,
pastas, padrões, regras de codificação, regras críticas).

**Fronteira:** a documentação diz **o quê** (negócio); a spec diz **como** (técnica). Decisões técnicas — que
funcionalidade imitar, que componente reaproveitar, que módulo/classe criar, que padrão aplicar — são **suas**.
Informação de negócio que falta ou está errada não é sua para decidir: é devolução (Passo 1.5).

## Passo 0 — Pré-condições

- `fase: especificado` (ou `implementando` com devolução aberta para o codificador) — antes disso, pare.
- `fase: planejando`, papel Codificador `em andamento`. Devolução aberta → **`sdd-retrabalho`** em modo
  recebimento.
- Checklist pré-voo: se existir `.kiro/aprendizado/checklists/sdd-criar-spec.md`, considere os itens.

## Passo 1 — Pattern grounding (obrigatório, antes de escrever)

1. Identifique o módulo/área (steering de estrutura) e **1–2 funcionalidades análogas reais** (mesmo tipo de
   entrada/saída, mesma camada, mesmo banco). Leia os arquivos de cada uma de ponta a ponta.
2. Procure o que já existe e pode ser reaproveitado: serviços, utilitários, repositórios/queries, componentes
   compartilhados, clientes de integração.
3. Para alteração/corretiva, leia todos os arquivos que a ET aponta.
4. Confirme no código cada nome que vai citar (arquivo, classe, função, rota, query, configuração). **Nada
   inventado:** o que não existir aparece como "a criar".

## Passo 1.5 — A documentação basta?

Cruzando HF, REGs, ET, código e banco, encontrou falta ou erro **de negócio**? Exemplos: regra sem definição,
valor de domínio sem significado, coluna citada que não existe, cenário que contradiz uma REG, exceção sem
comportamento definido.

→ **Pare** e acione **`sdd-retrabalho`** em modo devolução, gatilho "falha na spec na codificação", um item por
falta (com evidência). Ela registra o retrabalho (`FALHA_DOC`, causa raiz no especificador), devolve ao
especificador e reabre a Task do especificador. Isso vale **sempre** — inclusive no lote — mesmo que você "saiba"
a resposta: o que não está na documentação aprovada não pode virar regra no código.

Não é devolução (decida e registre no `design.md`): escolha técnica entre alternativas equivalentes, reuso de
componente, nome de classe/arquivo, ordem de execução, tratamento técnico que não muda o resultado de negócio.

## Passo 2 — requirements.md

~~~markdown
# Requisitos — IB <id>: <título>

## Introdução
<2–4 frases: o que muda e por quê. Fonte: HF + REGs.>

## Requisitos

### Requisito 1 — <nome>
**História:** Como <ator da HF>, quero <…>, para <…>.
**Origem:** HF cenários 1.1–1.3 · REG-01

#### Critérios de aceite
1. QUANDO <evento/condição> ENTÃO o sistema DEVE <efeito verificável>.
2. SE <condição de exceção> ENTÃO o sistema DEVE <rejeitar / registrar / desfazer / abortar>.
3. ENQUANTO <estado> o sistema DEVE <invariante>.
~~~

- Um requisito por grupo de cenários da HF (ou por REG); critérios numerados `N.M` — o `tasks.md` cita esses números.
- **Sempre** incluir: requisito de repetição/reexecução segura (idempotência) quando houver escrita, e de registro
  de log/auditoria/erro.
- Todo cenário Gherkin da HF e toda REG aparecem em algum critério (rastreabilidade completa). Não acrescente
  regra de negócio que não esteja na documentação.

## Passo 3 — design.md

~~~markdown
# Design — IB <id>: <título>

## Visão geral
<Abordagem em 3–6 linhas.>

## Padrões a seguir (pattern grounding)
| Categoria | Referência real | Padrão aplicado |
|---|---|---|
| <camada / tipo de componente> | `<caminho/do/arquivo>` | <o que é imitado> |

## Reaproveitamento
| Componente existente | Uso nesta implementação |
|---|---|

## Componentes
| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `<caminho/do/arquivo>` | criar \| alterar | <…> |

## Dados e interfaces
Queries, escritas e contratos: ver ET (Q01…, W01…, Interfaces). Bancos/conexões/transações por componente.

## Erros, transação e reexecução
<o que é rejeitado, o que vira log, o que desfaz/aborta; como a repetição evita duplicar.>

## Decisões técnicas
<escolhas feitas no Passo 1.5 que não eram de negócio, com o motivo.>

## Testes
| Arquivo/classe em escopo | Cenários (critérios) |
|---|---|
Gate: o do `sdd-projeto.md` (Comandos → Gate de cobertura). Massa de teste funcional: a convenção do `sdd-projeto.md`
(a partir do CT), se houver.

## Riscos e dependências
<concorrência, volume, DDL pendente, integração.>
~~~

## Passo 4 — tasks.md (formato do Kiro)

~~~markdown
# Plano de implementação — IB <id>

- [ ] 1. <Criar modelo/contrato de …>
  - `<caminho>` (skill <skill de código do projeto, se houver>)
  - _Requisitos: 1.1, 1.2_
- [ ] 2. <Implementar …>
  - [ ] 2.1 <…>
  - [ ] 2.2 <…> com teste
  - _Requisitos: 1.1–1.3_
- [ ] 3. <Integrar / registrar / expor …>
- [ ] 4. Massa de teste funcional a partir do CT (se o `sdd-projeto.md` define a convenção)
- [ ] 5. Testes e gate de cobertura
- [ ] 6. Validar com o comando de testes do `sdd-projeto.md` e revisar (sdd-revisar)
~~~

- DDL (ET "Alterações de Banco") **não vira item**: é tratada fora do fluxo. Implemente normalmente (modelos já
  com as colunas novas, testes no banco de teste do projeto), cite a DDL no `design.md` ("Riscos e dependências") e
  confira se o `status.md` tem `Banco (DDL): pendente`.
- Ordem de baixo para cima (o que é referenciado vem antes); cada item cita a skill de código (do `sdd-projeto.md`,
  "Skills por agente") ou o executor (tabela **Executores**) que o executa e os critérios (`_Requisitos: N.M_`).
- Itens pequenos o bastante para um "Start task" do Kiro (≈ 1 componente coeso cada).
- Corretiva: 1) teste que reproduz o defeito (falha), 2) correção, 3) regressão + cobertura, 4) correção dos dados
  já afetados, se a ET pedir.

## Passo 4.5 — Análise independente (antes de codificar)

No lote, quem dispara a análise é o orquestrador (`sdd-lote`); aqui, sem lote:
peça ao agente **`sdd-revisor`** a análise da spec pela rubrica S1–S6 de
[references/analise-spec.md](references/analise-spec.md) (sem agente disponível, aplique a rubrica você mesmo, sem
usar o seu raciocínio de escrita como evidência). Grave o relatório devolvido em `analise-spec-<N>.md` e registre
o resultado no Histórico do `status.md`.

- `ANALISE: OK` → Passo 5.
- `AJUSTAR` com falta **da spec** → corrija `requirements.md`/`design.md`/`tasks.md` e peça nova análise — no
  máximo 2 rodadas; persistindo, apresente os achados à pessoa responsável, que decide (corrigir com orientação ou
  aceitar explicitamente, registrado no `analise-spec-<N>.md`).
- Falta **da documentação** (ex.: cenário sem CT, regra contraditória) → Passo 1.5 (devolução pela `sdd-retrabalho`).

## Passo 5 — Fechar o planejamento

- Modo manual: apresente um resumo (`<N> requisitos · <N> itens no tasks.md · análogo · reaproveitamentos ·
  decisões técnicas · análise: OK na rodada <N>`) e peça "ok" para começar a implementação (não é gate: é o plano
  do próprio codificador, já analisado).
- `status.md`: Spec SDD `rascunho → aprovado` (pelo codificador), `fase: implementando`, linha no Histórico.
- Siga para **`sdd-implementar-spec`**. No lote (`ORCHESTRATED=true`), sem perguntas: siga direto.

## Modo devolução

- **Spec errada por falha do próprio codificador** (`FALHA_SPEC`: estava na documentação e não foi para a spec)
  → ajuste `requirements.md`/`design.md` e acrescente itens `- [ ] N. [R-<nnn>] <o que mudar>` ao `tasks.md`.
- **Documentação alterada pelo especificador** (devolução atendida, novo GATE 1) → `sdd-retrabalho` em modo
  recebimento (entrada **induzida**), atualize a spec ao que mudou e acrescente os itens `[R-<nnn>]`.
- Nunca desmarque itens prontos do `tasks.md`; o judge reavalia o IB inteiro.
- Spec alterada por devolução passa de novo pela análise (Passo 4.5), só do que mudou.
