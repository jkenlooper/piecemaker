SHELL := sh
.SHELLFLAGS := -o errexit -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
project_dir := $(dir $(mkfile_path))

# Generate a hash string based on the content of files related to the dependencies.
DEP_HASH := $(shell find . -type f \( -path './update-dep.Dockerfile' -o -path './pip-requirements.txt' -o -path './pyproject.toml' -o -path './src/piecemaker/*' -o -path './update-dep-run-audit.sh' -o -path './update-dep.sh' \) -exec md5sum '{}' \; | sort | md5sum - | cut -d' ' -f1)

objects := .dep-$(DEP_HASH)

# For debugging what is set in variables.
inspect.%:
	@printf "%s" '$($*)'

# Always run.  Useful when target is like targetname.% .
# Use $* to get the stem
FORCE:

.PHONY: all
all: $(objects) ## Default is to create the dep/* files

.dep-$(DEP_HASH): update-dep.sh
	rm -f .dep-*
	rm -f dep/*.whl
	rm -f dep/*.tar.gz
	./$<
	@touch $@

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
