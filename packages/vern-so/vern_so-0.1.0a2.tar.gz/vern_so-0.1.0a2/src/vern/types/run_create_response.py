# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["RunCreateResponse"]


class RunCreateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the run"""

    inputs: Optional[Dict[str, object]] = None
    """The inputs provided for the task"""

    queued_at: Optional[datetime] = None
    """Timestamp when the run was queued"""
