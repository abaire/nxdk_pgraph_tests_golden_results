#!/usr/bin/env bash

set -eu
set -o pipefail

readonly raw_base_url='https://raw.githubusercontent.com/abaire/nxdk_pgraph_tests_golden_results/main'

readonly results_dir="$1"
readonly wiki_dir="$2"

readonly ignore_dirs=(
  output
  perceptualdiff
  scripts
)


function process_dir() {
  test_dir=$1
  test_name=$2
  echo "Processing ${test_name} from ${test_dir}..."

  # Github's wiki does not seem to support pages in subdirs, so they are only used for
  # image content. Test suites should all have unique names so this should not cause
  # issues.
  output_file="${wiki_dir}/Results-${test_name}.md"
  echo "# Test suite ${test_name}" > "${output_file}"
  echo "" >> "${output_file}"

  for image_file in "${test_dir}"/*.png; do
    image_relative_path="${image_file##${results_dir}/}"
    image_filename="${image_file##${test_dir}/}"

    echo "## ${image_filename}" >> "${output_file}"
    echo "![${image_filename}](${raw_base_url}/${image_relative_path})" >> "${output_file}"
  done
}

function main() {

  output_pages=()

  for test_dir in "${results_dir}/"*/; do
    test_dir="${test_dir%%/}"
    test_name="${test_dir##${results_dir}/}"

    set +e
    printf '%s\n' "${ignore_dirs[@]}" | grep -F -x "${test_name}" > /dev/null
    ignored=$?
    set -e
    if [[ $ignored -eq 0 ]]; then
      continue
    fi

    process_dir "${test_dir}" "${test_name}"
    output_pages+=("${test_name}")
  done

  readonly results_index="${wiki_dir}/Results.md"
  echo "Results" > "${results_index}"
  for page in "${output_pages[@]}"; do
    echo "- [[${page}|Results-${page}]]" >> "${results_index}"
  done
}

main
