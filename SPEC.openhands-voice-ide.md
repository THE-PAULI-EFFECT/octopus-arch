# Machine-readable build spec — OpenHands-based Voice IDE (Full Stack)

> Use this file as the single source of truth for a GitHub coding agent or any autonomous builder. It contains: architecture, repo layout, services, env/secrets, workflows, agent roles, policies, UX spec, API contracts, events, CI/CD, deployment targets, and acceptance tests.

---

## 0) File metadata

```json
{
  "spec_version": "1.0.0",
  "name": "OpenHands Voice IDE",
  "tagline": "Self-hosted voice-first multi-agent coding IDE with automated PR + one-click deploy targets",
  "base_repo": "fork:OpenHands",
  "controls": {
    "primary_runtime": "OpenHands",
    "tool_adapter": "OpenCode CLI adapter",
    "orchestrator_pattern": "Agent Zero-style coordinator (role-based subagents)"
  },
  "hosting": {
    "primary": "Hostinger VPS",
    "orchestrator": "Coolify",
    "edge": "Cloudflare",
    "optional": ["Cloudflare Workers", "Firebase Hosting"]
  },
  "principles": [
    "Secrets are never embedded in repo or agent memory; injected at runtime",
    "Jobs are durable, resumable, auditable",
    "Primary UX = intents → plans → approvals → jobs (terminal secondary)",
    "Model-agnostic via OpenAI-compatible gateway",
    "Auto-approve/merge only when policy gates pass"
  ]
}
```

---

## 1) Repository structure

```json
{
  "repo_layout": {
    "root": "openhands-voice-ide/",
    "apps": {
      "web": "Next.js App Router UI",
      "api": "FastAPI orchestration API + WebSockets",
      "runner": "Sandbox executor + OpenCode adapter + artifact capture"
    },
    "packages": {
      "sdk": "Typed API client + WS event types",
      "ui": "Shared shadcn/ui components",
      "prompts": "System/agent prompts + policies",
      "workflows": "Reusable job workflows (YAML/JSON)",
      "policies": "Policy registry, gates, allowlists"
    },
    "infra": {
      "docker": "docker-compose + Dockerfiles",
      "coolify": "Coolify templates + env var docs",
      "github": "Actions workflows"
    },
    "docs": "Architecture + runbooks"
  }
}
```

---

## 2) Services and dependencies (docker-compose)

```json
{
  "services": {
    "web": {
      "tech": ["Next.js", "TypeScript", "Tailwind", "shadcn/ui", "Monaco"],
      "ports": ["3000"],
      "depends_on": ["api"],
      "env": ["NEXT_PUBLIC_API_BASE", "NEXT_PUBLIC_WS_BASE", "NEXT_PUBLIC_FEATURE_FLAGS"],
      "features": [
        "Voice push-to-talk (Web Speech API)",
        "Chat + plan approval UI",
        "File tree + editor + diff viewer",
        "Jobs timeline + agent panel",
        "Deploy targets panel"
      ]
    },
    "api": {
      "tech": ["FastAPI", "WebSockets", "Pydantic", "SQLAlchemy", "Alembic"],
      "ports": ["8000"],
      "depends_on": ["postgres", "redis", "runner"],
      "env": [
        "DATABASE_URL",
        "REDIS_URL",
        "ARTIFACT_STORE",
        "AUTH_MODE",
        "ADMIN_PASSWORD_HASH",
        "MODEL_GATEWAY_BASE_URL",
        "MODEL_GATEWAY_API_KEY",
        "GITHUB_APP_ID",
        "GITHUB_APP_PRIVATE_KEY",
        "GITHUB_WEBHOOK_SECRET",
        "POLICY_BUNDLE_PATH"
      ]
    },
    "runner": {
      "tech": ["Container sandbox", "OpenHands runtime", "OpenCode CLI adapter"],
      "ports": ["8081"],
      "env": [
        "WORKSPACE_ROOT",
        "COMMAND_ALLOWLIST_PATH",
        "NETWORK_EGRESS_MODE",
        "SECRETS_REDACTION_RULES_PATH",
        "OPEN_CODE_ENTRYPOINT",
        "OPENHANDS_CONFIG_PATH"
      ],
      "volumes": ["workspace:/workspaces", "artifacts:/artifacts"],
      "notes": "Runner executes per-job workspaces and streams structured events back to API"
    },
    "postgres": {
      "tech": ["Postgres"],
      "ports": ["5432"],
      "volumes": ["pgdata:/var/lib/postgresql/data"]
    },
    "redis": {
      "tech": ["Redis"],
      "ports": ["6379"],
      "volumes": ["redisdata:/data"]
    },
    "model_gateway": {
      "tech": ["LiteLLM (OpenAI-compatible gateway)"],
      "optional": true,
      "ports": ["4000"],
      "env": ["LITELLM_CONFIG", "LITELLM_MASTER_KEY"],
      "purpose": "Route to ZAI/GLM, OpenRouter, and other providers with uniform logging, fallback, caps"
    },
    "minio": {
      "tech": ["MinIO"],
      "optional": true,
      "ports": ["9000", "9001"],
      "env": ["MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD"],
      "purpose": "S3-compatible artifact store (optional; can use local volume)"
    }
  },
  "dependency_policy": {
    "free_tier_bias": true,
    "heavy_compute_off_edge": true,
    "edge_used_for": ["auth", "routing", "light webhooks"],
    "compute_used_for": ["LLM calls", "code execution", "tests", "build", "deploy CLIs"]
  }
}
```

---

## 3) Data model (minimal tables)

```json
{
  "db_schema": {
    "projects": {
      "fields": {
        "id": "uuid",
        "name": "text",
        "repo_url": "text",
        "default_branch": "text",
        "local_mount_path": "text",
        "created_at": "timestamptz"
      }
    },
    "runs": {
      "fields": {
        "id": "uuid",
        "project_id": "uuid",
        "status": "enum(planning, awaiting_approval, running, paused, failed, succeeded, canceled)",
        "mode": "enum(interactive, overnight)",
        "requested_by": "text",
        "intent": "jsonb",
        "plan": "jsonb",
        "policy_decision": "jsonb",
        "started_at": "timestamptz",
        "ended_at": "timestamptz"
      }
    },
    "agents": {
      "fields": {
        "id": "uuid",
        "run_id": "uuid",
        "role": "text",
        "status": "enum(queued, running, blocked, done, failed)",
        "model": "text",
        "started_at": "timestamptz",
        "ended_at": "timestamptz"
      }
    },
    "events": {
      "fields": {
        "id": "bigserial",
        "run_id": "uuid",
        "ts": "timestamptz",
        "type": "text",
        "payload": "jsonb"
      }
    },
    "artifacts": {
      "fields": {
        "id": "uuid",
        "run_id": "uuid",
        "kind": "enum(log, patch, report, test_results, build_output, deploy_output)",
        "uri": "text",
        "meta": "jsonb",
        "created_at": "timestamptz"
      }
    },
    "deployments": {
      "fields": {
        "id": "uuid",
        "run_id": "uuid",
        "target": "enum(coolify, firebase, cloudflare_workers)",
        "status": "enum(queued, running, failed, succeeded)",
        "meta": "jsonb",
        "created_at": "timestamptz"
      }
    }
  }
}
```

---

## 4) Event protocol (WebSocket + storage)

```json
{
  "ws": {
    "endpoint": "/ws/runs/{run_id}",
    "events": [
      {"type": "run.created", "schema": {"run_id": "uuid", "project_id": "uuid"}},
      {"type": "run.status", "schema": {"run_id": "uuid", "status": "string"}},
      {"type": "agent.status", "schema": {"agent_id": "uuid", "role": "string", "status": "string"}},
      {"type": "log", "schema": {"source": "string", "line": "string", "level": "string", "ts": "string"}},
      {"type": "step", "schema": {"name": "string", "state": "string", "meta": "object"}},
      {"type": "patch", "schema": {"path": "string", "diff": "string", "summary": "string"}},
      {"type": "tests", "schema": {"passed": "boolean", "report_uri": "string", "failures": "array"}},
      {"type": "policy.gate", "schema": {"gate": "string", "result": "pass|fail|needs_approval", "reason": "string"}},
      {"type": "pr.created", "schema": {"url": "string", "number": "int"}},
      {"type": "pr.approved", "schema": {"url": "string"}},
      {"type": "deploy.status", "schema": {"target": "string", "status": "string", "meta": "object"}},
      {"type": "report", "schema": {"uri": "string", "highlights": "array"}}
    ]
  }
}
```

---

## 5) Voice-first UX (intents → commands)

```json
{
  "voice": {
    "frontend_stt": {
      "default": "Web Speech API",
      "ui": ["push_to_talk_button", "live_transcript", "edit_and_confirm", "intent_card"],
      "fallback": "typed command bar"
    },
    "optional_backend_stt": {
      "endpoint": "/v1/stt/transcribe",
      "status": "stub for Whisper self-hosting",
      "input": "audio/wav|webm",
      "output": {"text": "string", "segments": "array"}
    },
    "intent_registry": [
      {
        "intent": "fix_tests",
        "utterances": ["fix the tests", "make tests pass", "repair failing tests"],
        "command_schema": {"intent": "fix_tests", "scope": "repo|path", "path": "string?"}
      },
      {
        "intent": "run_tests",
        "utterances": ["run the suite", "run tests", "execute test pipeline"],
        "command_schema": {"intent": "run_tests", "scope": "repo|path", "path": "string?"}
      },
      {
        "intent": "refactor",
        "utterances": ["refactor this", "clean up", "improve structure"],
        "command_schema": {"intent": "refactor", "path": "string?", "goal": "string?"}
      },
      {
        "intent": "overnight_mode",
        "utterances": ["keep going overnight", "work while I sleep", "continue until it passes"],
        "command_schema": {"intent": "overnight_mode", "hours": "int", "checkpoint_minutes": "int", "auto_pause_on": "array"}
      },
      {
        "intent": "deploy",
        "utterances": ["deploy staging", "ship to production", "deploy firebase"],
        "command_schema": {"intent": "deploy", "target": "coolify|firebase|cloudflare_workers", "env": "staging|production"}
      }
    ]
  }
}
```

---

## 6) Agent swarm (roles, tools, policies)

```json
{
  "agents": {
    "roles": [
      {
        "name": "planner",
        "responsibilities": ["convert intent → plan", "define acceptance criteria", "risk tagging"],
        "model_policy": {"preferred": "light", "fallback": "standard"},
        "tools": ["repo_context", "search_repo", "policy_registry"]
      },
      {
        "name": "implementer",
        "responsibilities": ["apply code changes", "produce patches", "incremental commits"],
        "model_policy": {"preferred": "standard", "fallback": "light"},
        "tools": ["open_code_adapter", "file_ops", "diff", "unit_tests"]
      },
      {
        "name": "test_agent",
        "responsibilities": ["run tests", "triage failures", "produce minimal repro"],
        "model_policy": {"preferred": "light"},
        "tools": ["open_code_adapter", "test_runner"]
      },
      {
        "name": "security_agent",
        "responsibilities": ["secret scan", "dependency checks", "sensitive-file gate"],
        "model_policy": {"preferred": "light"},
        "tools": ["secret_scanner", "dependency_scanner", "policy_registry"]
      },
      {
        "name": "review_agent",
        "responsibilities": ["automated code review", "style/architecture checks", "risk scoring"],
        "model_policy": {"preferred": "standard"},
        "tools": ["diff", "repo_context", "policy_registry"]
      },
      {
        "name": "release_agent",
        "responsibilities": ["PR description", "changelog", "version bump if needed"],
        "model_policy": {"preferred": "light"},
        "tools": ["git", "templates"]
      },
      {
        "name": "completion_agent",
        "responsibilities": ["enforce gates", "create PR", "auto-approve", "auto-merge", "trigger deploy"],
        "model_policy": {"preferred": "light"},
        "tools": ["github_api", "policy_engine", "deploy_workflows"]
      }
    ],
    "orchestration": {
      "pattern": "coordinator",
      "parallelism": {
        "implementers": 2,
        "tests_in_parallel": true,
        "security_in_parallel": true
      },
      "single_writer": "completion_agent",
      "branching": "per-agent branch; merge by coordinator"
    }
  }
}
```

---

## 7) Policy engine (auto-approve/merge rules)

```json
{
  "policy": {
    "command_allowlist": {
      "default": ["git", "npm", "pnpm", "yarn", "pytest", "go", "cargo", "make", "bash"],
      "deny": ["curl", "wget", "ssh", "scp"],
      "note": "network egress disabled by default; enable per-run with approval"
    },
    "sensitive_paths": [".env", "secrets", "infra/", "billing/", "auth/", "payments/"],
    "auto_approval_gates": [
      {"gate": "tests_pass", "required": true},
      {"gate": "lint_pass", "required": true},
      {"gate": "build_pass", "required": true},
      {"gate": "secret_scan_clean", "required": true},
      {"gate": "dependency_scan_ok", "required": true},
      {"gate": "review_score", "required": true, "min": 0.85},
      {"gate": "no_sensitive_paths_modified", "required": true}
    ],
    "manual_approval_triggers": [
      "production_deploy",
      "network_egress_enable",
      "touch_sensitive_paths",
      "major_dependency_upgrade",
      "diff_over_threshold"
    ],
    "diff_threshold": {"files": 25, "lines": 1500},
    "secrets_redaction": {
      "patterns": ["AWS_SECRET_ACCESS_KEY", "PRIVATE_KEY", "BEGIN PRIVATE KEY"],
      "entropy_scan": true
    }
  }
}
```

---

## 8) Deploy targets (one-click)

```json
{
  "deploy_targets": {
    "coolify": {
      "mode": "preferred_via_github_autodeploy_or_action_dispatch",
      "inputs": ["service_name", "branch", "env"],
      "outputs": ["deployment_url", "logs_uri"],
      "workflow": "infra/github/workflows/deploy_coolify.yml"
    },
    "firebase": {
      "mode": "github_actions",
      "inputs": ["project_id", "channel_or_site", "env"],
      "outputs": ["hosting_url", "logs_uri"],
      "workflow": "infra/github/workflows/deploy_firebase.yml"
    },
    "cloudflare_workers": {
      "mode": "github_actions",
      "inputs": ["worker_name", "env"],
      "outputs": ["worker_url", "logs_uri"],
      "workflow": "infra/github/workflows/deploy_cloudflare_workers.yml"
    }
  }
}
```

---

## 9) API contract (REST)

```json
{
  "api": {
    "base": "/v1",
    "endpoints": [
      {"method": "POST", "path": "/projects", "body": {"name": "string", "repo_url": "string", "local_mount_path": "string"}},
      {"method": "GET", "path": "/projects", "body": null},
      {"method": "POST", "path": "/runs", "body": {"project_id": "uuid", "intent": "object", "mode": "interactive|overnight"}},
      {"method": "POST", "path": "/runs/{run_id}/approve", "body": {"approved": true, "notes": "string?"}},
      {"method": "POST", "path": "/runs/{run_id}/pause", "body": {}},
      {"method": "POST", "path": "/runs/{run_id}/resume", "body": {}},
      {"method": "POST", "path": "/runs/{run_id}/cancel", "body": {}},
      {"method": "GET", "path": "/runs/{run_id}", "body": null},
      {"method": "GET", "path": "/runs/{run_id}/artifacts", "body": null},
      {"method": "POST", "path": "/deploy", "body": {"run_id": "uuid", "target": "coolify|firebase|cloudflare_workers", "env": "staging|production", "params": "object"}}
    ]
  }
}
```

---

## 10) CI/CD (GitHub Actions templates)

```json
{
  "github_actions": {
    "required_workflows": [
      {
        "name": "ci",
        "path": "infra/github/workflows/ci.yml",
        "jobs": ["lint", "test", "build", "secret_scan", "dep_scan"]
      },
      {
        "name": "deploy_coolify",
        "path": "infra/github/workflows/deploy_coolify.yml",
        "triggers": ["workflow_dispatch", "push_to_branch"],
        "steps": ["build", "publish", "trigger_coolify"]
      },
      {
        "name": "deploy_firebase",
        "path": "infra/github/workflows/deploy_firebase.yml",
        "triggers": ["workflow_dispatch"],
        "steps": ["build", "firebase_deploy"]
      },
      {
        "name": "deploy_cloudflare_workers",
        "path": "infra/github/workflows/deploy_cloudflare_workers.yml",
        "triggers": ["workflow_dispatch"],
        "steps": ["build", "wrangler_deploy"]
      }
    ],
    "pr_auto_approval": {
      "mode": "GitHub App or fine-scoped token",
      "trigger": "completion_agent_webhook",
      "rules": "only after all checks and gates pass"
    }
  }
}
```

---

## 11) Acceptance tests (definition of done)

```json
{
  "acceptance": {
    "mvp": [
      "User can create a project pointing to a repo mount",
      "User can start a run from UI and see live logs via WS",
      "Runner produces patch artifacts and diff viewer shows them",
      "Voice push-to-talk produces transcript and intent card",
      "Run can be paused/resumed/canceled; state persists",
      "Completion agent can open PR with artifacts links"
    ],
    "automation": [
      "If tests/lint/build/security/review gates pass, PR is auto-approved and auto-merged",
      "If any gate fails, job pauses and requests human approval",
      "Deploy buttons trigger target workflows and stream logs",
      "Production deploy always requires manual approval"
    ],
    "security": [
      "Secrets redacted from logs",
      "Sensitive paths modification triggers manual approval",
      "Network egress disabled by default"
    ]
  }
}
```

---

## 12) Single "builder prompt" (for GitHub agent)

```json
{
  "builder_prompt": {
    "role": "Lead engineer",
    "objective": "Fork OpenHands and build a voice-first, multi-agent web IDE that wraps Open Code, supports durable jobs, auto PR approval/merge with gates, and one-click deploy targets (Coolify/Firebase/Cloudflare Workers) with model routing via an OpenAI-compatible gateway.",
    "constraints": [
      "Self-host on Hostinger VPS via Coolify",
      "Cloudflare in front (Access recommended)",
      "Free-tier bias for edge/targets",
      "Secrets injected at runtime only",
      "Primary UX is intents/plans/jobs; terminal is secondary"
    ],
    "execution_order": [
      "Scan repo for OpenHands extension points and current tool system",
      "Implement Open Code adapter in runner + structured events",
      "Implement FastAPI orchestration + WS + DB schema + RQ",
      "Implement Next.js UI (workspace, jobs, agents, deploy targets)",
      "Implement agent swarm + policy engine + PR automation",
      "Implement voice-to-intent + overnight mode",
      "Add deploy workflows + Coolify/Firebase/Workers pipelines",
      "Write README + Coolify deploy instructions + env var docs"
    ],
    "deliverables": [
      "docker-compose.yml",
      "infra/github/workflows/*",
      "apps/web, apps/api, apps/runner",
      "packages/sdk, packages/workflows, packages/policies, packages/prompts",
      "docs/runbook.md",
      "README.md"
    ]
  }
}
```

---

## 13) Optional XML export (same spec pointer)

```xml
<OpenHandsVoiceIDE specVersion="1.0.0">
  <Hosting primary="HostingerVPS" orchestrator="Coolify" edge="Cloudflare" />
  <Runtime base="OpenHands" toolAdapter="OpenCodeCLI" />
  <UX primary="VoiceFirst" pattern="IntentPlanJob" />
  <Agents>
    <Agent role="planner" />
    <Agent role="implementer" />
    <Agent role="test_agent" />
    <Agent role="security_agent" />
    <Agent role="review_agent" />
    <Agent role="release_agent" />
    <Agent role="completion_agent" />
  </Agents>
  <DeployTargets>
    <Target name="coolify" />
    <Target name="firebase" />
    <Target name="cloudflare_workers" />
  </DeployTargets>
  <Policies autoApprove="true" productionDeployRequiresApproval="true" />
</OpenHandsVoiceIDE>
```

---

## 14) Human note (operational)

- This spec is intended to be dropped into the repo as `SPEC.openhands-voice-ide.json` (or `.md`) and executed by an autonomous GitHub coding agent.
- You do **not** need VS Code for the build if your GitHub agent can open PRs and run CI. VS Code is only needed for manual review/debug.
