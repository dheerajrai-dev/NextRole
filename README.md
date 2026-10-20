# NextRole 🚀
### AI-Powered Unified Job & Internship Finder (MVP)

**NextRole** is a simple, functional, student-friendly job and internship finder powered by the **TinyFish Web API**. It lets students and job seekers search across multiple career platforms (LinkedIn, Internshala, Indeed, Wellfound, direct company career pages) from a single interface, eliminates duplicate listings, and provides direct links to the original application portals.

---

## 📌 Table of Contents

- [Core Workflow](#-core-workflow)
- [Key Features](#-key-features)
- [Architecture & Data Flow](#-architecture--data-flow)
- [Reference Repositories & Learnings](#-reference-repositories--learnings)
- [Prerequisites](#-prerequisites)
- [Environment Setup & Installation](#-environment-setup--installation)
  - [1. Backend Setup (.venv)](#1-backend-setup-venv)
  - [2. Environment Variables (.env)](#2-environment-variables-env)
  - [3. Frontend Setup](#3-frontend-setup)
- [Running NextRole Locally](#-running-nextrole-locally)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing)
- [Troubleshooting & Known Limitations](#-troubleshooting--known-limitations)

---

## 🔄 Core Workflow

```text
Enter Job Query & Filters 
         ↓
Construct Targeted Query for TinyFish Web API
         ↓
TinyFish Searches & Discovers Live Postings
         ↓
Normalize Fields (Title, Company, Location, Skills, Salary, Work Mode)
         ↓
Deduplicate Listings (Canonical URL + Company/Title Matching)
         ↓
Display Interactive Results in Dashboard
         ↓
Open Original Application Link in New Tab
```

---

## ✨ Key Features

1. **Unified Job & Internship Search:**
   - Search by job title, keywords, location, work mode (Remote/Hybrid/On-site), employment type (Internship/Full-time/etc.), and experience level.
2. **TinyFish Web API Integration:**
   - Real server-side integration querying `https://api.search.tinyfish.ai` using authenticated `X-API-Key` headers.
3. **Smart Field Extraction:**
   - Parses job titles, hiring company names, technical skills chips, work modes, employment types, salary/stipend information, and source platforms without inventing missing fields.
4. **Duplicate Elimination:**
   - Multi-tier deduplication based on canonicalized URLs (stripping UTM tracking tags, session identifiers, trailing slashes) and normalized company + title pairs.
5. **Freshness & Integrity Badging:**
   - Every listing clearly displays a **Needs verification** badge explaining that active application status has not been confirmed by automated form submission.
6. **Graceful Search States & Actionable Error Handling:**
   - Distinct interface states for *Ready to search*, *Searching (skeleton loader)*, *Results found*, *No results found*, *Credentials missing*, and *Request timed out*.
7. **No Heavy Database Overhead:**
   - High-performance, in-memory processing using Python standard libraries and Pydantic models. Zero database setup required.

---

## 🏗️ Architecture & Data Flow

- **Frontend:** React 19 + TypeScript + Vite. Styled with modern, high-contrast dark theme.
- **Backend:** Python 3.14 + FastAPI + Uvicorn + Pydantic v2 + HTTPX.
- **Data Store:** In-memory session processing (no database required for MVP).
- **External Integration:** TinyFish Web API (`https://api.search.tinyfish.ai`).

```text
NextRole/
├── .venv/                     # Python 3.14 virtual environment
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point, CORS, static SPA mount
│   │   ├── models.py          # Pydantic schemas (JobListing, SearchRequest, etc.)
│   │   ├── routes/
│   │   │   └── search.py      # /api/health and /api/search endpoints
│   │   └── services/
│   │       ├── tinyfish.py     # TinyFish HTTP client & error hierarchy
│   │       ├── job_parser.py   # Text normalizer & attribute extractor
│   │       └── deduplication.py# URL canonicalizer & duplicate detector
│   ├── tests/
│   │   └── test_backend.py    # 10 unit tests covering all search flows
│   └── requirements.txt       # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # Header, SearchBar, JobCard, StatusViews
│   │   ├── services/api.ts    # Frontend HTTP client & error handler
│   │   ├── types.ts           # TypeScript interfaces
│   │   ├── App.tsx            # Main application coordinator
│   │   └── index.css          # Responsive styling
│   ├── package.json
│   └── vite.config.ts         # Vite configuration with /api dev proxy
├── .env                       # Local secrets (never committed to Git)
├── .env.example               # Safe template for environment variables
├── .gitignore                 # Excludes .venv/, .env, node_modules/, dist/
└── README.md
```

---

## 🔬 Reference Repositories & Learnings

Before building NextRole, two open-source reference implementations were inspected:

1. **AutoJobHunter-AI (`dilipnalage1063/AutoJobHunter-AI`)**
   - *Architecture:* Spring Boot backend querying `https://api.tinyfish.ai/v1/agent/run`.
   - *Key Learning & Caution:* When TinyFish returned an error or was unreachable, the code silently caught the exception and generated hardcoded mock job cards. NextRole specifically avoids this anti-pattern: errors, missing keys, and invalid tokens are surfaced transparently to the user with actionable instructions.
2. **JobScout-AI (`Bhavishya003Sharma/JobScout-AI`)**
   - *Architecture:* Streamlit single-script Python application using `https://api.search.tinyfish.ai`.
   - *Key Learning:* Provided useful heuristics for canonicalizing URLs (stripping query parameters and trailing slashes) and filtering out generic directory search index pages. NextRole adapted these patterns into decoupled, tested Python modules and a modern React/FastAPI architecture.

---

## 📋 Prerequisites

- **Python:** 3.10+ (tested on Python 3.14)
- **Node.js:** v18+ (tested on Node v24.12.0)
- **TinyFish API Key:** Generated from [agent.tinyfish.ai/api-keys](https://agent.tinyfish.ai/api-keys)

---

## 🚀 Environment Setup & Installation

### 1. Backend Setup (.venv)

Navigate to the project root and create the virtual environment:

```powershell
# Navigate to the NextRole project root
cd c:\Users\Dheeraj rai\Desktop\NextRole

# Create the virtual environment
python -m venv .venv

# Activate the virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1
# Or in Command Prompt: .\.venv\Scripts\activate.bat

# Verify Python executable is inside .venv
python -c "import sys; print(sys.executable)"

# Upgrade pip and install backend dependencies
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

### 2. Environment Variables (.env)

NextRole securely reads configuration from a `.env` file in the project root. Create `.env` from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` to configure your settings:

```env
# TinyFish API credentials (get your key from https://agent.tinyfish.ai/api-keys)
TINYFISH_API_KEY=your_actual_tinyfish_api_key_here

# Application configuration
APP_ENV=development
LOG_LEVEL=INFO

# Backend server configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173
```

> **Security Note:** The `.env` file is excluded in `.gitignore` and must never be committed to Git. The TinyFish API key is kept strictly on the backend and is never sent to the browser.

### 3. Frontend Setup

Install the frontend packages:

```powershell
cd frontend
npm.cmd install
npm.cmd run build
cd ..
```

---

## 🏃 Running NextRole Locally

### Option A: Development Mode (Hot Reloading)

Run the backend and frontend development servers concurrently:

**Terminal 1 — Backend (FastAPI):**
```powershell
# Inside NextRole root
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend runs at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.*

**Terminal 2 — Frontend (Vite):**
```powershell
cd frontend
npm.cmd run dev
```
*Frontend runs at `http://localhost:5173` and automatically proxies `/api` requests to the backend.*

---

### Option B: Unified Production Mode (Single Command)

Once built (`npm run build` in `frontend`), FastAPI serves both the REST API and the React frontend on a single port:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000` in your browser.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Checks backend status, API version, and whether TinyFish is configured. |
| `POST` | `/api/search` | Performs a live TinyFish search, parses results, deduplicates, and returns listings. |

### Example Search Request (`POST /api/search`):
```json
{
  "query": "Python Developer Intern",
  "location": "Delhi NCR",
  "work_mode": "Remote",
  "employment_type": "Internship",
  "experience_level": "Fresher",
  "limit": 20
}
```

### Example Search Response:
```json
{
  "query": "Python Developer Intern",
  "total_found": 15,
  "deduplicated_count": 3,
  "results": [
    {
      "id": "a1b2c3d4e5f67890",
      "title": "Python Developer Intern",
      "company": "TechSolutions",
      "location": "Delhi NCR",
      "description": "Looking for a Python Developer Intern with basic knowledge of FastAPI or Django.",
      "skills": ["Python", "FastAPI", "Git"],
      "employment_type": "Internship",
      "experience_level": "Fresher / Entry level",
      "work_mode": "Remote",
      "salary": "₹20,000/month",
      "source": "Internshala",
      "url": "https://internshala.com/internship/detail/python-intern",
      "posting_date": "2026-10-18",
      "extracted_at": "2026-10-20T12:30:00Z",
      "status": "Needs verification"
    }
  ],
  "applied_filters": {
    "location": "Delhi NCR",
    "work_mode": "Remote",
    "employment_type": "Internship",
    "experience_level": "Fresher"
  },
  "search_metadata": {
    "source": "TinyFish Web API",
    "provider_total": 15,
    "retrieved_at": "2026-10-20T12:30:00Z"
  }
}
```

---

## 🧪 Testing

The test suite covers request validation, parsing, error handling, duplicate detection, and health checks.

Run tests using pytest inside `.venv`:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m pytest backend/tests/ -v
```

### Test Coverage Highlights:
- `test_health_check_endpoint`: Verifies backend health and status reporting.
- `test_search_request_validation`: Ensures empty/invalid requests are rejected (422).
- `test_clean_text_and_url_canonicalization`: Tests tracking parameter removal and URL normalization.
- `test_job_parser_fields`: Validates extraction of title, company, skills, work mode, and salary.
- `test_job_parser_malformed_and_missing_fields`: Ensures unknown fields remain empty and are never hallucinated.
- `test_deduplication_exact_url_and_company_title`: Verifies that duplicate URLs and identical company+title listings are removed while preserving distinct companies.
- `test_api_auth_failure_handling`: Verifies 401 propagation when TinyFish credentials are invalid.
- `test_api_timeout_handling`: Verifies 504 gateway timeout handling.
- `test_empty_search_results`: Confirms clean response structure when zero results are found.
- `test_api_missing_key_handling`: Tests behavior when `TINYFISH_API_KEY` is not configured.

---

## ⚠️ Troubleshooting & Known Limitations

1. **TinyFish Authentication Error (HTTP 401):**
   - Symptom: Dashboard shows *"TinyFish API Credentials Required"*.
   - Cause: `TINYFISH_API_KEY` is missing or invalid.
   - Fix: Check your key at [agent.tinyfish.ai/api-keys](https://agent.tinyfish.ai/api-keys) and update `.env`.
2. **Missing Job Details:**
   - Some search snippets do not specify a salary or exact city. NextRole strictly preserves data integrity by leaving these fields unknown rather than inventing placeholders.
3. **In-Memory Storage:**
   - Search results exist in-memory for the active session. If the server restarts, historical search results are cleared. Persistent database storage (PostgreSQL/SQLite) can be introduced in a future release.
4. **PowerShell Script Execution Policy:**
   - If running `npm` or `.venv\Scripts\Activate.ps1` gives an execution policy error, run scripts with `npm.cmd` or run PowerShell with `-ExecutionPolicy Bypass`.
