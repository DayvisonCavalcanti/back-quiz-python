from supabase import create_client
from config import settings
import logging

logger = logging.getLogger(__name__)

def get_supabase():
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase connection established successfully")
        return supabase
    except Exception as e:
        logger.error(f"Error connecting to Supabase: {str(e)}")
        raise

# Instância global do cliente Supabase
supabase = get_supabase()