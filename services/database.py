import logging
from datetime import datetime
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

supabase: Client = None

def get_supabase() -> Client:
    global supabase
    if supabase is None:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def save_transaction(jenis: str, kategori: str, nominal: int, keterangan: str, raw_text: str) -> dict:
    try:
        client = get_supabase()
        data = {
            "jenis": jenis,
            "kategori": kategori,
            "nominal": nominal,
            "keterangan": keterangan,
            "raw_text": raw_text,
            "created_at": datetime.now().isoformat()
        }
        result = client.table("cash_flow").insert(data).execute()
        logger.info(f"Transaction saved: {result.data}")
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Database error: {e}")
        return {"success": False, "error": str(e)}

def get_transactions_by_date(date: str) -> list:
    try:
        client = get_supabase()
        result = client.table("cash_flow") \
            .select("*") \
            .gte("created_at", f"{date}T00:00:00") \
            .lte("created_at", f"{date}T23:59:59") \
            .execute()
        return result.data
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []

def get_transactions_by_week(start_date: str, end_date: str) -> list:
    try:
        client = get_supabase()
        result = client.table("cash_flow") \
            .select("*") \
            .gte("created_at", f"{start_date}T00:00:00") \
            .lte("created_at", f"{end_date}T23:59:59") \
            .execute()
        return result.data
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []

def get_all_transactions() -> list:
    try:
        client = get_supabase()
        result = client.table("cash_flow").select("*").execute()
        return result.data
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []