---
name: "alm-rm"
description: "Query, search, read, create or update IBM DOORS Next (RM) artifacts through the `alm` MCP, including attributes, links between requirements and artifacts embedded in the text. Use when the user asks about um requisito (REQ, RF, RNF), história de usuário (HU, HF, HNF), caso de uso (UC, CDU, use case), regra de negócio (RN, REG, BR), mensagem (MSG), especificação técnica (ET), especificação de leiaute (EL), protótipo (PRT, mockup), diagrama (DG), termo de glossário (GL), imagem (IMG) ou documento de visão (DV); pastas, tipos de artefato, componentes, streams e baselines do RM; \"me mostre o requisito 123456\", \"me mostre o uc 123456\", \"baixar hu 123\", \"requisitos da pasta 01-Requisitos\", \"crie uma HU\", \"liga o UC à regra\", \"embute a regra no passo 2\", \"cita a mensagem no fluxo\", \"referencia a ET no texto\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.1"
---

# alm-rm

Requisitos do DOORS Next pelo MCP `alm`, com as tools `rm_*`: recebem os ids do `.kiro/config/alm-power/pa_*.json` e trabalham com
**nomes** de atributo, valor e link. As tools genéricas do IBM AI Hub (baselines, change sets, configuração global,
outra project area) estão em [reference.md](reference.md): leia-o **só** quando precisar delas. Links com work
items e testes → **alm-gc**.

## Antes de chamar

1. **Leia `.kiro/config/alm-power/pa_*.json`** (um → use; vários → pergunte). A seção `rm` dá os três parâmetros fixos de **todas**
   as `rm_*`: `project_area_identifier` = `rm.project-area-identifier`, `component` = `rm.component`,
   `configuration` = `rm.configuration` (a stream). Também: `rm.folders` (`{caminho: FR_...}`),
   `rm.requirements-types` (`{nome: OT_...}`), `rm.members`.
2. Sem arquivo ou sem seção `rm` → ofereça a **alm-setup**. Pasta/tipo fora do arquivo → não invente: alm-setup.
3. Mostre nomes de tipo e pasta, nunca `FR_`/`OT_`/URLs (exceção: o código do requisito).

## Siglas e sinônimos

O termo do usuário indica o **tipo** do artefato; o número é o id global ("baixar hu 123" = requisito 123). O tipo
escolhe o `requirement_type` (e, em geral, a pasta) ao criar ou filtrar.

| Sigla | Termos do usuário | Tipo (`rm.requirements-types`) |
|---|---|---|
| **REQ** | requisito, req, requirement, RF, requisito funcional, RNF, requisito não funcional | Requisito |
| **HU** | história de usuário, história, user story, HF (funcional), HNF (não funcional) | História de Usuário |
| **UC** | caso de uso, use case, CDU | Caso de Uso |
| **RN** | regra, regra de negócio, REG, business rule, BR | Regra |
| **MSG** | mensagem, mensagem de sistema, mensagem de erro | Mensagem |
| **ET** | especificação técnica, spec técnica, ESP | Especificação Técnica |
| **EL** | especificação de leiaute, leiaute, layout | Especificação de Leiaute |
| **PRT** | protótipo, mockup, wireframe | Protótipo |
| **DG** | diagrama, fluxograma | Diagrama |
| **GL** | glossário, termo de glossário, termo | Termos de Glossário |
| **IMG** | imagem, figura, print | Imagem |
| **DV** | documento de visão, visão | Documento de Visão |
| — | artefato, artefato do RM | qualquer tipo |

Reconheça o termo sem diferenciar maiúsculas, acentos, singular/plural ou separador: "ib 123", "IB123",
"ib:123", "ib-123", "item de backlog 123", "os IBs da sprint". Responda sempre com a **sigla canônica** (1ª
coluna). Termo que não está aqui nem em `rm.requirements-types` → pergunte o tipo; não adivinhe.

- O nome real do tipo é a chave em `rm.requirements-types`; se o projeto usar outro nome (ex.: "Regra de Negócio"),
  case pela coluna "Tipo" sem diferenciar maiúsculas/acentos.
- **PT** é Plano de Teste (alm-qm), não Protótipo (**PRT**). **"Story"/"item de backlog"/"IB"** é work item
  (alm-ccm), não HU.

## Como responder

- **Listas** (mesmo com um resultado): tabela markdown que começa por **Código | Título** (`id` | `title`); pode
  acrescentar tipo e pasta. Sem resultado: "Nenhum item encontrado" + filtros. Vieram **1000** → avise que pode
  estar truncada e sugira filtrar por pasta/tipo.
- **Um requisito:** comece por `**<código>** — <título>` e mostre o documento de `rm_get_requirement` como veio.

## Tools

Todas com `project_area_identifier`, `component`, `configuration` do alm.json (omitidos abaixo).

| Tool | Entrada extra | Saída |
|---|---|---|
| `rm_search_requirements(text? \| folder?, requirement_type?)` | `text` **sozinho**, ou `folder` (`FR_`) e/ou `requirement_type` (`OT_`) | `[{id, title, type, folder, url}]` (≤1000) |
| `rm_get_requirement(requirement_id)` | id numérico (string) | Markdown + YAML (abaixo) |
| `rm_create_requirement(requirement_type, folder, title, text, attributes?)` | `OT_`, `FR_`; `text` em Markdown | `{id, title, url}` |
| `rm_update_requirement(requirement_id, title?, text?, attributes?)` | ≥1 dos três; `text` e cada atributo **substituem** o atual | `{id, title, url}` |

**Busca:** `text` + `folder`/`requirement_type` juntos dão **HTTP 400** no DOORS Next. Com texto, busque só pelo
texto e filtre o resultado pelas colunas `type`/`folder`. Prefira pasta/tipo quando o pedido permitir: a busca por
texto varre o componente inteiro e é mais lenta.

### Leitura (`rm_get_requirement`)

```markdown
---
id: 2010
type: Caso de Uso
title: UC - Cadastrar cliente
folder: "03-Casos de Uso"
url: "https://alm.example.com/rm/resources/TX_exemplo2010"
attributes:
  Prioridade: Alta
links:
  Vincular A:
    - "2002: RN - Cliente deve ser maior de idade"
  Implementado por:
    - "1001: Implementar cadastro de clientes"
embedded:
  - "2001: RN - Validar CPF do cliente"
---
## Fluxo Básico

1. O usuário informa os dados do cliente.
2. O sistema valida o documento: ![[2001: RN - Validar CPF do cliente]]
```

- Nomes de atributos e links são os do **DOORS Next** (o alm.json não mapeia o RM). Pessoas vêm pelo login; campos
  vazios são omitidos; datas em Brasília.
- `![[id: título]]` = artefato **embutido** naquele ponto do texto; `embedded` lista todos.
- Lê só a stream do alm.json e só os links do próprio artefato: **links de módulo e links que chegam de outros
  artefatos não aparecem**. Não afirme "não há link"; diga que não há link no artefato e sugira conferir na UI.

### Gravação

- `attributes` usa os **nomes do cabeçalho** como chave: enumeração pelo nome do valor (`"Alta"`), pessoa pelo
  login, link pelo id (`"2001"` ou `"2001: título"`) ou URL, lista = vários valores. O MCP valida e, em erro, lista
  os nomes/valores válidos: não consulte o schema antes.
- **Gravar um link substitui todos os links daquele tipo.** Leia antes e mande a lista completa (atuais + novo).
  Para remover um link, mande a lista sem ele.
- **`text` substitui o texto inteiro.** Leia, edite o corpo (sem o cabeçalho YAML), mantenha todos os `![[...]]`
  existentes e mande tudo. Ler → gravar → ler não muda o texto; só estilos visuais do Word (fonte, cor) se perdem.
- `text` em Markdown: títulos, listas, negrito e as referências da seção abaixo.

### Referências a outros artefatos do RM

Há três formas de relacionar um artefato a outro. Escolha pelo que o usuário quer ver:

| Forma | Escrita | Onde fica | Quando usar |
|---|---|---|---|
| **Embed** | `![[2003]]` no `text` | dentro do texto: o DOORS Next mostra o conteúdo do 2003 naquele ponto | "embute", "inclui a regra no passo", "mostra a mensagem no fluxo" |
| **Hyperlink no texto** | `[RN 2003](<url do 2003>)` no `text` | dentro do texto, como link clicável | "cita", "referencia", "aponta para" |
| **Link de rastreabilidade** | `attributes={"Vincular A": [...]}` | fora do texto (aba Links), em `links` do cabeçalho | "liga", "vincula", "relaciona", "rastreia" |

- **Embed:** o id basta (`![[2003]]`); o título é opcional e só ajuda a ler (`![[2003: RN - Validar CPF]]`). O
  DOORS Next mostra o artefato embutido; na leitura ele volta como `![[id: título]]` e aparece em `embedded`.
- **Hyperlink:** precisa da **URL** do artefato (`url` de `rm_search_requirements` ou do cabeçalho de
  `rm_get_requirement`), nunca só o id. É um link comum de texto: **não** cria link de rastreabilidade nem aparece
  em `links`.
- Embed e hyperlink vivem no `text`: gravar é mandar o corpo inteiro. Link de rastreabilidade vive em `attributes`:
  mandar a lista completa daquele tipo.
- Sem pedido explícito de rastreabilidade, não crie link em `attributes` além do embed/hyperlink pedido.

**Exemplo — "no UC 2010, embute a RN 2003 no passo 3 e cita a MSG 2005 no passo 4":**

1. `rm_get_requirement("2010")` → corpo atual:

   ```markdown
   ## Fluxo Básico

   1. O usuário informa os dados do cliente.
   2. O sistema valida o documento: ![[2001: RN - Validar CPF do cliente]]
   3. O sistema verifica a idade do cliente.
   4. O sistema grava o cliente.
   ```

2. URL da MSG 2005: `rm_get_requirement("2005")` (ou `url` de uma busca já feita na conversa).
3. Novo corpo: mantém o embed 2001, acrescenta o embed 2003 e o hyperlink para a 2005:

   ```markdown
   ## Fluxo Básico

   1. O usuário informa os dados do cliente.
   2. O sistema valida o documento: ![[2001: RN - Validar CPF do cliente]]
   3. O sistema verifica a idade do cliente: ![[2003]]
   4. O sistema grava o cliente e exibe a [MSG 2005](https://alm.example.com/rm/resources/TX_exemplo2005).
   ```

4. Mostre o trecho alterado, confirme e chame `rm_update_requirement("2010", text=<corpo inteiro>)`.
5. Confira lendo de novo: `embedded` deve listar 2001 e 2003.

**Exemplo — criar uma HU já com referências:**

```text
rm_create_requirement(..., requirement_type=rm.requirements-types["História de Usuário"],
    folder=rm.folders["02-Histórias"], title="HU - Exportar relatório em PDF",
    text="Como gestor, quero exportar o relatório em PDF.\n\n"
         "**Regras**\n\n- ![[2001]]\n- Formato do arquivo: ver [ET 2007](<url do 2007>)",
    attributes={"Vincular A": ["2010"]})
```

Aqui o 2001 fica embutido, a ET 2007 é citada por hyperlink e o UC 2010 recebe um link de rastreabilidade.

## Fluxos

- **Buscar:** por pasta/tipo do alm.json; ou só por texto e filtrar localmente.
- **Ler:** `rm_get_requirement(id)`. Baseline ou outra configuração → `get_requirement` com `configuration_url`
  ([reference.md](reference.md)).
- **Ligar requisitos** — "liga o UC 2010 à regra 2003 por Vincular A": leia o 2010 → `links["Vincular A"]` =
  `["2002: ..."]` → confirme → `rm_update_requirement("2010", attributes={"Vincular A": ["2002", "2003"]})`.
- **Embutir ou citar no texto:** ver "Referências a outros artefatos do RM".
- **Criar:**
  1. Tipo e pasta pelo alm.json (pergunte se o pedido não disser; sugira pela sigla).
  2. Monte título, `text` em Markdown e `attributes` pelos nomes do DOORS Next. Nomes de atributo do tipo ainda
     desconhecidos → leia um requisito do mesmo tipo (`rm_search_requirements(requirement_type=...)` + um
     `rm_get_requirement`) em vez de adivinhar.
  3. Mostre o resumo e peça confirmação. `rm_create_requirement(...)`; responda com código, título e url.
  4. Com `attributes` a tool faz POST e depois PUT: se der erro, o requisito **pode já existir sem os atributos**.
     Busque pelo título (`rm_search_requirements(text=<título>)`) e, achando, complete com `rm_update_requirement`
     em vez de criar de novo.
- **Ligar a work item / teste:** alm-gc, com o `url` do cabeçalho ou da busca.

## Erros

| Mensagem (trecho) | O que fazer |
|---|---|
| `Atributo 'x' não existe no tipo. Válidos: ...` | Mostre os válidos pelo nome e pergunte |
| `Valor 'x' inválido para 'y'. Válidos: ...` | Idem |
| HTTP 400 na busca | Não combine `text` com `folder`/`requirement_type` |
| `Informe ao menos um filtro` | Peça pasta, tipo ou texto |
| `requirement_id deve ser numérico` | Busque por texto para achar o id |
| `Requisito N não encontrado` | Pode estar em outro componente/stream: diga isso; não varra outras áreas |
| HTTP 403 | Sem permissão: informe e pare |
| HTTP 412 | Edição concorrente: releia e repita **uma** vez |

## Regras

- **Confirme toda escrita** com um resumo por nomes (inclusive a lista final de links). Uma escrita por vez.
- Nunca invente ids, nomes de atributo ou valores.
- Não crie requisitos para "testar" algo: use leitura.
