"""
Syncs the SEED constant in index.html from data.json.
Run directly or via the git pre-commit hook.
"""
import json, re, sys
from pathlib import Path

def js_str(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")

def fmt_player(p):
    g = 'true' if p['gespielt'] else 'false'
    return f"{{name:'{js_str(p['name'])}',gespielt:{g},tore:{p['tore']},vorl:{p['vorl']}}}"

def fmt_match(m):
    sf = 'null' if m['sf01'] is None else str(m['sf01'])
    op = 'null' if m['opp'] is None else str(m['opp'])
    return f"{{gegner:'{js_str(m['gegner'])}',sf01:{sf},opp:{op}}}"

def fmt_tournament(t):
    excluded = t.get('excludedPlayers', [])
    excl_str = ','.join(f"'{js_str(e)}'" for e in excluded)
    players_str = ','.join(fmt_player(p) for p in t['players'])
    matches_str = ',\n        '.join(fmt_match(m) for m in t['matches'])
    return (
        f"    {{ date:'{js_str(t['date'])}', venue:'{js_str(t['venue'])}', "
        f"trikot:'{js_str(t.get('trikot', ''))}', excludedPlayers:[{excl_str}],\n"
        f"      players:[\n        {players_str}\n      ],\n"
        f"      matches:[\n        {matches_str}\n      ]\n    }}"
    )

root = Path(__file__).parent
data = json.loads((root / 'data.json').read_text(encoding='utf-8'))

hinrunde_str = ',\n'.join(fmt_tournament(t) for t in data['hinrunde'])
rueck = data.get('rueckrunde', [])
rueck_str = ('[\n' + ',\n'.join(fmt_tournament(t) for t in rueck) + '\n  ]') if rueck else '[]'

seed = f'const SEED = {{\n  hinrunde: [\n{hinrunde_str}\n  ],\n  rueckrunde: {rueck_str}\n}};'

html_path = root / 'index.html'
content = html_path.read_text(encoding='utf-8')
new_content = re.sub(r'const SEED = \{[\s\S]*?\n\};', seed, content)

if new_content == content:
    print('WARNING: SEED pattern not found in index.html — no changes made', file=sys.stderr)
    sys.exit(1)

html_path.write_text(new_content, encoding='utf-8')
print('SEED synced from data.json')
