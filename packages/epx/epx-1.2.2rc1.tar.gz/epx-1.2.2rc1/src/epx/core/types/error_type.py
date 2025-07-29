from pydantic import BaseModel


class ForbiddenResponse(BaseModel):
    """Response object for a 403 Forbidden response from the SRS."""

    description: str


class NotFoundResponse(BaseModel):
    """Response object for a 404 NotFound response from the SRS."""

    description: str


class BadRequestResponse(BaseModel):
    """Response object for a 400 BadRequest response from the SRS."""

    description: str
