import json
from pathlib import Path

p = Path('model222_ipyn.ipynb')
nb = json.loads(p.read_text(encoding='utf-8'))
changed = False
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        if cell.get('outputs'):
            cell['outputs'] = []
            changed = True
        if 'execution_count' in cell and cell['execution_count'] is not None:
            cell['execution_count'] = None
            changed = True
        # also remove large output attachments in metadata if present
        if 'attachments' in cell:
            cell.pop('attachments')
            changed = True

if changed:
    p.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding='utf-8')
    print('Notebook outputs cleared.')
else:
    print('No outputs found to clear.')
