#!/bin/bash
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

# This script builds binary wheels of Tink for Linux based on PEP 599. It
# should be run inside a manylinux2014 Docker container to have the correct
# environment setup.

set -euo pipefail

# The following assoicative array contains:
#   ["<Python version>"]="<python tag>-<abi tag>"
# where:
#   <Python version> = language version, e.g "3.9"
#   <python tag>, <abi tag> = as defined at
#       https://packaging.python.org/en/latest/specifications/, e.g. "cp39-cp39"
declare -A PYTHON_VERSIONS
PYTHON_VERSIONS["3.9"]="cp39-cp39"
PYTHON_VERSIONS["3.10"]="cp310-cp310"
PYTHON_VERSIONS["3.11"]="cp311-cp311"
PYTHON_VERSIONS["3.12"]="cp312-cp312"
PYTHON_VERSIONS["3.13"]="cp313-cp313"
readonly -A PYTHON_VERSIONS

export TINK_PYTHON_ROOT_PATH="${PWD}"
export ARCH="$(uname -m)"

# Install Bazelisk 1.26.0.
readonly BAZELISK_VERSION="1.26.0"
readonly BAZELISK_DOWNLOAD_URL="https://github.com/bazelbuild/bazelisk/releases/download"
BAZELISK_URL="${BAZELISK_DOWNLOAD_URL}/v${BAZELISK_VERSION}/bazelisk-linux-amd64"
BAZELISK_SHA256="6539c12842ad76966f3d493e8f80d67caa84ec4a000e220d5459833c967c12bc"

if [[ "${ARCH}" == "aarch64" || "${ARCH}" == "arm64" ]]; then
  BAZELISK_URL="${BAZELISK_DOWNLOAD_URL}/v${BAZELISK_VERSION}/bazelisk-linux-arm64"
  BAZELISK_SHA256="54f85ef4c23393f835252cc882e5fea596e8ef3c4c2056b059f8067cd19f0351"
fi

readonly BAZELISK_URL
readonly BAZELISK_SHA256
curl -LsS "${BAZELISK_URL}" -o /usr/local/bin/bazelisk
echo "${BAZELISK_SHA256} /usr/local/bin/bazelisk" | sha256sum -c
chmod +x /usr/local/bin/bazelisk

# Install protoc 30.2.
readonly PROTOC_DOWNLOAD_URL="https://github.com/protocolbuffers/protobuf/releases/download"
readonly PROTOC_RELEASE_TAG="30.2"
PROTOC_URL="${PROTOC_DOWNLOAD_URL}/v${PROTOC_RELEASE_TAG}/protoc-${PROTOC_RELEASE_TAG}-linux-x86_64.zip"
PROTOC_SHA256="327e9397c6fb3ea2a542513a3221334c6f76f7aa524a7d2561142b67b312a01f"
if [[ "${ARCH}" == "aarch64" || "${ARCH}" == "arm64" ]]; then
  PROTOC_URL="${PROTOC_DOWNLOAD_URL}/v${PROTOC_RELEASE_TAG}/protoc-${PROTOC_RELEASE_TAG}-linux-aarch_64.zip"
  PROTOC_SHA256="a3173ea338ef91b1605b88c4f8120d6c8ccf36f744d9081991d595d0d4352996"
fi
readonly PROTOC_URL
readonly PROTOC_SHA256
curl -LsS "${PROTOC_URL}" -o protoc.zip
echo "${PROTOC_SHA256} protoc.zip" | sha256sum -c
unzip -o protoc.zip -d /usr/local bin/protoc

# Required to fix https://github.com/pypa/manylinux/issues/357.
export LD_LIBRARY_PATH="/usr/local/lib"

for v in "${!PYTHON_VERSIONS[@]}"; do
  (
    # Executing in a subshell to make the PATH modification temporary.
    # This makes shure that `which python3 ==
    # /opt/python/${PYTHON_VERSIONS[$v]}/bin/python3`, which is a symlink of
    # `/opt/python/${PYTHON_VERSIONS[$v]}/bin/python${v}`. This should allow
    # pybind11_bazel to pick up the correct Python binary [1].
    #
    # [1] https://github.com/pybind/pybind11_bazel/blob/fc56ce8a8b51e3dd941139d329b63ccfea1d304b/python_configure.bzl#L434
    export PATH="${PATH}:/opt/python/${PYTHON_VERSIONS[$v]}/bin"
    python3 -m pip wheel .
  )
done

# Repair wheels to convert them from linux to manylinux.
for wheel in ./tink*.whl; do
    auditwheel repair "${wheel}" -w release
done
