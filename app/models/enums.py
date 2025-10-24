import enum


class SessionStatus(str, enum.Enum):
    disconnected = "disconnected"
    qr = "qr"
    connected = "connected"


class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"
