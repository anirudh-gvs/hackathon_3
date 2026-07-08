import re
import sys

jid = sys.argv[1]
t = open(f'/tmp/jobtrace_{jid}.log').read()
t = re.sub(r'\x1b\[[0-9;]*[mK]', '', t)
t = re.sub(r'section_start:[0-9]+.*?\n', '', t)
t = re.sub(r'section_end:[0-9]+.*?\n', '', t)
lines = [l for l in t.split('\n') if l.strip()]
for l in lines[-60:]:
    print(l)
