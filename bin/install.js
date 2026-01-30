#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const REPO = 'https://github.com/sickn33/antigravity-awesome-skills.git';
const HOME = process.env.HOME || process.env.USERPROFILE || '';

function resolveDir(p) {
  if (!p) return null;
  const s = p.replace(/^~($|\/)/, HOME + '$1');
  return path.resolve(s);
}

function parseArgs() {
  const a = process.argv.slice(2);
  let pathArg = null;
  let cursor = false, claude = false, gemini = false;

  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--help' || a[i] === '-h') return { help: true };
    if (a[i] === '--path' && a[i + 1]) { pathArg = a[++i]; continue; }
    if (a[i] === '--cursor') { cursor = true; continue; }
    if (a[i] === '--claude') { claude = true; continue; }
    if (a[i] === '--gemini') { gemini = true; continue; }
    if (a[i] === 'install') continue;
  }

  return { pathArg, cursor, claude, gemini };
}

function defaultDir(opts) {
  if (opts.pathArg) return resolveDir(opts.pathArg);
  if (opts.cursor) return path.join(HOME, '.cursor', 'skills');
  if (opts.claude) return path.join(HOME, '.claude', 'skills');
  if (opts.gemini) return path.join(HOME, '.gemini', 'skills');
  return path.join(HOME, '.agent', 'skills');
}

function printHelp() {
  console.log(`
antigravity-awesome-skills — installer

  npx antigravity-awesome-skills [install] [options]

  Clones the skills repo into your agent's skills directory.

Options:
  --cursor    Install to ~/.cursor/skills (Cursor)
  --claude    Install to ~/.claude/skills (Claude Code)
  --gemini    Install to ~/.gemini/skills (Gemini CLI)
  --path <dir> Install to <dir> (default: ~/.agent/skills)

Examples:
  npx antigravity-awesome-skills
  npx antigravity-awesome-skills --cursor
  npx antigravity-awesome-skills --path ./my-skills
`);
}

function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, { stdio: 'inherit', ...opts });
  if (r.status !== 0) process.exit(r.status == null ? 1 : r.status);
}

function main() {
  const opts = parseArgs();
  if (opts.help) {
    printHelp();
    return;
  }

  const target = defaultDir(opts);
  if (!target || !HOME) {
    console.error('Could not resolve home directory. Use --path <absolute-path>.');
    process.exit(1);
  }

  if (fs.existsSync(target)) {
    const gitDir = path.join(target, '.git');
    if (fs.existsSync(gitDir)) {
      console.log('Directory already exists and is a git repo. Updating…');
      process.chdir(target);
      run('git', ['pull']);
      return;
    }
    console.error(`Directory exists and is not a git repo: ${target}`);
    console.error('Remove it or use --path to choose another location.');
    process.exit(1);
  }

  const parent = path.dirname(target);
  if (!fs.existsSync(parent)) {
    try {
      fs.mkdirSync(parent, { recursive: true });
    } catch (e) {
      console.error(`Cannot create parent directory: ${parent}`, e.message);
      process.exit(1);
    }
  }

  if (process.platform === 'win32') {
    run('git', ['-c', 'core.symlinks=true', 'clone', REPO, target]);
  } else {
    run('git', ['clone', REPO, target]);
  }

  console.log(`\nInstalled to ${target}`);
  console.log('Pick a bundle in docs/BUNDLES.md and use @skill-name in your AI assistant.');
}

main();
