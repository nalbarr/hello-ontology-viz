Goal:
- Add a GitHub Actions workflow that runs on push/PR
- Install dependencies via uv (uv sync)
- Run `make test` (fast tests) on every push/PR
- Optionally run `make test-all` (includes slow/reasoner tests, requires Java) on a schedule or main-branch-only
- Catch environment issues early (e.g. VIRTUAL_ENV / interpreter mismatches) before they surface locally
