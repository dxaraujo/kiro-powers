---
inclusion: always
---

# Configuração do fluxo SDD — <nome do projeto>

> Gerado pela skill `sdd-setup` do power `sdd-workflow`. Rode a `sdd-setup` de novo para alterar
> ("atualizar a configuração do sdd-workflow"). As skills `sdd-*` leem os valores daqui.

## Steering do projeto

| Papel | Arquivo |
|---|---|
| Produto e domínio | `<.kiro/steering/product.md>` |
| Tecnologia (stack, regras de codificação, banco) | `<.kiro/steering/tech.md>` |
| Estrutura (pastas, padrões, componentes) | `<.kiro/steering/structure.md>` |
| Extras (contexto de domínio carregado pelos agentes) | `<lista ou "nenhum">` |

**Regras críticas** (o judge e a análise da spec verificam como BLOQUEANTE; vêm do steering de tecnologia/estrutura):
- <ex.: uma query nunca cruza bancos>
- <ou "nenhuma além do steering">

## Git e PR

| Item | Valor |
|---|---|
| Branch base | `<main>` |
| Prefixo da branch | `<feature/>` |
| Mensagem de commit | `<Task <id> - <verbo no infinitivo> <descrição>>` |
| Abrir PR | `<gh pr create … | glab mr create … | entregar título e descrição para a pessoa abrir>` |

## Comandos

| Ação | Comando |
|---|---|
| Compilar / checar tipos | `<…>` |
| Testes unitários | `<…>` |
| Teste de uma classe/arquivo | `<…>` |
| Cobertura | `<… ou "não há">` |
| Gate de cobertura | `<ex.: linha ≥ 90% / branch ≥ 80% nas classes alteradas | "não há">` |
| Exclusões do gate | `<padrões de arquivo fora do gate | "nenhuma">` |
| Empacotar para teste funcional | `<…>` |

Falha de ambiente (banco, rede, dependência indisponível) → reportar como **AMBIENTE**, não "consertar".

## Banco de dados

| Item | Valor |
|---|---|
| MCP de consulta | `<nome do servidor MCP e da tool, ex.: @meu-db/query | "não há">` |
| Bancos / schemas | `<…>` |
| Uso | **somente leitura** (`SELECT`/`WITH`) — nunca DML/DDL |

## Testes funcionais (testador)

| Item | Valor |
|---|---|
| Ambiente | `<dev — o que os testes escrevem e onde>` |
| Massa de teste (scripts) | `<pasta e convenção, ex.: test/massa/<funcionalidade>/ — seed, verify-before, verify-after, cleanup | "não há">` |
| Executar a funcionalidade | `<comando, chamada HTTP, job, tela…>` |
| Verificar o resultado | `<consulta ao banco, log, resposta da API…>` |
| Logs | `<caminho do log>` |

## Work items

| Item | Valor |
|---|---|
| Prefixo — especificador | `[ESPEC]` |
| Prefixo — codificador | `[BE]` |
| Prefixo — testador | `[QA]` |
| Prefixo — banco (fora do fluxo) | `[BD]` |
| ALM | `<power alm — alm/pa_<nome>.json | sem power>` |

## Executores (codificador)

Quem implementa cada tipo de item do `tasks.md` (a `sdd-implementar-spec` e o `sdd-orquestrador` usam esta tabela;
o que não casar com nenhuma linha fica com o `sdd-codificador`).

| Tipo de item | Executor (agente ou skill) |
|---|---|
| <ex.: novo endpoint REST> | <agente do projeto ou skill> |

## Skills por agente (além das do fluxo)

| Agente | Skills extras | MCP | Subagentes |
|---|---|---|---|
| `sdd-especificador` | <…> | <…> | — |
| `sdd-codificador` | <…> | <…> | <…> |
| `sdd-revisor` | <…> | <…> | — |
| `sdd-orquestrador` | <…> | <…> | `sdd-especificador`, `sdd-codificador`, `sdd-revisor` <+ executores> |

## Regras promovidas

Regras permanentes vindas do aprendizado (`sdd-retrabalho`, promoção após 3 ocorrências). Cada skill `sdd-*` aplica
as do seu nome como se estivessem nela; o judge (`sdd-revisar`) as verifica como parte da rubrica.

| Skill | Regra | Origem |
|---|---|---|
