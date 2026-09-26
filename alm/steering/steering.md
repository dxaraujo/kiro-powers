---
inclusion: always
---

# ALM Power

Este power dá acesso ao **IBM Engineering Lifecycle Management (ELM)** via OSLC, pelo MCP `alm`
(`uvx mcp-alm@latest`). As tools têm os mesmos nomes e parâmetros do IBM Engineering AI Hub.

## O que ele cobre

| Aplicação | O que faz | Skill |
|---|---|---|
| **EWM/RTC (CCM)** | Consultar, listar, buscar, criar, atualizar, mudar estado e comentar work items (IB, TR, DF, DT, IMP, RSC, REU); itens de sprint, iteração ou plano | `alm-ccm` |
| **DOORS Next (RM)** | Consultar, buscar, listar, criar e atualizar requisitos (REQ, HU, UC, RN, MSG, ET, etc.); pastas, tipos, componentes, streams e baselines | `alm-rm` |
| **ETM/RQM (QM)** | Consultar e buscar artefatos de teste (CT, PT, ST, SCT, TER, RT) — só leitura | `alm-qm` |
| **Comum / GC** | Quem sou eu, usuários, project areas, times, configuração global e rastreabilidade entre work item, requisito e caso de teste | `alm-gc` |
| **Configuração** | Criar ou atualizar o arquivo `alm/pa_<nome>.json` do projeto | `alm-setup` |

## Como usar

1. **Carregue a skill da área** antes de chamar as tools: ela traz as siglas, os ids e a ordem das chamadas.
2. **Leia `alm/pa_*.json` do projeto** (gerado pela `alm-setup`). Ele tem os UUIDs de project area, times,
   membros, iterações, pastas e tipos — evita chamadas de descoberta. Se não existir, ofereça rodar a `alm-setup`.
3. **Prefira as tools enxutas** (`ccm_*`, `rm_*`), que usam os ids do `pa_*.json`. Use as genéricas só para o que
   elas não cobrem.
4. **Siglas** ("ib 123", "hu 45", "ct 7") indicam o tipo do artefato; o número é o id web.
5. **Listas e buscas** saem sempre como tabela que começa pelas colunas **Código | Título** (código = o id que a tool
   recebe), nunca só com títulos. Detalhes na seção "Como responder" de cada skill.

## Credenciais

Ficam em `~/.config/mcp-alm/alm.properties` (Windows: `%APPDATA%\mcp-alm\alm.properties`, ou `MCP_ALM_CONFIG`).
**Nunca leia nem mostre esse arquivo**: ele tem a senha. Em erro de login (HTTP 401), peça ao usuário que o corrija.
