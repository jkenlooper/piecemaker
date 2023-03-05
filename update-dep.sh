#!/usr/bin/env sh

# Modified from the original in python-worker directory in https://github.com/jkenlooper/cookiecutters .

set -o errexit


script_name="$(basename "$0")"
project_name="$(basename "$0" ".sh")-dep"

# Use $PWD to avoid using 'realpath' since it isn't always available.
project_dir="$PWD"
test -e "$project_dir/$script_name" || (echo "ERROR: Should run $script_name from the $project_name project directory." 1>&2 && exit 1)

usage() {
  cat <<HERE
Update the python requirement txt files, check for known vulnerabilities,
download local python packages to dep/.

Usage:
  $script_name -h
  $script_name -i
  $script_name

Options:
  -h                  Show this help message.
  -i                  Switch to interactive mode.

HERE
}

interactive="n"

while getopts "hi" OPTION ; do
  case "$OPTION" in
    h) usage
       exit 0 ;;
    i)
       interactive="y"
       ;;
    ?) usage
       exit 1 ;;
  esac
done
shift $((OPTIND - 1))

mkdir -p "$project_dir/dep"
image_name="$project_name"
docker image rm "$image_name" > /dev/null 2>&1 || printf ""
DOCKER_BUILDKIT=1 docker build \
  --quiet \
  -t "$image_name" \
  -f "$project_dir/update-dep.Dockerfile" \
  "$project_dir" > /dev/null

container_name="$project_name"
if [ "$interactive" = "y" ]; then
  docker run -i --tty \
    --user root \
    --name "$container_name" \
    "$image_name" sh > /dev/null

else
  docker run -d \
    --name "$container_name" \
    "$image_name" > /dev/null
fi

docker cp "$container_name:/home/dev/app/requirements.txt" "$project_dir/requirements.txt"
docker cp "$container_name:/home/dev/app/requirements-dev.txt" "$project_dir/requirements-dev.txt"
docker cp "$container_name:/home/dev/app/requirements-test.txt" "$project_dir/requirements-test.txt"
docker cp "$container_name:/home/dev/app/dep/." "$project_dir/dep/"
# Only copy over the security issues and vulnerabilities report if there are any.
rm -f "$project_dir/vulnerabilities-pip-audit.txt"
docker cp "$container_name:/home/dev/vulnerabilities-pip-audit.txt" "$project_dir/vulnerabilities-pip-audit.txt" > /dev/null 2>&1 || printf ""
rm -f "$project_dir/security-issues-from-bandit.txt"
docker cp "$container_name:/home/dev/security-issues-from-bandit.txt" "$project_dir/security-issues-from-bandit.txt" > /dev/null 2>&1 || printf ""
docker stop --time 0 "$container_name" > /dev/null 2>&1 || printf ""
docker rm "$container_name" > /dev/null 2>&1 || printf ""
