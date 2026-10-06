---
name: "sdd-testar"
description: "Papel testador do fluxo SDD (pessoa ou agente) — testa a funcionalidade do PR aberto pelo codificador (GATE 2) no ambiente de testes do sdd-projeto.md: confere a DDL em dev, prepara a massa com os scripts declarados, executa a funcionalidade, verifica o resultado (consulta somente leitura, resposta, logs) e registra as evidências em testes.md. Decide o PR (GATE 3): todos os CTs aprovados → PR aprovado, merge por uma pessoa, IB concluído e Tasks fechadas (se houver ALM); algum reprovado → devolução com retrabalho pela sdd-retrabalho. Use em \"testa o IB\", \"executa os CTs\", \"testa o PR\", \"PR aprovado\", ou ao pegar a Task do testador pela sdd-tarefa."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "testar, teste funcional, executar ct, casos de teste, qa, validar, homologar, evidencias, task qa, testador, reteste"
---

# sdd-testar — Testes do PR e decisão do GATE 3 (papel testador)

Entrada: o PR aberto (branch do IB) e a pasta `.kiro/specs/ib-<id>-<slug>/` (via `sdd-tarefa` com a Task do
testador). O teste **é** a decisão sobre o PR: a especificação é formal e os CTs cobrem as regras.
Fontes: `CT.csv` (casos), `HF.md`/`REG-*.md` (comportamento esperado), `ET.md` (queries de verificação,
interfaces) e a seção **Testes funcionais** do `.kiro/steering/sdd-projeto.md` (ambiente, massa, execução,
verificação, logs).

## Passo 0 — Pré-condições

- Pasta do IB fora da branch atual (chamada direta, sem `sdd-tarefa`) → localize-a por
  [localizar-ib.md](../sdd-tarefa/references/localizar-ib.md) e pergunte se troca para a branch do PR; não ache
  nada → peça a Task/IB e pare.
- `fase` = `em-teste` (GATE 2: PR aberto); antes disso → pare.
- **Banco (DDL)** no `status.md` = `não se aplica` ou `aplicada em dev`. `pendente` → **pare**: "Testes bloqueados:
  DDL ainda não aplicada em dev". Confira no dicionário do banco (MCP de consulta) antes de atualizar o campo para
  `aplicada em dev`.
- `git pull --ff-only` na branch; `git status` limpo.
- Reteste depois de uma devolução → acione **`sdd-retrabalho`** em modo recebimento (entrada **induzida**: a
  reexecução dos CTs é custo da falha).
- Build/empacotamento do que vai ser testado: comando "Empacotar para teste funcional" do `sdd-projeto.md`.
- Massa de teste (se o `sdd-projeto.md` define a convenção) existe? Não → é falha do codificador (a massa faz parte
  do `tasks.md`): devolva pelo Passo 4 em vez de gerá-la você.
- Papel Testador `em andamento` no `status.md` (a fase continua `em-teste`).

## Passo 1 — Plano

```
🧪 Testes — IB <id> · Task <id> · rodada <N>
| CT | Nome | Massa | Execução | Verificação |
| CT001 | … | <script de massa> | <comando / chamada / ação> | <consulta / resposta / log> |
Ambiente: <do sdd-projeto.md> — a massa e a execução ESCREVEM nesse ambiente.
Ok para executar?
```

## Passo 2 — Executar cada CT (na ordem do CSV)

1. **Massa:** execute o script de massa declarado no `sdd-projeto.md` (pelo terminal ou pelo MCP do banco).
   Escrita no banco só por esses scripts — nunca DML digitada. Confirme com uma pessoa antes da primeira massa.
2. **Antes:** a verificação "antes" (script ou query da ET) — guarde o resultado.
3. **Execução:** dispare a funcionalidade como o `sdd-projeto.md` indica — guarde o código de saída/resposta e o
   trecho relevante do log (início, contagens, erros).
4. **Depois:** a verificação "depois" — compare com o **RESULTADO ESPERADO** do CT.
5. **Repetição** (CTs de reexecução): execute de novo e confirme que nada duplicou.
6. **Limpeza:** o script de limpeza ao fim (ou entre CTs, se a massa conflitar).

Nunca altere dados à mão para "fazer passar"; nunca edite código, spec nem CT — o testador só observa e registra.

## Passo 3 — Registrar em `testes.md`

```markdown
# Testes — IB <id> · rodada <N> · <AAAA-MM-DD> · <login | agente:<nome>>

| CT | Resultado | Evidência |
|---|---|---|
| CT001 | ✅ passou | depois: 3 linhas com SITUACAO=2 (esperado 3) · exit 0 · lidos 3 / gravados 3 |
| CT004 | ❌ falhou | esperado: registro ignorado · obtido: SITUACAO alterada para 2 (id 123…) |

## Ambiente
Branch <branch> @ <commit curto> · <ambiente> · massa <caminho>
```

Uma seção por rodada (reteste = rodada nova, com **todos** os CTs; não apague as anteriores).

## Passo 4 — Resultado (GATE 3)

**Todos passaram** → o PR está apto. Numa só confirmação:
```
✅ Testes aprovados — IB <id> (rodada <N>, <N> CTs) · PR <link>
  1. commit + push  "Task <id> - Validar <funcionalidade>"   (testes.md + status.md)
  2. PR             recomendação de aprovação, com o resumo do testes.md
GATE 3: uma pessoa aprova o PR e faz o merge.
```
Quando a pessoa informar o merge:
- `status.md`: `fase: concluido`, papel Testador `entregue <data>`, devoluções `resolvida`, link do merge no
  Histórico. Se `Banco (DDL)` não estiver `aplicada em prod` → registre "implantação bloqueada até a DDL em produção".
- Com power ALM: Tasks do testador e do codificador → Concluir e comentário no IB (`IB concluído — PR <link>`).
  Registre o resultado dos CTs no ALM QM manualmente (o QM do power `alm` é só leitura) e informe isso.

**Algum falhou** → acione **`sdd-retrabalho`** em modo devolução com gatilho "testes reprovados", um item por CT
reprovado (esperado × obtido + evidência), e comente no PR que ele está reprovado. Ela classifica a causa (código →
codificador; CT, HF ou REG errados → especificador), registra a causa raiz e devolve. Você reexecuta todos os CTs
quando o IB voltar a `em-teste`.

**PR rejeitado na revisão humana** (mesmo com os testes aprovados) → a pessoa informa o motivo de cada apontamento e
a **`sdd-retrabalho`** trata como devolução, com gatilho "PR rejeitado".

## Regras

- Escrita no ambiente só pelos scripts de massa/limpeza declarados, com confirmação; consultas só `SELECT`/`WITH`.
- Pode ser executada por uma pessoa ou por um agente.
- Evidência objetiva em todo CT (valor consultado, contagem, código de saída, resposta) — "funcionou" não é evidência.
- Nunca editar código, spec ou CT; nunca abrir PR. O merge é sempre de uma pessoa (GATE 3).
