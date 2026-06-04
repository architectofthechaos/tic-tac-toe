# Platform Infrastructure Layer

## Acceptance Tests

<!-- Written FIRST, reviewed FIRST. Verified via `docker build` and `helm lint` only — NO Python test files (no test_docker.py, no test_helm.py). -->

### Container image

- AT-1: Given the repository root with a `Dockerfile`, When `docker build` is run, Then it completes successfully and produces an image that contains the application and its installed dependencies.
- AT-2: Given the built image, When a container is started from it, Then the FastAPI service starts and serves on the documented container port.
- AT-3: Given a `.dockerignore` at the repository root, When the image is built, Then build context excludes development cruft (e.g. `.git`, `.venv`, `__pycache__`, `_specs`, `tests`, CI files) and they are absent from the image.

### Helm chart

- AT-4: Given the Helm chart directory, When `helm lint <chart>` is run, Then it reports no failures.
- AT-5: Given the chart and its `values.yaml`, When `helm template <chart>` is rendered, Then it produces exactly one Deployment and one Service and no other Kubernetes resources.
- AT-6: Given default `values.yaml`, When the chart is rendered, Then the Deployment references the configured image repository and tag and exposes the container port, and the Service targets that same port.
- AT-7: Given an overridden value (e.g. image tag or replica count passed via `--set`), When the chart is rendered, Then the rendered Deployment reflects the overridden value.
- AT-8: Given the rendered Service, When inspected, Then it selects the Deployment's pods via matching labels/selectors.
- AT-9: Given the chart is rendered, When the Deployment is inspected, Then the container defines readiness and liveness probes targeting the service's `/health` endpoint on the container port.

## Summary

A minimal platform layer to containerize the tic-tac-toe FastAPI service and deploy it to Kubernetes via Helm. Scope is deliberately lean: a `Dockerfile` and `.dockerignore` for the image, and a Helm chart that renders exactly one Deployment and one Service. Correctness is validated with `docker build` and `helm lint`/`helm template` — no Python test files are produced.

## Users & Use Cases

- **Operator / deployer** — builds the image and installs the chart into a cluster, optionally overriding image tag and replica count.
- **CI pipeline** — builds the image and runs `helm lint` as a gate.
- **Developer** — runs the container locally to reproduce the deployed runtime.

## In Scope / Out of Scope

**In scope**
- A `Dockerfile` at the repository root that builds and runs the FastAPI service.
- A `.dockerignore` that trims the build context.
- A Helm chart containing a Deployment template, a Service template, and a `values.yaml`.
- Validation via `docker build` and `helm lint` / `helm template`.

**Out of scope**
- Docker Compose.
- Image scanning (Trivy) or any security-scan step.
- HorizontalPodAutoscaler (HPA).
- Ingress.
- Any automated test files (`test_docker.py`, `test_helm.py`) — `helm lint` is sufficient.
- ConfigMaps, Secrets, ServiceAccounts, RBAC, PVCs, and other resources beyond the single Deployment + Service.

## Functional Requirements

Each requirement maps to one or more acceptance tests.

- FR-1 — **Dockerfile builds the service.** A `Dockerfile` at the repo root installs dependencies and packages the application into a runnable image. *(AT-1)*
- FR-2 — **Container runs the service.** The image's start command launches the FastAPI service listening on a defined container port. *(AT-2)*
- FR-3 — **.dockerignore trims context.** A `.dockerignore` excludes VCS, virtualenvs, caches, specs, tests, and CI files from the build context. *(AT-3)*
- FR-4 — **Chart passes lint.** The Helm chart is well-formed and passes `helm lint` with no failures. *(AT-4)*
- FR-5 — **Renders only Deployment + Service.** Rendering the chart yields exactly one Deployment and one Service and no other Kubernetes resources. *(AT-5)*
- FR-6 — **Values wire image and port.** `values.yaml` drives the image repository/tag and the container port; the Deployment and Service consume them consistently. *(AT-6)*
- FR-7 — **Overrides apply.** Values overridden at install/template time (e.g. image tag, replica count) are reflected in the rendered output. *(AT-7)*
- FR-8 — **Service selects the pods.** The Service selector matches the Deployment pod labels so traffic reaches the pods. *(AT-8)*
- FR-9 — **Health probes.** The Deployment defines readiness and liveness probes against the service's `/health` endpoint on the container port. *(AT-9)*

## Non-Functional Requirements

- **Tooling:** Docker for image build; Helm 3 for the chart. No additional platform tooling.
- **Leanness:** the chart contains only what is needed to render a Deployment and a Service (plus `Chart.yaml`, `values.yaml`, and template helpers as needed by Helm).
- **Validation:** `docker build` succeeds; `helm lint` reports no failures; `helm template` renders the expected resources. These are the only required checks.
- **Consistency:** the image port, Deployment containerPort, and Service target port refer to the same value sourced from `values.yaml`.
- **Reproducibility:** building the image from a clean checkout produces a running service without manual steps.

## Configuration Model

Configurable values exposed by `values.yaml` (shapes, not code):

| Value | Meaning | Default (assumed) |
|-------|---------|-------------------|
| `image.repository` | Container image repository (local image name, no registry prefix) | the locally built service image name |
| `image.tag` | Image tag to deploy | `latest` or chart appVersion |
| `image.pullPolicy` | Image pull policy (local image must not be pulled) | `IfNotPresent` |
| `replicaCount` | Number of Deployment replicas | `1` |
| `service.type` | Kubernetes Service type | `ClusterIP` |
| `service.port` | Port the Service exposes | the container port |
| `containerPort` | Port the app listens on in the container | `8000` |
| `probes.readiness` / `probes.liveness` | HTTP probe settings against `/health` (path, port, timing) | enabled, path `/health` |

## Constraints & Assumptions

- The application is the existing tic-tac-toe FastAPI service; the container serves it on port `8000` by default.
- **Local-only image:** images are built and run against local Docker Desktop with no external registry; `image.pullPolicy` is `IfNotPresent` so Kubernetes uses the locally built image rather than pulling.
- **Resource limits:** CPU/memory requests and limits are intentionally left unset in v1.
- Service type defaults to `ClusterIP` (Ingress is out of scope).
- "Exactly one Deployment and one Service" refers to rendered Kubernetes resources; `Chart.yaml`, `values.yaml`, and `_helpers.tpl` are chart scaffolding, not rendered resources.
- Helm 3 (templating without Tiller) is the target.
- No persistence is required; the service holds state in memory.

## Resolved Decisions

- **Registry:** none — images are built and run locally against Docker Desktop; no external registry. `image.pullPolicy` is `IfNotPresent`.
- **Health probes:** yes — the Deployment defines readiness and liveness probes against the `/health` endpoint (FR-9, AT-9).
- **Resource limits:** left unset in v1.
