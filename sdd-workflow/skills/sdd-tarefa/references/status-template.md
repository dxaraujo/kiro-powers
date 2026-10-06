# IB <id> — <título>

| Campo | Valor |
|---|---|
| IB | [<id>](<url>) |
| Planejamento | <IB-XX · Sprint N \| —> |
| Classe | <NOVA-FUNCIONALIDADE \| ALTERACAO \| CORRETIVA \| MANUTENCAO> |
| Fast-track | <sim \| não> |
| Branch | `<branch>` |
| Fase | documentando |
| Retries do judge | 0 |
| PR | — |
| ALM | <com power \| pendente — publicar com o power alm \| publicado \| sem power — não publicado> |
| Banco (DDL) | <não se aplica \| pendente \| aplicada em dev \| aplicada em prod> |

<!-- Fases: documentando → validando → aguardando-aprovacao → especificado → planejando → implementando → em-revisao
     → em-teste → concluido · Desvios: bloqueado · devolução (volta a documentando/implementando)
     Banco (DDL): tratado fora do fluxo, com quem administra o banco; bloqueia testes até "aplicada em dev" e implantação até "aplicada em prod". -->

## Papéis

| Papel | Task | Responsável | Situação |
|---|---|---|---|
| Especificador | [ESPEC] <id> | <login> | em andamento |
| Codificador | [BE] <id> | <login \| —> | aguardando GATE 1 |
| Testador | [QA] <id> | <login \| —> | aguardando GATE 2 |

<!-- Responsável: login da pessoa ou agente:<nome> (ex.: agente:sdd-especificador).
     Situação: aguardando GATE N · em andamento · entregue <data> · devolvido <data> -->

## Artefatos

| Artefato | Arquivo | Status | ID ALM |
|---|---|---|---|
| Decisões | decisoes.md | — | n/a |
| HF | HF.md | — | — |
| REG | REG-01-<slug>.md | — | — |
| ET | ET.md | — | — |
| CT | CT.csv | — | — |
| Spec SDD | requirements.md · design.md · tasks.md | — | n/a |

<!-- Status: — (não gerado) · rascunho · aprovado · publicado · implementado
     Remova as linhas que a classe não exige. Uma linha por REG. -->

## Validação dos requisitos

<!-- Antes do GATE 1: preenchida pela sdd-validar-requisitos (rubrica V1–V10); a sdd-especificar marca como resolvido.
     Relatório completo em validacao-<N>.md. -->

| Rodada | Verificação | Achado | Situação |
|---|---|---|---|

## Devoluções

<!-- Depois de um gate: preenchida pela sdd-retrabalho (testes reprovados, PR rejeitado, falha na spec, correção pedida).
     R-<nnn> = entrada causa raiz em .kiro/aprendizado/retrabalho.md. -->

| R | Gatilho | Problema (esperado × obtido / motivo) | Causa | Volta para | Refeito por | Situação |
|---|---|---|---|---|---|---|

## Histórico

- <AAAA-MM-DD HH:MM> — pasta criada (sdd-tarefa, Task <id>)
