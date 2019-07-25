#!/bin/bash

relPath="`dirname $0`"
cd $relPath
PYTHONPATH="$relPath/riffler_env/bin/python"
if [ ! -f $PYTHONPATH ]; then
    python -m venv "$relPath/riffler_env"
    source "$relPath/riffler_env/bin/activate"
    pip install -r "$relPath/requirements.txt"
fi 
$PYTHONPATH "$relPath/riffler.py"