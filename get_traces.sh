#!/bin/bash
TOKEN='glpat-svSZOdCok6F-ehMr_6uGm286MQp1OjI3dHkK.01.100xmmoy6'
for jid in 303824 303827 303828 303833 303837 303838; do
  echo "=== Job $jid ==="
  curl -s "https://code.swecha.org/api/v4/projects/70615/jobs/$jid/trace" -H "PRIVATE-TOKEN: $TOKEN" > /tmp/jobtrace_$jid.log
  python3 /tmp/parse_trace.py "$jid"
  echo ""
done
