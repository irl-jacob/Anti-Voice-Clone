# AvC — Research & Build Handover
**SIH 2026 · Problem Statement SIH26104 · AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks**

This document hands off everything researched so far, so you can start building without re-doing the groundwork. Read it top to bottom once, then use it as a reference while you work.

---

## 1. The One-Line Version

AvC listens to a phone call in real time, in 1–2 second chunks, and tells you — with a visual explanation, not just a score — whether the voice on the line is a clone. It supports Hindi, Tamil, Telugu, and English.

---

## 2. Why This Problem Is Real (don't skip this — you'll need it for the pitch too)

Reported Indian incidents we're building against:
- ₹97,500 lost in Indore — a cloned "police-employee cousin's" voice used to request emergency funds
- ₹1.83 lakh lost in Indore — a cloned "brother-in-law's" voice used in a fake visa-arrest scam
- ₹1.97 lakh lost in Hyderabad — a cloned relative's voice message targeting a senior citizen
- ₹10.70 crore corporate fraud — a company director's voice cloned to authorise a fund transfer

**Why voice specifically is dangerous:** cloning needs only a few seconds of reference audio, needs far less compute than video deepfakes, and the artefacts it introduces are easy for a human ear to miss — especially over a compressed, low-bitrate phone line.

---

## 3. Research Foundations — read these before you touch code

### Core detection model
- **AASIST** (Audio Anti-Spoofing using Integrated Spectro-Temporal Graph Attention Networks) — the backbone classifier. Combines spectral and temporal graph attention branches to catch synthetic-speech artefacts.
  Repo: `github.com/clovaai/aasist`
  Why this one: published, open-source, and already benchmarked at a very low equal-error-rate on the standard spoof-detection benchmark (ASVspoof 2019 LA) — we fine-tune it rather than build a detector from scratch.

- **Wav2Vec 2.0** — self-supervised speech representation model used as a feature front-end feeding into AASIST. Gives the classifier richer input than raw spectrograms alone, which matters most for generalising across languages/accents.

### Datasets — download these first, in this order
1. **ASVspoof 2019 (Logical Access)** — `datashare.ed.ac.uk/handle/10283/3336` — your baseline training set. Academic research license.
2. **ASVspoof 2021 (LA/DF)** — `asvspoof2021.com` — cross-dataset evaluation set. This is harder and more realistic than 2019 — expect a higher equal-error-rate here, that's normal.
3. **In-the-Wild** — `deepfake-total.com/in_the_wild` — real-world podcast/political-speech deepfake benchmark. Use this to sanity-check that the model isn't just overfitting to lab-generated spoof audio.
4. **Team-recorded Indian-language set** — you'll need to record short consented samples in Hindi/Tamil/Telugu (team members reading the same lines) to fine-tune/validate multilingual coverage. Nothing public covers this well yet — this is one of our actual novelty claims, so don't skip it.

### Competitive landscape (context, not something to re-research — already done)
| Solution | Gap we exploit |
|---|---|
| Pindrop | real-time, but enterprise contact-centre platform only, not India-localised |
| Resemble AI (Detect) | strong accuracy, but proprietary SaaS, no Indian-language tuning |
| Reality Defender | real-time call coverage is an add-on, not core |
| DoT's Deepfake Detection System | general-purpose across media types, not live-call specialised |
| Kroop AI / VoiceID / academic prototypes | batch/offline only, or English-only |

**The gap we're filling:** nobody combines real-time streaming + explainability + Indian-language coverage + affordable deployment. That's the whole pitch — keep it in mind while making technical trade-offs.

---

## 4. System Architecture

```
Live Call / Uploaded Audio
        │
        ▼
VAD + Streaming Chunker (1–2s windows)
        │
        ▼
Feature Front-End (raw waveform + Wav2Vec 2.0 embeddings)
        │
        ▼
AASIST Spectro-Temporal Graph Attention Classifier
        │
        ▼
Rolling Risk Aggregator (per-call score)
        │
        ├──▶ Explainability Layer (spectral/temporal anomaly heatmap)
        │
        └──▶ Agent Dashboard + Real-Time Alert
                       │
                       ▼ (feedback)
              back into AASIST fine-tuning
```

**Component notes:**
- **VAD + Chunker:** strip silence, split into fixed windows. Window size is a real trade-off — smaller windows mean faster alerts but noisier per-window scores; 1–2s is our starting point, tune from there.
- **Rolling Risk Aggregator:** don't just average window scores — a single high-confidence spoof window mid-call should spike the risk score faster than it decays. Worth prototyping a simple exponential-weighted scheme before anything fancier.
- **Explainability Layer:** pull directly from AASIST's own attention weights rather than building a separate explainability model — cheaper and keeps the "why" tied to the actual decision.
- **Feedback loop:** log every flagged call's audio + verdict so it can be used for continual fine-tuning later. Doesn't need to be automated for the hackathon demo — just don't architect it in a way that makes this impossible later.

---

## 5. Tech Stack (with reasoning, so substitutions are informed choices, not accidents)

| Layer | Choice | Why |
|---|---|---|
| AI/ML | AASIST + Wav2Vec 2.0, PyTorch | Published, pretrained, fine-tunable — not starting from zero |
| Backend | FastAPI + WebSocket | WebSocket is non-negotiable for streaming; FastAPI plays well with async audio pipelines |
| Data | PostgreSQL (call logs/scores), Redis (rolling-window session cache) | Redis specifically for the per-call rolling state — don't put that in Postgres, too slow for real-time reads |
| Frontend | React.js + Tailwind + Chart.js | Chart.js is enough for a live risk-score line chart — no need for anything heavier |
| Deployment | Docker, AWS/GCP or on-prem | On-prem option matters for the "data sovereignty" pitch angle — keep the Docker setup portable |

---

## 6. Getting Started — step by step

1. **Environment setup**
   - `git clone github.com/clovaai/aasist` and get the baseline model running on ASVspoof 2019 LA first, before touching your own data. Confirm you can reproduce a reported equal-error-rate in the same ballpark as the paper — if you can't, something's wrong with your setup, not the model.
2. **Baseline validation**
   - Run the pretrained/fine-tuned checkpoint against ASVspoof 2021 LA/DF. Expect a noticeably higher equal-error-rate than on 2019 — that's the known train/test distribution gap, not a bug.
3. **Streaming wrapper**
   - Once the classifier works on full files, build the chunking layer around it. Test chunking on a few of your own recorded clips before wiring it to a live WebSocket feed.
4. **Multilingual pass**
   - Record the Hindi/Tamil/Telugu validation clips early — don't leave this for the last day, it's the piece with no existing dataset to fall back on.
5. **Explainability**
   - Extract attention weights from AASIST's forward pass and render them as a simple heatmap over the spectrogram — this can be a fairly late addition since it doesn't block the detection pipeline.
6. **Dashboard + alerting**
   - Wire the rolling risk score to the React dashboard last, once the backend is emitting scores reliably over WebSocket.
7. **Demo rehearsal**
   - Prepare a live clone-and-catch demo: clone a teammate's voice ahead of time (any consumer voice-cloning tool works for this), play it into the pipeline, and confirm the flag fires live in front of judges.

---

## 7. Task Breakdown by Role

- **AI/ML Lead:** AASIST fine-tuning, dataset preprocessing, baseline equal-error-rate validation
- **AI/ML Engineer:** explainability module, multilingual dataset recording/augmentation and evaluation
- **Backend/Full-Stack Lead:** FastAPI + WebSocket streaming pipeline, rolling risk aggregator logic
- **Frontend/UX:** React dashboard, live risk visualisation, call-simulation UI
- **DevOps/QA:** Docker packaging, on-prem/cloud deployment, latency testing against the <1.5s target
- **Research/Docs Lead:** keep this document updated, own the reference list, prep the pitch narrative

---

## 8. Targets to Hit (so you know what "done" looks like)

- Equal error rate **below 8%** on ASVspoof 2021 LA/DF
- Decision latency **under 1.5 seconds** per streaming window
- **≥90% detection accuracy** maintained across Hindi, Tamil, Telugu, and English
- A working end-to-end demo handling **50+ simulated calls**, including one live clone-and-catch moment

---

## 9. Open Risks — flag these, don't hide them

- **Accent/language generalisation** is the least de-risked part of this project — no public dataset covers it well, so our own recorded validation set is doing real work. Budget real time for this, not leftover time.
- **Latency at scale** — 1.5s is achievable per-window in isolation; confirm it holds once the full pipeline (VAD → features → model → aggregation → dashboard) is chained together, not just the model alone.
- **Adversarial drift** — newer cloning tools will keep outpacing any static detector. We're not solving this fully in a hackathon; the honest answer in the pitch is "continual retraining via the feedback loop," not "solved."

---

## 10. Master Reference List

- AASIST — `github.com/clovaai/aasist`
- ASVspoof 2019 dataset — `datashare.ed.ac.uk/handle/10283/3336`
- ASVspoof 2021 Challenge dataset — `asvspoof2021.com`
- "In-the-Wild" audio deepfake benchmark — `deepfake-total.com/in_the_wild`
- DoT Deepfake Detection System (DDS) — `deveservices.dot.gov.in/node/60`
- Kroop AI (VizMantiz) — `cbinsights.com/company/kroop-ai`
- VoiceID (multilingual Indian-language voice detector) — `hunted.space/product/voiceid`
- Resemble AI vs. Pindrop / Reality Defender comparisons — `resemble.ai/resemble-ai-vs-pindrop`, `resemble.ai/resemble-ai-vs-reality-defender`
- AI Incident Database — Indian voice-cloning fraud incidents — `incidentdatabase.ai/entities/scammers-in-india`

---

*Questions on any section — ping whoever's listed as the relevant role owner above before re-researching something that's already been figured out here.*
