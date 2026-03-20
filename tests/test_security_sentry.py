import json

from services.store.ops_store import OpsStore, ArtifactRecord
from services.agents.verifiers.security_sentry import SecuritySentry


def test_workspace_validation():
    sentry = SecuritySentry()

    result = sentry.run("")
    assert result["passed"] is False


def test_artifact_requires_evidence():
    store = OpsStore(":memory:")

    # Insert invalid artifact (no evidence)
    store.upsert_artifact(
        ArtifactRecord(
            workspace_id="ws1",
            artifact_type="Runway",
            artifact_key="bad",
            content_json=json.dumps({}),
            evidence_refs_json=json.dumps([]),
        )
    )

    sentry = SecuritySentry(store)
    result = sentry.run("ws1")

    assert result["passed"] is False


def test_forbidden_actions_blocked():
    sentry = SecuritySentry()

    result = sentry.run("ws1", requested_actions=["send_email"])
    assert result["passed"] is False
