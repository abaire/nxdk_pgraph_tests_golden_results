#!/usr/bin/env bash

set -eu

results_dir="${1}"
readonly results_dir
output_dir="${2}"
readonly output_dir

find "${results_dir}" -name "*.png" -type f -print0 | while IFS= read -r -d $'\0' file; do
  subpath="${file#$results_dir/}"
  output_file="${output_dir}/${subpath}"
  mkdir -p "$(dirname "${output_file}")"

  convert "${file}" -background black -alpha off "${output_file}"

done
