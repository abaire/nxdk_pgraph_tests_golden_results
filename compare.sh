#!/usr/bin/env bash
set -eu
set -o pipefail

if [[ $# < 1 ]]; then
  echo "Usage: $(basename $0) <path_to_emulator_outputs>"
  exit 1
fi

readonly script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

readonly emu_dir="$1"

readonly pdiff="${script_dir}/perceptualdiff/build/perceptualdiff"
readonly diff_dir="${script_dir}/output"


function check_file {
  local img="${1}"
  
  filename=$(basename "${img}")
  subdir=$(basename $(dirname "${img}"))
  emu_image="${emu_dir}/${subdir}/${filename}"
  diff_file="${diff_dir}/${subdir}/${filename}"

  set +e
  "${pdiff}" "${img}" "${emu_image}" --verbose --output "${diff_file}"
  different=$?
  set -e
  
  if [[ ${different} -ne 0 ]]; then
    echo "${img} differs"
  else
    rm -f "${diff_file}"
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

test_dirs=($(find "${script_dir}" -maxdepth 1 -type d))
for d in "${test_dirs[@]}"; do
  perform_test "${d}"
done

