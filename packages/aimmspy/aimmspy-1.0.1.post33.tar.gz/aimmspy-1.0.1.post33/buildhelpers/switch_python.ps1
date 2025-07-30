param (
    [string]$Version
)

if (-not $Version) {
    Write-Host "Usage: .\switch_python.ps1 3.11"
    return
}

# Remove dot for folder name like 3.11 -> 311
$versionNoDot = $Version -replace '\.', ''
$pythonPath = "C:\Python$versionNoDot"
$pythonExe = Join-Path $pythonPath "python.exe"

# Validate path
if (-not (Test-Path $pythonExe)) {
    Write-Host "Python $Version not found at $pythonPath"
    return
}

# Get current user PATH from registry
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathParts = $currentPath -split ';'

# Filter out other Python versions
$filteredParts = $pathParts | Where-Object {
    ($_ -notmatch "^C:\\Python\d{3}(\\Scripts)?$") -and ($_ -ne "")
}

# Prepend new Python path
$newPath = "$pythonPath;$pythonPath\Scripts;" + ($filteredParts -join ';')

# Save to user-level PATH (registry)
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# ALSO update current session PATH
$sessionParts = $env:PATH -split ';'
$sessionFiltered = $sessionParts | Where-Object {
    ($_ -notmatch "^C:\\Python\d{3}(\\Scripts)?$") -and ($_ -ne "")
}
$env:PATH = "$pythonPath;$pythonPath\Scripts;" + ($sessionFiltered -join ';')

# Done
Write-Host "Python $Version set as default globally and for this PowerShell session."
python --version
