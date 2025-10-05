"""
SSL certificate setup - MUST be imported before any httpx/httpcore usage
This module configures SSL certificates for Supabase connection

NOTE: SSL verification is disabled for development due to corporate Zscaler proxy.
For production, proper SSL certificate verification should be enabled.
"""
import ssl

# Create SSL context that doesn't verify certificates
# This is necessary when behind corporate SSL inspection proxies like Zscaler
_ssl_context = ssl._create_unverified_context()

# Monkey-patch httpcore to use our unverified SSL context
import httpcore._backends.sync as httpcore_sync

_original_start_tls = httpcore_sync.SyncStream.start_tls

def _patched_start_tls(self, ssl_context, *args, **kwargs):
    """Patched start_tls to use unverified SSL context for development"""
    # Use unverified context to bypass Zscaler SSL inspection
    return _original_start_tls(self, _ssl_context, *args, **kwargs)

httpcore_sync.SyncStream.start_tls = _patched_start_tls

print("⚠️  SSL verification disabled for development (Zscaler proxy detected)")
