# SOP Generator - PowerShell Alternative
# For Windows users who prefer PowerShell over CMD

param(
    [switch]$Watch,
    [switch]$ProcessExisting,
    [switch]$NoLLM,
    [string]$Caption
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

$arguments = @()

if ($Watch) {
    $arguments += "--watch"
}
elseif ($ProcessExisting) {
    $arguments += "--process-existing"
}
elseif ($Caption) {
    $arguments += "--caption"
    $arguments += $Caption
}
else {
    $arguments += "--watch"
}

if ($NoLLM) {
    $arguments += "--no-llm"
}

Write-Host "Starting SOP Generator..." -ForegroundColor Green
& python sop_generator.py $arguments
