param (
    [string]$computer
)

try {
    Test-Connection $computer
}
catch {
    Write-Output ("[ERROR] Failed to run Test-Connection: " + $_.Exception.Message)
}