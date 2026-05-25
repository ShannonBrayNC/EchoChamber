from packages.echochamber.artifacts.service import ArtifactService


def test_artifact_workspace_isolation(tmp_path, monkeypatch):
    monkeypatch.setenv('ECHOCHAMBER_STORAGE_ROOT', str(tmp_path))

    service = ArtifactService()

    artifact = service.save_translation_artifact(
        workspace_id='workspace-a',
        source_tool='manual',
        source_text='hello',
        translated_text='cześć'
    )

    loaded = service.get_artifact(
        artifact['artifactId'],
        'workspace-a'
    )

    assert loaded['workspaceId'] == 'workspace-a'
