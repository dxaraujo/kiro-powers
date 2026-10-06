---
name: "sdd-planejamento"
description: "Criação e reajuste de planejamento ágil Scrum do projeto (fluxo SDD). Extrai backlog dos documentos de insumo, estima complexidade (Fibonacci via Planning Poker simulado), distribui em sprints com entregáveis deployáveis, reserva 20% para correções pós-homologação, gera .md e exporta Excel com fórmulas. Suporta publicação no ALM/EWM via skill sdd-alm-publicar-planejamento. Use em \"monta o planejamento\", \"planejar sprints\", \"virada de sprint\", \"fechar sprint\", \"reajustar o planejamento\"."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.0.0"
  keywords: "fechar sprint, virada de sprint, encerrar sprint, reajuste, agile, scrum, planning, sprint, backlog, fibonacci, estimativa, homologacao, excel, planejamento, priorizacao, velocidade, planning poker, alm, ewm, publicar"
---

# sdd-planejamento — Planejamento Ágil

## Objetivo

Criar ou reajustar o planejamento ágil Scrum do projeto, gerando arquivos `.md` (um por sheet)
e consolidando em planilha Excel única com fórmulas de cálculo.

> **Regra de ouro:** ao final de cada etapa, **apresente o plano e aguarde "ok"** antes de gravar.
> Contexto: o steering de **produto** do projeto (apontado em `.kiro/steering/sdd-projeto.md`).

---

## Diretório de Saída

`planejamento-agil/` (na raiz do repositório)

---

## Conceitos-Chave

### IB (Item de Backlog)

Funcionalidade/requisito de **negócio** — nunca referência camada técnica.
Exemplos: "Limitar tentativas de login", "Importar o arquivo de pagamentos do parceiro".

**Regra de unificação:** Um IB engloba TODO o trabalho da funcionalidade (ESPEC+BE+BD+QA) — uma funcionalidade nova ou
uma alteração coesa. Nunca criar IBs separados por papel (ex.: "Especificar X" + "Implementar X").
Se a especificação é feita numa sprint e o código noutra, é o **mesmo IB** com tasks em sprints diferentes.

### Tasks (subordinadas ao IB)

Decomposição técnica. Cada task é uma linha na sprint:

| Prefixo | Descrição                 | Inclui                                                   |
| ------- | ------------------------- | -------------------------------------------------------- |
| [ESPEC] | Especificação             | HF/REG/ET/CT + validação + publicação no ALM — papel especificador |
| [BE]    | Codificação               | Spec SDD + implementação + testes unitários + massa de teste + PR — papel codificador |
| [BD]    | Banco de dados            | Solicitação de DDL — fora do fluxo; bloqueia só testes (dev) e implantação (prod) |
| [QA]    | Testes funcionais         | Execução dos CTs com evidências (nunca testes unitários) — papel testador |
| [INF]   | Infraestrutura            | Pipeline, ambientes, agendamento no workflow             |

> Os prefixos `[ESPEC]`, `[BE]` e `[QA]` (configuráveis no `sdd-projeto.md`) definem o **papel** de quem atende a
> Task no fluxo SDD (`sdd-tarefa`); `[BD]` é tratada com quem administra o banco, fora do fluxo. Testes unitários são parte intrínseca da task [BE] — código só é
> "Feito" com testes unitários.

### Tracking

Coluna única **"Feito"** (OK ou vazio) por task. Complexidade só no IB (linha-pai).
O "Feito" da linha do IB é calculado pelo Excel (OK quando todas as tasks da sprint estão OK) — não marcar à mão.

### Velocidade (Scrum clássico)

- `Velocidade da sprint (pts/hora) = Pontos Entregues / Total Horas Produtivas`
- `Velocidade média = AVERAGE(velocidades das sprints encerradas)`
- `Capacidade da Equipe em Pontos = Total Horas × Velocidade Média`
- Capacidade da próxima sprint = Capacidade da Equipe em Pontos
- Recalcular a cada sprint encerrada

---

## Fluxo de Execução

### Etapa 1 — Extração do Backlog

**Fontes de insumo** (buscar no repositório):

- Descrição dos IBs e Tasks no ALM (skill `alm-ccm`)
- Documentos de demanda (nota técnica, visão, atas)
- HFs existentes (`.kiro/specs/ib-*/HF.md`)
- Outros documentos indicados pelo usuário

**Ações:**

1. Ler os documentos de insumo.
2. Extrair funcionalidades e requisitos de negócio.
3. Decompor em **IBs granulares** (máximo 13 pontos cada).
   - Se um item parecer épico (≥ 20 pontos), **quebrá-lo imediatamente**.
   - **Validar unificação:** cada funcionalidade = 1 IB (ex.: "Limitar tentativas de login" inclui ESPEC+BE+QA).
   - **Nunca** criar IBs separados para "especificar X" e "implementar X".
   - Funcionalidades independentes (sem dependência entre si) → **cada uma é um IB**.
4. Para cada IB:
   - Descrição funcional (orientada a negócio)
   - Dependências (quais IBs são pré-requisito)
   - Criticidade (alta/média/baixa) — vira a **Prioridade** do IB no ALM
   - Tasks necessárias ([ESPEC], [BE], [BD], [QA], [INF]) — todo IB tem [ESPEC], [BE] e [QA]
5. Apresentar backlog e aguardar confirmação.

---

### Etapa 2 — Coleta de Informações da Equipe

> **Regra:** Perguntar **um bloco por vez**. Aguardar resposta antes de passar ao próximo.

#### 📂 Passo 0 — Ler a equipe salva (sempre, antes de perguntar)

Ler `planejamento-agil/equipe.json` (formato em [Arquivo da equipe](#arquivo-da-equipe-equipejson)).

- **Existe** → mostrar um resumo e perguntar **só o que mudou**, numa única pergunta:
  ```
  👥 Equipe salva (atualizada em <data>):
  | Membro | Login | Papel | Senioridade | Exp. | h/semana | Ausências previstas |
  Projeto: sprint de <N> semanas · velocidade média <x> pts/h · P.O.: <nome> · SM: <nome>
  Mudou algo para esta(s) sprint(s)? (entrada/saída de membro, horas, férias, papel) — ou "ok"
  ```
  "ok" → **pular os Blocos 1 e 2** (exceto o que faltar no arquivo) e ir ao Bloco 3.
  Mudança informada → aplicar no arquivo e seguir.
- **Não existe** → fazer os Blocos 1 e 2 e, ao final do Bloco 2, **criar** o arquivo.

---

#### 📋 Bloco 1 — Informações da Equipe

**Perguntar:**

| Informação                     | Exemplo                                                  |
| ------------------------------ | -------------------------------------------------------- |
| Nome do membro                 | João                                                     |
| Papel                          | Dev BE / Dev FE / FullStack / QA / DevOps / Scrum Master |
| Nível de senioridade           | Sênior / Pleno / Júnior / Estagiário                     |
| Experiência com a tecnologia   | Alta / Média / Baixa                                     |
| Disponibilidade (horas/semana) | 30h                                                      |
| Fatores especiais              | férias, part-time, ramp-up                               |

**Identificar obrigatoriamente:** Scrum Master (com nível/experiência) e P.O.

**Login ALM de cada membro:** buscar pelo nome em `members` de `alm/pa_*.json` (`ccm.members`, se houver o power alm); sem
correspondência única, perguntar. É o login usado como responsável na publicação no EWM.

**Aguardar resposta.**

---

#### ⚙️ Bloco 2 — Configurações do Projeto

**Perguntar:**

- Duração da sprint (padrão: 2 semanas)
- Velocidade prévia (pontos/sprint), se existir — será convertida para pts/hora
- Data de início do projeto
- Nome do projeto e demanda (se houver)

**Aguardar resposta.** Em seguida, gravar (ou atualizar) `planejamento-agil/equipe.json` com os Blocos 1 e 2.

---

#### 🎯 Bloco 3 — Planning Poker

**Perguntar:** A equipe vai participar do Planning Poker (vocês definem os pontos) ou quer que eu simule a estimativa com base nos perfis da equipe?

**Aguardar resposta.** O tratamento segue na Etapa 3.

---

### Etapa 3 — Estimativa de Complexidade (Planning Poker / Fibonacci)

**Escala (a mesma do campo Pontos de História do ALM):** 0, 1, 2, 3, 5, 8, 13, 20, 40, 100.
No planejamento usar só **0 a 13** — máximo por IB = **13**; 20, 40 e 100 só existem no ALM para épicos.

**Ações** — seguir a resposta do Bloco 3 (não perguntar de novo):

- **Equipe estima:**
  1. Perguntar a pontuação da equipe **um IB por vez** (pergunta sobre o IB-01, aguarda, depois IB-02…).
  2. Rodar a simulação de Planning Poker (abaixo).
  3. Apresentar a comparação e perguntar qual pontuação usar: equipe, simulação, média ou mediana.
     - **Mediana/média** = sobre {pontos da equipe + votos simulados}, arredondada para o valor mais próximo da escala.
     - **Desvio padrão** = populacional entre pontos da equipe e mediana simulada.
  4. Registrar no `Backlog.md` as colunas `Equipe | Simulação | Final | Desvio`.
- **Equipe não estima:** rodar só a simulação.

**Simulação de Planning Poker:**

- Criar um **agente** por membro (exceto P.O.).
- Cada agente estima considerando seu perfil.
- Estimativa final: **mediana** com justificativa se divergência > 1 nível.

**Viés por persona:**

| Persona    | Viés                                      |
| ---------- | ----------------------------------------- |
| Sênior     | Precisas, considera riscos e dependências |
| Pleno      | Razoáveis, pode subestimar integração     |
| Júnior     | Subestima em ~30%                         |
| Estagiário | Subestima em ~50%                         |

**Regra:** Se estimativa ≥ 20 → decompor em sub-IBs (≤ 13 cada). Nunca usar valores fora da escala (ex.: 21).
Após calcular a capacidade (Etapa 4), todo IB maior que a capacidade de **uma** sprint também é decomposto em sub-IBs e reestimado — um IB espalhado por várias sprints só para caber gera sprints com 0 pontos entregues e distorce a velocidade.

---

### Etapa 4 — Priorização e Alocação em Sprints

**Critérios:**

1. **Dependência técnica** — IBs que desbloqueiam outros primeiro
2. **Criticidade** — alta > média > baixa
3. **Entregáveis** — agrupar IBs que formam entrega deployável
4. **Risco** — maior incerteza mais cedo

**Regras:**

- Velocidade conhecida → `Capacidade = Total Horas/Sprint × Velocidade Média (pts/hora)`
- Se não há histórico (primeira sprint), calibrar a velocidade inicial pelo método "ver o que cabe"
  (Cohn, *Agile Estimating and Planning*, cap. 16):
  1. **Horas efetivas da sprint** (isto são horas, não pontos):
     ```
     Horas efetivas = Σ (horas_membro_na_sprint × fator_senioridade × fator_experiencia)
     Sênior=1.0, Pleno=0.75, Júnior=0.5, Estagiário=0.3
     Exp. tech: Alta=1.0, Média=0.7, Baixa=0.5
     ```
  2. Estimar em horas as tasks de uma **amostra variada** de IBs (não só os menores; misturar BE/FE/QA)
     e ir somando até encher as horas efetivas — ou até um papel (BE, FE, QA) lotar.
  3. `Velocidade inicial (pts/hora) = pontos dos IBs que couberam / horas produtivas da sprint`.
  4. Registrar a amostra (IB, pontos, horas das tasks) no `Planejamento Ágil.md`.
  - **Nunca** usar taxa fixa "1 ponto = N horas": a relação entre pontos e horas é uma distribuição,
    e uma taxa fixa produz números precisos demais e errados.
  - Na Etapa 5 as entregas usam a data da estimativa central; a velocidade é recalibrada ao fim de cada sprint.
- Velocidade prévia informada em pts/sprint (Bloco 2) → converter: `pts/sprint ÷ horas produtivas da sprint`.
- Na sheet "Planejamento Ágil", exibir capacidade como texto descritivo (não fórmula Excel)
- **Sprint 0** = Setup, planejamento, kickoff (sem pontos)
- Sprint pós-entrega: homologação + **~20%** para correções + **~80%** novos IBs

---

### Etapa 5 — Cronograma e Entregas

1. Agrupar sprints em entregas deployáveis.
2. Definir datas de início/término (perguntar data de início da sprint atual).
3. Gerar cronograma visual com datas no roadmap.
4. Incluir datas nas Entregas.

---

### Etapa 6 — Geração dos Arquivos Markdown

Gerar em `planejamento-agil/` (na raiz do repositório):

| Arquivo                 | Conteúdo                                                          |
| ----------------------- | ----------------------------------------------------------------- |
| `Backlog.md`            | Item \| Prioridade \| Sprint \| Entrega \| Complexidade \| Escopo (+ Equipe \| Simulação \| Final \| Desvio se a equipe estimou) |
| `Planejamento Ágil.md`  | Grid sprints × semanas + cerimônias + legenda                     |
| `SPRINT N.md`           | IBs + tasks + Feito + Horas + Métricas + Retrospectiva            |
| `Entregas.md`           | Nº \| Entrega \| Data Início \| Data Término                      |
| `Homologação.md`        | Tracking + retrospectiva geral + resumo sprints                   |
| `Conceito de Pronto.md` | Definition of Ready + Definition of Done                          |
| `equipe.json`           | Equipe e configuração do projeto, reutilizadas nas sprints atuais e futuras |
| `md_to_excel.py`        | Script MD → Excel (com fórmulas) — copiado desta skill            |
| `excel_to_md.py`        | Script Excel → MD — copiado desta skill                           |

> Os scripts `md_to_excel.py` e `excel_to_md.py` ficam na pasta desta skill (power `sdd-workflow`) e são copiados
> para `planejamento-agil/` na primeira geração (e atualizados se a versão da skill for mais nova).

**Formato da SPRINT N.md:**

```markdown
# SPRINT N

| Sprint N - <Foco>                    | Complexidade | Feito |
| :----------------------------------- | :----------- | :---- |
| Item de Backlog                      |              |       |
| IB-XX - Funcionalidade de Negócio    | 8            |       |
| [ESPEC] Especificar HF/REG/ET/CT     |              |       |
| [BE] Implementar + PR                |              |       |
| [BD] Solicitar alteração de modelo   |              |       |
| [QA] Executar CTs                    |              |       |
| IB-YY - Outra Funcionalidade         | 5            |       |
| [ESPEC] Especificar                  |              |       |
| [BE] Implementar                     |              |       |
| [QA] Testes funcionais               |              |       |
|                                      |              |       |
| Débitos Técnicos                     |              |       |
|                                      |              |       |
| Homologação (Entrega X)              |              |       |

| Horas Produtivas |      |
| :--------------- | :--- |
| <Membro 1>       | XX   |
| <Membro 2>       | XX   |
| Total            | =SUM |

| Métricas                     |          |
| :--------------------------- | :------- |
| Pontos Planejados            | XX       |
| Pontos Entregues             | =fórmula |
| Velocidade Sprint            | =fórmula |
| Velocidade Média (acumulada) | =fórmula |

| RETROSPECTIVA |
| :------------ | :------------------ | :------------------------ |
| O QUE FOI BOM | O QUE PODE MELHORAR | A FAZER NA PRÓXIMA SPRINT |
|               |                     |                           |
|               |                     |                           |
|               |                     |                           |
```

**Conceito de Pronto.md:**

```markdown
# Conceito de Pronto

| Conceito de preparado (Definition of Ready): |
| :------------------------------------------- |
| Especificação concluída ([ESPEC] Feito)      |
| Especificação aprovada pelo P.O.             |
| Dependências técnicas resolvidas             |

| Conceito de pronto (Definition of Done):             |
| :--------------------------------------------------- |
| Código implementado com testes unitários e cobertura no gate ([BE]) |
| Judge aprovado (sdd-revisar)                         |
| CTs executados e aprovados com evidência ([QA])      |
| Análise estática sem bloqueadores (se o projeto usa) |
| PR aprovado nos testes e mergeado (GATE 3)           |
```

---

### Etapa 7 — Exportação para Excel (com fórmulas e Gantt)

Gerar `<Nome do Projeto> - Planejamento Ágil.xlsx` com:

- Formatação visual (cabeçalhos azul escuro, IBs azul claro, OK verde, métricas amarelo, retro laranja)
- Fórmulas reais: Total horas (SUM), Pontos Entregues (SUMPRODUCT), Velocidade Sprint, Velocidade Média (AVERAGE entre sprints)
- Sheet "Gantt" com barras visuais (sprints × semanas, sprint atual destacada)
- Freeze panes no cabeçalho

Executar o script instalado no projeto:

```powershell
python planejamento-agil/md_to_excel.py planejamento-agil "<Nome do Projeto> - Planejamento Ágil"
```

> O script fica na pasta desta skill e é copiado para `planejamento-agil/`.

---

### Etapa 8 — Publicar no ALM (opcional)

Perguntar ao usuário:

```
O planejamento está concluído. Deseja publicar a SPRINT ATUAL (Sprint N) no ALM/EWM agora?
(As próximas sprints ficam só no planejamento local e são publicadas quando virarem a atual.)

(s) Sim — invocar a skill sdd-alm-publicar-planejamento
(n) Não — encerrar aqui
```

**Se "sim":** invocar a skill `sdd-alm-publicar-planejamento`, passando o contexto:

- Diretório dos arquivos de planejamento: `planejamento-agil/` (na raiz do repositório)
- Número e período da sprint atual (só ela é publicada)
- Perguntar ao usuário qual iteração deve ser utilizada ou se deve ser criada uma iteração nova.
- Perguntar ao usuário em qual plano da iteração selecionada os itens devem ser criados ou se deve ser criado um plano novo.
- Incluir as iterações ou planos criados as pa do projeto invocando a skill `alm-setup` do power alm

**Se "não":** encerrar normalmente com o resumo abaixo.

> Para publicar no ALM posteriormente, invoque diretamente: _"publicar planejamento no ALM"_.

---

## Modo de Reajuste

Usado a qualquer momento e, obrigatoriamente, na **virada de sprint** (fim da sprint atual — "fechar sprint",
"virada de sprint"). Na virada, a ordem é: Passo 1 → Passo 2 (com o estado do ALM) → Passo 3 → Passo 4.

### Passo 1 — Importar do Excel

O planejamento é mantido manualmente via Excel.

1. Ler a planilha de planejamento (`planejamento-agil/*.xlsx`).
2. Executar `excel_to_md.py` para converter em `.md`:

```powershell
python planejamento-agil/excel_to_md.py \
    "planejamento-agil/<planilha>.xlsx" \
    planejamento-agil/
```

> O script fica na pasta desta skill e é copiado para `planejamento-agil/`.

### Passo 2 — Avaliar Estado Atual

0. Ler `planejamento-agil/equipe.json` e confirmar mudanças da equipe para as próximas sprints
   (mesma pergunta única do Passo 0 da Etapa 2) — nunca refazer o questionário inteiro.
1. **Sincronizar com o ALM** (se a sprint foi publicada — há `alm_id` no `backlog.json`): obter o estado real
   de cada IB/Task da sprint que está terminando (via `sdd-alm-publicar-planejamento`, Passo 7, item 1) e
   marcar `Feito = OK` no `SPRINT N.md` o que estiver concluído no EWM. O EWM prevalece sobre o `.md`.

1. Identificar sprint atual.
2. Para sprints anteriores:
   - IBs com todas as tasks "Feito=OK" → **Done**, contabilizar na velocidade.
   - IBs/tasks **não prontos** → **replanejar** (mover para sprint atual ou seguinte).
3. Recalcular velocidade média com sprints encerradas e gravar em `equipe.json` (`projeto.velocidade_media` +
   entrada em `projeto.historico_velocidade`).
4. Perguntar motivo do reajuste.

### Passo 3 — Replanejar

1. **Migrar não concluídos para a próxima sprint:** IBs/Tasks da sprint encerrada sem `Feito = OK` vão para a
   `SPRINT N+1.md` (no topo, antes dos itens planejados). Na `SPRINT N.md` eles permanecem com `Feito` vazio e a
   nota `→ migrado para Sprint N+1` (o histórico não é apagado).
2. **Rever as próximas sprints:** com a velocidade recalculada e a capacidade da equipe (`equipe.json`, já com
   ausências), redistribuir a partir da Sprint N+1 — os migrados consomem capacidade primeiro; o excedente
   empurra itens para as sprints seguintes. Reavaliar prioridade e dependências; atualizar `Entregas.md` se datas mudarem.
3. Redistribuir usando velocidade média real. IB que não cabe numa sprint → decompor em sub-IBs (mesmo total, reestimados).
4. Manter histórico das sprints encerradas inalterado (tasks e marcações OK — inclusive não remarcar a linha do IB).
5. Regenerar `.md` afetados + Excel e apresentar o diff do plano (o que entrou/saiu de cada sprint futura).

### Passo 4 — Publicar a nova sprint atual

Na virada de sprint, perguntar e acionar a **`sdd-alm-publicar-planejamento`** em modo **virada de sprint**,
passando a sprint encerrada (N), a nova atual (N+1) e a lista de itens migrados: ela move no EWM os não
concluídos para a iteração da Sprint N+1 (sem recriar) e publica só os itens novos da Sprint N+1.

---

## Arquivo da equipe (`equipe.json`)

`planejamento-agil/equipe.json` — fonte da equipe para **todas** as sprints (criação e reajuste) e
para a `sdd-alm-publicar-planejamento` (logins do P.O. e dos responsáveis). Versionado no git.

```json
{
  "atualizado_em": "2026-10-05",
  "projeto": {
    "nome": "<Nome do Projeto>",
    "demanda": "<id da demanda, se houver>",
    "duracao_sprint_semanas": 2,
    "inicio": "2026-10-06",
    "velocidade_media": 0.42,
    "historico_velocidade": [{ "sprint": 1, "pts_hora": 0.40 }]
  },
  "membros": [
    {
      "nome": "Maria Silva",
      "login": "maria.silva",
      "papel": "Dev BE",
      "senioridade": "Sênior",
      "experiencia": "Alta",
      "horas_semana": 30,
      "scrum_master": false,
      "po": false,
      "ativo": true,
      "fatores": "part-time",
      "ausencias": [{ "inicio": "2026-12-20", "fim": "2027-01-05", "motivo": "férias" }]
    }
  ]
}
```

Regras:
- Exatamente um `po: true` e um `scrum_master: true` entre os membros ativos.
- Quem sai da equipe fica com `ativo: false` (preserva o histórico das sprints passadas); não apagar.
- Horas de uma sprint = `horas_semana × semanas` − dias de `ausencias` que caem na sprint.
- Atualizar `atualizado_em` a cada gravação; mostrar o diff à pessoa antes de gravar mudanças.
- Sem senha ou dado pessoal além de nome e login.

---

## Regras de Negócio

| Regra              | Detalhe                                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Pontos             | Escala do ALM: 0, 1, 2, 3, 5, 8, 13, 20, 40, 100. Máximo por IB = 13. Se ≥ 20, decompor.                               |
| Velocidade         | pts/hora. Recalcular a cada sprint. Capacidade = Horas × Velocidade Média.                                             |
| Homologação        | Sprint pós-entrega: homologação + 20% para correções.                                                                  |
| Entregáveis        | Funcionalidade completa (ESPEC+BE+QA, PR mergeado). Nunca entregar só a especificação ou só o código.                  |
| IBs                | Orientados a negócio, sem referência a camada. 1 funcionalidade = 1 IB.                                                |
| Unificação         | Nunca criar IBs separados por papel. ESPEC+BE+BD+QA = mesmo IB.                                                        |
| IB multi-sprint    | Só por dependência (ex.: ESPEC na sprint 2, BE na sprint 3), nunca para caber na capacidade. Pontos ficam só na linha do IB da sprint em que ele termina; nas demais, complexidade em branco. |
| IB > capacidade    | IB maior que a capacidade de uma sprint → decompor em sub-IBs e reestimar (criação e reajuste).                        |
| Sprints futuras    | Nunca planejar tasks já concluídas. Tasks feitas devem constar apenas na sprint onde foram executadas (verificar git). |
| Separação          | Funcionalidades independentes = IBs separados.                                                                         |
| Tasks              | Uma por papel: [ESPEC], [BE], [QA] em todo IB; [BD] e [INF] quando houver. [BE] inclui testes unitários e massa de teste.        |
| [ESPEC]            | Todo IB tem task de especificação (antes da implementação).                                                            |
| [QA]               | Todo IB tem task de testes funcionais (execução dos CTs).                                                              |
| [BD]               | Solicitação de DDL, fora do fluxo. Não bloqueia especificação nem codificação; bloqueia testes até a DDL em dev e implantação até a DDL em produção. |
| Feito              | Coluna única binária (OK/vazio) por task.                                                                              |
| Retrospectiva      | Ao final de cada sprint: O que foi bom \| O que pode melhorar \| A fazer na próxima sprint.                            |
| Review             | Cada sprint tem campo "Observações da Review" para anotações da apresentação ao P.O.                                   |
| Capacidade         | Nunca planejar sprint acima da Capacidade (Horas × Velocidade Média). Redistribuir excedentes.                         |
| Publicação no ALM  | Só a sprint atual é publicada. Futuras ficam locais até virarem a atual.                                               |
| Virada de sprint   | Não concluídos migram para a sprint seguinte (no EWM: movidos via plannedFor, nunca recriados) e as sprints futuras são replanejadas. |

---

## Dependências

- Python 3 + `openpyxl`
- Para publicação no ALM: skill `sdd-alm-publicar-planejamento` + power `alm` (MCP `alm`)
