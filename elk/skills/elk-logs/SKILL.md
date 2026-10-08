---
name: "elk-logs"
description: "Look up and count application logs in ELK/Kibana through the `elk` MCP (read-only), up to 100 documents shown in the conversation. Use when the user wants to see or count specific logs: \"me mostra os logs do CPF/usuário/protocolo X\", \"quantos erros hoje\", \"tem ERROR na última hora?\", \"logs com timeout entre 10h e 10h15\", \"rode a consulta salva Y\", \"quais valores tem o campo Z\", \"o que aconteceu com a requisição <trace id>\", \"últimos logs do serviço W em homologação\". For writing logs to a CSV file use elk-exportar; for explaining why something failed (incident, spike, root cause) use elk-diagnostico."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
---

# elk-logs

Consultas pontuais de logs: contar e mostrar documentos na conversa. As regras comuns (elk.json, fixos, apelidos,
janela, Lucene, ambiente, dados pessoais) estão no steering do power; aqui fica o fluxo.

Fora do escopo: gravar em arquivo → **elk-exportar**; explicar causa, pico ou incidente → **elk-diagnostico**.

## Antes de chamar

1. Leia `.kiro/config/power/elk/elk.json`. Sem ele → ofereça a **elk-setup** e pare.
2. Monte os parâmetros comuns, que serão os mesmos nas duas chamadas:
   - `indice` = `indices[<nome>].padrao` (pedido sem índice: `indice-padrao`); `campo_tempo` = `campo-tempo`.
   - `campos` = `fixos` + filtros exatos do pedido traduzidos pelos apelidos (`nivel` ERROR →
     `{"<campos.nivel>": "ERROR"}`). Valor com caixa/forma de `valores`.
   - `consulta` (Lucene) só para texto livre ou curinga: `<campos.mensagem>:*timeout*`.
   - Consulta salva citada pelo nome → `consultas[<título>]`: `consulta` e `filtros` como estão, `indice` do
     índice apontado, mais os `fixos` dele.
   - `inicio`/`fim`: do pedido; sem período, `now-1h` e diga isso na resposta.
3. Termo que não está em `campos` nem em `valores` (ex.: "erros do módulo financeiro" sem apelido `servico`): use-o
   como texto em `consulta` e avise; se for recorrente, sugira a elk-setup.

## Fluxo

1. **Conte primeiro:** `elk_contar(indice, inicio, fim, consulta?, campos, filtros?, campo_tempo, ambiente)`. É
   barato e evita trazer documentos de uma janela gigante.
   - Pergunta é "quantos" → responda com o total (e `agrupar_por` se pediu "por X"). Fim.
   - Total 0 → diga os filtros e a janela usados; sugira ampliar a janela ou conferir o valor.
2. **Busque:** `elk_buscar_logs(<mesmos parâmetros>, limite, retornar, mais_recentes)`.
   - `limite`: o que o usuário pediu, senão 20; teto 100.
   - `retornar`: `@timestamp`/`campo-tempo` + os campos de `campos` que importam ao pedido (`nivel`, `mensagem`,
     `servico`, `logger` e o filtro de negócio). Sem `retornar` cada documento vem com dezenas de campos e enche
     o contexto.
   - `mais_recentes=False` quando o pedido é "o primeiro", "quando começou".
3. **Total > 100 e o usuário quer tudo** → mostre os 20 mais recentes e ofereça a **elk-exportar**. Não pagine com
   várias buscas.

## Como responder

Comece pela linha de contexto: `**<total>** documentos · <ambiente> · <inicio> → <fim> · <índice>` e, se houver,
`mostrando <retornados>`. Depois uma tabela markdown com as colunas de `retornar`, nesta ordem:

| Data/hora | Nível | Serviço | Mensagem |
|---|---|---|---|
| 08/10 10:55:59 | ERROR | api-gestao | Timeout ao chamar ... |

- Data/hora em Brasília (`@timestamp` vem em UTC: subtraia 3h), formato `dd/MM HH:mm:ss`.
- Mensagem longa: primeiros ~150 caracteres na tabela; stack trace completo só se pedido, num bloco de código.
- Contagem agrupada: tabela **Valor | Total | %**.
- Feche com a consulta usada em uma linha (`campos` + `consulta`), para o usuário refazer no Kibana.

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
