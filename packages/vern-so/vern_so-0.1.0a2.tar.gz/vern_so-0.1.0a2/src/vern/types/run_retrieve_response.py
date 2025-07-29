# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["RunRetrieveResponse"]


class RunRetrieveResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the run"""

    completed_at: Optional[datetime] = None
    """Timestamp when the run completed"""

    created_at: Optional[datetime] = None
    """Timestamp when the run was created"""

    inputs: Optional[Dict[str, object]] = None
    """The inputs provided for the task"""

    response: Optional[Dict[str, object]] = None
    """The response data from the task execution"""

    started_at: Optional[datetime] = None
    """Timestamp when the run started executing"""

    status: Optional[Literal["queued", "running", "complete", "failed"]] = None
    """The current status of the run"""

    task: Optional[str] = None
    """The name of the task that was executed"""
