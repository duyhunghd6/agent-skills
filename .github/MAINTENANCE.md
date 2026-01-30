# 🛠️ Repository Maintenance Guide (V4)

> **"If it's not documented, it's broken."**

This guide details the exact procedures for maintaining `antigravity-awesome-skills`.
It covers the **Quality Bar**, **Documentation Consistency**, and **Release Workflows**.

---

## 0. 🤖 Agent Protocol (THE BIBLE)

**AGENTS MUST READ AND FOLLOW THIS SECTION BEFORE MARKING ANY TASK AS COMPLETE.**

There are 3 things that usually fail/get forgotten. **DO NOT FORGET THEM:**

### 1. 📤 ALWAYS PUSH (Non-Negotiable)

Committing is NOT enough. You must PUSH to the remote.

- **BAD**: `git commit -m "feat: new skill"` (User sees nothing)
- **GOOD**: `git commit -m "..." && git push origin main`

### 2. 🔄 SYNC GENERATED FILES (Avoid CI Drift)

If you touch **any of these**:

- `skills/` (add/remove/modify skills)
- the **Full Skill Registry** section of `README.md`
- **counts/claims** about the number of skills (`560+ Agentic Skills...`, `(560/560)`, etc.)

…then you **MUST** run the Validation Chain **BEFORE** committing.

- Running `npm run chain` is **NOT optional**.
- Running `npm run catalog` is **NOT optional**.

If CI fails with:

> `❌ Detected uncommitted changes produced by registry/readme/catalog scripts.`

it means you **did not run or commit** the Validation Chain correctly.

### 3. 📝 EVIDENCE OF WORK

- You must create/update `walkthrough.md` or `RELEASE_NOTES.md` to document what changed.
- If you made something new, **link it** in the artifacts.

### 4. 🚫 NO BRANCHES

- **ALWAYS use the `main` branch.**
- NEVER create feature branches (e.g., `feat/new-skill`).
- We commit directly to `main` to keep history linear and simple.

---

## 1. 🚦 Daily Maintenance Routine

### A. Validation Chain

Before ANY commit that adds/modifies skills, run the chain:

1.  **Validate, index, and update readme**:

    ```bash
    npm run chain
    ```

    _Must return 0 errors for new skills._

2.  **Build catalog**:

    ```bash
    npm run catalog
    ```

3.  **COMMIT GENERATED FILES**:
    ```bash
    git add README.md skills_index.json data/catalog.json data/bundles.json data/aliases.json CATALOG.md
    git commit -m "chore: sync generated files"
    ```
    > 🔴 **CRITICAL**: If you skip this, CI will fail with "Detected uncommitted changes".
    > See [docs/CI_DRIFT_FIX.md](../docs/CI_DRIFT_FIX.md) for details.

### B. Post-Merge Routine (Must Do)

After multiple PR merges or significant changes:

1.  **Sync Contributors List**:
    - Run: `git shortlog -sn --all`
    - Update `## Repo Contributors` in README.md.

2.  **Verify Table of Contents**:
    - Ensure all new headers have clean anchors.
    - **NO EMOJIS** in H2 headers.

3.  **Draft a Release**:
    - Go to [Releases Page](https://github.com/sickn33/antigravity-awesome-skills/releases).
    - Draft a new release for the merged changes.
    - Tag version (e.g., `v4.1.0`).

---

## 2. 📝 Documentation "Pixel Perfect" Rules

We discovered several consistency issues during V4 development. Follow these rules STRICTLY.

### A. Table of Contents (TOC) Anchors

GitHub's anchor generation breaks if headers have emojis.

- **BAD**: `## 🚀 New Here?` -> Anchor: `#--new-here` (Broken)
- **GOOD**: `## New Here?` -> Anchor: `#new-here` (Clean)

**Rule**: **NEVER put emojis in H2 (`##`) headers.** Put them in the text below if needed.

### B. The "Trinity" of Docs

If you update installation instructions or tool compatibility, you MUST update all 3 files:

1.  `README.md` (Source of Truth)
2.  `docs/GETTING_STARTED.md` (Beginner Guide)
3.  `docs/FAQ.md` (Troubleshooting)

_Common pitfall: Updating the clone URL in README but leaving an old one in FAQ._

### C. Statistics Consistency (CRITICAL)

If you add/remove skills, you **MUST** ensure the total count is identical in ALL locations.
**Do not allow drift** (e.g., 560 in title, 558 in header).

Locations to check:

1.  **Title of `README.md`**: "560+ Agentic Skills..."
2.  **`## Full Skill Registry (560/560)` header**.
3.  **`docs/GETTING_STARTED.md` intro**.

### D. Credits Policy (Who goes where?)

- **Credits & Sources**: Use this for **External Repos**.
  - _Rule_: "I extracted skills from this link you sent me." -> Add to `## Credits & Sources`.
- **Repo Contributors**: Use this for **Pull Requests**.
  - _Rule_: "This user sent a PR." -> Add to `## Repo Contributors`.

### E. Badges & Links

- **Antigravity Badge**: Must point to `https://github.com/sickn33/antigravity-awesome-skills`, NOT `anthropics/antigravity`.
- **License**: Ensure the link points to `LICENSE` file.

---

## 3. 🛡️ Governance & Quality Bar

### A. The 5-Point Quality Check

Reject any PR that fails this:

1.  **Metadata**: Has `name`, `description`?
2.  **Safety**: `risk: offensive` used for red-team tools?
3.  **Clarity**: Does it say _when_ to use it?
4.  **Examples**: Copy-pasteable code blocks?
5.  **Actions**: "Run this command" vs "Think about this".

### B. Risk Labels (V4)

- ⚪ **Safe**: Default.
- 🔴 **Risk**: Destructive/Security tools. MUST have `[Authorized Use Only]` warning.
- 🟣 **Official**: Vendor mirrors only.

---

## 4. 🚀 Release Workflow

When cutting a new version (e.g., V4):

1.  **Run Full Validation**: `python3 scripts/validate_skills.py --strict`
2.  **Update Changelog**: Create `RELEASE_NOTES.md`.
3.  **Bump Version**: Update header in `README.md`.
4.  **Tag Release**:
    ```bash
    git tag -a v4.0.0 -m "V4 Enterprise Edition"
    git push origin v4.0.0
    ```

### 📋 Release Note Template

All changeslogs/release notes MUST follow this structure to ensure professionalism and quality:

```markdown
# Release vX.Y.Z: [Theme Name]

> **[One-line catchy summary of the release]**

[Brief 2-3 sentence intro about the release's impact]

## 🚀 New Skills

### [Emoji] [Skill Name](skills/skill-name/)

**[Bold high-level benefit]**
[Description of what it does]

- **Key Feature 1**: [Detail]
- **Key Feature 2**: [Detail]

> **Try it:** `(User Prompt) ...`

---

## 📦 Improvements

- **Registry Update**: Now tracking [N] skills.
- **[Component]**: [Change detail]

## 👥 Credits

A huge shoutout to our community contributors:

- **@username** for `skill-name`
- **@username** for `fix-name`

---

_Upgrade now: `git pull origin main` to fetch the latest skills._
```

---

## 5. 🚨 Emergency Fixes

If a skill is found to be harmful or broken:

1.  **Move to broken folder** (don't detect): `mv skills/bad-skill skills/.broken/`
2.  **Or Add Warning**: Add `> [!WARNING]` to the top of `SKILL.md`.
3.  **Push Immediately**.
