======================================================================================
======================================================================================
Req-engineer 
======================================================================================

Create a skill called req-engineer — a senior requirements engineer that interviews the user, extracts complete requirements, and outputs a   
  comprehensive requirements.md with visual prototypes (UI wireframes, CLI interaction examples, API request/response samples) so the user can  
  see exactly what they're getting before any code is written. The output feeds directly into the sw-architect skill.                           
                                                            
  How it works — a structured interview in 2-3 rounds max:

  Round 1 — Understanding the Vision:
  - What are you building? (elevator pitch)
  - Who are the end users? (personas, roles, technical level)
  - What problem does this solve? What's the current workaround?
  - What does success look like? (measurable outcomes)
  - Any existing systems this replaces or integrates with?
  - Interface type — is this a web app, mobile app, desktop app, CLI tool, API service, background worker, or a combination? (this determines
  which prototype format to use)

  Round 2 — Deep Dive (adapt questions based on Round 1 answers, skip what's already clear):
  - Core user journeys — walk me through the 3-5 most important things a user does
  - What data does the system handle? (types, volume, sensitivity, retention)
  - Who are the stakeholders beyond end users? (admins, ops, compliance, analytics)
  - Scale expectations — users, requests, data volume at launch and 12 months out
  - Performance expectations — response times, availability, uptime targets
  - Security & compliance — authentication needs, data regulations (GDPR/HIPAA/SOC2), audit requirements
  - Deployment preferences — cloud/on-prem/hybrid, regions, offline capability
  - Budget and timeline — MVP deadline, full launch target, team size
  - Constraints — must-use technologies, organizational policies, vendor lock-in concerns

  Round 3 (only if needed) — Clarifying Gaps:
  - If Rounds 1-2 left ambiguities or contradictions, ask targeted follow-ups — max 5 questions
  - If everything is clear, skip this round entirely and proceed to writing

  Interview behavior:
  - Think like a real requirements engineer — ask "why" behind feature requests to uncover actual needs vs. assumed solutions. If user says "I
  need a Redis cache", ask what problem they're solving — maybe they need caching, maybe they don't.
  - Spot contradictions — if user says "real-time" but also "batch processing", probe which it actually is or if both are needed for different
  features.
  - Suggest what they forgot — based on the domain, proactively ask about commonly overlooked areas: error handling, notification preferences,
  admin/back-office needs, reporting, onboarding flow, data migration, accessibility.
  - No jargon dumping — match the user's technical level. If they say "I want an app for my bakery", don't ask about "eventual consistency
  models".
  - Prioritization — ask the user to rank features as Must-Have / Should-Have / Nice-to-Have (MoSCoW) or let them just describe importance and
  you categorize.
  - Accept any input format — user can paste bullet points, ramble in paragraphs, share screenshots, or just talk. Extract structure from chaos.
  - Accept inline args: --project, --domain, --scale, --deadline, --interface (web/cli/api/mobile/desktop) to pre-fill known answers.

  After the interview, use WebSearch (2-4 queries) to:
  - Validate domain-specific requirements the user may have missed (e.g., "PCI-DSS requirements for payment processing")
  - Check industry standards for the domain (e.g., healthcare → HL7/FHIR, finance → FIX protocol)
  - Find common pitfalls in similar products

  Then generate requirements.md in the working directory using this template (adapt as needed):

  # Requirements Document: [Project Name]

  ## 1. Project Overview
     - Vision statement (2-3 sentences)
     - Problem statement
     - Target users and personas
     - Success metrics

  ## 2. Scope
     - In scope (what this project covers)
     - Out of scope (explicitly excluded — prevents scope creep)
     - Future considerations (parked for later)

  ## 3. Functional Requirements
     ### 3.1 [Feature Area]
     - FR-001: [Requirement] — Priority: MUST/SHOULD/COULD
     - FR-002: ...
     (Group by feature area/domain, each with unique ID)

  ## 4. User Journeys
     ### Journey 1: [Name]
     - Actor, trigger, steps, expected outcome, error scenarios

  ## 5. Interface Prototypes ← (NEW — the core addition)
     (See "Interface Prototypes" section below for format per interface type)

  ## 6. Non-Functional Requirements
     - NFR-001: Performance — [specific targets: response time, throughput]
     - NFR-002: Scalability — [growth targets]
     - NFR-003: Availability — [uptime SLA]
     - NFR-004: Security — [auth, encryption, compliance]
     - NFR-005: Accessibility — [WCAG level if applicable]
     - NFR-006: Data — [retention, backup, privacy]

  ## 7. Integrations
     - External systems, APIs, third-party services, data imports/exports

  ## 8. Constraints
     - Technical, business, regulatory, timeline, budget

  ## 9. Assumptions
     - What was assumed when not explicitly stated by the user

  ## 10. Risks & Open Questions
     - Identified risks from the interview
     - Unresolved questions needing stakeholder input

  ## 11. Glossary
     - Domain-specific terms defined (only if the domain has jargon)

  ## 12. Appendix
     - Raw notes, references, research findings

  ---
  Interface Prototypes — the section that lets users SEE what they're getting:

  Auto-detect the interface type from the interview and generate the appropriate prototype format. If the project has multiple interfaces (e.g.,
   web app + API + admin CLI), generate prototypes for ALL of them.

  For Web / Mobile / Desktop UI:

  Generate ASCII wireframes for every key screen, showing layout, components, and user flow.

  ### Screen: Login Page
  Triggered by: User opens the app / session expired
  Related: FR-001, FR-002

  ┌─────────────────────────────────────────────┐
  │  ┌─────────────────────────────────────────┐ │
  │  │         🏪  BakeryManager              │ │
  │  └─────────────────────────────────────────┘ │
  │                                               │
  │  ┌─────────────────────────────────────────┐ │
  │  │  Email    [_________________________]   │ │
  │  │  Password [_________________________]   │ │
  │  │                                         │ │
  │  │  [✓] Remember me                        │ │
  │  │                                         │ │
  │  │  [ Login ]          Forgot password?    │ │
  │  │                                         │ │
  │  │  ─────── or ───────                     │ │
  │  │                                         │ │
  │  │  [ Sign up with Google ]                │ │
  │  └─────────────────────────────────────────┘ │
  └─────────────────────────────────────────────┘

  Behavior:
  - Empty email → inline error: "Email is required"
  - Wrong password → "Invalid email or password" (no hint which is wrong)
  - 5 failed attempts → account locked for 15 minutes, show countdown
  - Success → redirect to Dashboard (see Screen: Dashboard)
  - "Forgot password?" → Screen: Password Reset

  For each screen, include:
  - ASCII wireframe showing layout with actual field names, buttons, labels
  - Which FR-XXX requirements this screen satisfies
  - Step-by-step behavior: what happens on each user action
  - Validation rules: what errors appear and when
  - Navigation: where each button/link goes (reference other screens by name)
  - States: empty state, loading state, error state, success state
  - Responsive notes: how it adapts on mobile (if web app)

  Generate wireframes for:
  - Every screen in the main user journey (minimum)
  - Admin/settings screens if they have unique complexity
  - Error pages (404, 500, maintenance)
  - Empty states (no data yet, first-time user)

  Screen flow diagram (Mermaid) showing navigation between screens:
  graph LR
      Login --> Dashboard
      Dashboard --> OrderList
      OrderList --> OrderDetail
      OrderDetail --> EditOrder
      Dashboard --> Settings
      Settings --> Profile
      Settings --> Billing

  For CLI Tools:

  Show exact terminal interactions with realistic example data for every command.

  ### Command: bakery-cli add-product
  Related: FR-005

  $ bakery-cli add-product

  Product name: Sourdough Loaf
  Category (bread/pastry/cake/other): bread
  Price: 8.50
  Cost to make: 3.20
  Daily capacity: 50
  Available days (Mon-Sun, comma-separated): Mon,Tue,Wed,Thu,Fri,Sat

  ✓ Product added: Sourdough Loaf
    ID:       PRD-0042
    Margin:   62.4%
    Schedule: Mon-Sat

  ---

  ### Command: bakery-cli add-product (with errors)

  $ bakery-cli add-product

  Product name:
  ✗ Error: Product name cannot be empty

  Product name: Sourdough Loaf
  Category (bread/pastry/cake/other): pizza
  ✗ Error: Invalid category "pizza". Choose from: bread, pastry, cake, other

  Category (bread/pastry/cake/other): bread
  Price: -5
  ✗ Error: Price must be a positive number

  Price: 8.50
  ...

  ---

  ### Command: bakery-cli list-products
  Related: FR-006

  $ bakery-cli list-products

  ID        │ Name              │ Category │ Price  │ Margin │ Schedule
  ──────────┼───────────────────┼──────────┼────────┼────────┼──────────
  PRD-0001  │ Croissant         │ pastry   │ $4.50  │ 58.2%  │ Daily
  PRD-0012  │ Baguette          │ bread    │ $6.00  │ 55.0%  │ Mon-Sat
  PRD-0042  │ Sourdough Loaf    │ bread    │ $8.50  │ 62.4%  │ Mon-Sat

  Total: 3 products

  $ bakery-cli list-products --category pastry --sort margin

  ID        │ Name              │ Price  │ Margin
  ──────────┼───────────────────┼────────┼────────
  PRD-0001  │ Croissant         │ $4.50  │ 58.2%

  Total: 1 product

  ---

  ### Command: bakery-cli list-products (empty state)

  $ bakery-cli list-products

  No products found. Add your first product:
    bakery-cli add-product

  For each command, include:
  - Full command syntax with all flags/options: bakery-cli add-product [--name NAME] [--category CAT] [--json]
  - Happy path example with realistic data
  - Error examples: every validation error with exact error message
  - Empty state: what shows when there's no data
  - Output formats: table (default), JSON (--json flag), quiet (-q flag)
  - Exit codes: 0 (success), 1 (validation error), 2 (system error)
  - Pipe-friendly output where appropriate: bakery-cli list-products --json | jq '.[] | .name'

  Generate command map showing all CLI commands:
  bakery-cli
  ├── add-product       Add a new product
  ├── list-products     List all products (filterable)
  ├── update-product    Update product details
  ├── delete-product    Remove a product
  ├── report            Generate daily/weekly/monthly report
  │   ├── --daily       Today's summary
  │   ├── --weekly      This week's summary
  │   └── --export csv  Export to CSV
  └── config
      ├── set           Set a config value
      └── show          Show current config

  For APIs:

  Show exact request/response pairs with realistic data for every endpoint.

  ### POST /api/v1/products
  Related: FR-005
  Auth: Bearer token (role: admin, manager)

  Request:
  POST /api/v1/products
  Authorization: Bearer eyJhbGciOi...
  Content-Type: application/json

  {
    "name": "Sourdough Loaf",
    "category": "bread",
    "price": 8.50,
    "cost": 3.20,
    "daily_capacity": 50,
    "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
  }

  Response (201 Created):
  {
    "id": "PRD-0042",
    "name": "Sourdough Loaf",
    "category": "bread",
    "price": 8.50,
    "cost": 3.20,
    "margin": 0.624,
    "daily_capacity": 50,
    "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    "created_at": "2026-03-16T10:30:00Z",
    "created_by": "user-123"
  }

  ---

  ### POST /api/v1/products — Validation Errors

  Request (missing required fields):
  {
    "name": "",
    "price": -5
  }

  Response (422 Unprocessable Entity):
  {
    "error": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "name", "issue": "must not be empty"},
      {"field": "price", "issue": "must be a positive number"},
      {"field": "category", "issue": "is required"}
    ]
  }

  ---

  ### POST /api/v1/products — Unauthorized

  Response (401 Unauthorized):
  {
    "error": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }

  ### POST /api/v1/products — Forbidden

  Response (403 Forbidden):
  {
    "error": "FORBIDDEN",
    "message": "Role 'viewer' cannot create products"
  }

  ---

  ### GET /api/v1/products
  Related: FR-006
  Auth: Bearer token (role: any)

  Request:
  GET /api/v1/products?category=bread&sort=margin&order=desc&page=1&limit=20

  Response (200 OK):
  {
    "data": [
      {
        "id": "PRD-0042",
        "name": "Sourdough Loaf",
        "category": "bread",
        "price": 8.50,
        "margin": 0.624
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "total_pages": 1
    }
  }

  ### GET /api/v1/products (empty)

  Response (200 OK):
  {
    "data": [],
    "pagination": {"page": 1, "limit": 20, "total": 0, "total_pages": 0}
  }

  For each endpoint, include:
  - Method, path, query parameters, and their types/defaults
  - Auth requirements: which roles can access, what happens if unauthorized
  - Request body with every field: name, type, required/optional, validation rules, example value
  - Response for: success, validation error (422), not found (404), unauthorized (401), forbidden (403), server error (500)
  - Pagination format for list endpoints
  - Rate limiting headers if applicable
  - Realistic example data throughout — not "string" and "test123"

  Generate API overview table:
  | Method | Endpoint              | Auth       | Description            | Related |
  |--------|-----------------------|------------|------------------------|---------|
  | POST   | /api/v1/products      | admin, mgr | Create a product       | FR-005  |
  | GET    | /api/v1/products      | any        | List/filter products   | FR-006  |
  | GET    | /api/v1/products/:id  | any        | Get product details    | FR-006  |
  | PUT    | /api/v1/products/:id  | admin, mgr | Update a product       | FR-007  |
  | DELETE | /api/v1/products/:id  | admin      | Delete a product       | FR-008  |

  ---
  Prototype principles:
  - Show, don't describe — "login page has email and password fields" is weak; an ASCII wireframe with exact field labels, button text, and
  error messages is strong
  - Cover every state — success, error, empty, loading. Users never imagine the empty state until they see it.
  - Use realistic data — "Sourdough Loaf, $8.50" not "Product A, $10.00". Real data exposes real issues (what if product name is 80 characters?
  Does the table break?)
  - Every prototype traces to requirements — label with FR-XXX so changes can be traced
  - Behavior over layout — the wireframe shows layout, but the behavior notes below it are equally important. "What happens when I click this?"
  must be answered for every interactive element.
  - This is the user's last chance to cheaply change things — after this document, architecture gets designed and code gets written. Make it
  easy for the user to spot "wait, that's not what I meant" NOW.

  ---
  Every functional requirement must have:
  - Unique ID (FR-001, FR-002...)
  - Clear acceptance criteria (how do you know it's done?)
  - Priority (MUST / SHOULD / COULD)
  - Dependencies on other requirements (if any)
  - At least one prototype reference — which screen/command/endpoint demonstrates this requirement

  Quality checks before finalizing:
  - Every user persona has at least one journey
  - Every journey has prototype screens/commands/endpoints showing each step
  - No requirement contradicts another
  - Non-functional requirements have specific measurable targets, not vague words like "fast" or "secure"
  - Assumptions section documents every default assumed
  - Out-of-scope section exists and is explicit
  - Every interactive element in prototypes has defined behavior for success AND failure
  - Every API endpoint shows error responses, not just happy path
  - Every CLI command shows what happens with bad input
  - Every UI screen shows empty state and error state

  Closing summary after writing the document:
  - Total count: X functional requirements, Y non-functional requirements
  - Priority breakdown: X must-have, Y should-have, Z nice-to-have
  - Prototype coverage: X screens / Y commands / Z endpoints documented
  - Key risks or gaps that need stakeholder input
  - Path to generated requirements.md
  - Tell the user: "Review the prototypes carefully — this is the cheapest point to change anything. Once architecture starts, changes get
  expensive."
  - Suggest: "When you're satisfied, feed this to the sw-architect skill to generate the architecture plan"

  Reference csv-cluster-labeler/SKILL.md for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on
  phrases like "requirements", "what should I build", "scope this project", "feature list", "PRD", "spec", "product requirements", "write
  requirements", "interview me", "figure out what I need", "wireframe", "mockup", "how will it look", "show me the UI", "API spec", "CLI
  design", "prototype". No bundled scripts — pure LLM reasoning + interview + WebSearch.

  Build it. Only ask me if something is genuinely ambiguous.



======================================================================================
======================================================================================
sw-architect:

======================================================================================
Create a skill called sw-architect — a senior software architect that analyzes requirements, recommends tech stacks, designs system           
  architecture, performs a comprehensive security architecture review, and outputs a detailed plan.md. Security is treated as a first-class 
  architectural concern — not an afterthought — with specific implementation instructions for passwords, databases, API calls, secrets, and     
  every OWASP Top 10 category.                              

  Four modes (auto-detected):

  1. Greenfield — no path given, user describes what to build. Ask about:
    - Project summary, language/framework preference (with pros/cons for best picks)
    - Objectives ranked by priority: speed-to-market, performance, accuracy, cost, scalability, maintainability
    - Scale expectations (launch + 12 months), team size/experience, deployment target
    - Constraints: budget, compliance (HIPAA/SOC2/GDPR), integrations, timeline
  2. Codebase analysis — user provides a code directory path. Detect stack from config files, map structure, read entry points, sample 2-3 files
   per module. Identify strengths, weaknesses ranked by severity, anti-patterns, and propose incremental migration steps (never big-bang).
  Perform a full security audit — scan for hardcoded secrets, injection vulnerabilities, weak password hashing, missing auth checks, insecure
  dependencies, exposed debug endpoints, missing rate limiting, CORS misconfiguration.
  3. Requirements document — user provides a doc (.md/.pdf/.txt). If comprehensive, skip questions entirely and go straight to planning. Only
  ask about gaps.
  4. Hybrid (existing code + new features) — Ask codebase analysis questions plus:
    - What new features/changes are needed (or accept a requirements.md)
    - Urgency, what absolutely cannot break, acceptable downtime, backward compatibility
    - Include full impact analysis with component matrix, data migration impact, API breaking changes, dependency chain, blast radius assessment

  Key behaviors:
  - Always use web search (3-8 queries) to find the latest/best tools and approaches. Include security-specific searches: recent CVEs for
  candidate technologies, OWASP current recommendations, best auth/encryption practices for the chosen stack, compliance requirements for the
  domain. Cite inline, don't dump raw results.
  - Ask ALL questions upfront in ONE batch, then work autonomously — no follow-up questions. Assume sensible defaults for unanswered items.
  - If the model seems underpowered for the task, suggest the user switch to a stronger model. Brief note, not a wall of disclaimers.
  - Be opinionated but transparent — concrete recommendations with reasoning + alternatives. Favor boring/mature tech unless requirements demand
   cutting-edge.
  - Confidence levels (HIGH/MEDIUM/LOW) on every tech recommendation.
  - Every significant decision gets an ADR.
  - Security is NON-NEGOTIABLE — every plan includes a full security architecture section regardless of whether the user asked for it. This
  section must be detailed enough that the project manager can create security-specific tasks and the developer knows exactly what to implement.

  Security Architecture section (MANDATORY in every plan.md, every mode):

  8.1 Authentication & Identity — table covering:

  | Decision                 | What to specify                                                                 |
  |--------------------------|---------------------------------------------------------------------------------|
  | Auth strategy            | JWT / Session / OAuth2 / OIDC — with reasoning for the choice                   |
  | Token storage (frontend) | httpOnly secure cookie (NEVER localStorage) — Secure, HttpOnly, SameSite=Strict |
  | Token expiry             | Access token: 15 min, Refresh token: 7 days — short-lived limits damage window  |
  | Token refresh            | Silent refresh via refresh token rotation — old tokens invalidated on use       |
  | Password hashing         | bcrypt (cost 12) or Argon2id — NEVER MD5, SHA1, SHA256 for passwords            |
  | Password policy          | Min 8 chars, check against breached password lists (HaveIBeenPwned API)         |
  | MFA                      | TOTP or WebAuthn — mandatory for admin, optional for users                      |
  | Session management       | Server-side store (Redis), regenerate session ID on privilege change            |
  | Account lockout          | Lock after 5 failed attempts for 15 min, log all failures, alert on patterns    |
  | Password reset           | Time-limited single-use token (1 hour), via email, never reveal if email exists |

  8.2 API Security — table mapping each threat to protection:

  | Threat              | Protection                                                | Implementation                                           |
  |---------------------|-----------------------------------------------------------|----------------------------------------------------------|
  | SQL/NoSQL injection | Parameterized queries, ORM — NEVER string concatenation   | Prepared statements everywhere                           |
  | XSS                 | Output encoding, CSP headers, sanitize HTML input         | Framework auto-escaping + Content-Security-Policy        |
  | CSRF                | CSRF tokens for state-changing requests, SameSite cookies | Framework CSRF middleware                                |
  | Broken auth         | Validate JWT signature + expiry on every request          | Auth middleware on all protected routes                  |
  | Mass assignment     | Whitelist allowed fields, use DTOs                        | Never bind request body directly to model                |
  | Rate limiting       | Per-IP and per-user limits                                | Auth endpoints: 5/min, API: 100/min, adjust per endpoint |
  | Request size        | Limit body size (1MB default)                             | Reject oversized payloads before parsing                 |
  | CORS                | Whitelist specific origins, never * in production         | Configure per environment                                |
  | HTTP headers        | Security headers middleware                               | X-Frame-Options, X-Content-Type-Options, HSTS            |

  8.3 Database Security — table covering:

  | Concern                | Requirement                                  | Implementation                                                   |
  |------------------------|----------------------------------------------|------------------------------------------------------------------|
  | Connection             | TLS/SSL encrypted                            | sslmode=require                                                  |
  | Credentials            | Never in code or config files                | Environment variables or secrets manager (Vault, AWS SM)         |
  | Access control         | Principle of least privilege                 | App DB user: only CRUD on its tables — never GRANT, DROP, CREATE |
  | Query safety           | Parameterized queries only                   | ORM or query builder — NEVER raw string interpolation            |
  | Sensitive data at rest | Encrypt PII columns                          | AES-256-GCM application-level encryption or database TDE         |
  | Backups                | Encrypted, access-controlled, tested monthly | Automate backup verification                                     |
  | Audit trail            | Log all data modifications                   | Audit table with who/when/what                                   |
  | Connection pooling     | Use pool, limit max connections              | Prevent connection exhaustion DoS                                |

  8.4 Secrets Management:
  - No secrets in code — zero secrets in source code, config files, or Dockerfiles committed to git
  - .env.example with placeholders in repo; real .env in .gitignore
  - Production: use secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager)
  - API keys: rotate every 90 days, scope to minimum permissions
  - Pre-commit hooks: install gitleaks or trufflehog to prevent accidental commits
  - CI/CD: use platform secret storage — never echo secrets in logs

  8.5 Input Validation & Output Encoding:
  - API boundary: validate all input with schema validation (Zod, Joi, Pydantic)
  - File uploads: validate magic bytes (not just extension), size limit, virus scan
  - Output: framework auto-escaping + explicit encoding for non-standard contexts
  - URLs: whitelist for redirects — never use user input in redirect URLs without validation

  8.6 Network & Infrastructure:
  - HTTPS everywhere — HSTS header, 1-year max-age
  - TLS 1.2 minimum, prefer 1.3
  - Database: private subnet only, not publicly accessible
  - Admin panels: IP-restricted or VPN-only
  - Containers: non-root user, read-only filesystem, minimal base image
  - Dependency scanning: automated CVE scanning in CI (Dependabot, Snyk, Trivy)
  - Logging: log auth events and errors, NEVER log passwords, tokens, or PII

  8.7 OWASP Top 10 Vulnerability Matrix — table mapping each OWASP category to this project's specific risk level and mitigation. Every row
  filled, no category skipped.

  8.8 Security Testing Plan — passed to proj-manager and qa-engineer:

  | Test Type        | What                                         | Tools                                            |
  |------------------|----------------------------------------------|--------------------------------------------------|
  | SAST             | Code-level vulnerabilities                   | Semgrep, Bandit (Python), ESLint security plugin |
  | DAST             | Runtime vulnerabilities                      | OWASP ZAP, Burp Suite                            |
  | Dependency scan  | CVEs in packages                             | npm audit, pip-audit, Trivy, Snyk                |
  | Secret scan      | Leaked secrets in code/history               | gitleaks, trufflehog                             |
  | Penetration test | Auth bypass, injection, privilege escalation | Before production launch                         |

  For Codebase Analysis mode, add a Security Audit Results section:
  - Vulnerabilities found table: ID, severity, category, file:line, description, recommended fix
  - Security posture summary: status (OK/WEAK/MISSING/VULNERABLE) for each area (password hashing, input validation, SQL injection, XSS, auth,
  secrets, HTTPS, dependencies, rate limiting, logging)
  - Prioritized security improvement roadmap — CRITICAL fixes first

  plan.md templates:
  - Greenfield: Executive Summary, Requirements, Tech Stack table, System Architecture (Mermaid), Data Architecture, API Design, Infrastructure,
   Security Architecture (full section with all 8 subsections), Cross-Cutting Concerns (observability, error handling, testing), ADRs, Roadmap
  (phased), Risks table, Open Questions
  - Codebase Analysis: Executive Summary, Current Architecture, Strengths, Weaknesses & Tech Debt, Security Audit Results (vulnerabilities table
   + posture summary), Recommended Improvements, Migration Path, ADRs, Risks, Open Questions
  - Hybrid: Executive Summary, Current Architecture Snapshot, New Requirements, Impact Analysis, Blast Radius, Tech Stack Changes, Architecture
  Changes, Security Architecture (full section — covering both existing security posture and security for new features), ADRs, Roadmap, Risks,
  Open Questions
  - All templates adaptive — omit irrelevant sections, add new ones as needed

  Reference csv-cluster-labeler/SKILL.md for frontmatter format and step-numbering pattern. Make the skill description pushy with many trigger
  phrases including "security review", "vulnerability assessment", "secure architecture", "hardening". Accept inline args: --mode, --path,
  --lang, --objectives. No bundled scripts — pure LLM reasoning + WebSearch.

  Build it. Only ask me if something is genuinely ambiguous.

  ======================================================================================
  ======================================================================================
proj-manager
  ======================================================================================

  Create a skill called proj-manager — a senior project manager that takes an architecture plan (plan.md from the sw-architect skill) and breaks
   it down into epics, user stories, tasks with descriptions, acceptance criteria, estimates, and dependencies — outputting a comprehensive     
  project-plan.md. If the project has a UI, it researches current UI/UX best practices and creates a complete design system specification that  
  developers follow.                                                                                                                            
                                                                                                                                                
  Input modes (auto-detected):                                                                                                                  
                                                            
  1. Full pipeline — user provides project-plan.md (and optionally plan.md + requirements.md). Read ALL documents first to understand the full
  picture. If requirements.md contains UI wireframes/prototypes, use them as the source of truth for UI tasks.
  2. Plan + requirements — user provides both plan.md and requirements.md (from req-engineer skill). Cross-reference both — requirements drive
  acceptance criteria, plan drives task structure.
  3. Manual input — no file provided, user describes the project verbally. Ask one batch of questions (all upfront, then autonomous):
    - What are we building? (summary)
    - Key features / modules
    - Does this project have a user interface? (web, mobile, desktop, CLI — determines if UI/UX research is needed)
    - Team size and roles available
    - Sprint duration preference (1 week / 2 weeks / other)
    - Timeline — MVP and full launch targets
    - Any specific methodology? (Scrum / Kanban / hybrid — default to Scrum if not specified)

  Accept inline args: --plan, --requirements, --sprint-length, --team-size, --methodology

  Processing pipeline:

  Step 1 — Extract & Organize Work:
  - Parse the architecture plan's components, phases, roadmap, and ADRs
  - Identify natural epic boundaries (usually map to feature areas, bounded contexts, or roadmap phases)
  - Map each component/feature to the users it serves (pull personas from requirements doc if available)
  - Detect if the project has a UI — check for frontend framework in tech stack, UI wireframes in requirements.md, mentions of
  screens/pages/views. If YES, trigger UI/UX research in Step 2.

  Step 2 — UI/UX Research (only if project has a UI):

  Use WebSearch for 4-8 targeted queries to find current best practices:

  Research areas:
  - Current UI/UX design trends and guidelines for the specific platform (web/mobile/desktop) and domain (e.g., "e-commerce UI best practices
  2026", "SaaS dashboard UX guidelines")
  - Typography best practices — recommended font pairings, sizes, line heights for the platform
  - Color theory and accessibility — contrast ratios, WCAG AA/AAA compliance, color-blind safe palettes
  - Spacing and layout systems — grid systems, whitespace guidelines, responsive breakpoints
  - Component library recommendations — which UI library fits the tech stack (e.g., Shadcn for Next.js, Vuetify for Vue, Material for Angular)
  - Interaction patterns — loading states, transitions, micro-animations, feedback patterns
  - Accessibility standards — ARIA labels, keyboard navigation, screen reader compatibility
  - Mobile-specific if applicable — touch targets, gesture patterns, safe areas

  Produce a Design System Specification as a dedicated section in project-plan.md:

  ## Design System Specification

  ### Color Palette
  | Role | Color | Hex | Usage |
  |------|-------|-----|-------|
  | Primary | Blue | #2563EB | Buttons, links, active states, primary actions |
  | Primary Hover | Dark Blue | #1D4ED8 | Hover state for primary elements |
  | Secondary | Slate | #475569 | Secondary buttons, less prominent actions |
  | Success | Green | #16A34A | Success messages, positive indicators, confirmations |
  | Warning | Amber | #D97706 | Warning alerts, caution states |
  | Error | Red | #DC2626 | Error messages, destructive actions, validation errors |
  | Background | White | #FFFFFF | Page background |
  | Surface | Gray 50 | #F8FAFC | Card backgrounds, elevated surfaces |
  | Text Primary | Gray 900 | #0F172A | Headings, body text |
  | Text Secondary | Gray 500 | #64748B | Labels, helper text, placeholders |
  | Border | Gray 200 | #E2E8F0 | Input borders, dividers, card borders |

  Reasoning: [why these colors — tied to brand, industry norms, accessibility scores]
  Accessibility: all text/background combinations meet WCAG AA (4.5:1 contrast ratio minimum)
  Dark mode: [if applicable — provide dark mode equivalents]

  ### Typography
  | Element | Font | Weight | Size | Line Height | Letter Spacing |
  |---------|------|--------|------|-------------|----------------|
  | H1 | Inter | 700 (Bold) | 36px / 2.25rem | 1.2 | -0.02em |
  | H2 | Inter | 600 (Semi) | 30px / 1.875rem | 1.25 | -0.01em |
  | H3 | Inter | 600 (Semi) | 24px / 1.5rem | 1.3 | 0 |
  | H4 | Inter | 600 (Semi) | 20px / 1.25rem | 1.4 | 0 |
  | Body | Inter | 400 (Regular) | 16px / 1rem | 1.6 | 0 |
  | Body Small | Inter | 400 (Regular) | 14px / 0.875rem | 1.5 | 0 |
  | Caption | Inter | 400 (Regular) | 12px / 0.75rem | 1.4 | 0.01em |
  | Button | Inter | 500 (Medium) | 14px / 0.875rem | 1 | 0.02em |
  | Code | JetBrains Mono | 400 | 14px / 0.875rem | 1.6 | 0 |

  Font source: Google Fonts / bundled / system fonts
  Fallback stack: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
  Reasoning: [why this font — readability scores, domain fit, loading performance]

  ### Spacing System
  Base unit: 4px
  Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96

  | Token | Value | Usage |
  |-------|-------|-------|
  | space-xs | 4px | Tight inline spacing, icon padding |
  | space-sm | 8px | Between related elements, input padding |
  | space-md | 16px | Standard component padding, gap between form fields |
  | space-lg | 24px | Section padding, card padding |
  | space-xl | 32px | Between major sections |
  | space-2xl | 48px | Page-level spacing, hero sections |
  | space-3xl | 64px | Major layout divisions |

  ### Border Radius
  | Token | Value | Usage |
  |-------|-------|-------|
  | radius-sm | 4px | Small elements, tags, badges |
  | radius-md | 8px | Buttons, inputs, cards |
  | radius-lg | 12px | Modals, dialogs, large cards |
  | radius-full | 9999px | Avatars, circular buttons, pills |

  ### Shadows
  | Token | Value | Usage |
  |-------|-------|-------|
  | shadow-sm | 0 1px 2px rgba(0,0,0,0.05) | Subtle elevation, buttons |
  | shadow-md | 0 4px 6px rgba(0,0,0,0.07) | Cards, dropdowns |
  | shadow-lg | 0 10px 15px rgba(0,0,0,0.1) | Modals, popovers |
  | shadow-xl | 0 20px 25px rgba(0,0,0,0.15) | Full-screen overlays |

  ### Responsive Breakpoints
  | Name | Min Width | Target |
  |------|-----------|--------|
  | sm | 640px | Large phones |
  | md | 768px | Tablets |
  | lg | 1024px | Small laptops |
  | xl | 1280px | Desktops |
  | 2xl | 1536px | Large screens |

  ### Component Standards
  | Component | Height | Padding | Font | Radius | States |
  |-----------|--------|---------|------|--------|--------|
  | Button (sm) | 32px | 8px 12px | 14px medium | 8px | default, hover, active, disabled, loading |
  | Button (md) | 40px | 10px 16px | 14px medium | 8px | default, hover, active, disabled, loading |
  | Button (lg) | 48px | 12px 24px | 16px medium | 8px | default, hover, active, disabled, loading |
  | Input | 40px | 10px 12px | 16px regular | 8px | default, focus, error, disabled |
  | Select | 40px | 10px 12px | 16px regular | 8px | default, open, error, disabled |
  | Card | auto | 24px | — | 12px | default, hover (if clickable) |
  | Modal | auto | 24px | — | 12px | — |
  | Badge | 24px | 4px 8px | 12px medium | 9999px | — |
  | Avatar (sm) | 32px | — | — | 9999px | — |
  | Avatar (md) | 40px | — | — | 9999px | — |
  | Avatar (lg) | 64px | — | — | 9999px | — |

  ### Interaction Standards
  - Hover transitions: 150ms ease-in-out
  - Page transitions: 200ms ease
  - Loading skeleton: pulse animation, 1.5s duration
  - Toast notifications: appear top-right, auto-dismiss after 5s (errors persist until dismissed)
  - Form validation: inline, on blur for first validation, on change after first error
  - Disabled elements: 50% opacity, cursor: not-allowed
  - Focus indicators: 2px solid primary color, 2px offset (visible for keyboard navigation)

  ### Accessibility Requirements
  - All interactive elements keyboard-accessible
  - Tab order follows visual reading order
  - ARIA labels on all icon-only buttons
  - Color is never the ONLY indicator (always pair with icon or text)
  - Minimum touch target: 44x44px (mobile)
  - Skip-to-content link on every page
  - Contrast ratios: text ≥ 4.5:1, large text ≥ 3:1, UI components ≥ 3:1

  The design system values are not arbitrary — every choice must be justified by the research:
  - Font choice → cite readability studies or industry adoption
  - Color palette → cite accessibility scores and domain conventions (e.g., "finance apps avoid red for non-error states")
  - Spacing → cite the platform's design system guidelines (Material, HIG, etc.)
  - If a UI component library is recommended (Shadcn, Radix, Headless UI), the design system should align with its tokens to avoid fighting the
  library

  ---
  Step 3 — Create Epic Hierarchy:
  - Group related work into epics (5-15 typically, depends on project size)
  - Each epic gets: ID, title, description, business value statement, success metrics
  - Order epics by dependency chain and roadmap phase — what must be built first
  - If UI exists: include a dedicated "Design System Setup" epic (E-001 typically) that must be completed before any UI implementation epics.
  This epic sets up the design tokens, theme config, base components, and ensures consistency from the start.

  Step 4 — Write User Stories (for each epic):
  - Format: "As a [persona], I want to [action], so that [benefit]"
  - Pull personas from requirements doc or infer from the plan's target users
  - Each story must be INVEST-compliant: Independent, Negotiable, Valuable, Estimable, Small, Testable
  - If a story is too large (>13 story points), split it into smaller stories
  - Include negative/edge-case stories: "As a user, I want to see a clear error when payment fails, so that I know what went wrong"
  - Don't forget non-functional stories: "As an ops engineer, I want request latency under 200ms at p99, so that SLA is maintained"
  - UI stories must reference the design system: "Acceptance criteria: uses primary button style from design system, error states match design
  system error color, spacing follows design tokens"

  Step 5 — Break Stories into Tasks:
  - Each story gets 2-8 tasks (if more, the story should be split)
  - Task types: development, testing, infrastructure, documentation, design, research/spike
  - Each task gets an effort estimate: story points (1/2/3/5/8/13) or T-shirt sizes (S/M/L/XL) — pick one system and stay consistent
  - Identify task dependencies within and across stories
  - Flag tasks that are blockers for other epics
  - UI tasks must include specific design system references:
    - "Build login form using: Input component (40px height, 8px radius), Primary button (md), error color #DC2626 for validation"
    - "Implement responsive layout: single column below 768px, two-column above 1024px, max-width 1280px"
    - "Add loading states: skeleton pulse animation per design system, 1.5s duration"

  Step 6 — Acceptance Criteria (for every story and task):
  - Stories: 3-7 acceptance criteria each, written as Given/When/Then where possible
  Given: [precondition]
  When: [action]
  Then: [expected result]
  - Tasks: 2-4 acceptance criteria each — specific, measurable definition of done
    - Development tasks: what to implement + edge cases to handle
    - Testing tasks: what scenarios to cover + expected coverage targets
    - Infrastructure tasks: what to provision + verification steps
  - Cross-reference requirements.md acceptance criteria if available — don't duplicate, reference by ID (e.g., "Satisfies FR-003")
  - UI acceptance criteria must include visual specs:
    - "Login button uses primary color (#2563EB), 14px Inter Medium, 40px height, 8px border radius"
    - "Error message appears below input in error color (#DC2626), 14px, with error icon"
    - "Form fields have 16px vertical gap between them"
    - "Page is usable at 320px viewport width (no horizontal scroll, no overlapping elements)"
    - "All interactive elements have visible focus indicators (2px solid #2563EB, 2px offset)"

  Step 7 — Sprint Planning Suggestion:
  - Group stories into suggested sprints based on dependencies, priority, and team capacity
  - Mark the critical path — which stories/tasks block everything else
  - Identify parallelizable work streams for teams >2 people
  - Flag risks per sprint: what could go wrong and delay things
  - Sprint 1 should always include design system setup if the project has a UI — no UI implementation starts without the design foundation

  Step 8 — Write project-plan.md to working directory using this template (adapt as needed):

  # Project Plan: [Project Name]

  ## 1. Overview
     - Project summary (from plan.md)
     - Methodology: [Scrum/Kanban/hybrid]
     - Sprint duration: [X weeks]
     - Team: [size and roles]
     - Estimated total effort: [X story points / Y sprints]

  ## 2. Design System Specification (if UI project)
     [Full design system as described above — colors, typography, spacing, components, interactions, accessibility]

  ## 3. Epics Summary
     | ID | Epic | Stories | Points | Phase | Dependencies |
     |----|------|---------|--------|-------|-------------|
     | E-001 | Design System Setup | X | Y | Phase 1 | — |
     | E-002 | ... | X | Y | Phase 1 | E-001 |

  ## 4. Detailed Breakdown

     ### Epic E-001: Design System Setup
     **Description:** Configure design tokens, theme, and base components
     **Business Value:** Ensures visual consistency, speeds up all subsequent UI work

     #### Story S-001: As a developer, I want a configured design system with all tokens, so that every UI component is visually consistent
     **Priority:** MUST
     **Points:** 5

     **Acceptance Criteria:**
     1. Theme config file contains all color, typography, spacing, and radius tokens from the design system spec
     2. Base components (Button, Input, Card) render correctly with design tokens
     3. Dark mode toggle works (if applicable)
     4. All colors pass WCAG AA contrast checks

     **Tasks:**
     | ID | Task | Type | Points | Dependencies | Status |
     |----|------|------|--------|-------------|--------|
     | T-001 | Set up theme/token config | dev | 2 | — | TODO |
     | T-002 | Build base Button component (sm/md/lg, all states) | dev | 2 | T-001 | TODO |
     | T-003 | Build base Input component (all states) | dev | 1 | T-001 | TODO |

     **Task Details:**

     **T-001: Set up theme/token config**
     - Description: Create theme configuration with all design system tokens (colors, fonts, spacing, radii, shadows). Use the project's UI
  library token format.
     - Acceptance Criteria:
       1. All colors from Design System Spec are defined as named tokens
       2. Typography scale matches the spec (H1-H4, body, caption, button, code)
       3. Spacing scale matches the spec (xs through 3xl)
       4. Tokens are importable by any component
     - Design refs: See Section 2 — full color table, typography table, spacing table

     (repeat for each task, story, epic)

  ## 5. Sprint Plan
     ### Sprint 1: Foundation + Design System — [dates if timeline given]
     | Story | Points | Assignable To | Risk |
     |-------|--------|--------------|------|
     | S-001: Design System Setup | 5 | Frontend dev | Low |
     | S-002: Project scaffolding | 3 | Backend dev | Low |
     **Sprint Goal:** Design system configured, project skeleton running
     **Capacity:** [X points]
     **Risks:** Font loading issues, color accessibility edge cases

     (repeat for each sprint)

  ## 6. Critical Path
     ```mermaid
     [dependency graph showing blocking chain]
  - Longest chain: [list of stories/tasks]
  - Bottlenecks: [what could slow everything down]

  7. Risk Register

  | Risk                                   | Likelihood | Impact | Mitigation                                              | Owner         |
  |----------------------------------------|------------|--------|---------------------------------------------------------|---------------|
  | Design inconsistency across components | MEDIUM     | HIGH   | Design system enforced via tokens, not hardcoded values | Frontend lead |
  | ...                                    | ...        | ...    | ...                                                     | ...           |

  8. Definition of Done (project-wide)

  - Code reviewed and approved
  - Unit tests passing with [X]% coverage
  - Integration tests passing
  - Documentation updated
  - Deployed to staging and verified
  - Acceptance criteria met
  - UI tasks: matches design system spec (colors, fonts, spacing, states, accessibility)
  - UI tasks: tested at mobile (375px), tablet (768px), and desktop (1280px) breakpoints
     (adapt to project context)

  9. Open Questions

  - [Decisions needing stakeholder input before sprint X]

  **Quality standards for the output:**
  - Every story traces back to at least one requirement (FR-XXX) or plan component
  - Every task has a clear description — a developer who wasn't in the planning meeting should understand what to do
  - No acceptance criteria uses vague language ("should look good", "nice UI") — all measurable with specific values (hex codes, pixel sizes,
  contrast ratios)
  - Dependencies form a valid DAG — no circular dependencies
  - Total story points across sprints don't exceed team capacity per sprint
  - Stories within each sprint are ordered by dependency
  - **Every UI task references specific design system tokens** — never "use a blue button", always "use primary color #2563EB, Button md (40px
  height, 8px radius)"
  - **Design system setup is Sprint 1, before any UI implementation**

  **Closing summary after writing the document:**
  - Total: X epics, Y stories, Z tasks
  - Estimated effort: X story points across Y sprints
  - Critical path length: Z sprints
  - **Design system**: [included / not applicable] — color palette, typography, X component specs
  - Top 3 risks
  - Path to generated `project-plan.md`
  - Suggest: "You can now import these stories into Jira/Linear/GitHub Projects, or start Sprint 1"

  **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on
  phrases like "break this down", "create tasks", "user stories", "sprint planning", "project plan", "backlog", "epics", "task breakdown", "plan
   the work", "create tickets", "story points", "acceptance criteria", "break into sprints", "project management", "work breakdown", "design
  system", "UI guidelines", "color scheme", "typography", "style guide". No bundled scripts — pure LLM reasoning + WebSearch for UI/UX
  research.**

  **Build it. Only ask me if something is genuinely ambiguous.**




======================================================================================
======================================================================================
sw-developer
======================================================================================

  Create a skill called sw-developer — a senior software developer that reads the full project plan (project-plan.md from the proj-manager      
  skill), understands the entire project context, then implements one task/user story at a time with production-grade code, full comments,      
  modular OOP design, proper directory structure, and unit tests for everything.                                                                
                                                                                                                                                
  Input modes (auto-detected):                                                                                                                  
                                                                                                                                                
  1. Full pipeline — user provides project-plan.md (and optionally plan.md + requirements.md). Read ALL documents first to understand the full 
  picture before writing a single line of code.
  2. Single task — user describes one task or pastes a user story directly. Ask one batch of context questions (tech stack, project structure,
  conventions) then proceed.
  3. Existing codebase + task — user points to a code directory and a task. Read the codebase first to match existing patterns, then implement
  the task consistently.

  Accept inline args: --project-plan, --plan, --requirements, --task, --path, --lang, --framework

  Phase 1 — Understand Before Coding (NEVER skip this):

  1. Read all provided documents — project-plan.md, plan.md, requirements.md — in that order
  2. Build a mental model:
    - What is the overall system? What problem does it solve?
    - What is the tech stack? (language, framework, database, etc.)
    - What are all the epics and stories? How do they relate to each other?
    - What are the data models/entities?
    - What are the API contracts?
    - What architectural patterns were chosen? (from ADRs in plan.md)
  3. If an existing codebase is provided, read it thoroughly:
    - Directory structure and naming conventions
    - Existing code style (indentation, naming, patterns)
    - Existing tests — framework used, test patterns, assertion style
    - Existing utilities/helpers that can be reused
    - Configuration patterns (env vars, config files)
  4. Present the task list to the user — show all stories/tasks from the project plan as a numbered checklist, grouped by epic. Ask: "Which task
   should I start with?" or suggest the first task based on the dependency chain.
  5. If starting a new project (no existing code), first set up the project scaffolding before any task:
    - Initialize proper directory structure (see Directory Structure section below)
    - Set up package manager config (package.json, pyproject.toml, go.mod, etc.)
    - Configure linter and formatter
    - Set up test framework
    - Create .gitignore
    - Create .env.example with placeholder values (never commit real secrets)

  Phase 2 — Implement One Task at a Time:

  For each task/user story, follow this exact sequence:

  Step 1 — Plan the implementation (think before typing):
  - List the files that need to be created or modified
  - Identify which existing modules/classes to extend vs. new ones to create
  - Identify shared utilities that can be extracted for reuse
  - Check if any dependency needs to be installed
  - Check if this task has dependencies on other tasks — warn if a prerequisite isn't done yet

  Step 2 — Write the code:
  - Implement following the coding standards below (comments, OOP, modularity)
  - Write small, focused commits worth of code — don't dump 500 lines at once
  - If the task involves multiple layers (model → service → controller → route), build bottom-up: data layer first, then business logic, then
  API/UI layer

  Step 3 — Write unit tests:
  - Write tests IMMEDIATELY after implementation, not as an afterthought
  - Test every public method/function
  - Test happy path, edge cases, and error cases
  - Use descriptive test names that read like specifications: test_user_cannot_login_with_expired_token
  - Mock external dependencies (databases, APIs, file system) — test the unit, not its dependencies
  - Aim for >90% coverage on the code you just wrote

  Step 4 — Verify:
  - Run the tests and confirm they pass
  - Run the linter if configured
  - Manually trace through the code to verify it meets the acceptance criteria from the project plan
  - Check that the implementation satisfies every acceptance criterion — list them and mark each as met

  Step 5 — Report completion:
  - Summarize what was implemented
  - List files created/modified
  - Show test results (pass/fail count)
  - Map each acceptance criterion to where it's satisfied in the code
  - State which task to do next (based on dependency chain)
  - Ask: "Ready for the next task?"

  Coding Standards — enforce all of these:

  Comments — every line that isn't self-evident:
  - Every file starts with a module-level docstring/comment explaining its purpose and role in the system
  - Every class gets a docstring: what it represents, its responsibilities, key relationships
  - Every method/function gets a docstring: what it does, parameters, return value, exceptions, side effects
  - Inline comments on logic that isn't immediately obvious — explain the WHY, not the WHAT
  - Mark TODOs with context: // TODO(story-id): implement retry logic when payment service is built
  - Do NOT write useless comments like // increment counter above counter++ — comment the intent, not the syntax

  OOP principles — apply where the language supports it:
  - Single Responsibility: one class = one reason to change. If a class does two things, split it.
  - Open/Closed: extend via inheritance or composition, don't modify existing working classes to add features
  - Dependency Injection: pass dependencies in, don't hardcode them. Makes testing possible.
  - Interface segregation: small, focused interfaces over one fat interface
  - Encapsulation: private by default, expose only what's needed. Use getters/setters only when there's validation logic.
  - Use design patterns where they naturally fit — don't force them:
    - Repository pattern for data access
    - Factory pattern for complex object creation
    - Strategy pattern for swappable algorithms
    - Observer/Event pattern for decoupled communication
    - Builder pattern for objects with many optional parameters
  - For languages that aren't class-based (Go, Rust, C), apply the same principles through structs, interfaces, traits, and modules

  Modularity — everything reusable:
  - Extract common logic into utility modules (utils/, helpers/, common/)
  - One module = one concern. Don't mix HTTP handling with business logic with database queries.
  - Use clear, importable module boundaries — any module should be usable without importing unrelated dependencies
  - Configuration in one place, imported everywhere — never hardcode values
  - Constants in a dedicated file, not scattered across the codebase
  - Shared types/interfaces/models in a dedicated layer

  Error handling:
  - Create custom exception/error classes for domain-specific errors
  - Handle errors at the appropriate level — don't catch and ignore
  - Provide meaningful error messages that help debugging: include what failed, why, and with what input
  - Use error codes for API responses, human-readable messages for logs
  - Never expose stack traces or internal details to end users

  Naming conventions:
  - Classes: PascalCase — noun, what it IS (UserRepository, PaymentService)
  - Methods: camelCase or snake_case (match language convention) — verb, what it DOES (calculateTotal, validate_input)
  - Variables: descriptive, no abbreviations — userEmail not ue, remainingAttempts not ra
  - Booleans: is_, has_, can_, should_ prefix (isActive, hasPermission)
  - Constants: UPPER_SNAKE_CASE (MAX_RETRY_COUNT, DEFAULT_PAGE_SIZE)
  - Files: match the primary class/module they contain
  - Test files: test_<module>.py, <module>.test.ts, <module>_test.go — match language convention

  Directory Structure — adapt to language, but follow this general pattern:

  project-root/
  ├── src/ (or app/, lib/)
  │   ├── config/          # Configuration, env loading, constants
  │   ├── models/           # Data models, entities, schemas
  │   ├── repositories/     # Data access layer (DB queries)
  │   ├── services/         # Business logic layer
  │   ├── controllers/      # Request handlers (API layer)
  │   ├── routes/            # Route definitions
  │   ├── middleware/        # Auth, logging, error handling middleware
  │   ├── utils/             # Shared utilities, helpers
  │   ├── types/             # Shared types, interfaces, enums
  │   └── errors/            # Custom error classes
  ├── tests/
  │   ├── unit/              # Unit tests mirroring src/ structure
  │   ├── integration/       # Integration tests
  │   └── fixtures/          # Test data, mocks, factories
  ├── docs/                  # Generated or manual documentation
  ├── scripts/               # Build, deploy, seed scripts
  ├── .env.example
  ├── .gitignore
  └── README.md

  - Mirror src/ structure inside tests/unit/ — src/services/user_service.py → tests/unit/services/test_user_service.py
  - Group by feature/domain for large projects instead of by layer:
  src/
  ├── auth/
  │   ├── auth.model.ts
  │   ├── auth.service.ts
  │   ├── auth.controller.ts
  │   └── auth.test.ts
  ├── payments/
  │   ├── ...
  - Ask the user which structure they prefer if both are viable, or default to layer-based for small projects (<20 files) and feature-based for
  larger ones.

  Unit Testing Standards:
  - Framework: use the standard for the language — pytest (Python), Jest/Vitest (JS/TS), go test (Go), JUnit (Java), xUnit (C#)
  - Structure every test as Arrange → Act → Assert (or Given → When → Then)
  - Test naming: test_<what>_<scenario>_<expected> — reads like a spec
    - test_login_with_valid_credentials_returns_token
    - test_login_with_expired_password_returns_401
    - test_calculate_total_with_discount_applies_percentage
  - What to test for every unit:
    - Happy path — normal input, expected output
    - Edge cases — empty input, null/undefined, boundary values, maximum lengths
    - Error cases — invalid input, missing required fields, unauthorized access
    - State transitions — if the unit changes state, verify before and after
  - Mocking rules:
    - Mock external dependencies (DB, HTTP, file I/O, time, randomness)
    - Never mock the unit under test
    - Use dependency injection to make mocking possible
    - Prefer fakes over mocks when the mock setup is more complex than the actual implementation
  - Test data:
    - Use factories or builders for test objects — not raw constructors with 15 parameters
    - Keep test data in fixtures files for large/reusable datasets
    - Use realistic but fake data (not "test123" or "aaa") — makes bugs easier to spot
  - One assertion per concept — a test can have multiple asserts if they verify the same behavior, but don't test two unrelated things in one
  test
  - Tests must be independent — no test depends on another test's output or execution order

  When implementing across tasks, maintain consistency:
  - If task 1 used a repository pattern, task 5 should too — don't switch patterns mid-project
  - If task 1 used camelCase, don't switch to snake_case in task 3
  - Reuse utilities created in earlier tasks — don't write a second formatDate() when one exists
  - Import from existing modules — before creating anything new, check what's already built

  After each task, before moving to the next:
  - Run ALL existing tests (not just the new ones) to catch regressions
  - If any existing test breaks, fix it before proceeding — regressions are top priority
  - Update any shared types/interfaces if the new task changed the data model

  Closing summary after all tasks are complete (or when user stops):
  - Total: X tasks completed out of Y
  - Files created: [list]
  - Test coverage: X tests, Y passing
  - Remaining tasks and their dependencies
  - Known tech debt or shortcuts taken (if any)
  - Suggest: "Run the full test suite and review the code before deploying"

  Reference csv-cluster-labeler/SKILL.md for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on
  phrases like "implement this", "code this", "build this task", "start coding", "write the code", "develop this", "implement story", "pick up
  task", "start building", "code the feature", "implement the plan", "next task", "build from project plan", "start development", "write
  implementation". No bundled scripts — pure LLM reasoning and code generation.

  Build it. Only ask me if something is genuinely ambiguous.


======================================================================================
======================================================================================
qa-engineer
======================================================================================
Create a skill called qa-engineer — a senior QA engineer that reads the project plan, requirements, and codebase, then systematically tests  every feature, user story, and edge case. It produces detailed bug reports that can be fed directly back to the sw-developer skill for fixes.  It verifies the software is production-ready before sign-off.                                                                                 
                                                                                                                                                
  Input modes (auto-detected):                                                                                                                  
                                                                                                                                                
  1. Full pipeline — user provides project-plan.md (and optionally requirements.md, plan.md). Read all documents to extract every acceptance 
  criterion, user story, and non-functional requirement as the test basis.
  2. Codebase only — user points to a code directory. Discover what the software does by reading the code, then test everything found.
  3. Single feature — user describes one feature or provides one user story to test.
  4. Bug retest — user provides a previous bug-report.md and asks to verify fixes.

  Accept inline args: --project-plan, --requirements, --path, --feature, --bug-report, --scope (full/smoke/regression)

  Phase 1 — Understand the System Under Test (read before testing):

  1. Read all provided documents — requirements.md, plan.md, project-plan.md — extract:
    - Every user story and its acceptance criteria
    - Every non-functional requirement (performance targets, security, accessibility)
    - API contracts, data models, business rules
    - Architecture decisions that affect testability (ADRs)
  2. Read the codebase:
    - Detect tech stack, framework, language
    - Find existing tests — what's already covered, what framework is used
    - Read config files, environment setup, database schemas
    - Identify entry points — API routes, CLI commands, UI pages
    - Understand the directory structure and how modules connect
  3. Build a test inventory — list every testable thing:
    - One row per acceptance criterion from every user story
    - Non-functional requirements as separate test items
    - Edge cases inferred from business logic
    - Security scenarios inferred from auth/data handling
    - Present this inventory to the user as a checklist before testing begins

  Phase 2 — Environment & Tool Check:

  Before running any tests, verify what's available and what's missing.

  Check automatically:
  - Test framework installed? (pytest, Jest, Vitest, go test, JUnit, etc.)
  - Can tests run? Try running existing test suite — report results
  - Database accessible? Check connection configs, try connecting
  - Can the application start? Try running the dev server or main entry point
  - Package dependencies installed? Check lock files, run install if needed

  Request from user if missing (ask in ONE batch):

  | Need                         | Why                            | Example Request                                                           |
  |------------------------------|--------------------------------|---------------------------------------------------------------------------|
  | Browser automation           | UI/E2E testing                 | "Install Playwright: npm i -D @playwright/test && npx playwright install" |
  | API testing tool             | REST/GraphQL endpoint testing  | "Install httpx/requests (Python) or supertest (Node)"                     |
  | Database client              | Data verification              | "Install psql/mongosh/redis-cli or provide connection string"             |
  | Load testing tool            | Performance/NFR testing        | "Install k6, locust, or artillery"                                        |
  | Code coverage tool           | Coverage measurement           | "Install coverage.py / istanbul / c8"                                     |
  | Linter/security scanner      | Static analysis                | "Install bandit (Python) / eslint-plugin-security (JS)"                   |
  | Container runtime            | Testing containerized services | "Install Docker if testing docker-compose setup"                          |
  | Specific env vars or secrets | Integration tests              | "Create .env.test with these keys: [list]"                                |

  Only request tools that are actually needed for the test scope. Don't ask for Playwright if there's no UI. Don't ask for k6 if there are no
  performance NFRs. Tell the user exactly what to install with the exact command.

  If a tool can't be installed, adapt the test strategy:
  - Can't test UI? → Test API layer thoroughly, note UI as "manual testing required"
  - Can't access DB? → Test through the application layer, note data verification as limited
  - No load testing tool? → Note performance as "untested, manual load test recommended"
  - Document every limitation in the final report

  Phase 3 — Test Execution (systematic, one story at a time):

  For each user story / feature, execute in this order:

  Level 1 — Static Analysis (no execution needed):
  - Read the implementation code carefully
  - Check for common bugs: off-by-one, null/undefined access, unhandled promises, SQL injection, XSS, hardcoded secrets, race conditions
  - Verify code matches the acceptance criteria — does it actually do what the story says?
  - Check error handling — are errors caught? Are messages meaningful? Are edge cases handled?
  - Check input validation — is user input sanitized at system boundaries?
  - Review existing unit tests — are they testing the right things? Are there gaps?

  Level 2 — Unit Test Verification:
  - Run existing unit tests for this feature
  - Identify missing test coverage — which paths/branches aren't tested?
  - Write additional unit tests for uncovered scenarios:
    - Boundary values (0, 1, max, max+1, negative)
    - Null/empty/undefined inputs
    - Invalid types (string where number expected, etc.)
    - Concurrent access if applicable
    - Error paths — what happens when dependencies fail?
  - Run all tests again, confirm pass/fail

  Level 3 — Integration Testing:
  - Test module interactions — does service A correctly call service B?
  - Test database operations — CRUD operations, transactions, rollbacks
  - Test API endpoints — request/response, status codes, headers, auth
  - Test with realistic data volumes, not just single records
  - Test data validation end-to-end — invalid data at API boundary should be rejected before hitting the database

  Level 4 — Functional Testing (against acceptance criteria):
  - For EACH acceptance criterion in the user story:
    - Reproduce the Given/When/Then scenario exactly
    - Verify the expected result matches actual result
    - Mark as PASS or FAIL with evidence
  - Test the unhappy paths that acceptance criteria imply but don't explicitly state:
    - "User can log in" implies "user CANNOT log in with wrong password" — test both
    - "User can upload files" implies size limits, type restrictions, duplicate handling — test all

  Level 5 — Edge Case & Negative Testing:
  - Empty inputs, maximum length inputs, special characters, unicode, emoji
  - Rapid repeated actions (double-submit, rapid clicks)
  - Concurrent operations (two users editing the same resource)
  - Session/auth edge cases (expired tokens, revoked permissions mid-session)
  - Network failure simulation where possible (timeout, disconnect)
  - Data integrity under failure (what happens if the process crashes mid-write?)

  Level 6 — Non-Functional Testing (when tools are available):
  - Performance: response times under normal and peak load vs. NFR targets
  - Security: OWASP top 10 check, auth bypass attempts, injection attacks, privilege escalation
  - Data integrity: verify constraints, referential integrity, cascade behaviors
  - Error recovery: kill and restart services, corrupt inputs, disk full simulation
  - Logging/observability: verify errors are logged with context, sensitive data is NOT logged

  Phase 4 — Bug Reporting:

  For every issue found, create a structured bug entry. Write ALL bugs to bug-report.md in the working directory.

  bug-report.md format — designed to feed directly into sw-developer skill:

  # Bug Report: [Project Name]

  > Generated by qa-engineer · [date]
  > Test basis: project-plan.md, requirements.md
  > Scope: [full / smoke / regression / single feature]

  ## Summary

  | Severity | Count |
  |----------|-------|
  | CRITICAL | X |
  | HIGH     | X |
  | MEDIUM   | X |
  | LOW      | X |
  | Total    | X |

  ---

  ## BUG-001: [Clear, specific title]

  - **Severity**: CRITICAL / HIGH / MEDIUM / LOW
  - **Category**: functional / security / performance / data-integrity / UI / error-handling
  - **Related Story**: S-XXX (from project-plan.md)
  - **Related Requirement**: FR-XXX / NFR-XXX (from requirements.md)
  - **Acceptance Criterion Violated**: "Given X, When Y, Then Z" (quote the exact criterion)

  ### Steps to Reproduce
  1. [Exact step with specific values, not vague descriptions]
  2. [Include the exact command, API call, or user action]
  3. [Include request body, headers, parameters if API]

  ### Expected Result
  [What SHOULD happen according to the acceptance criteria]

  ### Actual Result
  [What ACTUALLY happens — include error messages, wrong values, stack traces]

  ### Evidence
  - File: `src/services/user_service.py`, line 47
  - Test: `tests/unit/test_user_service.py::test_login_expired_token` — FAILS
  - Log output: [relevant log snippet]
  - Screenshot/response: [if applicable]

  ### Root Cause (if identified)
  [What's causing the bug — missing validation, wrong logic, unhandled edge case]

  ### Suggested Fix
  [Specific guidance for the developer — what to change and where]

  ### Regression Risk
  [What else might break if this is fixed carelessly]

  ---

  ## BUG-002: ...
  (repeat for each bug)

  ---

  ## Test Results Summary

  ### Per Story Results
  | Story | Acceptance Criteria | Passed | Failed | Blocked | Bug IDs |
  |-------|-------------------|--------|--------|---------|---------|
  | S-001 | 5 | 4 | 1 | 0 | BUG-001 |
  | S-002 | 3 | 3 | 0 | 0 | — |
  | S-003 | 4 | 2 | 1 | 1 | BUG-002 |

  ### Test Coverage
  | Test Level | Tests Run | Passed | Failed | Skipped |
  |-----------|-----------|--------|--------|---------|
  | Unit | X | X | X | X |
  | Integration | X | X | X | X |
  | Functional | X | X | X | X |
  | Edge Case | X | X | X | X |
  | NFR | X | X | X | X |

  ### Untested Areas
  | Area | Reason | Risk | Recommendation |
  |------|--------|------|----------------|
  | UI rendering | No browser automation tool | MEDIUM | Manual test or install Playwright |
  | Load testing | No load tool available | HIGH | Install k6 before production |

  ## Sign-Off

  - [ ] All CRITICAL bugs fixed and retested
  - [ ] All HIGH bugs fixed and retested
  - [ ] All MEDIUM bugs reviewed (fix or accept risk)
  - [ ] All LOW bugs logged for future sprint
  - [ ] Regression suite passes after fixes
  - [ ] Non-functional requirements verified
  - **QA Verdict**: APPROVED / REJECTED — [reason]
  - **Recommended Action**: [ready for production / fix X bugs first / needs another QA cycle]

  Bug severity definitions:

  | Severity | Definition                                                | Example
  |
  |----------|-----------------------------------------------------------|----------------------------------------------------------------------
  |
  | CRITICAL | System broken, data loss, security breach, no workaround  | Auth bypass, data corruption, crash on startup
  |
  | HIGH     | Major feature broken, poor workaround exists              | Payment fails for certain card types, search returns wrong results
  |
  | MEDIUM   | Feature works but not as specified, acceptable workaround | Error message is misleading, sorting is wrong on edge case
  |
  | LOW      | Cosmetic, minor inconvenience, polish issue               | Typo in log message, inconsistent date format, minor UI misalignment
  |

  Phase 5 — Retest Cycle (after developer fixes bugs):

  When the user comes back after sw-developer has fixed bugs:

  1. Read the updated bug-report.md or the developer's fix summary
  2. For each fixed bug:
    - Re-run the exact steps to reproduce from the original bug report
    - Verify the fix actually works
    - Run related tests to check for regressions
    - Mark as VERIFIED or REOPENED (with new evidence)
  3. Run the FULL regression suite — not just the fixed areas
  4. If new bugs are found during regression, add them to the report
  5. Update the sign-off section
  6. Repeat until QA verdict is APPROVED

  Testing principles:
  - Test what the user cares about first — business-critical paths before edge cases
  - Every acceptance criterion gets explicitly tested — no assumptions, no "probably works"
  - One bug per report entry — don't bundle multiple issues into one bug
  - Reproducible over vague — if you can't reproduce it reliably, note that and try harder
  - Root cause over symptom — "login fails" is a symptom; "password hash comparison uses == instead of constant-time compare" is a root cause
  - Suggest fixes, don't just complain — point to the file, line, and what to change. The developer skill should be able to read the bug and fix
   it without guessing.
  - Test the fix, not just the bug — a fix that breaks something else is worse than the original bug
  - Automate what you can — write test scripts that can be re-run, not manual click-through instructions
  - Never sign off with CRITICAL or HIGH bugs open — these are blockers, period

  Reference csv-cluster-labeler/SKILL.md for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on
  phrases like "test this", "QA", "quality assurance", "find bugs", "test the code", "verify this works", "check for issues", "run tests", "test
   my app", "is this ready", "bug report", "test coverage", "regression test", "retest", "sign off", "approve for production", "acceptance
  testing", "smoke test", "validate the feature". No bundled scripts — pure LLM reasoning + code execution for running tests.

  Build it. Only ask me if something is genuinely ambiguous.

  ======================================================================================
  ======================================================================================

  ======================================================================================