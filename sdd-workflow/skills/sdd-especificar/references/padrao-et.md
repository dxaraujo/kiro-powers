# Padrão — Especificação Técnica (ET)

A ET detalha **dados e interfaces**: bancos e tabelas, queries, operações de escrita, contratos (telas, APIs,
arquivos, mensagens) e integrações. É a ponte entre a HF/REG e o `design.md` da spec SDD. Tudo que aparece aqui foi
**confirmado no banco (MCP de consulta, somente leitura) ou no código**. A ET diz **o que** os dados e as
interfaces são — não que classe ou componente implementa (isso é do codificador).

## Estrutura

~~~markdown
# ET - <Nome da funcionalidade>

**Task:** <id> · **HF:** HF · **REGs:** REG-01, REG-02 · **Funcionalidade:** `<nome>` (nova | alterada)

## Visão Geral

**Módulo / área:** <conforme o steering de estrutura>
**Dados:** <banco/schema> (leitura) → <…> (escrita)
**Tipo:** <tela | API | processamento | integração | manutenção de dados>
**Disparo:** <ação do usuário | requisição | agendamento | evento> · **Entradas:** <…>

## Interfaces

<Contrato de cada ponto de entrada/saída — omita o que não se aplica.>

| Interface | Tipo | Entrada | Saída | Erros |
|---|---|---|---|---|
| `<POST /recurso>` \| `<tela X>` \| `<arquivo Y>` | API \| tela \| arquivo \| mensagem | <campos> | <campos / status> | <códigos e mensagens> |

## Modelo de Dados

| Banco.Tabela | Operação | Campos usados | Observação |
|---|---|---|---|
| <SCHEMA>.<TABELA> | SELECT / INSERT / UPDATE / DELETE | <CAMPOS> | <índice usado, volume> |

## Queries

### Q01 - <Nome descritivo>

**Objetivo:** <…> · **Usada em:** <passo da HF> · **Parâmetros:** <…> · **Banco:** <…>

```sql
SELECT ...
```

## Operações de Escrita

### W01 - <UPDATE/INSERT ...>

**Tabela:** <…> · **Chave:** <…> · **Conforme:** REG-01

| Campo | Valor | Origem |
|---|---|---|
| <CAMPO> | <valor/expressão> | <regra/entrada> |

## Reexecução, Transação e Concorrência

- **Idempotência:** <o que impede duplicar na repetição/reexecução>
- **Transação:** <o que é atômico; o que acontece com o lote/requisição em caso de erro>
- **Concorrência:** <outras funcionalidades que tocam os mesmos dados; bloqueios>

## Integrações

<Sistema, protocolo (REST/arquivo/fila/tabela), contrato, tratamento de falha — ou "nenhuma".>

## Alterações de Banco

<"Nenhuma" — ou DDL proposta no padrão do projeto (steering de tecnologia), com rollback. Havendo DDL, ela é
tratada fora do fluxo com quem administra o banco (`Banco (DDL): pendente` no `status.md`): não bloqueia a
codificação, só os testes (até ser aplicada em dev) e a implantação (até ser aplicada em produção).>

## Correção (só CORRETIVA)

**Causa raiz:** <arquivo:linha + explicação> · **Correção:** <o que muda> ·
**Validação:** <consulta/chamada que comprova antes/depois> · **Dados já afetados:** <precisa de manutenção?>

---
Versão: 1.0 | Data/Hora: <DD/MM/AAAA HH:MM> | Status: <rascunho | aprovado | publicado>
Artefato produzido com uso de IA generativa — Fluxo SDD

| Data/Hora | Alteração |
|---|---|
| <DD/MM/AAAA HH:MM> | Versão inicial |
~~~

## Regras

- Omita seções vazias, exceto "Reexecução, Transação e Concorrência" (obrigatória) e "Alterações de Banco".
- Respeite as regras críticas de dados do `sdd-projeto.md`/steering de tecnologia (ex.: query que não cruza bancos).
- SQL com bind variables nomeadas (`:id`), nunca valores literais de produção.
- Nomes de tabela e coluna como estão no banco; não "corrija" nomes legados.
