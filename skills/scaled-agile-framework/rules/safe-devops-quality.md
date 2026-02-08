# SAFe DevOps & Built-in Quality

SAFe embeds DevOps culture and Built-in Quality practices to ensure every increment is potentially releasable. Quality is not inspected in — it is built in.

## Continuous Delivery Pipeline (CDP)

The CDP has four interconnected stages:

### 1. Continuous Exploration (CE)

Discover and validate what to build through customer research, hypothesis-driven development, and design thinking.

- Personas and empathy maps
- Customer journey mapping
- Feature hypothesis with measurable outcomes
- MVP/prototype validation before development

### 2. Continuous Integration (CI)

Merge, build, and test code frequently to catch defects early.

**Key Practices:**

- Developers commit to trunk/main multiple times per day
- Automated build triggered on every commit
- Unit tests, integration tests, and static analysis in the pipeline
- Feature flags for incomplete work (trunk-based development)

✅ **Do**: Fix broken builds immediately — "stop the line" mentality
✅ **Do**: Maintain >80% code coverage with meaningful tests
❌ **Don't**: Use long-lived feature branches that diverge from main

### 3. Continuous Deployment (CD)

Automate deployment to staging and production environments.

**Key Practices:**

- Infrastructure as Code (IaC) for environment parity
- Blue-green or canary deployments for zero-downtime releases
- Automated smoke tests and health checks post-deploy
- Rollback capability with database migration reversibility

### 4. Release on Demand

Decouple deployment from release. Deploy continuously, release when business value is ready.

- Feature toggles to control user-facing functionality
- Dark launches for production validation
- A/B testing and progressive rollout
- Business decides release timing, not engineering

## Built-in Quality Practices

SAFe defines five dimensions of Built-in Quality for software:

### 1. Flow Quality

- Small batch sizes and WIP limits
- Continuous integration across teams
- Automated testing at every level

### 2. Architecture & Design Quality

- Intentional architecture with emergent design
- Architectural runway: enabler features built ahead of need
- Non-functional requirements (NFRs) in the backlog, not as afterthoughts

### 3. Code Quality

| Practice                      | Description                                 |
| ----------------------------- | ------------------------------------------- |
| **TDD**                       | Write test first, then minimal code to pass |
| **Pair Programming**          | Real-time code review, knowledge sharing    |
| **Collective Code Ownership** | Any developer can modify any code           |
| **Refactoring**               | Continuously improve code structure         |
| **Coding Standards**          | Agreed-upon style, linting, formatting      |

### 4. System Quality

- Integration testing across team boundaries
- Performance, security, and accessibility testing
- System-level test automation (API, E2E)
- Continuous monitoring in production

### 5. Release Quality

- Definition of Done (DoD) at story, iteration, and PI levels
- Hardening/stabilization if needed (reduce over time)
- Automated regression suite
- Release readiness checklist

## Definition of Done (DoD) — Three Levels

| Level         | Scope                    | Example Criteria                                                  |
| ------------- | ------------------------ | ----------------------------------------------------------------- |
| **Story**     | Individual user story    | Code written, unit tested, peer reviewed, acceptance criteria met |
| **Iteration** | End of sprint            | Stories accepted, integration tests pass, no critical bugs        |
| **PI**        | End of Program Increment | System demo complete, NFRs validated, documentation updated       |

## Anti-Patterns

❌ Manual testing as the primary quality gate — automate relentlessly
❌ "QA team" separate from development — embed quality in every developer
❌ Skipping architectural runway — accruing technical debt that slows flow
❌ Deploying only at PI boundaries — aim for continuous deployment
❌ NFRs as a "later" concern — treat them as first-class backlog items
