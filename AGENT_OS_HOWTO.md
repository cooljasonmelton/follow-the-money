# Follow The Money – Agent OS Workflow

This repo is wired up with [Agent OS](https://buildermethods.com/agent-os) so AI copilots can work from the same playbook as the team. 

*“Which Agent OS command do I run, and in what order?”*  
Use the sequence below:

## Command Order At A Glance

```
/plan-product
/shape-spec
/write-spec
/create-tasks
/implement-tasks
```

- `/plan-product` – capture the mission, roadmap, and tech stack for the product
- `/shape-spec` – initialize a dated spec folder and collect requirements
- `/write-spec` – convert approved requirements into a concise implementation-ready spec
- `/create-tasks` – break the spec into grouped, dependency-aware task lists
- `/implement-tasks` – implement each task group (or delegate via `/orchestrate-tasks`)

Each command lives under `agent-os/commands/<command-name>/` and contains numbered phase files you follow in sequence.

**For more information:**

---

### 1. `/plan-product`
**Why run it?** Establish shared context (mission, roadmap, tech stack) before building anything.  
**Source files:** `agent-os/commands/plan-product/plan-product.md` (with numbered sub-files).  
**Outputs:**
- `agent-os/product/mission.md`
- `agent-os/product/roadmap.md`
- `agent-os/product/tech-stack.md`

Run this whenever you start a new product or the strategic direction changes. Future commands assume these docs exist.

### 2. `/shape-spec`
**Why run it?** Kick off a new feature by creating a dated spec folder and gathering requirements.  
**Source files:** `agent-os/commands/shape-spec/*.md`.  
**Outputs:**
- `agent-os/specs/YYYY-MM-DD-feature-name/` with `planning/` and `implementation/`
- `planning/initialization.md` and `planning/requirements.md`

Use `/shape-spec` for every roadmap item you plan to implement, even if you already know roughly what to build; it forces the clarifying questions, visual asset requests, and reuse analysis that Agent OS relies on later.

### 3. `/write-spec`
**Why run it?** Convert the approved requirements into a concise, skimmable implementation spec.  
**Source files:** `agent-os/commands/write-spec/write-spec.md`.  
**Outputs:**
- `agent-os/specs/<current-spec>/spec.md` describing goals, user stories, requirements, visuals, reusable code, and out-of-scope items.

This command expects the spec folder from `/shape-spec` to exist and reads its `planning/requirements.md` plus any visuals.

### 4. `/create-tasks`
**Why run it?** Translate `spec.md` (and/or `requirements.md`) into actionable task groups with dependencies.  
**Source files:** `agent-os/commands/create-tasks/*.md`.  
**Outputs:**
- `agent-os/specs/<current-spec>/tasks.md` with grouped checklists sized for subagents or specialists.

Only run `/create-tasks` after `/write-spec` so the task breakdown reflects the final decisions and standards (including `agent-os/standards/python/data-service.md` and other profiles).

### 5. `/implement-tasks`
**Why run it?** Execute the plan task group by task group, mark progress, and produce the verification report.  
**Source files:** `agent-os/commands/implement-tasks/implement-tasks.md`.  
**Outputs:**
- Code changes plus updated `tasks.md` checkboxes
- Implementation notes inside `agent-os/specs/<current-spec>/implementation/`
- Final verification artifacts inside `agent-os/specs/<current-spec>/verification/`

When running solo, stay inside `/implement-tasks`. If you want to delegate different task groups to focused subagents, swap to `/orchestrate-tasks` (see `agent-os/commands/orchestrate-tasks/orchestrate-tasks.md`) after `/create-tasks`; it walks you through assigning subagents via `orchestration.yml` and monitoring their work.

---

### Tips
- Always follow the numbered sub-files inside each command folder; they enforce the multi-phase workflow (e.g., `1-get-spec-requirements.md` then `2-create-tasks-list.md` inside `/create-tasks`).
- Stick with a single Agent OS profile per project. This repo currently uses the `default` profile, which includes the data-service standards in `agent-os/standards/python/data-service.md`.
- Re-run `~/agent-os/scripts/project-update.sh` if you change profiles or standards so the command files stay in sync.

With that order locked in, you can run through planning → specs → tasks → implementation with confidence that the next command always knows where to pick up.
