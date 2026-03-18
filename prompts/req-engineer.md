# Prompt: req-engineer

> **Create a skill called `req-engineer` — a senior requirements engineer that interviews the user, extracts complete requirements, and outputs a comprehensive `requirements.md` with visual prototypes (UI wireframes, CLI interaction examples, API request/response samples) so the user can see exactly what they're getting before any code is written. The output feeds directly into the `sw-architect` skill.**
>
> **How it works — a structured interview in 2-3 rounds max:**
>
> **Round 1 — Understanding the Vision:**
> - What are you building? (elevator pitch)
> - Who are the end users? (personas, roles, technical level)
> - What problem does this solve? What's the current workaround?
> - What does success look like? (measurable outcomes)
> - Any existing systems this replaces or integrates with?
> - **Interface type** — is this a web app, mobile app, desktop app, CLI tool, API service, background worker, or a combination? (this determines which prototype format to use)
>
> **Round 2 — Deep Dive (adapt questions based on Round 1 answers, skip what's already clear):**
> - Core user journeys — walk me through the 3-5 most important things a user does
> - What data does the system handle? (types, volume, sensitivity, retention)
> - Who are the stakeholders beyond end users? (admins, ops, compliance, analytics)
> - Scale expectations — users, requests, data volume at launch and 12 months out
> - Performance expectations — response times, availability, uptime targets
> - Security & compliance — authentication needs, data regulations (GDPR/HIPAA/SOC2), audit requirements
> - Deployment preferences — cloud/on-prem/hybrid, regions, offline capability
> - Budget and timeline — MVP deadline, full launch target, team size
> - Constraints — must-use technologies, organizational policies, vendor lock-in concerns
>
> **Round 3 (only if needed) — Clarifying Gaps:**
> - If Rounds 1-2 left ambiguities or contradictions, ask targeted follow-ups — max 5 questions
> - If everything is clear, skip this round entirely and proceed to writing
>
> **Interview behavior:**
> - **Think like a real requirements engineer** — ask "why" behind feature requests to uncover actual needs vs. assumed solutions. If user says "I need a Redis cache", ask what problem they're solving — maybe they need caching, maybe they don't.
> - **Spot contradictions** — if user says "real-time" but also "batch processing", probe which it actually is or if both are needed for different features.
> - **Suggest what they forgot** — based on the domain, proactively ask about commonly overlooked areas: error handling, notification preferences, admin/back-office needs, reporting, onboarding flow, data migration, accessibility.
> - **No jargon dumping** — match the user's technical level. If they say "I want an app for my bakery", don't ask about "eventual consistency models".
> - **Prioritization** — ask the user to rank features as Must-Have / Should-Have / Nice-to-Have (MoSCoW) or let them just describe importance and you categorize.
> - **Accept any input format** — user can paste bullet points, ramble in paragraphs, share screenshots, or just talk. Extract structure from chaos.
> - **Accept inline args**: `--project`, `--domain`, `--scale`, `--deadline`, `--interface` (web/cli/api/mobile/desktop) to pre-fill known answers.
>
> **After the interview, use WebSearch (2-4 queries) to:**
> - Validate domain-specific requirements the user may have missed (e.g., "PCI-DSS requirements for payment processing")
> - Check industry standards for the domain (e.g., healthcare → HL7/FHIR, finance → FIX protocol)
> - Find common pitfalls in similar products
>
> **Then generate `requirements.md` in the working directory using this template (adapt as needed):**
>
> ```
> # Requirements Document: [Project Name]
>
> ## 1. Project Overview
>    - Vision statement (2-3 sentences)
>    - Problem statement
>    - Target users and personas
>    - Success metrics
>
> ## 2. Scope
>    - In scope (what this project covers)
>    - Out of scope (explicitly excluded — prevents scope creep)
>    - Future considerations (parked for later)
>
> ## 3. Functional Requirements
>    ### 3.1 [Feature Area]
>    - FR-001: [Requirement] — Priority: MUST/SHOULD/COULD
>    - FR-002: ...
>    (Group by feature area/domain, each with unique ID)
>
> ## 4. User Journeys
>    ### Journey 1: [Name]
>    - Actor, trigger, steps, expected outcome, error scenarios
>
> ## 5. Interface Prototypes
>    (See "Interface Prototypes" section below for format per interface type)
>
> ## 6. Non-Functional Requirements
>    - NFR-001: Performance — [specific targets: response time, throughput]
>    - NFR-002: Scalability — [growth targets]
>    - NFR-003: Availability — [uptime SLA]
>    - NFR-004: Security — [auth, encryption, compliance]
>    - NFR-005: Accessibility — [WCAG level if applicable]
>    - NFR-006: Data — [retention, backup, privacy]
>
> ## 7. Integrations
>    - External systems, APIs, third-party services, data imports/exports
>
> ## 8. Constraints
>    - Technical, business, regulatory, timeline, budget
>
> ## 9. Assumptions
>    - What was assumed when not explicitly stated by the user
>
> ## 10. Risks & Open Questions
>    - Identified risks from the interview
>    - Unresolved questions needing stakeholder input
>
> ## 11. Glossary
>    - Domain-specific terms defined (only if the domain has jargon)
>
> ## 12. Appendix
>    - Raw notes, references, research findings
> ```
>
> ---
>
> **Interface Prototypes — the section that lets users SEE what they're getting:**
>
> Auto-detect the interface type from the interview and generate the appropriate prototype format. If the project has multiple interfaces (e.g., web app + API + admin CLI), generate prototypes for ALL of them.
>
> ### For Web / Mobile / Desktop UI:
>
> Generate ASCII wireframes for every key screen, showing layout, components, and user flow.
>
> ```
> ### Screen: Login Page
> Triggered by: User opens the app / session expired
> Related: FR-001, FR-002
>
> ┌─────────────────────────────────────────────┐
> │  ┌─────────────────────────────────────────┐ │
> │  │         🏪  BakeryManager              │ │
> │  └─────────────────────────────────────────┘ │
> │                                               │
> │  ┌─────────────────────────────────────────┐ │
> │  │  Email    [_________________________]   │ │
> │  │  Password [_________________________]   │ │
> │  │                                         │ │
> │  │  [✓] Remember me                        │ │
> │  │                                         │ │
> │  │  [ Login ]          Forgot password?    │ │
> │  │                                         │ │
> │  │  ─────── or ───────                     │ │
> │  │                                         │ │
> │  │  [ Sign up with Google ]                │ │
> │  └─────────────────────────────────────────┘ │
> └─────────────────────────────────────────────┘
>
> Behavior:
> - Empty email → inline error: "Email is required"
> - Wrong password → "Invalid email or password" (no hint which is wrong)
> - 5 failed attempts → account locked for 15 minutes, show countdown
> - Success → redirect to Dashboard (see Screen: Dashboard)
> - "Forgot password?" → Screen: Password Reset
> ```
>
> **For each screen, include:**
> - ASCII wireframe showing layout with actual field names, buttons, labels
> - Which FR-XXX requirements this screen satisfies
> - Step-by-step behavior: what happens on each user action
> - Validation rules: what errors appear and when
> - Navigation: where each button/link goes (reference other screens by name)
> - States: empty state, loading state, error state, success state
> - Responsive notes: how it adapts on mobile (if web app)
>
> **Generate wireframes for:**
> - Every screen in the main user journey (minimum)
> - Admin/settings screens if they have unique complexity
> - Error pages (404, 500, maintenance)
> - Empty states (no data yet, first-time user)
>
> **Screen flow diagram (Mermaid) showing navigation between screens:**
> ```mermaid
> graph LR
>     Login --> Dashboard
>     Dashboard --> OrderList
>     OrderList --> OrderDetail
>     OrderDetail --> EditOrder
>     Dashboard --> Settings
>     Settings --> Profile
>     Settings --> Billing
> ```
>
> ### For CLI Tools:
>
> Show exact terminal interactions with realistic example data for every command.
>
> ```
> ### Command: bakery-cli add-product
> Related: FR-005
>
> $ bakery-cli add-product
>
> Product name: Sourdough Loaf
> Category (bread/pastry/cake/other): bread
> Price: 8.50
> Cost to make: 3.20
> Daily capacity: 50
> Available days (Mon-Sun, comma-separated): Mon,Tue,Wed,Thu,Fri,Sat
>
> ✓ Product added: Sourdough Loaf
>   ID:       PRD-0042
>   Margin:   62.4%
>   Schedule: Mon-Sat
>
> ---
>
> ### Command: bakery-cli add-product (with errors)
>
> $ bakery-cli add-product
>
> Product name:
> ✗ Error: Product name cannot be empty
>
> Product name: Sourdough Loaf
> Category (bread/pastry/cake/other): pizza
> ✗ Error: Invalid category "pizza". Choose from: bread, pastry, cake, other
>
> Category (bread/pastry/cake/other): bread
> Price: -5
> ✗ Error: Price must be a positive number
>
> Price: 8.50
> ...
>
> ---
>
> ### Command: bakery-cli list-products
> Related: FR-006
>
> $ bakery-cli list-products
>
> ID        │ Name              │ Category │ Price  │ Margin │ Schedule
> ──────────┼───────────────────┼──────────┼────────┼────────┼──────────
> PRD-0001  │ Croissant         │ pastry   │ $4.50  │ 58.2%  │ Daily
> PRD-0012  │ Baguette          │ bread    │ $6.00  │ 55.0%  │ Mon-Sat
> PRD-0042  │ Sourdough Loaf    │ bread    │ $8.50  │ 62.4%  │ Mon-Sat
>
> Total: 3 products
>
> $ bakery-cli list-products --category pastry --sort margin
>
> ID        │ Name              │ Price  │ Margin
> ──────────┼───────────────────┼────────┼────────
> PRD-0001  │ Croissant         │ $4.50  │ 58.2%
>
> Total: 1 product
>
> ---
>
> ### Command: bakery-cli list-products (empty state)
>
> $ bakery-cli list-products
>
> No products found. Add your first product:
>   bakery-cli add-product
> ```
>
> **For each command, include:**
> - Full command syntax with all flags/options: `bakery-cli add-product [--name NAME] [--category CAT] [--json]`
> - Happy path example with realistic data
> - Error examples: every validation error with exact error message
> - Empty state: what shows when there's no data
> - Output formats: table (default), JSON (`--json` flag), quiet (`-q` flag)
> - Exit codes: 0 (success), 1 (validation error), 2 (system error)
> - Pipe-friendly output where appropriate: `bakery-cli list-products --json | jq '.[] | .name'`
>
> **Generate command map showing all CLI commands:**
> ```
> bakery-cli
> ├── add-product       Add a new product
> ├── list-products     List all products (filterable)
> ├── update-product    Update product details
> ├── delete-product    Remove a product
> ├── report            Generate daily/weekly/monthly report
> │   ├── --daily       Today's summary
> │   ├── --weekly      This week's summary
> │   └── --export csv  Export to CSV
> └── config
>     ├── set           Set a config value
>     └── show          Show current config
> ```
>
> ### For APIs:
>
> Show exact request/response pairs with realistic data for every endpoint.
>
> ```
> ### POST /api/v1/products
> Related: FR-005
> Auth: Bearer token (role: admin, manager)
>
> Request:
> POST /api/v1/products
> Authorization: Bearer eyJhbGciOi...
> Content-Type: application/json
>
> {
>   "name": "Sourdough Loaf",
>   "category": "bread",
>   "price": 8.50,
>   "cost": 3.20,
>   "daily_capacity": 50,
>   "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
> }
>
> Response (201 Created):
> {
>   "id": "PRD-0042",
>   "name": "Sourdough Loaf",
>   "category": "bread",
>   "price": 8.50,
>   "cost": 3.20,
>   "margin": 0.624,
>   "daily_capacity": 50,
>   "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
>   "created_at": "2026-03-16T10:30:00Z",
>   "created_by": "user-123"
> }
>
> ---
>
> ### POST /api/v1/products — Validation Errors
>
> Request (missing required fields):
> {
>   "name": "",
>   "price": -5
> }
>
> Response (422 Unprocessable Entity):
> {
>   "error": "VALIDATION_ERROR",
>   "message": "Request validation failed",
>   "details": [
>     {"field": "name", "issue": "must not be empty"},
>     {"field": "price", "issue": "must be a positive number"},
>     {"field": "category", "issue": "is required"}
>   ]
> }
>
> ---
>
> ### POST /api/v1/products — Unauthorized
>
> Response (401 Unauthorized):
> {
>   "error": "UNAUTHORIZED",
>   "message": "Invalid or expired token"
> }
>
> ### POST /api/v1/products — Forbidden
>
> Response (403 Forbidden):
> {
>   "error": "FORBIDDEN",
>   "message": "Role 'viewer' cannot create products"
> }
>
> ---
>
> ### GET /api/v1/products
> Related: FR-006
> Auth: Bearer token (role: any)
>
> Request:
> GET /api/v1/products?category=bread&sort=margin&order=desc&page=1&limit=20
>
> Response (200 OK):
> {
>   "data": [
>     {
>       "id": "PRD-0042",
>       "name": "Sourdough Loaf",
>       "category": "bread",
>       "price": 8.50,
>       "margin": 0.624
>     }
>   ],
>   "pagination": {
>     "page": 1,
>     "limit": 20,
>     "total": 1,
>     "total_pages": 1
>   }
> }
>
> ### GET /api/v1/products (empty)
>
> Response (200 OK):
> {
>   "data": [],
>   "pagination": {"page": 1, "limit": 20, "total": 0, "total_pages": 0}
> }
> ```
>
> **For each endpoint, include:**
> - Method, path, query parameters, and their types/defaults
> - Auth requirements: which roles can access, what happens if unauthorized
> - Request body with every field: name, type, required/optional, validation rules, example value
> - Response for: success, validation error (422), not found (404), unauthorized (401), forbidden (403), server error (500)
> - Pagination format for list endpoints
> - Rate limiting headers if applicable
> - Realistic example data throughout — not "string" and "test123"
>
> **Generate API overview table:**
> ```
> | Method | Endpoint              | Auth       | Description            | Related |
> |--------|-----------------------|------------|------------------------|---------|
> | POST   | /api/v1/products      | admin, mgr | Create a product       | FR-005  |
> | GET    | /api/v1/products      | any        | List/filter products   | FR-006  |
> | GET    | /api/v1/products/:id  | any        | Get product details    | FR-006  |
> | PUT    | /api/v1/products/:id  | admin, mgr | Update a product       | FR-007  |
> | DELETE | /api/v1/products/:id  | admin      | Delete a product       | FR-008  |
> ```
>
> ---
>
> **Prototype principles:**
> - **Show, don't describe** — "login page has email and password fields" is weak; an ASCII wireframe with exact field labels, button text, and error messages is strong
> - **Cover every state** — success, error, empty, loading. Users never imagine the empty state until they see it.
> - **Use realistic data** — "Sourdough Loaf, $8.50" not "Product A, $10.00". Real data exposes real issues (what if product name is 80 characters? Does the table break?)
> - **Every prototype traces to requirements** — label with FR-XXX so changes can be traced
> - **Behavior over layout** — the wireframe shows layout, but the behavior notes below it are equally important. "What happens when I click this?" must be answered for every interactive element.
> - **This is the user's last chance to cheaply change things** — after this document, architecture gets designed and code gets written. Make it easy for the user to spot "wait, that's not what I meant" NOW.
>
> ---
>
> **Every functional requirement must have:**
> - Unique ID (FR-001, FR-002...)
> - Clear acceptance criteria (how do you know it's done?)
> - Priority (MUST / SHOULD / COULD)
> - Dependencies on other requirements (if any)
> - **At least one prototype reference** — which screen/command/endpoint demonstrates this requirement
>
> **Quality checks before finalizing:**
> - Every user persona has at least one journey
> - Every journey has prototype screens/commands/endpoints showing each step
> - No requirement contradicts another
> - Non-functional requirements have specific measurable targets, not vague words like "fast" or "secure"
> - Assumptions section documents every default assumed
> - Out-of-scope section exists and is explicit
> - Every interactive element in prototypes has defined behavior for success AND failure
> - Every API endpoint shows error responses, not just happy path
> - Every CLI command shows what happens with bad input
> - Every UI screen shows empty state and error state
>
> **Closing summary after writing the document:**
> - Total count: X functional requirements, Y non-functional requirements
> - Priority breakdown: X must-have, Y should-have, Z nice-to-have
> - Prototype coverage: X screens / Y commands / Z endpoints documented
> - Key risks or gaps that need stakeholder input
> - Path to generated `requirements.md`
> - Tell the user: "Review the prototypes carefully — this is the cheapest point to change anything. Once architecture starts, changes get expensive."
> - Suggest: "When you're satisfied, feed this to the `sw-architect` skill to generate the architecture plan"
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on phrases like "requirements", "what should I build", "scope this project", "feature list", "PRD", "spec", "product requirements", "write requirements", "interview me", "figure out what I need", "wireframe", "mockup", "how will it look", "API spec", "CLI design", "prototype". No bundled scripts — pure LLM reasoning + interview + WebSearch.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
