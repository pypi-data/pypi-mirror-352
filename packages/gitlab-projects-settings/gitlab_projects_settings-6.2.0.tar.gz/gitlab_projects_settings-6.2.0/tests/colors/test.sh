#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gitlab-projects-settings --help
gitlab-projects-settings --help --no-color
gitlab-projects-settings --set themes no_color 1
gitlab-projects-settings --help
gitlab-projects-settings --set themes no_color 0
gitlab-projects-settings --help
gitlab-projects-settings --set themes no_color UNSET
gitlab-projects-settings --help
FORCE_COLOR=1 gitlab-projects-settings --help
FORCE_COLOR=0 gitlab-projects-settings --help
NO_COLOR=1 gitlab-projects-settings --help
