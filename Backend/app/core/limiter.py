"""Shared rate-limit configuration used across all API routes."""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limit per client IP.  In-memory storage is fine for a single
# server; swap in a Redis backend later if you run multiple instances.
limiter = Limiter(key_func=get_remote_address)
