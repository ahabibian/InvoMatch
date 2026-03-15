param(
    [Parameter(Mandatory=$true)][string]$Action,
    [string]$Path,
    [string]$Content
)

function Write-Utf8NoBom($file, $text){
    $dir = Split-Path $file
    if(!(Test-Path $dir)){ New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($file, $text, $enc)
}

switch($Action){

    "touch" {
        Write-Utf8NoBom $Path ""
    }

    "write" {
        Write-Utf8NoBom $Path $Content
    }

    "scaffold-api" {

        $base = @"
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status":"ok"}
"@

        Write-Utf8NoBom "api/health.py" $base
    }

    "readme" {

        $text = @"
# InvoMatch

Lightweight invoice reconciliation SaaS.

Modules:
- ingestion
- matching
- correction
- exports

"@

        Write-Utf8NoBom "README.md" $text
    }

}