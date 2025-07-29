"""
This module defines the base class for ENISA ID references, providing a UUID-based identifier.
"""

import uuid
from pydantic import BaseModel


class _BaseEnisaIdReference(BaseModel):
    """
    Base class for ENISA references.
    """

    id: uuid.UUID

    class Config:
                json_encoders = {uuid.UUID: str}


__all__ = [
    '_BaseEnisaIdReference',
]
