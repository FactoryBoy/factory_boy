#!/bin/sh

cd $(dirname $0)
for f in test_*.py; do
    python -m unittest discover
done
