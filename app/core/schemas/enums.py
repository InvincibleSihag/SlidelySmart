from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    WAITING_FOR_INPUT = "waiting_for_input"  # HITL: Agent paused, waiting for human response
    COMPLETED = "completed"
    FAILED = "failed"
