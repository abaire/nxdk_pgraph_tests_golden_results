#!/usr/bin/env bash
set -eu
set -o pipefail

readonly test_output_dir='e:\pgraph\nxdk_pgraph_tests\'

if [[ $# -gt 0 ]]; then
  xbox=$1
else
  if [[ -z "${XBOX:-}" ]]; then
    echo "Usage: $0 <xbox_ip_address>"
    echo ""
    echo "Alternatively, set the XBOX environment variable to your XBOX ip address."
    exit 1
  fi

  xbox="${XBOX}"
fi


echo "Collecting output of nxdk_pgraph_tests from ${xbox}..."
xbdm "${xbox}" getfile "${test_output_dir}" .

