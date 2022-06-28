#!/bin/bash

types="organizations projects inventories credential_types credentials"

for t in $types; do
  echo "$t:"
  awx $t list | jq --raw-output '.results[] | " * \(.name) (id=\(.id))"'
  echo
done
