"""Shared Supabase client — avoids circular imports between agents/ and orchestrator/."""
import os
import logging
from typing import Optional

from supabase import create_client, Client

logger = logging.getLogger(__name__)

_supabase: Optional[Client] = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set. "
                "On Railway, add them in Settings → Variables."
            )
        _supabase = create_client(url, key)
    return _supabase
