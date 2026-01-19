"""
Supabase client for database operations
"""

from supabase import create_client, Client
from api.config import settings
import structlog

logger = structlog.get_logger()


class SupabaseClient:
    """Supabase client wrapper"""

    def __init__(self):
        self.client: Client = None

    def connect(self):
        """Initialize Supabase connection"""
        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY,  # Use service key for server-side
            )
            logger.info("Supabase connected successfully")
        except Exception as e:
            logger.error("Failed to connect to Supabase", error=str(e))
            raise

    def get_client(self) -> Client:
        """Get Supabase client instance"""
        if not self.client:
            self.connect()
        return self.client


# Global Supabase client instance
supabase_client = SupabaseClient()
