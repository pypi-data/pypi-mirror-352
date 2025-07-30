import contextvars

servers_v = contextvars.ContextVar("server")
rules_v = contextvars.ContextVar("rules")
dist_file_v = contextvars.ContextVar("dist_file")
