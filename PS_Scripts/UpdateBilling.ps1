param(
    [string]$computer,
    [string]$billCode
)

try {
    Set-ADComputer -Identity $computer -Replace @{departmentNumber = $billCode} -Credential $GLOBAL:creds
    Write-Output "[DONE]"
}
catch {
    Write-Out ("[ERROR] " + $_.Exception.Message)
}
