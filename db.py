from supabase import create_client
import os

supabase_url = os.environ['SUPABASE_URL']
supabase_key = os.environ['SUPABASE_KEY']

supabase = create_client(supabase_url, supabase_key)
