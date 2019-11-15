#!/bin/bash

echo $1
git add .
git commit -m "debugging UI $1"
git push
