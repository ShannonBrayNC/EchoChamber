import pytest
from services.store.ops_store import OpsStore, EmailEventRecord, ArtifactRecord, WorkspaceRequiredError


def test_workspace_required():
    store = OpsStore(":memory:")
    with pytest.raises(WorkspaceRequiredError):
        store.upsert_email_event(EmailEventRecord(
            workspace_id="",
            message_id="1",
            subject="Test"
        ))


def test_idempotent_email_event():
    store = OpsStore(":memory:")

    record = EmailEventRecord(
        workspace_id="ws1",
        message_id="msg1",
        subject="Hello"
    )

    store.upsert_email_event(record)
    store.upsert_email_event(record)

    with store.connect() as conn:
        rows = conn.execute("SELECT * FROM EmailEvent").fetchall()
        assert len(rows) == 1


def test_artifact_insert():
    store = OpsStore(":memory:")

    artifact = ArtifactRecord(
        workspace_id="ws1",
        artifact_type="Runway",
        artifact_key="daily",
        content_json="{}",
        evidence_refs_json="[]"
    )

    store.upsert_artifact(artifact)

    results = store.list_artifacts("ws1")
    assert len(results) == 1
