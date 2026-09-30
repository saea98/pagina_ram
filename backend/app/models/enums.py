import enum

from sqlalchemy import Enum


class UserRole(enum.StrEnum):
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class MediaKind(enum.StrEnum):
    IMAGE = "image"
    AUDIO = "audio"
    FILE = "file"


class MediaVisibility(enum.StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class MediaStatus(enum.StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class PortfolioKind(enum.StrEnum):
    OWN_AUDIO = "own_audio"
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    BANDCAMP = "bandcamp"


class LeadStatus(enum.StrEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUOTED = "quoted"
    WON = "won"
    LOST = "lost"


class LeadEventType(enum.StrEnum):
    STATUS_CHANGE = "status_change"
    NOTE = "note"
    EMAIL_SENT = "email_sent"


class PlayEventType(enum.StrEnum):
    PLAY = "play"
    AB_TOGGLE = "ab_toggle"
    COMPLETE = "complete"


class JobType(enum.StrEnum):
    PROCESS_IMAGE = "process_image"
    PROCESS_AUDIO = "process_audio"
    SEND_EMAIL = "send_email"
    REVALIDATE = "revalidate"


class JobStatus(enum.StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


def pg_enum(enum_cls: type[enum.StrEnum], name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        length=32,
        values_callable=lambda members: [member.value for member in members],
    )


USER_ROLE = pg_enum(UserRole, "user_role")
MEDIA_KIND = pg_enum(MediaKind, "media_kind")
MEDIA_VISIBILITY = pg_enum(MediaVisibility, "media_visibility")
MEDIA_STATUS = pg_enum(MediaStatus, "media_status")
PORTFOLIO_KIND = pg_enum(PortfolioKind, "portfolio_kind")
LEAD_STATUS = pg_enum(LeadStatus, "lead_status")
LEAD_EVENT_TYPE = pg_enum(LeadEventType, "lead_event_type")
PLAY_EVENT_TYPE = pg_enum(PlayEventType, "play_event_type")
JOB_TYPE = pg_enum(JobType, "job_type")
JOB_STATUS = pg_enum(JobStatus, "job_status")
