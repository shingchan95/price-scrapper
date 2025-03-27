import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url: str = os.environ['SUPABASE_URL']
supabase_key: str = os.environ['SUPABASE_KEY']
supabase: Client = create_client(supabase_url, supabase_key)
