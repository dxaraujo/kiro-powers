# kiro-powers

Powers do [Kiro](https://kiro.dev) mantidos por [@dxaraujo](https://github.com/dxaraujo). Cada pasta é um power
independente, com manifesto (`plugin.json`), steering, skills e, quando usa, servidor MCP (`mcp.json`).

## Powers

| Power | O que faz | MCP |
|---|---|---|
| [alm](alm/) | IBM Engineering Lifecycle Management (ELM) via OSLC: work items do EWM/RTC, requisitos do DOORS Next, testes do ETM, configuração global e rastreabilidade | [mcp-alm](https://github.com/dxaraujo/mcp-alm) |
| [sdd-workflow](sdd-workflow/) | Fluxo de Spec-Driven Development (especificador, codificador, testador) com gates, judge, devoluções com causa raiz, aprendizado contínuo, lote e planejamento de sprints; cria os agentes no projeto pela `sdd-setup` | — (usa o `alm`, se instalado) |

## Instalação

1. Para powers com MCP, instale o [uv](https://docs.astral.sh/uv/): os servidores MCP rodam com `uvx`.
2. No Kiro, adicione o power pelo painel **Powers**, apontando para a pasta do power neste repositório
   (ex.: `https://github.com/dxaraujo/kiro-powers/alm`) ou para uma cópia local dela.
3. Siga o `README.md` da pasta do power para credenciais e primeiros passos.

## Estrutura de um power

```
<power>/
├── plugin.json        # manifesto e keywords de ativação
├── mcp.json           # servidor(es) MCP usados pelo power (se houver)
├── README.md          # pré-requisitos e primeiros passos
├── steering/          # contexto sempre carregado
└── skills/<skill>/    # uma pasta por skill, com SKILL.md
```

## Licença

[MIT](LICENSE)
