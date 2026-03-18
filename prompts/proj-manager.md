# Prompt: proj-manager

> **Create a skill called `proj-manager` — a senior project manager that takes an architecture plan (`plan.md` from the `sw-architect` skill) and breaks it down into epics, user stories, tasks with descriptions, acceptance criteria, estimates, and dependencies — outputting a comprehensive `project-plan.md`. If the project has a UI, it researches current UI/UX best practices and creates a complete design system specification that developers follow.**
>
> **Input modes (auto-detected):**
>
> 1. **Full pipeline** — user provides `project-plan.md` (and optionally `plan.md` + `requirements.md`). Read ALL documents first to understand the full picture. If `requirements.md` contains UI wireframes/prototypes, use them as the source of truth for UI tasks.
> 2. **Plan + requirements** — user provides both `plan.md` and `requirements.md` (from `req-engineer` skill). Cross-reference both — requirements drive acceptance criteria, plan drives task structure.
> 3. **Manual input** — no file provided, user describes the project verbally. Ask one batch of questions (all upfront, then autonomous):
>    - What are we building? (summary)
>    - Key features / modules
>    - **Does this project have a user interface?** (web, mobile, desktop, CLI — determines if UI/UX research is needed)
>    - Team size and roles available
>    - Sprint duration preference (1 week / 2 weeks / other)
>    - Timeline — MVP and full launch targets
>    - Any specific methodology? (Scrum / Kanban / hybrid — default to Scrum if not specified)
>
> **Accept inline args**: `--plan`, `--requirements`, `--sprint-length`, `--team-size`, `--methodology`
>
> **Processing pipeline:**
>
> **Step 1 — Extract & Organize Work:**
> - Parse the architecture plan's components, phases, roadmap, and ADRs
> - Identify natural epic boundaries (usually map to feature areas, bounded contexts, or roadmap phases)
> - Map each component/feature to the users it serves (pull personas from requirements doc if available)
> - **Detect if the project has a UI** — check for frontend framework in tech stack, UI wireframes in requirements.md, mentions of screens/pages/views. If YES, trigger UI/UX research in Step 2.
>
> **Step 2 — UI/UX Research (only if project has a UI):**
>
> Use WebSearch for **4-8 targeted queries** to find current best practices:
>
> **Research areas:**
> - Current UI/UX design trends and guidelines for the specific platform (web/mobile/desktop) and domain (e.g., "e-commerce UI best practices 2026", "SaaS dashboard UX guidelines")
> - Typography best practices — recommended font pairings, sizes, line heights for the platform
> - Color theory and accessibility — contrast ratios, WCAG AA/AAA compliance, color-blind safe palettes
> - Spacing and layout systems — grid systems, whitespace guidelines, responsive breakpoints
> - Component library recommendations — which UI library fits the tech stack (e.g., Shadcn for Next.js, Vuetify for Vue, Material for Angular)
> - Interaction patterns — loading states, transitions, micro-animations, feedback patterns
> - Accessibility standards — ARIA labels, keyboard navigation, screen reader compatibility
> - Mobile-specific if applicable — touch targets, gesture patterns, safe areas
>
> **Produce a Design System Specification** as a dedicated section in `project-plan.md`:
>
> ```
> ## Design System Specification
>
> ### Color Palette
> | Role | Color | Hex | Usage |
> |------|-------|-----|-------|
> | Primary | Blue | #2563EB | Buttons, links, active states, primary actions |
> | Primary Hover | Dark Blue | #1D4ED8 | Hover state for primary elements |
> | Secondary | Slate | #475569 | Secondary buttons, less prominent actions |
> | Success | Green | #16A34A | Success messages, positive indicators, confirmations |
> | Warning | Amber | #D97706 | Warning alerts, caution states |
> | Error | Red | #DC2626 | Error messages, destructive actions, validation errors |
> | Background | White | #FFFFFF | Page background |
> | Surface | Gray 50 | #F8FAFC | Card backgrounds, elevated surfaces |
> | Text Primary | Gray 900 | #0F172A | Headings, body text |
> | Text Secondary | Gray 500 | #64748B | Labels, helper text, placeholders |
> | Border | Gray 200 | #E2E8F0 | Input borders, dividers, card borders |
>
> Reasoning: [why these colors — tied to brand, industry norms, accessibility scores]
> Accessibility: all text/background combinations meet WCAG AA (4.5:1 contrast ratio minimum)
> Dark mode: [if applicable — provide dark mode equivalents]
>
> ### Typography
> | Element | Font | Weight | Size | Line Height | Letter Spacing |
> |---------|------|--------|------|-------------|----------------|
> | H1 | Inter | 700 (Bold) | 36px / 2.25rem | 1.2 | -0.02em |
> | H2 | Inter | 600 (Semi) | 30px / 1.875rem | 1.25 | -0.01em |
> | H3 | Inter | 600 (Semi) | 24px / 1.5rem | 1.3 | 0 |
> | H4 | Inter | 600 (Semi) | 20px / 1.25rem | 1.4 | 0 |
> | Body | Inter | 400 (Regular) | 16px / 1rem | 1.6 | 0 |
> | Body Small | Inter | 400 (Regular) | 14px / 0.875rem | 1.5 | 0 |
> | Caption | Inter | 400 (Regular) | 12px / 0.75rem | 1.4 | 0.01em |
> | Button | Inter | 500 (Medium) | 14px / 0.875rem | 1 | 0.02em |
> | Code | JetBrains Mono | 400 | 14px / 0.875rem | 1.6 | 0 |
>
> Font source: Google Fonts / bundled / system fonts
> Fallback stack: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
> Reasoning: [why this font — readability scores, domain fit, loading performance]
>
> ### Spacing System
> Base unit: 4px
> Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96
>
> | Token | Value | Usage |
> |-------|-------|-------|
> | space-xs | 4px | Tight inline spacing, icon padding |
> | space-sm | 8px | Between related elements, input padding |
> | space-md | 16px | Standard component padding, gap between form fields |
> | space-lg | 24px | Section padding, card padding |
> | space-xl | 32px | Between major sections |
> | space-2xl | 48px | Page-level spacing, hero sections |
> | space-3xl | 64px | Major layout divisions |
>
> ### Border Radius
> | Token | Value | Usage |
> |-------|-------|-------|
> | radius-sm | 4px | Small elements, tags, badges |
> | radius-md | 8px | Buttons, inputs, cards |
> | radius-lg | 12px | Modals, dialogs, large cards |
> | radius-full | 9999px | Avatars, circular buttons, pills |
>
> ### Shadows
> | Token | Value | Usage |
> |-------|-------|-------|
> | shadow-sm | 0 1px 2px rgba(0,0,0,0.05) | Subtle elevation, buttons |
> | shadow-md | 0 4px 6px rgba(0,0,0,0.07) | Cards, dropdowns |
> | shadow-lg | 0 10px 15px rgba(0,0,0,0.1) | Modals, popovers |
> | shadow-xl | 0 20px 25px rgba(0,0,0,0.15) | Full-screen overlays |
>
> ### Responsive Breakpoints
> | Name | Min Width | Target |
> |------|-----------|--------|
> | sm | 640px | Large phones |
> | md | 768px | Tablets |
> | lg | 1024px | Small laptops |
> | xl | 1280px | Desktops |
> | 2xl | 1536px | Large screens |
>
> ### Component Standards
> | Component | Height | Padding | Font | Radius | States |
> |-----------|--------|---------|------|--------|--------|
> | Button (sm) | 32px | 8px 12px | 14px medium | 8px | default, hover, active, disabled, loading |
> | Button (md) | 40px | 10px 16px | 14px medium | 8px | default, hover, active, disabled, loading |
> | Button (lg) | 48px | 12px 24px | 16px medium | 8px | default, hover, active, disabled, loading |
> | Input | 40px | 10px 12px | 16px regular | 8px | default, focus, error, disabled |
> | Select | 40px | 10px 12px | 16px regular | 8px | default, open, error, disabled |
> | Card | auto | 24px | — | 12px | default, hover (if clickable) |
> | Modal | auto | 24px | — | 12px | — |
> | Badge | 24px | 4px 8px | 12px medium | 9999px | — |
> | Avatar (sm) | 32px | — | — | 9999px | — |
> | Avatar (md) | 40px | — | — | 9999px | — |
> | Avatar (lg) | 64px | — | — | 9999px | — |
>
> ### Interaction Standards
> - Hover transitions: 150ms ease-in-out
> - Page transitions: 200ms ease
> - Loading skeleton: pulse animation, 1.5s duration
> - Toast notifications: appear top-right, auto-dismiss after 5s (errors persist until dismissed)
> - Form validation: inline, on blur for first validation, on change after first error
> - Disabled elements: 50% opacity, cursor: not-allowed
> - Focus indicators: 2px solid primary color, 2px offset (visible for keyboard navigation)
>
> ### Accessibility Requirements
> - All interactive elements keyboard-accessible
> - Tab order follows visual reading order
> - ARIA labels on all icon-only buttons
> - Color is never the ONLY indicator (always pair with icon or text)
> - Minimum touch target: 44x44px (mobile)
> - Skip-to-content link on every page
> - Contrast ratios: text ≥ 4.5:1, large text ≥ 3:1, UI components ≥ 3:1
> ```
>
> **The design system values are not arbitrary — every choice must be justified by the research:**
> - Font choice → cite readability studies or industry adoption
> - Color palette → cite accessibility scores and domain conventions
> - Spacing → cite the platform's design system guidelines
> - If a UI component library is recommended, the design system should align with its tokens
>
> ---
>
> **Step 3 — Create Epic Hierarchy:**
> - Group related work into epics (5-15 typically, depends on project size)
> - Each epic gets: ID, title, description, business value statement, success metrics
> - Order epics by dependency chain and roadmap phase — what must be built first
> - **If UI exists**: include a dedicated "Design System Setup" epic (E-001 typically) that must be completed before any UI implementation epics.
>
> **Step 4 — Write User Stories (for each epic):**
> - Format: "As a [persona], I want to [action], so that [benefit]"
> - Pull personas from requirements doc or infer from the plan's target users
> - Each story must be INVEST-compliant: Independent, Negotiable, Valuable, Estimable, Small, Testable
> - If a story is too large (>13 story points), split it into smaller stories
> - Include negative/edge-case stories: "As a user, I want to see a clear error when payment fails, so that I know what went wrong"
> - Don't forget non-functional stories: "As an ops engineer, I want request latency under 200ms at p99, so that SLA is maintained"
> - **UI stories must reference the design system**: "Acceptance criteria: uses primary button style from design system, error states match design system error color, spacing follows design tokens"
>
> **Step 5 — Break Stories into Tasks:**
> - Each story gets 2-8 tasks (if more, the story should be split)
> - Task types: development, testing, infrastructure, documentation, design, research/spike
> - Each task gets an effort estimate: story points (1/2/3/5/8/13) or T-shirt sizes (S/M/L/XL) — pick one system and stay consistent
> - Identify task dependencies within and across stories
> - Flag tasks that are blockers for other epics
> - **UI tasks must include specific design system references:**
>   - "Build login form using: Input component (40px height, 8px radius), Primary button (md), error color #DC2626 for validation"
>   - "Implement responsive layout: single column below 768px, two-column above 1024px, max-width 1280px"
>   - "Add loading states: skeleton pulse animation per design system, 1.5s duration"
>
> **Step 6 — Acceptance Criteria (for every story and task):**
> - **Stories**: 3-7 acceptance criteria each, written as Given/When/Then where possible
> - **Tasks**: 2-4 acceptance criteria each — specific, measurable definition of done
> - Cross-reference `requirements.md` acceptance criteria if available — reference by ID (e.g., "Satisfies FR-003")
> - **UI acceptance criteria must include visual specs:**
>   - "Login button uses primary color (#2563EB), 14px Inter Medium, 40px height, 8px border radius"
>   - "Error message appears below input in error color (#DC2626), 14px, with error icon"
>   - "Page is usable at 320px viewport width (no horizontal scroll, no overlapping elements)"
>   - "All interactive elements have visible focus indicators (2px solid #2563EB, 2px offset)"
>
> **Step 7 — Sprint Planning Suggestion:**
> - Group stories into suggested sprints based on dependencies, priority, and team capacity
> - Mark the critical path — which stories/tasks block everything else
> - Identify parallelizable work streams for teams >2 people
> - Flag risks per sprint
> - **Sprint 1 should always include design system setup if the project has a UI**
>
> **Step 8 — Write `project-plan.md` to working directory using this template (adapt as needed):**
>
> ```
> # Project Plan: [Project Name]
>
> ## 1. Overview
>    - Project summary (from plan.md)
>    - Methodology: [Scrum/Kanban/hybrid]
>    - Sprint duration: [X weeks]
>    - Team: [size and roles]
>    - Estimated total effort: [X story points / Y sprints]
>
> ## 2. Design System Specification (if UI project)
>    [Full design system as described above]
>
> ## 3. Epics Summary
>    | ID | Epic | Stories | Points | Phase | Dependencies |
>    |----|------|---------|--------|-------|-------------|
>    | E-001 | Design System Setup | X | Y | Phase 1 | — |
>    | E-002 | ... | X | Y | Phase 1 | E-001 |
>
> ## 4. Detailed Breakdown
>    [Epics → Stories → Tasks with acceptance criteria]
>
> ## 5. Sprint Plan
>    [Stories grouped by sprint with goals, capacity, risks]
>
> ## 6. Critical Path
>    [Mermaid dependency graph + bottleneck analysis]
>
> ## 7. Risk Register
>    [Risk table with likelihood, impact, mitigation, owner]
>
> ## 8. Definition of Done (project-wide)
>    [Including UI-specific requirements if applicable]
>
> ## 9. Open Questions
>    [Decisions needing stakeholder input]
> ```
>
> **Quality standards for the output:**
> - Every story traces back to at least one requirement (FR-XXX) or plan component
> - Every task has a clear description — a developer who wasn't in the planning meeting should understand what to do
> - No acceptance criteria uses vague language — all measurable with specific values
> - Dependencies form a valid DAG — no circular dependencies
> - **Every UI task references specific design system tokens**
> - **Design system setup is Sprint 1, before any UI implementation**
>
> **Closing summary after writing the document:**
> - Total: X epics, Y stories, Z tasks
> - Estimated effort: X story points across Y sprints
> - Critical path length: Z sprints
> - **Design system**: [included / not applicable]
> - Top 3 risks
> - Path to generated `project-plan.md`
> - Suggest: "You can now import these stories into Jira/Linear/GitHub Projects, or start Sprint 1"
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on phrases like "break this down", "create tasks", "user stories", "sprint planning", "project plan", "backlog", "epics", "task breakdown", "plan the work", "create tickets", "story points", "acceptance criteria", "break into sprints", "project management", "work breakdown", "design system", "UI guidelines", "color scheme", "typography", "style guide". No bundled scripts — pure LLM reasoning + WebSearch for UI/UX research.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
