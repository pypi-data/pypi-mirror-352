from enum import Enum

class TriggerType(Enum):
    MANUAL = 'MANUAL'
    SCHEDULE = 'SCHEDULE'
    SCRIPT = 'SCRIPT'

class ExecutionStatus(Enum):
    NOT_STARTED = 'NOT_STARTED'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'    
    TIMEOUT = 'TIMEOUT'

class LimitType(Enum):
    NEWEST = 'NEWEST' # meaning FIRST, TOP
    OLDEST = 'OLDEST' # meaning LAST, BOTTOM
