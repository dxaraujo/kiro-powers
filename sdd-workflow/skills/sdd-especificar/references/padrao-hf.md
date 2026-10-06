# Padrão — História Funcional (HF)

A HF descreve o **comportamento da funcionalidade** em termos de negócio: quem dispara, o que entra, o que
acontece e o que sai. O ator é quem de fato usa a funcionalidade — usuário de uma tela, cliente de uma API,
operador ou agendador de um processamento, sistema parceiro. Regras detalhadas ficam nas REGs; dados, interfaces e
queries, na ET.

## Estrutura

```markdown
# HF - <Nome da funcionalidade>

**Task:** <id> · **IB:** <id> — <título> · **Funcionalidade:** `<nome>` (nova | alterada)

## Narrativa

**Como** <ator>,
**Eu quero** <o que a funcionalidade faz>,
**Para** <benefício de negócio>.

## Gatilho e entradas

- **Disparo:** <ação do usuário | chamada de API | agendamento | evento de outro sistema>
- **Entradas:** <campos, parâmetros, arquivo… ou "nenhuma">
- **Pré-condições:** <estado necessário antes>

## Fluxo Principal

1. <O ator / o sistema …>
2. <Para cada registro / a cada requisição, …>
3. <Grava / atualiza / responde / gera …>
4. <Registra log / auditoria / ocorrência>

**Fluxos Alternativos:**
FA01: <variação válida — ex.: registro já processado é ignorado>

**Fluxos de Exceção:**
FE01: <erro de dado / permissão / integração — o que acontece com a operação (rejeita, registra, desfaz, aborta)>

## Critérios de Aceite

### 1. <Contexto — ex.: Seleção dos registros>

1.1 <Título do cenário>

**Dado que** <estado antes — dados, situação, permissões, datas>
**E** <condição adicional>
**Quando** <o ator dispara a funcionalidade com X>
**Então** <efeito verificável — dado gravado, resposta, mensagem>
**E** <efeito adicional>
**Conforme** REG-01

---

1.2 …

## Reexecução e volume

- **Reexecução / repetição:** <repetir a operação é seguro? o que impede duplicar — chave, situação, idempotência>
- **Volume esperado:** <ordem de grandeza, se conhecida>

## Regras de Negócio Aplicáveis

| Regra | Descrição |
|---|---|
| REG-01 | <resumo> |

## Dúvidas Pendentes

1. <dúvida que o código, o banco e a Task não responderam>

---
Versão: 1.0 | Data/Hora: <DD/MM/AAAA HH:MM> | Status: <rascunho | aprovado | publicado>
Artefato produzido com uso de IA generativa — Fluxo SDD

| Data/Hora | Alteração |
|---|---|
| <DD/MM/AAAA HH:MM> | Versão inicial |
```

## Regras

- Cenários Gherkin numerados por contexto (1.1, 1.2, 2.1…), separados por `---`.
- **Então** é sempre verificável (valor gravado, resposta, mensagem, contagem) — nada de "corretamente".
- Todo fluxo alternativo e de exceção tem ao menos um cenário.
- Cobrir sempre: caminho feliz, caso que **não** deve ser processado/aceito, repetição/reexecução, erro em um item
  (a operação continua? o que é registrado?).
- Valores de domínio em negrito (**Aprovado**, **Pendente**); nomes de campo entre aspas.
- Mais de ~15 cenários ou mais de uma funcionalidade → proponha dividir em duas HFs antes de gerar.
- Caracteres `<` e `>` no texto são convertidos pela publicação; não use entidades HTML no Markdown.
