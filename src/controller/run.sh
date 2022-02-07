#!/bin/bash

if ! xset q &>/dev/null; then
    sleep 1
    exit 1
fi

/usr/bin/python3 vtkgui.py
