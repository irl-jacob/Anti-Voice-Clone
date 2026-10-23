# Contributing to AvC

Thank you for your interest in contributing to **AvC (Audio Deepfake & Synthesis Detector)**! We welcome contributions from researchers, security practitioners, and developers worldwide.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior through our security/contact channels.

---

## Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **Docker & Docker Compose** (for Redis & PostgreSQL)
- **Git**

### 2. Fork and Clone
```bash
# Clone your fork
git clone https://github.com/<your-username>/avc.git
cd avc
```

### 3. Backend Setup
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Download / verify neural model weights (AASIST ONNX)
python scripts/fetch_weights.py
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. Running the Full Stack
```bash
# 1. Start databases
docker-compose up -d

# 2. Start FastAPI backend (in terminal 1)
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# 3. Start React frontend (in terminal 2)
cd frontend && npm run dev
```

---

## Development Workflow

### Branch Naming Conventions
- `feat/<feature-name>` for new features
- `fix/<bug-description>` for bug fixes
- `docs/<documentation-update>` for documentation changes
- `refactor/<cleanup>` for non-breaking code reorganizations
- `perf/<optimization>` for latency or memory improvements

### Running Tests
Before submitting a pull request, ensure all tests pass:

```bash
# Run backend pytest suite
./venv/bin/python -m pytest tests/

# Run frontend type-check & build
cd frontend && npm run build
```

---

## Submitting Pull Requests

1. **Commit Guidelines**: Write clear, imperative commit messages (e.g., `feat: add spectral attention visualization`, `fix: handle empty audio chunk buffer`).
2. **Sync with Main**: Rebase your branch onto the latest `main` branch before submitting.
3. **Open a PR**: Fill out the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) with details on:
   - What changed and why
   - Testing steps and outputs
   - Any related issue numbers (`Fixes #123`)

---

## Reporting Issues & Requesting Features
- Use [GitHub Issues](https://github.com/irl-jacob/Anti-Voice-Clone/issues) to report bugs or request features.
- Please choose the appropriate issue form (`bug_report.yml` or `feature_request.yml`) and include all requested details (OS, Python/Node versions, reproduction steps).

---

## License
By contributing to AvC, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
