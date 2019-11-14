#!/bin/bash

echo $1
git add .
git commit -m "docker replace $1"
git push
