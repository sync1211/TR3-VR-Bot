#!/bin/bash
if [ "$EUID" -eq 0 ]; then
    if ! [ "$1" == "--allow-root" ]; then
        echo "[FATAL]: Root privileges detected! Exiting..."
        exit 1
    else
        shift
        echo "[WARN]: Running as Root; I hope you know what you're doing!"
    fi
fi


if python3 -h &> /dev/null; then
    pyexec=python3
else
    pyexec=python
    if ![ $($pyexec --version | grep " 3.") ]; then
        echo "[FATAL]: Python3 not found! Please make sure that Python3 is installed and added to your PATH!"
        exit 1
    fi
fi


voiceargs=""
if ! command -v ffmpeg &> /dev/null; then
    echo "[WARN]: FFMPEG not found on PATH, voice functions will be disabled!"
    voiceargs="--novoice"
fi

if ls Pipfile.lock &> /dev/null || [ "$1" == "--pipenv" ] && ! [ "$1" == "--pip" ]; then
    echo "[INFO]: Running in pipenv..."
    $pyexec -m pipenv run $pyexec main.py $voiceargs $@
else
    $pyexec main.py $@
fi
