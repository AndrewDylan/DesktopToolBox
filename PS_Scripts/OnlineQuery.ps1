param (
    [string]$computer
)

try {
    Test-Connection $computer -Quiet -Count 1
}
catch {
    Write-Output ("[ERROR] Failed to run Test-Connection: " + $_.Exception.Message)
}