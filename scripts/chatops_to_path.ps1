$scriptPath = (Get-Item -Path $MyInvocation.MyCommand.Path).Directory.FullName
$chatOpsPath = Join-Path $scriptPath '..\'
$pythonScript = Join-Path $scriptPath 'ChatOpsFrames.py'

$currentPath = [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::Machine)
[System.Environment]::SetEnvironmentVariable("PATH", "$currentPath;$chatOpsPath", [System.EnvironmentVariableTarget]::Machine)

python $pythonScript $args
