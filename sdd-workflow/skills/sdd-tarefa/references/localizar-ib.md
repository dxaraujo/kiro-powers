# Localizar a Task e o IB

Procedimento único para chegar do id informado pela pessoa (Task ou IB) à pasta do IB e aos dados do work item.
Usado pela `sdd-tarefa`, `sdd-status`, `sdd-retrabalho`, `sdd-testar` e `sdd-lote`. Vale para qualquer id:
número do ALM (`611`), id do planejamento (`T-03`, `IB-02`) ou número solto.

Pare no primeiro passo que achar. **Nunca invente dados do work item.**

## 1. Pasta do IB nas branches (sempre primeiro, com ou sem ALM)

O `status.md` registra as Tasks de todos os papéis e os ids do IB (ALM e planejamento), então o id da Task basta.

```bash
git fetch --quiet
# branch atual e worktrees
git grep -l -F -e '<id>' -- '.kiro/specs/*/status.md'
git worktree list            # repita o grep em cada worktree
# todas as branches remotas (prefixo sem curinga: "refs/remotes/origin/" casa tudo abaixo dele;
# não use "feature*" — o * do for-each-ref não atravessa a "/")
for b in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/ | grep -v '/HEAD$'); do
  git grep -l -F -e '<id>' "$b" -- '.kiro/specs/*/status.md'
done
```

- Confira o acerto lendo o `status.md` (`git show <branch>:<caminho>`): o id tem de estar na linha do IB, da
  linha **Planejamento** ou da tabela **Papéis** — não basta aparecer no Histórico.
- Achou → os dados vêm do `status.md` (IB, Tasks, papéis, fase, branch). Siga a skill que chamou (a `sdd-tarefa`
  pergunta se troca de branch).
- Mais de uma pasta → mostre as opções e pergunte.

## 2. Com o power `alm`

Skill **`alm-ccm`** com os ids de `.kiro/config/alm-power/pa_*.json`: o work item completo e o IB pai com as Tasks irmãs
(Passo 1 da `sdd-tarefa`). Leitura falhou (401, não encontrado) → informe a causa e pare.

## 3. Sem ALM → planejamento da `sdd-planejamento`

Fonte: `planejamento-agil/` na raiz do repositório (branch base: `git show origin/<base>:planejamento-agil/<arquivo>`
se não estiver na branch atual).

1. **`backlog.json`** — procure em `sprints[].ibs[]` o IB por `id` (`IB-02`) ou `alm_id`, e em `ibs[].tasks[]` a
   Task por `id` (`T-03`) ou `alm_id`. Extraia:
   - `task`: id, título, `tipo` (`ESPEC`, `BE`, `QA`, `BD`, `INF` → papel pela tabela **Work items** do
     `sdd-projeto.md`), responsável;
   - `ib`: id, título, prioridade, complexidade, sprint (`sprints[].numero`);
   - `irmas`: as demais Tasks do mesmo IB (id, tipo, responsável).
   Id só de IB → liste as Tasks dele e pergunte qual atender.
2. **Descrição e critérios do IB** → coluna *Escopo* da linha do `IB-XX` no `Backlog.md`. Sem critérios de aceite
   explícitos → pergunte só os critérios (o resto já veio do planejamento).
3. Responsável → `login` do membro em `equipe.json`.
4. Sem `backlog.json`, mas com `SPRINT N.md` → localize a linha `IB-XX - <título>` e, abaixo dela, a linha com o
   prefixo do papel (`[ESPEC]`, `[BE]`, `[QA]`); a Task fica identificada por `IB-XX` + papel.

Mostre o que achou numa linha (`Task T-03 [BE] — IB-02 <título> · Sprint 1 · fonte: planejamento`) e siga.

## 4. Nada encontrado

Peça à pessoa número, título, descrição e critérios do IB e das Tasks (comportamento sem fonte), e registre
o campo `ALM` do `status.md` pela regra do steering (`pendente — publicar com o power alm` ou `sem power — não
publicado`).

## Pasta e ids sem ALM

- Pasta: `.kiro/specs/ib-<XX>-<slug>/`, com `<XX>` = parte numérica do `IB-XX` (ex.: `IB-02` → `ib-02-<slug>`).
- `status.md`: preencha a linha **Planejamento** (`IB-02 · Sprint 1`) e use os ids `T-XX` na tabela **Papéis**.
  Publicado depois no ALM, a pasta não muda: acrescente o id do ALM na linha **IB** e nas Tasks — a busca do passo 1
  passa a achar pelos dois.
