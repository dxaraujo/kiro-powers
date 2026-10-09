---
name: "elk-exportar"
description: "Export ELK/Kibana logs to a CSV file on disk through the `elk_exportar_csv` tool of the `elk` MCP, which pages through the results and writes the file itself without passing documents through the conversation. Use when the user wants logs as a file or in volume: \"exporta os logs de ontem para CSV\", \"baixar todos os erros da semana\", \"gera uma planilha com os acessos do CPF X\", \"preciso dos logs em arquivo para mandar ao fornecedor\", \"salva o resultado da consulta Y\", or when a search returned more than 100 documents and the user wants all of them. Does not analyze the content (elk-logs / elk-diagnostico do that)."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.1.0"
---

# elk-exportar

Volume grande vai **direto do MCP para o disco**: `elk_exportar_csv` pagina a consulta e grava o CSV na pasta
`download.path` do `elk-<ambiente>.json`. Os documentos nunca passam pela conversa — não use `elk_buscar_logs` para
montar arquivo, nem escreva o CSV você mesmo. As regras comuns (config por ambiente, fixos, apelidos, janela,
Lucene, consulta salva, ambiente) estão no steering do power.

## Antes de chamar

1. Identifique o ambiente (regra 6 do steering) e leia `.kiro/config/power/elk/elk-<ambiente>.json`. Sem ele, ou
   sem `download.path` → ofereça a **elk-setup** (etapa da pasta de download) e pare. Cada ambiente tem o seu
   `download.path` (podem apontar para a mesma pasta).
2. Monte a consulta como a elk-logs: `indice`, `campo_tempo`, `campos` = `fixos` + filtros do pedido, `consulta`
   Lucene para texto livre, consulta salva pela regra 5 do steering. Campo não reconhecido: regra 3.1 do
   steering. `inicio` é obrigatório: sem período no pedido, pergunte — exportar "tudo" sem janela varre meses.
3. **Arquivo** (`arquivo` precisa ser absoluto): raiz do repositório (`git rev-parse --show-toplevel`; sem git, a
   pasta do workspace) + `download.path` + `<AAAAMMDD-HHmm>_<assunto>.csv`, com `assunto` curto em kebab-case
   (`erros-servico-x`, `cpf-final-1234`). Arquivo existente é sobrescrito: com o mesmo nome, pergunte antes.
4. **Colunas** (`retornar`): o campo de tempo + os campos de `campos` úteis ao pedido. Sem `retornar` as colunas
   saem dos documentos da primeira página (dezenas, muitas vazias). Se o usuário quer "tudo", omita.

## Fluxo

1. `elk_contar(<mesma consulta>)` para dimensionar.
   - 0 → diga os filtros/janela e não exporte.
   - Acima de `max_linhas` (padrão 100.000) → mostre o total e pergunte: reduzir a janela, filtrar mais, ou subir
     `max_linhas` (arquivo maior e exportação mais lenta). Não decida sozinho.
2. Confirme em uma linha: total, ambiente, janela, colunas e caminho relativo do arquivo.
3. `elk_exportar_csv(indice, inicio, arquivo, fim, consulta?, campos, filtros?, retornar?, max_linhas,
   campo_tempo, ambiente)`.

## Como responder

```
CSV gravado: downloads/elk/20261008-1030_erros-servico-x.csv
<linhas> linhas de <total> · <ambiente> · <inicio> → <fim>
Colunas: @timestamp, <campo.nivel>, <campo.mensagem>, ...
```

- Caminho sempre relativo à raiz do repositório, com `/`.
- `truncado: true` → diga que o arquivo parou em `max_linhas` e quantas ficaram de fora.
- O CSV é UTF-8 com BOM, ordenado do mais antigo ao mais novo (abre direto no Excel).
- Se `download.path` não estiver no `.gitignore`, sugira incluir: logs têm dados pessoais.
- Não leia o CSV de volta para a conversa. Se o usuário quiser analisar, ofereça a elk-diagnostico ou uma consulta
  agregada pela elk-logs.

## Erros

| Mensagem | O que fazer |
|---|---|
| `` `arquivo` deve ser um caminho absoluto `` | Monte com a raiz do repositório (passo 3) |
| `Documentos demais com o mesmo @timestamp` | Sem ES direto o MCP não pagina esse caso: reduza a janela ou peça ao usuário `es_<ambiente>` no `elk.properties` |
| `Exportação interrompida após N linha(s)` | O arquivo ficou parcial com N linhas: informe, reduza a janela e exporte o restante em outro arquivo |
| `Consulta vazia`, `Ambiente desconhecido`, HTTP 400/401 | Mesmo tratamento da elk-logs |
