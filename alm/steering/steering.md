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
| **EWM/RTC (CCM)** | Listar, ler, criar, atualizar, mudar estado e comentar work items (IB, TR, DF, DT, IMP, RSC, REU); itens de sprint, iteração ou plano | `alm-ccm` |
| **DOORS Next (RM)** | Buscar, ler, criar e atualizar requisitos (REQ, HU, UC, RN, MSG, ET...), atributos, links entre requisitos e artefatos embutidos | `alm-rm` |
| **ETM/RQM (QM)** | Consultar artefatos de teste (CT, PT, ST, SCT, TER, RT) — só leitura | `alm-qm` |
| **Comum / GC** | Quem sou eu, usuários, project areas, configuração global e rastreabilidade entre work item, requisito e teste | `alm-gc` |
| **Configuração** | Criar/atualizar `.kiro/config/alm-power/pa_<nome>.json`; criar iterações e planos | `alm-setup` |

## Como usar

1. **Carregue a skill da área** antes de chamar as tools.
2. **alm.json primeiro, servidor depois.** `.kiro/config/alm-power/pa_*.json` (gerado pela `alm-setup`) resolve nomes → identifiers
   sem chamadas de descoberta. Sem o arquivo, ou faltando um nome, ofereça a `alm-setup`.
3. **Prefira as tools de skill** (`ccm_*`, `rm_*`): saída enxuta e leitura em Markdown + YAML. As genéricas do IBM
   AI Hub ficam no `reference.md` de cada skill, para o que as de skill não cobrem.
4. **Siglas** ("ib 123", "hu 45", "ct 7") indicam o tipo; o número é o id web.
5. **Listas** saem como tabela que começa por **Código | Título**. Leitura de um item começa por
   `**<código>** — <título>`.
6. **Confirme toda escrita** (criar, atualizar, mudar estado, comentar, ligar) com um resumo por nomes: é visível
   ao time e o MCP não desfaz. Erros do MCP dizem o que corrigir (valores válidos, estados): use-os, sem tentativas
   às cegas.

## Credenciais

Ficam em `~/.config/mcp-alm/alm.properties` (Windows: `%APPDATA%\mcp-alm\alm.properties`, ou `MCP_ALM_CONFIG`).
**Nunca leia nem mostre esse arquivo**: ele tem a senha. Em erro de login (HTTP 401), peça ao usuário que o corrija.
