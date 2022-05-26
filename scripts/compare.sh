#!/usr/bin/env bash
set -eu
set -o pipefail

if [[ $# < 1 ]]; then
  echo "Usage: $(basename $0) <path_to_emulator_outputs> [ignore_missing]"
  exit 1
fi

missing_is_different=1
if [[ $# > 1 ]]; then
  missing_is_different=0
fi

readonly emu_dir="$(realpath "$1")"

readonly pdiff="${PWD}/perceptualdiff/build/perceptualdiff"
readonly diff_dir="${PWD}/output"
readonly log_file="${diff_dir}/log.txt"

function check_file {
  local img="${1}"
  
  local filename=$(basename "${img}")
  local subdir=$(basename $(dirname "${img}"))
  local emu_image="${emu_dir}/${subdir}/${filename}"
  local output_dir="${diff_dir}/${subdir}"
  mkdir -p "${output_dir}"

  local diff_file="${output_dir}/${filename}"

  if [[ -f "${emu_image}" ]]; then
    set +e
    "${pdiff}" "${img}" "${emu_image}" --verbose --output "${diff_file}"
    different=$?
    set -e
  else
    echo "Missing emu output file at ${emu_image}"
    different=${missing_is_different}
  fi
  
  if [[ ${different} -ne 0 ]]; then
    echo "${img} differs"
    echo "FAIL: ${img}" >> "${log_file}"
  else
    rm -f "${diff_file}"
    echo "PASS: ${img}" >> "${log_file}"
  fi  
}

function perform_test {
  local test_dir="${1}"
  for img in "${test_dir}/"*.png; do
    if [[ -f "${img}" ]]; then
      check_file "${img}"
    fi
  done
}


mkdir -p "${diff_dir}"
echo "Starting test" > "${log_file}"

test_dirs=($(find "${PWD}" -maxdepth 1 -type d))
for d in "${test_dirs[@]}"; do
  perform_test "${d}"

  subdir=$(basename "${d}")
  output_dir="${diff_dir}/${subdir}"
  if [[ -d "${output_dir}" && -z "$(ls -A "${output_dir}")" ]]; then
    rmdir "${output_dir}"
  fi
  
done

