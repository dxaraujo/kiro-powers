---
name: "elk-setup"
description: "Configure, create, update or review the project's ELK/Kibana settings in .kiro/config/power/elk/elk.json: environment, index (data view), time field, fixed filters that scope the project's system, field aliases (nível, mensagem, serviço, logger, exceção...), known values, saved Kibana queries and the CSV download folder. Use when the user says \"configurar o ELK\", \"setup do ELK/Kibana\", \"criar/atualizar o elk.json\", \"qual índice o projeto usa\", \"adicionar a consulta salva X\", \"falta o campo Y no elk.json\", \"mudar a pasta de download\", or when another elk skill finds elk.json missing or incomplete. Does not search logs for the user."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
---

# elk-setup

Conduz o usuário, em conversa, na criação ou atualização de `.kiro/config/power/elk/elk.json`: a memória das skills
elk-logs, elk-exportar e elk-diagnostico. O MCP é agnóstico e não lê esse arquivo; ele guarda o que é do projeto
(índice, recorte, nomes de campos) para que as outras skills não redescubram nada a cada pedido. Você o grava, no
formato exato abaixo. Um arquivo por projeto: cada projeto consulta só o ELK dele.

## 1. Verificar a conexão

`elk_listar_indices(ambiente=<prod, ou o que o usuário disser>)` já testa credencial e certificado.

| Erro | O que pedir |
|---|---|
| `Arquivo de credenciais`/chave ausente, HTTP 401 | Criar/corrigir `~/.config/mcp-elk/elk.properties` (Windows: `%APPDATA%\mcp-elk\elk.properties`, ou `MCP_ELK_CONFIG`), `chmod 600` |
| `sem URL no elk.properties` | Acrescentar a linha do ambiente (`homol = https://...`) |
| `Certificado do servidor não confiável` | Gravar a cadeia PEM em `elk-bundle.pem`, na pasta do `elk.properties`, e reiniciar o MCP |

```ini
[DEFAULT]
user = SEU_USUARIO
password = SUA_SENHA
prod = https://logs.SEU-SERVIDOR
homol = https://hlogs.SEU-SERVIDOR
```

**Nunca leia nem mostre esse arquivo** (tem a senha). Espere o usuário confirmar e repita a chamada.

## 2. Arquivo existente

Leia `.kiro/config/power/elk/elk.json`. Não existe → todas as etapas. Existe → mostre um resumo (ambiente,
índices com `padrao`, quantos fixos/campos/consultas, `download.path`) e pergunte o que refazer: tudo, um índice,
só campos, só consultas, só download. Preserve o resto. Pedido pontual de outra skill ("falta o campo exceção") →
vá direto à etapa dele.

## 3. Etapas (uma pergunta por vez)

Mostre opções em lista numerada e deixe o usuário escolher; nunca escolha por ele. Não invente campo: todo campo
gravado veio de uma saída de tool desta conversa.

| # | O que fazer | elk.json |
|---|---|---|
| 1 | Pergunte o ambiente padrão (prod, homol, dev) | `ambiente` |
| 2 | Lista da etapa 1 (`elk_listar_indices`). Muitos data views → peça um trecho do nome e repita com `busca`. Mostre `padrao` e `espaco`; o usuário escolhe um ou mais. Dê a cada um um nome curto (sugira pelo padrão: `logs-app-x-*` → `aplicacao`) e pergunte qual é o padrão | `indices[nome].padrao`, `campo-tempo` (= `campo_tempo` da tool), `indice-padrao` |
| 3 | **Recorte do projeto (fixos).** Um índice costuma ter vários sistemas. Pergunte como o projeto se identifica nos logs (nome do sistema, aplicação, cliente). Ache o campo com uma amostra: `elk_buscar_logs(indice, inicio="now-15m", consulta="<nome do sistema>", limite=1)` e procure o campo cujo valor é o nome; confirme com `elk_contar(indice, inicio="now-15m", campos={campo: valor})` (total > 0). **Wildcard:** se o sistema tem variações de nome (ex.: `myapp`, `myapp-worker`, `myapp_batch`), use `myapp*` — valores com `*` viram filtro wildcard em vez de term. Índice já exclusivo do projeto → `fixos` fica vazio | `fixos` `{campo: valor ou wildcard}` |
| 4 | **Apelidos de campos.** Índices têm milhares de campos: não liste todos. Pegue 1–3 documentos com os fixos (`elk_buscar_logs(..., campos=fixos, limite=3)`) e proponha o campo para cada papel: `nivel` (INFO/ERROR), `mensagem`, `servico` (módulo/aplicação), `logger` (classe), `excecao` (stack trace/tipo), `host`, `uri`, `trace` (id de correlação). Pergunte também campos de negócio (CPF, protocolo, usuário, ID). Para dúvidas, `elk_listar_campos(indice, busca="<trecho>")`. Os apelidos permitem usar nomes curtos (ex.: `id` ou `app.id`) que resolvem para o caminho completo (ex.: `context.app.id`). Amostre também um documento de erro (`campos` = fixos + nível ERROR): erros costumam ter campos próprios (exceção, stack trace) e às vezes outra grafia do mesmo papel (`loggerName` × `logger_name`); havendo duas, grave a que tem mais documentos no recorte (`elk_contar(..., campos=fixos, consulta="_exists_:<campo>")` para cada uma) | `campos` `{apelido: campo}` |
| 5 | **Valores conhecidos.** Para cada apelido agregável de baixa cardinalidade (`nivel`, `servico`, categorias): `elk_contar(indice, inicio="now-1d", campos=fixos, agrupar_por=<campo>, top=20)`. `grupos` vazio = campo ausente nesse recorte ou não agregável (texto): confira com `elk_listar_campos` e, se houver, use a variante `.keyword` | `valores` `{apelido: [valor, ...]}` |
| 6 | **Consultas prontas (opcional).** `elk_listar_consultas(busca=<trecho>)` (peça um trecho do título; sem ele a lista vem com todos os spaces). O usuário escolhe; `indice` = o nome curto da etapa 2 cujo `padrao` bate com o da consulta. **Chave obrigatória `titulo:id`:** grave como `"<título>:<id>"` (ex.: `"Erros críticos:abc123"`) — o título é legível, o id garante identidade se o título mudar no Kibana | `consultas` `{"titulo:id": {indice, consulta?, filtros?, descricao?}}` |
| 7 | **Pasta de download.** Pergunte onde a elk-exportar grava os CSV; sugira `downloads/elk` e lembre de pô-la no `.gitignore` (logs têm dados pessoais) | `download.path` |

Consulta salva com `linguagem: kuery` (KQL) só entra se for simples (`campo:valor AND ...`); com `campo:{...}`
avise que o MCP não suporta e não grave.

## 4. Gravar

O formato é definido pelo JSON Schema #[[file:assets/elk.schema.json]] (fonte da verdade). Ele fica dentro do power
instalado, não no projeto: leia-o direto por esse caminho, relativo à pasta desta skill (não use busca no
workspace, que não o acha). Mostre o JSON completo, peça confirmação e grave na **raiz do repositório**
(`git rev-parse --show-toplevel`; sem git, a pasta do workspace). Cite o arquivo sempre como
`.kiro/config/power/elk/elk.json`, nunca por caminho absoluto. `$schema` é a primeira propriedade:

```json
{
  "$schema": "https://raw.githubusercontent.com/dxaraujo/kiro-powers/main/elk/skills/elk-setup/assets/elk.schema.json",
  "ambiente": "prod",
  "indice-padrao": "aplicacao",
  "indices": {
    "aplicacao": {
      "padrao": "logs-app-*",
      "campo-tempo": "@timestamp",
      "fixos": { "<campo.sistema>": "myapp*" },
      "campos": {
        "nivel": "<campo.nivel>",
        "mensagem": "<campo.mensagem>",
        "servico": "<campo.servico>",
        "logger": "<campo.logger>",
        "id": "context.app.id"
      },
      "valores": {
        "nivel": ["INFO", "WARN", "ERROR"],
        "servico": ["<servico-a>", "<servico-b>"]
      }
    }
  },
  "consultas": {
    "Erros críticos:abc123": { "indice": "aplicacao", "consulta": "<lucene>", "filtros": [] }
  },
  "download": { "path": "downloads/elk" }
}
```

- Só as chaves do schema; nada de URL do Kibana, usuário ou senha.
- `download.path` relativo à raiz, com `/`.

## 5. Conferir

1. **Estrutura:** releia o schema e o arquivo gravado: `$schema` primeiro, obrigatórios presentes, `indice-padrao`
   e todo `consultas[*].indice` existem em `indices`, nada a mais.
2. **Recorte:** `elk_contar(indice=<padrao>, inicio="now-15m", campos=<fixos>, agrupar_por=<campos.nivel>)` e mostre
   o total por nível. Total 0 → algum fixo está errado: volte à etapa 3.

## Erros comuns

| Erro | Certo |
|---|---|
| Listar os milhares de campos de `elk_listar_campos` sem `busca` | Amostra de documentos + `busca` por trecho |
| Gravar o nome do data view em `padrao` | O `padrao` (com `*`) da tool, que é o que vai em `indice` |
| Fixos vazios num índice compartilhado | Recorte pelo sistema do projeto (etapa 3) |
| Valores inventados ou traduzidos (`erro`) | Os de `grupos` de `elk_contar`, como vieram (`ERROR`) |
| Caminho absoluto em `download.path` ou citar `/home/...` | Relativo à raiz do repositório, com `/` |
| Buscar logs "para testar" além da conferência | Só as chamadas das etapas |
