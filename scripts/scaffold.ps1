param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("init")]
    [string]$Action
)

function WriteFile($Path,$Content){
    $dir = Split-Path $Path -Parent
    if($dir -and !(Test-Path $dir)){
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path,$Content,$utf8)
}

if($Action -eq "init"){

WriteFile "pyproject.toml" @"
[project]
name = "invomatch"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi",
  "uvicorn",
  "pydantic",
  "pytest"
]

[tool.pytest.ini_options]
pythonpath = ["src"]
"@

WriteFile ".env.example" @"
APP_ENV=dev
APP_PORT=8000
DATABASE_URL=sqlite:///./invomatch.db
"@

WriteFile "README.md" @"
# InvoMatch

Deterministic invoice reconciliation backend.

## Layers
- API
- Services
- Domain
- Repositories
"@

WriteFile "src/invomatch/main.py" @"
from fastapi import FastAPI
from invomatch.api.health import router as health_router

app = FastAPI(title='InvoMatch')

app.include_router(health_router)
"@

WriteFile "src/invomatch/api/health.py" @"
from fastapi import APIRouter

router = APIRouter()

@router.get('/health')
def health():
    return {'status':'ok'}
"@

WriteFile "src/invomatch/domain/models.py" @"
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class Invoice(BaseModel):
    id:str
    date:date
    amount:Decimal

class Payment(BaseModel):
    id:str
    date:date
    amount:Decimal
"@

WriteFile "src/invomatch/services/matching_engine.py" @"
from invomatch.domain.models import Invoice,Payment

def match(invoice:Invoice,payments:list[Payment]):
    for p in payments:
        if p.amount == invoice.amount:
            return {'status':'matched','payment_id':p.id}
    return {'status':'unmatched'}
"@

WriteFile "tests/test_health.py" @"
from fastapi.testclient import TestClient
from invomatch.main import app

def test_health():
    c = TestClient(app)
    r = c.get('/health')
    assert r.status_code == 200
"@

}