---
inclusion: always
---

# ALM Power

Este power dá acesso ao **IBM Engineering Lifecycle Management (ELM)** via OSLC, pelo MCP `alm`
(`uvx mcp-alm@latest`). **O MCP fornece as capacidades; as skills fornecem o conhecimento** (quais tools, em que
ordem, de onde vem cada parâmetro).

## O que ele cobre

| Aplicação | O que faz | Skill |
|---|---|---|
| **EWM/RTC (CCM)** | Listar, ler, criar, atualizar, mudar estado, comentar work items (IB, TR, DF, DT, IMP, RSC, REU); itens de sprint, iteração ou plano; **lançar horas trabalhadas (timesheet)** | `alm-ccm` |
| **DOORS Next (RM)** | Buscar, ler, criar e atualizar requisitos (REQ, HU, UC, RN, MSG, ET...), atributos, links entre requisitos e artefatos embutidos | `alm-rm` |
| **Documentação RM** | Baixar os artefatos do DOORS Next para o repositório em OKF (`rm.download.path`) e sincronizar só o que mudou (`sync.md`) | `alm-sync` |
| **ETM/RQM (QM)** | Consultar artefatos de teste (CT, PT, ST, SCT, TER, RT) — só leitura | `alm-qm` |
| **Comum / GC** | Quem sou eu, usuários, project areas, configuração global e rastreabilidade entre work item, requisito e teste | `alm-gc` |
| **Configuração** | Criar/atualizar `.kiro/config/power/alm/pa_<nome>.json`; criar iterações e planos | `alm-setup` |

## Como usar

1. **Carregue a skill da área** antes de chamar as tools.
2. **alm.json primeiro, servidor depois.** `.kiro/config/power/alm/pa_*.json` (gerado pela `alm-setup`) resolve nomes → identifiers
   sem chamadas de descoberta. Com o arquivo, nada muda: use-o.
3. **Sem setup.** Sem o arquivo (ou faltando a seção/nome que o pedido precisa), pergunte **uma vez**: rodar a
   `alm-setup` (grava para as próximas vezes) ou **seguir sem setup**. Seguindo sem setup:
   - pergunte só o que **este** pedido precisa (a lista "Sem setup" de cada skill), uma pergunta por vez;
   - descubra os identifiers com as mesmas tools da `alm-setup` (tabelas da etapa 3 dela), mostrando só **nomes** em
     lista numerada para o usuário escolher — nunca peça uuid, `FR_`, `OT_` ou attribute. Uma opção só (ex.: a
     busca por trecho achou uma project area) → use direto e diga qual; lista só com 2 ou mais;
   - project area: `list_project_areas(app_type=<CCM|RM|QM>, search_name=<trecho que o usuário disser>)`; não liste
     todas sem trecho;
   - guarde as escolhas **na conversa** e reaproveite nos pedidos seguintes (não pergunte de novo); não grave
     arquivo nenhum;
   - no fim, se o usuário for repetir pedidos desse projeto, ofereça gravar o que já foi escolhido com a `alm-setup`.
   Usuário recusou a setup → não ofereça de novo na mesma conversa.
4. **Prefira as tools de skill** (`ccm_*`, `rm_*`): saída enxuta e leitura em Markdown + YAML. As genéricas do IBM
   AI Hub ficam no `reference.md` de cada skill, para o que as de skill não cobrem.
5. **Siglas** ("ib 123", "hu 45", "ct 7") indicam o tipo; o número é o id web.
6. **Listas** saem como tabela que começa por **Código | Título**. Leitura de um item começa por
   `**<código>** — <título>`.
7. **Confirme toda escrita** (criar, atualizar, mudar estado, comentar, ligar) com um resumo por nomes: é visível
   ao time e o MCP não desfaz. Erros do MCP dizem o que corrigir (valores válidos, estados): use-os, sem tentativas
   às cegas.

## Credenciais

Ficam em `~/.config/mcp-alm/alm.properties` (Windows: `%APPDATA%\mcp-alm\alm.properties`, ou `MCP_ALM_CONFIG`).
**Nunca leia nem mostre esse arquivo**: ele tem a senha. Em erro de login (HTTP 401), peça ao usuário que o corrija.
