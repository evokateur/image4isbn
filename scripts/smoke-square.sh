#!/bin/bash

token="$(pass api/square/sandbox/sfizio)"

echo "token: ${token}"

curl https://connect.squareupsandbox.com/v2/catalog/list \
    -H 'Square-Version: 2026-05-20' \
    -H "Authorization: Bearer ${token}" \
    -H 'Content-Type: application/json'
