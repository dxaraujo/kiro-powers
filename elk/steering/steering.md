---
inclusion: always
---

# ELK Power

Este power dá acesso **só de leitura** aos logs do ELK (Elasticsearch + Kibana), pelo MCP `elk`
(`uvx mcp-elk@latest`). **O MCP fornece as capacidades; as skills fornecem o conhecimento.** O MCP é agnóstico:
índice, campos e consultas do projeto vêm do `elk.json`.

## Skills (escopos que não se sobrepõem)

| Pedido | Skill |
|---|---|
| Configurar o projeto: índice, campos, filtros fixos, consultas salvas, pasta de download (`elk.json`) | `elk-setup` |
| Ver ou contar logs: "logs do usuário X", "quantos erros hoje", "rode a consulta Y" (até 100 documentos na conversa) | `elk-logs` |
| Gravar logs em arquivo: CSV, planilha, "baixar/exportar todos", volume grande | `elk-exportar` |
| Entender um problema: incidente, pico, lentidão, "por que caiu", causa raiz, comparação com antes | `elk-diagnostico` |

Carregue a skill antes de chamar as tools.

## Regras comuns (valem para todas as skills)

1. **`elk.json` primeiro, servidor depois.** `.kiro/config/power/elk/elk.json` (raiz do repositório; um por
   projeto) diz o ambiente, o índice (`padrao`), o campo de tempo, os filtros fixos, os apelidos de campos e as
   consultas prontas. Sem o arquivo, ou faltando o que o pedido precisa, ofereça a `elk-setup`; não adivinhe índice
   nem campo.
2. **Índice e filtros.** `indice` = `indices[<nome>].padrao` (sem nome no pedido: `indice-padrao`);
   `campo_tempo` = `campo-tempo`. Os `fixos` vão **sempre** em `campos` (filtro exato `term`) ou `consulta` (para
   valores com wildcard `*`), somados aos do pedido: são o recorte do projeto, e sem eles a consulta pega o ELK
   inteiro. Valores com `*` (ex.: `app*`, `*batch*`) viram filtro wildcard em vez de term.
3. **Apelidos.** O usuário fala o apelido (`nivel`, `mensagem`, `servico`, `cpf`...); a chamada usa o campo real de
   `campos`. Valores possíveis estão em `valores`: use-os em vez de inventar (`ERROR`, não `erro`).
   - **3.1 Termo não reconhecido:** campo ou valor que não está em `campos` nem em `valores`: antes de usar como
     texto livre em `consulta`, tente `elk_listar_campos(indice, busca="<termo>")`. Um único resultado → use o
     campo real. Vários resultados → mostre ao usuário uma lista numerada para escolher. Nenhum resultado → use
     como texto em `consulta` e sugira a elk-setup se for recorrente.
   - **3.2 Expansão parcial:** `app.id` → busque com os segmentos (`app` e `id`). Match único → use automaticamente
     (ex.: `context.app.id`). Múltiplos matches → mostre opções.
   - **3.3 Wildcard em campos:** `app*.campo` busca campos que comecem com variantes de `app` (`app`, `app-worker`,
     `app_batch`). O MCP filtra por trecho; combine os segmentos na busca.
4. **Janela de tempo.** `inicio` é obrigatório (`now-15m`, `now-1h`, `now-1d` ou ISO 8601 com fuso, ex.:
   `2026-10-08T10:00:00-03:00`). Horário falado pelo usuário é de Brasília (`-03:00`). Comece curto e amplie; o
   volume costuma ser de milhões por hora.
5. **Consulta.** `consulta` é Lucene (`campo:valor AND campo2:*trecho*`); operadores `AND/OR/NOT` em
   maiúsculas, valores com espaço entre aspas, sem `campo:{...}`. Filtro exato → `campos`; DSL pronta (de
   `consultas`) → `filtros`.
6. **Ambiente.** `ambiente` do `elk.json`, salvo se o usuário pedir outro (prod/produção, homol/homologação/hml,
   dev/desenvolvimento). Diga sempre o ambiente e a janela usados na resposta.
7. **Dados pessoais.** Logs podem ter CPF, nome e e-mail: mostre só o que o pedido precisa.
8. **Erros do MCP** dizem o que corrigir: siga a mensagem, sem tentativas às cegas.

## Credenciais

Ficam em `~/.config/mcp-elk/elk.properties` (Windows: `%APPDATA%\mcp-elk\elk.properties`, ou `MCP_ELK_CONFIG`).
**Nunca leia nem mostre esse arquivo**: ele tem a senha. HTTP 401 → peça ao usuário que corrija `user`/`password`.
Certificado não confiável → a cadeia PEM vai em `elk-bundle.pem`, na mesma pasta; reinicie o MCP.
