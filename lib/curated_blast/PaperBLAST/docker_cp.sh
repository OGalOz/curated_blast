#!/bin/bash


if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
else 
      docker create -ti --name dummy $1 bash
      docker cp dummy:/root/cgi/out.html .
fi


