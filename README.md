

Created the pre-push hook script and made it executable to automate the tests before each push. The script will run pytest -q and append the "reports.txt" artifact with results, timestamps, directory, and the error message, if any, in three formats:

- reports.txt → append-only, human-readable history.
- pytest_full.txt → full details for debugging.
- junit.xml → integration with CI/CD tools.

[![CI](https://github.com/MoeNamini/infra/actions/workflows/ci.yml/badge.svg)](https://github.com/MoeNamini/infra/actions/workflows/ci.yml)

The automated tests also run locally with git hooks - triggers: git push & git pull
