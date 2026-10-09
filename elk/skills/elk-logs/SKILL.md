---
name: "elk-logs"
description: "Look up and count application logs in ELK/Kibana through the `elk` MCP, up to 100 documents shown in the conversation, and save the query built in the conversation as a Kibana saved query. Use when the user wants to see or count specific logs: \"me mostra os logs do usuário/transação X\", \"quantos erros hoje\", \"tem ERROR na última hora?\", \"logs com timeout entre 10h e 10h15\", \"rode a consulta salva Y\", \"quais valores tem o campo Z\", \"o que aconteceu com a requisição <trace id>\", \"últimos logs do serviço W em homologação\", and at the end of a search \"salva essa consulta\", \"cria uma consulta no Kibana com esse filtro\", \"guarda essa busca como X\". For writing logs to a CSV file use elk-exportar; for explaining why something failed (incident, spike, root cause) use elk-diagnostico."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.4.0"
---

# elk-logs

Consultas pontuais de logs: contar e mostrar documentos na conversa. As regras comuns (elk-<ambiente>.json, fixos,
apelidos, janela, Lucene, ambiente, dados pessoais) estão no steering do power; aqui fica o fluxo.

Fora do escopo: gravar em arquivo → **elk-exportar**; explicar causa, pico ou incidente → **elk-diagnostico**.

## Antes de chamar

1. Identifique o ambiente (regra 6 do steering).
2. Leia `.kiro/config/power/elk/elk-<ambiente>.json`. Sem ele → ofereça a **elk-setup** e pare.
3. Monte os parâmetros comuns, que serão os mesmos nas duas chamadas:
   - `indice` = `indices[<nome>].padrao` (pedido sem índice: `indice-padrao`); `campo_tempo` = `campo-tempo`.
   - `campos` = `fixos` + filtros exatos do pedido traduzidos pelos apelidos (`nivel` ERROR →
     `{"<campos.nivel>": "ERROR"}`). Valor com caixa/forma de `valores`.
   - `consulta` (Lucene) só para texto livre ou curinga: `<campos.mensagem>:*timeout*`.
   - Consulta salva citada pelo título → regra 5 do steering (`elk_obter_consulta`).
   - `inicio`/`fim`: do pedido; sem período, `now-1h` e diga isso na resposta.
   - `ambiente`: o ambiente identificado na etapa 1.
4. Termo que não está em `campos` nem em `valores`: regra 3.1 do steering.

## Fluxo

1. **Conte primeiro:** `elk_contar(indice, inicio, fim, consulta?, campos, filtros?, campo_tempo, ambiente)`. É
   barato e evita trazer documentos de uma janela gigante.
   - Pergunta é "quantos" → responda com o total (e `agrupar_por` se pediu "por X"). Fim.
   - Pergunta é "quais valores tem o campo Z" → `agrupar_por=<Z>`, `top=20`. Fim.
   - Total 0 → diga os filtros e a janela usados; sugira ampliar a janela ou conferir o valor.
2. **Busque:** `elk_buscar_logs(<mesmos parâmetros>, limite, retornar, mais_recentes)`.
   - `limite`: o que o usuário pediu, senão 20; teto 100.
   - `retornar`: `@timestamp`/`campo-tempo` + os campos de `campos` que importam ao pedido (`nivel`, `mensagem`,
     `servico`, `logger` e o filtro de negócio). Sem `retornar` cada documento vem com dezenas de campos e enche
     o contexto. Busca de ERROR → inclua também `stacktrace`.
   - `mais_recentes=False` quando o pedido é "o primeiro", "quando começou".
3. **Total > 100 e o usuário quer tudo** → mostre os 20 mais recentes e ofereça a **elk-exportar**. Não pagine com
   várias buscas.

## Como responder

Comece pela linha de contexto: `**<total>** documentos · <ambiente> · <inicio> → <fim> · <índice>` e, se houver,
`mostrando <retornados>`. Depois uma tabela markdown com as colunas de `retornar`, nesta ordem:

| Data/hora | Nível | Serviço | Mensagem |
|---|---|---|---|
| 08/10 10:55:59 | ERROR | api | Timeout ao chamar ... |

- Data/hora em Brasília (`@timestamp` vem em UTC: subtraia 3h), formato `dd/MM HH:mm:ss`.
- Mensagem longa: primeiros ~150 caracteres na tabela. Stack trace fora da tabela: a do erro mais recente (ou de
  cada tipo de `excecao` distinto) num bloco de código, cortada na exceção, no `Caused by` mais interno e nos frames
  da aplicação; completa só se pedido.
- Contagem agrupada: tabela **Valor | Total | %**.
- Feche com a consulta usada em uma linha (`campos` + `consulta`), para o usuário refazer no Kibana.

## Salvar a consulta no Kibana

Quando o usuário, depois de buscar e refinar, pede para salvar ("salva essa consulta", "guarda como X"):

1. **Consulta:** a **última** que ele aceitou nesta conversa (não a primeira tentativa). Converta tudo para uma
   `consulta` Lucene única, com os `fixos` incluídos para funcionar também no Discover: valor exato →
   `campo:"valor"`; valor com `*` → `campo:valor*` (sem aspas); texto livre como estava; tudo unido por `AND`.
   Veio de consulta salva → mantenha os `filtros` dela em `filtros`.
2. **Título:** o que o usuário deu; senão, sugira um curto que descreva o filtro (`Erros de timeout no serviço W`).
   Título já em `consultas` → pergunte se quer outro nome.
3. **Confirme** em um bloco: título, ambiente, `indice` (`padrao`), `espaco` (`default`, salvo se o usuário disser
   outro) e a `consulta`. Sem confirmação, não grave nada.
4. `elk_criar_consulta(titulo, indice, consulta, filtros?, descricao?, espaco, ambiente)` → devolve o `id`.
5. Registre em `consultas` do `.kiro/config/power/elk/elk-<ambiente>.json`:
   `"<titulo>": { "id": "<id>", "espaco": "<espaco>" }` (omita `espaco` se for `default`), preservando o resto do
   arquivo. Assim "rode a consulta <titulo>" funciona depois. Sem o arquivo → só informe o `id` e ofereça a
   elk-setup.

Responda: `Consulta salva no Kibana: "<titulo>" · <ambiente> · espaço <espaco>` + a `consulta` gravada.

## Erros

| Mensagem | O que fazer |
|---|---|
| `Consulta vazia` | Falta filtro: sempre há `fixos` ou o pedido; sem nenhum, pergunte o que buscar |
| `` `limite` deve estar entre 1 e 100 `` | Use ≤ 100; mais que isso → elk-exportar |
| `Ambiente desconhecido` / `sem URL no elk.properties` | Use prod, homol ou dev; ambiente sem URL → peça ao usuário para configurar o `elk.properties` |
| `HTTP 400` com `query_string`/`parse` | Lucene inválido: aspas em valores com espaço/`:` e operadores em maiúsculas; refaça uma vez |
| `HTTP 400` com `fielddata`/`aggregat` | `agrupar_por` em campo texto: use a variante `.keyword` |
| `HTTP 401` / certificado | Veja o steering (credenciais) |
| Timeout ou 5xx | Reduza a janela pela metade e tente de novo uma vez |
