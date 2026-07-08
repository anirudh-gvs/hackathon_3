#!/bin/bash
TOKEN='glpat-svSZOdCok6F-ehMr_6uGm286MQp1OjI3dHkK.01.100xmmoy6'
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
  sleep 5
  curl -s "https://code.swecha.org/api/v4/projects/70615/pipelines/79206/jobs" -H "PRIVATE-TOKEN: $TOKEN" -o /tmp/pipe_jobs.json
  echo "=== Check $i ==="
  python3 << 'PYEOF'
import json
jobs = json.load(open('/tmp/pipe_jobs.json'))
for jj in sorted(jobs, key=lambda x: x['id']):
    s = jj['status']
    if s == 'failed':
        print("  %-35s FAILED (%s)" % (jj['name'], jj.get('failure_reason','')))
    elif s == 'success':
        print("  %-35s passed" % jj['name'])
    else:
        print("  %-35s %s" % (jj['name'], s))
PYEOF
  all_done=$(python3 -c "import json; j=json.load(open('/tmp/pipe_jobs.json')); print(all(jj['status'] in ('success','failed') for jj in j))")
  if [ "$all_done" = "True" ]; then
    echo "ALL JOBS COMPLETE"
    break
  fi
done
echo DONE
