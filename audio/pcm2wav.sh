#!/usr/bin/env bash

SAMPLING_RATE=16000
CH=1
BITS=16

if [ $# -ne 2 ]; then
  echo "Usage: $0 [input] [output]"
  exit 1
fi

INPUT_FILE=$1
OUTPUT_FILE=$2

sox -r ${SAMPLING_RATE} -c ${CH} -b ${BITS} -e signed-integer -t raw ${INPUT_FILE} ${OUTPUT_FILE}

echo "Completed. ${INPUT_FILE} >> ${OUTPUT_FILE}"