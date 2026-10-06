# Padrão — Regra de Negócio (REG)

Uma REG por regra: seleção, validação, cálculo, transição de situação, temporal. A REG é **tecnologia-neutra**
(não cita classe, componente ou framework); tabelas e campos podem ser citados em "Dados envolvidos".

## Estrutura

```markdown
# REG - <Nome da regra>

**Task:** <id> · **Categoria:** <Seleção | Validação | Cálculo | Situação | Temporal | Integração>

## Descrição

<O que a regra garante e por que existe, em 2–4 frases.>

## Condições de Aplicação

**Aplica-se quando:**
- <condição>

**Não se aplica quando:**
- <exceção>

## Lógica

**SE** <condição>
**E** <condição>
**ENTÃO** <resultado>
**SENÃO** <resultado alternativo>

<!-- Várias combinações → tabela -->
| Condição | Resultado |
|---|---|
| <situação A> | <resultado A> |

## Dados Envolvidos

| Tabela | Campo | Uso |
|---|---|---|
| <TABELA> | <CAMPO> | <lido / gravado — significado> |

## Ocorrências e Logs

| Código | Texto | Quando |
|---|---|---|
| <motivo/ocorrência> | "<texto gravado>" | <condição> |

## Referências

- HF · REG-<nn> relacionadas

---
Versão: 1.0 | Data/Hora: <DD/MM/AAAA HH:MM> | Status: <rascunho | aprovado | publicado>
Artefato produzido com uso de IA generativa — Fluxo SDD

| Data/Hora | Alteração |
|---|---|
| <DD/MM/AAAA HH:MM> | Versão inicial |
```

## Regras

- **SE/ENTÃO/SENÃO/E/OU** em negrito; valores de domínio em negrito; tabelas em MAIÚSCULAS.
- Valores de código de domínio (situação, motivo, indicadores) **confirmados no código ou no banco**
  — informe o valor e o significado (ex.: `SITUACAO = 3` → **Aprovado**).
- Regra que já existe no sistema e não muda → não gere REG nova; cite-a na HF.
- Nome do arquivo: `REG-<nn>-<slug>.md` com `nn` sequencial na Task (01, 02…).
