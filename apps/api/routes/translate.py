from fastapi import APIRouter
from packages.echochamber.contracts.models import EchoChamberRequest
from packages.echochamber.translation.service import TranslationService
from packages.echochamber.artifacts.service import ArtifactService
from apps.api.middleware.provenance import ProvenanceGuard
from apps.api.middleware.workspace_guard import WorkspaceGuard

router = APIRouter()

translation_service = TranslationService()
artifact_service = ArtifactService()


@router.post('/translate')
def translate(payload: EchoChamberRequest):
    ProvenanceGuard.validate(payload)

    WorkspaceGuard.validate_workspace(
        payload.provenance.workspaceId
    )

    translated = translation_service.translate(
        payload.sourceText,
        payload.sourceLanguage,
        payload.targetLanguage
    )

    artifact = artifact_service.save_translation_artifact(
        workspace_id=payload.provenance.workspaceId,
        source_tool=payload.sourceTool,
        source_text=payload.sourceText,
        translated_text=translated
    )

    return {
        'contractVersion': payload.contractVersion,
        'status': 'success',
        'translatedText': translated,
        'targetLanguage': payload.targetLanguage,
        'artifact': artifact
    }
