---
name: "elk-logs"
description: "Look up and count application logs in ELK/Kibana through the `elk` MCP, up to 100 documents shown in the conversation, save the query built in the conversation as a Kibana saved search (Discover, KQL or Lucene) and update an existing saved search. Use when the user wants to see or count specific logs: \"me mostra os logs do usuário/transação X\", \"quantos erros hoje\", \"tem ERROR na última hora?\", \"logs com timeout entre 10h e 10h15\", \"rode a consulta salva Y\", \"quais valores tem o campo Z\", \"o que aconteceu com a requisição <trace id>\", \"últimos logs do serviço W em homologação\", and at the end of a search \"salva essa consulta\", \"cria uma consulta no Kibana com esse filtro\", \"guarda essa busca como X\", \"altera/corrige a consulta salva X\", \"adiciona o filtro Y na consulta X\". For writing logs to a CSV file use elk-exportar; for explaining why something failed (incident, spike, root cause) use elk-diagnostico; for the per-step execution summary of a Spring Batch job use elk-job-logs."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.1.5"
---

# elk-logs

Consultas pontuais de logs: contar e mostrar documentos na conversa. As regras comuns (elk-<ambiente>.json, fixos,
apelidos, janela, Lucene, ambiente, dados pessoais) estão no steering do power; aqui fica o fluxo.

Fora do escopo: gravar em arquivo → **elk-exportar**; explicar causa, pico ou incidente → **elk-diagnostico**.

## Antes de chamar

1. Identifique o ambiente (regra 6 do steering).
2. Leia `.kiro/config/power/elk/elk-<ambiente>.json`. Sem ele → regra 1.1 do steering (sem setup): pergunte índice
   e recorte e siga — **exceto** se o pedido é uma consulta salva (regra 5): ela já traz índice e filtros, então só
   pergunte setup sim/não.
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

Quando o usuário, depois de buscar e refinar, pede para salvar ("salva essa consulta", "guarda como X"), crie uma
busca salva do Discover (ligada ao data view):

1. **Consulta:** a **última** que ele aceitou nesta conversa (não a primeira tentativa), separada como o Discover
   mostra:
   - **Filtros (pílulas):** os `fixos` + os filtros exatos do pedido vão em `campos` (`{campo: valor}`; valor com
     `*` vira wildcard). É o recorte que aparece como filtro no Kibana.
   - **Barra de busca:** só o que não é filtro exato — texto livre e comparações — em `consulta`. KQL
     (`linguagem="kuery"`, padrão): `campo: *trecho*`, `campo > 0`, unidos por `and`; sem `campo:{...}`. Use Lucene
     (`linguagem="lucene"`) só se o usuário pedir ou precisar de `campo:[1 TO 5]`, `campo:valor~`, escape `\-`.
     Sem nada disso, `consulta` fica vazia.
   Veio de consulta salva → mantenha os `filtros` dela em `filtros`.
   **Parâmetros:** filtro cujo valor muda a cada execução (o usuário diz "será sempre passado", "por <campo>") vai
   em `campos` com um valor de exemplo (`0` para número, `""` para texto) — vira a pílula que o usuário edita no
   Discover — e em `descricao` como `Parâmetros: <campo>[, <campo>...]` (regra 5 do steering).
   **Colunas:** os campos de `retornar` usados na busca, sem o campo de tempo (o Discover já o mostra).
2. **Título:** o que o usuário deu; senão, sugira um curto que descreva o filtro (`Erros de timeout no serviço W`).
   Título já existe (em `consultas` ou em `elk_listar_consultas(busca=<título>)`) → pergunte: **atualizar** a
   existente (seção abaixo) ou usar outro nome.
3. **Espaço:** o do data view do `indice` (`elk_listar_indices(busca=<trecho do padrão>)` mostra o `espaco`). O
   data view existe em mais de um → pergunte em qual salvar.
4. **Confirme** em um bloco: título, ambiente, `indice` (`padrao`), `espaco`, filtros (`campos`), `consulta` e
   linguagem, parâmetros e `colunas`. Sem confirmação, não grave nada.
5. `elk_criar_consulta(titulo, indice, campos, consulta?, filtros?, colunas, descricao?, espaco, linguagem,
   ambiente)` → devolve o `id`.
   `Data view ... não existe no espaço` → volte ao passo 3.
6. Registre em `consultas` do `.kiro/config/power/elk/elk-<ambiente>.json`:
   `"<titulo>": { "id": "<id>", "espaco": "<espaco>" }` (omita `espaco` se for `default`), preservando o resto do
   arquivo. Assim "rode a consulta <titulo>" funciona depois. Sem o arquivo → só informe o `id` e ofereça a
   elk-setup.

Responda: `Consulta salva no Kibana: "<titulo>" · <ambiente> · espaço <espaco>` + os filtros e a `consulta`
gravados.

## Atualizar uma consulta salva

Quando o usuário pede para mudar uma consulta que já existe ("corrige a consulta X", "adiciona o filtro Y", "tira a
coluna Z", "renomeia"):

1. Ache `id` e `espaco`: `consultas[<título>]`, senão `elk_listar_consultas(busca=<trecho do título>)`. Só o tipo
   `search` é atualizável; `query` → ofereça criar uma busca salva nova (seção acima).
2. `elk_obter_consulta(id, espaco)` para ver o estado atual.
3. Monte **só o que muda**. Filtros: `campos`/`filtros` substituem **todos** — reenvie os que ficam: `match_phrase`
   `{campo: valor}` → `campos`; o resto → `filtros`. Barra de busca: `consulta` (`""` limpa). Demais: `titulo`,
   `colunas`, `descricao` (inclusive `Parâmetros:`), `indice`, `linguagem`.
4. **Confirme** em um bloco **antes → depois**, só com o que muda. Sem confirmação, não grave nada.
5. `elk_atualizar_consulta(id, espaco, <só os campos que mudam>, ambiente)`. O resto (ordenação, período, layout
   feitos no Kibana) é preservado.
6. Título mudou e está em `consultas` do `elk-<ambiente>.json` → renomeie a chave, mantendo `id` e `espaco`.

Responda: `Consulta atualizada no Kibana: "<titulo>" · <ambiente> · espaço <espaco>` + o que mudou.

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
