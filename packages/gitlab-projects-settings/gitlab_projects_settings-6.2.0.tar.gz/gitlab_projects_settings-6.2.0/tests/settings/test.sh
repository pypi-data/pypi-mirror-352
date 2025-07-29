#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gitlab-projects-settings --settings
! type sudo >/dev/null 2>&1 || sudo -E env PYTHONPATH="${PYTHONPATH}" gitlab-projects-settings --settings
gitlab-projects-settings --set && exit 1 || true
gitlab-projects-settings --set GROUP && exit 1 || true
gitlab-projects-settings --set GROUP KEY && exit 1 || true
gitlab-projects-settings --set package test 1
gitlab-projects-settings --set package test 0
gitlab-projects-settings --set package test UNSET
gitlab-projects-settings --set updates enabled NaN
gitlab-projects-settings --version
gitlab-projects-settings --set updates enabled UNSET
