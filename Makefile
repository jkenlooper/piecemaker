SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:
.ONESHELL:

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
project_dir := $(dir $(mkfile_path))

CONTAINER_RUNTIME := docker

source_files := Dockerfile pip-requirements.txt pip-audit.sh pyproject.toml $(shell find src/piecemaker -type f)

HASH := $(shell echo "$(source_files)" | xargs -n1 md5sum | sort | md5sum - | cut -d' ' -f1)

objects := .dep-$(HASH) security-issues-from-bandit.csv requirements.txt vulnerabilities-pip-audit.txt

# For debugging what is set in variables.
inspect.%:
	@printf "%s" '$($*)'

# Always run.  Useful when target is like targetname.% .
# Use $* to get the stem
FORCE:

.PHONY: all
all: $(objects) ## Default is to create the requirements.txt

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: dist
dist: ## Create files for distribution
	python -m build --sdist --wheel

.dep-$(HASH) requirements.txt vulnerabilities-pip-audit.txt &: $(source_files)
	rm -f .dep-*
	tmp_iidfile="$$(mktemp)"
	$(CONTAINER_RUNTIME) build \
		--target build \
		--iidfile "$$tmp_iidfile" \
		-f "$(project_dir)Dockerfile" \
		"$(project_dir)"
	image_name="$$(cat "$$tmp_iidfile")"
	rm -f "$$tmp_iidfile"
	container_name="$$(
		$(CONTAINER_RUNTIME) run -d \
			"$$image_name"
	)"
	$(CONTAINER_RUNTIME) cp "$$container_name:/home/dev/app/requirements.txt" "$(project_dir)requirements.txt"
	rm -f $(project_dir)dep/*.whl
	rm -f $(project_dir)dep/*.tar.gz
	$(CONTAINER_RUNTIME) cp "$$container_name:/home/dev/app/dep/." "$(project_dir)dep/"
	# Only copy over the vulnerabilities report if there is one.
	rm -f "$(project_dir)vulnerabilities-pip-audit.txt"
	$(CONTAINER_RUNTIME) cp "$$container_name:/home/dev/app/vulnerabilities-pip-audit.txt" "$(project_dir)vulnerabilities-pip-audit.txt"
	$(CONTAINER_RUNTIME) stop --time 0 "$$container_name"
	$(CONTAINER_RUNTIME) rm "$$container_name"
	$(CONTAINER_RUNTIME) image rm "$$image_name"
	touch .dep-$(HASH) requirements.txt vulnerabilities-pip-audit.txt

security-issues-from-bandit.csv: $(source_files)
	tmp_iidfile="$$(mktemp)"
	$(CONTAINER_RUNTIME) build \
		--target app \
		--iidfile "$$tmp_iidfile" \
		-f "$(project_dir)Dockerfile" \
		"$(project_dir)"
	image_name="$$(cat "$$tmp_iidfile")"
	rm -f "$$tmp_iidfile"
	container_name="$$(
		$(CONTAINER_RUNTIME) run -d \
			"$$image_name"
	)"
	# Only copy over the security issues if there is one.
	rm -f "$(project_dir)security-issues-from-bandit.csv"
	$(CONTAINER_RUNTIME) cp "$$container_name:/home/dev/security-issues-from-bandit.csv" "$(project_dir)security-issues-from-bandit.csv"
	$(CONTAINER_RUNTIME) stop --time 0 "$$container_name"
	$(CONTAINER_RUNTIME) rm "$$container_name"
	$(CONTAINER_RUNTIME) image rm "$$image_name"
	touch security-issues-from-bandit.csv

.PHONY: container_test
container_test: ## Build docker container image and run test
	tmp_iidfile="$$(mktemp)"
	$(CONTAINER_RUNTIME) build \
		--iidfile "$$tmp_iidfile" \
		-f "$(project_dir)Dockerfile" \
		"$(project_dir)"
	image_name="$$(cat "$$tmp_iidfile")"
	rm -f "$$tmp_iidfile"
	$(CONTAINER_RUNTIME) run \
		-it \
		--rm \
		"$$image_name" --version
	$(CONTAINER_RUNTIME) image rm "$$image_name"

.PHONY: clean
clean: ## Remove any created files which were created by the `make all` recipe.
	printf '%s\0' $(objects) | xargs -0 rm -f

.PHONY: upkeep
upkeep: ## Send to stderr any upkeep comments that have a past due date
	@grep -r -n -E "^\W+UPKEEP\W+(due:\W?\".*?\"|label:\W?\".*?\"|interval:\W?\".*?\")" . \
	| xargs -L 1 \
	python -c "\
import sys; \
import datetime; \
import re; \
now=datetime.date.today(); \
upkeep=\" \".join(sys.argv[1:]); \
m=re.search(r'due: (\d{4}-\d{2}-\d{2})', upkeep); \
due=datetime.date.fromisoformat(m.group(1)); \
remaining=due - now; \
sys.exit(upkeep if remaining.days < 0 else 0)"
