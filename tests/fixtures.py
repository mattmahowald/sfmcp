from __future__ import annotations
import pytest

@pytest.fixture(scope="session")
def env_setup(monkeypatch: pytest.MonkeyPatch):
    # Provide dummy env so settings load; replace with real values in dev
    monkeypatch.setenv("SF_INSTANCE_URL", "https://example.my.salesforce.com")
    monkeypatch.setenv("SF_ACCESS_TOKEN", "REPLACE_ME")
    return True
