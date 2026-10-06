---
name: "sdd-especificar"
description: "Papel especificador do fluxo SDD — entrevista a pessoa sobre as decisões de negócio em aberto (uma pergunta por vez, registradas em decisoes.md) e gera a documentação funcional e técnica do IB na pasta .kiro/specs/ib-<id>-<slug>/: HF (história funcional com cenários Gherkin), REG (regras de negócio), ET (especificação técnica com dados e interfaces confirmados no código e no banco) e CT (casos de teste em CSV, importáveis no ALM). Também corrige os achados da validação (sdd-validar-requisitos) e a documentação devolvida pelo codificador (sdd-retrabalho). Use após sdd-tarefa, ou quando pedirem \"gera a HF\", \"documenta a regra\", \"faz a ET\", \"gera os CTs\", \"documentar a task\". Não valida (sdd-validar-requisitos), não publica no ALM (sdd-alm-publicar-requisitos) e não gera requirements/design/tasks (isso é do codificador, sdd-criar-spec)."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "entrevista, decisoes, hf, reg, et, ct, historia funcional, regra de negocio, especificacao tecnica, caso de teste, documentar, documentacao, gerar hf, gerar et, gerar ct, spec funcional"
---

# sdd-especificar — Documentação do IB (papel especificador)

Leia antes: `status.md` da pasta do IB, o steering do power `sdd-workflow` e `.kiro/steering/sdd-projeto.md`.
Contexto de domínio: o steering de **produto** do projeto (módulos, fluxos, regras, glossário) e os steering extras
listados no `sdd-projeto.md`.

## Passo 0 — Checklist pré-voo

Se existir `.kiro/aprendizado/checklists/sdd-especificar.md`, leia os itens e considere-os ao gerar (são falhas
recorrentes de documentação ainda não promovidas a regra). Sem arquivo → siga sem comentar.

## Passo 1 — Insumos

1. Dados da Task (vindos da `sdd-tarefa`, ou relidos via `alm-ccm` se a skill foi chamada direto e houver ALM).
2. **Código existente:** em `ALTERACAO`/`CORRETIVA`/`MANUTENCAO`, leia a funcionalidade afetada (pontos de
   entrada, regras, acesso a dados — a estrutura está no steering de estrutura). A documentação descreve o
   comportamento **depois** da mudança; o código atual é a fonte da verdade do "antes".
3. **Banco (somente leitura, MCP do `sdd-projeto.md`):** estrutura das tabelas citadas e, se útil, volumetria
   (`COUNT`). Nunca DML/DDL. Sem MCP de banco → confirme pelo código (modelos, migrações) e marque o que não deu
   para confirmar.
4. Pergunte **uma vez** só por insumos que não estão no ALM/Task (planilha, e-mail, ata, demanda). As dúvidas de
   negócio vão para a entrevista (Passo 1.5).

## Passo 1.5 — Entrevista (decisões de negócio)

Antes de escrever, feche o que as fontes não respondem — o agente não preenche lacunas com suposições plausíveis.

1. Liste as **decisões de negócio em aberto**: o que a HF/REG vai precisar e nem a Task, nem o código, nem o banco
   respondem (filtro, valor de domínio, data de corte, comportamento em exceção, reexecução, permissão, escopo).
2. Pergunte **uma por vez**, na ordem em que uma resposta pode mudar as seguintes:
   ```
   Decisão D-03 · <tema>
   Contexto: <o que se sabe e de onde veio>
   Opções: (a) <…> (recomendada — <motivo>) · (b) <…> · (c) outra
   ```
3. Registre cada resposta em `decisoes.md` na pasta do IB (cria na primeira):
   ```markdown
   | D | Pergunta | Decisão | Quem decidiu | Data | Situação |
   |---|---|---|---|---|---|
   | D-01 | <…> | <…> | <login> | <AAAA-MM-DD> | decidida |
   ```
   Uma resposta pode abrir novas perguntas — acrescente-as à lista.
4. Termina quando não resta decisão em aberto, ou quando a pessoa diz que o restante fica pendente: essas entram
   como `em aberto` em `decisoes.md` e em "Dúvidas pendentes" da HF (a validação cobra o aceite no GATE 1).
5. Nada a decidir → registre `decisoes.md` com "Sem decisões em aberto — fontes: <…>" e siga.

Modo orquestrado (`ORCHESTRATED=true`, lote): sem entrevista — liste as perguntas em `decisoes.md` como `em aberto`
e em "Dúvidas pendentes" da HF. Devolução recebida: entreviste só sobre o que a devolução aponta (`D-<nn>` novos).

## Passo 2 — Gerar, na ordem

Gere só os artefatos que o `status.md` lista, nesta ordem (cada um referencia os anteriores):

| # | Artefato | Padrão | Arquivo |
|---|---|---|---|
| 1 | REG (uma por regra) | [references/padrao-reg.md](references/padrao-reg.md) | `REG-<nn>-<slug>.md` |
| 2 | HF | [references/padrao-hf.md](references/padrao-hf.md) | `HF.md` |
| 3 | ET | [references/padrao-et.md](references/padrao-et.md) | `ET.md` |
| 4 | CT | [references/padrao-ct.md](references/padrao-ct.md) | `CT.csv` |

Leia o padrão **antes** de escrever cada artefato — nunca escreva de memória. Regra ou cenário que nasce de uma
decisão da entrevista cita a origem (`Conforme D-03`).
`fast-track: sim` → só ET (seções Causa raiz, Correção, Validação) e CT de regressão.

Referências entre artefatos usam o nome local até a publicação (`REG-01`, `HF`); a `sdd-alm-publicar-requisitos`
troca pelos IDs do ALM. Para o CT, os campos do ALM (Responsável, Criado Por, Planejado para, Atendido por)
vêm do `alm/pa_*.json`/Task; pergunte só o que faltar, com o valor exato do ALM. Sem ALM, preencha só o que souber.

## Passo 3 — Status e próximo passo

- Marque cada artefato como `rascunho` no `status.md` e acrescente uma linha no Histórico.
- Apresente um resumo: nº de regras, cenários Gherkin, interfaces/queries na ET, CTs; dúvidas pendentes listadas na HF.
- Próximo passo: **`sdd-validar-requisitos`** (validação formal e GATE 1). A spec SDD não é do especificador —
  o codificador a gera depois do GATE 1.

## Ajuste por achados da validação (antes do GATE 1)

Quando a `sdd-validar-requisitos` devolve achados (seção **Validação dos requisitos** do `status.md`):

1. Corrija **só** o que está listado, no artefato indicado — releia o padrão do artefato antes de alterar.
2. Busque a informação nas fontes de sempre (Task, código, banco); decisão de negócio sem fonte → pergunte a uma
   pessoa (no lote, "Dúvidas pendentes" da HF) e deixe o achado `aberto`.
3. Artefato em `rascunho` → acrescente a linha no histórico do rodapé (`<data> | Ajuste: V<n> <achado>`), sem
   mudar a versão.
4. Marque cada achado como `resolvido — <o que mudou>` (ou `aberto — <motivo>`) e devolva para a
   **`sdd-validar-requisitos`**.

## Devolução e novas versões (depois do GATE 1)

Alterar artefato `aprovado` ou `publicado` só acontece por uma **devolução** (seção **Devoluções** do `status.md`,
aberta pela `sdd-retrabalho`). Pedido de alteração sem devolução registrada → acione a **`sdd-retrabalho`** primeiro.

1. Modo recebimento da `sdd-retrabalho` (registra a causa raiz ou a induzida).
2. Corrija só o que a devolução aponta; artefato alterado volta a `rascunho`. Incremente a versão no rodapé
   (correção 1.0→1.1, evolução 1.0→2.0) e registre no histórico do artefato com `R-<nnn>`.
3. Siga para a **`sdd-validar-requisitos`** (validação e GATE 1 só do que mudou); depois, se houver power ALM, a
   `sdd-alm-publicar-requisitos` republica os alterados. Nunca apague versões publicadas — o ALM guarda o histórico.
4. Só o CT estava errado e o código está certo → corrija o CT, faça o GATE 1 do CT e devolva direto ao testador
   (`fase: em-teste`; com ALM, comentário na Task do testador).

## Regras

- Escreva no idioma do projeto; nomes de tabela, coluna, classe, endpoint e SQL na forma original.
- Descreva o comportamento pelo ator real (usuário de uma tela, cliente de uma API, operador de um processamento,
  sistema parceiro) — o que o steering de produto disser que o sistema é.
- Nunca invente tabela, coluna, endpoint ou regra: confirme no código ou no banco; decisão de negócio sem fonte
  vai para a entrevista (Passo 1.5) — e, se não for decidida, para "Dúvidas pendentes" da HF.
