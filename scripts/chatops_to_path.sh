#!/bin/bash
# chatops Bash entry point script
scriptPath="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pythonScript="$scriptPath/ChatOpsFrames.py"
python3 $pythonScript "$@"
