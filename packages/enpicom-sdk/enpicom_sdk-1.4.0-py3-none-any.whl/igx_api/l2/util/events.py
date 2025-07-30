from loguru import logger

from igx_api.l2.types.event import Event
from igx_api.l2.types.job import JobId, JobState


def job_is_finished(event: Event, job_id: JobId) -> bool:
    if event.payload:
        running_job_id = dict(event.payload).get("job_id")
        state = str(dict(event.payload).get("state")).lower()
        if running_job_id == job_id and (state == JobState.SUCCEEDED or state == JobState.FAILED):
            logger.info(f"Job {job_id} finished with state: {state}")
            return True
    return False
