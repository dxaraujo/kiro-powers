# elk

Power do Kiro para os **logs do ELK** (Elasticsearch + Kibana), usando o MCP
[mcp-elk](https://github.com/dxaraujo/mcp-elk). Lê os logs; a única escrita é criar consulta salva no Kibana, com
confirmação. Agnóstico: índice, campos e consultas do projeto ficam em `.kiro/config/power/elk/elk-<ambiente>.json`
(`elk-prod.json`, `elk-homol.json`, `elk-dev.json`), gerados pela `elk-setup`.

## O que faz

- **Logs:** busca e conta logs (até 100 documentos na conversa), por filtros, texto ou consultas salvas do Kibana.
- **Exportar:** grava resultados em CSV na pasta de download do projeto, direto pelo MCP, sem passar pela conversa.
- **Diagnóstico:** investiga incidentes comparando o período do problema com um período normal (volume, taxa de
  erro, onde concentra, quando começou, evidências e hipótese).
- **Consultas salvas:** usa as do Kibana pelo título e salva no Kibana a consulta montada na conversa (`elk-logs`).

## Conteúdo

| Arquivo | Função |
|---|---|
| `plugin.json` | Manifesto e keywords de ativação |
| `mcp.json` | Servidor MCP `elk` (`uvx mcp-elk@latest`) |
| `steering/steering.md` | Visão geral e regras comuns, sempre carregada |
| `skills/elk-setup/` | Cria/atualiza `.kiro/config/power/elk/elk-<ambiente>.json`; `assets/elk.schema.json` é o JSON Schema |
| `skills/elk-logs/` | Buscar e contar logs; salvar a consulta no Kibana |
| `skills/elk-exportar/` | Exportar CSV para `download.path` |
| `skills/elk-diagnostico/` | Investigar incidentes e causa raiz |

## Pré-requisitos

1. [uv](https://docs.astral.sh/uv/) instalado (`uvx` no PATH).
2. Credenciais em `~/.config/mcp-elk/elk.properties` (Windows: `%APPDATA%\mcp-elk\elk.properties`, ou o caminho
   em `MCP_ELK_CONFIG`). `prod`, `homol` e `dev` são as URLs do Kibana; só `prod` é obrigatória:

   ```ini
   [DEFAULT]
   user = SEU_USUARIO
   password = SUA_SENHA
   prod = https://logs.SEU-SERVIDOR
   homol = https://hlogs.SEU-SERVIDOR
   dev = https://dlogs.SEU-SERVIDOR
   ```

3. CA interna não instalada na máquina: grave a cadeia PEM em `elk-bundle.pem`, na mesma pasta.

## Primeiros passos

Peça ao Kiro "configurar o ELK": a skill `elk-setup` pergunta o ambiente, escolhe o índice, o recorte do sistema,
os campos e a pasta de download, e grava `.kiro/config/power/elk/elk-<ambiente>.json` (repita para cada ambiente). Depois é só pedir, por exemplo, "quantos erros na última hora",
"exporta os erros de ontem" ou "o sistema caiu às 10h, o que aconteceu?".
