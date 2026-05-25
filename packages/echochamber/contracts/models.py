from pydantic import BaseModel
from typing import Optional, List


class Provenance(BaseModel):
    workspaceId: str
    artifactType: str
    sourceId: str
    correlationId: Optional[str] = None


class VoiceOptions(BaseModel):
    provider: Optional[str] = 'elevenlabs'
    voiceId: Optional[str] = None
    consentId: Optional[str] = None


class RequestOptions(BaseModel):
    includePhonetics: bool = False
    includeAudio: bool = False
    preserveFormatting: bool = True


class EchoChamberRequest(BaseModel):
    contractVersion: str
    sourceTool: str
    requestType: str
    sourceLanguage: str
    targetLanguage: str
    sourceText: str
    provenance: Provenance
    options: Optional[RequestOptions] = None
    voice: Optional[VoiceOptions] = None


class PronunciationChunk(BaseModel):
    text: str
    hint: str
    note: Optional[str] = None


class AudioArtifact(BaseModel):
    provider: str
    voiceId: Optional[str] = None
    artifactPath: Optional[str] = None


class TranslationArtifact(BaseModel):
    artifactId: str
    workspaceId: str
    createdAt: str


class EchoChamberResponse(BaseModel):
    contractVersion: str
    status: str
    translatedText: str
    targetLanguage: str
    phoneticHint: Optional[str] = None
    practiceChunks: Optional[List[PronunciationChunk]] = None
    audio: Optional[AudioArtifact] = None
    artifact: TranslationArtifact
