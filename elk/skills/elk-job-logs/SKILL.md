---
name: "elk-job-logs"
description: "Show the execution log of a Spring Batch job as a formatted per-step summary (status, read/filtered/written rows, skips, commits, rollbacks, duration) in chronological order, consolidating the partitions of a partitioned step into a single result, plus a scan of the WARN/ERROR events in the execution window with an analysis of the errors. Reads from two sources: local log files (when the request says \"log local\" or \"execução local\") or ELK/Kibana (configured environments) otherwise. Use when the user asks \"exibe os logs do job X\", \"mostra a execução do job X\", \"como foi a execução do X\", \"log de execução do job X\". For ad-hoc logs by user/transaction/trace id, counting, or saved queries use elk-logs; to investigate an incident or root cause use elk-diagnostico; to export logs to a CSV file use elk-exportar."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
---

# Exibidor de Log de Execução — Spring Batch

Você apresenta o log de uma execução de job Spring Batch de forma legível e
sofisticada: para cada step, uma tabela com o sumário de execução, em ordem
cronológica, do início ao fim do job; e, ao final, uma varredura dos eventos
`WARN`/`ERROR` da janela da execução com uma análise dos erros encontrados.

O log cru dos listeners (um listener de job e um de step) vem como dezenas de
linhas de texto repetitivas, com as partições de steps particionados intercaladas
e embaralhadas entre threads. Seu trabalho é **recolher, consolidar e tabelar**.

> **Premissa:** o projeto usa listeners de job e de step que logam no formato
> descrito na seção 3 (as mensagens "Iniciando processamento do JOB...",
> "##### SUMÁRIO DE EXECUCAO #####" etc.). Esses listeners costumam ter "LoggerListener"
> no nome da classe. Se o projeto não logar nesse formato, esta skill não se aplica.

---

## Quando ativar esta skill

Pedidos como:

- "exibe os logs do job `<nomeDoJob>`"
- "mostra como foi a execução do `<nomeDoJob>`"
- "log de execução do `<nomeDoJob>` de hoje"
- "me mostra a última execução do job X"

---

## 1. Escolher a fonte (local vs ELK)

Decida pela presença de palavras no pedido:

| O pedido menciona... | Fonte |
|---|---|
| "log local", "execução local", "localmente", "aqui", "na minha máquina" | **Local** (arquivo de log) |
| qualquer outro caso (sem menção a local) | **ELK** (ambientes configurados) |

Se o pedido não deixar claro o ambiente do ELK (prod/homol/dev) e houver mais de
um configurado, use o padrão (prod) e diga qual usou; o usuário corrige se
precisar.

---

## 2. Buscar o log

### 2a. Fonte local (arquivo)

O log local costuma vir em um ou dois arquivos na pasta de logs do projeto
(ex.: `logs/`): um em **JSONL** (uma linha JSON por evento) e, às vezes, um em
**texto humano**.

**Sempre prefira o arquivo JSONL** — cada linha é um JSON com campos estruturados
(ex.: `message`, `logger_name`, `thread_name`, `level`, `@timestamp`), análogos aos
do ELK, o que evita parsear o prefixo de texto e dá o `thread_name` já pronto para
desembaralhar as partições (seção 4). Use o arquivo de **texto só como fallback**,
quando não houver JSONL.

Se não souber o caminho/nome dos arquivos, descubra-os (procure por arquivos `.log`
na pasta de logs; o JSONL é o cujas linhas começam com `{`). Na dúvida, pergunte ao
usuário.

As linhas relevantes vêm de dois loggers, cujas classes têm **"LoggerListener"**
no nome:

- o **listener de job** — início/fim do job ("...processamento do JOB...")
- o **listener de step** — início/fim de step e o bloco de sumário

**No JSONL**, filtre os eventos cujo `logger_name` contém `LoggerListener` e recorte
do "Iniciando processamento do JOB: `<job>`" até o "Finalizando processamento do
JOB: `<job>`" correspondente; leia o texto do campo `message` e a thread de
`thread_name`. Ferramentas como `jq` ajudam, mas `grep` na linha JSON também serve.

Formato de uma linha JSONL (campos podem variar conforme o encoder do projeto):

```
{"@timestamp":"2026-10-09T11:43:42.736-03:00","message":"Iniciando processamento do JOB: <nomeDoJob> na data 09/10/2026 11:43:42","logger_name":"...JobLoggerListener","thread_name":"main","level":"INFO"}
```

No **fallback de texto**, o prefixo de data/nível/thread/classe varia conforme o
`logback`/`log4j`; filtre por `LoggerListener` e recorte do mesmo jeito:

```
2026-10-09T11:43:42.736-03:00  INFO 9266 --- [main] <...>.JobLoggerListener   : Iniciando processamento do JOB: <nomeDoJob> na data 09/10/2026 11:43:42
```

Como o arquivo pode ter várias execuções, por padrão use a **última** (a mais
recente) do job pedido, a menos que o usuário dê uma data/horário.

> O log local costuma ser single-process; as partições aparecem na mesma thread ou
> em threads de um task executor, mas o padrão de parsing é o mesmo do ELK — use o
> `thread_name` do JSONL para separá-las.

### 2b. Fonte ELK (power `elk`)

A configuração do ELK do projeto está em
`.kiro/config/power/elk/elk-<ambiente>.json` — **esta é a fonte da verdade** do
índice, do recorte e dos nomes dos campos. **Leia esse arquivo** e use os valores
dele; não embuta nomes de índice ou de campo nesta skill.

Do `elk-<ambiente>.json`, pegue:

- **índice:** `indices[<indice-padrao>].padrao`
- **recorte fixo:** `indices[<indice-padrao>].fixos` (passe inteiro em `campos` —
  é o que isola a aplicação do projeto dentro de um índice compartilhado)
- **nomes dos campos** em `indices[<indice-padrao>].campos`:
  - mensagem → o apelido `mensagem`
  - logger/classe → o apelido `logger`
  - thread → o apelido `thread` (se houver)
  - nível → o apelido `nivel`
  - campo de tempo → `indices[<indice-padrao>].campo-tempo`

Se o arquivo não existir ou faltar algum campo, rode a skill `elk-setup` (do power
`elk`) ou pergunte ao usuário; não invente nomes de campo.

Estratégia de busca, usando `<campo-mensagem>`, `<campo-logger>`, `<campo-thread>`
e `<campo-tempo>` resolvidos acima:

**Passo 1 — achar a janela da execução.** Busque a linha de início do job
(`elk_buscar_logs`) para pegar o `<campo-tempo>`:

- `campos`: o objeto `fixos` do arquivo
- `consulta`: `<campo-logger>:*LoggerListener* AND <campo-mensagem>:*processamento*do*JOB*<nomeDoJob>*`
- `mais_recentes: true`, `limite` pequeno
- **Importante:** a busca por frase exata (`"Iniciando processamento do JOB"`)
  costuma não casar por causa da análise de texto do índice; use **wildcard por
  tokens** (`*processamento*do*JOB*`) com o nome do job.

Você verá o par início/fim mais recente. A janela é do `<campo-tempo>` do início ao
do fim; use uma folga de alguns segundos de cada lado. Se o usuário der data/hora,
use como `inicio`/`fim`.

> **Fuso horário:** no ELK o `<campo-tempo>` (ex.: `@timestamp`) costuma estar em
> **UTC**, enquanto a mensagem do listener traz o horário **local** (ex.: evento
> `10:19Z` com mensagem "...na data 09/10/2026 07:19:12"). Use o `<campo-tempo>`
> **só para recortar a janela**; na exibição ao usuário, use sempre o horário que
> vem **dentro da mensagem** do listener. Não misture os dois.

**Passo 2 — trazer os eventos dos listeners na janela.** Com o início e o fim do
job em mãos, **sempre exporte para CSV** (`elk_exportar_csv`). Não monte o resultado
a partir de `elk_buscar_logs`: o CSV vem **ordenado por tempo** e sem o teto de 100
eventos, o que é indispensável para jobs particionados (dezenas de eventos
embaralhados entre threads) e evita erro mesmo nos jobs simples.

- `indice`, `campos` = `fixos`, `inicio`/`fim` = a janela
- `consulta`: `<campo-logger>:*LoggerListener*`
- `retornar`: `[<campo-tempo>, <campo-thread>, <campo-mensagem>]` (a thread é
  **obrigatória** — é ela que desembaralha as partições; veja a seção 4)
- `arquivo`: dentro de `download.path` do `elk-<ambiente>.json`, com um nome que
  identifique job/ambiente/data (ex.: `<download.path>/<job>-<ambiente>-<data>.csv`)

Depois processe o CSV com ferramentas de texto (grep/sort/uniq), não item a item na
conversa.

> `elk_buscar_logs` fica reservado ao **passo 1** (achar início/fim do job). A
> montagem do sumário é sempre a partir do CSV.

---

## 3. Parsear as mensagens

As mensagens dos listeners seguem padrões fixos. Reconheça:

| Linha | Significado |
|---|---|
| `Iniciando processamento do JOB: <job> na data <dt>` | início do job |
| `Finalizando processamento do JOB: <job> na data <dt>, com status <STATUS>` | fim do job |
| `Iniciando step: <step> na data <dt>` | início de step |
| `Finalizando step: <step> na data <dt> com duração de <HH:MM:SS>` | fim de step |
| `##### SUMÁRIO DE EXECUCAO #####` | abre o bloco de sumário do step |
| `Situação do step:                <STATUS>` | status do step |
| `Total de linhas lidas:           <n>` | lidas |
| `Total de skips na leitura:       <n>` | skips leitura |
| `Total de linhas filtradas:       <n>` | filtradas |
| `Total de linhas gravadas:        <n>` | gravadas |
| `Total de skips na gravação:      <n>` | skips gravação |
| `Total de skips no processamento: <n>` | skips processamento |
| `Total de commits:                <n>` | commits |
| `Total de rollback:               <n>` | rollback |

Também pode haver mensagens livres de steps específicos (ex.: um id encontrado, um
"OK" de carga de cache). Essas podem ser mostradas como uma nota abaixo da tabela
do step, se agregarem valor; na dúvida, omita.

**Atenção ao embaralhamento:** em steps particionados, várias threads logam o
sumário ao mesmo tempo, então no log cru as linhas de um `##### SUMÁRIO #####`
podem vir intercaladas com as de outro. Agrupe por bloco: cada `##### SUMÁRIO DE
EXECUCAO #####` abre um bloco que vai até o próximo `Finalizando step`. Quando as
linhas vierem fora de ordem, associe cada campo ao sumário mais próximo pela thread
e pela sequência; se não der para desembaralhar com confiança, diga isso em vez de
inventar números.

---

## 4. Consolidar partições

Steps particionados aparecem com um sufixo de partição no nome
(ex.: `<step>:partition0` .. `<step>:partitionN`), além do step manager
(normalmente o `<step>` sem sufixo).

Regras:

- **Não** liste cada partição. Elas são ruído.
- **Desembaralhe por thread.** Cada partição roda em uma thread própria (ex.:
  `AsyncTaskExecutor-1` .. `-N`), então o bloco de sumário de uma partição sai
  **limpo quando você filtra pela thread dela** — mesmo que no tempo global os
  sumários de várias partições venham intercalados. Agrupe as linhas por
  `<campo-thread>`; cada thread de worker dá o sumário de uma partição. (Os steps
  não particionados ficam na thread principal, ex.: `main`.)
- Mostre **um resultado consolidado por step particionado**: some os contadores
  (linhas lidas, gravadas, filtradas, skips, commits, rollback) de todas as
  partições; a situação é `COMPLETED` se todas completaram, senão destaque o pior
  status; a duração é a do **step manager** (o step sem sufixo de partição) — do
  "Iniciando step: `<step>`" ao "Finalizando step: `<step>`".
- **Conferência cruzada.** O step manager normalmente também emite um sumário
  próprio com os totais agregados. Compare a **soma das partições** com esse
  agregado: se baterem, use os números com confiança; se divergirem, mostre o
  agregado do manager e **sinalize a divergência** em vez de escolher um número em
  silêncio.

Steps não particionados aparecem uma única vez: tabela direta.

> **Desembaralhar os steps da thread principal:** os steps não particionados (ex.:
> os de preparação) costumam logar todos na mesma thread (`main`) e, no ELK, podem
> cair no mesmo milissegundo, embaralhados entre si. Quando não der para separar os
> blocos com confiança, use os valores **distintos** de cada contador (ex.: os
> valores únicos de "linhas lidas" casam com os steps pela ordem de início) e, se
> ainda houver ambiguidade, diga qual número não foi possível atribuir com certeza —
> nunca invente a associação.

---

## 5. Formatar a saída

Objetivo: exibição sofisticada, uma **tabela por step**, em ordem cronológica.

Estrutura sugerida:

```
# Execução — <job>  (<ambiente: local | prod | ...>)

Início:  09/10/2026 11:43:42
Fim:     09/10/2026 11:44:32
Status:  ✅ COMPLETED
Duração: 00:00:50

## Steps
```

Para **cada step** (na ordem em que iniciaram), uma tabela compacta de duas
colunas (título / valor):

| <nomeDoStep> | |
|---|---|
| Situação | COMPLETED |
| Linhas lidas | 0 |
| Linhas filtradas | 0 |
| Linhas gravadas | 0 |
| Skips (leitura / processamento / gravação) | 0 / 0 / 0 |
| Commits | 10 |
| Rollback | 0 |
| Duração | 00:00:01 |

Quando o step for particionado, acrescente uma linha discreta indicando a
consolidação, ex.: `| Partições | 10 (consolidadas) |`.

Diretrizes de formatação:

- Início/Fim/Duração do **job** vêm das linhas do `JobLoggerListener` (horário
  dentro da mensagem; e, quando houver, a linha "JOB: `<job>` executado com duração:
  `<HH:MM:SS>`"). **Não** calcule a duração pelo `<campo-tempo>` de indexação do ELK
  (UTC, e pode ter atraso de ingestão).
- Status do job: ✅ para `COMPLETED`, ❌ para `FAILED`, ⚠️ para outros.
- Omita colunas que são zero em todos os steps **só** se o usuário pedir algo mais
  enxuto; por padrão, mantenha as linhas para leitura comparável.
- Agrupe skips numa linha (`leitura / processamento / gravação`) para a tabela
  ficar menor, como no exemplo.
- Se um step falhou, destaque a situação e inclua a mensagem de erro/exit
  description logo abaixo da tabela dele.
- No fim, um resumo de uma linha: nº de steps, totais de lidas/gravadas, e se houve
  rollback ou skip em algum step (sinalize).

Não despeje o log cru. O usuário quer o consolidado tabelado; o texto bruto só se
ele pedir explicitamente ("mostra o log cru").

---

## 6. Varredura de WARN e ERROR na janela da execução

Depois do sumário por step, **sempre** procure os eventos de nível `WARN` e `ERROR`
dentro da **mesma janela** da execução (do início ao fim do job) e entregue uma
análise. Esses eventos vêm de **qualquer logger** (não só dos listeners), então
aqui **não** filtre por `*LoggerListener*`.

### Como buscar

**Fonte ELK:** exporte para CSV (`elk_exportar_csv`), mesma janela do sumário:

- `indice`, `campos` = `fixos`, `inicio`/`fim` = a janela da execução
- `consulta`: `<campo-nivel>:(WARN OR ERROR)` (use o apelido `nivel` e os valores de
  `valores.nivel` do `elk-<ambiente>.json`; se o nível não for agregável como texto,
  tente a variante `.keyword`)
- `retornar`: `[<campo-tempo>, <campo-nivel>, <campo-logger>, <campo-mensagem>]` e,
  se existirem no arquivo, os apelidos `excecao` e `stacktrace`
- `arquivo`: `<download.path>/<job>-<ambiente>-<data>-warn-error.csv`

Para dimensionar antes de trazer tudo, `elk_contar` com `agrupar_por` =
`<campo-logger>` (ou `excecao`) na janela dá a contagem por origem.

**Fonte local:** no arquivo **JSONL** (preferido), recorte a mesma faixa de eventos
da execução (entre o "Iniciando processamento do JOB" e o "Finalizando...") e filtre
pelo campo `level` igual a `WARN` ou `ERROR`, de **qualquer** `logger_name`. Só caia
para o arquivo de texto se não houver JSONL (coluna de nível do `logback`/`log4j`).

### Como analisar

Não despeje as linhas cruas. Entregue:

1. **Contagem** por nível (quantos WARN, quantos ERROR) e por origem (logger ou
   tipo de exceção).
2. **Agrupamento** de mensagens semelhantes: junte ocorrências repetidas numa só
   entrada com a contagem (ex.: "`SQLTimeoutException` em `XRepository` — 14×"),
   em vez de listar 14 linhas quase iguais.
3. Para cada grupo relevante: nível, origem (logger/classe), 1ª e última
   ocorrência (horário da mensagem), a mensagem representativa e, se houver, o tipo
   da exceção. Mostre a stacktrace só do primeiro caso de cada grupo, e só se o
   usuário quiser detalhe.
4. **Correlação com os steps:** quando der para situar o horário do erro dentro de
   um step (pela janela de início/fim do step), diga em qual step ocorreu.
5. **Leitura:** diga se os WARN/ERROR afetaram o resultado (ex.: viraram skip ou
   rollback no sumário? o job terminou `FAILED`?) ou se são ruído conhecido/
   inofensivo. Seja explícito sobre o que é suspeita e o que é fato.

Se **não** houver WARN nem ERROR na janela, diga isso em uma linha ("Sem WARN/ERROR
na janela da execução.") — é um resultado positivo e vale registrar.

### Formato sugerido

```
## WARN / ERROR na janela

Total: <n> ERROR · <m> WARN

| Nível | Origem | Ocorrências | 1ª | Última | Mensagem (resumo) | Step |
|---|---|---|---|---|---|---|
| ERROR | <logger/exceção> | 14× | 07:19:40 | 07:20:05 | <resumo> | <step> |
| WARN  | <logger> | 3× | ... | ... | <resumo> | <step> |

Análise: <leitura em 2-4 frases: o que são, se afetaram o resultado, o que investigar>
```

---

## Erros comuns

| Erro | Certo |
|---|---|
| Listar cada partição | Consolidar num único resultado por step particionado |
| Montar o sumário a partir do `elk_buscar_logs` | Achar início/fim com `elk_buscar_logs` e **sempre exportar CSV** para montar |
| Buscar no ELK com frase exata entre aspas | Wildcard por tokens (`*processamento*do*JOB*<job>*`) |
| Usar o `@timestamp` (UTC) do ELK na exibição | Exibir o horário que vem **na mensagem** do listener; `@timestamp` só recorta a janela |
| Embutir nome de índice/campo na skill | Ler do `elk-<ambiente>.json`; sem ele, rodar `elk-setup` |
| Esquecer o recorte `fixos` no ELK | Sempre passar o objeto `fixos` em `campos` |
| Filtrar WARN/ERROR por `*LoggerListener*` | Na varredura de erros, buscar **todos** os loggers no nível WARN/ERROR |
| Misturar execuções diferentes do mesmo job | Recortar da linha de início até o fim correspondente; sem data, usar a mais recente |
| Inventar números quando o log vem embaralhado | Desembaralhar por thread/bloco; se não der, dizer que não foi possível |
| Pular a análise de erros quando o job foi COMPLETED | Varrer WARN/ERROR sempre; "sem erros" também é resultado |
| Despejar o log cru | Tabela consolidada por step + análise de erros |
