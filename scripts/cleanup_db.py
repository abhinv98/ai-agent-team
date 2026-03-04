"""Delete all tasks, activity, and knowledge data. Keep agent_costs intact."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_KEY"]
db = create_client(url, key)

tables = ["tasks", "agent_activity", "agent_knowledge", "research_findings", "ad_library_snapshots"]

for table in tables:
    try:
        db.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"Cleared: {table}")
    except Exception as e:
        print(f"Error clearing {table}: {e}")

print("\nDone. agent_costs data preserved.")
