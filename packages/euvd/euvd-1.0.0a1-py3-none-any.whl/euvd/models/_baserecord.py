"""
This module defines the base class for common record attributes.
"""

from typing import Set
import datetime

from pydantic import BaseModel, Field

from euvd.models.basescore import BaseScore


class _BaseRecord(BaseModel):
    """
    Base class for common record attributes.
    """
    description: str
    date_published: datetime.datetime
    date_updated: datetime.datetime
    base_score: BaseScore | None = None
    references: Set[str] = Field(default_factory=set)
    aliases: Set[str] = Field(default_factory=set)


__all__ = [
    '_BaseRecord',
]
