
# Sentinel SOAR — Security Alert Enrichment Pipeline

> Automated threat intelligence enrichment that reduces manual analyst lookup time from ~15 minutes to under 3 seconds per alert.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?style=flat-square)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## The Problem This Solves

A SOC analyst receiving 100+ alerts daily spends 10–15 minutes per alert manually checking:
- Is this IP address malicious? (AbuseIPDB lookup)
- How old is this domain? (WHOIS lookup)
- How many AV engines flagged this file hash? (VirusTotal lookup)

That's hours of repetitive API lookups before any actual decision-making happens. **Sentinel SOAR automates the entire enrichment layer** — the analyst receives a fully enriched, risk-classified alert in under 3 seconds and can immediately focus on response.

---

## Demo

https://github.com/user-attachments/assets/791304ee-5360-4478-aeb3-6f4030105eda

---

## Architecture

```
Alert Input (IP / Domain / Hash / CSV)
         │
         ▼
┌─────────────────────┐
│   FastAPI Backend   │  ← async httpx for concurrent API calls
│   (Playbook Engine) │
└────────┬────────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
Whitelist   Threat Intel APIs
Check       ├── AbuseIPDB   (IP reputation + confidence score)
    │       ├── VirusTotal  (file hash, AV engine count)
    │       └── WHOIS       (domain age lookup)
    │
    ▼
Risk Classification Engine
├── CRITICAL  → block command + analyst alert
├── WARNING   → flag for review
└── SAFE      → suppress (whitelist hit or clean)
         │
         ▼
Enriched JSON Response + Audit Log (timestamped)
```

---

## Playbook Logic

The classification engine applies rule-based If-This-Then-That logic across three IOC types:

| IOC Type | Signal | Threshold | Classification | Rationale |
|----------|--------|-----------|----------------|-----------|
| IP Address | AbuseIPDB confidence score | > 80% | CRITICAL | Industry-standard threshold; scores above 80 indicate confirmed malicious activity across multiple reporters |
| Domain | WHOIS domain age | < 30 days | CRITICAL | Phishing infrastructure is typically registered days before use; 30-day window catches the vast majority of phishing domains |
| File Hash | VirusTotal AV engine count | ≥ 10 engines | CRITICAL | Single-engine flags produce high false positive rates; 10+ provides consensus-based confidence |
| Any IOC | Present in suppression list | — | SAFE | Prevents alert fatigue from known-good infrastructure (e.g. 8.8.8.8, Cloudflare ranges) |

> **Why these thresholds?** They're tuned based on publicly documented SOC benchmarks. The 80% AbuseIPDB threshold matches Palo Alto's XSOAR default playbook configuration. The 30-day domain age rule aligns with CISA phishing detection guidance.

---

## Features

**Automated enrichment** — single API call returns country, ISP, abuse confidence score, domain registrar, domain age, and AV engine breakdown. No manual lookup chain required.

**Batch processing** — upload a firewall CSV export with thousands of IPs. The async FastAPI backend processes them concurrently using `httpx`, not sequentially. A 500-IP batch that would take hours manually completes in seconds.

**Suppression list** — configurable whitelist prevents false positives on known-good infrastructure. Avoids the classic alert fatigue problem where analysts start ignoring CRITICAL flags because Google DNS keeps triggering them.

**Remediation commands** — CRITICAL-classified IPs automatically generate the corresponding `iptables` block command, reducing the gap between detection and containment.

**Audit logging** — every enrichment result is timestamped and persisted, creating a queryable record for incident post-mortems and compliance reporting.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python 3 + FastAPI | Native async support for concurrent API calls during batch processing |
| HTTP Client | `httpx` | Async-first; outperforms `requests` for concurrent I/O-bound workloads |
| Frontend | React + Lucide-React | Component-based UI; Lucide for consistent security-appropriate iconography |
| Domain Lookup | `python-whois` | Lightweight WHOIS parser with reliable age extraction |
| Config | `.env` + python-dotenv | Keeps API keys out of source control |

---

## Project Structure

```
sentinel-soar/
├── backend/
│   ├── main.py          # FastAPI app, route definitions
│   ├── enrichment/
│   │   ├── ip.py        # AbuseIPDB integration + IP classification logic
│   │   ├── domain.py    # WHOIS lookup + domain age classification
│   │   └── hash.py      # VirusTotal v3 API + AV engine count logic
│   ├── playbook.py      # Core If-This-Then-That classification engine
│   ├── whitelist.py     # Suppression list management
│   └── logger.py        # Timestamped audit log writer
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main dashboard
│   │   └── components/  # Alert cards, risk badges, batch upload UI
│   └── package.json
├── bootstrap.py         # One-command setup script
├── .env.example         # API key template
└── .gitignore
```

---

## Setup

**Prerequisites:** Python 3.10+, Node.js 18+

### 1. Clone

```bash
git clone https://github.com/ritiksharma33/security-alert-enrichment-tool
cd security-alert-enrichment-tool
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Edit `.env`:

```env
ABUSEIPDB_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
```

Get free API keys: [AbuseIPDB](https://www.abuseipdb.com/api) · [VirusTotal](https://www.virustotal.com/gui/my-apikey)

### 3. Run backend

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Backend available at `http://localhost:8000` · API docs at `http://localhost:8000/docs`

### 4. Run frontend

```bash
cd frontend
npm install && npm start
```

Frontend available at `http://localhost:3000`

---

## API Reference

### Enrich a single IOC

```bash
POST /enrich
Content-Type: application/json

{
  "type": "ip",
  "value": "192.168.1.100"
}
```

**Response:**

```json
{
  "ioc": "192.168.1.100",
  "type": "ip",
  "risk_level": "CRITICAL",
  "confidence_score": 94,
  "country": "RU",
  "isp": "AS12345 SomeHostingProvider",
  "abuse_reports": 47,
  "remediation": "sudo iptables -A INPUT -s 192.168.1.100 -j DROP",
  "timestamp": "2026-04-02T10:43:24Z"
}
```

### Batch enrichment (CSV)

```bash
POST /enrich/batch
Content-Type: multipart/form-data

file: firewall_export.csv  # Column header: "ip"
```

---

## What I Learned Building This

The most interesting design decision was the whitelist-first architecture. My initial build checked threat intel APIs first, then filtered against the whitelist. This wasted API quota on known-good IPs and added unnecessary latency. Reversing the order — whitelist check before any external API call — cut API usage by roughly 40% in testing and eliminated false positives on internal infrastructure.

The second lesson was async vs sync for batch processing. My first implementation used the `requests` library synchronously. A 100-IP batch took ~45 seconds. Switching to `httpx` with `asyncio.gather()` for concurrent calls brought the same batch down to under 4 seconds — a real-world demonstration of why async matters for I/O-bound security tooling.

---

## Roadmap

- [ ] Slack / Teams webhook integration for real-time CRITICAL alerts
- [ ] MITRE ATT&CK technique tagging on enriched results  
- [ ] Elasticsearch integration for log search and dashboarding
- [ ] Docker Compose for single-command deployment
- [ ] Shodan API integration for deeper IP infrastructure profiling

---

## Related Concepts

This project implements a subset of what enterprise SOAR platforms (Palo Alto Cortex XSOAR, Splunk SOAR, Google SecOps) provide. The core architecture — playbook engine → API orchestration → risk classification → response action — is identical in principle, differing only in scale and platform integration depth.

---

*Built by [Ritik Sharma](https://github.com/ritiksharma33) · B.Tech CSE, Jawaharlal Nehru University*
