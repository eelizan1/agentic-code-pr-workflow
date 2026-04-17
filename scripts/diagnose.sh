#!/usr/bin/env bash
# Diagnose why `python main.py` fails with APIConnectionError in this shell.
# Run from the project root:  bash scripts/diagnose.sh

set +e

echo "=== 1. Which python? ==="
which python
python --version 2>&1
echo "VIRTUAL_ENV=${VIRTUAL_ENV:-(unset)}"
echo

echo "=== 2. Proxy / Anthropic env vars in this shell ==="
env | grep -Ei '^(http_proxy|https_proxy|all_proxy|no_proxy|anthropic_base_url|ssl_cert_file|requests_ca_bundle|curl_ca_bundle)=' \
  || echo "(none set)"
echo

echo "=== 3. Can langchain_anthropic import? ==="
python -c "import langchain_anthropic, anthropic, httpx; print('anthropic', anthropic.__version__); print('httpx', httpx.__version__)" 2>&1
echo

echo "=== 4. DNS for api.anthropic.com ==="
host api.anthropic.com 2>&1 || dscacheutil -q host -a name api.anthropic.com 2>&1
echo

echo "=== 5. curl reachability (expect HTTP 401 without API key) ==="
curl -sS -o /dev/null -w "HTTP %{http_code}  DNS %{time_namelookup}s  connect %{time_connect}s  total %{time_total}s\n" \
  https://api.anthropic.com/v1/models -H "anthropic-version: 2023-06-01" --max-time 15
echo

echo "=== 6. httpx reachability from THIS python ==="
python - <<'PY' 2>&1
import os, httpx
try:
    r = httpx.get(
        "https://api.anthropic.com/v1/models",
        headers={"anthropic-version": "2023-06-01"},
        timeout=15,
    )
    print(f"httpx OK  status={r.status_code}")
except Exception as e:
    print(f"httpx FAILED  {type(e).__name__}: {e}")
    cause = getattr(e, "__cause__", None) or getattr(e, "__context__", None)
    if cause:
        print(f"  cause: {type(cause).__name__}: {cause}")
PY
