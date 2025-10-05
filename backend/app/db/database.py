"""
Supabase database client configuration
"""
# Import SSL setup FIRST - before any httpx/supabase imports
import app.ssl_setup  # noqa: F401

from supabase import create_client, Client
from app.core.config import settings

# Supabase clients - SSL configured via ssl_setup module
# Note: Timeout is handled at the httpx level in ssl_setup
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def get_db() -> Client:
    """Get Supabase client instance"""
    return supabase


def get_admin_db() -> Client:
    """Get Supabase admin client instance"""
    return supabase_admin
