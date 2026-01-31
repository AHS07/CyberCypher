import os
from pathlib import Path
from dotenv import load_dotenv
import httpx

# Monkeypatch httpx.Client to accept 'proxy' argument (mapping to 'proxies')
# This fixes a compatibility issue between gotrue and this specific httpx environment
_original_init = httpx.Client.__init__

def _patched_init(self, *args, **kwargs):
    if "proxy" in kwargs and "proxies" not in kwargs:
        kwargs["proxies"] = kwargs.pop("proxy")
    _original_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_init

from supabase import create_client

# Load env from engine directory first, fallback to orchestrator
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    # Fallback to orchestrator .env if engine .env doesn't exist
    env_path = Path(__file__).parent.parent / "orchestrator" / ".env"
    
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Orchestrator API URL for triggering council analysis
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8003")

LEGACY_URL = "http://localhost:8001/checkout"
HEADLESS_URL = "http://localhost:8002/checkout"
BUGS_ENABLED = {
    "type_change": True,
    "missing_key": True,
    "case_mismatch": True,
    "performance_delay": False,
    "flaky": False
}

