param(
    [Parameter(Mandatory=$true)][int]$Epic
)

$repoRoot = "C:\dev\InvoMatch"
$manifestPath = Join-Path $repoRoot ("docs\architecture\epic-manifests\epic-{0:d2}.json" -f $Epic)
$templatePath = Join-Path $repoRoot "docs\architecture\templates\EPIC_ARCHITECTURE_TEMPLATE.md"

if (-not (Test-Path $manifestPath)) {
    Write-Host "ERROR: manifest not found: $manifestPath"
    exit 1
}

if (-not (Test-Path $templatePath)) {
    Write-Host "ERROR: template not found: $templatePath"
    exit 1
}

$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$outputPath = Join-Path $repoRoot ("docs\architecture\" + $manifest.required_architecture_file)

if (Test-Path $outputPath) {
    Write-Host "ERROR: architecture file already exists: $outputPath"
    exit 1
}

$template = Get-Content $templatePath -Raw
$title = "# EPIC $($manifest.epic_number) - $($manifest.epic_name)"
$content = $template -replace '^# EPIC X - Architecture', $title

$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($outputPath, $content, $utf8)

Write-Host "OK: architecture file created: $outputPath"