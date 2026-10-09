# alm

Power do Kiro para o **IBM Engineering Lifecycle Management (ELM)** via OSLC, usando o MCP
[mcp-alm](https://github.com/dxaraujo/mcp-alm).

## O que faz

- **EWM/RTC (CCM):** consulta, busca, cria, atualiza, muda estado, comenta work items (IB, TR, DF, DT…) e lança
  horas trabalhadas (timesheet).
- **DOORS Next (RM):** consulta, busca, cria e atualiza requisitos (REQ, HU, UC, RN, MSG…).
- **Documentação do RM em OKF:** baixa os artefatos do DOORS Next para o repositório (um `.md` por artefato) e
  sincroniza só o que mudou no ALM.
- **ETM/RQM (QM):** consulta artefatos de teste (CT, PT, ST, TER…) — só leitura.
- **Comum / GC:** usuários, project areas, times, configuração global e links de rastreabilidade.

## Conteúdo

| Arquivo | Função |
|---|---|
| `plugin.json` | Manifesto e keywords de ativação |
| `mcp.json` | Servidor MCP `alm` (`uvx mcp-alm@latest`) |
| `steering/steering.md` | Visão geral do power, sempre carregada |
| `skills/alm-setup/` | Cria/atualiza `.kiro/config/power/alm/pa_<nome>.json` do projeto; cria iterações e planos |
| `skills/alm-ccm/` | Work items (EWM); `reference.md` com as tools genéricas |
| `skills/alm-rm/` | Requisitos (DOORS Next); `reference.md` com as tools genéricas |
| `skills/alm-sync/` | Sincroniza nos dois sentidos a documentação do RM como bundle OKF (`sync.md` + `index.md` gravados pelo MCP; conflito = pergunta ao usuário) |
| `skills/alm-qm/` | Testes (ETM) |
| `skills/alm-gc/` | Usuários, project areas, GC e rastreabilidade; `reference.md` com project areas, GC e qnames |

## Pré-requisitos

1. [uv](https://docs.astral.sh/uv/) instalado (`uvx` no PATH).
2. Credenciais em `~/.config/mcp-alm/alm.properties` (Windows: `%APPDATA%\mcp-alm\alm.properties`, ou o caminho
   em `MCP_ALM_CONFIG`):

   ```ini
   [DEFAULT]
   server = https://alm.SEU-SERVIDOR
   user = SEU_USUARIO
   password = SUA_SENHA
   ```

## Primeiros passos

Peça ao Kiro "configurar o ALM": a skill `alm-setup` valida a conexão e gera `.kiro/config/power/alm/pa_<nome>.json` com os ids da
project area. Depois é só pedir, por exemplo, "me mostre o ib 123456" ou "crie uma HU".

O setup é opcional: sem ele, as skills perguntam o que o pedido precisa (project area, tipo, iteração, pasta...),
descobrem os ids no servidor, mostram só nomes para você escolher e guardam as escolhas na conversa, sem gravar
arquivo. Com o setup feito, nada muda: elas usam o `pa_<nome>.json` sem perguntar.
