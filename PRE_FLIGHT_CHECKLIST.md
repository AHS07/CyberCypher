# 🔍 Pre-Flight Checklist - Shadow Twin Guardian

Before running the system, complete these **mandatory** verification steps.

## 1. ✅ Environment Variables Check

### Backend (Orchestrator)

Create `/orchestrator/.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# LLM Provider API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=sk-your-openai-key  # Optional

# Ollama (Local Fallback)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Orchestrator
ORCHESTRATOR_HOST=0.0.0.0
ORCHESTRATOR_PORT=8000
```

### Frontend (Dashboard)

Create `/dashboard/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

> **CRITICAL**: The Supabase URL must be **identical** in both files!

---

## 2. 🗄️ Database Setup

### Run SQL Migrations

1. Go to Supabase Dashboard → SQL Editor
2. Run each migration in order:

**Migration 1: shadow_tests table**
```bash
# Copy contents from: shared/migrations/001_create_shadow_tests.sql
```

**Migration 2: reliability_logs table**
```bash
# Copy contents from: shared/migrations/002_create_reliability_logs.sql
```

**Migration 3: checkpoints table**
```bash
# Copy contents from: shared/migrations/003_create_checkpoints.sql
```

### Verify Tables

Go to Supabase Dashboard → Table Editor

You should see:
- ✅ `shadow_tests` (with indexes)
- ✅ `reliability_logs`
- ✅ `checkpoints`

### Enable Realtime

1. Go to Database → Replication
2. Find `shadow_tests` table
3. Toggle **Enable Insert** and **Enable Update**

---

## 3. 🧪 Smoke Test

Run the smoke test to verify everything is connected:

```bash
cd orchestrator
python test_connection.py
```

**Expected Output:**
```
✓ Supabase URL: https://...
✓ Service Key: ********************...
✓ Connected to Supabase successfully
✓ Table 'shadow_tests' exists and is accessible
✓ Table 'reliability_logs' exists and is accessible
✓ Table 'checkpoints' exists and is accessible
✓ Mock test inserted with ID: smoke_test_20260131_210324
✓ Mock data retrieved successfully
✓ All smoke tests passed!
```

If you see errors, **STOP** and fix them before proceeding.

---

## 4. 🚀 Start the System

### Terminal 1: Orchestrator

```bash
cd orchestrator
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Visit http://localhost:8000/health
Should return: `{"status": "healthy"}`

### Terminal 2: Dashboard

```bash
cd dashboard
npm run dev
```

**Verify**: Visit http://localhost:3000
Should see the Shadow Twin Guardian dashboard.

---

## 5. 🧪 End-to-End Test

### Option A: Via API (Recommended)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d @test_payload.json
```

### Option B: Via Python

```python
import requests

response = requests.post(
    'http://localhost:8000/api/analyze',
    json={
        "test_id": "e2e_test_001",
        "merchant_id": "Test_Merchant",
        "legacy_response": {"price": 100},
        "headless_response": {"price": "100"},
        "diff_report": {"type_changes": {"root['price']": {"old_type": "int", "new_type": "str"}}}
    }
)
print(response.json())
```

### Expected Behavior:

1. **Dashboard Feed**: Test appears with status "pending" → "analyzing"
2. **Agent Trace**: Nodes light up as agents deliberate
3. **Council Opinions**: Opinions appear in right panel
4. **Final Verdict**: Shows PASS/FAIL/NEEDS_REVIEW

---

## 6. 🔧 Troubleshooting

### "All Providers Down"

- Verify API keys in `.env`
- Check Anthropic/Google API key limits
- Start Ollama: `ollama serve`

### "Stale Signal" Warning

- Check orchestrator is running
- Verify Supabase realtime is enabled

### Dashboard Not Updating

- Open browser DevTools → Console
- Check for errors
- Verify `NEXT_PUBLIC_SUPABASE_URL` matches backend

### Table Not Found

- Run migrations again
- Check table names are lowercase: `shadow_tests` (not `ShadowTests`)

---

## ✅ Sign-Off Checklist

Before pushing to production:

- [ ] All environment variables set correctly
- [ ] Database migrations applied
- [ ] Smoke test passes
- [ ] Orchestrator starts without errors
- [ ] Dashboard loads successfully
- [ ] End-to-end test completes
- [ ] Real-time updates work
- [ ] Agent trace visualizes correctly
- [ ] Mitigation gate activates on high-risk

**Once all items checked, you're ready to deploy! 🚀**
