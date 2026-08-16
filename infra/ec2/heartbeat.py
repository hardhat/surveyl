#!/usr/bin/env python3
"""Pings Supabase to keep the free-tier project from auto-pausing due to inactivity."""
import sys
import urllib.error
import urllib.request

ENV_FILE = "/etc/surveyle/surveyle.env"


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def main():
    env = load_env(ENV_FILE)
    url = env["SUPABASE_URL"].rstrip("/")
    key = env["SUPABASE_SERVICE_ROLE_KEY"]

    req = urllib.request.Request(
        f"{url}/rest/v1/admins?select=user_id&limit=1",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"heartbeat ok: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"heartbeat failed: HTTP {e.code} {e.reason} - {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"heartbeat failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
