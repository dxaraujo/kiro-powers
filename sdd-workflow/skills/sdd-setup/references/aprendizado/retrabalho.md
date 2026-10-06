# Retrabalho

> Registro **somente de acréscimo** (nunca editar nem remover entradas). Mantido pela skill `sdd-retrabalho`.
> Cada entrada é trabalho refeito **depois de um gate**: a **causa raiz** (papel onde estava o erro) e as
> **induzidas** (papéis que refizeram por consequência). `MUDANCA_ESCOPO` não é registrado.

## Formato

```markdown
### R-<nnn> · <AAAA-MM-DD> · IB <id> · Task <id> · <papel: especificador|codificador|testador>

Origem: <causa raiz | induzido por R-<nnn>>
Gatilho: <testes reprovados | PR rejeitado | falha na spec na codificação | correção pedida>
Artefato: <HF|REG|ET|CT|spec|código|testes>
Pedido / o que foi refeito: "<resumo>"
Classificação: <categoria — só na causa raiz>
Evidência: <arquivo:linha | "ausente em todos os artefatos consultados">
Rubrica relacionada: <A–N | N/A>
Responsável: <login | agente:<nome>>
```

## Categorias (só causa raiz)

| Categoria | Onde estava a informação | Volta para | Checklist |
|---|---|---|---|
| `FALHA_IMPLEMENTADOR` | na spec (requirements/design/tasks) e não foi implementado | codificador | `sdd-implementar-spec` |
| `FALHA_JUDGE_SEVERIDADE` | na spec, implementado errado, e o judge deixou passar | codificador | `sdd-revisar` / rubrica |
| `FALHA_STEERING` | convenção documentada no steering e violada no código | codificador | `sdd-implementar-spec` |
| `FALHA_SPEC` | na HF/REG/ET, mas o codificador não a levou para requirements/design/tasks | codificador | `sdd-criar-spec` |
| `FALHA_DOC` | no ALM, no código ou no banco, mas não entrou (ou entrou errado) na HF/REG/ET/CT | especificador | `sdd-especificar` + `sdd-validar-requisitos` |
| `PREFERENCIA_NAO_DOCUMENTADA` | em lugar nenhum, mas é recorrente no time | papel onde deveria estar | candidato a steering |

## Registros

<!-- Novas entradas abaixo desta linha, sempre ao final. Numeração R-001, R-002, … contínua. -->
