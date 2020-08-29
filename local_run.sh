#!/bin/bash
# shellcheck disable=SC2115
# shellcheck disable=SC2128
# shellcheck disable=SC2046
# shellcheck disable=SC2220

set -e

declare -a dirs=("sender" "timeline")

main() {
  while getopts "m:r:h" option; do
    case $option in
    m) MOUNT=$OPTARG ;;
    h) HELP='true' ;;
    r) USRREMAP=$OPTARG ;;
    esac
  done
  if [ ! -z ${HELP+x} ]; then
    print_help
  else
    trap cleanup EXIT
    if [ "${MOUNT}" == "true" ]; then
      create_local_dirs_for_mount_fs
    fi
    create_docker_image
    run_docker_image $MOUNT $USRREMAP
  fi
}

print_help() {
  echo "
  -m true -> to mount local fs to docker fs,
  -h -> print this message,
  -r true -> remap user by docker container fs side, you cannot delete created folder without sudo!
  "
}

cleanup() {
  for i in "${dirs[@]}"; do
    rm -rf "$(pwd)/$i/"
  done
}

create_local_dirs_for_mount_fs() {
  for i in "${dirs[@]}"; do
    current_proceeded_dir="$(pwd)/$i"
    if [ -d "$current_proceeded_dir" ]; then
      echo "path exist"
    else
      mkdir "$current_proceeded_dir"
    fi
  done
}

create_docker_image() {
  echo "Build docker container image"
  docker build \
    -f Dockerfile \
    -t python_mailer .
}

run_docker_image() {
  local mount_true=$1
  local user_remap=$2

  echo "Run docker container"
  if [ "${mount_true}" == "true" ]; then
    additional_settings="
    -v $(pwd)/sender:/python_mailer/sender \
    -v $(pwd)/timeline:/python_mailer/timeline \
    "
  else
    additional_settings=""
  fi

  if [ "${user_remap}" == "true" ]; then
    additional_settings="
    ${additional_settings} -e user_remap=true"
  fi

  docker run \
    -it \
    --rm \
    -p 8080:8080 \
    $additional_settings \
    python_mailer
}

main "$@"
