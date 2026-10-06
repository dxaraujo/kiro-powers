#!/usr/bin/env python3
"""md_to_excel.py — Converte os .md do planejamento ágil em Excel com formatação e fórmulas.

Uso:
    python md_to_excel.py <dir_md> "<nome do arquivo de saída>" [opções]

Opções:
    --inicio DD/MM/AAAA        início da primeira sprint (habilita datas no Gantt)
    --semanas-por-sprint N     duração da sprint em semanas (padrão: 2)
    --hoje DD/MM/AAAA          data de referência para destacar a semana corrente

Sem --inicio, a aba Gantt sai com as colunas de semana vazias ("a definir") —
o script nunca inventa datas.
"""
import os, re, sys
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Console do Windows costuma vir em cp1252 — garante que ✓ não quebre a execução
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ─── Estilos ────────────────────────────────────────────────────────────────────
HEADER_FONT_WHITE = Font(bold=True, size=11, color='FFFFFF')
HEADER_FILL = PatternFill('solid', fgColor='1F4E79')
SECTION_FILL = PatternFill('solid', fgColor='2E75B6')
SECTION_FONT = Font(bold=True, size=10, color='FFFFFF')
IB_FONT = Font(bold=True, size=10)
IB_FILL = PatternFill('solid', fgColor='D6E4F0')
TASK_FONT = Font(size=10)
OK_FILL = PatternFill('solid', fgColor='C6EFCE')
OK_FONT = Font(bold=True, color='006100')
METRIC_FILL = PatternFill('solid', fgColor='FFF2CC')
METRIC_HEADER_FILL = PatternFill('solid', fgColor='BF8F00')
METRIC_HEADER_FONT = Font(bold=True, size=10, color='FFFFFF')
RETRO_HEADER_FILL = PatternFill('solid', fgColor='FCE4D6')
RETRO_HEADER_FONT = Font(bold=True, size=10)
GANTT_FILL = PatternFill('solid', fgColor='C6EFCE')
THIN_BORDER = Border(
    left=Side('thin'), right=Side('thin'),
    top=Side('thin'), bottom=Side('thin')
)


# ─── Parser ─────────────────────────────────────────────────────────────────────
def parse_md_file(filepath):
    """Parse um arquivo .md em seções estruturadas."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = []
    current_section = {'title': None, 'rows': []}

    for line in content.strip().split('\n'):
        ls = line.strip()
        if not ls or ls == '---':
            continue
        if ls.startswith('# ') and not ls.startswith('## ') and not ls.startswith('### '):
            continue
        if ls.startswith('## '):
            continue
        if ls.startswith('### ') or ls.startswith('#### '):
            if current_section['rows']:
                sections.append(current_section)
            current_section = {'title': ls.lstrip('# ').strip(), 'rows': []}
            continue
        if ls.startswith('|') and re.match(r'^\|[\s:\-|]+\|?$', ls):
            continue
        if ls.startswith('|'):
            raw_cells = ls.split('|')[1:-1]
            # Preserve leading spaces on first cell (for indentation), strip the rest
            cells = []
            for i, c in enumerate(raw_cells):
                if i == 0:
                    cells.append(c.rstrip())  # Keep leading spaces, strip trailing
                else:
                    cells.append(c.strip())
            current_section['rows'].append(cells)
            continue
        if re.match(r'^\d+\.', ls):
            text = re.sub(r'^\d+\.\s*', '', ls)
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            current_section['rows'].append([text])
            continue

    if current_section['rows']:
        sections.append(current_section)
    return sections


# ─── Helpers ────────────────────────────────────────────────────────────────────
TASK_PREFIXES = ('[BE]', '[FE]', '[BD]', '[QA]', '[INF]', '[DOC]', '[ESPEC]', '⚡ [QA]')


def is_number(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def detect_row_type(row, in_retro_block=False):
    """Detecta o tipo de uma linha para formatação."""
    if not row:
        return 'normal'
    raw_first = row[0] if row[0] else ''
    first = raw_first.strip()
    joined = ' '.join(row)

    if in_retro_block:
        if 'O QUE FOI BOM' in joined:
            return 'retro_header'
        return 'retro_data'

    if 'RETROSPECTIVA' in joined:
        return 'retro_start'
    if 'O QUE FOI BOM' in joined:
        return 'retro_header'

    # Métricas section header
    if first == 'Métricas' or first == '**Métricas**':
        return 'metric_header'

    # Débitos Técnicos header (format like IB)
    if 'Débitos Técnicos' in first or 'Débitos Técnicos' in joined:
        return 'ib'

    first_clean = first.lstrip()
    if any(first_clean.startswith(p) for p in TASK_PREFIXES):
        return 'task'
    # Lines with 2+ leading spaces in markdown = indented = task
    if raw_first.startswith('  ') and first:
        return 'task'

    if '**' in joined:
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', first)
        if re.search(r'\bIB-\d+', cleaned):
            return 'ib'
        if first.startswith('**') and first.endswith('**'):
            return 'ib'
        # "Débitos pendentes" or similar bold group headers
        if '**' in first:
            return 'ib'

    metric_keys = ['Horas Produtivas', 'Pontos Planejados', 'Pontos Entregues',
                   'Velocidade Sprint', 'Velocidade Média', 'Capacidade da Equipe', 'Total']
    if any(k in joined for k in metric_keys):
        return 'metric'

    return 'normal'


# ─── Escrita ────────────────────────────────────────────────────────────────────
def write_section(ws, section, start_row, sheet_context):
    """Escreve uma seção completa."""
    row_idx = start_row

    if section['title']:
        max_cols = max((len(r) for r in section['rows']), default=3)
        for col in range(1, max_cols + 1):
            cell = ws.cell(row=row_idx, column=col)
            cell.fill = SECTION_FILL
            cell.border = THIN_BORDER
        ws.cell(row=row_idx, column=1, value=section['title']).font = SECTION_FONT
        row_idx += 1

    if section['rows']:
        first_row = section['rows'][0]
        first_joined = ' '.join(first_row).lower()
        header_keywords = ['sprint', 'ib', 'item', 'membro', 'parâmetro', 'nº', '#',
                          'cenário', 'critério', 'artefato', 'task', 'funcionalidade',
                          'entrega', 'débitos', 'review', 'observações']
        is_header = (section['title'] is not None and
                     any(k in first_joined for k in header_keywords) and
                     all(not is_number(c.replace('**', '').strip()) for c in first_row) and
                     'OK' not in ' '.join(first_row))

        if is_header:
            for c_idx, val in enumerate(first_row):
                cell = ws.cell(row=row_idx, column=c_idx + 1)
                cell.value = re.sub(r'\*\*(.*?)\*\*', r'\1', val).strip()
                cell.font = HEADER_FONT_WHITE
                cell.fill = HEADER_FILL
                cell.border = THIN_BORDER
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            row_idx += 1
            data_rows = section['rows'][1:]
        else:
            data_rows = section['rows']
    else:
        data_rows = []

    in_retro = False
    for row in data_rows:
        row_type = detect_row_type(row, in_retro_block=in_retro)
        if row_type == 'retro_start':
            in_retro = True
            row_type = 'retro_header'

        for c_idx, cell_val in enumerate(row):
            cell = ws.cell(row=row_idx, column=c_idx + 1)
            val = re.sub(r'\*\*(.*?)\*\*', r'\1', cell_val).strip()
            if val == 'nan':
                val = ''
            if is_number(val):
                val = float(val)
                if val == int(val):
                    val = int(val)

            cell.value = val
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical='center', wrap_text=True)

            if row_type == 'ib':
                cell.font = IB_FONT
                cell.fill = IB_FILL
            elif row_type == 'task':
                cell.font = TASK_FONT
                if c_idx == 0 and isinstance(val, str):
                    cell.alignment = Alignment(indent=2, vertical='center', wrap_text=True)
            elif row_type == 'metric_header':
                cell.font = METRIC_HEADER_FONT
                cell.fill = METRIC_HEADER_FILL
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif row_type == 'metric':
                cell.fill = METRIC_FILL
                cell.font = Font(size=10, bold=any(k in str(val) for k in ['Total', 'Pontos', 'Velocidade', 'Capacidade', 'Horas']))
            elif row_type in ('retro_start', 'retro_header'):
                cell.font = RETRO_HEADER_FONT
                cell.fill = RETRO_HEADER_FILL
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            elif row_type == 'retro_data':
                cell.font = TASK_FONT
            else:
                cell.font = TASK_FONT

            if str(val).strip() == 'OK':
                cell.fill = OK_FILL
                cell.font = OK_FONT
                cell.alignment = Alignment(horizontal='center', vertical='center')

        row_idx += 1

    return row_idx


# ─── Formatação especial por aba ────────────────────────────────────────────────
def post_format_sprint(ws):
    """Formata linha 1 como header e linha 'Métricas' como destaque."""
    # Linha 1 = header com destaque
    max_col = ws.max_column
    for col in range(1, max_col + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = HEADER_FONT_WHITE
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)


def post_format_planejamento(ws):
    """Alinha grupo Parâmetros (coluna B) à direita, coluna E (h/semana) à direita, e Roadmap A/C/D/E ao centro."""
    max_row = ws.max_row
    in_roadmap = False
    for row in range(1, max_row + 1):
        a_val = str(ws.cell(row=row, column=1).value or '')

        # Coluna E (h/semana) na seção Equipe: alinhar à direita
        cell_e = ws.cell(row=row, column=5)
        if cell_e.value is not None and cell_e.fill != HEADER_FILL and cell_e.fill != SECTION_FILL:
            val_e = str(cell_e.value)
            if val_e.isdigit() or 'indisponível' in val_e.lower() or val_e == '0 (indisponível)':
                cell_e.alignment = Alignment(horizontal='right', vertical='center')

        # Parâmetros section: align B to right
        if any(k in a_val for k in ['Total de IBs', 'Total de Pontos', 'Sprints', 'Duração',
                                     'Capacidade/Sprint', 'Capacidade estimada', 'Escala', 'Máximo por IB']):
            cell_b = ws.cell(row=row, column=2)
            cell_b.alignment = Alignment(horizontal='right', vertical='center')

        # Detect start of Roadmap section
        if 'Roadmap' in a_val:
            in_roadmap = True
            continue

        # Roadmap rows: align columns A, C, D, E to center
        if in_roadmap:
            cell_a = ws.cell(row=row, column=1)
            if cell_a.value is not None and cell_a.fill != HEADER_FILL:
                cell_a.alignment = Alignment(horizontal='center', vertical='center')
            for col in [3, 4, 5]:
                cell = ws.cell(row=row, column=col)
                if cell.value is not None:
                    cell.alignment = Alignment(horizontal='center', vertical='center')


def post_format_entregas(ws):
    """Formata linha 1 como header, centraliza coluna A (números e funcionalidades) e colunas C/D/E."""
    max_col = ws.max_column
    # Linha 1 header
    for col in range(1, max_col + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = HEADER_FONT_WHITE
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # Coluna A: centralizar linhas com números ou funcionalidades
    for row in range(2, ws.max_row + 1):
        cell_a = ws.cell(row=row, column=1)
        if cell_a.fill != SECTION_FILL and cell_a.fill != HEADER_FILL:
            val = cell_a.value
            if val is not None:
                cell_a.alignment = Alignment(horizontal='center', vertical='center')

    # Colunas C, D e E ao centro
    for row in range(2, ws.max_row + 1):
        for col in [3, 4, 5]:
            cell = ws.cell(row=row, column=col)
            if cell.value and cell.fill != SECTION_FILL and cell.fill != HEADER_FILL:
                cell.alignment = Alignment(horizontal='center', vertical='center')


def post_format_backlog(ws):
    """Alinha coluna A (IB-XX) ao centro e colunas C, D, E ao centro."""
    for row in range(1, ws.max_row + 1):
        # Coluna A: centralizar se contém IB-XX
        cell_a = ws.cell(row=row, column=1)
        val_a = str(cell_a.value or '').strip()
        if re.match(r'^IB-\d+$', val_a) and cell_a.fill != HEADER_FILL and cell_a.fill != SECTION_FILL:
            cell_a.alignment = Alignment(horizontal='center', vertical='center')
        # Colunas C+ ao centro
        for col in range(3, ws.max_column + 1):
            cell = ws.cell(row=row, column=col)
            if cell.fill != HEADER_FILL and cell.fill != SECTION_FILL:
                cell.alignment = Alignment(horizontal='center', vertical='center')


def post_format_conceito(ws):
    """Alinha tudo à esquerda, exceto coluna A na seção 'Definição de Feito por Task' (centralizada)."""
    for row in range(1, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            cell = ws.cell(row=row, column=col)
            if cell.fill != SECTION_FILL and cell.fill != HEADER_FILL:
                cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # Centralizar coluna A nas linhas de tasks (que começam com [ESPEC], [BE], etc.)
    task_labels = ['[ESPEC]', '[BE]', '[FE]', '[BD]', '[QA]', '[INF]', '[DOC]']
    for row in range(1, ws.max_row + 1):
        val = str(ws.cell(row=row, column=1).value or '').strip()
        if val in task_labels:
            ws.cell(row=row, column=1).alignment = Alignment(horizontal='center', vertical='center')


# ─── Fórmulas ───────────────────────────────────────────────────────────────────
def _formula_feito_ib(ws, first, last):
    """Linha do IB fica OK quando todas as suas tasks nesta sprint estão OK."""
    ib_row = None
    for r in range(first, last + 2):
        val = str(ws.cell(row=r, column=1).value or '').strip() if r <= last else ''
        if ib_row and not re.search(r'\[[A-Z]+\]', val):
            if r - 1 > ib_row:
                ws.cell(row=ib_row, column=3,
                    value=f'=IF(COUNTIF(C{ib_row+1}:C{r-1},"OK")={r-1-ib_row},"OK","")')
            ib_row = None
        if val.startswith('IB-'):
            ib_row = r


def add_sprint_formulas(ws, sprint_sheets, current_idx):
    """Adiciona fórmulas nas sprint sheets."""
    max_row = ws.max_row
    items_start = None
    items_end = None
    total_row = None
    pontos_entreg_row = None
    vel_sprint_row = None
    vel_media_row = None

    for row in range(1, max_row + 1):
        val = str(ws.cell(row=row, column=1).value or '').strip()

        if items_start is None and 'IB-' in val:
            items_start = row
        if items_start and items_end is None:
            if 'Débitos' in val or 'Horas Produtivas' in val or val == 'Métricas':
                items_end = row - 1
                _formula_feito_ib(ws, items_start, items_end)

        if val == 'Total':
            total_row = row
            start = row - 1
            while start > 0:
                above = str(ws.cell(row=start, column=1).value or '').strip()
                if 'Horas Produtivas' in above:
                    break
                start -= 1
            start += 1
            if start < row:
                ws.cell(row=row, column=2, value=f"=SUM(B{start}:B{row-1})")

        elif 'Pontos Entregues' in val:
            pontos_entreg_row = row
            if items_start and items_end and items_end > items_start:
                ws.cell(row=row, column=2,
                    value=f'=SUMPRODUCT((B{items_start}:B{items_end}<>"")*1,(C{items_start}:C{items_end}="OK")*1,B{items_start}:B{items_end})')
            else:
                # Sprint sem IB: não deixar o placeholder "=fórmula" virar fórmula inválida
                ws.cell(row=row, column=2, value='')

        elif 'Velocidade Sprint' in val:
            vel_sprint_row = row
            if not (items_start and items_end and items_end > items_start):
                # Sprint sem IB (setup/homologação) fica fora da Velocidade Média
                ws.cell(row=row, column=2, value='')
            elif pontos_entreg_row and total_row:
                # "" enquanto nenhuma task tem OK: sprint futura não entra no AVERAGE como 0
                ws.cell(row=row, column=2,
                    value=f'=IF(COUNTIF(C{items_start}:C{items_end},"OK")=0,"",'
                          f'IFERROR(ROUND(B{pontos_entreg_row}/B{total_row},4),"-"))')

        elif 'Velocidade Média' in val:
            vel_media_row = row
            refs = []
            for prev_name in sprint_sheets[:current_idx + 1]:
                prev_ws = ws.parent[prev_name]
                for r in range(1, prev_ws.max_row + 1):
                    if 'Velocidade Sprint' in str(prev_ws.cell(row=r, column=1).value or ''):
                        refs.append(f"'{prev_name}'!B{r}")
                        break
            if refs:
                ws.cell(row=row, column=2, value=f'=IFERROR(ROUND(AVERAGE({",".join(refs)}),4),"-")')

        elif 'Capacidade da Equipe' in val:
            if vel_media_row and total_row:
                ws.cell(row=row, column=2, value=f'=IFERROR(ROUND(B{total_row}*B{vel_media_row},2),"-")')


# ─── Gantt ──────────────────────────────────────────────────────────────────────
CURRENT_WEEK_FILL = PatternFill('solid', fgColor='FF6B35')
CURRENT_WEEK_FONT = Font(size=9, bold=True, color='FFFFFF')


def parse_marcos_gantt(md_dir):
    """Lê Gantt.md (opcional) e devolve {nome_da_sprint: marco}.

    Formato esperado (qualquer tabela com as colunas Sprint e Marco):

        | Sprint   | Marco                        |
        |----------|------------------------------|
        | SPRINT 2 | Marco 1 — Cadastro completo  |
    """
    path = os.path.join(md_dir, 'Gantt.md')
    marcos = {}
    if not os.path.exists(path):
        return marcos
    for section in parse_md_file(path):
        rows = section['rows']
        if not rows:
            continue
        header = [re.sub(r'\*\*', '', c).strip().lower() for c in rows[0]]
        if 'sprint' not in header:
            continue
        col_sprint = header.index('sprint')
        col_marco = header.index('marco') if 'marco' in header else 1
        for row in rows[1:]:
            if len(row) <= max(col_sprint, col_marco):
                continue
            sprint = re.sub(r'\*\*', '', row[col_sprint]).strip()
            marco = re.sub(r'\*\*', '', row[col_marco]).strip()
            if sprint and marco and marco not in ('-', '—'):
                marcos[sprint.upper()] = marco
    return marcos


def create_gantt_sheet(wb, sprint_sheets, marcos=None, inicio=None,
                       semanas_por_sprint=2, hoje=None):
    """Cria a aba Gantt: uma linha por sprint, uma coluna por semana da sprint.

    - `inicio` (datetime) — início da primeira sprint da lista. Se ausente, as
      colunas de semana ficam vazias ("a definir"), sem inventar datas.
    - `semanas_por_sprint` — duração da sprint em semanas (padrão 2).
    - `hoje` (datetime) — usada para destacar a semana corrente (padrão: data de hoje).
    - `marcos` — {nome_da_sprint: marco} vindo de Gantt.md, quando existir.
    """
    from datetime import timedelta

    marcos = {k.upper(): v for k, v in (marcos or {}).items()}
    hoje = hoje or datetime.now()
    ws = wb.create_sheet(title="Gantt")

    headers = ['Sprint']
    for s in range(1, semanas_por_sprint + 1):
        headers.append(f'Semana {s}' if inicio else f'Semana {s} (a definir)')
    headers.append('Marco')

    for c_idx, h in enumerate(headers):
        cell = ws.cell(row=1, column=c_idx + 1, value=h)
        cell.font = HEADER_FONT_WHITE
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    for idx, sn in enumerate(sprint_sheets):
        row = idx + 2
        cell_sprint = ws.cell(row=row, column=1, value=sn)
        cell_sprint.border = THIN_BORDER
        cell_sprint.font = Font(size=10, bold=True)

        for s in range(semanas_por_sprint):
            col = 2 + s
            cell = ws.cell(row=row, column=col)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if inicio:
                ini = inicio + timedelta(weeks=idx * semanas_por_sprint + s)
                fim = ini + timedelta(days=6)
                cell.value = f"{ini.strftime('%d/%m')} a {fim.strftime('%d/%m')}"
                cell.fill = GANTT_FILL
                cell.font = Font(size=9, bold=True)
                if ini <= hoje <= fim:
                    cell.fill = CURRENT_WEEK_FILL
                    cell.font = CURRENT_WEEK_FONT

        marco_cell = ws.cell(row=row, column=2 + semanas_por_sprint,
                             value=marcos.get(sn.upper(), ''))
        marco_cell.border = THIN_BORDER
        if marco_cell.value:
            marco_cell.font = Font(size=10, bold=True)
            marco_cell.fill = GANTT_FILL

    ws.column_dimensions['A'].width = 22
    for c in range(2, 2 + semanas_por_sprint):
        ws.column_dimensions[get_column_letter(c)].width = 20
    ws.column_dimensions[get_column_letter(2 + semanas_por_sprint)].width = 40

    ws.freeze_panes = 'A2'


# ─── Main ───────────────────────────────────────────────────────────────────────
def create_excel(md_dir, output_path, inicio=None, semanas_por_sprint=2, hoje=None):
    wb = Workbook()
    wb.remove(wb.active)

    order = ['Planejamento Ágil', 'Conceito de Pronto', 'Entregas', 'Backlog']
    md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]

    def sort_key(f):
        name = f.replace('.md', '')
        if name in order:
            return (0, order.index(name))
        m = re.search(r'\d+', name)
        if name.startswith('SPRINT'):
            return (1, int(m.group()) if m else 99)
        if name == 'Homologação':
            return (2, 0)
        return (4, 0)

    md_files.sort(key=sort_key)
    sprint_sheets = []

    for md_file in md_files:
        if md_file == 'Gantt.md':
            continue

        sheet_name = md_file.replace('.md', '')[:31]
        ws = wb.create_sheet(title=sheet_name)

        context = 'normal'
        if sheet_name == 'Backlog':
            context = 'backlog'
        elif sheet_name.startswith('Conceito'):
            context = 'conceito'

        filepath = os.path.join(md_dir, md_file)
        sections = parse_md_file(filepath)

        current_row = 1
        for section in sections:
            if section['rows']:
                current_row = write_section(ws, section, current_row, context)

        # Column widths
        for col in range(1, ws.max_column + 1):
            max_len = 10
            for row in range(1, ws.max_row + 1):
                val = ws.cell(row=row, column=col).value
                if val:
                    max_len = max(max_len, min(len(str(val)), 60))
            ws.column_dimensions[get_column_letter(col)].width = max_len + 3
        if ws.max_column >= 1:
            ws.column_dimensions['A'].width = 75

        # Post-formatting
        if context == 'backlog':
            post_format_backlog(ws)
        elif context == 'conceito':
            post_format_conceito(ws)
        elif sheet_name == 'Planejamento Ágil':
            post_format_planejamento(ws)
        elif sheet_name == 'Entregas':
            post_format_entregas(ws)

        if sheet_name.startswith('SPRINT'):
            sprint_sheets.append(sheet_name)
            post_format_sprint(ws)
        elif sheet_name == 'Homologação':
            # Centralizar coluna A nas linhas de pré-requisitos (números 1-7)
            for row in range(1, ws.max_row + 1):
                val = ws.cell(row=row, column=1).value
                if val is not None and isinstance(val, (int, float)):
                    ws.cell(row=row, column=1).alignment = Alignment(horizontal='center', vertical='center')

    # Formulas
    for idx, sn in enumerate(sprint_sheets):
        add_sprint_formulas(wb[sn], sprint_sheets, idx)

    # Freeze sprint sheets
    for sn in sprint_sheets:
        wb[sn].freeze_panes = 'A2'

    # Gantt — construído a partir das sprints e (opcionalmente) de Gantt.md
    create_gantt_sheet(wb, sprint_sheets,
                       marcos=parse_marcos_gantt(md_dir),
                       inicio=inicio,
                       semanas_por_sprint=semanas_por_sprint,
                       hoje=hoje)
    # Move Gantt para a posição 2 (logo após Planejamento Ágil)
    gantt_ws = wb['Gantt']
    wb.move_sheet(gantt_ws, offset=-(len(wb.sheetnames) - 2))

    wb.save(output_path)
    print(f"✓ Planilha gerada: {output_path}")


def _parse_data(valor, rotulo):
    if not valor:
        return None
    try:
        return datetime.strptime(valor, '%d/%m/%Y')
    except ValueError:
        print(f"✗ {rotulo} inválida: '{valor}' — use o formato DD/MM/AAAA")
        sys.exit(1)


if __name__ == '__main__':
    argv = sys.argv[1:]
    opcoes = {}
    posicionais = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg.startswith('--'):
            chave = arg[2:]
            valor = argv[i + 1] if i + 1 < len(argv) else ''
            opcoes[chave] = valor
            i += 2
        else:
            posicionais.append(arg)
            i += 1

    md_dir = posicionais[0] if posicionais else '.'
    project = posicionais[1] if len(posicionais) > 1 else 'Projeto'

    create_excel(
        md_dir,
        os.path.join(md_dir, f'{project}.xlsx'),
        inicio=_parse_data(opcoes.get('inicio'), '--inicio'),
        semanas_por_sprint=int(opcoes.get('semanas-por-sprint', 2)),
        hoje=_parse_data(opcoes.get('hoje'), '--hoje'),
    )
