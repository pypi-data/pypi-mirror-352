# Check for typos in texts across the codebase
check-spelling:
	codespell

# Run Vale linter over the docs
vale:
	vale sync
	vale docs/

# Run a linter and a code formatter
lint:
	ruff check --fix
	ruff format
	@echo "✅ Python linting successful!"

# Run a static type checker
type-checking:
	mypy .
	@echo "✅ Type check successful!"

# Run all unit tests
unit-tests:
	pytest .
	@echo "✅ Unit tests successful!"

# Run docs checks: spelling and linting, this can be ran against a single Python version
docs-checks:
	make check-spelling
	make vale
	uv run scripts/checks_docs_completeness.py
	@echo "✅ Docs checks successful!"

# Run Python checks, in CI this should be ran against all supported Python versions
python-checks:
	pre-commit run --all-files
	make type-checking
	make unit-tests

# Run all code quality checks: static and dynamic tests
all-checks:
	make python-checks
	make docs-checks
	@echo "✅ All checks successful!"

# Serve documentation website locally
serve-docs:
	mkdocs serve

# Count lines of code in the project and get output in the command line
count-lines:
	uv run lines_counter.py
