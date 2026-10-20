# NextRole

**One search. Multiple sources. Better job discovery.**

NextRole is a unified job discovery platform that helps students, freshers, and job seekers find relevant opportunities without repeatedly searching across different websites. It uses the TinyFish Web API to discover and extract job listings from supported sources, then brings the results into a single searchable dashboard.

Rather than acting as another job board, NextRole focuses on making fragmented job listings easier to search, compare, and verify.

The platform is designed around three core principles:

- **Discover more efficiently:** Search across multiple supported sources from one interface.
- **Improve result quality:** Normalize listings, identify duplicates, and evaluate freshness.
- **Find relevant opportunities:** Apply user-defined filters and build toward personalized, AI-assisted job matching.

---

## The Problem We're Solving

Job discovery is fragmented. A candidate searching for a Python internship might need to check several job boards, company career pages, and internship platforms separately.

This creates three practical problems:

1. **Search fragmentation:** Relevant opportunities are scattered across different sources, each with its own search interface and filters.
2. **Noisy results:** Duplicate listings, inconsistent job titles, and incomplete information make comparisons difficult.
3. **Uncertain availability:** A listing appearing in search results does not necessarily mean the position is still open.

NextRole addresses these problems through a single discovery and data-processing workflow.

## How NextRole Works

<details>
<summary><strong>Explore the search pipeline</strong></summary>

1. **Query construction:** The user specifies a role and search preferences.
2. **Source discovery:** The backend initiates requests to configured, supported job sources.
3. **Data extraction:** TinyFish and permitted integrations retrieve available listing information.
4. **Data normalization:** Source-specific records are mapped to a common job schema.
5. **Duplicate resolution:** Similar listings are compared to identify potential duplicates.
6. **Freshness evaluation:** The system records verification timestamps and evaluates available evidence of listing availability.
7. **Result filtering:** Listings are filtered and ordered according to the user's search criteria.
8. **Opportunity discovery:** The user reviews consolidated results and follows the original application link.

</details>

```mermaid
flowchart TD
    A[Search Query] --> B[FastAPI Backend]
    B --> C[Search Orchestrator]
    C --> D[TinyFish Web API]
    C --> E[Other Supported Sources]
    D --> F[Extracted Listings]
    E --> F
    F --> G[Normalization]
    G --> H[Duplicate Detection]
    H --> I[Freshness Evaluation]
    I --> J[Filtering and Ranking]
    J --> K[(PostgreSQL)]
    K --> L[Unified Dashboard]
    L --> M[Original Job Listing]
```

The pipeline is designed to keep source integrations separate from the core processing logic, making it easier to add or replace supported sources without redesigning the entire application.

## Core Capabilities

| Capability | What it does | Why it matters |
|---|---|---|
| Unified search | Collects results from configured sources | Reduces repeated searches |
| Smart filters | Filters by role, location, experience, work mode, and employment type | Narrows results to suitable opportunities |
| Data normalization | Standardizes available job fields | Makes listings easier to compare |
| Duplicate detection | Identifies listings that may describe the same opportunity | Reduces repetitive results |
| Freshness tracking | Records when listings were last checked | Helps users assess how current the information is |
| Direct application links | Connects users to the original listing | Keeps the application process with the source |
| AI-assisted matching | Planned comparison of skills and job requirements | Can improve relevance beyond keyword matching |

Freshness and duplicate detection are particularly important: a large collection of listings is less useful if it contains repeated opportunities or misleading availability information.

### Listing verification

NextRole should distinguish between:

- **Recently verified:** A recent check found evidence supporting the listing's current availability.
- **Needs verification:** The system could not establish its current status.
- **Potentially expired:** Available evidence suggests the listing may no longer be active.

These statuses must reflect actual verification logic. A recent check alone does not guarantee that a position remains open.

## Example Search

A student searching for entry-level Python roles could enter:

| Filter | Selected value |
|---|---|
| Role | Python Developer Intern |
| Experience | Fresher |
| Location | Delhi NCR |
| Work mode | Remote or Hybrid |
| Employment type | Internship |

NextRole would consolidate matching listings from the configured sources into a common results view.

Each result should show the available job title, company, location, source, relevant requirements, verification information, and original application link.

*Any example listings shown in the interface should be clearly identified as sample data unless they have been retrieved from actual sources.*

## Technology Stack

The proposed stack separates the user interface, API, source integrations, and data processing.

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React, TypeScript, Vite | Search interface and results dashboard |
| Backend | Python, FastAPI | API endpoints and application logic |
| Web extraction | TinyFish Web API | Discovery and extraction from supported websites |
| Database | PostgreSQL | Persistent job and verification records |
| Data processing | Python | Normalization, filtering, and duplicate detection |
| AI matching | Embeddings or language models | Planned semantic matching and recommendations |
| Version control | Git, GitHub | Collaboration and source management |

The final stack should reflect the technologies actually implemented in the repository. TinyFish capabilities and the access rules of each job source must be verified before integration.

## Data Quality and Deduplication

Different websites may describe the same opportunity differently. For example, one source might list *Python Developer Intern*, while another uses *Python Development Internship*.

A robust deduplication process can combine several signals:

- Source-provided job identifiers, when available.
- Canonicalized application URLs.
- Normalized company names and job titles.
- Location and employment type.
- Similarity between descriptions and other listing attributes.

Exact identifiers and URLs should generally take precedence over approximate text similarity. Similarity-based matching should be conservative so that different openings at the same company are not incorrectly merged.

The system should preserve source references and useful metadata when consolidating duplicate records.

## Project Roadmap

Development is organized around delivering a reliable discovery workflow before adding more complex AI features.

- [ ] **Phase 1 — Foundation:** Define the common job schema, project structure, and API contracts.
- [ ] **Phase 2 — Source integrations:** Connect TinyFish and at least one additional usable source.
- [ ] **Phase 3 — Processing pipeline:** Implement normalization, filtering, and duplicate detection.
- [ ] **Phase 4 — Dashboard:** Build the unified search and results experience.
- [ ] **Phase 5 — Freshness and reliability:** Add verification records, error handling, and integration tests.
- [ ] **Phase 6 — AI matching:** Introduce skill-based matching and personalized ranking.
- [ ] **Phase 7 — Deployment:** Configure production settings, monitoring, and documentation.

The checklist should be updated as milestones are completed. It describes the intended development sequence, not a claim that these features already exist.

## Getting Started

The instructions below describe the intended local development setup. Adjust the commands to match the actual repository structure.

### Prerequisites

- Python 3.12 or a compatible supported version
- Node.js and npm
- PostgreSQL
- Git
- TinyFish API access and credentials, where required

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd NextRole
```

Replace the placeholder with the actual repository URL.

### 2. Set up the backend

```bash
cd backend
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the backend dependencies if `requirements.txt` is present:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file using the configuration expected by the application.

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/nextrole
TINYFISH_API_KEY=your_api_key
```

Use the actual variable names expected by the implementation. Never commit API keys, database passwords, or other secrets to version control.

### 4. Run the backend

If the FastAPI application entry point is `app.main:app`:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to inspect the interactive API documentation.

### 5. Run the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL reported by the frontend development server.

**Note:** These commands will work only after the corresponding application files, dependencies, and configuration have been created.

## Responsible Data Access

NextRole relies on access to external job sources, so source availability is a technical and operational constraint.

- Prefer official APIs, authorized feeds, and permitted integrations.
- Respect platform terms, rate limits, and applicable laws.
- Do not bypass authentication or access controls.
- Store only the information needed for job discovery and verification.
- Preserve source attribution and original listing URLs.
- Handle extraction failures and unavailable sources without misrepresenting results.

The availability of TinyFish does not imply that every job platform can be accessed without restrictions. Each integration must be evaluated independently.

## Future Direction

Once unified search and data quality are reliable, NextRole can evolve from a discovery tool into a personalized opportunity-matching platform.

Potential extensions include:

- **Resume-aware search:** Identify opportunities that align with a candidate's existing skills.
- **Skill-gap analysis:** Highlight requirements that a candidate may need to develop.
- **Semantic search:** Understand related job titles and skill requirements beyond exact keyword matches.
- **Personalized ranking:** Prioritize listings according to experience, location, preferences, and skill compatibility.
- **Job alerts:** Surface newly discovered opportunities that match saved searches.
- **Application tracking:** Organize saved listings and application progress.

These features should build on reliable listing data rather than compensate for incomplete or inaccurate source information.

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement a focused change.
4. Test the affected functionality.
5. Submit a pull request explaining the change.

Use descriptive commit messages, document configuration changes, and never include credentials in commits.

## License

A license has not yet been specified. Add the appropriate license file before distributing the project.

---

**NextRole** — Less time searching. More time pursuing the right opportunities.
