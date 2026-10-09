---
name: "elk-diagnostico"
description: "Investigate a production problem from ELK/Kibana logs through the `elk` MCP (read-only): size the impact, find where errors concentrate, compare with a normal period, find when it started, sample evidence and report a root-cause hypothesis. Use when the user wants to understand a problem, not just see logs: \"o sistema caiu às 10h, o que aconteceu?\", \"por que está dando erro 500?\", \"teve pico de erros hoje?\", \"está lento desde ontem\", \"investiga o incidente\", \"qual a causa raiz\", \"o erro aumentou depois do deploy?\", \"o que mudou em relação a ontem\". For just listing or counting logs use elk-logs; for files use elk-exportar."
license: "MIT"
metadata:
  author: "Daniel Xavier Araújo"
  version: "1.2.0"
---

# elk-diagnostico

Investigação com método: **números agregados primeiro, documentos só como evidência**. Com milhões de logs por
hora, ler documentos soltos engana; contagens agrupadas e comparadas com um período normal mostram onde está o
problema. As regras comuns (config por ambiente, fixos, apelidos, janela, Lucene, ambiente) estão no steering do
power.

Fora do escopo: não exporta (ofereça a **elk-exportar** no fim, se o usuário quiser os dados) e não configura.

## Antes de chamar

1. Identifique o ambiente (regra 6 do steering) e leia `.kiro/config/power/elk/elk-<ambiente>.json`. Sem ele →
   ofereça a **elk-setup** e pare. Este fluxo depende dos apelidos `nivel`, `servico`, `logger`, `excecao`,
   `stacktrace`, `mensagem`: os que faltarem, pule o passo e diga que a elk-setup pode completá-los.
2. **Janela do problema (J):** do relato ("às 10h" → 09:45–10:30 em Brasília, `-03:00`; "hoje" → `now/d`→`now`;
   sem horário → `now-1h`). **Referência (R):** mesma duração, mesmo horário do dia anterior (`-1d`) — o volume
   varia com o horário, então compare horários equivalentes. "Depois do deploy" → R = mesma duração antes do deploy.
3. Base de toda chamada: `indice`, `campo_tempo`, `campos` = `fixos` (+ recorte do relato, se houver). Campo
   mencionado que não está nos apelidos: aplique a regra 3.1 do steering (resolução via `elk_listar_campos`).

## Fluxo

Cada passo é um `elk_contar` (barato). Faça J e R lado a lado.

1. **Volume e severidade:** `agrupar_por=<nivel>` em J e em R. Taxa de erro = (ERROR [+ FATAL]) / total. Variação
   de total também é sinal: queda de volume = tráfego parou (indisponibilidade a montante); alta = carga ou laço.
2. **Onde concentra:** com `campos` + `{<nivel>: "ERROR"}`, `agrupar_por` em `servico`, depois `logger`, depois
   `excecao` (ou `host`, `uri`), `top=10`, em J e R. Procure o que é **novo** em J (ausente em R) ou cresceu muito
   mais que o resto — erro que existe igual em R é ruído de fundo, não a causa.
3. **Quando começou** (se o relato não diz): não há histograma no MCP. Fatie J em 4 partes iguais e conte o grupo
   suspeito em cada; refine a fatia onde ele salta, até ~5 min de precisão. Mais de 8 contagens → pare e use o que
   tem.
4. **Evidência:** `elk_buscar_logs` com o grupo suspeito, `limite=5` (no máximo 10: a amostra só ilustra o que as
   contagens já mostraram; ler dezenas de logs gasta contexto e não muda a conclusão), `retornar` = tempo + `nivel`, `servico`,
   `logger`, `excecao`, `stacktrace`, `mensagem`, `trace`, `mais_recentes=False` (os primeiros mostram o gatilho). A
   stack trace mostra onde o erro nasce: leia a causa raiz (`Caused by` mais interno) e o primeiro frame do código da
   aplicação, não dos frameworks. Se houver
   `trace`, uma busca por ele mostra a requisição inteira.
5. **Conclua** com o que os números sustentam. Faltou dado → diga qual consulta resolveria.

Use `consulta` Lucene só para texto em `mensagem` (`*timeout*`, `*Connection refused*`), e conte também esse texto
em R antes de chamá-lo de causa.

## Como responder

```markdown
## Diagnóstico — <sintoma> (<ambiente>, <J em Brasília>)

**Resumo:** <1–2 frases: o que aconteceu, onde, desde quando, hipótese principal>

| Métrica | Problema (J) | Referência (R) | Variação |
|---|---|---|---|
| Total de logs | ... | ... | ... |
| Erros (ERROR) | ... | ... | ... |
| Taxa de erro | ...% | ...% | ... p.p. |

**Onde concentra** (top em J, com R ao lado)

| Serviço / logger / exceção | J | R | Novo? |
|---|---|---|---|

**Linha do tempo:** <início estimado, pico, se já normalizou>

**Evidências:** 2–3 logs (`_id`, data/hora, mensagem curta) e a stack trace do primeiro, em bloco de código, cortada
na exceção, no `Caused by` mais interno e nos frames da aplicação

**Hipótese:** <causa provável e por que os números apontam para ela> · **Confiança:** alta/média/baixa

**Próximos passos:** <o que conferir fora do ELK (deploy, banco, integração), consultas para acompanhar>
```

- Números com separador de milhar; horários em Brasília.
- Diferencie fato (contagem) de hipótese. Sem diferença relevante entre J e R, diga isso: "nada anormal nos logs"
  é um resultado válido.
- Quantas chamadas foram feitas cabe numa linha final, para o usuário saber o custo.

## Erros

| Situação | O que fazer |
|---|---|
| `grupos` vazio em `agrupar_por` | Campo ausente no recorte ou texto: tente `.keyword` uma vez; senão pule o passo |
| R também com erro alto | O problema é crônico: diga isso e compare com uma R mais antiga (`-7d`) |
| Timeout/5xx em janela grande | Divida J ao meio; não tente janelas maiores |
| `Consulta vazia`, HTTP 400/401, ambiente | Mesmo tratamento da elk-logs |
