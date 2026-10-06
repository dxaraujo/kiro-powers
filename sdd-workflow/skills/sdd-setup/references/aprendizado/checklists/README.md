# Checklists pré-voo

Um arquivo por skill (`sdd-especificar.md`, `sdd-validar-requisitos.md`, `sdd-criar-spec.md`, `sdd-implementar-spec.md`,
`sdd-revisar.md`), criado na primeira
ocorrência e lido pela skill no início da execução. Alimentado por:

- `sdd-retrabalho` — só entradas de **causa raiz** (as induzidas não entram);
- `sdd-validar-requisitos` — achados BLOQUEANTES antes do GATE 1 (vão para `sdd-especificar.md`).

São lembretes **temporários**:

```markdown
- [ ] <achado> — ocorrências: <N> (Task <a>, Task <b>) — desde <AAAA-MM-DD> — última: <AAAA-MM-DD>
```

- 3 ocorrências em Tasks distintas → a `sdd-retrabalho` propõe **promoção** (vira regra em **Regras promovidas** do `sdd-projeto.md` ou num
  steering do projeto) e o item **sai** daqui.
- 10 Tasks registradas sem reincidência → o item expira e sai.
- Checklist crescendo sem parar = promoções não estão sendo feitas.
