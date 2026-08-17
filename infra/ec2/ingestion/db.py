"""Thin PostgREST client for the EC2 ingestion pipeline, authenticated with the
service-role key (bypasses RLS, same convention as heartbeat.py's ENV_FILE loading).
"""
import os

import requests

ENV_FILE = "/etc/surveyle/surveyle.env"


def load_env(path=ENV_FILE):
    env = dict(os.environ)
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


class SupabaseClient:
    """Minimal PostgREST wrapper: enough for select/insert/update used by ingestion."""

    def __init__(self, url, service_role_key):
        self.base_url = url.rstrip("/") + "/rest/v1"
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_env(cls, env=None):
        env = env or load_env()
        return cls(env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"])

    def select(self, table, params=None):
        resp = requests.get(f"{self.base_url}/{table}", headers=self.headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def insert(self, table, rows, on_conflict=None):
        headers = {**self.headers, "Prefer": "return=representation"}
        params = {"on_conflict": on_conflict} if on_conflict else None
        resp = requests.post(
            f"{self.base_url}/{table}", headers=headers, params=params, json=rows, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def update(self, table, params, patch):
        headers = {**self.headers, "Prefer": "return=representation"}
        resp = requests.patch(
            f"{self.base_url}/{table}", headers=headers, params=params, json=patch, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def delete(self, table, params):
        resp = requests.delete(f"{self.base_url}/{table}", headers=self.headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.content else None
