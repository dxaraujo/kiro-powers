---
name: "sdd-alm-publicar-requisitos"
description: "Publica no ALM a documentação aprovada de um IB do fluxo SDD (papel especificador) — REG, HF e ET no DOORS Next (alm-rm, Markdown direto, ordem de baixo para cima, troca das referências locais pelos IDs do ALM, link \"implementa\" com o IB no EWM), entrega o CT.csv pronto para importação manual e conclui a Task [ESPEC]. Passo opcional depois do GATE 1 — só roda se o power alm estiver instalado; sem ele o fluxo segue normalmente. Atualiza status.md com IDs e URLs. Use depois do GATE 1 (requisitos aprovados) ou quando pedirem \"publica no ALM\", \"sobe a documentação\", \"atualiza a HF no ALM\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "publicar, alm, doors, rm, subir documentacao, publicar hf, publicar reg, publicar et, atualizar alm, att_alm, pub_alm"
---

# sdd-alm-publicar-requisitos — Requisitos aprovados → ALM (opcional)

Requer o MCP `alm` (power ALM) e as skills **`alm-rm`** e **`alm-gc`**. IDs de pasta e tipo: `.kiro/config/alm-power/pa_*.json`.
**Sem o MCP `alm` nesta sessão, esta skill não publica:** registre o campo `ALM` pela regra do steering
(projeto com ALM → `pendente — publicar com o power alm` + `ALM pendente: publicar HF/REG/ET e concluir [ESPEC]` no
Histórico; projeto sem ALM → `sem power — não publicado`) e pare — o IB já está `especificado` e a codificação pode
começar. Rodada depois, com o power, ela publica as pendências e acrescenta `ALM feito: …` no Histórico.

## Passo 1 — Pré-condições

- `status.md` do IB: GATE 1 aprovado (`fase: especificado` ou adiante) e artefatos **`aprovado`**. Sem isso, não
  publica: volte à `sdd-validar-requisitos`.
- **Republicação** (devolução): artefato que já tem ID ALM e foi reaprovado → atualização do mesmo ID (Passo 4),
  sem perguntar; só os alterados.
- Conexão: `whoami()`. 401 → peça para corrigir as credenciais do mcp-alm (nunca leia o arquivo de senha).

## Passo 2 — Ordem e mapeamento

Publique **de baixo para cima**, para que cada artefato já nasça com os IDs dos que ele referencia:

| Ordem | Artefato | Tipo RM (`rm.requirements-types`) | Pasta (`rm.folders`) | Título no ALM |
|---|---|---|---|---|
| 1 | `REG-*.md` | Regra | pasta de regras | `REG - <nome>` |
| 2 | `HF.md` | História de Usuário (funcional) | pasta de histórias | `HF - <nome>` |
| 3 | `ET.md` | Especificação Técnica | pasta de especificações técnicas | `ET - <nome>` |

Tipo e pasta vêm do `.kiro/config/alm-power/pa_*.json` (`rm.requirements-types`, `rm.folders`) pelo nome mais próximo. Não achou um
correspondente único → mostre as opções do arquivo e pergunte uma vez; a escolha vale para o IB inteiro.

Antes de publicar cada arquivo, substitua no texto as referências locais (`REG-01`, `HF`) por
`<ID>: REG - <nome>` usando os IDs já publicados (ficam no `status.md`). Atualize o rodapé
(`Data/Hora` = agora, `Status: publicado`) **no arquivo local** — ele continua sendo a fonte.

## Passo 3 — Duplicata

`rm_search_requirements` por título na pasta/tipo. Se existir:
`(a) atualizar o existente · (b) criar outro · (c) pular` — aguarde a escolha. Artefato já com ID no
`status.md` → é **atualização** direto (sem perguntar), via `rm_update_requirement`.

## Passo 4 — Publicar

O MCP `alm` aceita o **Markdown direto** em `text` (converte para o primaryText do DOORS) — envie o conteúdo do
arquivo como está, sem converter.

- **Novo:** `rm_create_requirement(requirement_type, folder, title, text=<markdown do arquivo>)`.
- **Atualização:** `rm_update_requirement(requirement_id, text=<markdown>)` — substitui o texto inteiro.

Registre no `status.md`: `ID ALM` = `[<id>](<url>)`, status `publicado`, linha no Histórico.

## Passo 5 — Rastreabilidade

Para cada artefato publicado: `link_workitem_and_requirement(<url do IB>, <url do requisito>, "implements")`
(skill `alm-gc`). Links só acrescentam — não duplique se já existir (`list_linked_requirements(<url do IB>)`).

## Passo 6 — CT

O QM do power é somente leitura. Confirme que `CT.csv` está em UTF-8 com BOM e LF e informe:
`Importe <pasta>/CT.csv no ALM QM (Importar → CSV).` Pergunte o ID do plano/caso após a importação e,
se informado, registre-o no `status.md`.

## Passo 7 — Concluir a etapa no EWM

Todos os artefatos exigidos publicados → `ALM: publicado` no `status.md`. Numa só confirmação:

```
✅ Publicado — IB <id>
REG-01 → <id> · HF → <id> · ET → <id>   (links "implementa" com o IB: ok)
CT.csv → importar manualmente no QM
  1. commit + push   "Task <id [ESPEC]> - Publicar especificação no ALM"  (status.md com os IDs)
  2. EWM             Task [ESPEC] <id> → ação de conclusão (estado final da PA)
  3. EWM (opcional)  comentário na Task [BE] <id>: branch, pasta e IDs do ALM
(sim / escolha os itens)
```

- Comentário (`add_comment_to_workitem`) na `[BE]`: `Especificação aprovada. Branch: <branch> ·
  Pasta: .kiro/specs/ib-<id>-<slug>/ · REG-01 <id>, HF <id>, ET <id> · Comece com: "vamos trabalhar na task
  <id [BE]>".` É só um aviso: o codificador começa pela `fase: especificado` do `status.md`, com ou sem comentário.
- Estado da `[ESPEC]` pela ação de `ccm_list_workitem_states` (a ação que leva ao estado de conclusão da PA).
- Push recusado (branch protegida, sem permissão, divergência) → informe e pare; nunca `--force`.

**Republicação** (devolução atendida): só os artefatos alterados (atualização dos IDs existentes), commit
`Task <id [ESPEC]> - Ajustar especificação (R-<nnn>)`, `[ESPEC]` → concluída de novo e comentário opcional na `[BE]`
`Devolução R-<nnn> atendida: <artefatos alterados>`.

A etapa do especificador termina aqui.

## Regras

- Nunca publica sem aprovação; nunca sobrescreve no ALM sem confirmação (exceto artefato já registrado como deste IB).
- Falha de publicação: o Markdown local fica intacto; informe código HTTP e mensagem; os já publicados permanecem.
- Mostre à pessoa nomes de tipo e pasta, nunca URIs `FR_`/`OT_`.
