# 🌌 Antigravity Awesome Skills: 727+ Agentic Skills for Claude Code, Gemini CLI, Cursor, Copilot & More

> **The Ultimate Collection of 727+ Universal Agentic Skills for AI Coding Assistants — Claude Code, Gemini CLI, Codex CLI, Antigravity IDE, GitHub Copilot, Cursor, OpenCode, AdaL**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Anthropic-purple)](https://claude.ai)
[![Gemini CLI](https://img.shields.io/badge/Gemini%20CLI-Google-blue)](https://github.com/google-gemini/gemini-cli)
[![Codex CLI](https://img.shields.io/badge/Codex%20CLI-OpenAI-green)](https://github.com/openai/codex)
[![Cursor](https://img.shields.io/badge/Cursor-AI%20IDE-orange)](https://cursor.sh)
[![Copilot](https://img.shields.io/badge/GitHub%20Copilot-VSCode-lightblue)](https://github.com/features/copilot)
[![OpenCode](https://img.shields.io/badge/OpenCode-CLI-gray)](https://github.com/opencode-ai/opencode)
[![Antigravity](https://img.shields.io/badge/Antigravity-DeepMind-red)](https://github.com/sickn33/antigravity-awesome-skills)
[![AdaL CLI](https://img.shields.io/badge/AdaL%20CLI-SylphAI-pink)](https://sylph.ai/)
[![ASK Supported](https://img.shields.io/badge/ASK-Supported-blue)](https://github.com/yeasy/ask)

**Antigravity Awesome Skills** is a curated, battle-tested library of **727 high-performance agentic skills** designed to work seamlessly across all major AI coding assistants:

- 🟣 **Claude Code** (Anthropic CLI)
- 🔵 **Gemini CLI** (Google DeepMind)
- 🟢 **Codex CLI** (OpenAI)
- 🔴 **Antigravity IDE** (Google DeepMind)
- 🩵 **GitHub Copilot** (VSCode Extension)
- 🟠 **Cursor** (AI-native IDE)
- ⚪ **OpenCode** (Open-source CLI)
- 🌸 **AdaL CLI** (Self-evolving Coding Agent)

This repository provides essential skills to transform your AI assistant into a **full-stack digital agency**, including official capabilities from **Anthropic**, **OpenAI**, **Google**, **Supabase**, and **Vercel Labs**.

## Table of Contents

- [🚀 New Here? Start Here!](#new-here-start-here)
- [🔌 Compatibility & Invocation](#compatibility--invocation)
- [📦 Features & Categories](#features--categories)
- [🎁 Curated Collections (Bundles)](#curated-collections)
- [📚 Browse 727+ Skills](#browse-727-skills)
- [🛠️ Installation](#installation)
- [🤝 How to Contribute](#how-to-contribute)
- [👥 Contributors & Credits](#credits--sources)
- [⚖️ License](#license)
- [👥 Repo Contributors](#repo-contributors)
- [🌟 Star History](#star-history)

---

## New Here? Start Here!

**Welcome to the V4.0.0 Enterprise Edition.** This isn't just a list of scripts; it's a complete operating system for your AI Agent.

### 1. 🐣 Context: What is this?

**Antigravity Awesome Skills** (Release 4.0.0) is a massive upgrade to your AI's capabilities.

AI Agents (like Claude Code, Cursor, or Gemini) are smart, but they lack **specific tools**. They don't know your company's "Deployment Protocol" or the specific syntax for "AWS CloudFormation".
**Skills** are small markdown files that teach them how to do these specific tasks perfectly, every time.

### 2. ⚡️ Quick Start (The "Bundle" Way)

Install once (clone or npx); then use our **Starter Packs** in [docs/BUNDLES.md](docs/BUNDLES.md) to see which skills fit your role. You get the full repo; Starter Packs are curated lists, not a separate install.

1.  **Install** (pick one):

    ```bash
    # Easiest: npx installer (clones to ~/.agent/skills by default)
    npx antigravity-awesome-skills

    # Or clone manually
    git clone https://github.com/sickn33/antigravity-awesome-skills.git .agent/skills
    ```

2.  **Pick your persona** (See [docs/BUNDLES.md](docs/BUNDLES.md)):
    - **Web Dev?** use the `Web Wizard` pack.
    - **Hacker?** use the `Security Engineer` pack.
    - **Just curious?** start with `Essentials`.

### 3. 🧠 How to use

Once installed, just ask your agent naturally:

> "Use the **@brainstorming** skill to help me plan a SaaS."
> "Run **@lint-and-validate** on this file."

👉 **[Read the Full Getting Started Guide](docs/GETTING_STARTED.md)**

---

## Compatibility & Invocation

These skills follow the universal **SKILL.md** format and work with any AI coding assistant that supports agentic skills.

| Tool            | Type | Invocation Example                | Path              |
| :-------------- | :--- | :-------------------------------- | :---------------- |
| **Claude Code** | CLI  | `>> /skill-name help me...`       | `.claude/skills/` |
| **Gemini CLI**  | CLI  | `(User Prompt) Use skill-name...` | `.gemini/skills/` |
| **Codex CLI**   | CLI  | `(User Prompt) Use skill-name...` | `.codex/skills/`  |
| **Antigravity** | IDE  | `(Agent Mode) Use skill...`       | `.agent/skills/`  |
| **Cursor**      | IDE  | `@skill-name (in Chat)`           | `.cursor/skills/` |
| **Copilot**     | Ext  | `(Paste content manually)`        | N/A               |
| **OpenCode**    | CLI  | `opencode run @skill-name`        | `.agent/skills/`  |
| **AdaL CLI**    | CLI  | `(Auto) Skills load on-demand`    | `.adal/skills/`   |

> [!TIP]
> **Universal Path**: We recommend cloning to `.agent/skills/`. Most modern tools (Antigravity, recent CLIs) look here by default.

> [!WARNING]
> **Windows Users**: This repository uses **symlinks** for official skills.
> The **npx** installer sets `core.symlinks=true` automatically. For **git clone**, enable Developer Mode or run Git as Administrator:
> `git clone -c core.symlinks=true https://github.com/...`

---

Whether you are using **Gemini CLI**, **Claude Code**, **Codex CLI**, **Cursor**, **GitHub Copilot**, **Antigravity**, **OpenCode**, or **AdaL**, these skills are designed to drop right in and supercharge your AI agent.

This repository aggregates the best capabilities from across the open-source community, transforming your AI assistant into a full-stack digital agency capable of Engineering, Design, Security, Marketing, and Autonomous Operations.

## Features & Categories

The repository is organized into specialized domains to transform your AI into an expert across the entire software development lifecycle:

| Category            | Focus                                              | Example skills                                                                  |
| :------------------ | :------------------------------------------------- | :------------------------------------------------------------------------------ |
| Architecture (52)   | System design, ADRs, C4, and scalable patterns     | `architecture`, `c4-context`, `senior-architect`                                |
| Business (35)       | Growth, pricing, CRO, SEO, and go-to-market        | `copywriting`, `pricing-strategy`, `seo-audit`                                  |
| Data & AI (81)      | LLM apps, RAG, agents, observability, analytics    | `rag-engineer`, `prompt-engineer`, `langgraph`                                  |
| Development (72)    | Language mastery, framework patterns, code quality | `typescript-expert`, `python-patterns`, `react-patterns`                        |
| General (95)        | Planning, docs, product ops, writing, guidelines   | `brainstorming`, `doc-coauthoring`, `writing-plans`                             |
| Infrastructure (72) | DevOps, cloud, serverless, deployment, CI/CD       | `docker-expert`, `aws-serverless`, `vercel-deployment`                          |
| Security (107)      | AppSec, pentesting, vuln analysis, compliance      | `api-security-best-practices`, `sql-injection-testing`, `vulnerability-scanner` |
| Testing (21)        | TDD, test design, fixes, QA workflows              | `test-driven-development`, `testing-patterns`, `test-fixing`                    |
| Workflow (17)       | Automation, orchestration, jobs, agents            | `workflow-automation`, `inngest`, `trigger-dev`                                 |

## Curated Collections

[Check out our Starter Packs in docs/BUNDLES.md](docs/BUNDLES.md) to find the perfect toolkit for your role.

## Browse 727+ Skills

We have moved the full skill registry to a dedicated catalog to keep this README clean.

👉 **[View the Complete Skill Catalog (CATALOG.md)](CATALOG.md)**

## Installation

To use these skills with **Claude Code**, **Gemini CLI**, **Codex CLI**, **Cursor**, **Antigravity**, **OpenCode**, or **AdaL**:

### Option A: npx (recommended)

```bash
# Default: ~/.agent/skills (universal)
npx antigravity-awesome-skills

# Cursor
npx antigravity-awesome-skills --cursor

# Claude Code
npx antigravity-awesome-skills --claude

# Gemini CLI
npx antigravity-awesome-skills --gemini

# Codex CLI
npx antigravity-awesome-skills --codex

# OpenCode (Universal)
npx antigravity-awesome-skills

# Custom path
npx antigravity-awesome-skills --path ./my-skills
```

Run `npx antigravity-awesome-skills --help` for all options. If the directory already exists, the installer runs `git pull` to update.

> **If you see a 404 error:** the package may not be published to npm yet. Use: `npx github:sickn33/antigravity-awesome-skills`

### Option B: git clone

```bash
# Universal (works with most tools)
git clone https://github.com/sickn33/antigravity-awesome-skills.git .agent/skills

# Claude Code specific
git clone https://github.com/sickn33/antigravity-awesome-skills.git .claude/skills

# Gemini CLI specific
git clone https://github.com/sickn33/antigravity-awesome-skills.git .gemini/skills

# Codex CLI specific
git clone https://github.com/sickn33/antigravity-awesome-skills.git .codex/skills

# Cursor specific
git clone https://github.com/sickn33/antigravity-awesome-skills.git .cursor/skills

# OpenCode specific (Universal path)
git clone https://github.com/sickn33/antigravity-awesome-skills.git .agent/skills
```

---

## How to Contribute

We welcome contributions from the community! To add a new skill:

1. **Fork** the repository.
2. **Create a new directory** inside `skills/` for your skill.
3. **Add a `SKILL.md`** with the required frontmatter (name and description).
4. **Run validation**: `python3 scripts/validate_skills.py`.
5. **Submit a Pull Request**.

Please ensure your skill follows the Antigravity/Claude Code best practices.

---

## Credits & Sources

We stand on the shoulders of giants.

👉 **[View the Full Attribution Ledger](docs/SOURCES.md)**

Key contributors and sources include:

- **HackTricks**
- **OWASP**
- **Anthropic / OpenAI / Google**
- **The Open Source Community**

This collection would not be possible without the incredible work of the Claude Code community and official sources:

### Official Sources

- **[anthropics/skills](https://github.com/anthropics/skills)**: Official Anthropic skills repository - Document manipulation (DOCX, PDF, PPTX, XLSX), Brand Guidelines, Internal Communications.
- **[anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks)**: Official notebooks and recipes for building with Claude.
- **[remotion-dev/skills](https://github.com/remotion-dev/skills)**: Official Remotion skills - Video creation in React with 28 modular rules.
- **[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)**: Vercel Labs official skills - React Best Practices, Web Design Guidelines.
- **[openai/skills](https://github.com/openai/skills)**: OpenAI Codex skills catalog - Agent skills, Skill Creator, Concise Planning.
- **[supabase/agent-skills](https://github.com/supabase/agent-skills)**: Supabase official skills - Postgres Best Practices.

### Community Contributors

- **[rmyndharis/antigravity-skills](https://github.com/rmyndharis/antigravity-skills)**: For the massive contribution of 300+ Enterprise skills and the catalog generation logic.

- **[obra/superpowers](https://github.com/obra/superpowers)**: The original "Superpowers" by Jesse Vincent.
- **[guanyang/antigravity-skills](https://github.com/guanyang/antigravity-skills)**: Core Antigravity extensions.
- **[diet103/claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase)**: Infrastructure and Backend/Frontend Guidelines.
- **[ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase)**: React UI patterns and Design Systems.
- **[travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)**: Loki Mode and Playwright integration.
- **[zebbern/claude-code-guide](https://github.com/zebbern/claude-code-guide)**: Comprehensive Security suite & Guide (Source for ~60 new skills).
- **[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)**: Senior Engineering and PM toolkit.
- **[karanb192/awesome-claude-skills](https://github.com/karanb192/awesome-claude-skills)**: A massive list of verified skills for Claude Code.
- **[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)**: Curated collection of 61 high-quality skills including official team skills from Sentry, Trail of Bits, Expo, Hugging Face, and comprehensive context engineering suite (v4.3.0 integration).
- **[zircote/.claude](https://github.com/zircote/.claude)**: Shopify development skill reference.
- **[vibeforge1111/vibeship-spawner-skills](https://github.com/vibeforge1111/vibeship-spawner-skills)**: AI Agents, Integrations, Maker Tools (57 skills, Apache 2.0).
- **[coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)**: Marketing skills for CRO, copywriting, SEO, paid ads, and growth (23 skills, MIT).
- **[vudovn/antigravity-kit](https://github.com/vudovn/antigravity-kit)**: AI Agent templates with Skills, Agents, and Workflows (33 skills, MIT).
- **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)**: Complete Claude Code configuration collection from Anthropic hackathon winner - skills only (8 skills, MIT).
- **[whatiskadudoing/fp-ts-skills](https://github.com/whatiskadudoing/fp-ts-skills)**: Practical fp-ts skills for TypeScript – fp-ts-pragmatic, fp-ts-react, fp-ts-errors (v4.4.0).
- **[webzler/agentMemory](https://github.com/webzler/agentMemory)**: Source for the agent-memory-mcp skill.
- **[sstklen/claude-api-cost-optimization](https://github.com/sstklen/claude-api-cost-optimization)**: Save 50-90% on Claude API costs with smart optimization strategies (MIT).

### Inspirations

- **[f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts)**: Inspiration for the Prompt Library.
- **[leonardomso/33-js-concepts](https://github.com/leonardomso/33-js-concepts)**: Inspiration for JavaScript Mastery.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

## Community

- [Community Guidelines](docs/COMMUNITY_GUIDELINES.md)
- [Security Policy](docs/SECURITY_GUARDRAILS.md)

---

---

## GitHub Topics

For repository maintainers, add these topics to maximize discoverability:

```text
claude-code, gemini-cli, codex-cli, antigravity, cursor, github-copilot, opencode,
agentic-skills, ai-coding, llm-tools, ai-agents, autonomous-coding, mcp,
ai-developer-tools, ai-pair-programming, vibe-coding, skill, skills, SKILL.md, rules.md, CLAUDE.md, GEMINI.md, CURSOR.md
```

---

## Repo Contributors

<a href="https://github.com/sickn33/antigravity-awesome-skills/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=sickn33/antigravity-awesome-skills" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

We officially thank the following contributors for their help in making this repository awesome!

- [@sck000](https://github.com/sck000)
- [@munir-abbasi](https://github.com/munir-abbasi)
- [@sickn33](https://github.com/sickn33)
- [@Mohammad-Faiz-Cloud-Engineer](https://github.com/Mohammad-Faiz-Cloud-Engineer)
- [@Dokhacgiakhoa](https://github.com/Dokhacgiakhoa)
- [@IanJ332](https://github.com/IanJ332)
- [@chauey](https://github.com/chauey)
- [@PabloSMD](https://github.com/PabloSMD)
- [@GuppyTheCat](https://github.com/GuppyTheCat)
- [@Tiger-Foxx](https://github.com/Tiger-Foxx)
- [@arathiesh](https://github.com/arathiesh)
- [@liyin2015](https://github.com/liyin2015)
- [@1bcMax](https://github.com/1bcMax)
- [@ALEKGG1](https://github.com/ALEKGG1)
- [@ar27111994](https://github.com/ar27111994)
- [@BenedictKing](https://github.com/BenedictKing)
- [@whatiskadudoing](https://github.com/whatiskadudoing)
- [@LocNguyenSGU](https://github.com/LocNguyenSGU)
- [@yubing744](https://github.com/yubing744)
- [@SuperJMN](https://github.com/SuperJMN)
- [@truongnmt](https://github.com/truongnmt)
- [@viktor-ferenczi](https://github.com/viktor-ferenczi)
- [@c1c3ru](https://github.com/c1c3ru)
- [@ckdwns9121](https://github.com/ckdwns9121)
- [@fbientrigo](https://github.com/fbientrigo)
- [@junited31](https://github.com/junited31)
- [@KrisnaSantosa15](https://github.com/KrisnaSantosa15)
- [@sstklen](https://github.com/sstklen)
- [@taksrules](https://github.com/taksrules)
- [@zebbern](https://github.com/zebbern)
- [@vuth-dogo](https://github.com/vuth-dogo)
- [@mvanhorn](https://github.com/mvanhorn)
- [@rookie-ricardo](https://github.com/rookie-ricardo)
- [@evandro-miguel](https://github.com/evandro-miguel)
- [@raeef1001](https://github.com/raeef1001)
- [@devchangjun](https://github.com/devchangjun)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sickn33/antigravity-awesome-skills&type=date&legend=top-left)](https://www.star-history.com/#sickn33/antigravity-awesome-skills&type=date&legend=top-left)
