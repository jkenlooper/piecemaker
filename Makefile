SHELL := sh
.SHELLFLAGS := -o errexit -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:
.ONESHELL:

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
project_dir := $(dir $(mkfile_path))

DOCKER := docker

src_files := Dockerfile pip-requirements.txt pip-audit.sh pyproject.toml install-libspatialindex.sh $(shell find src/piecemaker -type f)

HASH := $(shell echo "$(src_files)" | xargs -n1 md5sum | sort | md5sum - | cut -d' ' -f1)

objects := .dep-$(HASH) security-issues-from-bandit.txt .iidfile

# For debugging what is set in variables.
inspect.%:
	@printf "%s" '$($*)'

# Always run.  Useful when target is like targetname.% .
# Use $* to get the stem
FORCE:

.PHONY: all
all: $(objects) ## Default is to create the dep/* and requirements.txt files

.dep-$(HASH) requirements.txt vulnerabilities-pip-audit.txt &: $(src_files)
	rm -f .dep-*
	tmp_iidfile="$$(mktemp)"
	$(DOCKER) build \
		--target build \
		--iidfile "$$tmp_iidfile" \
		-f "$(project_dir)Dockerfile" \
		"$(project_dir)"
	image_name="$$(cat "$$tmp_iidfile")"
	rm -f "$$tmp_iidfile"
	container_name="$$(
		$(DOCKER) run -d \
			"$$image_name"
	)"
	$(DOCKER) cp --quiet "$$container_name:/home/dev/app/requirements.txt" "$(project_dir)requirements.txt"
	rm -f $(project_dir)dep/*.whl
	rm -f $(project_dir)dep/*.tar.gz
	$(DOCKER) cp --quiet "$$container_name:/home/dev/app/dep/." "$(project_dir)dep/"
	# Only copy over the vulnerabilities report if there is one.
	rm -f "$(project_dir)vulnerabilities-pip-audit.txt"
	$(DOCKER) cp --quiet "$$container_name:/home/dev/app/vulnerabilities-pip-audit.txt" "$(project_dir)vulnerabilities-pip-audit.txt"
	$(DOCKER) stop --time 0 "$$container_name"
	$(DOCKER) rm "$$container_name"
	$(DOCKER) image rm "$$image_name"
	touch .dep-$(HASH) requirements.txt vulnerabilities-pip-audit.txt

security-issues-from-bandit.txt: $(src_files)
	tmp_iidfile="$$(mktemp)"
	$(DOCKER) build \
		--target app \
		--iidfile "$$tmp_iidfile" \
		-f "$(project_dir)Dockerfile" \
		"$(project_dir)"
	image_name="$$(cat "$$tmp_iidfile")"
	rm -f "$$tmp_iidfile"
	container_name="$$(
		$(DOCKER) run -d \
			"$$image_name"
	)"
	# Only copy over the security issues if there is one.
	rm -f "$(project_dir)security-issues-from-bandit.txt"
	$(DOCKER) cp --quiet "$$container_name:/home/dev/security-issues-from-bandit.txt" "$(project_dir)security-issues-from-bandit.txt"
	$(DOCKER) stop --time 0 "$$container_name"
	$(DOCKER) rm "$$container_name"
	$(DOCKER) image rm "$$image_name"
	touch security-issues-from-bandit.txt

.iidfile: .dep-$(HASH) requirements.txt vulnerabilities-pip-audit.txt security-issues-from-bandit.txt ## Build docker container image
	$(DOCKER) build \
		--iidfile "$@" \
		-f "$(project_dir)Dockerfile" \
		"$(project_dir)"

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: dist
dist: ## Create files for distribution
	python -m build --sdist --wheel

.PHONY: clean
clean: ## Remove files that were created
	printf '%s\0' dist/*.tar.gz | xargs -0 rm -f
	printf '%s\0' dist/*.whl | xargs -0 rm -f
	printf '%s\0' dep/*.tar.gz | xargs -0 rm -f
	printf '%s\0' dep/*.whl | xargs -0 rm -f
	printf '%s\0' $(objects) | xargs -0 rm -f

.PHONY: upkeep
upkeep: ## Send to stderr any upkeep comments that have a past due date
	@grep -r -n --exclude-dir='.git/' -E "^\W+UPKEEP\W+(due:\W?\".*?\"|label:\W?\".*?\"|interval:\W?\".*?\")" . \
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
