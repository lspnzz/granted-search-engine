# Ultrareview - Deep Multi-Agent Code Review

When asked to run an "ultrareview", follow this protocol. The goal is a deep,
verified code review that focuses on real bugs over style nits.

## Trigger

Run this when the user says: "ultrareview", "run ultrareview", or
"deep review". Accept an optional argument for scope (PR number, file path,
directory, or base branch).

## Phase 1 - Scope

1. Default scope: `git diff origin/main...HEAD`
2. PR number: `gh pr diff <number> --patch`
3. File/directory: `git diff origin/main...HEAD -- <path>`
4. Branch name: `git diff <branch>...HEAD`
5. Compute the diff stat and list changed files.
6. Summarize: "Reviewing N files (+X/-Y lines) across [domains]"

## Phase 2 - Review Fleet

Perform 5 independent review passes, each with a dedicated lens:

### R1 - Security

Input validation, injection, auth bypass, secrets exposure, SSRF, CSRF, path
traversal, unsafe local listener exposure. Trace data from environment values,
HTTP requests, broker payloads, runtime responses, and token files to dangerous
sinks.

### R2 - Correctness

Logic errors, race conditions, off-by-one errors, nil handling, broken state
machines, idempotency gaps, context cancellation mistakes, retry semantics, and
inbound/outbound A2A protocol mismatches. Walk the happy path and failure paths.

### R3 - Performance & Reliability

Unbounded polling or loops, missing timeouts, retry storms, resource leaks,
goroutine leaks, response body leaks, large in-memory state growth, startup
latency, and weak readiness/health behavior. Consider production sidecar scale
and failure modes.

### R4 - Go/Connector Standards

Type consistency, error wrapping, context propagation, HTTP client/server
patterns, test gaps, dead code, package boundaries, environment parsing,
gofmt/go vet/golangci-lint issues, and compatibility with the Go version in
`go.mod`. Check against `AGENTS.md` if present, `.llm-repo-instructions`,
`.llm-repo-instructions-extra` if present, and ADRs under `docs/adr/`.

### R5 - Infrastructure

Docker, distroless runtime behavior, Makefile targets, CI/CD workflows, release
tagging, registry/image names, build flags, Kubernetes sidecar assumptions,
configuration defaults, rollback paths, storage, and deployment safety.

For each pass, return max 5 findings with:

- severity: critical / high / medium / low
- file: path:line
- title: one-line summary
- evidence: the specific problematic code
- impact: what goes wrong in production
- fix: concrete suggestion

## Phase 3 - Deduplicate

Merge findings pointing to the same root cause. Tag when multiple lenses
independently found the same issue (higher confidence).

## Phase 4 - Verify

For each unique finding:

1. Read the actual source at the referenced line.
2. Confirm the finding is real (not hallucinated).
3. Check if the issue is pre-existing or introduced by this diff.
4. Discard findings that are already handled, pre-existing, unreachable, or
   style-only.

## Phase 5 - Report

```markdown
## Ultrareview Report

**Scope:** [branch/PR] - N files, +X/-Y lines
**Reviewers:** 5 lenses, M raw findings, K verified

### Must Fix (block merge)

[Verified critical/high findings]

### Should Fix (address soon)

[Verified medium findings]

### Consider (low priority)

[Verified low findings]

### Positive Notes

[Things done well]

### Reviewer Agreement

[Findings found by multiple lenses]
```

Ask: "Want me to fix any of these?"

## Standards

- Bar: "Would this cause a production issue, data loss, security hole, or
  significant developer confusion?"
- Every finding MUST be verified against actual source. Unverified = discarded.
- Use `AGENTS.md` if present, `.llm-repo-instructions`,
  `.llm-repo-instructions-extra` if present, and `docs/adr/` for project
  conventions and architecture context.
- Pay special attention to sidecar trust boundaries: local listener binding,
  connector auth, Keycloak private-key JWT handling, A2A broker calls, MCP proxy
  forwarding, runtime adapter calls, and persisted conversation state.
