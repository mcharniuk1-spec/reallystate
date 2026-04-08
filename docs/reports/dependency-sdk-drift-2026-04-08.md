# Dependency and SDK Drift Report

Date: 2026-04-08
Workspace: `/Users/getapple/Documents/Real Estate Bulg`

## Scope

This report checks declared dependency/runtime targets against what is actually present in the repository and executable in the local environment. It avoids guessing target versions beyond what the repo declares.

## Repository facts

### Python

- Declared Python runtime: `3.12`
  - Source: [`.python-version`](/Users/getapple/Documents/Real%20Estate%20Bulg/.python-version)
- Declared project runtime: `>=3.12`
  - Source: [`pyproject.toml`](/Users/getapple/Documents/Real%20Estate%20Bulg/pyproject.toml)
- Current local interpreter observed during this run: `Python 3.9.6`
  - Command: `python3 --version`

### Node / frontend

- Declared frontend package manager manifest exists:
  - Source: [`package.json`](/Users/getapple/Documents/Real%20Estate%20Bulg/package.json)
- Declared web stack:
  - `next ^15.3.0`
  - `react ^19.1.0`
  - `react-dom ^19.1.0`
  - `@tanstack/react-query ^5.74.0`
  - `@deck.gl/core ^9.1.0`
  - `@deck.gl/layers ^9.1.0`
  - `@deck.gl/react ^9.1.0`
  - `maplibre-gl ^5.3.0`
- Current frontend implementation in repo:
  - [`web/index.html`](/Users/getapple/Documents/Real%20Estate%20Bulg/web/index.html) only
  - no `web/app`, `web/pages`, `web/package.json`, `tsconfig.json`, or `next.config.*`
- Current local tool availability observed during this run:
  - `node`: not found
  - `npm`: not found
  - `pnpm`: not found
  - `yarn`: not found

### Locking / reproducibility

- No Python lockfile found:
  - no `poetry.lock`
  - no `requirements*.txt`
- No Node lockfile found:
  - no `package-lock.json`
  - no `pnpm-lock.yaml`
  - no `yarn.lock`
- No Node version file found:
  - no `.nvmrc`
  - no `.tool-versions`

### Import surface vs declared Python dependencies

Observed top-level third-party imports in `src/` and `tests/`:

- `httpx`
- `sqlalchemy`

Observed top-level imports in `scripts/` are stdlib-only.

Declared Python dependencies in [`pyproject.toml`](/Users/getapple/Documents/Real%20Estate%20Bulg/pyproject.toml) include many additional packages, including:

- `alembic>=1.15`
- `asyncpg>=0.30`
- `beautifulsoup4>=4.13`
- `boto3>=1.37`
- `dateparser>=1.2`
- `fastapi>=0.115`
- `imagehash>=4.3`
- `lxml>=5.3`
- `phonenumbers>=8.13`
- `pillow>=11.0`
- `price-parser>=0.5`
- `psycopg[binary]>=3.2`
- `pydantic>=2.11`
- `pyproj>=3.7`
- `redis>=5.2`
- `shapely>=2.0`
- `structlog>=25.0`
- `temporalio>=1.10`
- `tenacity>=9.0`
- `uvicorn[standard]>=0.34`

This is not automatically wrong. The roadmap in [`PLAN.md`](/Users/getapple/Documents/Real%20Estate%20Bulg/PLAN.md) explicitly calls for these systems later. The concrete issue is that the repo currently does not pin a tested resolved set for them.

## Confirmed drift

### 1. Runtime drift: Python target vs actual executable

Confirmed.

- Repo target: Python `3.12` / `>=3.12`
- Local executable used by default: Python `3.9.6`

Why this matters:

- A quick parsing script failed because `tomllib` is unavailable on 3.9.
- Current tests still pass because they do not exercise many runtime-only dependency paths.
- This can hide breakage until a developer actually runs migrations, API code, or future FastAPI/Temporal paths.

Minimal alignment action:

1. Standardize all documented commands on Python 3.12.
2. Add a bootstrap note that `python3` must resolve to 3.12 or use an explicit 3.12 interpreter.
3. Consider a small runtime guard in tooling or CI that fails fast on `<3.12`.

### 2. Reproducibility drift: manifests without lockfiles

Confirmed.

- Python manifest uses open lower bounds like `fastapi>=0.115` and `sqlalchemy>=2.0`.
- Node manifest uses caret ranges like `next ^15.3.0` and `react ^19.1.0`.
- No lockfiles are committed, so the repo does not define a reproducible current resolved dependency set.

Why this matters:

- A fresh install today can resolve to versions different from the versions another developer tested.
- The automation cannot cite a current resolved version from the repo because none is recorded.

Minimal alignment action:

1. Pick one Python environment workflow and commit its lock artifact.
   - Option A: keep `pyproject.toml` and add a generated pinned requirements/constraints file.
   - Option B: adopt a resolver with a native lockfile.
2. Pick one Node package manager and commit its lockfile.
3. Do not broaden manifest ranges further until locks exist.

Target versions:

- Current declared targets are only the manifest ranges in [`pyproject.toml`](/Users/getapple/Documents/Real%20Estate%20Bulg/pyproject.toml) and [`package.json`](/Users/getapple/Documents/Real%20Estate%20Bulg/package.json).
- Exact target resolved versions are unclear from the repo today and should be treated as a follow-up decision, not guessed here.

### 3. Frontend/tooling drift: declared Next stack vs actual runnable frontend

Confirmed.

- Declared stack: Next.js/React toolchain in [`package.json`](/Users/getapple/Documents/Real%20Estate%20Bulg/package.json)
- Actual runnable frontend path: `make run-frontend` serves static HTML via Python HTTP server from [`web/index.html`](/Users/getapple/Documents/Real%20Estate%20Bulg/web/index.html)
  - Source: [`Makefile`](/Users/getapple/Documents/Real%20Estate%20Bulg/Makefile)

Why this matters:

- The manifest suggests an active Next application, but the repo does not yet contain one.
- This makes dependency updates for Next/React hard to validate because there is no app source and no Node runtime configured.

Minimal alignment action:

1. Choose one of these and document it explicitly:
   - Option A: keep the Next stack declaration, but mark it as planned-only and defer version movement until the first real Next app files exist.
   - Option B: remove or relocate the Node manifest until Phase 5+ frontend work begins.
2. Keep `run-frontend` aligned with the actual implementation until a Next app exists.

Recommended choice:

- Option A is the smallest change because the repo plan already describes frontend work as later-phase and [`web/index.html`](/Users/getapple/Documents/Real%20Estate%20Bulg/web/index.html) explicitly says the Next.js product UI is planned later.

## Items that look ahead-of-phase, not necessarily drift

These are declared but not yet exercised in the current source tree:

- `fastapi`
- `temporalio`
- `redis`
- `boto3`
- `asyncpg`
- `psycopg[binary]`
- `pydantic`
- `pyproj`
- `shapely`
- several parser/media helpers

Because [`PLAN.md`](/Users/getapple/Documents/Real%20Estate%20Bulg/PLAN.md) and [`README.md`](/Users/getapple/Documents/Real%20Estate%20Bulg/README.md) describe upcoming phases for persistence, workers, APIs, and media processing, I am treating these as anticipatory dependencies, not removal candidates. The actual drift is the absence of a pinned, reproducible tested set.

## Minimal alignment plan

1. Fix the runtime contract first.
   - Make Python 3.12 the enforced local and CI baseline.
   - Add a fast-fail version check to install/test entrypoints or CI.
2. Add lockfiles before changing package versions.
   - Python: choose a lock strategy and commit it.
   - Node: choose a package manager and commit its lockfile.
3. Clarify frontend status.
   - Keep the current static shell and document the Next manifest as planned-only, or remove the manifest until implementation starts.
4. After lockfiles exist, review actual version movement.
   - At that point, compare declared manifests to resolved locks and upgrade only the packages the repo truly uses.

## Commands and observed outputs

### Workspace and memory

Command:

```bash
pwd && ls -la
```

Key output:

```text
/Users/getapple/Documents/Real Estate Bulg
```

### Manifest and lockfile discovery

Command:

```bash
rg --files -g 'package.json' -g 'package-lock.json' -g 'pnpm-lock.yaml' -g 'yarn.lock' -g 'poetry.lock' -g 'pyproject.toml' -g 'requirements*.txt' -g 'Pipfile*' -g '.python-version' -g '.nvmrc' -g '.tool-versions' -g 'Cargo.toml' -g 'Cargo.lock' -g 'go.mod' -g 'Gemfile' -g 'Gemfile.lock' -g 'src/**' -g 'tests/**'
```

Key output:

```text
.python-version
package.json
pyproject.toml
src/...
tests/...
```

No lockfiles were present in that result.

### Python version check

Command:

```bash
python3 --version && which python3
```

Output:

```text
Python 3.9.6
/usr/bin/python3
```

### Node tool availability

Command:

```bash
node --version
npm --version
pnpm --version
yarn --version
```

Observed result: no versions were returned; the tools are not available in this environment.

### Python import-surface check

Command:

```bash
rg -n "^(from|import) " src tests scripts -g '*.py'
```

Key result:

- `src/` and `tests/` use `httpx` and `sqlalchemy` as third-party imports.
- `scripts/` are stdlib-only.

### Test run

Command:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Output summary:

```text
Ran 21 tests in 0.013s
OK (skipped=1)
```

## Conclusion

There is dependency/SDK drift, but the minimal corrective path is process and environment alignment, not broad version churn:

- enforce Python 3.12
- commit lockfiles
- clarify the frontend’s planned-vs-active toolchain state

I did not change dependency versions in this run because the repo does not record current resolved targets, and guessing them would violate the grounding rule.
