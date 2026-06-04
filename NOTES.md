# OpenHands Assignment — Notes

## Overview

The assignment is driven by **spec-driven development** and **TDD**. A spec is
written and reviewed first, broken into executable tasks, and only then
implemented test-first.

We use the **superpowers** plugin (plus a custom project-level `spec-driven`
skill) to generate standard spec templates and drive the TDD workflow.

## Phase 0 — Setup

1. Set up the GitHub repository.
2. Create the base Claude scaffolding (skills, project config).
3. Initialize git in the project and push to the remote.

## Phase 1 — Tic-Tac-Toe App

1. Generate the spec for the tic-tac-toe app.
2. Break the spec into executable tasks.
3. Iterate through each task and implement it, following TDD (acceptance tests
   written first). For the assignment, tasks are grouped and implemented in bulk
   with Claude Code rather than one PR per task.
4. Add CI so the build is green before any code is pushed to GitHub.
5. Add a `Taskfile.yaml` for local testing.
6. Run the Taskfile locally before pushing — clears issues early, before CI
   catches them.

## Phase 2 — Platform & Infrastructure

Includes Helm and Docker, reflecting the platform-engineer scope.

1. Generate the spec for Docker and Helm.
2. Break the spec into tasks.
3. Extend `Taskfile.yaml` with the platform checks.
4. Validate the phase by deploying the Helm chart directly.

## Phase 3 — Deployment

1. Verify the Helm chart (`helm lint` / `helm template`).
2. Package the chart locally.
3. Create a `kind` cluster.
4. Build the Docker image.
5. Port-forward the Kubernetes pod.
6. Test the deployment.

## Intentionally Skipped

To keep the assignment focused, the following are deliberately out of scope:

1. A separate branch and PR per task.
2. Running the local Taskfile to validate tests/checks after *every* task.
3. Pushing to git after every task.
