param(
    [Parameter(Mandatory=$true)][int]$Epic,
    [Parameter(Mandatory=$true)][string]$Status,
    [Parameter(Mandatory=$true)][string]$Notes
)

$file = "C:\dev\InvoMatch\docs\architecture\EPIC_TRACKER.md"

if (-not (Test-Path $file)) {
    Write-Host "ERROR: EPIC_TRACKER.md not found"
    exit 1
}

$lines = Get-Content $file

for ($i = 0; $i -lt $lines.Length; $i++) {

    if ($lines[$i] -match "^\|\s*$Epic\s*\|") {
        # split columns
        $cols = $lines[$i].Split("|")

        # normalize spaces
        for ($j=0; $j -lt $cols.Length; $j++) {
            $cols[$j] = $cols[$j].Trim()
        }

        # rebuild row
        # format: | Epic | Name | Status | Notes |
        $newLine = "| $($cols[1]) | $($cols[2]) | $Status | $Notes |"

        $lines[$i] = $newLine
        break
    }
}

$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($file, $lines, $utf8)

Write-Host "OK: EPIC $Epic updated"