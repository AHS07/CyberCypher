# 🚀 Quick Setup Guide - Shadow Twin Guardian

Follow these steps in order to get the system running.

---

## Step 1: Get Supabase Credentials (2 minutes)

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project (or create new one)
3. Navigate to: **Settings** → **API**
4. Copy these values:

   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: Starts with `eyJh...`
   - **service_role key**: Starts with `eyJh...` (different from anon)

---

## Step 2: Update Environment Files

### Backend: `orchestrator/.env`

```bash
SUPABASE_URL=https://xxxxx.supabase.co          # Paste Project URL
SUPABASE_ANON_KEY=eyJh...                        # Paste anon key
SUPABASE_SERVICE_KEY=eyJh...                     # Paste service_role key

# Add your LLM API keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

### Frontend: `dashboard/.env.local`

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co   # Same Project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJh...                # Same anon key
NEXT_PUBLIC_API_URL=http://localhost:8000            # Leave as-is
```

> ⚠️ **IMPORTANT**: `SUPABASE_URL` must be identical in both files!

---

## Step 3: Run Database Migrations (3 minutes)

1. Go to Supabase Dashboard → **SQL Editor**
2. Click **New Query**
3. Copy and run each migration file:

   **Migration 1:** `shared/migrations/001_create_shadow_tests.sql`
   
   **Migration 2:** `shared/migrations/002_create_reliability_logs.sql`
   
   **Migration 3:** `shared/migrations/003_create_checkpoints.sql`

4. Verify tables exist: **Database** → **Tables**
   - ✅ `shadow_tests`
   - ✅ `reliability_logs`
   - ✅ `checkpoints`

---

## Step 4: Enable Realtime (1 minute)

1. Go to: **Database** → **Replication**
2. Find table: `shadow_tests`
3. Toggle **ON** for:
   - ✅ Enable Insert
   - ✅ Enable Update
4. Click **Save**

---

## Step 5: Run Smoke Test (30 seconds)

```bash
cd orchestrator
pip install supabase python-dotenv  # First time only
python test_connection.py
```

**Expected output:**
```
✓ Connected to Supabase successfully
✓ Table 'shadow_tests' exists
✓ Mock test inserted with ID: smoke_test_...
✓ All smoke tests passed!
```

❌ **If you see errors:**
- Check `.env` file has correct values
- Verify migrations ran successfully
- Check table names are lowercase

---

## Step 6: Test Real-Time Connection (30 seconds)

```bash
python test_realtime.py
```

This will:
1. Insert a test record
2. Update it 3 times (pending → analyzing → complete)
3. You should see these updates LIVE in the dashboard

---

## Step 7: Start the System

### Option A: One Command (Recommended)

```bash
# From project root
./start.sh
```

### Option B: Manual Start

**Terminal 1 - Orchestrator:**
```bash
cd orchestrator
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Dashboard:**
```bash
cd dashboard
npm run dev
```

---

## Step 8: Verify Everything Works

1. **Check Orchestrator**: http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

2. **Check Dashboard**: http://localhost:3000
   - Should see Shadow Twin Guardian UI

3. **Send Test Request**:
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H 'Content-Type: application/json' \
     -d @test_payload.json
   ```

4. **Watch Dashboard**:
   - Test appears in Real-Time Feed
   - Agent Trace nodes light up
   - Council opinions appear
   - Final verdict shows

---

## Troubleshooting

### "All Providers Down"
- Add your Anthropic and Google API keys to `orchestrator/.env`
- Or start Ollama: `ollama serve`

### "Stale Signal" Warning
- Check realtime is enabled (Step 4)
- Verify orchestrator is running

### No Real-Time Updates
- Check browser console for errors
- Verify both `.env` files have same `SUPABASE_URL`
- Check realtime replication is enabled

### Import Errors
```bash
cd orchestrator
pip install -r requirements.txt
```

---

## ✅ You're Done!

The system is now running. Your team can:
- Clone the repo
- Update `.env` files with their own keys
- Run the same setup steps
- Start building!

**Next**: Integrate with Aayush's API layer and test end-to-end with real merchant data.
