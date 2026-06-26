#!/usr/bin/env node
'use strict';

const { spawnSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const REPO = 'chengkj99/kj-skills';

const TARGETS = {
  claude: path.join(os.homedir(), '.claude', 'skills'),
  codex: process.env.CODEX_HOME
    ? path.join(process.env.CODEX_HOME, 'skills')
    : path.join(os.homedir(), '.codex', 'skills'),
  cursor: process.env.CURSOR_SKILLS_DIR
    ? process.env.CURSOR_SKILLS_DIR
    : path.join(os.homedir(), '.cursor', 'skills'),
};

function usage() {
  console.log(`
Usage:
  npx kj-skills install <skill-name> [--for claude|codex|cursor]

Options:
  --for   Target platform (default: claude)

Examples:
  npx kj-skills install git-push
  npx kj-skills install git-push --for cursor
  npx kj-skills install git-push --for codex
`);
}

const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  usage();
  process.exit(0);
}

const cmd = args[0];

if (cmd !== 'install') {
  console.error(`Unknown command: ${cmd}`);
  usage();
  process.exit(1);
}

const skillName = args[1];
if (!skillName) {
  console.error('Error: missing skill name.\n');
  usage();
  process.exit(1);
}

const forIndex = args.indexOf('--for');
const platform = forIndex !== -1 ? args[forIndex + 1] : 'claude';

if (!TARGETS[platform]) {
  console.error(`Error: unknown platform "${platform}". Choose from: claude, codex, cursor\n`);
  process.exit(1);
}

const skillsDir = TARGETS[platform];
const dst = path.join(skillsDir, skillName);

if (fs.existsSync(dst)) {
  console.log(`Already installed: ${dst}`);
  process.exit(0);
}

const src = `${REPO}/skills/${skillName}`;
console.log(`Installing ${skillName} → ${dst} ...`);

fs.mkdirSync(skillsDir, { recursive: true });

const result = spawnSync('npx', ['--yes', 'degit', src, dst], {
  stdio: 'inherit',
  shell: true,
});

if (result.status !== 0) {
  console.error(`\nFailed to install "${skillName}". Check that the skill exists in ${REPO}.`);
  process.exit(result.status || 1);
}

console.log(`Done: ${skillName} installed for ${platform}.`);
