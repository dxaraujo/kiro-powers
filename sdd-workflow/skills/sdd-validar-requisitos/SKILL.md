---
name: "sdd-validar-requisitos"
description: "Validação formal da documentação de um IB antes da entrega ao codificador (papel especificador) — verifica HF, REGs, ET e CT contra a rubrica V1–V10 (completude, rastreabilidade, testabilidade, não ambiguidade, consistência, dados confirmados no banco, exceções e reexecução, escopo, dúvidas, padrão), devolve achados à sdd-especificar (até 2 rodadas) e conduz o GATE 1 — aprovação dos requisitos por uma pessoa, que libera o IB para a codificação (fase especificado) e, havendo power ALM, a publicação. Use após sdd-especificar, ou quando pedirem \"valida os requisitos\", \"a documentação está pronta?\", \"GATE 1\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "validar, validacao, requisitos, documentacao pronta, especificacao formal, revisar documentacao, gate 1, aprovar documentacao, checklist de requisitos"
---

# sdd-validar-requisitos — Requisitos prontos para o codificador

Objetivo: o codificador recebe uma documentação que ele **não precisa devolver**. Tudo o que é de negócio
(regra, dado, exceção, escopo) tem de estar decidido aqui; o que é técnico (como implementar, que serviço
reaproveitar) fica para o codificador, na `sdd-criar-spec`.

Pode ser executada pelo próprio especificador ou, para um olhar independente, pelo agente **`sdd-revisor`**
(só leitura — ele devolve o relatório e quem chamou grava os arquivos). Insumos: `status.md`, `decisoes.md`, HF, REGs, ET, CT da pasta do IB; a Task/IB no ALM; código da funcionalidade afetada;
banco pelo MCP de consulta do `sdd-projeto.md` (somente leitura).

## Passo 0 — Checklist pré-voo

Se existir `.kiro/aprendizado/checklists/sdd-validar-requisitos.md`, verifique também esses itens (são falhas que
já passaram por esta validação e voltaram do codificador).

## Passo 1 — Rubrica

`fase: validando` no `status.md`.

| # | Verificação | Como verificar | Severidade |
|---|---|---|---|
| V1 | **Completude** — existem todos os artefatos exigidos pela classe (`status.md`) | listar a pasta | BLOQUEANTE |
| V2 | **Rastreabilidade** — todo cenário da HF com regra cita a REG (`Conforme`); toda REG aparece em ≥ 1 cenário; toda decisão `decidida` de `decisoes.md` aparece em alguma REG/HF; a ET traz os dados de todas as REGs; o CT cobre todos os cenários e fluxos da HF | cruzar referências | BLOQUEANTE |
| V3 | **Testabilidade** — todo "Então" e todo resultado de CT é verificável por consulta (valor, situação, contagem); nada de "corretamente", "adequado", "etc." | ler cenários e CTs | BLOQUEANTE |
| V4 | **Não ambiguidade** — valores de domínio com código **e** significado confirmados; datas de corte, limites e parâmetros explícitos | REG × código/banco | BLOQUEANTE |
| V5 | **Consistência** — HF, REG, ET e CT não se contradizem (filtros, quantidades, nomes de tabela/coluna iguais) | cruzar artefatos | BLOQUEANTE |
| V6 | **Dados confirmados** — tabelas/colunas da ET existem no banco (MCP de consulta, `SELECT` no dicionário; sem MCP, no código — modelos e migrações) ou estão em "Alterações de Banco" com DDL | banco / código | BLOQUEANTE |
| V7 | **Exceções e reexecução** — há fluxo de exceção para erro em um registro (pula, registra log, aborta) e cenário de reexecução (não duplica) | HF + ET | BLOQUEANTE |
| V8 | **Escopo** — funcionalidade nova × alterada explícita; o que fica fora explícito; impacto em outras funcionalidades/tabelas citado na ET | HF + ET | AJUSTE |
| V9 | **Dúvidas e decisões** — `decisoes.md` existe; nenhuma decisão `em aberto` nem dúvida de negócio na HF sem aceite explícito para o GATE 1 | `decisoes.md` + HF | BLOQUEANTE |
| V10 | **Padrão** — estrutura dos `references/padrao-*.md` da `sdd-especificar` (seções, numeração, rodapé, CSV UTF-8 com BOM e LF) | comparar | AJUSTE |

Cada achado tem **evidência** (`arquivo:linha`, consulta ou referência ausente) e a correção esperada.

## Passo 2 — Resultado e ciclo com a `sdd-especificar`

```markdown
## Validação — IB <id> · rodada <N>
| # | Resultado | Achado | Evidência | Correção |
|---|---|---|---|---|
| V1 | ✅ | | | |
| V4 | ❌ BLOQUEANTE | situação "4" sem significado | REG-02:18 | confirmar no domínio da coluna SITUACAO |
…
RESULTADO: PRONTO | AJUSTAR
```

- Grave em `.kiro/specs/ib-<id>-<slug>/validacao-<N>.md` e registre na seção **Validação dos requisitos** do
  `status.md` (`# | verificação | achado | situação`).
- Qualquer BLOQUEANTE → `AJUSTAR`: acione **`sdd-especificar`** em modo ajuste com os achados e, quando ela devolver,
  valide de novo (rodada nova). Achados só de AJUSTE não impedem o `PRONTO`.
- **No máximo 2 rodadas** automáticas. Persistindo, siga ao GATE 1 com os achados abertos — quem decide é a pessoa.
- Achado que depende de decisão de negócio sem fonte → pergunta direta à pessoa (no lote: "Dúvidas pendentes"
  da HF e achado aberto).
- Aprendizado: cada achado BLOQUEANTE incrementa `.kiro/aprendizado/checklists/sdd-especificar.md` (origem
  `sdd-validar-requisitos`) — antes do GATE 1 não é retrabalho.

## Passo 3 — GATE 1 (aprovação da documentação)

`fase: aguardando-aprovacao` e uma só tabela:

```
📋 GATE 1 — IB <id> · <título>
| Artefato | Resumo |
|---|---|
| Decisões | <N> decididas · <N> em aberto (aceitas: <lista>) |
| REG-01..N | <N regras> |
| HF | <N cenários> · fluxos alternativos/exceção: <N> |
| ET | <N interfaces> · <N queries> · <N escritas> · DDL: <sim/não> |
| CT | <N casos> |
| Validação | rodada <N>: PRONTO | achados abertos: <lista> |
Aprova os requisitos? ("ok" · ou diga o que ajustar)
```

- Achado BLOQUEANTE aberto impede o "ok" automático: a pessoa aceita explicitamente ("ok, aceito V8") ou ajusta.
- "ok" → artefatos `aprovado`, `fase: especificado`, papel Especificador `entregue <data>` e, se houver DDL na ET,
  `Banco (DDL): pendente` no `status.md`. Numa só confirmação: commit
  no padrão do `sdd-projeto.md` (ex.: `Task <id [ESPEC]> - Especificar <funcionalidade>`; só a pasta do IB) e push da branch — é o sinal assíncrono
  para o codificador.
- Com power ALM → siga para **`sdd-alm-publicar-requisitos`** (publica, rastreia e conclui a `[ESPEC]`). Sem ALM →
  registre `ALM: sem power — não publicado` no `status.md`; a etapa do especificador termina aqui.
- Ajuste pedido → `sdd-especificar` e nova rodada de validação (só do que mudou).
- Devolução (depois do GATE 1) → mesma validação, só dos artefatos alterados, antes do novo GATE 1; o commit passa
  a ser `Task <id [ESPEC]> - Ajustar especificação (R-<nnn>)`.
- No lote (`ORCHESTRATED=true`) não apresente o gate: devolva o resultado ao orquestrador, que agrupa os gates.

## Regras

- Nada de técnica aqui: classe, componente, padrão de código são do codificador. Validar é garantir que o
  **negócio** está completo, verificável e sem contradição.
- Não altera a documentação — quem altera é a `sdd-especificar`.
