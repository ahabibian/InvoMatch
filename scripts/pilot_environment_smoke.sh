#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: $0 https://pilot.example.com [expected-commit-sha] [cookie-jar]" >&2
  exit 2
}

[ "$#" -ge 1 ] && [ "$#" -le 3 ] || usage

base_url=${1%/}
expected_sha=${2:-}
cookie_jar=${3:-}

case "$base_url" in
  https://*) ;;
  *) echo "Smoke target must use HTTPS." >&2; exit 2 ;;
esac

host=${base_url#https://}
host=${host%%/*}
host=${host%%:*}
case "$host" in
  ""|localhost|127.*|::1) echo "Smoke target must use the configured pilot hostname." >&2; exit 2 ;;
esac

request_status() {
  expected=$1
  path=$2
  actual=$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' \
    --connect-timeout 10 --max-time 30 "$base_url$path")
  [ "$actual" = "$expected" ] || {
    echo "$path returned HTTP $actual; expected $expected." >&2
    exit 1
  }
}

# curl performs normal certificate-chain and hostname verification by default.
request_status 200 /
request_status 200 /health
request_status 200 /readiness
request_status 401 /api/auth/session

if [ -n "$cookie_jar" ]; then
  [ -r "$cookie_jar" ] || { echo "Cookie jar is not readable: $cookie_jar" >&2; exit 2; }
  command -v jq >/dev/null 2>&1 || { echo "jq is required for release identity verification." >&2; exit 2; }
  [ -n "$expected_sha" ] || { echo "Expected SHA is required with a cookie jar." >&2; exit 2; }
  identity=$(curl --fail --silent --show-error --cookie "$cookie_jar" \
    --connect-timeout 10 --max-time 30 "$base_url/api/operations/release-identity")
  printf '%s' "$identity" | jq --exit-status --arg sha "$expected_sha" \
    '.git_commit_sha == $sha and .git_branch == "main" and .environment == "production" and .validation_status == "controlled_pilot"' \
    >/dev/null
  echo "Authenticated release identity matches $expected_sha."
else
  echo "Public HTTPS, health, readiness, and authentication-boundary checks passed."
  [ -z "$expected_sha" ] || echo "Release identity was not checked because no authenticated cookie jar was supplied."
fi
