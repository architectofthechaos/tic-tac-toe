# Platform Infrastructure Layer — Tasks

## Execution Order

Work top to bottom; each task lists what it depends on.

1. T-001 — Dockerfile + .dockerignore (no dependencies)
2. T-002 — Helm chart scaffold (no dependencies)
3. T-003 — Deployment template with probes (needs T-002)
4. T-004 — Service template (needs T-002)
5. T-005 — Validate rendering and wire `helm lint` (needs T-002, T-003, T-004)

---

### T-001 — Containerize the service (Dockerfile + .dockerignore)
**Description:** Add a `Dockerfile` at the repo root that installs dependencies and packages the FastAPI service into a runnable image listening on port 8000, plus a `.dockerignore` that trims the build context. Built and run locally against Docker Desktop (no registry).
**Acceptance criteria (→ AT):**
- [ ] `docker build` completes and produces an image containing the app and its dependencies (→ AT-1).
- [ ] A container started from the image serves the FastAPI service on port 8000 (→ AT-2).
- [ ] `.dockerignore` excludes `.git`, `.venv`, `__pycache__`, `_specs`, `tests`, and CI files from the build context (→ AT-3).
**Files modified:** `Dockerfile`, `.dockerignore`

---

### T-002 — Scaffold the Helm chart
**Description:** Create the Helm 3 chart skeleton for the service: `Chart.yaml`, a `values.yaml` exposing image repository/tag/pullPolicy, replicaCount, service type/port, containerPort, and probe settings, and a template helpers file for shared labels/selectors. No rendered K8s resources yet beyond what later tasks add.
**Acceptance criteria (→ AT):**
- [ ] `helm lint` on the chart reports no failures (→ AT-4).
- [ ] `values.yaml` defines image (repository/tag/pullPolicy `IfNotPresent`), replicaCount, service.type `ClusterIP`, service.port, containerPort `8000`, and readiness/liveness probe settings (→ AT-6, AT-7, AT-9).
- [ ] Helper labels/selectors are defined for reuse by the Deployment and Service (→ AT-8).
**Files modified:** `helm/tic-tac-toe/Chart.yaml`, `helm/tic-tac-toe/values.yaml`, `helm/tic-tac-toe/templates/_helpers.tpl`, `helm/tic-tac-toe/.helmignore`

---

### T-003 — Deployment template with health probes
**Description:** Add the Deployment template driven by `values.yaml`: image repository/tag, replica count, container port, pod labels, and readiness/liveness HTTP probes against `/health`. Value overrides (e.g. image tag, replicas) must flow through to the rendered output.
**Acceptance criteria (→ AT):**
- [ ] Rendered Deployment references the configured image repository/tag and exposes the container port (→ AT-6).
- [ ] Overriding a value via `--set` (e.g. image tag, replicaCount) is reflected in the rendered Deployment (→ AT-7).
- [ ] Deployment defines readiness and liveness probes targeting `/health` on the container port (→ AT-9).
- [ ] Pod template labels match the shared selector helper (→ AT-8).
**Files modified:** `helm/tic-tac-toe/templates/deployment.yaml`

---

### T-004 — Service template
**Description:** Add the Service template (type from `values.yaml`, default `ClusterIP`) that exposes `service.port` and targets the container port, selecting the Deployment's pods via the shared selector labels.
**Acceptance criteria (→ AT):**
- [ ] Rendered Service exposes the configured port and targets the container port (→ AT-6).
- [ ] Service selector matches the Deployment pod labels (→ AT-8).
**Files modified:** `helm/tic-tac-toe/templates/service.yaml`

---

### T-005 — Validate rendering and wire `helm lint`
**Description:** Confirm the chart renders exactly one Deployment and one Service (and no other K8s resources), and add `helm lint` as a validation step in the Taskfile and CI so the chart is gated on every change. No Python test files are created.
**Acceptance criteria (→ AT):**
- [ ] `helm template` renders exactly one Deployment and one Service and no other resources (→ AT-5).
- [ ] `helm lint` runs clean and is invokable via the Taskfile and runs in CI (→ AT-4).
**Files modified:** `Taskfile.yaml`, `.github/workflows/ci.yaml`
