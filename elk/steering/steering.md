---
inclusion: always
---

# ELK Power

Este power dá acesso **de leitura** aos logs do ELK (Elasticsearch + Kibana), pelo MCP `elk`
(`uvx mcp-elk@latest`). As únicas escritas são criar e atualizar busca salva no Kibana (`elk_criar_consulta`,
`elk_atualizar_consulta`), só pela `elk-logs` e com confirmação do usuário. **O MCP fornece as capacidades; as skills fornecem o conhecimento.** O
MCP é agnóstico: índice, campos e consultas do projeto vêm do `elk-<ambiente>.json`.

## Skills (escopos que não se sobrepõem)

| Pedido | Skill |
|---|---|
| Configurar o projeto: índice, campos, filtros fixos, consultas salvas, pasta de download (`elk-<ambiente>.json`) | `elk-setup` |
| Ver ou contar logs: "logs do usuário X", "quantos erros hoje", "rode a consulta Y" (até 100 documentos na conversa); salvar no Kibana a consulta montada na conversa ("salva essa consulta") ou alterar uma consulta salva | `elk-logs` |
| Gravar logs em arquivo: CSV, planilha, "baixar/exportar todos", volume grande | `elk-exportar` |
| Entender um problema: incidente, pico, lentidão, "por que caiu", causa raiz, comparação com antes | `elk-diagnostico` |

Carregue a skill antes de chamar as tools.

## Regras comuns (valem para todas as skills)

1. **Config primeiro, servidor depois.** `.kiro/config/power/elk/elk-<ambiente>.json` (raiz do repositório; um
   por ambiente: `elk-prod.json`, `elk-homol.json`, `elk-dev.json`) diz o índice (`padrao`), o campo de tempo, os
   filtros fixos, os apelidos de campos, as consultas prontas e a pasta de download. Sem o arquivo do ambiente, ou
   faltando o que o pedido precisa, ofereça a `elk-setup`; não adivinhe índice nem campo.
2. **Índice e filtros.** `indice` = `indices[<nome>].padrao` (sem nome no pedido: `indice-padrao`);
   `campo_tempo` = `campo-tempo`. Os `fixos` vão **sempre** em `campos`, somados aos do pedido: são o recorte do
   projeto, e sem eles a consulta pega o ELK inteiro. Valor com `*` vira filtro wildcard em vez de term (ex.:
   `sistema.nome: "myapp*"` pega `myapp`, `myapp-worker`, `myapp_batch`).
3. **Apelidos.** O usuário fala o apelido (`nivel`, `mensagem`, `servico`, `cpf`...); a chamada usa o campo real de
   `campos`. Valores possíveis estão em `valores`: use-os em vez de inventar (`ERROR`, não `erro`).
   - **3.1 Campo fora dos apelidos.** O usuário cita um campo pelo nome curto ou parcial (ex.: `pedido`) que não
     está em `campos`:
     1. `elk_listar_campos(indice, busca="<termo>")` — acha todo campo com o termo no nome (`pedido` →
        `app.venda.pedido`, `ctx.pedido_id`, `pedidos.total`).
     2. Prefira os que têm o termo como **último segmento** (`pedido` ou `*.pedido`); se não houver, considere todos.
     3. Um candidato → use e diga qual campo usou. Vários → lista numerada para o usuário escolher (para filtro exato
        ou `agrupar_por`, só os `agregavel`). Nenhum → use o termo como texto livre em `consulta`.
     4. Campo resolvido assim e usado de novo → sugira gravá-lo como apelido na elk-setup.
4. **Janela de tempo.** `inicio` é obrigatório (`now-15m`, `now-1h`, `now-1d` ou ISO 8601 com fuso, ex.:
   `2026-10-08T10:00:00-03:00`). Horário falado pelo usuário é de Brasília (`-03:00`). Comece curto e amplie; o
   volume costuma ser de milhões por hora.
5. **Consulta.** `consulta` aceita Lucene (`campo:valor AND campo2:*trecho* AND n:[1 TO 5]`) ou KQL simples
   (`campo: "valor" and n > 0`): o MCP converte `and/or/not` e `campo > 0` para Lucene. Valores com espaço entre
   aspas; sem `campo:{...}` (KQL aninhado não é suportado). Filtro exato → `campos`.
   **Consulta salva** citada pelo título → `consultas[<título>]` dá `id` e `espaco`; `elk_obter_consulta(id,
   espaco)` devolve `consulta`, `filtros`, `indice` e `descricao`, que vão nas tools somados aos `fixos`. Se esse
   `indice` não estiver em `indices`, use-o sem fixos e avise o usuário; se vier `null` (saved query), use o
   `indice-padrao` com os fixos dele. Consulta salva em KQL com `campo:{...}` dá HTTP 400 → diga ao usuário e
   reescreva em Lucene.
   **Parâmetros:** `descricao` com `Parâmetros: <campo>[, <campo>...]` → cada campo é obrigatório: use o valor do
   pedido ("rode a consulta X para 123") ou pergunte. **Tire** de `filtros` o filtro desse campo (valor de exemplo,
   ex.: `0`) e ponha o valor pedido em `campos` (`{<campo>: <valor>}`); somar os dois zera o resultado. Sem o valor,
   não rode.
6. **Ambiente.** Do pedido (prod/produção, homol/homologação/hml, dev/desenvolvimento); sem menção, `prod`. Ele
   escolhe o arquivo de config e vai no parâmetro `ambiente` das tools. Diga sempre o ambiente e a janela usados na
   resposta.
7. **Dados pessoais.** Logs podem ter CPF, nome e e-mail: mostre só o que o pedido precisa.
8. **Erros do MCP** dizem o que corrigir: siga a mensagem, sem tentativas às cegas.

## Credenciais

Ficam em `~/.config/mcp-elk/elk.properties` (Windows: `%APPDATA%\mcp-elk\elk.properties`, ou `MCP_ELK_CONFIG`).
**Nunca leia nem mostre esse arquivo**: ele tem a senha. HTTP 401 → peça ao usuário que corrija `user`/`password`.
Certificado não confiável → a cadeia PEM vai em `elk-bundle.pem`, na mesma pasta; reinicie o MCP.
