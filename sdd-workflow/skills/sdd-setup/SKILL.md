---
name: "sdd-setup"
description: "Configura o fluxo SDD (power sdd-workflow) no projeto: gera .kiro/steering/sdd-projeto.md (steering de produto/tecnologia/estrutura — padrão do Kiro ou os arquivos informados —, branch base, comandos de build/teste/cobertura, banco, testes funcionais, prefixos das Tasks, executores), cria os agentes sdd-especificador, sdd-codificador, sdd-revisor e sdd-orquestrador em .kiro/agents/ a partir das referências do power, perguntando para cada agente quais skills e MCPs já existentes ele pode usar, e prepara .kiro/aprendizado/. Também atualiza a configuração e os agentes depois de uma atualização do power. Use em \"configurar o sdd-workflow\", \"setup do sdd\", \"criar os agentes do sdd\", \"atualizar a configuração do sdd-workflow\", \"atualizar os agentes do sdd\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "setup, configurar, instalar, sdd, sdd-workflow, agentes, criar agentes, steering, configuracao, atualizar agentes"
---

# sdd-setup — Configurar o fluxo SDD no projeto

O power não traz agentes (o Kiro não os distribui por power): esta skill os cria no projeto a partir de
[references/agents/](references/agents/) e grava a configuração do projeto, que todas as skills `sdd-*` leem.

**Uma pergunta por vez**, sempre com a opção recomendada e o que foi detectado. Nada é gravado antes do resumo
final (Passo 6) e do "ok". Nunca leia nem mostre arquivos de credenciais.

## Passo 0 — Onde estou

1. **Pasta do power:** `~/.kiro/powers/installed/sdd-workflow` (o Kiro instala sempre ali, em Linux, macOS e
   Windows). Confirme que `~/.kiro/powers/installed/sdd-workflow/steering/steering.md` existe.
   **Caminhos nos agentes e no steering — sempre relativos, nunca absolutos** (os `.kiro/agents/*.json` e o
   `sdd-projeto.md` são versionados e usados em Linux e Windows):
   - arquivo do projeto → relativo à raiz do repositório: `file://.kiro/steering/tech.md`, `skill://.kiro/skills/x/SKILL.md`;
   - arquivo do power ou do usuário → relativo ao home: `~/.kiro/powers/installed/...`, `~/.kiro/skills/...`
     (o Kiro expande o `~` em `file://` e `skill://`);
   - prompt do agente → relativo ao `.json`: `file://./prompts/<agente>.md`;
   - separador sempre `/`; nunca `/Users/…`, `/home/…`, `C:\…`, `\` nem `%USERPROFILE%`/`$HOME`.
2. Raiz do repositório: `git rev-parse --show-toplevel` (sem git → avise: o fluxo depende de branches e PRs).
3. Já existe `.kiro/steering/sdd-projeto.md` ou `.kiro/agents/sdd-*.json`? → **modo atualização**: mostre a
   configuração atual em uma tabela e pergunte o que mudar ("nada — só regenerar os agentes" é uma opção, útil
   depois de atualizar o power). Responda só o que mudou; o resto é mantido.

## Passo 1 — Steering do projeto

O fluxo precisa de três papéis de steering: **produto** (domínio, glossário), **tecnologia** (stack, regras de
codificação, banco) e **estrutura** (pastas, camadas, padrões).

- Existem `.kiro/steering/product.md`, `tech.md` e `structure.md` → confirme ("Uso os padrões do Kiro? sim/não").
- Faltam ou a pessoa disse "não" → liste os `.md` de `.kiro/steering/` (recursivo) e os documentos do repositório
  que parecem guias (`README*`, `docs/**/*.md`, `CONTRIBUTING*`, `AGENTS.md`, `CLAUDE.md`) e pergunte, **um papel
  por vez**, qual arquivo faz aquele papel (pode ser o mesmo arquivo para mais de um, ou "nenhum").
  Papel sem arquivo → ofereça gerar o padrão do Kiro a partir do código (o próprio Kiro faz isso em "Generate
  Steering Docs") e siga registrando "nenhum".
- Depois pergunte quais **steering extras** (contexto de domínio) os agentes devem carregar (múltipla escolha da
  lista; padrão: nenhum).
- **Regras críticas:** leia o steering de tecnologia/estrutura e proponha as regras que, se violadas, causam perda de
  dado, duplicidade ou falha em produção (ex.: transação, concorrência, acesso a dados). A pessoa confirma, edita ou
  diz "nenhuma além do steering".

## Passo 2 — Projeto

Detecte e proponha; pergunte só o que não der para inferir.

| Item | Como detectar |
|---|---|
| Branch base | `git symbolic-ref refs/remotes/origin/HEAD`; branches `develop`/`desenvolvimento`/`main`/`master` |
| Prefixo da branch | branches remotas existentes (`feature/`, `feat/`…); padrão `feature/` |
| Mensagem de commit | últimos `git log --oneline -20` (padrão por Task? Conventional Commits?) |
| Abrir PR | `gh`/`glab` no PATH e o host do `origin`; senão "entregar título e descrição para a pessoa abrir" |
| Compilar, testar, cobertura | arquivo de build (`pom.xml`, `build.gradle*`, `package.json`, `pyproject.toml`, `go.mod`, `*.csproj`, `Cargo.toml`, `Makefile`) e o steering de tecnologia; gate e exclusões da configuração de cobertura, se houver |
| Banco | servidores MCP em `.kiro/settings/mcp.json` e `~/.kiro/settings/mcp.json` — qual é o de consulta ao banco (ou "não há") |
| Testes funcionais | pastas de massa/seed/fixtures, como a aplicação é executada (README, scripts), onde ficam os logs |
| Prefixos das Tasks | padrão `[ESPEC]`, `[BE]`, `[QA]`, `[BD]` — pergunte se o time usa outros |
| ALM | power `alm` instalado (`~/.kiro/powers/installed/alm/`) e `.kiro/config/alm-power/pa_*.json` no repositório; sem → `sem power` |

## Passo 3 — Skills e MCPs por agente

Monte o **inventário** (nome + início da `description`) de:
- `.kiro/skills/*/SKILL.md` (projeto), `~/.kiro/skills/*/SKILL.md` (usuário) e
  `~/.kiro/powers/installed/*/skills/*/SKILL.md` (outros powers);
- excluindo as `sdd-*` (já fazem parte do fluxo).

Para **cada agente, um de cada vez**, mostre o inventário numerado **sem** as skills que o agente já tem e pergunte
quais ele pode invocar (números separados por vírgula, "nenhuma" ou "as mesmas do <agente>"):

| Agente | Já tem | Sugestão de extras |
|---|---|---|
| `sdd-especificador` | `sdd-especificar` | skills de domínio/negócio do projeto |
| `sdd-codificador` | `sdd-criar-spec` | skills de código e de testes do projeto (padrões de componentes, testes, cobertura) |
| `sdd-revisor` | `sdd-revisar`, `sdd-validar-requisitos`, `sdd-criar-spec` | skills de padrão de código e de cobertura (para julgar) |
| `sdd-orquestrador` | `sdd-lote`, `sdd-tarefa`, `sdd-alm-publicar-requisitos` | normalmente nenhuma |

Na mesma rodada de cada agente, pergunte também:
- **MCPs** além do banco (lista dos servidores configurados; padrão: nenhum). O MCP de banco do Passo 2 entra em
  todos, como somente leitura. **Nunca ofereça o MCP `alm`**: o ALM é do power `alm` (skills `alm-ccm`, `alm-rm`,
  `alm-gc` com o MCP dele) e os agentes não o redeclaram — no kiro-cli um agente não herda o power, e o MCP sem as
  skills `alm-*` seria usado sem as regras delas. Nos agentes os passos de ALM seguem o caminho "sem ALM" do fluxo e
  ficam para a pessoa fazer na sessão com o power `alm` (IDE).
- Só `sdd-codificador` e `sdd-orquestrador`: **agentes do projeto** que podem ser chamados como subagentes (lista de
  `.kiro/agents/*.json` e `~/.kiro/agents/*.json`, exceto `sdd-*`). Para cada agente escolhido, pergunte que tipo de
  item do `tasks.md` ele executa — vira a tabela **Executores** do `sdd-projeto.md`.

## Passo 4 — Montar os arquivos (em memória)

1. **`.kiro/steering/sdd-projeto.md`** a partir de [references/projeto-template.md](references/projeto-template.md)
   com as respostas dos Passos 1–3 (no modo atualização, preserve a seção **Regras promovidas** como está).
2. **Agentes** — para cada `references/agents/<agente>.json`:
   - `resources`: acrescente `file://<arquivo>` de cada steering do Passo 1 (produto, tecnologia, estrutura, extras;
     sem duplicar) e `skill://<caminho relativo do SKILL.md>` de cada skill extra do agente (regras do Passo 0: do projeto
     `.kiro/skills/...`; do usuário ou de outro power `~/.kiro/...`);
   - `tools`: acrescente `@<servidor>` (ou `@<servidor>/<tool>`) do banco e dos MCPs escolhidos (nunca `@alm`
     nem o bloco `alm` em `mcpServers`);
   - subagentes escolhidos → acrescente em `toolsSettings.subagent.availableAgents` (no `sdd-codificador`, que não
     tem, inclua também `subagent` em `tools`/`allowedTools` e a permissão `{"capability": "subagent", "effect": "allow"}`).
3. **Prompts** — `references/agents/prompts/<agente>.md` → `.kiro/agents/prompts/<agente>.md`, trocando:
   - `{{SKILLS_EXTRAS}}` → `Skills extras do projeto: \`a\`, \`b\` — carregue a do artefato antes de usá-la.` (ou
     remova a linha se não houver);
   - `{{SUBAGENTES}}` → lista dos subagentes (orquestrador: os `sdd-*` + os do projeto; codificador:
     `Subagentes do projeto: \`x\` (<tipo de item>) — passe a pasta do IB e os itens; sem a ferramenta de subagente,
     faça em sequência.` ou remova a linha).
4. **Aprendizado** — se não existir `.kiro/aprendizado/`, copie [references/aprendizado/](references/aprendizado/)
   (`retrabalho.md`, `checklists/README.md`, `promocoes/README.md`). Existindo, **nunca** sobrescreva.
5. **`.gitignore`** — acrescente `.kiro/local/` se ainda não estiver.

## Passo 5 — Validar

- `kiro-cli agent validate --path .kiro/agents/<agente>.json` para cada agente, se o `kiro-cli` existir. A saída
  vazia é sucesso (o código de saída é sempre 0): qualquer texto de erro → corrija e valide de novo.
- Todo `skill://` e `file://` dos agentes aponta para arquivo existente (resolvendo `~` no home e o resto a partir
  da raiz do repositório) e é relativo: nenhum caminho absoluto (`/…`, `C:\…`), `\` ou variável de ambiente.
- O mesmo vale para os caminhos escritos no `sdd-projeto.md` (ex.: ALM `.kiro/config/alm-power/pa_<nome>.json`).
- `sdd-projeto.md` sem nenhum `<…>` de template sobrando (o que não se aplica fica "não há"/"nenhum").

## Passo 6 — Resumo e gravação

```
⚙️ sdd-workflow — <projeto>
Steering: produto <arq> · tecnologia <arq> · estrutura <arq> · extras <N>
Git: base <branch> · prefixo <prefixo> · PR <ferramenta | texto para a pessoa>
Comandos: testes <cmd> · cobertura <cmd> (gate <…>)
Banco: <MCP | não há> · ALM: <power alm | sem power>
| Agente | Skills extras | MCPs | Subagentes |
Arquivos: .kiro/steering/sdd-projeto.md · .kiro/agents/sdd-*.json + prompts/ · .kiro/aprendizado/ (<novo | mantido>) · .gitignore
Gravar? ("ok")
```

No modo atualização, mostre o diff dos arquivos que mudam. "ok" → grave, rode o Passo 5 nos arquivos gravados e
sugira o commit (`.kiro/steering/sdd-projeto.md`, `.kiro/agents/`, `.kiro/aprendizado/`, `.gitignore`) — commit só
com confirmação. Termine com o próximo passo: "vamos trabalhar na task <id>" (`sdd-tarefa`) ou "onde parei?"
(`sdd-status`).

## Regras

- Não altere nada fora de `.kiro/` e do `.gitignore`.
- Agente `.json` já existente e editado à mão → mostre o diff antes de sobrescrever e pergunte.
- As skills `sdd-*` ficam no power — nunca copie para o projeto (uma atualização do power as atualiza; rode a
  `sdd-setup` em modo atualização depois, para refazer os caminhos e os prompts dos agentes).
