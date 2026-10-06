# Padrão — Casos de Teste (CT)

CSV de casos de teste — fonte da execução pelo testador (`sdd-testar`) e importável no ALM QM (o QM do power `alm`
é só leitura — a importação é manual). Fonte: cenários Gherkin da HF + REGs. Um CT por **comportamento testável**
(deduplicado).

## Arquivo

- `CT.csv` na pasta do IB · UTF-8 **com BOM** · quebras de linha **LF** · separador `;`
- Após gravar, garanta LF (`sed -i '' $'s/\r$//' CT.csv` no macOS, `sed -i 's/\r$//' CT.csv` no Linux) e o BOM.

## Colunas (nesta ordem)

Os valores de ALM vêm do `.kiro/config/alm-power/pa_*.json` e da Task; sem ALM, deixe vazios os que não souber.

| # | Coluna | Valor |
|---|---|---|
| 1 | Tipo | tipo de artefato de teste usado na importação do ALM (pergunte uma vez se não souber) |
| 2 | Resumo | `<Funcionalidade> : CT<nnn> - <Nome do caso>` |
| 3 | Responsável | valor exato do ALM |
| 4 | Status | estado inicial na importação (ex.: Em Testes) |
| 5 | Categoria | valor do ALM do projeto, se houver |
| 6 | Planejado para | valor exato do ALM (sprint) |
| 7 | Atendido por | valor exato do ALM (time) |
| 8 | Pontos de História | 0 pt |
| 9 | Criado Por | valor exato do ALM |
| 10 | Descrição | bloco abaixo, entre aspas duplas, com quebras de linha reais |

## Descrição

```
"OBJETIVO:
<o que o caso comprova> (Conforme cenário 1.2 da HF; REG-01)

PRÉ-CONDIÇÕES:
- <estado dos dados — gerado pelos scripts de massa do sdd-projeto.md quando existirem>

PASSOS:
1. <Disparar a funcionalidade: ação na tela, chamada da API, execução do processamento> com <entradas>
2. Consultar <tabela/resposta/log> pela <chave>

RESULTADO ESPERADO:
- <valor verificável no banco, na resposta ou no log>

MASSA DE TESTE SUGERIDA:
- <registros / identificadores / datas>"
```

- Dentro da Descrição **nunca** aspas duplas — use aspas simples ('Aprovado').
- Sem tags HTML; títulos em MAIÚSCULAS; listas com `-`.

## Cobertura e ordem

1. Caminho feliz (cria o estado usado pelos seguintes)
2. Variações válidas (FAs)
3. Casos que **não** devem ser processados/aceitos (filtros, permissões, validações)
4. Exceções (FEs): dado inválido, falha de integração
5. **Repetição / reexecução** (não duplica)
6. Limites (datas de corte, valores extremos)

Consolide em um CT o mesmo comportamento descrito em vários pontos da HF (`Conforme FE01 e cenário 3.1`).
Apresente a lista proposta (`CT001 - nome — fontes`) e gere o CSV completo após o "ok".
