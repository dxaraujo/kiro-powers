---
name: "alm-rm"
description: "Query, search, read, create or update IBM DOORS Next (RM) artifacts through the `alm` MCP, including artifacts embedded or linked in the text (traceability links are read-only). Use when the user asks about um requisito (REQ, RF, RNF), história de usuário (HU, HF, HNF), caso de uso (UC, CDU, use case), regra de negócio (RN, REG, BR), mensagem (MSG), especificação técnica (ET), especificação de leiaute (EL), protótipo (PRT, mockup), diagrama (DG), termo de glossário (GL), imagem (IMG) ou documento de visão (DV); pastas, tipos de artefato, componentes, streams e baselines do RM; \"me mostre o requisito 123456\", \"me mostre o uc 123456\", \"baixar hu 123\", \"requisitos da pasta 01-Requisitos\", \"crie uma HU\", \"embute a regra no passo 2\", \"cita a mensagem no fluxo\", \"referencia a ET no texto\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "2.0.1"
---

# alm-rm

Requisitos do DOORS Next pelo MCP `alm`, com as tools `rm_*`: recebem os ids do `.kiro/config/power/alm/pa_*.json` e trabalham com
**nomes** de pasta, tipo e link. As tools genéricas do IBM AI Hub (baselines, change sets, configuração global,
outra project area) estão em [reference.md](reference.md): leia-o **só** quando precisar delas. Links com work
items e testes → **alm-gc**. Baixar a documentação para o repositório, conferir o que mudou e atualizar o que foi
baixado → **alm-sync**.

## Antes de chamar

1. **Leia `.kiro/config/power/alm/pa_*.json`** (um → use; vários → pergunte). A seção `rm` dá os três parâmetros fixos de **todas**
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
| `rm_search_requirements(text? \| folder?, requirement_type?)` | `text` **sozinho**, ou `folder` (`FR_`) e/ou `requirement_type` (`OT_`) | `[{id, title, type, folder, modified, path, url}]` (≤1000); `path` = arquivo do artefato no bundle da alm-sync |
| `rm_count_folder(folder)` | `FR_` | `{folder, count}` (só a pasta, sem subpastas, sem teto) |
| `rm_list_folder(folder)` | `FR_` | `[{id, title, modified}]` (só a pasta, sem subpastas, sem teto) |
| `rm_sync_plan(folders, dest)` | só para a alm-sync; `dest` absoluto | regrava `sync.md`, apaga removidos; resumo por pasta (novo, sincronizado, desatualizado, atualizado, normalizado, conflito, erro) + `a_baixar`, `a_subir`, `conflitos` |
| `rm_download_requirements(dest, requirement_ids?, limit?)` | só para a alm-sync; sem ids = próximos novo/desatualizado/erro do `sync.md` | grava arquivos, `sync.md` e `index.md`; `{baixados, erros, restantes}` |
| `rm_upload_requirements(dest, requirement_ids?, limit?)` | só para a alm-sync; sem ids = próximos `atualizado`/`normalizado` (só se o ALM não mudou) | sobe título e corpo do md e baixa de novo; `{enviados, erros, conflitos, restantes}` |
| `rm_list_modified(requirement_ids)` | lista de ids numéricos (string); um id = consulta individual, vários = lote | `[{id, title, modified}]`; id inexistente não volta |
| `rm_get_requirement(requirement_id, links?)` | id numérico (string); `links="bundle"` só para a alm-sync | Markdown + YAML (abaixo) |
| `rm_create_requirement(requirement_type, folder, title, text, embedded?)` | `OT_`, `FR_`; `text` em Markdown; `embedded` = ids a embutir | `{id, title, url}` |
| `rm_update_requirement(requirement_id, title?, text?, embedded?)` | ≥1 de title/text; `text` **substitui** o atual; com `text`, mande o `embedded` do cabeçalho | `{id, title, url}` |

`modified` (busca e `rm_list_modified`) é a última modificação no DOORS Next em ISO 8601 UTC (`...Z`), o mesmo
formato de `sources[0].last_modified` e `generated.at` da leitura: compare como texto. `rm_list_modified` não lê
o conteúdo: use-a para "o 2010 mudou?" ou para conferir muitos ids de uma vez.

**Busca:** `text` + `folder`/`requirement_type` juntos dão **HTTP 400** no DOORS Next. Com texto, busque só pelo
texto e filtre o resultado pelas colunas `type`/`folder`. Prefira pasta/tipo quando o pedido permitir: a busca por
texto varre o componente inteiro e é mais lenta.

### Leitura (`rm_get_requirement`)

A saída de `rm_get_requirement` é um documento no **Open Knowledge Format (OKF) v0.2** — Markdown com cabeçalho YAML
(frontmatter) + corpo. Cada leitura é **um único concept** OKF (não um bundle): não há `index.md`/`log.md` nem
hierarquia de diretórios numa leitura unitária. Referências:
[spec e repositório](https://github.com/GoogleCloudPlatform/open-knowledge-format),
[SPEC.md v0.2](https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md),
[okf.md](https://okf.md/).

```markdown
---
# --- campos OKF padrão ---
type: Caso de Uso                                   # OBRIGATÓRIO (OKF §4.1)
title: UC - Cadastrar cliente                       # recomendado
description: Cadastro de um novo cliente no sistema. # recomendado (1 linha)
resource: "https://alm.example.com/rm/resources/TX_exemplo2010"  # recomendado: URI do artefato
tags: ["03-Casos de Uso"]                           # recomendado: a pasta
# --- provenance (OKF §5.1) ---
sources:
  - id: doors-next
    resource: "https://alm.example.com/rm/resources/TX_exemplo2010"
    author: "human:ana.silva"                       # quem criou
    last_modified: "2026-10-05T19:42:00Z"           # última modificação no ALM
    last_modified_by: "human:joao.souza"            # quem modificou por último (extensão)
# --- família trust (OKF §5.2) ---
generated: { by: "process:alm-mcp/1.0.14", at: "2026-10-06T13:00:00Z" }  # quando este documento foi gerado
# --- chaves de extensão RM (OKF §4.1 "Extensions") ---
id: 2010
created: "2026-09-01T13:15:00Z"                      # UTC
links:                                               # só leitura
  Vincular A:
    - "2002: RN - Cliente deve ser maior de idade"
  Implementado por:
    - "1001: Implementar cadastro de clientes"
embedded:
  - "2001: RN - Validar CPF do cliente"
---
## Fluxo Básico

1. O usuário informa os dados do cliente.
2. O sistema valida o documento: [2001 RN - Validar CPF do cliente](https://alm.example.com/rm/resources/TX_exemplo2001)
3. O sistema aplica a regra [2002 RN - Cliente deve ser maior de idade](https://alm.example.com/rm/resources/TX_exemplo2002) e grava o cliente.
```

**Campos OKF padrão.** Só `type` é obrigatório (um concept só com `type` já é conforme). `title`, `description`,
`resource` (o URI canônico do artefato) e `tags` (a pasta) são recomendados. Nomes de links são os
do **DOORS Next** (o alm.json não mapeia o RM); pessoas vêm pelo login; campos vazios são omitidos; todas as datas
(`created`, `sources[].last_modified`, `generated.at`) em **ISO 8601 com offset UTC**.

**Provenance (OKF §5.1).** `sources` tem uma entrada, o artefato no DOORS Next: `resource` (URL), `author`
(`human:<login>` de quem criou), `last_modified` = a **última modificação no ALM**, em ISO 8601 UTC, e a extensão
`last_modified_by` (`human:<login>` de quem modificou por último). Vazios são omitidos.

**Trust (OKF §5.2).** `generated: { by, at }` é sempre emitido: `by` é um ator — aqui `process:alm-mcp/<versão>`,
a geração automática pelo MCP (§7) — e `at` é o **instante em que o documento foi gerado**, em ISO 8601 UTC.
`sources[0].last_modified` > `generated.at` ⇒ a cópia está desatualizada. (A alm-sync não usa esse critério: o
`sync.md` guarda a data do ALM e o hash de cada arquivo.)
`description` só aparece quando o artefato tem descrição no DOORS Next; senão é omitido.

As demais famílias OKF — `verified`, `status` (lifecycle §5.4) e `stale_after` (§5.5) — **não são emitidas** para
requisitos do RM: o DOORS Next não expõe um sinal de revisão/estado/validade definido pelo servidor. A ausência é
conforme (campos opcionais ausentes, §11); por §5.3, sem `verified` o concept é tratado como **unverified**.
Atributos do tipo (ex.: "Prioridade", "Situação") não são emitidos.

**Chaves de extensão RM.** `id`, `created`, `links` e `embedded` (e `sources[].last_modified_by`)
são chaves extras do produtor (OKF §4.1 "Extensions"): consumidores OKF **preservam** essas chaves e **não**
rejeitam o documento por não as conhecer (§11). Carregam o que o OKF padrão não modela:

- `id` — o id global do DOORS Next (o concept ID "oficial" do OKF seria o caminho do arquivo, que não existe numa
  leitura unitária).
- `created` — criação do artefato, em ISO 8601 UTC.
- `links` — links de rastreabilidade por tipo de link, pelos **nomes do DOORS Next**. **Só leitura**: nenhuma
  tool os grava (crie/remova na UI do DOORS Next).
- `embedded` — os artefatos embutidos no texto (`id: título`). É **esta lista** que diz o que é embed no corpo.
  Não aparece com `links="bundle"`: no bundle, a regra fixa abaixo já diz o que é embed.

**Relacionamentos no corpo.** De forma idiomática, o OKF expressa relações como links markdown no corpo (o tipo da
relação vem da prosa, não do link); consumidores toleram links quebrados. No RM a leitura sai **sempre no mesmo
padrão**, qualquer que seja o jeito como o texto foi escrito:

| No DOORS Next | Na leitura |
|---|---|
| Artefato **embutido** | `[<id> <título>](<URL do ALM>)` e o id em `embedded` |
| **Hyperlink** para artefato do RM | `[<id> <título>](<URL do ALM>)` (o texto original do link é trocado por `id título`) |
| Embed ou link quebrado (artefato ilegível) | `[texto](URL do ALM)`, como está; fora de `embedded` |
| Link para fora do RM | `[texto](url)`, como está |

- Com `rm_get_requirement(id, links="bundle")` (usado pela alm-sync) a regra é fixa: **artefato do bundle é embed**,
  com alvo no **caminho relativo do arquivo**, ex.:
  `[23434 REG Validar data fim periodo PAB](<../03 Regras Negócio/23434-reg-validar-data-fim-periodo-pab.md>)`;
  **o resto é link** (outra PA, fora das pastas), com alvo na URL do ALM. Caminho com espaço vem entre `<...>`.
- O corpo não tem `!`: embed e hyperlink têm a mesma escrita; o que é embed está em `embedded`. Ao gravar, mande o
  `embedded` junto, senão o embed vira hyperlink.
- O mapa `links` do frontmatter continua sendo a fonte dos links de rastreabilidade; `embedded` lista os embeds.
- Lê só a stream do alm.json e só os links do próprio artefato: **links de módulo e links que chegam de outros
  artefatos não aparecem**. Não afirme "não há link"; diga que não há link no artefato e sugira conferir na UI.

**Conformance (OKF §11).** O documento é conforme ao OKF v0.2: tem frontmatter YAML parseável e `type` não-vazio.
Como é um concept único, `index.md`/`log.md` (§8/§9) não se aplicam. Consumidores OKF **não devem** rejeitar o
documento por campos opcionais ausentes, `type` desconhecido, chaves de extensão (`id`, `created`, `links`,
`embedded`, `sources[].last_modified_by`) ou links quebrados no corpo.

### Gravação

- Só **título e texto** são gravados. Atributos e links de rastreabilidade não têm gravação pelo MCP.
- **`text` substitui o texto inteiro.** Leia, edite o corpo (sem o cabeçalho YAML), mantenha os links existentes e
  mande tudo com o `embedded` do cabeçalho (mais os ids que forem embutir). Ler → gravar → ler não muda o texto; só estilos visuais do Word (fonte, cor) se perdem.
- `text` em Markdown: títulos, listas, negrito e as referências da seção abaixo.

### Referências a outros artefatos do RM

Há três formas de relacionar um artefato a outro. Escolha pelo que o usuário quer ver:

| Forma | Escrita | Onde fica | Quando usar |
|---|---|---|---|
| **Embed** | `[2003](2003)` no `text` + `"2003"` em `embedded` | dentro do texto: o DOORS Next mostra o conteúdo do 2003 naquele ponto | "embute", "inclui a regra no passo", "mostra a mensagem no fluxo" |
| **Hyperlink no texto** | `[2003](2003)` no `text`, fora de `embedded` | dentro do texto, como link clicável | "cita", "referencia", "aponta para" |
| **Link de rastreabilidade** | — (só leitura) | fora do texto (aba Links), em `links` do cabeçalho | "liga", "vincula", "relaciona": diga que é feito na UI do DOORS Next |

- **Escrita.** Sempre `[texto](alvo)`; é embed se o artefato está em `embedded` (`"2003"` ou `"2003: título"`),
  senão hyperlink. O texto entre `[]` é livre (o MCP o normaliza na próxima leitura) e o alvo pode ser:

  | Alvo | Exemplo |
  |---|---|
  | id | `[2003](2003)` |
  | URL do ALM (ou link da UI web com `artifactURI`) | `[x](https://.../rm/resources/TX_...)` |
  | arquivo do bundle (nome começa pelo id) | `[x](<../03 Regras/2003-rn-validar-cpf.md>)`, `[2003 RN Validar](<2003 RN Validar.md>)` |

  Escreva o alvo com espaço entre `<...>`. Alvo que não é artefato do RM (site, imagem) fica como link/imagem comum.
- Embed: o DOORS Next mostra o conteúdo do artefato naquele ponto; na leitura volta como `[id título](alvo)` e
  aparece em `embedded`. Hyperlink: link comum de texto, **não** cria link de rastreabilidade nem aparece em `links`.
- Embed e hyperlink vivem no `text`: gravar é mandar o corpo inteiro.

**Exemplo — "no UC 2010, embute a RN 2003 no passo 3 e cita a MSG 2005 no passo 4":**

1. `rm_get_requirement("2010")` → corpo atual:

   ```markdown
   ## Fluxo Básico

   1. O usuário informa os dados do cliente.
   2. O sistema valida o documento: [2001 RN - Validar CPF do cliente](https://alm.example.com/rm/resources/TX_exemplo2001)
   3. O sistema verifica a idade do cliente.
   4. O sistema grava o cliente.
   ```

2. Novo corpo: mantém o embed 2001, acrescenta o embed 2003 e o hyperlink para a 2005:

   ```markdown
   ## Fluxo Básico

   1. O usuário informa os dados do cliente.
   2. O sistema valida o documento: [2001 RN - Validar CPF do cliente](https://alm.example.com/rm/resources/TX_exemplo2001)
   3. O sistema verifica a idade do cliente: [2003](2003)
   4. O sistema grava o cliente e exibe a [2005](2005).
   ```

3. Mostre o trecho alterado, confirme e chame
   `rm_update_requirement("2010", text=<corpo inteiro>, embedded=["2001", "2003"])` (o 2005 fica fora: hyperlink).
4. Confira lendo de novo: `embedded` deve listar 2001 e 2003, e o corpo volta no padrão
   (`[2003 RN - ...](url)`, `[2005 MSG - ...](url)`).

**Exemplo — criar uma HU já com referências:**

```text
rm_create_requirement(..., requirement_type=rm.requirements-types["História de Usuário"],
    folder=rm.folders["02-Histórias"], title="HU - Exportar relatório em PDF",
    text="Como gestor, quero exportar o relatório em PDF.\n\n"
         "**Regras**\n\n- [2001](2001)\n- Formato do arquivo: ver [ET 2007](2007)",
    embedded=["2001"])
```

Aqui o 2001 fica embutido e a ET 2007 é citada por hyperlink.

## Fluxos

- **Buscar:** por pasta/tipo do alm.json; ou só por texto e filtrar localmente.
- **Conferir modificação:** "o 2010 mudou?", "quando foi alterado o UC 2010" → `rm_list_modified(["2010"])`;
  vários ids → uma chamada com a lista. Responda em tabela **Código | Título | Última modificação**.
- **Ler:** `rm_get_requirement(id)`. Baseline ou outra configuração → `get_requirement` com `configuration_url`
  ([reference.md](reference.md)).
- **Ligar requisitos** ("liga o UC 2010 à regra 2003"): não há tool; diga que o link de rastreabilidade é criado na
  UI do DOORS Next. Se servir, ofereça citar (hyperlink) ou embutir no texto.
- **Embutir ou citar no texto:** ver "Referências a outros artefatos do RM".
- **Criar:**
  1. Tipo e pasta pelo alm.json (pergunte se o pedido não disser; sugira pela sigla).
  2. Monte título e `text` em Markdown.
  3. Mostre o resumo e peça confirmação. `rm_create_requirement(...)`; responda com código, título e url.
- **Ligar a work item / teste:** alm-gc, com o `resource` do cabeçalho ou o `url` da busca.

## Erros

| Mensagem (trecho) | O que fazer |
|---|---|
| HTTP 400 na busca | Não combine `text` com `folder`/`requirement_type` |
| `Informe ao menos um filtro` | Peça pasta, tipo ou texto |
| `requirement_id deve ser numérico` | Busque por texto para achar o id |
| `Requisito N não encontrado` | Pode estar em outro componente/stream: diga isso; não varra outras áreas |
| HTTP 403 | Sem permissão: informe e pare |
| HTTP 412 | Edição concorrente: releia e repita **uma** vez |

## Regras

- **Confirme toda escrita** com um resumo por nomes (inclusive a lista final de links). Uma escrita por vez.
- Nunca invente ids, nomes de pasta/tipo ou valores.
- Não crie requisitos para "testar" algo: use leitura.
