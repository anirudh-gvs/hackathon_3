#!/bin/bash
TOKEN="glpat-svSZOdCok6F-ehMr_6uGm286MQp1OjI3dHkK.01.100xmmoy6"
for jid in 303824 303827 303828 303833; do
  case $jid in
    303824) jname="lint-pylint" ;;
    303827) jname="lint-vulture" ;;
    303828) jname="json-syntax-validation" ;;
    303833) jname="python-typecheck" ;;
  esac
  echo "=== Job $jid - $jname ==="
  curl -s "https://code.swecha.org/api/v4/projects/70615/jobs/$jid" -H "PRIVATE-TOKEN: $TOKEN" -o /tmp/job_$jid.json
  python3 -c "import json; d=json.load(open('/tmp/job_$jid.json')); print('Status: '+d['status']); print('Duration: '+str(d.get('duration',''))+'s'); print('Failure reason: '+str(d.get('failure_reason','')))"
  echo ""
done
