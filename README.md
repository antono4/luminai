# LuminAI - Perplexity API Python Wrapper

Self-Healing AI Agent untuk Perplexity API wrapper yang bisa mendeteksi dan memperbaiki bug secara otomatis.

## 🎯 Features

- **Self-Healing Agent** - AI agent yang otomatis mendeteksi dan memperbaiki bug
- **Dashboard** - Web interface untuk monitoring real-time
- **GitHub Actions** - CI/CD pipeline yang berjalan setiap 10 menit
- **OpenHands Integration** - Integrasi dengan OpenHands Cloud

## 🚀 Quick Start

### Installation

```bash
pip install -e .
```

### Dashboard

```bash
# Jalankan dashboard
python -m http.server 8080
# Buka http://localhost:8080
```

### CLI

```bash
# Run self-healing workflow
python -c "from luminai_self_healing import SelfHealingOrchestrator; print(SelfHealingOrchestrator().run_workflow())"
```

## 📁 Project Structure

```
luminai/
├── c4.yml                    # Konfigurasi C4 Model
├── index.html                 # Dashboard web
├── perplexity/                # Main package
│   ├── client.py             # API client
│   ├── config.py             # Configuration
│   ├── driver.py             # HTTP driver
│   └── ...
├── luminai_self_healing/    # Self-healing module
│   ├── __init__.py
│   ├── orchestrator.py       # Main orchestrator
│   ├── bug_detector.py      # Bug detection
│   └── config.py            # Config loader
├── openhands/               # OpenHands integration
│   ├── __init__.py
│   └── client.py            # OpenHands client
├── .github/workflows/        # GitHub Actions
│   └── self-healing.yml     # Self-healing workflow
└── tests/                   # Unit tests
```

## 🔧 Configuration

Edit `c4.yml` untuk konfigurasi:

```yaml
self_healing:
  enabled: true
  auto_fix: true
  max_retries: 3
  interval_minutes: 10

releases:
  enabled: true
  schedule:
    interval_minutes: 10
```

## ⚡ GitHub Actions

Workflow berjalan otomatis setiap **10 menit**:

1. **Self-Healing** - Run agent workflow
2. **Test** - Run pytest
3. **Lint** - Check code quality
4. **Build** - Build package

## 🌐 OpenHands Cloud

Integrasikan dengan OpenHands Cloud:

```python
from openhands import OpenHandsClient, OpenHandsConfig

config = OpenHandsConfig(
    repository="antono4/luminai",
    branch="main"
)

client = OpenHandsClient(config)
result = client.start_conversation(
    message="Run self-healing for LuminAI",
    title="[LuminAI] Self-Healing"
)
```

## 📊 Dashboard

Dashboard menyediakan:

- 📈 Real-time statistics
- ⏰ Countdown timer
- 📋 Activity logs
- 🎮 Start/Stop controls

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📝 License

MIT
