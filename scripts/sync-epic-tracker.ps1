param(
    [string]$RepoRoot = "C:\dev\InvoMatch"
)

$trackerPath = Join-Path $RepoRoot "docs\architecture\EPIC_TRACKER.md"

if (-not (Test-Path $trackerPath)) {
    Write-Host "ERROR: EPIC_TRACKER.md not found at $trackerPath"
    exit 1
}

function Test-AnyFileMatch {
    param(
        [string]$Root,
        [string[]]$Patterns
    )

    foreach ($pattern in $Patterns) {
        $items = Get-ChildItem -Path $Root -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
            $_.FullName -match $pattern
        }
        if ($items) { return $true }
    }

    return $false
}

function Get-EpicState {
    param(
        [int]$Epic,
        [string]$RepoRoot,
        [string]$ArchitectureFile,
        [string[]]$CodePatterns,
        [string[]]$TestPatterns
    )

    $archPath = Join-Path $RepoRoot ("docs\architecture\" + $ArchitectureFile)
    $closurePath = Join-Path $RepoRoot ("docs\architecture\EPIC_{0}_CLOSURE.md" -f $Epic)

    $hasArchitecture = Test-Path $archPath
    $hasClosure = Test-Path $closurePath
    $hasCode = Test-AnyFileMatch -Root $RepoRoot -Patterns $CodePatterns
    $hasTests = Test-AnyFileMatch -Root $RepoRoot -Patterns $TestPatterns

    $status = "NOT STARTED"
    $notes = "no tracked artifacts found"

    if ($hasArchitecture -and $hasCode -and $hasTests -and $hasClosure) {
        $status = "DONE"
        $notes = "architecture + code + tests + closure present"
    }
    elseif ($hasArchitecture -and ($hasCode -or $hasTests)) {
        $status = "PARTIAL"
        $notes = "architecture present; implementation/testing incomplete"
    }
    elseif ($hasArchitecture) {
        $status = "PARTIAL"
        $notes = "architecture drafted; implementation pending"
    }
    elseif ($hasCode -or $hasTests) {
        $status = "IN PROGRESS"
        $notes = "work started in repo; architecture file missing"
    }

    return @{
        Status = $status
        Notes  = $notes
    }
}

$epics = @(
    @{
        Epic = 1
        Name = "Execution Lifecycle Engine"
        ArchitectureFile = "EXECUTION_LIFECYCLE.md"
        CodePatterns = @(
            "src\\invomatch\\services\\.*run",
            "src\\invomatch\\services\\.*lease",
            "src\\invomatch\\services\\.*reconciliation_runs",
            "src\\invomatch\\domain\\.*run"
        )
        TestPatterns = @(
            "tests\\.*run_store",
            "tests\\.*lease",
            "tests\\.*reconciliation_runs"
        )
    },
    @{
        Epic = 2
        Name = "Persistence & Storage Strategy"
        ArchitectureFile = "STORAGE_ARCHITECTURE.md"
        CodePatterns = @(
            "src\\invomatch\\services\\sqlite_run_store",
            "src\\invomatch\\services\\run_store",
            "src\\invomatch\\db\\"
        )
        TestPatterns = @(
            "tests\\.*sqlite",
            "tests\\.*run_store"
        )
    },
    @{
        Epic = 3
        Name = "Matching Intelligence Engine"
        ArchitectureFile = "MATCH_ENGINE_DESIGN.md"
        CodePatterns = @(
            "src\\invomatch\\domain\\matching\\",
            "src\\invomatch\\services\\matching\\"
        )
        TestPatterns = @(
            "tests\\.*matching",
            "tests\\.*decision"
        )
    },
    @{
        Epic = 4
        Name = "Feedback & Learning System"
        ArchitectureFile = "LEARNING_LOOP_ARCHITECTURE.md"
        CodePatterns = @(
            "src\\invomatch\\.*feedback",
            "src\\invomatch\\.*learning"
        )
        TestPatterns = @(
            "tests\\.*feedback",
            "tests\\.*learning"
        )
    },
    @{
        Epic = 5
        Name = "Review & Audit System"
        ArchitectureFile = "REVIEW_SYSTEM_ARCHITECTURE.md"
        CodePatterns = @(
            "src\\invomatch\\.*review",
            "src\\invomatch\\.*audit"
        )
        TestPatterns = @(
            "tests\\.*review",
            "tests\\.*audit"
        )
    },
    @{
        Epic = 6
        Name = "Rule Engine & Governance"
        ArchitectureFile = "RULE_GOVERNANCE_ARCHITECTURE.md"
        CodePatterns = @(
            "src\\invomatch\\.*rule",
            "src\\invomatch\\.*govern"
        )
        TestPatterns = @(
            "tests\\.*rule",
            "tests\\.*govern"
        )
    },
    @{
        Epic = 7
        Name = "Replay & Evaluation Engine"
        ArchitectureFile = "REPLAY_EVALUATION_ARCHITECTURE.md"
        CodePatterns = @(
            "src\\invomatch\\.*replay",
            "src\\invomatch\\.*evaluation",
            "src\\invomatch\\.*regression"
        )
        TestPatterns = @(
            "tests\\.*replay",
            "tests\\.*evaluation",
            "tests\\.*regression"
        )
    },
    @{
        Epic = 8
        Name = "API & Product Layer"
        ArchitectureFile = "API_PRODUCT_ARCHITECTURE.md"
        CodePatterns = @(
            "src\\invomatch\\api\\",
            "src\\invomatch\\routers\\",
            "src\\invomatch\\main\.py",
            "src\\invomatch\\contracts\\"
        )
        TestPatterns = @(
            "tests\\.*api",
            "tests\\.*contract"
        )
    },
    @{
        Epic = 9
        Name = "Observability & Reliability"
        ArchitectureFile = "OBSERVABILITY_RELIABILITY_ARCHITECTURE.md"
        CodePatterns = @(
            "src\\invomatch\\.*telemetry",
            "src\\invomatch\\.*observ",
            "src\\invomatch\\.*metric",
            "src\\invomatch\\.*logging"
        )
        TestPatterns = @(
            "tests\\.*telemetry",
            "tests\\.*observ",
            "tests\\.*metric",
            "tests\\.*logging"
        )
    },
    @{
        Epic = 10
        Name = "SaaS & Scalability"
        ArchitectureFile = "SAAS_SCALABILITY_ARCHITECTURE.md"
        CodePatterns = @(
            "src\\invomatch\\.*tenant",
            "src\\invomatch\\.*auth",
            "src\\invomatch\\.*security",
            "src\\invomatch\\.*scale"
        )
        TestPatterns = @(
            "tests\\.*tenant",
            "tests\\.*auth",
            "tests\\.*security",
            "tests\\.*scale"
        )
    }
)

$lines = Get-Content $trackerPath

for ($i = 0; $i -lt $lines.Length; $i++) {
    foreach ($epicDef in $epics) {
        $epicNumber = [int]$epicDef.Epic
        if ($lines[$i] -match ("^\|\s*" + $epicNumber + "\s*\|")) {
            $state = Get-EpicState `
                -Epic $epicDef.Epic `
                -RepoRoot $RepoRoot `
                -ArchitectureFile $epicDef.ArchitectureFile `
                -CodePatterns $epicDef.CodePatterns `
                -TestPatterns $epicDef.TestPatterns

            $newLine = "| {0} | {1} | {2} | {3} |" -f `
                $epicDef.Epic, `
                $epicDef.Name, `
                $state.Status, `
                $state.Notes

            $lines[$i] = $newLine
            break
        }
    }
}

$currentPhaseLineIndex = -1
for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -eq "System Stage:") {
        $currentPhaseLineIndex = $i + 1
        break
    }
}

if ($currentPhaseLineIndex -ge 0 -and $currentPhaseLineIndex -lt $lines.Length) {
    $doneCount = 0
    $partialOrInProgressCount = 0

    foreach ($epicDef in $epics) {
        $state = Get-EpicState `
            -Epic $epicDef.Epic `
            -RepoRoot $RepoRoot `
            -ArchitectureFile $epicDef.ArchitectureFile `
            -CodePatterns $epicDef.CodePatterns `
            -TestPatterns $epicDef.TestPatterns

        if ($state.Status -eq "DONE") { $doneCount++ }
        if ($state.Status -eq "PARTIAL" -or $state.Status -eq "IN PROGRESS") { $partialOrInProgressCount++ }
    }

    if ($doneCount -ge 8) {
        $lines[$currentPhaseLineIndex] = "Product System (NEAR PRODUCTION)"
    }
    elseif ($doneCount -ge 4 -or $partialOrInProgressCount -ge 4) {
        $lines[$currentPhaseLineIndex] = "Core Platform (STILL NOT PRODUCTION-READY)"
    }
    else {
        $lines[$currentPhaseLineIndex] = "Core Engine (NOT production-ready)"
    }
}

$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($trackerPath, $lines, $utf8)

Write-Host "OK: EPIC_TRACKER.md synced from repo artifacts"