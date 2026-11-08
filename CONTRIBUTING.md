# Contributing to Pursely

Thanks for taking the time to contribute.

## Setup

Follow [Getting started](README.md#getting-started) to run the backend and frontend locally.
`python -m app.seed` fills the database with sample data (login `sample@example.com` / `sample1234`).

## Branches

`main` always holds releasable code. It is protected: every change reaches it through a pull request,
and CI must pass before merging. Never commit to `main` directly.

Create a short-lived branch from the latest `main` for each change:

| Prefix | Use for | Example |
|---|---|---|
| `feature/` | New functionality | `feature/budget-rollover` |
| `bugfix/` | Fixing a bug found during development | `bugfix/csv-import-dates` |
| `hotfix/` | An urgent fix for something broken in production, released right away | `hotfix/login-500` |
| `chore/` | Tooling, dependencies, CI, refactoring with no behaviour change | `chore/upgrade-vite` |
| `docs/` | Documentation only | `docs/render-deploy-guide` |

Use lowercase words separated by hyphens. Delete the branch once it is merged.

```bash
git switch main && git pull
git switch -c feature/budget-rollover
# ...commit work...
git push -u origin feature/budget-rollover
gh pr create --fill
```

## Pull requests

- Keep each pull request focused on one change, and describe what changed and why.
- Add an entry under `[Unreleased]` in [CHANGELOG.md](CHANGELOG.md) for anything a user would notice.
- Pull requests are squash-merged, so the PR title becomes the commit on `main`.
  Write it in the imperative mood ("Add budget alerts", not "Added budget alerts"), under 72 characters.

Before opening one, run the same checks as CI:

```bash
cd backend && ruff check . && python -m pytest
cd frontend && npm run build      # type-checks and builds
```

- Add or update tests for backend behaviour changes.
- Schema changes need an Alembic migration: `alembic revision --autogenerate -m "describe change"`.
  CI fails if models and migrations drift.
- Money values are `Decimal`, never `float`.
- Every query that reads user data must filter by the current user.

## Versioning and releases

Pursely follows [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

| Change | Bump | Example |
|---|---|---|
| Breaking change to the API or data that needs users or deployments to adapt | MAJOR | 1.4.2 → 2.0.0 |
| New feature, backwards compatible | MINOR | 1.4.2 → 1.5.0 |
| Bug fix or hotfix only | PATCH | 1.4.2 → 1.4.3 |

The version lives in `backend/app/__init__.py` and `frontend/package.json`, and the running API reports it at `/health`.

To cut a release:

1. On a `chore/release-vX.Y.Z` branch, move the `[Unreleased]` entries in `CHANGELOG.md` under a new
   `## [X.Y.Z] - YYYY-MM-DD` heading and update the compare links at the bottom.
2. Set the new version in `backend/app/__init__.py` and with `npm version X.Y.Z --no-git-tag-version` in `frontend/`.
3. Open a pull request titled `Release vX.Y.Z` and merge it.
4. Tag the merge commit and publish the release:
   ```bash
   git switch main && git pull
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   gh release create vX.Y.Z --title "vX.Y.Z" --generate-notes
   ```
   `--generate-notes` lists the pull requests merged since the last release.
5. Publishing the release builds the Docker images tagged `vX.Y.Z` and `stable`. Render runs `stable`,
   so trigger a deploy there once the build finishes.

### Docker images

| Tag | Built from | Used for |
|---|---|---|
| `latest` | Every merge to `main` that touches `backend/` or `frontend/` | Testing what is about to ship |
| `stable`, `vX.Y.Z` | Every published release | Production on Render |

A weekly job deletes every other image, so the registry only ever holds `stable` and `latest`.
Git tags and GitHub Releases are the permanent history: to roll back, run the publish workflow
manually from an older tag. Real deletion only happens when the repository variable
`IMAGE_CLEANUP_ENABLED` is `true`; otherwise the job only lists what it would delete.

## Reporting bugs and ideas

Open an issue using the bug report or feature request template.
For security problems, see [SECURITY.md](SECURITY.md) instead of opening a public issue.
