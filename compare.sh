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

mkdir -p "${diff_dir}"

for img in "${script_dir}/"*.png; do
  filename=$(basename "${img}")
  emu_image="${emu_dir}/${filename}"
  diff_file="${diff_dir}/${filename}"

  set +e
  "${pdiff}" "${img}" "${emu_image}" --verbose --output "${diff_file}"
  different=$?
  set -e
  
  if [[ ${different} ]]; then
    echo "${img} differs"
  else
    rm "${diff_file}"
  fi
done
