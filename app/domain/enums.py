import enum


class UserTypeEnum(str, enum.Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    DEVOPS = "devops"
    QA = "qa"
    PM = "pm"


class EnvironmentEnum(str, enum.Enum):
    CI = "ci"
    CD = "cd"
    DEV = "development"
    STAGE = "staging"
    PROD = "production"


class UrgencyEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BugStatusEnum(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    RESOLVED = "resolved"


class RecordStatusEnum(str, enum.Enum):
    DELETED = "deleted"
    ACTIVE = "active"
