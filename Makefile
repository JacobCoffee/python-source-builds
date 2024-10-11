.PHONY: install
install:  clean ## Install project in development mode
	@uv sync --force-reinstall --dev --all-extras
	@uv run nodeenv --python-virtualenv
	@uv run npm install

.PHONY: clean
clean:  ## Remove generated project files
	@rm -rf .venv/ .*_cache/ .coverage  *.egg-info/ node_modules/

.PHONY: update
update:  ## Update project dependencies
	@uv sync --upgrade

.PHONY: lint
lint:  ## Lint and format codebase
	-@uv run --no-sync ruff check --fix .
	-@uv run ruff format
	-@prettier --ignore-unknown ./**/*.{html,css,js,yml,json} --write

.PHONY: test
test:  ## Run tests
	@uv run --no-sync pytest .

.PHONY: frontend
frontend:
	@uv run tailwindcss -i ./resources/tailwind.css -o ./app/applets/core/public/styles.css --minify --watch

.PHONY: serve
serve:  ## Run the project in development mode
	@uv run app run --debug --reload

.PHONY: applet
applet:
	@uv run copier copy gh:JacobCoffee/applet-template app/applets/
