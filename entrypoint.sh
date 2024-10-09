#!/bin/bash

if [[ "$1" == "worker" ]]; then
    exec rq worker
else
    exec python3 -m src.main
fi