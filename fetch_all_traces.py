import urllib.request
import re
import sys

TOKEN = 'glpat-svSZOdCok6F-ehMr_6uGm286MQp1OjI3dHkK.01.100xmmoy6'
jobs = [(303824, 'lint-pylint'), (303827, 'lint-vulture'), (303828, 'json-syntax-validation'),
        (303833, 'python-typecheck'), (303837, 'secret-scanning'), (303838, 'secret-scanning-gitleaks')]

for jid, name in jobs:
    url = f'https://code.swecha.org/api/v4/projects/70615/jobs/{jid}/trace'
    req = urllib.request.Request(url, headers={'PRIVATE-TOKEN': TOKEN})
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'Error fetching {jid} ({name}): {e}', file=sys.stderr)
        continue

    content = re.sub(r'\x1b\[[0-9;]*[mK]', '', content)
    content = re.sub(r'section_start:[0-9]+.*?\n', '', content)
    content = re.sub(r'section_end:[0-9]+.*?\n', '', content)
    lines = [l for l in content.split('\n') if l.strip()]

    print(f'\n{"="*60}')
    print(f'=== {name} (job {jid}) ===')
    print(f'{"="*60}')
    for l in lines[-50:]:
        print(l)
