$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) { throw 'OPENAI_API_KEY manglar' }
Set-Location -LiteralPath $root
& py -3 (Join-Path $root 'astra_agent.py')
if ($LASTEXITCODE -ne 0) { throw ('Astra-agent returnerte ' + $LASTEXITCODE) }
