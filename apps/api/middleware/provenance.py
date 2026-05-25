from fastapi import HTTPException


REQUIRED_PROVENANCE_FIELDS = [
    'workspaceId',
    'artifactType',
    'sourceId'
]


class ProvenanceGuard:

    @staticmethod
    def validate(payload):
        provenance = payload.provenance

        for field in REQUIRED_PROVENANCE_FIELDS:
            value = getattr(provenance, field, None)

            if not value:
                raise HTTPException(
                    status_code=400,
                    detail=f'Missing provenance field: {field}'
                )
