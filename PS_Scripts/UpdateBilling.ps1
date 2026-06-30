param(
    [string]$computer,
    [string]$billCode
)

$computer = $computer.Trim()
$billCode = $billCode.Trim()

try {
    Set-ADComputer -Identity $computer -Replace @{departmentNumber = $billCode} -Credential $GLOBAL:creds
    Write-Output "[DONE] Billing for $computer set to $billCode."
}
catch {
    Write-Out ("[ERROR] Failed to set bill code - " + $_.Exception.Message)
}
