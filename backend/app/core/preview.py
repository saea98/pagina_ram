from contextvars import ContextVar

preview_active: ContextVar[bool] = ContextVar("preview_active", default=False)
