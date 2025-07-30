from enum import StrEnum
from typing import NewType

JobId = NewType("JobId", int)
"""The unique identifier of a job."""


class JobState(StrEnum):
    """Current state of a job."""

    PENDING = "pending"
    WAITING = "waiting"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMED_OUT = "timedOut"
    ERROR = "error"
    UNKNOWN = "unknown"
    OMITTED = "omitted"
    SKIPPED = "skipped"


END_STATES = {JobState.SUCCEEDED, JobState.CANCELLED, JobState.FAILED, JobState.TIMED_OUT, JobState.ERROR, JobState.UNKNOWN, JobState.OMITTED, JobState.SKIPPED}
