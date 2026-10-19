#!/usr/bin/env bash
set -euo pipefail

service="${SWARM_STACK:-devsecops-demo}_api"

wait_for_replicas() {
  local expected="$1"
  local replicas healthy
  for attempt in {1..60}; do
    replicas="$(docker service ls --filter "name=$service" --format '{{.Replicas}}')"
    healthy="$(docker ps --filter "label=com.docker.swarm.service.name=$service" --filter health=healthy --quiet | wc -l | tr -d '[:space:]')"
    if [ "$replicas" = "$expected/$expected" ] && [ "$healthy" = "$expected" ]; then
      echo "$service: $expected healthy replicas."
      return 0
    fi
    sleep 2
  done
  echo "Timed out waiting for $expected healthy replicas of $service." >&2
  return 1
}

check_http() {
  curl --fail --silent --show-error --max-time 5 http://127.0.0.1:8081/health \
    | python3 -c 'import json,sys; assert json.load(sys.stdin)["status"] == "ok"'
  curl --fail --silent --show-error --max-time 5 http://127.0.0.1:8081/ \
    | python3 -c 'import json,sys; assert json.load(sys.stdin)["service"] == "devsecops-swarm-demo"'
}

wait_for_replicas 2
check_http

docker service scale --detach "$service=3"
wait_for_replicas 3
check_http

timeout 180s docker service update --force --detach=false "$service"
update_state="$(docker service inspect --format '{{.UpdateStatus.State}}' "$service")"
if [ "$update_state" != completed ]; then
  echo "Rolling update did not complete successfully: $update_state" >&2
  exit 1
fi
wait_for_replicas 3
check_http

docker service scale --detach "$service=2"
wait_for_replicas 2
check_http
echo "Swarm smoke test passed: HTTP, scaling, healthchecks, and rolling restart."
