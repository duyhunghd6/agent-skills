# Release v4.3.0: VoltAgent Integration & Context Engineering Suite

> **Massive expansion with 61 new skills from VoltAgent repository, including official team skills and comprehensive context engineering capabilities**

This release adds 61 high-quality skills sourced from the VoltAgent/awesome-agent-skills curated collection, bringing the total to 614 skills. Highlights include official skills from Sentry, Trail of Bits, Expo, Hugging Face, and a complete context engineering suite for building sophisticated AI agents.

## 🚀 New Skills

### Official Team Skills (27)

#### Sentry (4)
- **[commit](skills/commit/)** – Create commits with best practices following Sentry conventions
- **[create-pr](skills/create-pr/)** – Create pull requests with proper descriptions and review guidelines
- **[find-bugs](skills/find-bugs/)** – Find and identify bugs in code systematically
- **[iterate-pr](skills/iterate-pr/)** – Iterate on pull request feedback efficiently

#### Trail of Bits (3)
- **[culture-index](skills/culture-index/)** – Index and search culture documentation
- **[fix-review](skills/fix-review/)** – Verify fix commits address audit findings without new bugs
- **[sharp-edges](skills/sharp-edges/)** – Identify error-prone APIs and dangerous configurations

#### Expo (2)
- **[expo-deployment](skills/expo-deployment/)** – Deploy Expo apps to production
- **[upgrading-expo](skills/upgrading-expo/)** – Upgrade Expo SDK versions safely

#### Hugging Face (2)
- **[hugging-face-cli](skills/hugging-face-cli/)** – HF Hub CLI for models, datasets, repos, and compute jobs
- **[hugging-face-jobs](skills/hugging-face-jobs/)** – Run compute jobs and Python scripts on HF infrastructure

#### Other Official (16)
- **[vercel-deploy-claimable](skills/vercel-deploy-claimable/)** – Deploy projects to Vercel
- **[design-md](skills/design-md/)** – Create and manage DESIGN.md files (Google Stitch)
- **[using-neon](skills/using-neon/)** – Best practices for Neon Serverless Postgres
- **[n8n-code-python](skills/n8n-code-python/)** – Python in n8n Code nodes
- **[n8n-mcp-tools-expert](skills/n8n-mcp-tools-expert/)** – n8n MCP tools guide
- **[n8n-node-configuration](skills/n8n-node-configuration/)** – n8n node configuration
- **[swiftui-expert-skill](skills/swiftui-expert-skill/)** – SwiftUI best practices
- **[fal-audio](skills/fal-audio/)** – Text-to-speech and speech-to-text using fal.ai
- **[fal-generate](skills/fal-generate/)** – Generate images and videos using fal.ai AI models
- **[fal-image-edit](skills/fal-image-edit/)** – AI-powered image editing with style transfer
- **[fal-platform](skills/fal-platform/)** – Platform APIs for model management and usage tracking
- **[fal-upscale](skills/fal-upscale/)** – Upscale and enhance image/video resolution using AI
- **[fal-workflow](skills/fal-workflow/)** – Generate workflow JSON files for chaining AI models
- **[deep-research](skills/deep-research/)** – Gemini Deep Research Agent for autonomous research
- **[imagen](skills/imagen/)** – Generate images using Google Gemini
- **[readme](skills/readme/)** – Generate comprehensive project documentation

### Community Skills (34)

#### Context Engineering Suite (7)
A complete suite for building sophisticated AI agents with advanced context management:

- **[context-fundamentals](skills/context-fundamentals/)** – Understand what context is, why it matters, and the anatomy of context in agent systems
- **[context-degradation](skills/context-degradation/)** – Recognize patterns of context failure: lost-in-middle, poisoning, distraction, and clash
- **[context-compression](skills/context-compression/)** – Design and evaluate compression strategies for long-running sessions
- **[context-optimization](skills/context-optimization/)** – Apply compaction, masking, and caching strategies
- **[multi-agent-patterns](skills/multi-agent-patterns/)** – Master orchestrator, peer-to-peer, and hierarchical multi-agent architectures
- **[memory-systems](skills/memory-systems/)** – Design short-term, long-term, and graph-based memory architectures
- **[evaluation](skills/evaluation/)** – Build evaluation frameworks for agent systems

#### Development Tools (8)
- **[frontend-slides](skills/frontend-slides/)** – Generate animation-rich HTML presentations with visual style previews
- **[linear-claude-skill](skills/linear-claude-skill/)** – Manage Linear issues, projects, and teams
- **[skill-rails-upgrade](skills/skill-rails-upgrade/)** – Analyze Rails apps and provide upgrade assessments
- **[terraform-skill](skills/terraform-skill/)** – Terraform infrastructure as code best practices
- **[tool-design](skills/tool-design/)** – Build tools that agents can use effectively, including architectural reduction patterns
- **[screenshots](skills/screenshots/)** – Generate marketing screenshots with Playwright
- **[automate-whatsapp](skills/automate-whatsapp/)** – Build WhatsApp automations with workflows and agents
- **[observe-whatsapp](skills/observe-whatsapp/)** – Debug WhatsApp delivery issues and run health checks

#### Platform & Framework Skills (19)
- **[aws-skills](skills/aws-skills/)** – AWS development with infrastructure automation
- **[ui-skills](skills/ui-skills/)** – Opinionated constraints for building interfaces
- **[vexor](skills/vexor/)** – Vector-powered CLI for semantic file search
- **[pypict-skill](skills/pypict-skill/)** – Pairwise test generation
- **[makepad-skills](skills/makepad-skills/)** – Makepad UI development for Rust apps
- **[threejs-skills](skills/threejs-skills/)** – Three.js 3D experiences
- **[claude-scientific-skills](skills/claude-scientific-skills/)** – Scientific research skills
- **[claude-win11-speckit-update-skill](skills/claude-win11-speckit-update-skill/)** – Windows 11 management
- **[security-bluebook-builder](skills/security-bluebook-builder/)** – Security documentation
- **[claude-ally-health](skills/claude-ally-health/)** – Health assistant
- **[clarity-gate](skills/clarity-gate/)** – RAG quality verification
- **[beautiful-prose](skills/beautiful-prose/)** – Writing style guide
- **[claude-speed-reader](skills/claude-speed-reader/)** – Speed reading tool
- **[skill-seekers](skills/skill-seekers/)** – Skill conversion tool
- **[varlock-claude-skill](skills/varlock-claude-skill/)** – Secure environment variable management
- **[superpowers-lab](skills/superpowers-lab/)** – Superpowers Lab integration
- **[nanobanana-ppt-skills](skills/nanobanana-ppt-skills/)** – PowerPoint presentation skills
- **[x-article-publisher-skill](skills/x-article-publisher-skill/)** – X/Twitter article publishing
- **[ffuf-claude-skill](skills/ffuf-claude-skill/)** – Web fuzzing with ffuf

---

## 📦 Registry Update

- **Total Skills**: 614 (from 553)
- **New Skills Added**: 61
- **Catalog**: Fully regenerated with all new skills
- **Sources**: All skills properly attributed in `docs/SOURCES.md`

## 🔧 Improvements

### Quality Assurance
- All new skills validated for frontmatter compliance
- "When to Use" sections added where missing
- Source attribution maintained for all skills
- Risk labels properly set

### Documentation
- Updated README.md with correct skill count (614)
- Updated package.json version to 4.3.0
- Comprehensive release notes created

## 📊 Statistics

- **Skills from VoltAgent Repository**: 61
  - Official Team Skills: 27
  - Community Skills: 34
- **Skills Analyzed**: 174 total from VoltAgent
- **Skills Already Present**: 32 (skipped as duplicates)
- **Skills with Similar Names**: 89 (analyzed, 12 implemented as complementary)

## 👥 Credits

A huge shoutout to our community contributors and the VoltAgent team:

- **VoltAgent/awesome-agent-skills** for curating an excellent collection
- **Official Teams**: Sentry, Trail of Bits, Expo, Hugging Face, Vercel Labs, Google Labs, Neon, fal.ai
- **Community Contributors**: zarazhangrui, wrsmith108, robzolkos, muratcankoylan, antonbabenko, and all other skill authors

---

_Upgrade now: `git pull origin main` to fetch the latest skills._
