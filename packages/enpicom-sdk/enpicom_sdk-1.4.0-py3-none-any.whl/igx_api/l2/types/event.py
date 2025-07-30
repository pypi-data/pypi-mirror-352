from datetime import datetime

from pydantic import BaseModel

from igx_api.l2.types.organization import OrganizationId
from igx_api.l2.types.user import UserId
from igx_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class JobPayload(BaseModel):
    """The payload of a JobEvent."""

    kind: str
    """The type of job."""
    state: str
    """The state of the job."""
    job_id: int
    """The ID of the job."""
    category: str
    """The category of the job."""
    config_id: int
    """The ID of the job configuration."""


class WorkflowExecutionTaskPayload(BaseModel):
    """The payload of a WorkflowExecutionEvent."""

    id: WorkflowExecutionTaskId
    """The ID of the workflow execution task."""
    workflow_execution_id: WorkflowExecutionId
    """The ID of the workflow execution."""
    task_template_name: WorkflowTaskTemplateName
    """The name of the job template."""
    state: str
    """The state of the workflow execution."""


class Event(BaseModel):
    """A single event body representing a single action that has happened in the Platform."""

    timestamp: datetime
    """The timestamp when the event was fired."""
    organization_id: OrganizationId
    """The organization that the event belongs to."""
    user_id: UserId | None
    """The user that the event belongs to, if any."""
    category: str
    """The category of the event."""
    action: str
    """The action that was performed."""
    payload: dict[str, int | float | bool | str | None] | JobPayload | WorkflowExecutionTaskPayload
    """The payload of the event.

    The contents of the payload are specific to the event category and action, and may contain more detailed information
    about the event that occurred.
    """
