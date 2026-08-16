import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const failures = [];
const checks = [];

function pass(message) {
  checks.push(message);
}

function fail(message) {
  failures.push(message);
}

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function parseFrontMatter(frontMatter) {
  const rubyProgram = [
    "require 'yaml'",
    "require 'json'",
    "data = YAML.safe_load($stdin.read, aliases: false)",
    "raise 'front matter must be a mapping' unless data.is_a?(Hash)",
    "STDOUT.write(JSON.generate(data))",
  ].join("; ");
  const result = spawnSync("ruby", ["-e", rubyProgram], {
    input: frontMatter,
    encoding: "utf8",
  });

  if (result.error) throw new Error(`Ruby YAML parser unavailable: ${result.error.message}`);
  if (result.status !== 0) throw new Error(result.stderr.trim().split("\n").at(-1) || "YAML parse failed");
  return JSON.parse(result.stdout);
}

function validateFrontMatterSchema(frontMatter) {
  for (const key of ["name", "description", "license"]) {
    if (typeof frontMatter[key] !== "string" || !frontMatter[key].trim()) {
      throw new Error(`${key} must be a non-empty string`);
    }
  }
  if (frontMatter.compatibility !== undefined && typeof frontMatter.compatibility !== "string") {
    throw new Error("compatibility must be a string when present");
  }
  if (!frontMatter.metadata || Array.isArray(frontMatter.metadata) || typeof frontMatter.metadata !== "object") {
    throw new Error("metadata must be a mapping");
  }
  for (const key of ["version", "author"]) {
    if (typeof frontMatter.metadata[key] !== "string" || !frontMatter.metadata[key].trim()) {
      throw new Error(`metadata.${key} must be a non-empty string`);
    }
  }
}

function walkMarkdown(relativeDir) {
  const absoluteDir = path.join(root, relativeDir);
  return fs.readdirSync(absoluteDir, { withFileTypes: true }).flatMap((entry) => {
    const relativePath = path.join(relativeDir, entry.name);
    if (entry.isDirectory()) return walkMarkdown(relativePath);
    return entry.isFile() && entry.name.endsWith(".md") ? [relativePath] : [];
  });
}

const packageJson = JSON.parse(read("package.json"));
pass("package.json parses");

const skill = read("SKILL.md");
if (!skill.startsWith("---\n")) fail("SKILL.md must start with YAML front matter");

const frontMatterEnd = skill.indexOf("\n---\n", 4);
if (frontMatterEnd === -1) {
  fail("SKILL.md front matter is not closed");
} else {
  const frontMatter = skill.slice(4, frontMatterEnd);
  let parsedFrontMatter;
  try {
    parsedFrontMatter = parseFrontMatter(frontMatter);
    validateFrontMatterSchema(parsedFrontMatter);
    pass("complete SKILL.md front matter parses as YAML and matches the supported schema");
  } catch (error) {
    fail(`SKILL.md front matter is invalid: ${error.message}`);
  }

  if (parsedFrontMatter) {
    const { name, description, metadata = {} } = parsedFrontMatter;
    if (name !== packageJson.name) fail(`skill name ${name ?? "<missing>"} does not match package name ${packageJson.name}`);
    else if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name) || name.length > 64) fail(`skill name violates Agent Skills constraints: ${name}`);
    else pass("skill name matches package name and naming constraints");

    if (!description) fail("skill description is missing");
    else if (description.length > 1024) fail(`skill description exceeds 1024 characters (${description.length})`);
    else pass(`skill description length is valid (${description.length})`);

    if (metadata.version !== packageJson.version) fail(`skill version ${metadata.version ?? "<missing>"} does not match package version ${packageJson.version}`);
    else pass(`skill/package version match (${metadata.version})`);

    const invalidProbe = frontMatter.replace(/^  author:.*$/m, "  author: bad: yaml");
    let rejectedInvalidProbe = false;
    try {
      const parsedProbe = parseFrontMatter(invalidProbe);
      validateFrontMatterSchema(parsedProbe);
    } catch {
      rejectedInvalidProbe = true;
    }

    const invalidShapeProbe = frontMatter.replace(/^license:.*$/m, "license: [bad]");
    let rejectedInvalidShape = false;
    try {
      const parsedProbe = parseFrontMatter(invalidShapeProbe);
      validateFrontMatterSchema(parsedProbe);
    } catch {
      rejectedInvalidShape = true;
    }

    if (!rejectedInvalidProbe) fail("front-matter validation accepted an invalid unquoted colon-space scalar");
    else if (!rejectedInvalidShape) fail("front-matter validation accepted a non-string license");
    else pass("front-matter validation rejects malformed YAML and invalid field types");
  }

  const releasedVersion = read("CHANGELOG.md").match(/^## \[([0-9][^\]]*)\]/m)?.[1];
  if (releasedVersion !== packageJson.version) fail(`latest changelog release ${releasedVersion ?? "<missing>"} does not match package version ${packageJson.version}`);
  else pass("changelog release matches package version");
}

const markdownFiles = [
  "SKILL.md",
  "AGENTS.md",
  "README.md",
  "CHANGELOG.md",
  ...walkMarkdown("references"),
  ...walkMarkdown("examples"),
];

for (const relativePath of markdownFiles) {
  const content = read(relativePath);
  const aliasMatches = [...content.matchAll(/\$T\d+/g)];
  for (const match of aliasMatches) {
    const line = content.slice(0, match.index).split("\n").length;
    fail(`${relativePath}:${line} contains unsupported alias ${match[0]}`);
  }

  const linkPattern = /!?\[[^\]]*\]\(([^)]+)\)/g;
  for (const match of content.matchAll(linkPattern)) {
    const rawTarget = match[1].trim().replace(/^<|>$/g, "");
    const target = rawTarget.split(/\s+["']/)[0].split("#", 1)[0];
    if (!target || /^(?:[a-z]+:|\/)/i.test(target)) continue;

    const resolved = path.resolve(root, path.dirname(relativePath), decodeURIComponent(target));
    if (!fs.existsSync(resolved)) {
      const line = content.slice(0, match.index).split("\n").length;
      fail(`${relativePath}:${line} links to missing ${target}`);
    }
  }
}

if (!failures.some((failure) => failure.includes("unsupported alias"))) pass("no unsupported $Tn aliases");
if (!failures.some((failure) => failure.includes("links to missing"))) pass("all internal Markdown links resolve");

for (const requiredPath of ["SKILL.md", "README.md", "AGENTS.md", "CHANGELOG.md", "LICENSE", "references/", "examples/", "scripts/"]) {
  if (!packageJson.files.includes(requiredPath)) fail(`package.json files is missing ${requiredPath}`);
  else if (!fs.existsSync(path.join(root, requiredPath))) fail(`packaged path does not exist: ${requiredPath}`);
}
if (!failures.some((failure) => failure.startsWith("package.json files") || failure.startsWith("packaged path"))) {
  pass("required package paths exist and are included");
}

const requiredOverviewHeadings = [
  "## Goal",
  "## Assumptions",
  "## Open Questions",
  "## Spec-Lite",
  "## Design Decisions",
  "## Steps Overview",
  "## Validation Commands",
  "## Context & Learnings",
  "### Working Set",
  "### Verified Facts",
  "## Implementation Log",
];
const requiredStepHeadings = [
  "## Goal",
  "## Prerequisites",
  "## Deliverables",
  "## Plan",
  "## Quality Checklist",
  "## Validation Checklist",
  "## Test Checklist",
  "## Implementation Notes",
  "## Files Changed",
];

for (const [relativePath, headings] of [
  ["references/task-overview-template.md", requiredOverviewHeadings],
  ["references/step-template.md", requiredStepHeadings],
]) {
  const content = read(relativePath);
  for (const heading of headings) {
    if (!content.includes(heading)) fail(`${relativePath} is missing required heading: ${heading}`);
  }
}
if (!failures.some((failure) => failure.includes("missing required heading"))) pass("canonical templates contain required headings");

const populatedPlan = "examples/add-email-validation/2024-11-04-add-email-validation/plan.md";
for (const heading of requiredOverviewHeadings) {
  if (!read(populatedPlan).includes(heading)) fail(`${populatedPlan} is missing required heading: ${heading}`);
}
for (const relativePath of [1, 2, 3, 4].map((step) => `examples/add-email-validation/2024-11-04-add-email-validation/steps/step-${step}.md`)) {
  const content = read(relativePath);
  for (const heading of requiredStepHeadings) {
    if (!content.includes(heading)) fail(`${relativePath} is missing required heading: ${heading}`);
  }
}
const compactExample = read("examples/plan-example.md");
for (const marker of ["## Spec-Lite", "> Status: ACTIVE", "steps/step-1.md", "vertical slice"]) {
  if (!compactExample.includes(marker)) fail(`examples/plan-example.md is missing current-contract marker: ${marker}`);
}
if (!failures.some((failure) => failure.includes("examples/") && (failure.includes("missing required heading") || failure.includes("missing current-contract marker")))) {
  pass("populated examples follow current plan/step structure and vertical slicing");
}

const evaluationPrompts = read("examples/evaluation-prompts.md");
const evaluationCases = [...evaluationPrompts.matchAll(/^## \d+\./gm)].length;
const expectedBlocks = [...evaluationPrompts.matchAll(/^\*\*Expected:\*\*/gm)].length;
const forbiddenBlocks = [...evaluationPrompts.matchAll(/^\*\*Forbidden:\*\*/gm)].length;
if (evaluationCases < 10 || expectedBlocks !== evaluationCases || forbiddenBlocks !== evaluationCases) {
  fail(`evaluation matrix is incomplete: cases=${evaluationCases} expected=${expectedBlocks} forbidden=${forbiddenBlocks}`);
} else {
  pass(`behavioral evaluation matrix has ${evaluationCases} expected/forbidden cases`);
}

const workflowFiles = markdownFiles;
const dangerousGitCommand = /\bgit\s+(?:add|am|apply|branch|checkout|cherry-pick|clean|commit|merge|mv|rebase|reset|restore|revert|rm|stash|switch|tag|update-ref|worktree)\b/i;
const explicitAuthorization = /(?:forbidden|never|must not|may not|do not|don't|avoid|without explicit|unless[^\n]*explicit|only (?:after|when|with)[^\n]*explicit|user[^\n]*authoriz)/i;
for (const relativePath of workflowFiles) {
  const lines = read(relativePath).split("\n");
  lines.forEach((line, index) => {
    if (dangerousGitCommand.test(line) && !explicitAuthorization.test(line)) {
      fail(`${relativePath}:${index + 1} contains a Git state-changing command without explicit-authorization language`);
    }
  });
}
if (!failures.some((failure) => failure.includes("Git state-changing command"))) {
  pass("Git state-changing commands across shipped guidance require explicit user authorization");
}

const clarification = read("references/require-clarification.md");
if (!clarification.includes("find plans -mindepth 2 -maxdepth 2 -name plan.md")) {
  fail("clarification workflow does not scan canonical nested plan directories");
} else if (!clarification.includes("plans/*/steps/*.md")) {
  fail("clarification workflow does not inspect authoritative step statuses");
} else {
  pass("active-plan discovery uses canonical nested plans and step statuses");
}

const persistence = read("references/persist-plan.md");
const reflection = read("references/global-reflection.md");
if (!persistence.includes("only a successful global reflection sets plan-level `COMPLETED`")) {
  fail("persistence contract does not reserve plan completion for global reflection");
} else if (!reflection.includes("create an authorized fix step")) {
  fail("global reflection does not route file changes through an authorized fix step");
} else {
  pass("plan completion and reflection fix routing are consistent");
}

const routingFiles = ["SKILL.md", "AGENTS.md", "README.md"];
const routingText = routingFiles.map((relativePath) => read(relativePath)).join("\n");
for (const required of [
  "Workflow mode: Lightweight — <reason>; success: <outcome>; plan: no.",
  "Workflow mode: Full",
]) {
  if (!routingText.includes(required)) fail(`routing contract is missing: ${required}`);
}
if (!skill.includes("read-only reviews or discovery—even when many files must be inspected")) {
  fail("Lightweight routing does not explicitly include broad read-only review/discovery");
} else if (!skill.includes("File count alone is a signal, not a trigger")) {
  fail("Full routing does not reject file count as an automatic trigger");
} else {
  pass("binary routing covers read-only Lightweight work and risk-based Full escalation");
}

const agentsInstructions = read("AGENTS.md");
if (!agentsInstructions.includes("## Delegated Mode Exemption") || !agentsInstructions.includes("Skip the user-facing triage block")) {
  fail("AGENTS.md does not exempt focused delegated agents from user-facing triage");
} else {
  pass("repository instructions and skill agree on Delegated Mode");
}

if (!packageJson.description.includes("host-specific behavior varies by version")) {
  fail("package description overstates cross-host compatibility");
} else {
  pass("package compatibility claim is version-qualified");
}

const ceremonyText = [
  "SKILL.md",
  "AGENTS.md",
  "README.md",
  "references/require-clarification.md",
  "references/create-plan.md",
  "references/checkpoint.md",
].map((relativePath) => read(relativePath)).join("\n");
for (const forbidden of [
  "grill relentlessly",
  "5-15 minutes",
  "Never batch",
  "Ready to proceed to planning?",
  "anything expected to touch more than 3 files",
]) {
  if (ceremonyText.includes(forbidden)) fail(`obsolete routing/ceremony instruction remains: ${forbidden}`);
}
if (!read("references/create-plan.md").includes("sole routine pre-execution approval")) {
  fail("planning does not define a single routine approval gate");
} else if (!failures.some((failure) => failure.includes("obsolete routing/ceremony"))) {
  pass("clarification, step sizing, and approval guidance are bounded");
}

for (const check of checks) console.log(`✓ ${check}`);
if (failures.length) {
  for (const failure of failures) console.error(`✗ ${failure}`);
  console.error(`\n${failures.length} validation failure(s)`);
  process.exit(1);
}
console.log(`\n${checks.length} validation checks passed`);
