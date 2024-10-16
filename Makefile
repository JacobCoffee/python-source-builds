.DEFAULT_GOAL:=help
.PHONY: help install clean update export lint type-check test frontend serve applet docs-serve docs

help: ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install:  clean ## Install project in development mode
	@uv sync --force-reinstall --dev --all-extras
	@uv run nodeenv --python-virtualenv
	@uv run npm install

clean:  ## Remove generated project files
	@rm -rf .venv/ .*_cache/ .coverage  *.egg-info/ node_modules/ docs/_build

update:  ## Update project dependencies
	@uv sync --upgrade

export:  ## Export project dependencies
	@uv export --format requirements-txt > requirements.txt

lint:  ## Lint and format codebase
	-@uv run --no-sync ruff check --fix .
	-@uv run ruff format
	-@prettier --ignore-unknown ./**/*.{html,css,js,json} --write

type-check:  ## Run type checking
	@uv run mypy .

test:  ## Run tests
	@uv run --no-sync pytest .

frontend:  ## Run CSS compiler in watch mode
	@uv run tailwindcss -i ./resources/tailwind.css -o ./app/applets/core/public/styles.css --watch

serve:  ## Run the API in development mode
	@uv run app run --debug --reload

applet:  ## Generate a new applet
	@uv run copier copy gh:JacobCoffee/applet-template app/applets/

docs-serve:  ## Serve the docs locally
	@uv run sphinx-autobuild docs docs/_build/ -j auto --watch app --watch docs --watch tests --watch CONTRIBUTING.rst --port 8002

docs:  ## Dump the existing built docs and rebuild them
	@uv run sphinx-build -M html docs docs/_build/ -E -a -j auto --keep-going

changelog:	## Generate a changelog
	@uv run git-cliff --config pyproject.toml --output docs/changelog.rst
