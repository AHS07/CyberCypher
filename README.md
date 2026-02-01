# Shadow Twin Guardian

A sophisticated multi-agent AI system for e-commerce migration parity testing. The system uses a council of specialized AI agents powered by HuggingFace models to analyze API differences and provide intelligent deployment recommendations with human oversight capabilities.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Shadow Engine │───▶│   Orchestrator   │───▶│   Dashboard     │
│   (Port 8001/2)│    │   (Port 8005)    │    │   (Port 3000)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────▼────────┐             │
         │              │ Multi-Agent     │             │
         │              │ Council:        │             │
         │              │ • Primary       │             │
         │              │ • Skeptic       │             │
         │              │ • Judge         │             │
         │              └─────────────────┘             │
         │                       │                       │
         └───────────────────────▼───────────────────────┘
                        Supabase Database
                     (Real-time Updates)
```

## 📁 Project Structure

```
CyberCypher/
├── engine/                   # Shadow replay testing engine
│   ├── shadow_engine.py     # Main shadow testing logic
│   ├── server_legacy.py     # Legacy API simulator (port 8001)
│   ├── server_headless.py   # Headless API simulator (port 8002)
│   ├── config.py           # Configuration and bug simulation
│   └── utils.py            # Utility functions
├── orchestrator/            # Multi-agent orchestration system
│   ├── app/
│   │   ├── agents/         # AI agent implementations
│   │   │   ├── primary_analyzer.py    # Technical analysis agent
│   │   │   ├── skeptic_critic.py      # False positive detection
│   │   │   └── consensus_judge.py     # Final decision making
│   │   ├── api/            # FastAPI routes
│   │   ├── core/           # Core services
│   │   │   ├── config.py   # Configuration management
│   │   │   ├── hf_manager.py # HuggingFace API manager
│   │   │   └── llm_manager.py # LLM provider management
│   │   ├── graph/          # Multi-agent workflow
│   │   └── models/         # Pydantic schemas
│   └── requirements.txt
├── dashboard/              # Next.js real-time dashboard
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   │   ├── agent-trace.tsx        # Agent workflow visualization
│   │   ├── mitigation-gate.tsx    # Human oversight controls
│   │   ├── parity-visualizer.tsx  # API diff comparison
│   │   ├── real-time-feed.tsx     # Live test monitoring
│   │   └── reliability-badge.tsx  # System health status
│   └── lib/               # Supabase client & utilities
├── shared/                # Shared resources
│   ├── migrations/        # Database schema
│   └── types/            # Type definitions
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Supabase Project**: Create at [supabase.com](https://supabase.com)
- **HuggingFace Token**: Get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Setup

1. **Clone and Install Dependencies**
   ```bash
   # Install dashboard dependencies
   cd dashboard
   npm install
   cd ..
   
   # Setup Python environment
   cd engine
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   pip install -r ../orchestrator/requirements.txt
   cd ..
   ```

2. **Configure Environment**
   ```bash
   # Copy example environment files
   cp .env.example .env
   
   # Edit configuration files with your actual values:
   # - orchestrator/.env: Supabase URL, keys, HF token
   # - dashboard/.env.local: API URLs, Supabase config
   # - engine/.env: Supabase credentials
   ```

3. **Setup Database**
   
   In your Supabase dashboard, run the SQL migrations:
   ```sql
   -- Run these in order:
   -- shared/migrations/001_create_shadow_tests.sql
   -- shared/migrations/002_create_reliability_logs.sql  
   -- shared/migrations/003_create_checkpoints.sql
   ```

4. **Start All Services**
   ```bash
   # Terminal 1: Start Legacy API (port 8001)
   cd engine
   venv\Scripts\activate
   python server_legacy.py
   
   # Terminal 2: Start Headless API (port 8002)  
   cd engine
   venv\Scripts\activate
   python server_headless.py
   
   # Terminal 3: Start Orchestrator (port 8005)
   cd orchestrator
   ..\engine\venv\Scripts\activate
   set PYTHONPATH=D:\git\CyberCypher\orchestrator
   python -m uvicorn app.main:app --host localhost --port 8005
   
   # Terminal 4: Start Dashboard (port 3000)
   cd dashboard
   npm run dev
   ```

5. **Access the System**
   - **Dashboard**: http://localhost:3000
   - **API Docs**: http://localhost:8005/docs
   - **Health Check**: http://localhost:8005/api/health/providers

## 🎯 Core Features

### 1. Multi-Agent Council (HuggingFace Powered)

Three specialized AI agents analyze API differences:

- **Primary Analyzer** (`Qwen/Qwen2.5-7B-Instruct`)
  - Technical analysis of API differences
  - Detects type mismatches, missing fields, performance issues
  - Assigns initial risk scores

- **Skeptic Critic** (`microsoft/Phi-3-medium-4k-instruct`)
  - Challenges findings and identifies false positives
  - Semantic equivalence detection (e.g., 100.0 ≈ "100")
  - Risk adjustment recommendations

- **Consensus Judge** (`mistralai/Mistral-7B-Instruct-v0.3`)
  - Weighted decision making based on council input
  - Final verdict: PASS / NEEDS_REVIEW / FAIL
  - Deployment recommendations

### 2. Shadow Replay Testing

- **Dual API Testing**: Compares legacy vs headless API responses
- **Difference Detection**: Uses DeepDiff for comprehensive analysis
- **Bug Simulation**: Configurable issues for testing (type changes, missing fields)
- **Performance Monitoring**: Latency comparison and regression detection

### 3. Real-time Dashboard

- **Live Test Feed**: Real-time monitoring via Supabase subscriptions
- **Risk Assessment**: Visual risk scoring and verdict display
- **API Comparison**: Side-by-side JSON diff visualization
- **Agent Trace**: Multi-agent workflow visualization
- **Mitigation Controls**: Human-in-the-loop approval/rejection

### 4. Human Oversight

- **Mitigation Gate**: Manual override capabilities
- **Risk Thresholds**: Configurable risk-based routing
- **Audit Trail**: Complete decision history in database
- **Real-time Notifications**: Instant alerts for high-risk scenarios

## 🧪 Usage Examples

### Basic Shadow Test
```bash
cd engine
venv\Scripts\activate
python shadow_engine.py --payload '{"item": "laptop", "price": 1000}'
```

### High-Risk Scenario (Multiple Issues)
```bash
# Enable bugs in engine/config.py:
# BUGS_ENABLED = {"type_change": True, "missing_key": True}

python shadow_engine.py --payload '{"item": "enterprise_server", "price": 50000}'
```

**Expected Council Analysis:**
- **Primary**: Risk 0.9 - "Type mismatch + missing tax field"
- **Skeptic**: Risk 0.7 - "Type change is false positive, but missing field is serious"  
- **Judge**: Risk 0.82 - "FAIL - Do not deploy"

### API Status Check
```bash
curl http://localhost:8005/api/status/{test_id}
```

### Manual Mitigation
```bash
curl -X POST http://localhost:8005/api/mitigate/{test_id}
```

## 📡 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Trigger parity test analysis |
| `GET` | `/api/status/{test_id}` | Get test status and results |
| `GET` | `/api/health/providers` | Check AI provider health |
| `POST` | `/api/mitigate/{test_id}` | Mark test as mitigated |
| `WebSocket` | `/ws/tests/{test_id}` | Real-time test updates |

### Request/Response Examples

**Analyze Request:**
```json
{
  "test_id": "test-123",
  "merchant_id": "merchant-456", 
  "legacy_response": {"status": "SUCCESS", "price": 100.0, "tax_total": 10.0},
  "headless_response": {"status": "SUCCESS", "price": "100"},
  "diff_report": {"type_changes": {...}, "dictionary_item_removed": [...]}
}
```

**Status Response:**
```json
{
  "test_id": "test-123",
  "status": "complete",
  "final_verdict": "FAIL",
  "risk_score": 0.82,
  "council_opinions": [
    {
      "agent": "primary_analyzer",
      "provider": "huggingface",
      "risk_score": 0.9,
      "detected_issues": ["Type mismatch", "Missing tax field"],
      "confidence": 0.85
    }
  ],
  "mitigation_recommendation": "Do not deploy - high risk detected"
}
```

## 🔧 Configuration

### Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_SERVICE_KEY` | Supabase service key | Required |
| `HF_TOKEN` | HuggingFace API token | Required |
| `ORCHESTRATOR_PORT` | Orchestrator port | 8005 |
| `MAX_RETRIES` | Max retry attempts | 3 |

### Bug Simulation (engine/config.py)
```python
BUGS_ENABLED = {
    "type_change": False,    # float -> string conversion
    "missing_key": False,    # Remove tax_total field  
    "case_mismatch": False,  # SUCCESS -> success
    "performance_delay": False,  # Add 2s delay
    "flaky": False          # Random 20% failures
}
```

## 🐛 Troubleshooting

### Common Issues

**Dashboard shows no data:**
- Check orchestrator is running: `curl http://localhost:8005/health`
- Verify Supabase realtime is enabled for `shadow_tests` table
- Check browser console for connection errors

**Council analysis fails:**
- Verify HuggingFace token is valid
- Check provider health: `curl http://localhost:8005/api/health/providers`
- Review orchestrator logs for API errors

**Shadow tests fail:**
- Ensure legacy (8001) and headless (8002) APIs are running
- Check engine configuration in `config.py`
- Verify network connectivity between services

## 📊 System Monitoring

### Health Endpoints
- **Orchestrator**: http://localhost:8005/health
- **Providers**: http://localhost:8005/api/health/providers
- **Legacy API**: http://localhost:8001/health (if implemented)
- **Headless API**: http://localhost:8002/health (if implemented)

### Performance Metrics
- **Analysis Latency**: Tracked per test in database
- **Provider Response Times**: Monitored and logged
- **Failure Rates**: Consecutive failure tracking with auto-recovery

## 🎯 Demo Scenarios

### Scenario 1: Safe Migration (PASS)
```bash
# No bugs enabled - identical responses
python shadow_engine.py --payload '{"item": "laptop", "price": 1000}'
# Expected: Risk ~0.0, Verdict: PASS
```

### Scenario 2: Minor Issue (NEEDS_REVIEW)  
```bash
# Only type_change enabled
python shadow_engine.py --payload '{"item": "tablet", "price": 500}'
# Expected: Risk ~0.3, Verdict: NEEDS_REVIEW
```

### Scenario 3: Critical Issue (FAIL)
```bash
# Both type_change and missing_key enabled  
python shadow_engine.py --payload '{"item": "server", "price": 10000}'
# Expected: Risk ~0.8, Verdict: FAIL
```

## 👥 Team

**Built by:**
- **Aayush**
- **Keshav**

## 📝 License

MIT License - see LICENSE file for details.

---

**Shadow-SHERPA Hybrid System** - Intelligent AI-powered migration safety net for enterprise e-commerce platforms. 🛡️✨
