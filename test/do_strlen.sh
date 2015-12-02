#!/bin/bash
echo Parsing $1
for i in $1/*1; do
    echo Diffing $i
    python strlen.py $i >> out
done
